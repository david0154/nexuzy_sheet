# -*- coding: utf-8 -*-

# Copyright (c) 2026 Nexuzy Lab

"""
Qwen3-0.6B Language Model Interface

Local inference via llama.cpp GGUF quantization.
Handles:
- Formula generation
- Formula explanation
- Command understanding
- Data analysis guidance
"""

import logging
import json
from typing import Optional, Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from llama_cpp import Llama
    HAS_LLAMA_CPP = True
except ImportError:
    HAS_LLAMA_CPP = False
    logger.warning("llama-cpp-python not available. Qwen3 inference disabled.")


class QwenInterface:
    """Interface to Qwen3-0.6B model via llama.cpp"""
    
    # System prompt that constrains model to generate only valid actions
    SYSTEM_PROMPT = """You are Nexuzy Sheet AI, an assistant for spreadsheet operations.
Your role is to help users by generating formulas, explaining spreadsheet operations, and analyzing data.

IMPORTANT RULES:
1. ALWAYS respond with valid JSON in this exact format:
{
  "action": "formula|explain_formula|find|data_analysis|format|detect_duplicates|import_table|error",
  "payload": {...},
  "explanation": "human readable text",
  "confidence": 0.0 to 1.0
}

2. For formula generation: payload = {"cell": "A1", "formula": "=A2+B2"}
3. For explanations: payload = {"cell": "E5"}
4. For find: payload = {"query": "search term", "search_columns": [0, 1]}
5. For data analysis: payload = {"analysis_type": "type", "result": "result"}
6. For formatting: payload = {"cells": ["A1:B5"], "format": {"bold": true}}
7. For duplicates: payload = {"key_columns": [0, 1]}
8. For import: payload = {"data": [[row1], [row2]], "start_cell": "A1"}

3. Never generate arbitrary Python code.
4. Only generate valid spreadsheet formulas starting with =
5. Keep explanations clear and concise.
6. If you cannot help, return action: "error" with explanation.

You have access to spreadsheet context like current cell, nearby data, and sheet structure."""
    
    def __init__(self, model_path: str, n_ctx: int = 2048, n_threads: int = 4):
        """
        Initialize Qwen3 interface
        
        Args:
            model_path: Path to Qwen3-0.6B GGUF model file
            n_ctx: Context window size (tokens)
            n_threads: Number of CPU threads to use
        """
        if not HAS_LLAMA_CPP:
            raise RuntimeError("llama-cpp-python is not installed. Cannot initialize QwenInterface.")
        
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        try:
            self.model = Llama(
                model_path=str(model_path),
                n_ctx=n_ctx,
                n_threads=n_threads,
                verbose=False,
            )
            self.model_path = model_path
            self.n_ctx = n_ctx
            logger.info(f"Loaded Qwen3 model: {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def generate_response(self, prompt: str, max_tokens: int = 512, 
                         temperature: float = 0.3) -> Optional[str]:
        """
        Generate response from Qwen3
        
        Args:
            prompt: User prompt/command
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (lower = more deterministic)
        
        Returns:
            Generated text or None if failed
        """
        try:
            response = self.model(
                f"{self.SYSTEM_PROMPT}\n\nUser: {prompt}\n\nAssistant:",
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                stop=["\n\nUser:", "User:"],
            )
            
            return response["choices"][0]["text"].strip()
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return None
    
    def parse_action(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse AI response as JSON action
        
        Args:
            response_text: Raw text response from model
        
        Returns:
            Parsed action dict or None if invalid JSON
        """
        try:
            # Try to extract JSON from response
            # Model might include extra text, so look for JSON block
            if "{" in response_text and "}" in response_text:
                start = response_text.index("{")
                end = response_text.rindex("}") + 1
                json_str = response_text[start:end]
                return json.loads(json_str)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse action JSON: {e}")
        
        return None
    
    def handle_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Process user command and return structured AI action
        
        Args:
            command: User command/query
            context: Optional spreadsheet context (current cell, nearby data, etc.)
        
        Returns:
            Parsed AI action dict or None if failed
        """
        # Build prompt with context
        prompt = command
        if context:
            context_str = self._format_context(context)
            prompt = f"{context_str}\n\nUser request: {command}"
        
        # Generate response
        response_text = self.generate_response(prompt)
        if not response_text:
            return None
        
        # Parse as action
        action = self.parse_action(response_text)
        if not action:
            logger.warning(f"Could not parse action from: {response_text}")
            return None
        
        return action
    
    def explain_formula(self, formula: str) -> Optional[str]:
        """
        Explain what a formula does
        
        Args:
            formula: Spreadsheet formula (with or without =)
        
        Returns:
            Human-readable explanation
        """
        if not formula.startswith("="):
            formula = f"={formula}"
        
        prompt = f'Explain this spreadsheet formula in simple terms: {formula}\n\nKeep it brief and clear.'
        return self.generate_response(prompt, max_tokens=256)
    
    def generate_formula(self, requirement: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Generate a formula based on user requirement
        
        Args:
            requirement: What the user wants to calculate
            context: Optional context (cell range names, data types, etc.)
        
        Returns:
            Generated formula (starting with =) or None if failed
        """
        prompt = f"Generate a spreadsheet formula to: {requirement}\n\nRespond with ONLY the formula starting with ="
        
        response = self.generate_response(prompt, max_tokens=256, temperature=0.2)
        if not response:
            return None
        
        # Extract formula
        formula = response.strip()
        if not formula.startswith("="):
            if "=" in formula:
                formula = "=" + formula.split("=", 1)[1]
            else:
                return None
        
        return formula
    
    @staticmethod
    def _format_context(context: Dict[str, Any]) -> str:
        """Format spreadsheet context for prompt"""
        lines = []
        
        if "current_cell" in context:
            lines.append(f"Current cell: {context['current_cell']}")
        
        if "nearby_data" in context:
            lines.append(f"Nearby data: {context['nearby_data']}")
        
        if "column_headers" in context:
            lines.append(f"Headers: {', '.join(context['column_headers'])}")
        
        if "sheet_info" in context:
            lines.append(f"Sheet info: {context['sheet_info']}")
        
        return "\n".join(lines)
    
    def __del__(self):
        """Cleanup model on destruction"""
        if hasattr(self, 'model'):
            del self.model
