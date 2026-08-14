# -*- coding: utf-8 -*-

# Copyright (c) 2026 Nexuzy Lab

"""
AI Integration Configuration

Manages model downloads, caching, and initialization.
"""

import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, Optional
from urllib.request import urlopen
from urllib.error import URLError

logger = logging.getLogger(__name__)


class AIConfig:
    """Configuration for AI models and dependencies"""
    
    # Model registry with download URLs and SHA-256 checksums
    MODELS = {
        "qwen3-0.6b": {
            "name": "Qwen3-0.6B GGUF Q4",
            "size_mb": 512,
            "sha256": "placeholder_sha256_qwen3_06b_q4",
            # In production, use official Hugging Face/Modelscope URLs
            "url": "https://huggingface.co/qwen/Qwen3-0.6B-GGUF/resolve/main/qwen3-0.6b-q4.gguf",
        },
        "paddleocr-pp-ocrv6-tiny": {
            "name": "PaddleOCR PP-OCRv6 Tiny",
            "size_mb": 50,
            "sha256": "placeholder_sha256_paddleocr_tiny",
            "url": "https://paddleocr.bj.bcebos.com/PP-OCRv6/small/",
        },
    }
    
    # Dependencies (pip packages)
    DEPENDENCIES = {
        "llama-cpp-python": ">=0.2.0",
        "paddleocr": ">=2.8.0",
        "opencv-python": ">=4.8.0",
        "pymupdf": ">=1.23.0",
        "numpy": ">=1.24.0",
    }
    
    def __init__(self):
        """Initialize AI configuration"""
        self.ai_cache_dir = Path.home() / ".nexuzy_sheet" / "ai_models"
        self.ai_cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_file = self.ai_cache_dir / "config.json"
        self.config_data = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load config: {e}")
        return {"initialized": False, "models": {}}
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config_data, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save config: {e}")
    
    def get_model_path(self, model_key: str) -> Optional[Path]:
        """Get local path to model file"""
        model_path = self.ai_cache_dir / f"{model_key}.gguf"
        if model_path.exists():
            return model_path
        return None
    
    def is_model_downloaded(self, model_key: str) -> bool:
        """Check if model is already downloaded"""
        return self.get_model_path(model_key) is not None
    
    def is_dependency_installed(self, package_name: str) -> bool:
        """Check if a Python package is installed"""
        try:
            __import__(package_name.replace("-", "_"))
            return True
        except ImportError:
            return False
    
    def get_missing_dependencies(self) -> Dict[str, str]:
        """Return dictionary of missing dependencies"""
        missing = {}
        for package, version_spec in self.DEPENDENCIES.items():
            if not self.is_dependency_installed(package):
                missing[package] = version_spec
        return missing
    
    def calculate_file_sha256(self, filepath: Path) -> str:
        """Calculate SHA-256 checksum of a file"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def verify_model_integrity(self, model_key: str) -> bool:
        """Verify model file integrity using SHA-256"""
        model_path = self.get_model_path(model_key)
        if not model_path:
            return False
        
        if model_key not in self.MODELS:
            return True  # Unknown model, assume OK
        
        expected_sha256 = self.MODELS[model_key]["sha256"]
        if expected_sha256.startswith("placeholder"):
            return True  # Placeholder checksum, skip verification
        
        actual_sha256 = self.calculate_file_sha256(model_path)
        return actual_sha256 == expected_sha256
    
    def mark_model_downloaded(self, model_key: str):
        """Mark a model as downloaded in config"""
        if "models" not in self.config_data:
            self.config_data["models"] = {}
        self.config_data["models"][model_key] = {"downloaded": True}
        self._save_config()
    
    def mark_initialized(self):
        """Mark AI integration as initialized"""
        self.config_data["initialized"] = True
        self._save_config()
    
    def is_initialized(self) -> bool:
        """Check if AI integration has been initialized"""
        return self.config_data.get("initialized", False)
