# -*- coding: utf-8 -*-

# Copyright (c) 2026 Nexuzy Lab

"""
AI Coordinator

Central hub that manages all AI components:
- Qwen2.5-0.5B-Instruct (text/reasoning)
- PaddleOCR (document reading)
- OpenCV (image preprocessing)
- PyMuPDF (PDF handling)

Coordinates between components and exposes unified AI interface to spreadsheet.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import tempfile
import os

logger = logging.getLogger(__name__)

from .config import AIConfig
from .schemas import AIAction, AIActionType, ErrorAction
from .qwen_interface import QwenInterface
from .ocr_processor import OCRProcessor
from .image_processor import ImageProcessor
from .pdf_processor import PDFProcessor


class AICoordinator:
    """
    Central coordinator for all AI operations
    
    Manages model initialization, component coordination, and action execution.
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize AI coordinator
        
        Args:
            verbose: Enable detailed logging
        """
        self.verbose = verbose
        self.config = AIConfig()
        
        # Component instances
        self.qwen = None
        self.ocr = None
        self.image_processor = None
        self.pdf_processor = None
        
        # Check and report status
        self._check_initialization()
    
    def _check_initialization(self):
        """Check what components are available"""
        logger.info("AI Coordinator initialization check:")
        
        # Check dependencies
        missing = self.config.get_missing_dependencies()
        if missing:
            logger.warning(f"Missing dependencies: {', '.join(missing.keys())}")
        else:
            logger.info("All AI dependencies installed")
        
        # Check models
        if self.config.is_model_downloaded("qwen2.5-0.5b-instruct"):
            logger.info("Qwen2.5-0.5B-Instruct model available")
        else:
            logger.warning("Qwen2.5-0.5B-Instruct model not downloaded")
    
    def initialize_async(self, progress_callback=None):
        """
        Initialize AI components (may take time for first-run downloads)
        
        Args:
            progress_callback: Optional function(status_text) for progress updates
        """
        def log_progress(msg):
            if progress_callback:
                progress_callback(msg)
            logger.info(msg)
        
        try:
            log_progress("Checking AI dependencies...")
            missing = self.config.get_missing_dependencies()
            if missing:
                log_progress(f"Missing: {', '.join(missing.keys())}")
                log_progress("Install with: pip install " + " ".join(missing.keys()))
                return False
            
            log_progress("Initializing Qwen2.5-0.5B-Instruct...")
            self._init_qwen()
            
            log_progress("Initializing OCR (PaddleOCR)...")
            self._init_ocr()
            
            log_progress("Initializing image processor (OpenCV)...")
            self._init_image_processor()
            
            log_progress("Initializing PDF processor (PyMuPDF)...")
            self._init_pdf_processor()
            
            log_progress("AI integration ready!")
            self.config.mark_initialized()
            return True
        
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            log_progress(f"Error: {e}")
            return False
    
    def _init_qwen(self):
        """Initialize the Qwen2.5-0.5B-Instruct model"""
        try:
            model_path = self.config.get_model_path("qwen2.5-0.5b-instruct")
            if not model_path:
                logger.warning("Qwen2.5 model not found. Download via: "
                               "config.download_model('qwen2.5-0.5b-instruct')")
                return False
            
            self.qwen = QwenInterface(str(model_path))
            logger.info("Qwen2.5-0.5B-Instruct initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Qwen2.5: {e}")
            return False
    
    def _init_ocr(self):
        """Initialize OCR processor"""
        try:
            self.ocr = OCRProcessor(language="en")
            logger.info("OCR initialized successfully")
            return True
        except Exception as e:
            logger.warning(f"OCR not available: {e}")
            return False
    
    def _init_image_processor(self):
        """Initialize image processor"""
        try:
            self.image_processor = ImageProcessor()
            logger.info("Image processor initialized successfully")
            return True
        except Exception as e:
            logger.warning(f"Image processor not available: {e}")
            return False
    
    def _init_pdf_processor(self):
        """Initialize PDF processor"""
        try:
            self.pdf_processor = PDFProcessor()
            logger.info("PDF processor initialized successfully")
            return True
        except Exception as e:
            logger.warning(f"PDF processor not available: {e}")
            return False
    
    def is_ready(self) -> bool:
        """Check if AI is ready to use"""
        return self.qwen is not None
    
    # ========== Main AI Interface ==========
    
    def process_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> AIAction:
        """
        Process user command and return AI action
        
        Args:
            command: User command (e.g., "Add GST of 18% to B5")
            context: Optional spreadsheet context
        
        Returns:
            AIAction (formula, find, error, etc.)
        """
        if not self.is_ready():
            return ErrorAction("AI not initialized. Install dependencies and download models.")
        
        try:
            action_dict = self.qwen.handle_command(command, context)
            if not action_dict:
                return ErrorAction("Could not understand command")
            
            # Convert dict to proper AIAction object
            return self._dict_to_action(action_dict)
        
        except Exception as e:
            logger.error(f"Command processing error: {e}")
            return ErrorAction(f"Error processing command: {e}")
    
    def explain_formula(self, formula: str) -> Optional[str]:
        """
        Explain a formula in human-readable terms
        
        Args:
            formula: Spreadsheet formula
        
        Returns:
            Explanation or None if failed
        """
        if not self.is_ready():
            return None
        
        try:
            return self.qwen.explain_formula(formula)
        except Exception as e:
            logger.error(f"Formula explanation error: {e}")
            return None
    
    # ========== Document/Image Processing ==========
    
    def import_from_image(self, image_path: str, output_cell: str = "A1") -> AIAction:
        """
        Import data from image (photo, screenshot, etc.)
        
        Args:
            image_path: Path to image file
            output_cell: Cell to import data into
        
        Returns:
            AIAction with import_table action or error
        """
        if not self.ocr or not self.image_processor:
            return ErrorAction("OCR or image processing not available")
        
        try:
            # Load and preprocess image
            img = self.image_processor.load_image(image_path)
            if img is None:
                return ErrorAction(f"Could not load image: {image_path}")
            
            img = self.image_processor.auto_preprocess(img)
            
            # Save preprocessed image to temp file
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                self.image_processor.save_image(img, tmp.name)
                temp_path = tmp.name
            
            # Recognize table
            table = self.ocr.recognize_table(temp_path)
            os.unlink(temp_path)
            
            if not table:
                return ErrorAction("Could not extract table from image")
            
            from .schemas import ImportTableAction
            return ImportTableAction(table, output_cell, 
                                    f"Imported table from image ({len(table)} rows)",
                                    confidence=0.8)
        
        except Exception as e:
            logger.error(f"Image import error: {e}")
            return ErrorAction(f"Error importing from image: {e}")
    
    def import_from_pdf(self, pdf_path: str, output_cell: str = "A1", 
                       page: int = 0) -> AIAction:
        """
        Import data from PDF
        
        Args:
            pdf_path: Path to PDF file
            output_cell: Cell to import data into
            page: Page number (0-indexed)
        
        Returns:
            AIAction with import_table action or error
        """
        if not self.pdf_processor:
            return ErrorAction("PDF processing not available")
        
        try:
            # Check if text PDF or scanned PDF
            is_text = self.pdf_processor.is_text_pdf(pdf_path)
            
            if is_text:
                # Extract text directly
                text_dict = self.pdf_processor.extract_text_by_page(pdf_path)
                if not text_dict or page not in text_dict:
                    return ErrorAction(f"Could not extract text from page {page}")
                
                # Split by lines to create table
                lines = text_dict[page].split('\n')
                table = [[line] for line in lines if line.strip()]
                
                if not table:
                    return ErrorAction("No text found on page")
                
                from .schemas import ImportTableAction
                return ImportTableAction(table, output_cell,
                                        f"Imported text from PDF page {page} ({len(table)} lines)",
                                        confidence=0.95)
            
            else:
                # Scanned PDF - render page and use OCR
                if not self.ocr or not self.image_processor:
                    return ErrorAction("OCR not available for scanned PDF")
                
                image_bytes = self.pdf_processor.render_page_to_image(pdf_path, page)
                if not image_bytes:
                    return ErrorAction(f"Could not render page {page}")
                
                # Save to temp file
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    tmp.write(image_bytes)
                    temp_path = tmp.name
                
                # Preprocess and OCR
                img = self.image_processor.load_image(temp_path)
                img = self.image_processor.auto_preprocess(img)
                self.image_processor.save_image(img, temp_path)
                
                table = self.ocr.recognize_table(temp_path)
                os.unlink(temp_path)
                
                if not table:
                    return ErrorAction("Could not extract table from PDF page")
                
                from .schemas import ImportTableAction
                return ImportTableAction(table, output_cell,
                                        f"Imported table from PDF page {page} ({len(table)} rows)",
                                        confidence=0.8)
        
        except Exception as e:
            logger.error(f"PDF import error: {e}")
            return ErrorAction(f"Error importing from PDF: {e}")
    
    # ========== Helper Methods ==========
    
    @staticmethod
    def _dict_to_action(action_dict: Dict[str, Any]) -> AIAction:
        """Convert dict response to AIAction object"""
        try:
            action_type_str = action_dict.get("action", "error")
            action_type = AIActionType(action_type_str)
            
            return AIAction(
                action=action_type,
                payload=action_dict.get("payload", {}),
                explanation=action_dict.get("explanation"),
                confidence=float(action_dict.get("confidence", 0.0)),
            )
        except Exception as e:
            logger.error(f"Error converting action: {e}")
            return ErrorAction(f"Invalid action format: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current AI system status"""
        return {
            "qwen": "ready" if self.qwen else "not initialized",
            "ocr": "ready" if self.ocr else "not initialized",
            "image_processor": "ready" if self.image_processor else "not initialized",
            "pdf_processor": "ready" if self.pdf_processor else "not initialized",
            "overall": "ready" if self.is_ready() else "not ready",
        }
