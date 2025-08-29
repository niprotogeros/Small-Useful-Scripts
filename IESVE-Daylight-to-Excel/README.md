# IESVE Daylight Metrics → Excel

Export IESVE/Radiance daylight metrics from `.wpd` outputs to a clean Excel workbook — with a friendly launcher and one-click desktop shortcut.

## Features
- Select a **Radiance results folder** and parse `.wpd` files
- Auto-detect **metric** from the filename (final underscore-separated token)
- Choose **Full Area** or **AOI** (Area Of Interest) statistics
- Export to **.xlsx** with a sheet name derived from metric + area mode
- Windows-friendly setup: a `.bat` launcher bootstraps a local virtual environment and installs dependencies automatically
- Optional `.vbs` creates a desktop shortcut with a custom icon

## Project Structure
```
IESVE-Daylight-to-Excel/
├─ IESVE_Dayilght_Metrics_to_Excel.py   # Main Python script (GUI-based)
├─ Run_IESVE_Daylight_to_Excell.bat     # Launcher (creates .venv & installs deps)
├─ Create_IESVE_Daylight_to_Excel_Shortcut.vbs # One-click desktop shortcut
├─ DaylightExcel.ico                    # Custom icon
├─ requirements.txt                     # Python deps
├─ .gitignore
├─ LICENSE
└─ README.md
```

## Requirements
- Windows 10/11 (64-bit)
- Python **3.10+ (64-bit)** from python.org
  - During install, tick: **Add python.exe to PATH**, **pip**, and (recommended) **py launcher**
- No Microsoft Excel required to generate `.xlsx` files

## Quick Start
1. **Download** the latest release ZIP (or clone the repo) and **extract** it.
2. Double-click **`Run_IESVE_Daylight_to_Excell.bat`**.
   - On first run it will:
     - create `.venv/`
     - upgrade `pip`
     - `pip install -r requirements.txt`
   - Then it will launch the GUI.
3. (Optional) Double-click **`Create_IESVE_Daylight_to_Excel_Shortcut.vbs`** to create a desktop shortcut with the icon.

## Usage
1. When prompted, **select the Radiance results folder** containing `.wpd` files.
2. Choose a **metric** (parsed from the filename).
3. Choose **Full Area** or **AOI** statistics.
4. Select an output path for the **Excel** file — done!

## Troubleshooting
- **Python not found** → Install Python 3.10+ (64-bit) from python.org with “Add to PATH” checked.
- **Missing modules** → Delete `.venv/` and run the BAT again to re-create and reinstall.
- **tkinter missing** → Use the official python.org installer; it includes Tcl/Tk.
- **Excel save error / permission denied** → Close the file if open and export again.
- **AOI values empty** → Ensure AOI stats are present in the `.wpd` files or choose Full Area.

## Contributing
Issues and PRs are welcome. Please include a minimal sample `.wpd` (with sensitive data removed) when reporting parsing bugs.

## License
MIT – see [LICENSE](LICENSE).
