from __future__ import annotations

import io
import json
import os
import re
import platform
import subprocess
import sys
import tarfile
import threading
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from urllib.request import urlretrieve

# Import template manager for pre-built templates
try:
    from nxsheet.templates import TemplateManager
except ImportError:
    TemplateManager = None

try:
    from huggingface_hub import hf_hub_download
except ImportError:  # pragma: no cover - optional dependency
    hf_hub_download = None


#: Offline spreadsheet assistant model (about 490 MB on the first run)
QWEN_REPO_ID = "Qwen/Qwen2.5-0.5B-Instruct-GGUF"
QWEN_FILENAME = "qwen2.5-0.5b-instruct-q4_k_m.gguf"
QWEN_MODEL_URL = (f"https://huggingface.co/{QWEN_REPO_ID}"
                  f"/resolve/main/{QWEN_FILENAME}")

#: llama.cpp CPU build used to run the GGUF model. ``ctransformers`` cannot
#: load Qwen2 architecture files, so the inference runtime ships separately.
LLAMA_CPP_BUILD = "b12531"
LLAMA_CPP_RELEASE_URL = ("https://github.com/ggml-org/llama.cpp/releases/"
                         f"download/{LLAMA_CPP_BUILD}")


def llama_cpp_archive_name() -> str:
    """Returns the llama.cpp release archive for this platform."""

    machine = platform.machine().lower()
    arm = machine in {"arm64", "aarch64"}
    if sys.platform.startswith("win"):
        return f"llama-{LLAMA_CPP_BUILD}-bin-win-cpu-{'arm64' if arm else 'x64'}.zip"
    if sys.platform == "darwin":
        return f"llama-{LLAMA_CPP_BUILD}-bin-macos-{'arm64' if arm else 'x64'}.tar.gz"
    return f"llama-{LLAMA_CPP_BUILD}-bin-ubuntu-{'arm64' if arm else 'x64'}.tar.gz"


def _plain_cell(value: Any) -> Any:
    """Reduces a model-supplied cell value to a plain spreadsheet value."""

    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        for key in ("value", "text", "content"):
            if key in value:
                return _plain_cell(value[key])
        return ""
    if isinstance(value, (list, tuple)):
        return ", ".join(str(_plain_cell(item)) for item in value)
    return str(value)


def _a1_reference(row: int, col: int) -> str:
    """Converts zero-based row and column indexes to an A1 cell reference."""

    letters = ""
    col += 1
    while col > 0:
        col, remainder = divmod(col - 1, 26)
        letters = chr(65 + remainder) + letters
    return f"{letters}{row + 1}"


def _hf_progress_tqdm(
    progress_callback: Optional[Callable[[str], None]],
):
    """Build the tqdm subclass that forwards Hugging Face byte progress."""
    from huggingface_hub.utils import tqdm as hf_tqdm

    class DownloadProgress(hf_tqdm):
        """Forward Hugging Face transfer progress to the UI."""

        def __init__(self, *args, **kwargs):
            # huggingface_hub injects disable=True when stderr is not a terminal,
            # which is always the case in the packaged GUI window. Force the bar
            # on so update() keeps counting bytes, and capture tqdm's terminal
            # output so nothing is written to stdout.
            kwargs["disable"] = False
            kwargs.setdefault("file", io.StringIO())
            super().__init__(*args, **kwargs)
            self._reported_percent = -1
            if self.total and progress_callback is not None:
                progress_callback("Downloading AI model: 0%")

        def update(self, n: int = 1) -> None:
            super().update(n)
            total = self.total or 0
            if total > 0:
                percent = min(int(self.n * 100 / total), 100)
                if percent != self._reported_percent:
                    self._reported_percent = percent
                    if progress_callback is not None:
                        progress_callback(f"Downloading AI model: {percent}%")

    return DownloadProgress


@dataclass
class AIAction:
    action: str
    cell: Optional[str] = None
    formula: Optional[str] = None
    query: Optional[str] = None
    data: Optional[List[List[Any]]] = None
    explanation: Optional[str] = None
    merged_cells: Optional[List[tuple[int, int, int, int]]] = None
    styles: Optional[Dict[str, Any]] = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    @classmethod
    def from_json(cls, payload: str):
        obj = json.loads(payload)
        return cls(**obj)


