from typing import Any, List, Dict
import re


class DrawingMetadataParser:
    """Extract sheet, zone, revision, and title block metadata from PDF text."""

    SHEET_REGEX = re.compile(r"SHEET\s*(\d+)\s*OF\s*(\d+)", re.IGNORECASE)
    ZONE_REGEX = re.compile(r"ZONE\s*([A-Z]\d+)", re.IGNORECASE)
    REVISION_REGEX = re.compile(r"REV(?:ISION)?\s*[:\s]*([A-Z0-9]+)", re.IGNORECASE)
    TITLE_REGEX = re.compile(r"TITLE\s*[:\s]*(.+)", re.IGNORECASE)

    def parse(self, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        metadata = {
            "sheet_number": None,
            "sheet_count": None,
            "zone": None,
            "revision": None,
            "title": None,
            "drawing_notes": [],
        }

        for page in pages:
            for item in page.get("text_items", []):
                text = (item.get("text") or "").strip()
                if not text:
                    continue

                if not metadata["sheet_number"] or not metadata["sheet_count"]:
                    sheet_match = self.SHEET_REGEX.search(text)
                    if sheet_match:
                        metadata["sheet_number"] = int(sheet_match.group(1))
                        metadata["sheet_count"] = int(sheet_match.group(2))

                if not metadata["zone"]:
                    zone_match = self.ZONE_REGEX.search(text)
                    if zone_match:
                        metadata["zone"] = zone_match.group(1)

                if not metadata["revision"]:
                    rev_match = self.REVISION_REGEX.search(text)
                    if rev_match:
                        metadata["revision"] = rev_match.group(1)

                if not metadata["title"]:
                    title_match = self.TITLE_REGEX.search(text)
                    if title_match:
                        metadata["title"] = title_match.group(1).strip()

                if len(text) > 30 and "note" in text.lower():
                    metadata["drawing_notes"].append(text)

        return metadata
