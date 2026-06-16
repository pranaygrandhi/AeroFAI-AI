from typing import Any
import re


class DimensionParser:
    def parse(self, ocr_pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Detect and classify engineering dimensions from OCR and vector text."""
        dimensions = []
        regex = re.compile(r"(?:^|\s)(Ø|⌀)?\s*(\d+(?:\.\d+)?)\s*(?:±|\+\-|\+/-)\s*(\d+(?:\.\d+)?)(?:\s*(mm|in|cm))?", flags=re.IGNORECASE)
        blacklist = ["MATERIAL", "FINISH", "DEBURR", "DRAWING", "SHEET", "PER", "STEEL", "PLATE"]

        for page in ocr_pages:
            page_number = page.get("page") or page.get("page_number") or 1
            for item in page.get("text_items", []):
                text = item.get("text", "")
                upper = text.upper()
                if any(word in upper for word in blacklist):
                    continue
                match = regex.search(text)
                if not match:
                    continue
                # only accept a dimension if the matched measurement appears at the end of the text
                if not text[match.start():].strip().startswith(match.group(0).strip()):
                    continue
                diameter_symbol = match.group(1)
                value = match.group(2)
                tolerance = f"±{match.group(3)}"
                unit = match.group(4) or "mm"
                dim_type = "diameter" if diameter_symbol else "length"
                dimensions.append({
                    "page": page_number,
                    "type": dim_type,
                    "value": value,
                    "tolerance": tolerance,
                    "unit": unit,
                    "text": text,
                    "target": item.get("center"),
                })

        return dimensions
