# PDF Locker GUI (Windows)

A tiny Windows GUI to protect PDFs with either:
- **Open password (AES-256)** — the file requires a password to open.
- **Viewer-enforced no-copy/print** — opens without a password but blocks copy/print in compliant PDF viewers.

Built with **PySide6 (Qt)** and **pikepdf** (wrapper around qpdf).

## What's new
- Eye buttons next to both password fields to **show/hide** the passwords.
- Included **padlock icon** (`pdf-locker.ico`) and **shortcut creator** (`Create_PDF_Locker_Shortcut.vbs`).

## Prerequisites:
- Python 3.8 or higher

## Quick Start (Windows 10/11)

1. Extract this folder to `C:\Python_Scripts\pdf-locker\`.
2. Double-click **`Run_PDF_Locker.bat`** (first run creates a local virtualenv and installs Python packages).
3. (Optional) Use **`Run_PDF_Locker_DEBUG.bat`** if you want to see logs or diagnose issues.
4. You can **drag & drop** a PDF onto either `.bat`; the GUI will prefill the path.

## Create a Desktop Shortcut with Icon

1. Ensure `pdf-locker.ico` is in `C:\Python_Scripts\pdf-locker\`.
2. Double-click **`Create_PDF_Locker_Shortcut.vbs`**.  
   It creates **PDF Locker.lnk** on your Desktop pointing to `C:\Python_Scripts\pdf-locker\Run_PDF_Locker.bat` and using the icon.

If your install lives in a different folder, open the VBS and change:
```vb
target  = "C:\Python_Scripts\pdf-locker\Run_PDF_Locker.bat"
workdir = "C:\Python_Scripts\pdf-locker"
icon    = "C:\Python_Scripts\pdf-locker\pdf-locker.ico"
```

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
- `Create_PDF_Locker_Shortcut.vbs` — creates a desktop shortcut with icon
- `pdf-locker.ico` — padlock icon
- `requirements.txt`
- `README.md`
- `LICENSE`
- `.gitignore`

## Developer Notes
- Python 3.8–3.13 is supported. The BAT creates a local venv and installs dependencies there.
- To build a standalone EXE with icon (optional):
  ```bat
  .venv_pdf_locker\Scripts\python.exe -m pip install pyinstaller
  .venv_pdf_locker\Scripts\pyinstaller --onefile --windowed lockpdf_gui_qt.py --icon=pdf-locker.ico
  ```

## License
MIT © 2025 Nikos
