import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event
from unittest.mock import patch

from nxsheet.ai.engine import LocalModelManager, NexuzyAIController


def _write_valid_model(manager):
    with manager.qwen_gguf.open("wb") as model_file:
        model_file.truncate(400_000_000)


def _write_runtime(manager):
    manager.llama_cli.parent.mkdir(parents=True, exist_ok=True)
    manager.llama_cli.write_bytes(b"runtime")


def test_existing_model_is_reused_without_download(tmp_path):
    manager = LocalModelManager(str(tmp_path))
    _write_valid_model(manager)

    with patch("nxsheet.ai.engine.hf_hub_download") as download:
        result = manager.download_qwen_model(auto_download=True)

    assert result["status"] == "ready"
    download.assert_not_called()


def test_partial_model_is_not_treated_as_ready(tmp_path):
    manager = LocalModelManager(str(tmp_path))
    manager.qwen_gguf.write_bytes(b"x" * 100_000_001)

    assert manager.model_ready() is False


def test_url_download_rejects_html_or_truncated_response(tmp_path):
    manager = LocalModelManager(str(tmp_path))

    with patch("nxsheet.ai.engine.hf_hub_download", None), \
            patch("nxsheet.ai.engine.urlretrieve") as retrieve:
        retrieve.side_effect = lambda url, path, reporthook: Path(path).write_bytes(b"error page")
        result = manager.download_qwen_model(auto_download=True)

    assert result["status"] == "error"
    assert "smaller than expected" in result["error"]


def test_missing_model_is_not_downloaded_without_explicit_request(tmp_path):
    manager = LocalModelManager(str(tmp_path))

    with patch("nxsheet.ai.engine.hf_hub_download") as download:
        result = manager.download_qwen_model(auto_download=False)

    assert result["status"] == "manual_required"
    download.assert_not_called()


def test_model_download_reports_start_and_progress(tmp_path):
    manager = LocalModelManager(str(tmp_path))
    messages = []

    def download_model(**kwargs):
        _write_valid_model(manager)
        return str(manager.qwen_gguf)

    with patch("nxsheet.ai.engine.hf_hub_download", side_effect=download_model):
        result = manager.download_qwen_model(
            auto_download=True, progress_callback=messages.append)

    assert result["status"] == "downloaded"
    assert messages[0] == "Connecting to Hugging Face; checking model file..."
    assert "Starting download from Hugging Face..." in messages


def test_progress_bar_stays_enabled_without_a_terminal():
    from nxsheet.ai.engine import _hf_progress_tqdm

    messages = []
    # huggingface_hub passes disable=True when stderr is not a terminal, which
    # is the normal case inside the packaged GUI window.
    bar = _hf_progress_tqdm(messages.append)(total=100, disable=True)
    try:
        bar.update(50)
    finally:
        bar.close()

    assert messages == ["Downloading AI model: 0%",
                        "Downloading AI model: 50%"]


def test_download_forwards_huggingface_progress(tmp_path):
    manager = LocalModelManager(str(tmp_path))
    messages = []

    def download_model(**kwargs):
        bar = kwargs["tqdm_class"](total=4, desc="model")
        try:
            for _ in range(4):
                bar.update(1)
        finally:
            bar.close()
        _write_valid_model(manager)
        return str(manager.qwen_gguf)

    with patch("nxsheet.ai.engine.hf_hub_download",
               side_effect=download_model):
        result = manager.download_qwen_model(
            auto_download=True, progress_callback=messages.append)

    assert result["status"] == "downloaded"
    assert "Downloading AI model: 50%" in messages
    assert messages[-1] == "Downloading AI model: 100%"


def test_startup_does_not_start_model_setup(monkeypatch):
    from PyQt6.QtWidgets import QApplication
    from nxsheet.main_window import MainWindow

    app = QApplication.instance() or QApplication([])
    scheduled = []
    monkeypatch.setattr("nxsheet.main_window.QTimer.singleShot",
                        lambda delay, callback: scheduled.append(callback))
    window = MainWindow()

    assert not any(getattr(callback, "__name__", "") == "start_ai_setup"
                   for callback in scheduled)
    assert not getattr(window, "_ai_setup_running", False)
    window.close()
    app.processEvents()


def test_download_progress_updates_and_closes_dialog(monkeypatch):
    from PyQt6.QtWidgets import QApplication, QProgressDialog
    from nxsheet.main_window import MainWindow

    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    dialog = QProgressDialog("Preparing", "", 0, 100, window)
    window._ai_progress_dialog = dialog
    window._ai_download_percent = 0

    window.on_ai_download_progress("Downloading AI model: 37%")
    app.processEvents()

    assert dialog.labelText() == "Downloading AI model: 37%"
    assert dialog.value() == 37

    window.on_ai_stack_ready({"model": {"status": "downloaded"}})
    app.processEvents()

    assert window._ai_progress_dialog is None
    assert not dialog.isVisible()
    window.close()


