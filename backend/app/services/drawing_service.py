import datetime
from pathlib import Path

from fastapi import UploadFile

from app.schemas.drawing import DrawingUploadResponse
from app.ai.pdf_parser import PdfParser
from app.ai.ocr_engine import OcrEngine
from app.ai.dimension_parser import DimensionParser
from app.ai.gdt_parser import GdtParser
from app.ai.datum_parser import DatumParser
from app.ai.note_parser import NoteParser
from app.ai.balloon_engine import BalloonEngine
from app.ai.confidence_engine import ConfidenceEngine


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

    async def process_pdf(self, file: UploadFile) -> DrawingUploadResponse:
        temp_dir = Path("./tmp")
        temp_dir.mkdir(parents=True, exist_ok=True)
        target_file = temp_dir / file.filename

        with target_file.open("wb") as buffer:
            buffer.write(await file.read())

        parsed_pages = self.pdf_parser.extract(file_path=str(target_file))
        ocr_result = self.ocr_engine.process(file_path=str(target_file), pages=parsed_pages)
        dimensions = self.dimension_parser.parse(ocr_result)
        gdts = self.gdt_parser.parse(ocr_result)
        datums = self.datum_parser.parse(ocr_result)
        notes = self.note_parser.parse(ocr_result)
        balloons = self.balloon_engine.generate(dimensions, gdts, datums, notes)
        confidence_score = self.confidence_engine.calculate(dimensions, gdts, datums, notes, balloons)

        return DrawingUploadResponse(
            drawing_id=1,
            filename=file.filename,
            uploaded_at=datetime.datetime.utcnow(),
            status="processed",
            confidence_score=confidence_score,
        )
