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


def test_ai_controller_generates_formula_action(tmp_path):
    _app()
    controller = NexuzyAIController(base_dir=str(tmp_path))

    action = controller.handle_text_request("Add GST of 18% to B5")

    assert action.action == "formula"
    assert action.formula == "=B5*1.18"
    assert action.cell == "B5"


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