def test_explicit_setup_downloads_missing_model_once(tmp_path):
    controller = NexuzyAIController(str(tmp_path))
    manager = controller.model_manager
    manager.llama_cli.parent.mkdir(parents=True, exist_ok=True)
    manager.llama_cli.write_bytes(b"runtime")

    def download_model(**kwargs):
        _write_valid_model(manager)
        return str(manager.qwen_gguf)

    with patch("nxsheet.ai.engine.hf_hub_download", side_effect=download_model) as download:
        result = controller.ensure_local_stack()

    assert result["model"]["status"] == "downloaded"
    assert result["runtime"]["qwen_model"] is True
    assert result["runtime"]["llama.cpp"] is True
    assert result["packages"]["status"] == "ready"
    download.assert_called_once()


def test_llama_runtime_is_downloaded_and_unpacked(tmp_path):
    import zipfile

    manager = LocalModelManager(str(tmp_path))
    messages = []

    def fake_retrieve(url, path, reporthook=None):
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr(manager.llama_cli.name, "runtime")
        if reporthook is not None:
            reporthook(1, 100, 100)

    with patch("nxsheet.ai.engine.urlretrieve",
               side_effect=fake_retrieve) as retrieve:
        result = manager.download_llama_runtime(
            progress_callback=messages.append)

    assert result["status"] == "downloaded"
    assert manager.llama_runtime_ready
    assert "Installing the local AI runtime..." in messages
    retrieve.assert_called_once()


def test_existing_llama_runtime_is_reused(tmp_path):
    manager = LocalModelManager(str(tmp_path))
    _write_runtime(manager)

    with patch("nxsheet.ai.engine.urlretrieve") as retrieve:
        result = manager.download_llama_runtime()

    assert result["status"] == "ready"
    retrieve.assert_not_called()


def test_missing_runtime_is_reported_before_generating(tmp_path):
    controller = NexuzyAIController(str(tmp_path))
    _write_valid_model(controller.model_manager)

    action = controller.handle_text_request("Sum A1 to A3")

    assert action.action == "error"
    assert "runtime" in action.explanation.lower()


def test_local_model_runs_through_llama_cli(tmp_path):
    controller = NexuzyAIController(str(tmp_path))
    manager = controller.model_manager
    _write_valid_model(manager)
    _write_runtime(manager)
    completed = subprocess.CompletedProcess(
        [], 0,
        '{"action":"formula","cell":"A4","formula":"=SUM(A1:A3)"}',
        "")

    with patch("nxsheet.ai.engine.subprocess.run",
               return_value=completed) as run:
        action = controller.handle_text_request("Sum A1 to A3 in A4")

    assert action.action == "formula"
    assert action.formula == "=SUM(A1:A3)"
    command = run.call_args.args[0]
    assert command[0] == str(manager.llama_cli)
    assert str(manager.qwen_gguf) in command
    assert "-sys" in command and "-st" in command


def test_prompt_echo_is_stripped_from_the_reply(tmp_path):
    controller = NexuzyAIController(str(tmp_path))
    manager = controller.model_manager
    _write_valid_model(manager)
    _write_runtime(manager)
    system, user = controller.reasoner._build_messages(
        "Sum A1 to A3", {"sheet": {"data": [[1], [2]]}})
    reply = '{"action":"formula","cell":"A4","formula":"=SUM(A1:A3)"}'
    completed = subprocess.CompletedProcess(
        [], 0, f"Loading model...\n> {user}\n```json\n{reply}\n```\n", "")

    with patch("nxsheet.ai.engine.subprocess.run", return_value=completed):
        action = controller.handle_text_request(
            "Sum A1 to A3", {"data": [[1], [2]]})

    assert action.action == "formula"
    assert action.formula == "=SUM(A1:A3)"


def test_list_cell_and_styles_are_normalized(tmp_path):
    controller = NexuzyAIController(str(tmp_path))

    payload = controller.reasoner._parse_response(
        '{"action":"formula","cell":[0,0],"formula":"=SUM(A1:A3)",'
        '"styles":[]}')

    assert payload["cell"] == "A1"
    assert "styles" not in payload


def test_concurrent_setup_requests_do_not_duplicate_download(tmp_path):
    manager = LocalModelManager(str(tmp_path))
    download_started = Event()
    allow_download_to_finish = Event()

    def download_model(**kwargs):
        download_started.set()
        assert allow_download_to_finish.wait(timeout=120)
        _write_valid_model(manager)
        return str(manager.qwen_gguf)

    with patch("nxsheet.ai.engine.hf_hub_download", side_effect=download_model) as download:
        with ThreadPoolExecutor(max_workers=2) as executor:
            first = executor.submit(manager.download_qwen_model, auto_download=True)
            assert download_started.wait(timeout=5)
            second = executor.submit(manager.download_qwen_model, auto_download=True)
            allow_download_to_finish.set()
            results = [first.result(timeout=120), second.result(timeout=120)]

    assert {result["status"] for result in results} == {"downloaded", "ready"}
    download.assert_called_once()


