from pathlib import Path
from typing import Any


class OcrEngine:
    def process(self, file_path: str, pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Run OCR on scanned drawing pages and merge with vector text."""
        # TODO: integrate PaddleOCR and page-level preprocessing
        if not Path(file_path).exists():
            return []
        return [{"page": 1, "text": "", "tokens": []}]
