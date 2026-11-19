# -*- coding: utf-8 -*-

from pathlib import Path

from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtWidgets import QApplication

from nxsheet.ai.engine import NexuzyAIController
from nxsheet.dialogs import SinglePageArea


def _app():
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    return app


def test_ai_controller_reports_missing_offline_model(tmp_path):
    _app()
    controller = NexuzyAIController(base_dir=str(tmp_path))

    action = controller.handle_text_request("Add GST of 18% to B5")

    assert action.action == "error"
    assert "Download" in action.explanation


def test_qwen_reasoner_parses_import_table_action(tmp_path):
    controller = NexuzyAIController(base_dir=str(tmp_path))
    payload = controller.reasoner._parse_response(
        '{"action":"import_table","cell":"A1","data":[["Name","Amount"],["Sales",10]]}'
    )

    assert payload["action"] == "import_table"
    assert payload["data"][1][1] == 10


def test_qwen_reasoner_rejects_executable_or_invalid_response(tmp_path):
    controller = NexuzyAIController(base_dir=str(tmp_path))

    payload = controller.reasoner._parse_response("print('do something')")

    assert payload["action"] == "error"


def test_ai_prompt_includes_product_and_developer_context(tmp_path):
    controller = NexuzyAIController(base_dir=str(tmp_path))
    prompt = controller.reasoner.prompt("What is this app?")

    assert "Nexuzy Lab" in prompt
    assert "https://sheet.nexuzy.in" in prompt
    assert "https://github.com/david0154/nexuzy_sheet" in prompt
    assert "formula" in prompt


def test_ai_table_title_and_header_styles_use_visible_cell_attributes():
    _app()
    from nxsheet.main_window import MainWindow

    window = MainWindow()
    start_row, start_col = 20, 4
    window._insert_table(
        [["Quarterly Report", ""], ["Item", "Sales"], ["Tea", 42]],
        "E21",
        styles={"title_row": 0, "header_row": 1},
    )

    attrs = window.grid.model.code_array.cell_attributes
    title = attrs[(start_row, start_col, window.grid.table)]
    title_next = attrs[(start_row, start_col + 1, window.grid.table)]
    header = attrs[(start_row + 1, start_col + 1, window.grid.table)]

    assert title.bgcolor == (31, 78, 121)
    assert title.textcolor == (255, 255, 255)
    assert title.fontweight == 75
    assert title_next.bgcolor == (31, 78, 121)
    assert header.bgcolor == (217, 225, 242)
    assert header.fontweight == 75


def test_main_window_has_ai_dock():
    app = _app()
    from nxsheet.main_window import MainWindow

    main_window = MainWindow()
    assert hasattr(main_window, "ai_dock")
    assert main_window.ai_dock.windowTitle() == "Ask Nexuzy AI"
    app.processEvents()


def test_core_requirements_stay_python_only_by_default():
    requirements = (Path(__file__).resolve().parents[1] / "requirements.txt").read_text(encoding="utf-8")
    root_requirements = (Path(__file__).resolve().parents[2] / "requirements.txt").read_text(encoding="utf-8")

    active_lines = [
        line.strip() for line in requirements.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    root_lines = [
        line.strip() for line in root_requirements.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    for package in [
        "opencv-python",
        "paddleocr",
        "ctransformers",
        "llama-cpp-python",
        "pyyaml",
    ]:
        assert package not in "\n".join(active_lines).lower()
        assert package not in "\n".join(root_lines).lower()

    assert "pymupdf" in "\n".join(active_lines).lower()


def test_ai_dock_can_be_toggled_from_view_menu():
    app = _app()
    from nxsheet.main_window import MainWindow

    main_window = MainWindow()
    assert hasattr(main_window.main_window_actions, "toggle_ai_dock")
    assert any(action.text() == "AI panel" for action in main_window.menuBar().view_menu.actions())
    assert main_window.ai_dock.isVisible()
    main_window.on_toggle_ai_dock(False)
    assert not main_window.ai_dock.isVisible()
    main_window.on_toggle_ai_dock(True)
    assert main_window.ai_dock.isVisible()
    app.processEvents()


def test_grid_data_changed_is_safe_when_main_window_is_deleted():
    app = _app()
    from nxsheet.main_window import MainWindow

    main_window = MainWindow()
    grid = main_window.grid
    del main_window

    grid.on_data_changed()
    app.processEvents()

    assert True


def test_pdf_export_handles_single_page_area():
    app = _app()
    from nxsheet.main_window import MainWindow

    main_window = MainWindow()
    main_window.print_area = SinglePageArea(top=0, left=0, bottom=2, right=2)

    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
    printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)

    main_window.on_paint_request(printer)

    assert True

