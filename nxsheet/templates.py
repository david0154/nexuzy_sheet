# -*- coding: utf-8 -*-
"""
NXSheet Template System
Provides pre-built templates with styling for common business documents
"""

from typing import Dict, List, Any, Optional
from pathlib import Path


class TemplateManager:
    """Manages spreadsheet templates with styling and layouts"""

    TEMPLATES = {
        "invoice": {
            "name": "Invoice",
            "description": "Professional invoice template with itemized billing",
            "headers": [
                ["NEXUZY BUSINESS SERVICES"],
                ["", "", "", "INVOICE"],
                ["123 Business Avenue", "", "", "Invoice #", "INV-2026-001"],
                ["City, State 00000", "", "", "Date", "2026-08-14"],
                ["support@nexuzy.local", "", "", "Due Date", "2026-09-14"],
                ["", "", "", "", ""],
                ["Bill To:", "", "", "", ""],
                ["Acme Industries", "", "", "", ""],
                ["P.O. Box 515", "", "", "", ""],
                ["", "", "", "", ""],
                ["Item Description", "Qty", "Unit Price", "Tax %", "Amount"],
            ],
            "sample_data": [
                ["Consulting & Strategy", 1, 5000, 18, "=C12*(1+D12/100)"],
                ["Software License", 12, 500, 18, "=C13*B13*(1+D13/100)"],
                ["Maintenance & Support", 1, 2000, 0, "=C14*B14"],
                ["", "", "", "Subtotal:", "=SUM(E12:E14)"],
                ["", "", "", "Tax:", "=SUMPRODUCT(C12:C14,B12:B14,D12:D14/100)"],
                ["", "", "", "Total:", "=SUM(E15:E16)"],
            ],
            "merged_cells": [
                (0, 0, 0, 11),
                (1, 3, 1, 11),
                (6, 0, 6, 4),
                (7, 0, 8, 4),
                (10, 0, 10, 4),
            ],
            "styling": {
                "title_row": 0,
                "header_row": 10,
                "data_start_row": 11,
                "font_size": 12,
                "currency_columns": [2, 4],
                "centered_columns": [1, 3],
                "brand_title": "NEXUZY BUSINESS SERVICES",
                "subtitle": "Invoice",
            }
        },
        "attendance": {
            "name": "Attendance Register",
            "description": "Employee attendance tracking with dates and status",
            "headers": [
                ["TEAM ATTENDANCE REGISTER"],
                ["Month", "August 2026", "", "Department", "Operations"],
                ["", "", "", "", ""],
                ["Employee ID", "Name", "01", "02", "03", "04", "05", "06", "07", "08",
                 "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
                 "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "Present"],
            ],
            "sample_data": [
                ["EMP001", "John Doe", "P", "P", "A", "P", "P", "P", "P", "P", "P", "P",
                 "P", "P", "A", "P", "P", "P", "P", "P", "P", "P", "P", "P", "P", "P", "P",
                 "P", "P", "P", "P", "P", "P", "P", "=COUNTIF(C5:AG5,\"P\")"],
                ["EMP002", "Jane Smith", "P", "P", "P", "P", "P", "A", "P", "P", "P", "P",
                 "P", "P", "P", "P", "P", "P", "A", "P", "P", "P", "P", "P", "P", "P", "P",
                 "P", "P", "P", "P", "P", "P", "P", "=COUNTIF(C6:AG6,\"P\")"],
                ["EMP003", "Aisha Khan", "P", "P", "P", "A", "P", "P", "P", "P", "P", "P",
                 "P", "P", "P", "P", "P", "P", "P", "P", "P", "A", "P", "P", "P", "P", "P",
                 "P", "P", "P", "P", "P", "P", "P", "=COUNTIF(C7:AG7,\"P\")"],
            ],
            "merged_cells": [
                (0, 0, 0, 33),
                (1, 1, 1, 2),
                (1, 3, 1, 4),
            ],
            "styling": {
                "title_row": 0,
                "header_row": 3,
                "data_start_row": 4,
                "font_size": 10,
                "centered_columns": list(range(2, 34)),
                "brand_title": "TEAM ATTENDANCE REGISTER",
            }
        },
        "ledger": {
            "name": "General Ledger",
            "description": "Financial transaction ledger with debit/credit columns",
            "headers": [
                ["GENERAL LEDGER"],
                ["Account Name:", "Sales Account", "", "Period:", "August 2026"],
                ["", "", "", "", ""],
                ["Date", "Reference", "Description", "Debit", "Credit", "Balance"],
            ],
            "sample_data": [
                ["2026-08-01", "OPEN", "Opening Balance", "", "", 50000],
                ["2026-08-05", "INV-002", "Invoice #INV-002", 25000, "", "=F5+D6"],
                ["2026-08-10", "CHQ-001", "Customer Payment", "", 10000, "=F6-E7"],
                ["2026-08-15", "INV-003", "Invoice #INV-003", 15000, "", "=F7+D8"],
                ["2026-08-20", "CHQ-002", "Vendor Settlement", "", 5000, "=F8-E9"],
                ["", "", "TOTAL", "=SUM(D6:D9)", "=SUM(E6:E9)", "=SUM(F5:F8)"],
            ],
            "merged_cells": [
                (0, 0, 0, 5),
                (1, 0, 1, 1),
                (1, 2, 1, 2),
                (1, 3, 1, 4),
            ],
            "styling": {
                "title_row": 0,
                "header_row": 3,
                "data_start_row": 4,
                "font_size": 11,
                "currency_columns": [3, 4, 5],
                "date_columns": [0],
                "brand_title": "GENERAL LEDGER",
            }
        },
        "payroll": {
            "name": "Payroll Sheet",
            "description": "Employee salary and deductions payroll template",
            "headers": [
                ["PAYROLL SUMMARY"],
                ["Month", "August 2026", "", "Department", "Sales"],
                ["", "", "", "", ""],
                ["Emp ID", "Name", "Basic", "HRA", "DA", "Gross", "Income Tax", "PF", "Net Salary"],
            ],
            "sample_data": [
                ["EMP001", "John Doe", 25000, 5000, 5000, "=C5+D5+E5", "=F5*0.10", "=F5*0.12", "=F5-G5-H5"],
                ["EMP002", "Jane Smith", 30000, 6000, 6000, "=C6+D6+E6", "=F6*0.10", "=F6*0.12", "=F6-G6-H6"],
                ["EMP003", "Mike Wilson", 28000, 5600, 5600, "=C7+D7+E7", "=F7*0.10", "=F7*0.12", "=F7-G7-H7"],
                ["", "TOTAL", "=SUM(C5:C7)", "=SUM(D5:D7)", "=SUM(E5:E7)", "=SUM(F5:F7)",
                 "=SUM(G5:G7)", "=SUM(H5:H7)", "=SUM(I5:I7)"],
            ],
            "merged_cells": [
                (0, 0, 0, 8),
                (1, 0, 1, 1),
                (1, 3, 1, 4),
            ],
            "styling": {
                "title_row": 0,
                "header_row": 3,
                "data_start_row": 4,
                "font_size": 11,
                "currency_columns": [2, 3, 4, 5, 6, 7, 8],
                "bold_rows": [7],
                "brand_title": "PAYROLL SUMMARY",
            }
        },
        "budget": {
            "name": "Budget Planning",
            "description": "Budget vs Actual expense tracking",
            "headers": [
                ["BUDGET PLANNING & TRACKING"],
                ["Year", "2026", "", "Department", "Operations"],
                ["", "", "", "", ""],
                ["Category", "Budgeted Amount", "Actual Spent", "Variance", "% Variance"],
            ],
            "sample_data": [
                ["Salaries", 500000, 510000, "=C5-B5", "=D5/B5*100"],
                ["Office Supplies", 50000, 45000, "=C6-B6", "=D6/B6*100"],
                ["Travel", 100000, 95000, "=C7-B7", "=D7/B7*100"],
                ["Utilities", 60000, 62000, "=C8-B8", "=D8/B8*100"],
                ["Maintenance", 80000, 78000, "=C9-B9", "=D9/B9*100"],
                ["", "=SUM(B5:B9)", "=SUM(C5:C9)", "=C10-B10", "=D10/B10*100"],
            ],
            "merged_cells": [
                (0, 0, 0, 4),
                (1, 0, 1, 1),
                (1, 3, 1, 4),
            ],
            "styling": {
                "title_row": 0,
                "header_row": 3,
                "data_start_row": 4,
                "font_size": 11,
                "currency_columns": [1, 2, 3],
                "percentage_columns": [4],
                "bold_rows": [9],
                "brand_title": "BUDGET PLANNING & TRACKING",
            }
        },
    }

    @classmethod
    def get_template(cls, template_name: str) -> Optional[Dict[str, Any]]:
        """Get a template by name"""
        return cls.TEMPLATES.get(template_name.lower())

    @classmethod
    def get_template_layout(cls, template_name: str) -> Dict[str, Any]:
        """Return template data together with merge regions and layout hints."""
        template = cls.get_template(template_name)
        if not template:
            return {"data": [], "merged_cells": [], "styles": {}}

        return {
            "data": cls.apply_template_to_sheet(template_name, {"data": []}),
            "merged_cells": template.get("merged_cells", []),
            "styles": template.get("styling", {}),
        }

    @classmethod
    def list_templates(cls) -> List[str]:
        """List all available templates"""
        return list(cls.TEMPLATES.keys())

    @classmethod
    def get_template_display_names(cls) -> Dict[str, str]:
        """Get display names for all templates"""
        return {key: value["name"] for key, value in cls.TEMPLATES.items()}

    @classmethod
    def apply_template_to_sheet(cls, template_name: str, sheet_data: Dict[str, Any]) -> List[List[Any]]:
        """Apply a template to spreadsheet with data"""
        template = cls.get_template(template_name)
        if not template:
            return []

        result = []
        
        # Add headers
        for row in template.get("headers", []):
            result.append(row[:])

        # Add sample data or provided data
        data_rows = sheet_data.get("data", template.get("sample_data", []))
        for row in data_rows:
            result.append(row[:])

        return result

    @classmethod
    def get_styling_config(cls, template_name: str) -> Dict[str, Any]:
        """Get styling configuration for a template"""
        template = cls.get_template(template_name)
        if not template:
            return {}
        return template.get("styling", {})
