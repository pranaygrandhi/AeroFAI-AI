from typing import Any
import re


class NoteParser:
    def parse(self, ocr_pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Extract general, process, finish, material, and inspection notes."""
        results = []
        note_keywords = ["material", "deburr", "finish", "inspection", "critical", "tolerance"]
        pattern = re.compile(r"\b(" + "|".join(note_keywords) + r")\b", flags=re.IGNORECASE)

        for page in ocr_pages:
            page_number = page.get("page") or page.get("page_number") or 1
            for item in page.get("text_items", []):
                text = item.get("text", "")
                if pattern.search(text):
                    results.append({
                        "page": page_number,
                        "note": text,
                        "region": "annotation",
                        "target": item.get("center"),
                    })
        return results