def test_fenced_reply_with_loose_data_field_is_repaired(tmp_path):
    controller = NexuzyAIController(str(tmp_path))

    payload = controller.reasoner._parse_response(
        '```json\n{\n  "action": "formula",\n  "cell": "b2",\n'
        '  "formula": "=SUM(A1:A3)",\n  "data": "A1:A3",\n'
        '  "styles": ["SUM", "A1:A3"]\n}\n```\n\n[ Prompt: 129.2 t/s ]\nExiting...')

    assert payload["action"] == "formula"
    assert payload["cell"] == "B2"
    assert payload["formula"] == "=SUM(A1:A3)"
    assert "data" not in payload
    assert "styles" not in payload


def test_bare_array_reply_becomes_an_import(tmp_path):
    controller = NexuzyAIController(str(tmp_path))

    payload = controller.reasoner._parse_response(
        '[["Fruit", "Price"], ["Apple", 2]]')

    assert payload["action"] == "import_table"
    assert payload["data"] == [["Fruit", "Price"], ["Apple", 2]]


def test_ragged_and_oversized_tables_are_normalized(tmp_path):
    controller = NexuzyAIController(str(tmp_path))
    rows = [[1, 2, 3], [4]] + [[row] for row in range(200)]

    payload = controller.reasoner._parse_response(
        json.dumps({"action": "import_table", "data": rows}))

    assert payload["action"] == "import_table"
    assert payload["data"][1] == [4, "", ""]
    assert len(payload["data"]) == controller.reasoner.MAX_TABLE_ROWS


def test_missing_formula_and_unreadable_reply_report_errors(tmp_path):
    controller = NexuzyAIController(str(tmp_path))

    no_formula = controller.reasoner._parse_response(
        '{"action": "formula", "cell": "A4"}')
    no_json = controller.reasoner._parse_response("I cannot help with that.")

    assert no_formula["action"] == "error"
    assert no_json["action"] == "error"


def test_prompt_carries_product_identity_and_the_whole_formula_library(tmp_path):
    from nxsheet import VERSION
    from nxsheet.lib.excel_functions import EXCEL_FUNCTION_NAMES

    controller = NexuzyAIController(str(tmp_path))
    system, _ = controller.reasoner._build_messages(
        "what does vlookup do?", {"sheet": {"active_cell": "A1"}})

    assert "Nexuzy AI" in system
    assert VERSION in system
    assert "Nexuzy Lab" in system
    assert "Manoj Konar" in system
    assert "https://sheet.nexuzy.in" in system
    assert all(f"{name}(" in system for name in EXCEL_FUNCTION_NAMES)
    # A function named in the request is described, not just listed.
    assert "Searches the first column" in system


def test_legal_documents_are_shipped_and_locatable():
    from nxsheet.dialogs import LEGAL_DOCUMENTS, legal_document_path

    for filename, _title in LEGAL_DOCUMENTS:
        path = legal_document_path(filename)
        assert path is not None, filename
        assert len(path.read_text(encoding="utf-8")) > 500


def test_product_and_formula_questions_are_answered_without_the_model(tmp_path):
    from nxsheet import AI_NAME, COMPANY, VERSION

    controller = NexuzyAIController(str(tmp_path))

    identity = controller.direct_answer("who are you and who made this app?")
    assert AI_NAME in identity and COMPANY in identity and VERSION in identity
    assert "Manoj Konar" in identity

    vlookup = controller.direct_answer("what does VLOOKUP do?")
    assert "VLOOKUP(value, table, col_index" in vlookup
    assert "Searches the first column" in vlookup

    count = controller.direct_answer("how many formulas can you use?")
    assert "107" in count and "TEXTJOIN" in count

    # A request naming a cell stays a sheet action for the model.
    assert controller.direct_answer("what is the total in A1?") is None
    assert controller.direct_answer("sum A1 to A5 in A6") is None


def test_cell_named_in_the_request_wins_over_the_active_cell(tmp_path):
    controller = NexuzyAIController(str(tmp_path))
    reasoner = controller.reasoner

    assert reasoner._preferred_cell(
        "add the values in A1 to A3 and put the total in A4") == "A4"
    assert reasoner._preferred_cell("total A1 to A5 in A6") == "A6"
    assert reasoner._preferred_cell("sum A1 to A5") is None
    assert reasoner._preferred_cell("put it in B2",
                                    {"sheet": {"current_cell": "B2"}}) is None
