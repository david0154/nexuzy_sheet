# -*- coding: utf-8 -*-

# Copyright (c) 2026 Nexuzy Lab

"""
OCR Processing with PaddleOCR

Recognizes text and numbers from:
- Images
- Scanned documents
- Table photos
- Screenshots

Uses PaddleOCR PP-OCRv6 Tiny model (lightweight, fast).
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)

try:
    from paddleocr import PaddleOCR
    HAS_PADDLEOCR = True
except ImportError:
    HAS_PADDLEOCR = False
    logger.warning("PaddleOCR not available. OCR functionality disabled.")


class OCRProcessor:
    """Process images with PaddleOCR"""
    
    def __init__(self, language: str = "en"):
        """
        Initialize OCR processor
        
        Args:
            language: OCR language code (en, zh, etc.)
        """
        if not HAS_PADDLEOCR:
            raise RuntimeError("PaddleOCR is not installed. Cannot initialize OCRProcessor.")
        
        self.language = language
        # Use lightweight PP-OCRv6 Tiny model
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang=language,
            ocr_version="PP-OCRv6_tiny",
            show_log=False,
        )
    
    def recognize_text(self, image_path: str) -> Optional[Dict]:
        """
        Recognize text from image
        
        Args:
            image_path: Path to image file
        
        Returns:
            Dictionary with:
            - text: Full recognized text
            - lines: List of recognized lines with confidence
            - raw: Raw PaddleOCR output
        """
        try:
            result = self.ocr.ocr(str(image_path), cls=True)
            
            if not result or not result[0]:
                return None
            
            lines = []
            full_text = []
            
            for line in result[0]:
                text_box, (text, confidence) = line
                lines.append({
                    "text": text,
                    "confidence": float(confidence),
                    "bbox": [[float(p[0]), float(p[1])] for p in text_box],
                })
                full_text.append(text)
            
            return {
                "text": " ".join(full_text),
                "lines": lines,
                "raw": result,
            }
        
        except Exception as e:
            logger.error(f"OCR recognition failed: {e}")
            return None
    
    def recognize_table(self, image_path: str) -> Optional[List[List[str]]]:
        """
        Recognize table structure from image
        
        Args:
            image_path: Path to image containing a table
        
        Returns:
            2D list representing table rows and columns
        """
        ocr_result = self.recognize_text(image_path)
        if not ocr_result:
            return None
        
        lines = ocr_result["lines"]
        if not lines:
            return None
        
        # Group lines into rows based on Y-coordinate proximity
        rows = []
        current_row = []
        current_y = None
        row_height_threshold = 30  # pixels
        
        # Sort by Y coordinate (top to bottom)
        sorted_lines = sorted(lines, key=lambda l: l["bbox"][0][1])
        
        for line_info in sorted_lines:
            y_pos = line_info["bbox"][0][1]
            
            # Check if this line belongs to current row
            if current_y is None or abs(y_pos - current_y) < row_height_threshold:
                current_row.append(line_info)
                if current_y is None:
                    current_y = y_pos
            else:
                # Start new row
                if current_row:
                    # Sort current row by X coordinate (left to right)
                    sorted_row = sorted(current_row, key=lambda l: l["bbox"][0][0])
                    rows.append([item["text"] for item in sorted_row])
                
                current_row = [line_info]
                current_y = y_pos
        
        # Add last row
        if current_row:
            sorted_row = sorted(current_row, key=lambda l: l["bbox"][0][0])
            rows.append([item["text"] for item in sorted_row])
        
        return rows if rows else None
    
    def extract_numbers(self, image_path: str) -> Optional[List[float]]:
        """
        Extract numbers from image
        
        Args:
            image_path: Path to image
        
        Returns:
            List of recognized numbers
        """
        ocr_result = self.recognize_text(image_path)
        if not ocr_result:
            return None
        
        numbers = []
        lines = ocr_result["lines"]
        
        for line_info in lines:
            text = line_info["text"].strip()
            try:
                # Try to parse as number
                num = float(text.replace(",", "").replace("₹", "").replace("$", ""))
                if line_info["confidence"] > 0.5:  # Only high confidence
                    numbers.append(num)
            except ValueError:
                pass
        
        return numbers if numbers else None
    
    def get_text_with_positions(self, image_path: str) -> Optional[List[Dict]]:
        """
        Get recognized text with bounding box positions
        
        Useful for reconstructing table structure or layout.
        
        Args:
            image_path: Path to image
        
        Returns:
            List of dicts with text, confidence, and bbox position
        """
        ocr_result = self.recognize_text(image_path)
        if not ocr_result:
            return None
        
        return ocr_result["lines"]
