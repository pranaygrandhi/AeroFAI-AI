import json
import os
from pathlib import Path
from typing import Dict, Any, List
from ..schemas.drawing import DrawingUploadResponse, DrawingSummary, Characteristic, PageData

DATABASE_DIR = Path(__file__).resolve().parents[2] / "data"
DATABASE_FILE = DATABASE_DIR / "drawings.json"

class JSONDatabase:
    def __init__(self):
        DATABASE_DIR.mkdir(parents=True, exist_ok=True)
        if not DATABASE_FILE.exists():
            self._save({})
            
    def _load(self) -> Dict[str, Any]:
        try:
            with open(DATABASE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save(self, data: Dict[str, Any]):
        with open(DATABASE_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def get_all_drawings(self) -> List[DrawingSummary]:
        data = self._load()
        summaries = []
        for drawing_id, details in data.items():
            chars = details.get("characteristics", [])
            measured_count = sum(1 for c in chars if c.get("measured_value") is not None)
            pass_count = sum(1 for c in chars if c.get("status") == "pass")
            fail_count = sum(1 for c in chars if c.get("status") == "fail")
            
            summaries.append(DrawingSummary(
                drawing_id=int(drawing_id),
                filename=details.get("filename", ""),
                uploaded_at=details.get("uploaded_at", ""),
                status=details.get("status", "pending"),
                confidence_score=details.get("confidence_score", 95.0),
                part_name=details.get("part_name", "Unknown Part"),
                part_number=details.get("part_number", "PN-XXXX"),
                revision=details.get("revision", "A"),
                characteristics_count=len(chars),
                measured_count=measured_count,
                pass_count=pass_count,
                fail_count=fail_count
            ))
        return summaries

    def get_drawing(self, drawing_id: int) -> Optional[Dict[str, Any]]:
        data = self._load()
        return data.get(str(drawing_id))

    def save_drawing(self, drawing_id: int, drawing_data: Dict[str, Any]):
        data = self._load()
        data[str(drawing_id)] = drawing_data
        self._save(data)
        
    def delete_drawing(self, drawing_id: int):
        data = self._load()
        if str(drawing_id) in data:
            del data[str(drawing_id)]
            self._save(data)

db = JSONDatabase()