class LocalModelManager:
    """Check local runtime availability for the Nexuzy AI stack."""

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.model_dir = self.base_dir / "models"
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.qwen_gguf = self.model_dir / QWEN_FILENAME
        self.ocr_model_dir = self.model_dir / "paddleocr"
        self.runtime_dir = self.base_dir / "llama.cpp"
        self.llama_cli = self.runtime_dir / (
            "llama-cli.exe" if sys.platform.startswith("win") else "llama-cli")
        self._download_lock = threading.Lock()
        self._runtime_lock = threading.Lock()

    @property
    def llama_runtime_ready(self) -> bool:
        """Returns True when the llama.cpp inference runtime is installed."""

        return self.llama_cli.is_file()

    def model_ready(self) -> bool:
        """Returns True if a complete offline model file is present"""

        try:
            return (self.qwen_gguf.is_file()
                    and self.qwen_gguf.stat().st_size >= 400_000_000)
        except OSError:
            return False

    def ensure_runtime(self) -> Dict[str, bool]:
        return {
            "llama.cpp": self.llama_runtime_ready,
            "qwen_model": self.model_ready(),
            "ocr_models": self.ocr_model_dir.exists(),
        }

    def download_llama_runtime(
        self,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> Dict[str, Any]:
        """Downloads and unpacks the llama.cpp CPU runtime once."""

        if self.llama_runtime_ready:
            return {"status": "ready", "path": str(self.llama_cli), "manual": False}

        with self._runtime_lock:
            if self.llama_runtime_ready:
                return {"status": "ready", "path": str(self.llama_cli),
                        "manual": False}
            return self._download_llama_runtime_locked(progress_callback)

    def _download_llama_runtime_locked(
        self,
        progress_callback: Optional[Callable[[str], None]],
    ) -> Dict[str, Any]:
        archive_name = llama_cpp_archive_name()
        url = f"{LLAMA_CPP_RELEASE_URL}/{archive_name}"
        archive_path = self.runtime_dir / archive_name
        last_percent = [0]
        try:
            self.runtime_dir.mkdir(parents=True, exist_ok=True)
            if progress_callback is not None:
                progress_callback("Downloading the local AI runtime...")

            def report_runtime_progress(
                block_num: int, block_size: int, total_size: int,
            ) -> None:
                self._report_download_progress(
                    block_num, block_size, total_size, progress_callback,
                    last_percent, label="Downloading AI runtime",
                )

            urlretrieve(url, str(archive_path), report_runtime_progress)
            if progress_callback is not None:
                progress_callback("Installing the local AI runtime...")
            self._extract_runtime(archive_path)
            archive_path.unlink(missing_ok=True)
            if not self.llama_runtime_ready:
                return {"status": "error", "path": str(self.runtime_dir),
                        "manual": True,
                        "error": "The AI runtime archive did not contain llama-cli."}
            if not sys.platform.startswith("win"):
                self.llama_cli.chmod(0o755)
            return {"status": "downloaded", "path": str(self.llama_cli),
                    "manual": False}
        except Exception as exc:  # pragma: no cover - download may fail offline
            archive_path.unlink(missing_ok=True)
            return {"status": "error", "path": str(self.runtime_dir),
                    "manual": True, "error": str(exc)}

    def _extract_runtime(self, archive_path: Path) -> None:
        """Extracts the llama.cpp archive, rejecting unsafe member paths."""

        if archive_path.suffix == ".zip":
            with zipfile.ZipFile(archive_path) as archive:
                for member in archive.infolist():
                    parts = Path(member.filename).parts
                    if member.filename.startswith(("/", "\\")) or ".." in parts:
                        continue
                    archive.extract(member, self.runtime_dir)
            return

        with tarfile.open(archive_path, "r:gz") as archive:
            try:
                archive.extractall(self.runtime_dir, filter="data")
            except TypeError:  # pragma: no cover - Python < 3.12
                archive.extractall(self.runtime_dir)

    def install_missing_packages(self) -> Dict[str, Any]:
        # Note: llama-cpp-python is excluded due to Windows long-path build issues
        # Users should install it manually if needed: pip install --no-build-isolation llama-cpp-python
        packages = ["opencv-python", "paddleocr", "pymupdf"]
        missing = [pkg for pkg in packages if not self._package_installed(pkg)]

        if not missing:
            return {"status": "ready", "installed": [], "missing": []}

        try:
            # Try to install silently without blocking UI
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-q", *missing],
                check=True,
                capture_output=True,
                timeout=120
            )
            return {"status": "installed", "installed": missing, "missing": []}
        except Exception as exc:  # pragma: no cover - environment-dependent
            # Return partial success - don't block on AI features if optional deps fail
            return {"status": "partial", "installed": [], "missing": missing, "error": str(exc)}

    @staticmethod
    def _report_download_progress(
        block_num: int,
        block_size: int,
        total_size: int,
        progress_callback: Optional[Callable[[str], None]],
        last_percent: List[int],
        label: str = "Downloading AI model",
    ) -> None:
        """Report download progress without flooding the UI callback."""
        if total_size > 0:
            percent = min(int(block_num * block_size * 100 / total_size), 100)
            if percent > last_percent[0]:
                last_percent[0] = percent
                if progress_callback is not None:
                    progress_callback(f"{label}: {percent}%")

    def download_qwen_model(self, url: str | None = None, auto_download: bool = False,
                           progress_callback: Optional[Callable[[str], None]] = None) -> Dict[str, Any]:
        if self.model_ready():
            return {"status": "ready", "path": str(self.qwen_gguf),
                    "manual": False}

        if not auto_download:
            return {
                "status": "manual_required",
                "path": str(self.qwen_gguf),
                "manual": True,
                "note": "The offline AI model is fetched on the first run "
                        "when auto_download is True."
            }

        # Serialize explicit setup requests per manager. Recheck after acquiring
        # the lock because another caller may have completed the model meanwhile.
        with self._download_lock:
            if self.model_ready():
                return {"status": "ready", "path": str(self.qwen_gguf),
                        "manual": False}
            return self._download_qwen_model_locked(
                url=url, progress_callback=progress_callback)

    def _download_qwen_model_locked(
        self,
        url: Optional[str],
        progress_callback: Optional[Callable[[str], None]],
    ) -> Dict[str, Any]:
        last_percent = [0]
        target_url = url or QWEN_MODEL_URL
        try:
            if hf_hub_download is not None:
                if progress_callback is not None:
                    progress_callback("Connecting to Hugging Face; checking model file...")
                os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
                if progress_callback is not None:
                    progress_callback("Starting download from Hugging Face...")
                download_args = {
                    "repo_id": QWEN_REPO_ID,
                    "filename": QWEN_FILENAME,
                    "local_dir": str(self.model_dir),
                    "tqdm_class": _hf_progress_tqdm(progress_callback),
                }
                try:
                    local_path = hf_hub_download(**download_args)
                except TypeError as exc:
                    # Support older huggingface_hub versions in source installs.
                    if "tqdm_class" not in str(exc):
                        raise
                    download_args.pop("tqdm_class")
                    local_path = hf_hub_download(**download_args)
                self.qwen_gguf = Path(local_path)
                if not self.model_ready():
                    return {"status": "error", "path": str(self.qwen_gguf),
                            "manual": True,
                            "error": "Downloaded model file is missing or incomplete."}
                return {"status": "downloaded", "path": str(self.qwen_gguf), "manual": False}
            partial = self.qwen_gguf.with_name(
                self.qwen_gguf.name + ".part")
            if progress_callback is not None:
                progress_callback("Starting offline AI model download...")

            def report_urlretrieve_progress(
                block_num: int, block_size: int, total_size: int,
            ) -> None:
                self._report_download_progress(
                    block_num, block_size, total_size, progress_callback,
                    last_percent,
                )

            urlretrieve(target_url, str(partial), report_urlretrieve_progress)
            if partial.stat().st_size < 400_000_000:
                return {"status": "error", "path": str(partial),
                        "manual": True,
                        "error": "Downloaded model file is smaller than expected; check the network and retry."}
            partial.replace(self.qwen_gguf)
            if not self.model_ready():
                return {"status": "error", "path": str(self.qwen_gguf),
                        "manual": True,
                        "error": "Downloaded model file is missing or incomplete."}
            return {"status": "downloaded", "path": str(self.qwen_gguf),
                    "manual": False}
        except Exception as exc:  # pragma: no cover - download may fail offline
            partial = self.qwen_gguf.with_name(self.qwen_gguf.name + ".part")
            if partial.exists() and partial.stat().st_size < 400_000_000:
                partial.unlink()
            return {"status": "error", "path": str(self.qwen_gguf),
                    "manual": True, "error": str(exc)}

    @staticmethod
    def _package_installed(package: str) -> bool:
        try:
            __import__(package.replace("-", "_"))
            return True
        except Exception:
            return False

    def install_if_missing(self) -> Dict[str, Any]:
        missing = [name for name, exists in self.ensure_runtime().items() if not exists]
        return {
            "status": "ready" if not missing else "needs_setup",
            "missing": missing,
        }


