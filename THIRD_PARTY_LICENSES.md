# Third-party licences and notices

**Nexuzy Sheet 1.6.0** — Copyright (c) 2026 Nexuzy Lab.
Nexuzy Sheet's own source code is licensed under the **MIT License** (see
`LICENSE`).

The packaged desktop application is built from the components below. Each
component remains under its own licence; nothing in the MIT License changes
those terms. Versions are the ones bundled in the 1.6.0 release builds.

---

## 1. Application framework and runtime

| Component | Version | Licence |
| --- | --- | --- |
| Qt 6 (Qt libraries) | 6.11.1 | LGPL-3.0 |
| PyQt6 (Python bindings) | 6.11.0 | GPL-3.0-only (or commercial from Riverbank) |
| PyQt6-sip | 13.12.0 | BSD-2-Clause |
| Python | 3.14 | Python Software Foundation License |

## 2. Bundled Python packages

| Component | Version | Licence |
| --- | --- | --- |
| attrs | 26.1.0 | MIT |
| click | 8.5.0 | BSD-3-Clause |
| cryptography | 48.0.0 | Apache-2.0 OR BSD-3-Clause |
| h2 | 4.3.0 | MIT |
| httpcore2 | 2.16.0 | BSD-3-Clause |
| httpx2 | 2.16.0 | BSD-3-Clause |
| markdown2 | 2.5.5 | MIT |
| MarkupSafe | 3.0.4 | BSD-3-Clause |
| matplotlib | 3.11.2 | Python Software Foundation License |
| numpy | 2.4.6 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 |
| openpyxl | 3.1.5 | MIT |
| pydantic | 2.14.2 | MIT |
| python-dateutil | 2.9.0.post0 | Apache-2.0 |
| tqdm | 4.67.3 | MPL-2.0 AND MIT |

Optional features use further packages that are installed only when the user
selects them (`pymupdf`, `pyenchant`, `py-moneyed`, `plotnine`, `pycel`,
`rpy2`, `huggingface_hub`). Their licences apply when present.

## 3. Downloaded at runtime (not part of the installer)

| Component | Version | Licence | Source |
| --- | --- | --- | --- |
| Qwen2.5-0.5B-Instruct GGUF (Q4_K_M) | Qwen2.5 | Apache-2.0 | huggingface.co/Qwen |
| llama.cpp CPU runtime | b12531 | MIT | github.com/ggml-org/llama.cpp |

These files are fetched only when the user starts the offline AI download and
are stored in the user's profile folder. Removing that folder removes them.

## 4. Upstream project

Nexuzy Sheet started as a fork of **pyspread** (Copyright (c) Martin Manns and
contributors, GPL-3.0). The interface, workbook model and parts of the
calculation engine descend from that project. Files derived from pyspread keep
their original notices.

---

## 5. Compliance notes

- **PyQt6 is GPL-3.0-only.** A distributed binary that links PyQt6 must be
  distributed under GPL-3.0-compatible terms, with complete corresponding
  source available to recipients. Nexuzy Sheet's own sources are MIT (which is
  GPL-compatible), and the release bundles ship the licence texts and
  documentation so recipients can exercise their GPL rights. A commercial
  PyQt licence is required if a build must be distributed without GPL
  obligations.
- **Qt is used under LGPL-3.0.** Recipients may relink the Qt libraries; the
  Qt shared libraries are shipped as separate dynamically linked files inside
  the bundle for that reason. Do not statically link Qt in a proprietary build.
- **PyMuPDF is AGPL-3.0** (or commercial from Artifex) and is not bundled in
  the default build. Distributing a build that includes PyMuPDF requires
  AGPL-3.0 compliance, or a commercial licence from Artifex.
- **The Qwen model is Apache-2.0**, which requires keeping its `NOTICE` and
  attribution with redistributed copies of the model file. The app downloads
  the model directly from the publisher rather than redistributing it.
- Trademarks, product names and logos of third parties belong to their owners
  and are used only for identification.

For licence questions about a specific build, contact
<support@nexuzy.in>.
