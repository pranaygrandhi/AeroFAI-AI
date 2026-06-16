from __future__ import annotations

import base64
import io
import json
import random
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class ModelTrainer:
    class_names = ["dimension", "gdt", "datum", "note"]

    def __init__(self, base_dir: str = "./training") -> None:
        self.base_dir = Path(base_dir)
        self.images_dir = self.base_dir / "images"
        self.labels_dir = self.base_dir / "labels"
        self.weights_dir = self.base_dir / "weights"
        self.runs_dir = self.base_dir / "runs"
        self.data_yaml = self.base_dir / "data.yaml"
        self._model = None

        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.labels_dir.mkdir(parents=True, exist_ok=True)
        self.weights_dir.mkdir(parents=True, exist_ok=True)
        self.runs_dir.mkdir(parents=True, exist_ok=True)

    def _decode_image(self, image_uri: str) -> Tuple[bytes, int, int, Any]:
        if not image_uri or "," not in image_uri:
            raise ValueError("Invalid image data URI")

        header, payload = image_uri.split(",", 1)
        image_bytes = base64.b64decode(payload)

        from PIL import Image

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return image_bytes, image.width, image.height, image

    def get_weights_paths(self) -> List[Path]:
        weights = sorted(self.weights_dir.glob("*.pt"), key=lambda p: p.stat().st_mtime, reverse=True)
        weights += sorted(self.runs_dir.glob("**/*.pt"), key=lambda p: p.stat().st_mtime, reverse=True)
        return weights

    def get_latest_weights(self) -> Optional[Path]:
        paths = self.get_weights_paths()
        return paths[0] if paths else None

    def has_weights(self) -> bool:
        return self.get_latest_weights() is not None

    def load_model(self, weights_path: Optional[str] = None):
        import os

        from ultralytics import YOLO

        selected = Path(weights_path) if weights_path else self.get_latest_weights()
        if selected is None or not selected.exists():
            raise FileNotFoundError("No YOLO weights were found. Train a model before using inference.")

        self._model = YOLO(str(selected))
        return self._model

    def _normalize_box(self, bbox: List[float], page_width: float, page_height: float) -> List[float]:
        x1, y1, x2, y2 = bbox
        width = max(1.0, page_width)
        height = max(1.0, page_height)
        x_center = ((x1 + x2) / 2.0) / width
        y_center = ((y1 + y2) / 2.0) / height
        box_width = abs(x2 - x1) / width
        box_height = abs(y2 - y1) / height
        return [
            max(0.0, min(1.0, x_center)),
            max(0.0, min(1.0, y_center)),
            max(0.0, min(1.0, box_width)),
            max(0.0, min(1.0, box_height)),
        ]

    def predict_pages(self, pages: List[Dict[str, Any]], conf: float = 0.25) -> List[List[Dict[str, Any]]]:
        if not pages or not self.has_weights():
            return [[] for _ in pages]

        model = self._model or self.load_model()

        predictions = []
        for page in pages:
            image_uri = page.get("image")
            if not image_uri:
                predictions.append([])
                continue

            _, image_width, image_height, image = self._decode_image(image_uri)
            try:
                import numpy as np

                image_array = np.array(image)
            except Exception as exc:
                raise RuntimeError(f"Failed to convert image for inference: {exc}")

            try:
                results = model.predict(source=image_array, conf=conf, verbose=False, save=False)
            except Exception as exc:
                raise RuntimeError(f"YOLO model inference failed: {exc}")

            page_detections: List[Dict[str, Any]] = []
            for result in results:
                for box in getattr(result, "boxes", []):
                    coords = box.xyxy[0].tolist() if hasattr(box.xyxy, "tolist") else []
                    if len(coords) != 4:
                        continue
                    cls = int(box.cls[0]) if hasattr(box, "cls") and box.cls is not None else 0
                    confidence = float(box.conf[0]) if hasattr(box, "conf") and box.conf is not None else 0.0
                    x1, y1, x2, y2 = coords
                    page_x1 = x1 / image_width * page.get("width", image_width)
                    page_y1 = y1 / image_height * page.get("height", image_height)
                    page_x2 = x2 / image_width * page.get("width", image_width)
                    page_y2 = y2 / image_height * page.get("height", image_height)
                    center_x = (page_x1 + page_x2) / 2.0
                    center_y = (page_y1 + page_y2) / 2.0
                    page_detections.append({
                        "class_id": cls,
                        "class_name": self.class_names[cls] if 0 <= cls < len(self.class_names) else str(cls),
                        "confidence": confidence,
                        "bbox": [page_x1, page_y1, page_x2, page_y2],
                        "center": [center_x, center_y],
                    })

            predictions.append(page_detections)

        return predictions

    def _create_label_lines(self, characteristics: List[Dict[str, Any]], page_width: float, page_height: float) -> List[str]:
        lines: List[str] = []
        for char in characteristics:
            class_name = char.get("type")
            if class_name not in self.class_names:
                continue
            class_id = self.class_names.index(class_name)
            value = char.get("value", {}) if isinstance(char.get("value"), dict) else {}
            target = value.get("target")
            bbox = value.get("bbox")
            if target and isinstance(target, list) and len(target) == 2:
                if bbox and isinstance(bbox, list) and len(bbox) == 4:
                    x1, y1, x2, y2 = bbox
                else:
                    x_center, y_center = float(target[0]), float(target[1])
                    width = page_width * 0.08
                    height = page_height * 0.04
                    x1 = x_center - width / 2.0
                    y1 = y_center - height / 2.0
                    x2 = x_center + width / 2.0
                    y2 = y_center + height / 2.0

                normalized = self._normalize_box([x1, y1, x2, y2], page_width, page_height)
                lines.append("{} {:.6f} {:.6f} {:.6f} {:.6f}".format(class_id, *normalized))
        return lines

    def _save_label_file(self, label_path: Path, lines: List[str]) -> None:
        label_path.parent.mkdir(parents=True, exist_ok=True)
        with label_path.open("w", encoding="utf-8") as fh:
            for line in lines:
                fh.write(f"{line}\n")

    def build_dataset_from_results(
        self,
        results_dir: str = "./tmp",
        output_dir: Optional[str] = None,
        train_ratio: float = 0.8,
    ) -> Dict[str, Any]:
        results_path = Path(results_dir)
        output_path = Path(output_dir or self.base_dir)
        train_images = output_path / "images" / "train"
        val_images = output_path / "images" / "val"
        train_labels = output_path / "labels" / "train"
        val_labels = output_path / "labels" / "val"

        train_images.mkdir(parents=True, exist_ok=True)
        val_images.mkdir(parents=True, exist_ok=True)
        train_labels.mkdir(parents=True, exist_ok=True)
        val_labels.mkdir(parents=True, exist_ok=True)

        entries: List[Dict[str, Any]] = []
        for json_file in sorted(results_path.glob("result_*.json")):
            try:
                content = json.loads(json_file.read_text(encoding="utf-8"))
            except Exception:
                continue

            for page in content.get("pages", []):
                image_uri = page.get("image")
                if not image_uri:
                    continue

                text_entries = [
                    char for char in content.get("characteristics", []) if char.get("type") in self.class_names
                ]
                page_number = page.get("page", 1)
                page_entries = [
                    char
                    for char in text_entries
                    if char.get("value", {}).get("page") == page_number
                ]
                if not page_entries:
                    continue

                label_lines = self._create_label_lines(page_entries, float(page.get("width", 1)), float(page.get("height", 1)))
                if not label_lines:
                    continue

                try:
                    image_bytes, _, _, _ = self._decode_image(image_uri)
                except Exception:
                    continue

                entries.append({
                    "image_bytes": image_bytes,
                    "page_number": page_number,
                    "label_lines": label_lines,
                    "page_id": json_file.stem,
                })

        if not entries:
            raise ValueError("No labeled training examples were found in the results directory.")

        random.shuffle(entries)
        split_index = max(1, int(len(entries) * train_ratio))
        train_entries = entries[:split_index]
        val_entries = entries[split_index:] if len(entries) > split_index else []

        def save_entries(dataset_entries: List[Dict[str, Any]], image_dir: Path, label_dir: Path) -> int:
            for index, item in enumerate(dataset_entries, start=1):
                image_name = f"{item['page_id']}_{item['page_number']}_{index}.png"
                image_path = image_dir / image_name
                label_path = label_dir / f"{item['page_id']}_{item['page_number']}_{index}.txt"
                image_path.parent.mkdir(parents=True, exist_ok=True)
                label_path.parent.mkdir(parents=True, exist_ok=True)
                with image_path.open("wb") as fh:
                    fh.write(item["image_bytes"])
                self._save_label_file(label_path, item["label_lines"])
            return len(dataset_entries)

        train_count = save_entries(train_entries, train_images, train_labels)
        val_count = save_entries(val_entries, val_images, val_labels)
        self._save_data_yaml(output_path)

        return {
            "dataset_directory": str(output_path),
            "train_images": str(train_images),
            "val_images": str(val_images),
            "train_count": train_count,
            "val_count": val_count,
            "classes": self.class_names,
            "data_yaml": str(self.data_yaml),
        }

    def _save_data_yaml(self, output_path: Path) -> None:
        data = {
            "train": str((output_path / "images" / "train").as_posix()),
            "val": str((output_path / "images" / "val").as_posix()),
            "nc": len(self.class_names),
            "names": {index: name for index, name in enumerate(self.class_names)},
        }
        try:
            import yaml
        except ImportError:
            raise RuntimeError("PyYAML is required to generate the YOLO data YAML. Install it or add it to requirements.")

        with self.data_yaml.open("w", encoding="utf-8") as fh:
            yaml.safe_dump(data, fh)

    def train(
        self,
        epochs: int = 20,
        model: str = "yolov8n.pt",
        data_yaml: Optional[str] = None,
        run_name: str = "train",
    ) -> Dict[str, Any]:
        from ultralytics import YOLO

        data_file = Path(data_yaml) if data_yaml else self.data_yaml
        if not data_file.exists():
            raise FileNotFoundError(
                f"Training data configuration not found at {data_file}. Build the dataset first."
            )

        result = YOLO(model).train(
            data=str(data_file),
            epochs=epochs,
            project=str(self.runs_dir),
            name=run_name,
            exist_ok=True,
            save=True,
        )

        run_dir = self.runs_dir / run_name
        weights_candidates = sorted(run_dir.glob("weights/*.pt"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not weights_candidates:
            raise RuntimeError(f"Training completed but no weights were found in {run_dir}")

        best_weights = weights_candidates[0]
        final_weights = self.weights_dir / best_weights.name
        shutil.copy(best_weights, final_weights)
        return {
            "run_name": run_name,
            "epochs": epochs,
            "data_yaml": str(data_file),
            "weights": str(final_weights),
            "run_directory": str(run_dir),
        }

    def list_weights(self) -> List[str]:
        return [str(path) for path in self.get_weights_paths()]