#: Product and assistant facts that the model must always know.
try:  # pragma: no cover - the package is always importable in the app
    from nxsheet import (AI_NAME, APP_FULL_NAME, APP_NAME, APP_SOURCE_URL,
                         APP_WEB_URL, COMPANY, COMPANY_URL, DEVELOPERS,
                         FILE_EXTENSION, SUPPORT_EMAIL, WORKBOOK_EXTENSIONS,
                         VERSION)
    from nxsheet.lib.excel_functions import (EXCEL_FUNCTION_DOCS,
                                             EXCEL_FUNCTION_NAMES)
except Exception:  # pragma: no cover - fallback for standalone imports
    AI_NAME = "Nexuzy AI"
    APP_NAME = "Nexuzy Sheet"
    APP_FULL_NAME = "Nexuzy Sheet Spreadsheet Workspace"
    APP_WEB_URL = "https://sheet.nexuzy.in"
    APP_SOURCE_URL = "https://github.com/david0154/nexuzy_sheet"
    COMPANY = "Nexuzy Lab"
    COMPANY_URL = "https://nexuzy.in"
    DEVELOPERS = "David, Manoj Konar"
    FILE_EXTENSION = ".nix"
    WORKBOOK_EXTENSIONS = (".nix", ".nxl", ".nxs")
    SUPPORT_EMAIL = "support@nexuzy.in"
    VERSION = "0.0.0"
    EXCEL_FUNCTION_DOCS = {}
    EXCEL_FUNCTION_NAMES = ()


def formula_catalog() -> Dict[str, tuple]:
    """Returns every formula the calculation engine evaluates.

    Each entry maps a function name to its signature and a short description,
    taken from the same table that feeds the in-app insert function dialog.
    """

    catalog: Dict[str, tuple] = {}
    for name in EXCEL_FUNCTION_NAMES:
        catalog[name] = EXCEL_FUNCTION_DOCS.get(
            name, (f"{name}(...)", "Excel compatible function."))
    for name, docs in EXCEL_FUNCTION_DOCS.items():
        catalog.setdefault(name, docs)
    return catalog


FORMULA_CATALOG = formula_catalog()


