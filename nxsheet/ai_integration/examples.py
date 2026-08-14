# -*- coding: utf-8 -*-

# Copyright (c) 2026 Nexuzy Lab

"""
AI Integration Examples

Demonstrates how to use Nexuzy Sheet AI components.
"""

from nxsheet.ai_integration import AICoordinator, AIActionType


def example_basic_command():
    """Example 1: Process a basic user command"""
    print("=" * 60)
    print("Example 1: Basic Command Processing")
    print("=" * 60)
    
    coordinator = AICoordinator(verbose=True)
    
    # User asks AI to generate a formula
    command = "Add 18% GST to cell B5 and put result in C5"
    
    action = coordinator.process_command(
        command,
        context={
            "current_cell": "C5",
            "column_headers": ["Item", "Price", "Total with GST"],
            "nearby_data": "[[Phone, 10000], [Charger, 500]]"
        }
    )
    
    print(f"\nCommand: {command}")
    print(f"AI Action: {action.action.value}")
    print(f"Explanation: {action.explanation}")
    print(f"Payload: {action.payload}")
    print(f"Confidence: {action.confidence:.1%}")


def example_formula_explanation():
    """Example 2: Explain a formula"""
    print("\n" + "=" * 60)
    print("Example 2: Formula Explanation")
    print("=" * 60)
    
    coordinator = AICoordinator(verbose=True)
    
    formula = "=SUM(B2:B10)/COUNT(B2:B10)"
    
    explanation = coordinator.explain_formula(formula)
    
    print(f"\nFormula: {formula}")
    print(f"Explanation:\n{explanation}")


def example_image_import():
    """Example 3: Import data from image"""
    print("\n" + "=" * 60)
    print("Example 3: Import from Image")
    print("=" * 60)
    
    coordinator = AICoordinator(verbose=True)
    
    # In real usage, you'd have an actual image file
    image_path = "/path/to/invoice.jpg"
    
    action = coordinator.import_from_image(image_path, output_cell="A1")
    
    print(f"\nImage: {image_path}")
    print(f"Action: {action.action.value}")
    print(f"Explanation: {action.explanation}")
    
    if action.action == AIActionType.IMPORT_TABLE:
        data = action.payload.get("data", [])
        print(f"Table size: {len(data)} rows × {len(data[0]) if data else 0} columns")
        if data:
            print("First row:", data[0])


def example_pdf_import():
    """Example 4: Import data from PDF"""
    print("\n" + "=" * 60)
    print("Example 4: Import from PDF")
    print("=" * 60)
    
    coordinator = AICoordinator(verbose=True)
    
    # Text PDF
    pdf_path = "/path/to/document.pdf"
    
    action = coordinator.import_from_pdf(pdf_path, output_cell="A1", page=0)
    
    print(f"\nPDF: {pdf_path}")
    print(f"Action: {action.action.value}")
    print(f"Explanation: {action.explanation}")


def example_status_check():
    """Example 5: Check AI system status"""
    print("\n" + "=" * 60)
    print("Example 5: System Status")
    print("=" * 60)
    
    coordinator = AICoordinator()
    status = coordinator.get_status()
    
    print("\nAI System Status:")
    for component, state in status.items():
        print(f"  {component}: {state}")


def example_analyze_action():
    """Example 6: Analyze different AI actions"""
    print("\n" + "=" * 60)
    print("Example 6: Different AI Action Types")
    print("=" * 60)
    
    coordinator = AICoordinator(verbose=True)
    
    commands = [
        ("Calculate total sales", "Generate formula to sum sales column"),
        ("Find high-value customers", "Search for data analysis"),
        ("Highlight headers", "Apply formatting"),
        ("Check for duplicates", "Detect duplicate rows"),
    ]
    
    for user_command, description in commands:
        print(f"\n{description}:")
        print(f"  User: {user_command}")
        
        action = coordinator.process_command(user_command)
        if action:
            print(f"  AI Action: {action.action.value}")
            print(f"  Confidence: {action.confidence:.1%}")


def example_context_aware():
    """Example 7: Context-aware command processing"""
    print("\n" + "=" * 60)
    print("Example 7: Context-Aware Processing")
    print("=" * 60)
    
    coordinator = AICoordinator(verbose=True)
    
    # Context from spreadsheet
    context = {
        "current_cell": "D5",
        "column_headers": ["Date", "Product", "Quantity", "Price", "Total"],
        "sheet_info": "Sales data for Q1 2026",
        "nearby_data": "[[2026-01-05, Keyboard, 2, 800], [2026-01-10, Mouse, 1, 500]]"
    }
    
    command = "Calculate the total price for this row"
    
    action = coordinator.process_command(command, context)
    
    print(f"\nContext-Aware Command:")
    print(f"  Command: {command}")
    print(f"  Current Cell: {context['current_cell']}")
    print(f"  Columns: {context['column_headers']}")
    print(f"  AI Response: {action.action.value if action else 'None'}")
    if action and action.payload:
        print(f"  Payload: {action.payload}")


if __name__ == "__main__":
    """Run examples"""
    
    print("\n" + "╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "NEXUZY SHEET AI INTEGRATION EXAMPLES" + " " * 12 + "║")
    print("╚" + "=" * 58 + "╝")
    
    try:
        # Run examples
        example_status_check()
        example_basic_command()
        example_formula_explanation()
        example_analyze_action()
        example_context_aware()
        
        # These require actual files
        # example_image_import()
        # example_pdf_import()
        
        print("\n" + "=" * 60)
        print("All examples completed!")
        print("=" * 60)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nNote: Some examples require:")
        print("  - Dependencies installed: pip install llama-cpp-python paddleocr opencv-python pymupdf")
        print("  - Qwen3 model downloaded to ~/.nexuzy_sheet/ai_models/")
        print("  - Image/PDF files for document import examples")

