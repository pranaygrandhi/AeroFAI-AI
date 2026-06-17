import logging
from typing import Any
import re

logger = logging.getLogger(__name__)


class GdtParser:
    """Extract and classify GD&T feature control frames from engineering drawings."""
    
    # GD&T symbol mappings (text patterns and Unicode symbols)
    GDT_SYMBOLS = {
        "perpendicularity": [r"perpendicular|⊥|perp"],
        "parallelism": [r"parallel|∥|para"],
        "true_position": [r"true\s*position|position\s*true|true\s*loc|⌀.*pos|⌀\s*(?:pos|tp)"],
        "profile_surface": [r"profile.*surface|surface.*profile"],
        "profile_line": [r"profile.*line|line.*profile"],
        "circularity": [r"circular|circularity|roundness"],
        "cylindricity": [r"cylindric|cylindricity"],
        "flatness": [r"flatness|flat"],
        "straightness": [r"straightness|straight"],
        "concentricity": [r"concentr|concentric"],
        "symmetry": [r"symmetry|symmetric"],
        "angularity": [r"angularity|angular|angle"],
        "runout": [r"runout|total.*runout|t\.?o\.?r"],
    }
    
    def parse(self, ocr_pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Extract GD&T feature control frames and classify symbols."""
        results = []
        
        for page in ocr_pages:
            page_number = page.get("page") or page.get("page_number") or 1
            for item in page.get("text_items", []) + page.get("ocr_text_items", []):
                text = (item.get("text") or "").strip()
                if not text or len(text) < 2:
                    continue
                
                # Check for GD&T symbols
                detected_symbol = self._detect_gdt_symbol(text)
                if not detected_symbol:
                    continue
                
                # Parse tolerance value if present
                tolerance_value = self._extract_tolerance_value(text)
                
                # Extract datum references if present
                datum_refs = self._extract_datum_refs(text)
                
                match_data = {
                    "page": page_number,
                    "symbol": detected_symbol,
                    "tolerance_value": tolerance_value,
                    "datum_refs": datum_refs,
                    "tolerance_zone": self._infer_tolerance_zone(detected_symbol, tolerance_value),
                    "text": text,
                    "target": item.get("center"),
                    "source": item.get("source", "vector"),
                }
                results.append(match_data)
                logger.debug("GD&T detected: %s", match_data)
        
        return results
    
    def _detect_gdt_symbol(self, text: str) -> str:
        """Detect which GD&T symbol is present in text."""
        text_upper = text.upper()
        
        for symbol, patterns in self.GDT_SYMBOLS.items():
            for pattern in patterns:
                if re.search(pattern, text_upper, re.IGNORECASE):
                    return symbol
        
        return None
    
    def _extract_tolerance_value(self, text: str) -> float:
        """Extract tolerance value from text (e.g., '0.05', '±0.10')."""
        match = re.search(r'±?\s*(\d+(?:\.\d+)?)', text)
        return float(match.group(1)) if match else None
    
    def _extract_datum_refs(self, text: str) -> list[str]:
        """Extract datum references (A, B, C, etc.) from text."""
        # Match single uppercase letters that appear after common keywords
        matches = re.findall(r'(?:datum|ref)[\s\-]?([A-Z](?:\s*[A-Z])*)', text, re.IGNORECASE)
        if matches:
            return [m.strip() for m in matches[0].split()]
        
        # Also look for isolated datum letters (usually one letter)
        letters = re.findall(r'\b([A-Z])\b', text)
        # Filter to likely datum refs (usually near end or after keywords)
        if letters and len(letters) <= 3:
            return letters
        
        return []
    
    def _infer_tolerance_zone(self, symbol: str, tolerance_value: float) -> dict:
        """Infer tolerance zone shape and size based on symbol."""
        if not tolerance_value:
            return None
        
        zone_map = {
            "true_position": "cylindrical",
            "perpendicularity": "bilateral",
            "parallelism": "bilateral",
            "flatness": "bilateral",
            "straightness": "bilateral",
            "angularity": "bilateral",
            "circularity": "bilateral",
            "cylindricity": "bilateral",
            "concentricity": "cylindrical",
            "symmetry": "bilateral",
            "profile_surface": "bilateral",
            "profile_line": "bilateral",
            "runout": "cylindrical",
        }
        
        return {
            "type": zone_map.get(symbol, "bilateral"),
            "value": tolerance_value,
            "unit": "mm",
        }
