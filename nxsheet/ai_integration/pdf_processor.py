# -*- coding: utf-8 -*-

# Copyright (c) 2026 Nexuzy Lab

"""
PDF Processing with PyMuPDF

Extracts text and images from PDFs.
Handles both text PDFs (direct extraction) and scanned PDFs (OCR).
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import io

logger = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    logger.warning("PyMuPDF not available. PDF processing disabled.")


class PDFProcessor:
    """Process PDFs using PyMuPDF"""
    
    def __init__(self):
        """Initialize PDF processor"""
        if not HAS_PYMUPDF:
            raise RuntimeError("PyMuPDF is not installed. Cannot initialize PDFProcessor.")
    
    @staticmethod
    def open_pdf(pdf_path: str) -> Optional[fitz.Document]:
        """
        Open PDF file
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            PyMuPDF Document object or None if failed
        """
        try:
            return fitz.open(str(pdf_path))
        except Exception as e:
            logger.error(f"Could not open PDF: {e}")
            return None
    
    @staticmethod
    def get_page_count(pdf_path: str) -> int:
        """Get number of pages in PDF"""
        doc = PDFProcessor.open_pdf(pdf_path)
        if doc is None:
            return 0
        count = doc.page_count
        doc.close()
        return count
    
    @staticmethod
    def extract_text(pdf_path: str) -> Optional[str]:
        """
        Extract all text from PDF
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            Extracted text or None if failed
        """
        doc = PDFProcessor.open_pdf(pdf_path)
        if doc is None:
            return None
        
        try:
            text = ""
            for page in doc:
                text += page.get_text()
                text += "\n---PAGE BREAK---\n"
            doc.close()
            return text
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return None
    
    @staticmethod
    def extract_text_by_page(pdf_path: str) -> Optional[Dict[int, str]]:
        """
        Extract text from each page separately
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            Dict mapping page number to extracted text
        """
        doc = PDFProcessor.open_pdf(pdf_path)
        if doc is None:
            return None
        
        try:
            pages_text = {}
            for page_num, page in enumerate(doc):
                pages_text[page_num] = page.get_text()
            doc.close()
            return pages_text
        except Exception as e:
            logger.error(f"Error extracting text by page: {e}")
            return None
    
    @staticmethod
    def is_text_pdf(pdf_path: str) -> Optional[bool]:
        """
        Determine if PDF contains selectable text (not just images)
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            True if text PDF, False if scanned/image PDF, None if error
        """
        doc = PDFProcessor.open_pdf(pdf_path)
        if doc is None:
            return None
        
        try:
            if doc.page_count == 0:
                return None
            
            first_page = doc[0]
            text = first_page.get_text()
            doc.close()
            
            # If first page has significant text, it's a text PDF
            return len(text.strip()) > 50
        except Exception as e:
            logger.error(f"Error checking PDF type: {e}")
            return None
    
    @staticmethod
    def render_page_to_image(pdf_path: str, page_num: int = 0, 
                            dpi: int = 150) -> Optional[bytes]:
        """
        Render PDF page to image (for OCR on scanned PDFs)
        
        Args:
            pdf_path: Path to PDF file
            page_num: Page number (0-indexed)
            dpi: Resolution in dots per inch
        
        Returns:
            Image bytes (PNG format) or None if failed
        """
        doc = PDFProcessor.open_pdf(pdf_path)
        if doc is None:
            return None
        
        try:
            if page_num >= doc.page_count:
                logger.warning(f"Page {page_num} not found")
                return None
            
            page = doc[page_num]
            
            # Set zoom level for DPI
            zoom = dpi / 72.0
            mat = fitz.Matrix(zoom, zoom)
            
            # Render to image
            pix = page.get_pixmap(matrix=mat, alpha=False)
            image_bytes = pix.tobytes("png")
            
            doc.close()
            return image_bytes
        except Exception as e:
            logger.error(f"Error rendering page: {e}")
            return None
    
    @staticmethod
    def extract_images(pdf_path: str) -> Optional[List[bytes]]:
        """
        Extract all images from PDF
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            List of image bytes (PNG format) or None if failed
        """
        doc = PDFProcessor.open_pdf(pdf_path)
        if doc is None:
            return None
        
        try:
            images = []
            for page in doc:
                image_list = page.get_images()
                for img_index in image_list:
                    xref = img_index[0]
                    pix = fitz.Pixmap(doc, xref)
                    if pix.n - pix.alpha < 4:  # GRAY or RGB
                        img_data = pix.tobytes("png")
                    else:  # CMYK
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                        img_data = pix.tobytes("png")
                    images.append(img_data)
            
            doc.close()
            return images if images else None
        except Exception as e:
            logger.error(f"Error extracting images: {e}")
            return None
    
    @staticmethod
    def get_page_dimensions(pdf_path: str, page_num: int = 0) -> Optional[Tuple[float, float]]:
        """
        Get page width and height in points
        
        Args:
            pdf_path: Path to PDF file
            page_num: Page number (0-indexed)
        
        Returns:
            Tuple of (width, height) or None if error
        """
        doc = PDFProcessor.open_pdf(pdf_path)
        if doc is None:
            return None
        
        try:
            if page_num >= doc.page_count:
                return None
            
            page = doc[page_num]
            rect = page.rect
            doc.close()
            
            return (rect.width, rect.height)
        except Exception as e:
            logger.error(f"Error getting page dimensions: {e}")
            return None
