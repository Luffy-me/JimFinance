"""
OCR (Optical Character Recognition) pipeline for extracting text from images.
Supports Tesseract and PaddleOCR.
"""

import io
import logging
from typing import Optional, Tuple
from pathlib import Path
from PIL import Image
import pytesseract

logger = logging.getLogger(__name__)


class OCRProcessor:
    """Main OCR processor using Tesseract and PaddleOCR."""
    
    def __init__(self, use_paddle: bool = True):
        """
        Initialize OCR processor.
        
        Args:
            use_paddle: Use PaddleOCR for better multilingual support
        """
        self.use_paddle = use_paddle
        self.paddle_ocr = None
        
        if use_paddle:
            try:
                from paddleocr import PaddleOCR
                self.paddle_ocr = PaddleOCR(use_angle_cls=True, lang="en")
                logger.info("PaddleOCR initialized successfully")
            except ImportError:
                logger.warning("PaddleOCR not available, falling back to Tesseract")
                self.use_paddle = False
            except Exception as e:
                logger.warning(f"Failed to initialize PaddleOCR: {e}, falling back to Tesseract")
                self.use_paddle = False
    
    def extract_text_from_image(
        self, image_path: str | Path, language: str = "eng+rus"
    ) -> str:
        """
        Extract text from image file.
        
        Args:
            image_path: Path to image file
            language: OCR language (Tesseract format: 'eng' for English, 'rus' for Russian)
        
        Returns:
            Extracted text
        """
        try:
            image = Image.open(image_path)
            return self.extract_text_from_pil_image(image, language)
        except Exception as e:
            logger.error(f"Failed to extract text from {image_path}: {e}")
            return ""
    
    def extract_text_from_bytes(
        self, image_bytes: bytes, language: str = "eng+rus"
    ) -> str:
        """
        Extract text from image bytes.
        
        Args:
            image_bytes: Image data as bytes
            language: OCR language
        
        Returns:
            Extracted text
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            return self.extract_text_from_pil_image(image, language)
        except Exception as e:
            logger.error(f"Failed to extract text from bytes: {e}")
            return ""
    
    def extract_text_from_pil_image(
        self, image: Image.Image, language: str = "eng+rus"
    ) -> str:
        """
        Extract text from PIL Image object.
        
        Args:
            image: PIL Image
            language: OCR language
        
        Returns:
            Extracted text
        """
        # Preprocess image for better OCR
        processed_image = self._preprocess_image(image)
        
        if self.use_paddle and self.paddle_ocr:
            return self._extract_with_paddle_ocr(processed_image)
        else:
            return self._extract_with_tesseract(processed_image, language)
    
    def extract_text_with_layout(
        self, image_path: str | Path, language: str = "eng+rus"
    ) -> dict:
        """
        Extract text with layout information (bounding boxes, confidence scores).
        
        Args:
            image_path: Path to image file
            language: OCR language
        
        Returns:
            Dict with text and layout information
        """
        try:
            image = Image.open(image_path)
            processed_image = self._preprocess_image(image)
            
            if self.use_paddle and self.paddle_ocr:
                return self._extract_layout_with_paddle_ocr(processed_image)
            else:
                return self._extract_layout_with_tesseract(processed_image, language)
        except Exception as e:
            logger.error(f"Failed to extract layout from {image_path}: {e}")
            return {"text": "", "layout": []}
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR results.
        - Convert to RGB if needed
        - Increase contrast
        - Remove noise
        """
        # Convert RGBA to RGB
        if image.mode == "RGBA":
            rgb_image = Image.new("RGB", image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[3])
            image = rgb_image
        elif image.mode != "RGB":
            image = image.convert("RGB")
        
        # Enhance image for OCR
        import PIL.ImageEnhance as ImageEnhance
        
        # Increase contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # Increase sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        
        return image
    
    def _extract_with_tesseract(self, image: Image.Image, language: str) -> str:
        """Extract text using Tesseract."""
        try:
            text = pytesseract.image_to_string(image, lang=language)
            return text.strip()
        except Exception as e:
            logger.error(f"Tesseract extraction failed: {e}")
            return ""
    
    def _extract_with_paddle_ocr(self, image: Image.Image) -> str:
        """Extract text using PaddleOCR."""
        try:
            result = self.paddle_ocr.ocr(image, cls=True)
            
            # Extract text from results
            text_lines = []
            if result:
                for line in result:
                    if line:
                        for word_info in line:
                            text, confidence = word_info[1], word_info[2]
                            if confidence > 0.5:  # Only include confident predictions
                                text_lines.append(text)
            
            return " ".join(text_lines)
        except Exception as e:
            logger.error(f"PaddleOCR extraction failed: {e}")
            return ""
    
    def _extract_layout_with_tesseract(self, image: Image.Image, language: str) -> dict:
        """Extract text layout using Tesseract."""
        try:
            # Get detailed data
            data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
            
            text_lines = []
            for i in range(len(data["text"])):
                if int(data["conf"][i]) > 30:  # Confidence threshold
                    text_lines.append({
                        "text": data["text"][i],
                        "confidence": int(data["conf"][i]) / 100.0,
                        "bbox": {
                            "x": data["left"][i],
                            "y": data["top"][i],
                            "width": data["width"][i],
                            "height": data["height"][i],
                        }
                    })
            
            full_text = " ".join([item["text"] for item in text_lines if item["text"]])
            
            return {
                "text": full_text.strip(),
                "layout": text_lines,
            }
        except Exception as e:
            logger.error(f"Tesseract layout extraction failed: {e}")
            return {"text": "", "layout": []}
    
    def _extract_layout_with_paddle_ocr(self, image: Image.Image) -> dict:
        """Extract text layout using PaddleOCR."""
        try:
            result = self.paddle_ocr.ocr(image, cls=True)
            
            text_lines = []
            if result:
                for line in result:
                    if line:
                        for word_info in line:
                            bbox, (text, confidence) = word_info[0], word_info[1:]
                            if confidence > 0.5:
                                # Convert bbox to standard format
                                x_coords = [point[0] for point in bbox]
                                y_coords = [point[1] for point in bbox]
                                
                                text_lines.append({
                                    "text": text,
                                    "confidence": confidence,
                                    "bbox": {
                                        "x": min(x_coords),
                                        "y": min(y_coords),
                                        "width": max(x_coords) - min(x_coords),
                                        "height": max(y_coords) - min(y_coords),
                                    }
                                })
            
            full_text = " ".join([item["text"] for item in text_lines])
            
            return {
                "text": full_text.strip(),
                "layout": text_lines,
            }
        except Exception as e:
            logger.error(f"PaddleOCR layout extraction failed: {e}")
            return {"text": "", "layout": []}


def extract_text_from_image(image_path: str | Path) -> str:
    """Convenience function to extract text from image."""
    processor = OCRProcessor()
    return processor.extract_text_from_image(image_path)


def extract_text_from_bytes(image_bytes: bytes) -> str:
    """Convenience function to extract text from image bytes."""
    processor = OCRProcessor()
    return processor.extract_text_from_bytes(image_bytes)
