import datetime
import json
import threading
from pathlib import Path
from typing import Any, Optional

from fastapi import UploadFile

from ..schemas.drawing import DrawingUploadResponse
from ..ai.pdf_parser import PdfParser
from ..ai.ocr_engine import OcrEngine
from ..ai.dimension_parser import DimensionParser
from ..ai.gdt_parser import GdtParser
from ..ai.datum_parser import DatumParser
from ..ai.note_parser import NoteParser
from ..ai.balloon_engine import BalloonEngine
from ..ai.confidence_engine import ConfidenceEngine
from ..ai.model_trainer import ModelTrainer


class DrawingService:
    def __init__(self) -> None:
        self.pdf_parser = PdfParser()
        self.ocr_engine = OcrEngine()
        self.dimension_parser = DimensionParser()
        self.gdt_parser = GdtParser()
        self.datum_parser = DatumParser()
        self.note_parser = NoteParser()
        self.balloon_engine = BalloonEngine()
        self.confidence_engine = ConfidenceEngine()
        self.trainer = ModelTrainer()
        self._storage_dir = Path("./tmp")
        self._storage_dir.mkdir(parents=True, exist_ok=True)

    def _write_result(self, drawing_id: int, payload: dict):
        path = self._storage_dir / f"result_{drawing_id}.json"
        with path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, default=str)

    def _read_result(self, drawing_id: int) -> Optional[dict]:
        path = self._storage_dir / f"result_{drawing_id}.json"
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def _background_process(self, drawing_id: int, target_file: str, filename: str):
        try:
            # Step 1: parse pages
            self._write_result(drawing_id, {"drawing_id": drawing_id, "filename": filename, "uploaded_at": datetime.datetime.utcnow().isoformat(), "status": "parsing", "confidence_score": 0.0, "pages": [], "characteristics": []})
            parsed_pages = self.pdf_parser.extract(file_path=target_file)
            if parsed_pages:
                detections = self.trainer.predict_pages(parsed_pages, conf=0.25)
                for page_data, page_detections in zip(parsed_pages, detections):
                    page_data["detections"] = page_detections

            # Step 2: OCR
            self._write_result(drawing_id, {"drawing_id": drawing_id, "filename": filename, "uploaded_at": datetime.datetime.utcnow().isoformat(), "status": "ocr", "confidence_score": 0.0, "pages": parsed_pages or [], "characteristics": []})
            ocr_result = self.ocr_engine.process(file_path=target_file, pages=parsed_pages)
            parsed_pages = ocr_result or parsed_pages

            # Step 3: extract dimensions and annotations
            self._write_result(drawing_id, {"drawing_id": drawing_id, "filename": filename, "uploaded_at": datetime.datetime.utcnow().isoformat(), "status": "extracting", "confidence_score": 0.0, "pages": parsed_pages or [], "characteristics": []})
            dimensions = self.dimension_parser.parse(parsed_pages)
            gdts = self.gdt_parser.parse(parsed_pages)
            datums = self.datum_parser.parse(parsed_pages)
            notes = self.note_parser.parse(parsed_pages)

            # Step 4: generate balloons
            self._write_result(drawing_id, {"drawing_id": drawing_id, "filename": filename, "uploaded_at": datetime.datetime.utcnow().isoformat(), "status": "ballooning", "confidence_score": 0.0, "pages": parsed_pages or [], "characteristics": []})
            balloons = self.balloon_engine.generate(dimensions, gdts, datums, notes, pages=parsed_pages)

            # Step 5: compute confidence
            confidence_score = self.confidence_engine.calculate(dimensions, gdts, datums, notes, balloons)

            # Build characteristics list from extracted elements
            characteristics = []
            if dimensions:
                for dim in dimensions:
                    characteristics.append({
                        "id": len(characteristics) + 1,
                        "type": "dimension",
                        "value": dim,
                    })
            if gdts:
                for gdt in gdts:
                    characteristics.append({
                        "id": len(characteristics) + 1,
                        "type": "gdt",
                        "value": gdt,
                    })
            if datums:
                for datum in datums:
                    characteristics.append({
                        "id": len(characteristics) + 1,
                        "type": "datum",
                        "value": datum,
                    })
            if notes:
                for note in notes:
                    characteristics.append({
                        "id": len(characteristics) + 1,
                        "type": "note",
                        "value": note,
                    })
            if balloons:
                for balloon in balloons:
                    characteristics.append({
                        "id": len(characteristics) + 1,
                        "type": "balloon",
                        "value": balloon,
                    })

            result_payload = {
                "drawing_id": drawing_id,
                "filename": filename,
                "uploaded_at": datetime.datetime.utcnow().isoformat(),
                "status": "processed",
                "confidence_score": confidence_score,
                "pages": parsed_pages or [],
                "characteristics": characteristics,
            }
            # simulate some processing time for demo and UI polling
            # Removed artificial sleep to speed up processing
            self._write_result(drawing_id, result_payload)
        except Exception as e:
            err_payload = {
                "drawing_id": drawing_id,
                "filename": filename,
                "uploaded_at": datetime.datetime.utcnow().isoformat(),
                "status": "error",
                "confidence_score": 0.0,
                "pages": [],
                "characteristics": [],
                "error": str(e),
            }
            self._write_result(drawing_id, err_payload)

    async def process_pdf(self, file: UploadFile) -> DrawingUploadResponse:
        target_file = self._storage_dir / file.filename

        with target_file.open("wb") as buffer:
            buffer.write(await file.read())

        # generate a simple unique id from timestamp
        drawing_id = int(datetime.datetime.utcnow().timestamp() * 1000)

        initial_payload = {
            "drawing_id": drawing_id,
            "filename": file.filename,
            "uploaded_at": datetime.datetime.utcnow().isoformat(),
            "status": "processing",
            "confidence_score": 0.0,
            "pages": [],
            "characteristics": [],
        }

        # persist initial payload so status endpoints can read it
        self._write_result(drawing_id, initial_payload)

        # kick off background processing thread to avoid blocking request
        thread = threading.Thread(
            target=self._background_process,
            args=(drawing_id, str(target_file), file.filename),
            daemon=True,
        )
        thread.start()

        return DrawingUploadResponse(
            drawing_id=drawing_id,
            filename=file.filename,
            uploaded_at=datetime.datetime.utcnow(),
            status="processing",
            confidence_score=0.0,
            pages=[],
            characteristics=[],
        )

    def build_training_dataset(self, results_dir: str = "./tmp", output_dir: Optional[str] = None, train_ratio: float = 0.8) -> dict[str, Any]:
        return self.trainer.build_dataset_from_results(results_dir=results_dir, output_dir=output_dir, train_ratio=train_ratio)

    def train_model(self, epochs: int = 20, model: str = "yolov8n.pt", run_name: str = "train") -> dict[str, Any]:
        return self.trainer.train(epochs=epochs, model=model, run_name=run_name)

    def list_model_weights(self) -> list[str]:
        return self.trainer.list_weights()

    def update_characteristics(self, drawing_id: int, characteristics: list) -> dict:
        """Update stored result characteristics for a drawing and persist to disk."""
        existing = self._read_result(drawing_id)
        if existing is None:
            raise FileNotFoundError(f"Result for drawing_id {drawing_id} not found")
        existing["characteristics"] = characteristics
        # update timestamp and keep status
        existing["uploaded_at"] = datetime.datetime.utcnow().isoformat()
        existing["status"] = existing.get("status", "processed")
        self._write_result(drawing_id, existing)
        return existing
