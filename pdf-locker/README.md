# PDF Locker GUI (Windows)

A tiny Windows GUI to protect PDFs with either:
- **Open password (AES-256)** — the file requires a password to open.
- **Viewer-enforced no-copy/print** — opens without a password but blocks copy/print in compliant PDF viewers.

Built with **PySide6 (Qt)** and **pikepdf** (wrapper around qpdf).

## What's new
- Eye buttons next to both password fields to **show/hide** the passwords.

## Quick Start (Windows 10/11)

1. Extract this folder anywhere (e.g. `C:\Tools\pdf-locker\`).
2. Double-click **`Run_PDF_Locker.bat`** (first run creates a local virtualenv and installs Python packages).
3. (Optional) Use **`Run_PDF_Locker_DEBUG.bat`** if you want to see logs or diagnose issues.
4. You can **drag & drop** a PDF onto either `.bat`; the GUI will prefill the path.

## Usage
1. Choose a PDF.
2. Pick a **Protection type**:
   - **Require password to open** — enter an **Open password** and an **Owner password**.
   - **No-copy/print** — leave Open password blank; provide **Owner password** and choose restrictions.
3. Confirm the output file path.
4. Click **Apply Protection**.

> **Note:** No-copy/print is viewer-enforced; for real protection use the Open password mode.

## Repo Files
- `lockpdf_gui_qt.py` — the GUI
- `Run_PDF_Locker.bat` — normal launcher (hidden console)
- `Run_PDF_Locker_DEBUG.bat` — debug launcher (visible console + pause)
- `run_hidden.vbs` — helper to run hidden if `pythonw.exe` is unavailable
- `requirements.txt`
- `README.md`

## License
MIT © 2025 Nikos
