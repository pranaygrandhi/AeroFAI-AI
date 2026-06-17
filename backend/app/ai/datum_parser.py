import logging
from typing import Any
import re

logger = logging.getLogger(__name__)


class DatumParser:
    def parse(self, ocr_pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Locate datum callouts and extract datum feature identifiers."""
        results = []
        pattern = re.compile(r"\b([ABC])\b")

        for page in ocr_pages:
            page_number = page.get("page") or page.get("page_number") or 1
            for item in page.get("text_items", []) + page.get("ocr_text_items", []):
                text = item.get("text", "")
                match = pattern.search(text)
                if not match:
                    continue
                datum = match.group(1)
                match_data = {
                    "page": page_number,
                    "datum": datum,
                    "feature": text,
                    "type": "datum",
                    "text": text,
                    "target": item.get("center"),
                    "source": item.get("source", "vector"),
                }
                results.append(match_data)
                logger.debug("Datum detected: %s", match_data)
        return results
