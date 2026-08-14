# -*- coding: utf-8 -*-

# Copyright (c) 2026 Nexuzy Lab

"""
AI Action Schemas

Defines the contract between AI and Nexuzy Sheet spreadsheet.
All AI responses are structured JSON actions validated against these schemas.
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field


class AIActionType(Enum):
    """Valid AI action types"""
    
    FORMULA = "formula"                    # Generate a formula
    EXPLAIN_FORMULA = "explain_formula"    # Explain existing formula
    FIND = "find"                          # Search for data
    DATA_ANALYSIS = "data_analysis"        # Analyze data
    FORMAT = "format"                      # Apply formatting
    DETECT_DUPLICATES = "detect_duplicates"  # Find duplicate rows
    IMPORT_TABLE = "import_table"          # Import OCR/PDF table
    ERROR = "error"                        # AI encountered an error


@dataclass
class AIAction:
    """
    Structured AI action response
    
    All AI responses conform to this format.
    The spreadsheet validates and executes these actions.
    """
    
    action: AIActionType
    payload: Dict[str, Any] = field(default_factory=dict)
    explanation: Optional[str] = None
    confidence: float = 0.0  # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "action": self.action.value,
            "payload": self.payload,
            "explanation": self.explanation,
            "confidence": self.confidence,
        }


class FormulaAction(AIAction):
    """Generate formula in a cell"""
    
    def __init__(self, cell: str, formula: str, explanation: str = "", confidence: float = 0.9):
        super().__init__(
            action=AIActionType.FORMULA,
            payload={"cell": cell, "formula": formula},
            explanation=explanation,
            confidence=confidence,
        )


class ExplainFormulaAction(AIAction):
    """Explain a formula"""
    
    def __init__(self, cell: str, explanation: str, confidence: float = 0.95):
        super().__init__(
            action=AIActionType.EXPLAIN_FORMULA,
            payload={"cell": cell},
            explanation=explanation,
            confidence=confidence,
        )


class FindAction(AIAction):
    """Search for data"""
    
    def __init__(self, query: str, search_columns: Optional[List[int]] = None, 
                 explanation: str = "", confidence: float = 0.9):
        payload = {"query": query}
        if search_columns is not None:
            payload["search_columns"] = search_columns
        super().__init__(
            action=AIActionType.FIND,
            payload=payload,
            explanation=explanation,
            confidence=confidence,
        )


class DataAnalysisAction(AIAction):
    """Perform data analysis"""
    
    def __init__(self, analysis_type: str, result: Any, 
                 explanation: str = "", confidence: float = 0.85):
        super().__init__(
            action=AIActionType.DATA_ANALYSIS,
            payload={"analysis_type": analysis_type, "result": result},
            explanation=explanation,
            confidence=confidence,
        )


class FormatAction(AIAction):
    """Apply cell formatting"""
    
    def __init__(self, cells: List[str], format_spec: Dict[str, Any], 
                 explanation: str = "", confidence: float = 0.9):
        super().__init__(
            action=AIActionType.FORMAT,
            payload={"cells": cells, "format": format_spec},
            explanation=explanation,
            confidence=confidence,
        )


class DetectDuplicatesAction(AIAction):
    """Detect duplicate rows"""
    
    def __init__(self, key_columns: List[int], explanation: str = "", confidence: float = 0.85):
        super().__init__(
            action=AIActionType.DETECT_DUPLICATES,
            payload={"key_columns": key_columns},
            explanation=explanation,
            confidence=confidence,
        )


class ImportTableAction(AIAction):
    """Import structured table from OCR/PDF"""
    
    def __init__(self, data: List[List[Any]], start_cell: str = "A1", 
                 explanation: str = "", confidence: float = 0.8):
        super().__init__(
            action=AIActionType.IMPORT_TABLE,
            payload={"data": data, "start_cell": start_cell},
            explanation=explanation,
            confidence=confidence,
        )


class ErrorAction(AIAction):
    """Error response"""
    
    def __init__(self, error_message: str, suggestion: Optional[str] = None):
        payload = {"error": error_message}
        if suggestion:
            payload["suggestion"] = suggestion
        super().__init__(
            action=AIActionType.ERROR,
            payload=payload,
            explanation=error_message,
            confidence=0.0,
        )