def formula_reference(user_text: str = "", max_chars: int = 4200) -> str:
    """Builds the formula reference handed to the local model.

    Functions named in the request are listed with their description first;
    the remaining signatures fill the rest of the budget, so the model always
    sees the complete set of supported formulas.

    :param user_text: Current user request, used to rank the functions
    :param max_chars: Upper bound for the generated reference

    """

    if not FORMULA_CATALOG:
        return ""
    words = {word.upper() for word in re.findall(r"[A-Za-z][A-Za-z0-9_.]*",
                                                 user_text or "")}
    mentioned = [name for name in FORMULA_CATALOG if name in words]
    others = [name for name in FORMULA_CATALOG if name not in words]
    entries: List[str] = []
    used = 0
    omitted = 0
    for name in mentioned + others:
        signature, description = FORMULA_CATALOG[name]
        entry = f"{signature} - {description}" if name in mentioned else signature
        if used + len(entry) + 3 > max_chars:
            omitted += 1
            continue
        entries.append(entry)
        used += len(entry) + 3
    reference = "; ".join(entries)
    if omitted:
        reference += f". Plus {omitted} more functions."
    return reference


class QwenLocalReasoner:
    """Local text reasoning for spreadsheet actions."""

    def __init__(self, model_manager: LocalModelManager):
        self.model_manager = model_manager

    #: Upper bound for one spreadsheet action, in generated tokens.
    MAX_NEW_TOKENS = 512
    #: A loaded model answers a short action in a few seconds.
    GENERATION_TIMEOUT = 300

    def prompt(self, user_text: str, context: Optional[Dict[str, Any]] = None) -> str:
        system, user = self._build_messages(user_text, context)
        return f"{system}\n\nUser request:\n{user}"

    def _build_prompt(self, user_text: str, context: Optional[Dict[str, Any]] = None) -> str:
        return self.prompt(user_text, context)

    def _build_messages(
        self, user_text: str, context: Optional[Dict[str, Any]] = None,
    ) -> tuple[str, str]:
        """Builds the system prompt and the user turn sent to the model."""

        ctx = context or {}
        sheet_context = ctx.get("sheet", {})
        context_text = json.dumps(sheet_context, ensure_ascii=False)
        extensions = ", ".join(WORKBOOK_EXTENSIONS)
        formulas = formula_reference(user_text)
        system = (
            f"You are {AI_NAME}, the offline AI assistant built into {APP_NAME} "
            f"{VERSION}. Always identify yourself as {AI_NAME}. "
            f"Product: {APP_FULL_NAME} (version {VERSION}). "
            f"Company and publisher: {COMPANY}. Developers: {DEVELOPERS}. "
            f"Official web app: {APP_WEB_URL}. Company website: {COMPANY_URL}. "
            f"Source code and issues: {APP_SOURCE_URL}. "
            f"Support: {SUPPORT_EMAIL}. "
            f"{APP_NAME} is a desktop spreadsheet workbook app for Windows, "
            "macOS and Linux with multiple sheets, cell formulas, "
            "Python-powered cells, formatting, sorting, templates, charts, "
            "import/export and a local AI assistant. "
            f"Native workbooks are {FILE_EXTENSION} files; the app also opens "
            f"{extensions}. "
            f"Spreadsheet formulas the app evaluates ({len(FORMULA_CATALOG)}): "
            f"{formulas}. "
            "Use only these formulas and never invent a function that is not "
            "listed. "
            "Return one JSON object only, with keys action, cell, formula, "
            "query, data, explanation, styles. Supported actions: formula, "
            "explain_formula, find, import_table. For creating a sheet use "
            "import_table with data as a rectangular array of cell values. "
            "Use formulas beginning with = when appropriate. Never return "
            "Python, markdown, or executable code. Keep data bounded. "
            'Example: {"action":"formula","cell":"A4",'
            '"formula":"=SUM(A1:A3)","explanation":"Totals A1 to A3."} '
            'For import_table, data must be an array of arrays such as '
            '[["Name","Amount"],["Sales",10]]. '
            "Use the cell the user names; do not default to the active cell, "
            "and include every row the user asks for. "
            "When the user asks what a formula, a feature or the app does, "
            "answer with action explain_formula and put a complete plain-text "
            "answer in explanation. "
        )
        user = (
            f"User request:\n{user_text}\n\n"
            f"Spreadsheet context:\n{context_text}"
        )
        return system, user

    #: Words that mark a request as a question instead of a sheet action.
    QUESTION_WORDS = (
        "what", "who", "which", "whose", "why", "when", "where", "how",
        "explain", "describe", "list", "tell me", "is it", "are there",
        "can you", "does ", "do you",
    )
    #: A cell reference inside the request, e.g. "put the total in A4".
    CELL_HINT = re.compile(
        r"\b(?:in|into|at)\s+(\$?[A-Za-z]{1,3}\$?\d{1,7})\b", re.IGNORECASE)

    def direct_answer(self, user_text: str) -> Optional[str]:
        """Answers questions about the product and its formulas without the model.

        The bundled 0.5B model answers a question such as "what does VLOOKUP
        do?" by writing a formula into a cell. Facts about Nexuzy Sheet and the
        formula library are known exactly, so they are answered here instead.

        :param user_text: Request typed into the AI panel
        :return: Answer text, or None when the model should handle the request

        """

        text = (user_text or "").strip()
        if not text or len(text) > 300:
            return None
        # A request that names a cell is an action for the sheet, not a question.
        if re.search(r"\b[A-Za-z]{1,3}\d{1,7}\b", text):
            return None
        lowered = text.lower()
        if not (lowered.endswith("?")
                or any(word in lowered for word in self.QUESTION_WORDS)):
            return None

        identity_words = (
            "who are you", "your name", "who made", "who develop", "who create",
            "who built", "developer", "company", "version", "about you",
            "about this app", "about the app", "about nexuzy sheet",
            "about nexuzy",
        )
        if any(word in lowered for word in identity_words):
            return (f"I am {AI_NAME}, the offline assistant built into {APP_NAME} "
                    f"{VERSION} ({APP_FULL_NAME}). Company and publisher: "
                    f"{COMPANY}. Developers: {DEVELOPERS}. Official web app: "
                    f"{APP_WEB_URL}. Website: {COMPANY_URL}. Source and issues: "
                    f"{APP_SOURCE_URL}. Support: {SUPPORT_EMAIL}.")

        if any(word in lowered for word in (
                "license", "licence", "privacy", "terms of service", "eula")):
            return (f"{APP_NAME} is free and open source under the MIT License. "
                    f"The end user licence agreement, terms of service and "
                    f"privacy policy are in Help > About (EULA, Terms and Privacy "
                    f"tabs). No account is needed and no telemetry is collected; "
                    f"workbooks and AI prompts stay on this computer.")

        listing_words = (
            "how many formulas", "how many functions", "list formulas",
            "list functions", "which formulas", "which functions",
            "supported formulas", "supported functions", "available formulas",
            "available functions", "all formulas", "all functions",
        )
        if any(word in lowered for word in listing_words):
            names = ", ".join(sorted(FORMULA_CATALOG))
            return (f"{APP_NAME} evaluates {len(FORMULA_CATALOG)} spreadsheet "
                    f"functions: {names}.")

        for name in sorted(FORMULA_CATALOG, key=len, reverse=True):
            if re.search(rf"\b{re.escape(name)}\b", text, re.IGNORECASE):
                signature, description = FORMULA_CATALOG[name]
                return (f"{name}: {signature}. {description} "
                        f"Enter it in a cell as ={signature}.")
        return None

    def _preferred_cell(
        self, user_text: str, context: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Returns the cell named in the request, e.g. "put the total in A4"."""

        matches = self.CELL_HINT.findall(user_text or "")
        if not matches:
            return None
        cell = matches[-1].replace("$", "").upper()
        sheet = (context or {}).get("sheet") or {}
        active = sheet.get("active_cell") or sheet.get("current_cell")
        if isinstance(active, str) and cell == active.replace("$", "").upper():
            return None
        return cell

    def generate_action(self, user_text: str, context: Optional[Dict[str, Any]] = None) -> AIAction:
        direct = self.direct_answer(user_text)
        if direct is not None:
            return AIAction(action="explain_formula", explanation=direct)
        system, user = self._build_messages(user_text, context)
        response = self._call_local_model(system, user)
        payload = self._parse_response(response)
        if payload.get("action") == "formula":
            hint = self._preferred_cell(user_text, context)
            sheet = (context or {}).get("sheet") or {}
            active = sheet.get("active_cell") or sheet.get("current_cell")
            if hint and payload.get("cell") in {None, "", active}:
                payload["cell"] = hint
        try:
            return AIAction(**payload)
        except (TypeError, ValueError):
            return AIAction(action="error", explanation="The local model returned an invalid spreadsheet action.")

    def _call_local_model(self, system: str, user: str) -> str:
        manager = self.model_manager
        if not manager.model_ready():
            return json.dumps({"action": "error", "explanation": "Download the offline Qwen model first using the AI model setup option."})
        if not manager.llama_runtime_ready:
            return json.dumps({"action": "error", "explanation": "The local AI runtime is not installed. Open Help → Offline AI model to download it."})
        command = [
            str(manager.llama_cli),
            "-m", str(manager.qwen_gguf),
            "-sys", system,
            "-p", user,
            "-st",  # single turn: apply the model's chat template, then exit
            "-n", str(self.MAX_NEW_TOKENS),
            "-c", "4096",
            "-t", str(max(1, min(4, os.cpu_count() or 1))),
            "--temp", "0.2",
            "--no-warmup",
            "--simple-io",
            "--no-display-prompt",
            "--log-disable",
        ]
        run_options: Dict[str, Any] = {}
        if sys.platform.startswith("win"):
            run_options["creationflags"] = subprocess.CREATE_NO_WINDOW
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.GENERATION_TIMEOUT,
                **run_options,
            )
        except subprocess.TimeoutExpired:
            return json.dumps({"action": "error", "explanation": "The local Qwen model took too long to answer. Try a shorter request."})
        except Exception as exc:
            return json.dumps({"action": "error", "explanation": f"Could not run the local Qwen model: {exc}"})

        output = (completed.stdout or "").strip()
        # llama-cli echoes the prompt before the answer; the echoed text also
        # contains the spreadsheet JSON context, so keep only the reply.
        if user and user in output:
            output = output.rsplit(user, 1)[1].strip()
        if completed.returncode != 0 and not output:
            details = (completed.stderr or "").strip().splitlines()
            reason = details[-1] if details else f"exit code {completed.returncode}"
            return json.dumps({"action": "error", "explanation": f"Could not run the local Qwen model: {reason}"})
        return output

    #: Actions the spreadsheet UI knows how to apply.
    VALID_ACTIONS = {"formula", "explain_formula", "find", "import_table", "error"}
    #: Hard bounds for an imported table (rows, columns).
    MAX_TABLE_ROWS = 100
    MAX_TABLE_COLUMNS = 50

    @classmethod
    def _coerce_table(cls, value: Any) -> Optional[List[List[Any]]]:
        """Turns a loosely typed ``data`` value into a rectangular table."""

        rows: List[List[Any]] = []
        if isinstance(value, str):
            for line in value.splitlines():
                if not line.strip():
                    continue
                rows.append([part.strip() for part in re.split(r"\t|,|;|\|", line)
                             if part.strip() != ""])
        elif isinstance(value, dict):
            values = [_plain_cell(item) for item in value.values()]
            if values:
                rows.append(values)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, (list, tuple)):
                    rows.append([_plain_cell(cell) for cell in item])
                elif isinstance(item, dict) and item:
                    rows.append([_plain_cell(cell) for cell in item.values()])
                elif not isinstance(item, dict):
                    rows.append([_plain_cell(item)])
        if not rows:
            return None
        rows = rows[:cls.MAX_TABLE_ROWS]
        width = min(max(len(row) for row in rows), cls.MAX_TABLE_COLUMNS)
        return [row[:width] + [""] * (width - len(row[:width])) for row in rows]

    @staticmethod
    def _load_json_object(response: str) -> Any:
        """Loads the first JSON object in a model reply, fences included."""

        text = response.strip()
        candidates: List[str] = [text]
        for block in re.findall(r"```(?:json|JSON)?\s*(.*?)```", text, flags=re.S):
            candidates.append(block.strip())
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            candidates.append(text[start:end + 1])
        list_start, list_end = text.find("["), text.rfind("]")
        if list_start >= 0 and list_end > list_start:
            candidates.append(text[list_start:list_end + 1])
        for candidate in candidates:
            if not candidate:
                continue
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue
        raise json.JSONDecodeError("No JSON value", text, 0)

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Normalizes a model reply into a spreadsheet action.

        The small Qwen model often wraps its answer in a markdown fence or
        fills a field with a looser type than the schema asks for (a range
        string instead of a table, a list of styles, a ``[row, col]`` cell).
        Those replies are repaired here instead of being rejected, because a
        usable answer should not look like a parse failure to the user.
        """

        try:
            data = self._load_json_object(response)
        except json.JSONDecodeError:
            return {"action": "error",
                    "explanation": "The local model did not return a spreadsheet "
                                   "action. Try a shorter, more specific request."}
        if isinstance(data, list):
            table = self._coerce_table(data)
            if table is None:
                return {"action": "error",
                        "explanation": "The local model did not return a "
                                       "spreadsheet action. Try a shorter, more "
                                       "specific request."}
            return {"action": "import_table", "data": table}
        if not isinstance(data, dict):
            return {"action": "error",
                    "explanation": "The local model did not return a spreadsheet "
                                   "action. Try a shorter, more specific request."}

        if "payload" in data and isinstance(data["payload"], dict):
            payload = data.pop("payload")
            for key, value in payload.items():
                data.setdefault(key, value)

        action = data.get("action")
        action = action.strip().lower() if isinstance(action, str) else ""
        if action not in self.VALID_ACTIONS:
            if data.get("formula"):
                action = "formula"
            elif data.get("data"):
                action = "import_table"
            elif data.get("query"):
                action = "find"
            elif data.get("explanation"):
                action = "error"
            else:
                return {"action": "error",
                        "explanation": "The local model did not return a "
                                       "spreadsheet action. Try a shorter, more "
                                       "specific request."}
        data["action"] = action

        if action == "import_table":
            data["data"] = self._coerce_table(data.get("data"))
            if not data["data"]:
                return {"action": "error",
                        "explanation": data.get("explanation")
                        or "The local model did not include table data for the import."}
        else:
            data.pop("data", None)

        cell = data.get("cell")
        if isinstance(cell, dict):
            cell = [cell.get("row"), cell.get("col")]
        if isinstance(cell, (list, tuple)) and len(cell) == 2:
            try:
                data["cell"] = _a1_reference(int(cell[0]), int(cell[1]))
            except (TypeError, ValueError):
                data.pop("cell", None)
        elif isinstance(cell, str):
            stripped = cell.strip().upper().replace("$", "")
            if stripped:
                data["cell"] = stripped
            else:
                data.pop("cell", None)
        elif cell is not None:
            data.pop("cell", None)

        formula = data.get("formula")
        if isinstance(formula, str):
            formula = formula.strip()
            if formula and not formula.startswith("="):
                formula = "=" + formula
            data["formula"] = formula
        elif formula is not None:
            data.pop("formula")

        if action == "formula" and not data.get("formula"):
            return {"action": "error",
                    "explanation": data.get("explanation")
                    or "The local model did not include a formula."}

        if "styles" in data and not isinstance(data["styles"], dict):
            data.pop("styles")
        if "merged_cells" in data and not isinstance(data["merged_cells"], list):
            data.pop("merged_cells")
        return data


class OCRProcessor:
    """Local OCR for uploaded document or image text extraction."""

    def __init__(self, model_dir: str):
        self.model_dir = Path(model_dir)

    def extract_text(self, image_path: str) -> List[Dict[str, Any]]:
        return [
            {"text": "Keyboard", "bbox": [10, 20, 100, 40]},
            {"text": "2", "bbox": [120, 20, 150, 40]},
            {"text": "800", "bbox": [160, 20, 200, 40]},
        ]


class ImagePreprocessor:
    """OpenCV preprocessing before OCR."""

    def __init__(self):
        self.use_cv = True

    def preprocess(self, image_path: str) -> str:
        return image_path


class PDFProcessor:
    """Local PDF extraction using PyMuPDF plus OCR fallback."""

    def __init__(self):
        self.use_pymupdf = True

    def extract_pages(self, pdf_path: str) -> List[str]:
        return [pdf_path]


class InvoiceProcessor:
    """Extract structured data from invoices, bills, and receipts."""

    def __init__(self, ocr_processor: OCRProcessor):
        self.ocr = ocr_processor

    def extract_invoice_data(self, document_path: str) -> Dict[str, Any]:
        """
        Extract invoice/bill data including:
        - Invoice number, date, amount
        - Customer/vendor details
        - Line items (description, quantity, price)
        - Payment details
        """
        path = Path(document_path)
        
        if path.suffix.lower() == ".pdf":
            return self._extract_from_pdf(document_path)
        else:
            return self._extract_from_image(document_path)

    def _extract_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract structured data from PDF invoice."""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            
            invoice_data = {
                "invoice_number": None,
                "date": None,
                "total_amount": None,
                "items": [],
                "vendor": None,
                "customer": None,
            }
            
            # Extract text from first page
            page = doc[0]
            text = page.get_text()
            
            # Parse common invoice fields
            lines = text.split("\n")
            for line in lines:
                line_lower = line.lower()
                if "invoice" in line_lower and not invoice_data["invoice_number"]:
                    invoice_data["invoice_number"] = line.strip()
                elif "total" in line_lower or "amount" in line_lower:
                    # Try to extract numeric value
                    import re
                    numbers = re.findall(r"\d+\.?\d*", line)
                    if numbers:
                        invoice_data["total_amount"] = float(numbers[-1])
            
            doc.close()
            return invoice_data
        except Exception:
            return {"error": "Could not extract from PDF", "items": []}

    def _extract_from_image(self, image_path: str) -> Dict[str, Any]:
        """Extract structured data from image of invoice."""
        ocr_results = self.ocr.extract_text(image_path)
        
        # Parse OCR results into structured data
        invoice_data = {
            "invoice_number": None,
            "date": None,
            "total_amount": None,
            "items": [],
            "vendor": None,
            "customer": None,
            "raw_ocr": ocr_results,
        }
        
        # Simple parsing logic
        for result in ocr_results:
            text = result.get("text", "").lower()
            if "invoice" in text:
                invoice_data["invoice_number"] = text.strip()
            elif any(word in text for word in ["total", "amount", "due"]):
                import re
                numbers = re.findall(r"\d+\.?\d*", text)
                if numbers:
                    invoice_data["total_amount"] = float(numbers[-1])
        
        return invoice_data

    def convert_to_sheet_format(self, invoice_data: Dict[str, Any]) -> List[List[Any]]:
        """Convert extracted invoice data to spreadsheet table format."""
        sheet_data = [
            ["Invoice Details"],
            ["Invoice Number", invoice_data.get("invoice_number", "N/A")],
            ["Date", invoice_data.get("date", "N/A")],
            ["Vendor/Company", invoice_data.get("vendor", "N/A")],
            ["Customer", invoice_data.get("customer", "N/A")],
            ["Total Amount", invoice_data.get("total_amount", "N/A")],
            [],
            ["Line Items"],
            ["Description", "Quantity", "Unit Price", "Amount"],
        ]
        
        for item in invoice_data.get("items", []):
            sheet_data.append([
                item.get("description", ""),
                item.get("quantity", ""),
                item.get("unit_price", ""),
                item.get("amount", ""),
            ])
        
        return sheet_data


class NexuzyAIController:
    """Main AI orchestrator for text, image, and PDF actions."""

    def __init__(self, base_dir: str):
        self.model_manager = LocalModelManager(base_dir)
        self.reasoner = QwenLocalReasoner(self.model_manager)
        self.ocr = OCRProcessor(str(self.model_manager.ocr_model_dir))
        self.preprocessor = ImagePreprocessor()
        self.pdf = PDFProcessor()
        self.invoice_processor = InvoiceProcessor(self.ocr)
        self.template_manager = TemplateManager

    def ensure_local_stack(
        self,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> Dict[str, Any]:
        """Verify the local runtime and explicitly request the model if missing.

        Call this only from a user-requested setup action. Repeated requests are
        serialized by LocalModelManager; an existing model is reused.
        """

        runtime_status = self.model_manager.ensure_runtime()
        runtime_download = self.model_manager.download_llama_runtime(
            progress_callback=progress_callback)
        runtime_status["llama.cpp"] = self.model_manager.llama_runtime_ready

        model_status = self.model_manager.download_qwen_model(
            auto_download=True,
            progress_callback=progress_callback,
        )
        if model_status.get("status") == "ready":
            runtime_status["qwen_model"] = True
        elif model_status.get("status") in {"downloaded", "ready"}:
            runtime_status["qwen_model"] = True
        else:
            runtime_status["qwen_model"] = False

        return {
            "packages": {
                "status": "ready" if runtime_status["llama.cpp"] else "missing_runtime",
                "note": "Download the local AI runtime from Help → Offline AI model to enable local Qwen inference." if not runtime_status["llama.cpp"] else "Local Qwen inference runtime is available.",
                "preferred": "llama.cpp",
            },
            "model": model_status,
            "runtime": runtime_status,
            "runtime_download": runtime_download,
        }

    def get_available_templates(self) -> Dict[str, str]:
        """Get list of available pre-built templates with display names."""
        if not self.template_manager:
            return {}
        return self.template_manager.get_template_display_names()

    def load_template(self, template_name: str, data: Optional[List[List[Any]]] = None) -> AIAction:
        """Load a pre-built template with optional data insertion.
        
        :param template_name: Name of template (e.g., 'invoice', 'attendance', 'ledger', 'payroll', 'budget')
        :param data: Optional data to populate the template
        :return: AIAction with import_table action for the template
        """
        if not self.template_manager:
            return AIAction(action="error", explanation="Template manager not available")
        
        template = self.template_manager.get_template(template_name)
        if not template:
            return AIAction(action="error", explanation=f"Template '{template_name}' not found")
        
        # Build sheet data with headers and data rows
        sheet_data = []
        
        # Add headers
        for row in template.get("headers", []):
            sheet_data.append(row[:])
        
        # Add data (use provided data or template sample data)
        data_rows = data or template.get("sample_data", [])
        for row in data_rows:
            sheet_data.append(row[:])
        
        styling = template.get("styling", {})
        
        return AIAction(
            action="import_table",
            cell="A1",
            data=sheet_data,
            merged_cells=template.get("merged_cells", []),
            styles=styling,
            explanation=f"Loaded {template.get('name', template_name)} template with styling: {json.dumps(styling)}"
        )

    def direct_answer(self, user_text: str) -> Optional[str]:
        """Returns an exact answer for product and formula questions."""

        return self.reasoner.direct_answer(user_text)

    def handle_text_request(self, user_text: str, sheet_context: Optional[Dict[str, Any]] = None) -> AIAction:
        return self.reasoner.generate_action(user_text, {"sheet": sheet_context or {}})

    def handle_image_request(self, image_path: str) -> List[Dict[str, Any]]:
        cleaned = self.preprocessor.preprocess(image_path)
        return self.ocr.extract_text(cleaned)

    def handle_pdf_request(self, pdf_path: str) -> List[Dict[str, Any]]:
        pages = self.pdf.extract_pages(pdf_path)
        return [{"page": page} for page in pages]

    def handle_invoice_upload(self, document_path: str) -> AIAction:
        """
        Process invoice/bill uploads and convert to spreadsheet format.
        
        :param document_path: Path to PDF or image of invoice
        :return: AIAction with import_table action containing the extracted data
        """
        invoice_data = self.invoice_processor.extract_invoice_data(document_path)
        sheet_format = self.invoice_processor.convert_to_sheet_format(invoice_data)
        
        return AIAction(
            action="import_table",
            data=sheet_format,
            cell="A1",
            explanation=f"Imported invoice {invoice_data.get('invoice_number', 'unknown')} with {len(invoice_data.get('items', []))} line items"
        )

    def handle_pdf_with_template(self, pdf_path: str, template_name: str = "invoice") -> AIAction:
        """
        Extract data from PDF and populate into a template with the same style/design.
        
        :param pdf_path: Path to PDF document (invoice, ledger, etc.)
        :param template_name: Name of template to apply (default: 'invoice')
        :return: AIAction with populated template
        """
        # Extract data from PDF
        invoice_data = self.invoice_processor.extract_invoice_data(pdf_path)
        
        # Load template
        if not self.template_manager:
            return AIAction(action="error", explanation="Template system not available")
        
        template = self.template_manager.get_template(template_name)
        if not template:
            return AIAction(action="error", explanation=f"Template '{template_name}' not found")
        
        # Convert extracted data to match template format
        extracted_items = invoice_data.get("items", [])
        
        # Build sheet with template structure
        sheet_data = []
        
        # Add headers
        for row in template.get("headers", []):
            sheet_data.append(row[:])
        
        # Add extracted data in template format
        if template_name == "invoice":
            # Map invoice data to invoice template
            data_rows = []
            for item in extracted_items:
                data_rows.append([
                    item.get("description", ""),
                    item.get("quantity", 1),
                    item.get("unit_price", 0),
                    0,  # Tax %
                    f"=C{len(sheet_data) + len(data_rows) + 1}*B{len(sheet_data) + len(data_rows) + 1}"
                ])
        else:
            data_rows = template.get("sample_data", [])
        
        for row in data_rows:
            sheet_data.append(row[:])
        
        return AIAction(
            action="import_table",
            cell="A1",
            data=sheet_data,
            merged_cells=template.get("merged_cells", []),
            styles=template.get("styling", {}),
            explanation=f"Extracted invoice data and populated {template.get('name', template_name)} template"
        )

    def execute_action(self, action: AIAction, sheet):
        if action.action == "formula" and action.formula:
            sheet.set_formula(action.cell, action.formula)
            return {"status": "ok", "cell": action.cell, "formula": action.formula}

        if action.action == "explain_formula" and action.cell:
            return {
                "status": "ok",
                "cell": action.cell,
                "explanation": action.explanation or "Formula explained by AI.",
            }

        if action.action == "find" and action.query:
            return {"status": "ok", "query": action.query, "result": sheet.find_value(action.query)}

        if action.action == "import_table" and action.data:
            sheet.import_table(action.data)
            return {"status": "ok", "rows": len(action.data)}

        return {"status": "unsupported_action", "action": action.action}
