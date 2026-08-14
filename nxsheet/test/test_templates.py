# -*- coding: utf-8 -*-
"""
Test suite for NXSheet template system and PDF extraction
"""

import json
import pytest
from pathlib import Path
from nxsheet.templates import TemplateManager
from nxsheet.ai.engine import NexuzyAIController


class TestTemplateManager:
    """Test the template management system"""

    def test_list_templates(self):
        """Verify all templates are available"""
        templates = TemplateManager.list_templates()
        assert len(templates) == 5
        assert "invoice" in templates
        assert "attendance" in templates
        assert "ledger" in templates
        assert "payroll" in templates
        assert "budget" in templates

    def test_get_template_invoice(self):
        """Verify invoice template structure"""
        template = TemplateManager.get_template("invoice")
        assert template is not None
        assert template["name"] == "Invoice"
        assert "headers" in template
        assert "sample_data" in template
        assert "merged_cells" in template
        assert len(template["headers"]) > 0
        assert len(template["sample_data"]) > 0

    def test_get_template_attendance(self):
        """Verify attendance template structure"""
        template = TemplateManager.get_template("attendance")
        assert template is not None
        assert template["name"] == "Attendance Register"
        assert len(template["headers"]) == 4
        assert len(template["sample_data"]) == 3

    def test_get_template_ledger(self):
        """Verify ledger template structure"""
        template = TemplateManager.get_template("ledger")
        assert template is not None
        assert template["name"] == "General Ledger"
        assert "styling" in template

    def test_get_template_payroll(self):
        """Verify payroll template structure"""
        template = TemplateManager.get_template("payroll")
        assert template is not None
        assert template["name"] == "Payroll Sheet"

    def test_get_template_budget(self):
        """Verify budget template structure"""
        template = TemplateManager.get_template("budget")
        assert template is not None
        assert template["name"] == "Budget Planning"

    def test_template_display_names(self):
        """Verify all templates have display names"""
        names = TemplateManager.get_template_display_names()
        assert len(names) == 5
        assert names["invoice"] == "Invoice"
        assert names["attendance"] == "Attendance Register"
        assert names["ledger"] == "General Ledger"
        assert names["payroll"] == "Payroll Sheet"
        assert names["budget"] == "Budget Planning"

    def test_apply_template_to_sheet(self):
        """Verify template can be applied to spreadsheet"""
        sheet_data = {"data": [["Test", "Data"]]}
        result = TemplateManager.apply_template_to_sheet("invoice", sheet_data)
        
        assert len(result) > 0
        # Should have headers + data
        assert len(result) > len(sheet_data["data"])

    def test_get_styling_config_invoice(self):
        """Verify invoice template styling"""
        styling = TemplateManager.get_styling_config("invoice")
        assert "title_row" in styling
        assert "header_row" in styling
        assert "data_start_row" in styling
        assert "currency_columns" in styling

    def test_get_styling_config_attendance(self):
        """Verify attendance template styling"""
        styling = TemplateManager.get_styling_config("attendance")
        assert "centered_columns" in styling
        assert len(styling["centered_columns"]) > 0


class TestNexuzyAIControllerWithTemplates:
    """Test AI controller integration with templates"""

    def test_controller_has_template_manager(self):
        """Verify controller has template manager"""
        controller = NexuzyAIController(".")
        assert hasattr(controller, "template_manager")
        assert controller.template_manager is not None

    def test_get_available_templates(self):
        """Verify controller can list templates"""
        controller = NexuzyAIController(".")
        templates = controller.get_available_templates()
        
        assert len(templates) == 5
        assert "Invoice" in templates.values()
        assert "Attendance Register" in templates.values()

    def test_load_template_invoice(self):
        """Verify invoice template loading via controller"""
        controller = NexuzyAIController(".")
        action = controller.load_template("invoice")
        
        assert action.action == "import_table"
        assert action.data is not None
        assert len(action.data) > 0
        assert action.cell == "A1"

    def test_load_template_with_custom_data(self):
        """Verify template loading with custom data"""
        controller = NexuzyAIController(".")
        custom_data = [["Custom Item", 5, 1000, 18, "=C1*B1*(1+D1/100)"]]
        action = controller.load_template("invoice", data=custom_data)
        
        assert action.action == "import_table"
        assert len(action.data) > 0

    def test_load_template_invalid(self):
        """Verify error handling for invalid template"""
        controller = NexuzyAIController(".")
        action = controller.load_template("nonexistent")
        
        assert action.action == "error"
        assert "not found" in action.explanation.lower()

    def test_handle_text_request_gst(self):
        """Verify AI text handling for GST calculation"""
        controller = NexuzyAIController(".")
        action = controller.handle_text_request("Add GST of 18% to B5")
        
        assert action.action == "formula"
        assert "1.18" in action.formula or "18" in action.formula

    def test_handle_text_request_average(self):
        """Verify AI text handling for average calculation"""
        controller = NexuzyAIController(".")
        action = controller.handle_text_request("average of January to March")
        
        assert action.action == "formula"
        assert "AVERAGE" in action.formula or "average" in action.formula.lower()

    def test_invoice_processor_convert_to_sheet_format(self):
        """Verify invoice processor sheet format conversion"""
        from nxsheet.ai.engine import InvoiceProcessor, OCRProcessor
        
        ocr = OCRProcessor(".")
        processor = InvoiceProcessor(ocr)
        
        invoice_data = {
            "invoice_number": "INV001",
            "date": "2026-08-14",
            "total_amount": 5000.00,
            "items": [
                {"description": "Item 1", "quantity": 1, "unit_price": 5000},
            ],
        }
        
        sheet_data = processor.convert_to_sheet_format(invoice_data)
        assert len(sheet_data) > 0
        # Should have invoice details + line items header + items
        assert any("Invoice" in str(row) for row in sheet_data)


class TestPDFTemplateIntegration:
    """Test PDF extraction with template population"""

    def test_handle_pdf_with_template_method_exists(self):
        """Verify PDF with template method exists"""
        controller = NexuzyAIController(".")
        assert hasattr(controller, "handle_pdf_with_template")

    def test_pdf_invoice_extraction_structure(self):
        """Verify PDF invoice extraction returns proper structure"""
        from nxsheet.ai.engine import InvoiceProcessor, OCRProcessor
        
        ocr = OCRProcessor(".")
        processor = InvoiceProcessor(ocr)
        
        # Mock invoice data
        invoice_data = {
            "invoice_number": "INV123",
            "date": "2026-08-14",
            "total_amount": 10000,
            "vendor": "ABC Company",
            "customer": "XYZ Ltd",
            "items": [],
        }
        
        sheet_format = processor.convert_to_sheet_format(invoice_data)
        assert len(sheet_format) > 0
        assert "Invoice Details" in sheet_format[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
