# Nexuzy Sheet — Privacy Policy

**Last updated:** 19 November 2026
**Applies to:** Nexuzy Sheet 1.6.0 and later desktop releases

Nexuzy Sheet is built to work offline. This policy explains exactly what the
application stores, what it sends over the network, and what it never does.

---

## 1. Summary

| Question | Answer |
| --- | --- |
| Do I need an account? | No. |
| Does Nexuzy Sheet collect telemetry or analytics? | No. |
| Are my workbooks sent to a server? | No. |
| Does the AI assistant send my prompts anywhere? | No. Inference runs locally. |
| What network access happens? | Only the AI model and runtime downloads you start, and links you click. |
| Where is my data stored? | On your device, in your workbook files and the app data folder. |

## 2. Data the application stores locally

Nexuzy Sheet stores data only on the device where it runs:

- **Workbooks** you save, in the native `.nix` format or in the export formats
  you choose (`.xlsx`, `.ods`, `.csv`, `.pdf`, `.svg`).
- **Recovery and version history** files written by auto save and by the
  version-history feature, stored in the application data folder.
- **Application settings**, such as window layout, language, theme, recent
  files and preferences (stored through Qt's platform settings store).
- **The offline AI model and runtime**, downloaded only when you start the
  download, stored under your user profile:
  - Windows: `%USERPROFILE%\.nexuzy_sheet\`
  - macOS and Linux: `~/.nexuzy_sheet/`
- **Application logs**, written locally to help diagnose crashes and errors.

We have no access to any of these files.

## 3. Network connections

The desktop application makes network requests only in these cases:

1. **Offline AI model download** — when you choose *Download now*, the
   application downloads the Qwen2.5-0.5B-Instruct GGUF model from Hugging Face
   (`huggingface.co`) and the llama.cpp runtime from the llama.cpp GitHub
   releases (`github.com`). The provider receives the ordinary technical
   information any HTTP download exposes, such as your IP address and user
   agent.
2. **Links you click** — the About dialog, documentation and messages contain
   links to `sheet.nexuzy.in`, `nexuzy.in` and `github.com`. Opening one uses
   your default browser, and the destination site's own privacy policy applies.
3. **The optional web application** at <https://sheet.nexuzy.in> is a separate
   product with its own notices. Using the desktop application does not send
   anything to it.

Nexuzy Sheet contains no advertising SDKs, no crash-reporting service, no
usage analytics and no background update checks.

## 4. The offline AI assistant (Nexuzy AI)

- Prompts, spreadsheet context and model output are processed **entirely on your
  device** by the locally installed model. Nothing is uploaded.
- The model file is stored on disk and loaded when you submit a prompt.
- The model is a small instruction-tuned language model; it does not have
  memory of your data beyond the request being processed.
- If you never download the model, the assistant cannot run and no AI-related
  network access occurs.

## 5. Imported documents

PDF and image import and OCR run locally with bundled libraries. Documents you
import are read from the path you choose and are not transmitted.

## 6. Children

The Software is a general-purpose office tool and is not directed to children
under 13. We do not knowingly collect any personal information from anyone,
including children, because the desktop application collects none.

## 7. Your choices and rights

Because we do not hold your data, there is nothing for us to export, correct or
delete on your behalf. You control your data directly:

- delete workbooks, recovery files and version history from your filesystem;
- remove the AI model and runtime by deleting the `.nexuzy_sheet` folder in
  your user profile;
- clear settings through your operating system's settings store, or by
  resetting application preferences;
- uninstall the application to remove its program files.

If you believe we hold personal data about you (for example because you emailed
support), you may request access, correction or deletion by writing to
<support@nexuzy.in>. We keep support email only as long as needed to resolve
your request.

## 8. Security

The application runs with your user permissions and stores data in your user
profile. Protect your device account, keep backups of important workbooks, and
be careful when opening workbook files from untrusted sources — like any
spreadsheet application, Nexuzy Sheet can execute the Python expressions and
formulas contained in a workbook.

## 9. Changes to this policy

We update this policy when the application's behaviour changes. The version
shipped with a release, and shown in **Help → About → Privacy**, is the version
that applies to that release.

## 10. Contact

**Nexuzy Lab** — privacy enquiries: <support@nexuzy.in>
Website: <https://nexuzy.in>
