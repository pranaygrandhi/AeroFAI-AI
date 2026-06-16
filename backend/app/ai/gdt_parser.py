from typing import Any
import re


class GdtParser:
    def parse(self, ocr_pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Extract GD&T feature control frames and classify symbols."""
        symbols = ["perpendicularity", "parallelism", "cylindricity", "concentricity", "flatness", "position"]
        results = []
        pattern = re.compile(r"\b(" + "|".join(symbols) + r")\b", flags=re.IGNORECASE)

        for page in ocr_pages:
            page_number = page.get("page") or page.get("page_number") or 1
            for item in page.get("text_items", []):
                text = item.get("text", "")
                match = pattern.search(text)
                if not match:
                    continue
                results.append({
                    "page": page_number,
                    "symbol": match.group(1).lower(),
                    "datum": item.get("text", "").split()[-1] if "datum" in text.lower() else None,
                    "tolerance_zone": None,
                    "text": text,
                    "target": item.get("center"),
                })
        return results
