import logging
from typing import Any
import re

logger = logging.getLogger(__name__)


class DimensionParser:
    """Parse and classify dimensions from PDF text."""
    
    def parse(self, ocr_pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Detect, classify, and extract engineering dimensions from OCR and vector text."""
        dimensions = []
        regex = re.compile(
            r"(?P<diameter>Ø|⌀)?\s*(?P<value>\d+(?:\.\d+)?)"
            r"(?:\s*(?P<unit>mm|cm|in))?"
            r"(?:\s*(?:±|\+/-|\+\-)\s*(?P<tolerance>\d+(?:\.\d+)?)(?:\s*(?:mm|cm|in))?)?",
            flags=re.IGNORECASE,
        )
        required_marker = re.compile(r"(?:Ø|⌀|KO|R\b|BEND\b|mm\b|cm\b|in\b|±|°)", flags=re.IGNORECASE)
        note_pattern = re.compile(r"^\d+\.\s+[A-Z]", flags=re.IGNORECASE)
        blacklist = ["MATERIAL", "FINISH", "DEBURR", "DRAWING", "SHEET", "PER", "STEEL", "PLATE", "NOTE", "FACTOR", "DISTANCE", "CALCULATION", "SCALE", "EDGES", "CHROMATE", "ALLOW", "UNLESS NOTED"]

        for page in ocr_pages:
            page_number = page.get("page") or page.get("page_number") or 1

            for item in page.get("text_items", []) + page.get("ocr_text_items", []):
                text = (item.get("text") or "").strip()
                if not text:
                    continue
                upper = text.upper()
                center = item.get("center", [])
                x, y = center[0] if center else 0, center[1] if center else 0

                # Exclude note patterns
                if note_pattern.match(text):
                    continue

                # Exclude blacklisted keywords
                if any(word in upper for word in blacklist):
                    continue
                if len(text) <= 2 and not required_marker.search(text):
                    continue
                if not required_marker.search(text):
                    continue
                
                # Classify dimension type (basic, reference, normal)
                dim_class = self._classify_dimension(text)
                
                match = regex.search(text)
                if not match:
                    continue

                diameter_symbol = match.group("diameter")
                value = match.group("value")
                if not value:
                    continue

                tolerance = f"±{match.group('tolerance')}" if match.group("tolerance") else ""
                unit = match.group("unit") or "mm"
                text_type = text.upper()
                if diameter_symbol or re.search(r"\bKO\b", text_type):
                    dim_type = "diameter"
                elif re.search(r"\bR\b", text_type) and not re.search(r"\bREV\b", text_type):
                    dim_type = "radius"
                elif re.search(r"°", text_type):
                    dim_type = "angle"
                else:
                    dim_type = "length"

                match_data = {
                    "page": page_number,
                    "type": dim_type,
                    "class": dim_class,  # 'basic', 'reference', or 'normal'
                    "value": value,
                    "tolerance": tolerance,
                    "unit": unit,
                    "text": text,
                    "target": item.get("center"),
                    "source": item.get("source", "vector"),
                }
                dimensions.append(match_data)
                logger.debug("Dimension detected: %s", match_data)

        return dimensions
    
    def _classify_dimension(self, text: str) -> str:
        """Classify dimension as basic, reference, or normal.
        
        Basic dimensions (no tolerance): [10], <20>
        Reference dimensions: (50), (100) REF
        Normal dimensions: 5±0.1, Ø30
        """
        # Check for basic dimension markers (square/angle brackets)
        if re.search(r"\[.*?\d+.*?\]|<.*?\d+.*?>", text):
            return "basic"
        
        # Check for reference dimension markers (parentheses or 'REF' keyword)
        if re.search(r"\(.*?\d+.*?\)|REF\s*$|REFERENCE", text, re.IGNORECASE):
            return "reference"
        
        return "normal"
