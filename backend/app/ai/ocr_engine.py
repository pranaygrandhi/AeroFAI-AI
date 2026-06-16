import logging
from pathlib import Path
from typing import Any
from io import BytesIO
import cv2
import numpy as np
from PIL import Image
import base64

try:
    from paddleocr import PaddleOCR
except ImportError:
    PaddleOCR = None

logger = logging.getLogger(__name__)


class OcrEngine:
    def __init__(self, lang: str = "en", use_gpu: bool = False):
        """Initialize OCR engine with PaddleOCR.
        
        Args:
            lang: Language code ('en' for English, 'ch' for Chinese, etc.)
            use_gpu: Whether to use GPU acceleration
        """
        if PaddleOCR is None:
            logger.warning("PaddleOCR not installed. OCR will be disabled.")
            self.ocr = None
        else:
            try:
                self.ocr = PaddleOCR(use_angle_cls=True, lang=lang, use_gpu=use_gpu)
            except Exception as e:
                logger.error(f"Failed to initialize PaddleOCR: {e}")
                self.ocr = None
    
    def process(self, file_path: str, pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Run OCR on scanned drawing pages and merge with vector text.
        
        Args:
            file_path: Path to the PDF file
            pages: List of page data dicts with 'image' (base64) and optional 'vector_text'
            
        Returns:
            Enhanced pages with OCR text and tokens extracted
        """
        if not Path(file_path).exists():
            return []
        
        if not pages:
            return []
        
        enhanced_pages = []
        for idx, page in enumerate(pages):
            try:
                enhanced = self._process_single_page(page, idx + 1)
                enhanced_pages.append(enhanced)
            except Exception as e:
                logger.error(f"Error processing page {idx + 1}: {e}")
                # Fallback: return page with empty OCR text
                enhanced = page.copy()
                enhanced["ocr_text"] = ""
                enhanced["ocr_tokens"] = []
                enhanced_pages.append(enhanced)
        
        return enhanced_pages
    
    def _process_single_page(self, page: dict[str, Any], page_num: int) -> dict[str, Any]:
        """Process a single page with OCR.
        
        Args:
            page: Page data dict
            page_num: Page number
            
        Returns:
            Enhanced page dict with OCR results
        """
        enhanced = page.copy()
        enhanced["page_num"] = page_num
        
        # If no OCR engine, return empty
        if self.ocr is None:
            enhanced["ocr_text"] = ""
            enhanced["ocr_tokens"] = []
            enhanced["ocr_confidence"] = 0.0
            return enhanced
        
        # Extract image from page
        image = self._extract_image(page)
        if image is None:
            enhanced["ocr_text"] = ""
            enhanced["ocr_tokens"] = []
            enhanced["ocr_confidence"] = 0.0
            return enhanced
        
        # Run OCR
        try:
            results = self.ocr.ocr(image, cls=True)
            ocr_text, ocr_tokens, avg_confidence = self._parse_ocr_results(results)
            
            enhanced["ocr_text"] = ocr_text
            enhanced["ocr_tokens"] = ocr_tokens
            enhanced["ocr_confidence"] = avg_confidence
            
            # Merge with vector text if present
            if "vector_text" in page:
                enhanced["merged_text"] = self._merge_texts(ocr_text, page.get("vector_text", ""))
            else:
                enhanced["merged_text"] = ocr_text
                
        except Exception as e:
            logger.error(f"OCR processing failed for page {page_num}: {e}")
            enhanced["ocr_text"] = ""
            enhanced["ocr_tokens"] = []
            enhanced["ocr_confidence"] = 0.0
            enhanced["merged_text"] = page.get("vector_text", "")
        
        return enhanced
    
    def _extract_image(self, page: dict[str, Any]) -> np.ndarray | None:
        """Extract and convert image from page data.
        
        Args:
            page: Page data dict with 'image' key (base64 or path)
            
        Returns:
            OpenCV image array or None if extraction failed
        """
        try:
            if "image" in page:
                # Try base64 first
                if isinstance(page["image"], str):
                    try:
                        img_data = base64.b64decode(page["image"])
                        img_pil = Image.open(BytesIO(img_data))
                    except Exception:
                        # Try as file path
                        img_pil = Image.open(page["image"])
                    
                    # Convert to OpenCV format (BGR)
                    img_np = np.array(img_pil)
                    if len(img_np.shape) == 3 and img_np.shape[2] == 3:
                        return cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
                    return img_np
            
            elif "image_path" in page:
                img_pil = Image.open(page["image_path"])
                img_np = np.array(img_pil)
                if len(img_np.shape) == 3 and img_np.shape[2] == 3:
                    return cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
                return img_np
        except Exception as e:
            logger.error(f"Failed to extract image: {e}")
        
        return None
    
    def _parse_ocr_results(self, results: list) -> tuple[str, list[dict], float]:
        """Parse PaddleOCR results into text, tokens, and confidence.
        
        Args:
            results: PaddleOCR results (list of detection boxes)
            
        Returns:
            Tuple of (full_text, tokens, avg_confidence)
        """
        text_lines = []
        tokens = []
        confidences = []
        
        if not results:
            return "", [], 0.0
        
        for line in results:
            if not line:
                continue
            
            for box_result in line:
                text = box_result[1]
                confidence = float(box_result[2])
                
                text_lines.append(text)
                tokens.append({
                    "text": text,
                    "confidence": confidence,
                    "bbox": box_result[0] if len(box_result) > 3 else None
                })
                confidences.append(confidence)
        
        full_text = "\n".join(text_lines)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return full_text, tokens, avg_confidence
    
    def _merge_texts(self, ocr_text: str, vector_text: str) -> str:
        """Merge OCR and vector text, preferring vector text for precision.
        
        Args:
            ocr_text: Text from OCR
            vector_text: Text extracted from PDF vectors
            
        Returns:
            Merged text with vector text having priority
        """
        if not vector_text:
            return ocr_text
        if not ocr_text:
            return vector_text
        
        # Prefer vector text but supplement with OCR for missing lines
        vector_lines = set(vector_text.split("\n"))
        ocr_lines = ocr_text.split("\n")
        
        merged_lines = list(vector_lines)
        for line in ocr_lines:
            if line and line not in vector_lines:
                merged_lines.append(line)
        
        return "\n".join(merged_lines)
