"""
OCR (Optical Character Recognition) Module.

Supports:
- Tesseract OCR
- PaddleOCR (multilingual)
- Image preprocessing
"""

from app.ml.ocr.processor import (
    OCRProcessor,
    extract_text_from_image,
    extract_text_from_bytes,
)

__all__ = [
    "OCRProcessor",
    "extract_text_from_image",
    "extract_text_from_bytes",
]
