"""
lockpdf_gui_qt.py — Simple GUI to protect PDFs with either:
  1) An "open" password (AES-256), or
  2) Viewer-enforced no-copy/print permissions (opens without a password).

Built with:
  - PySide6 (Qt) for the GUI
  - pikepdf (a Python wrapper of qpdf) for PDF encryption

Notes:
  - The "no-copy/print" option is NOT true security; it relies on PDF
    viewers to honor permissions. Determined users can bypass it.
  - Tested with pikepdf 9.10.2. Older/newer versions may offer additional
    permissions, but we only use arguments supported by 9.10.2.

Update:
  - Eye buttons next to both password fields. Click to show/hide.
"""

import os
import sys
import subprocess
from typing import Optional

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QRadioButton,
    QButtonGroup,
    QCheckBox,
    QMessageBox,
)
from PySide6.QtCore import Qt

import pikepdf
from pikepdf import Encryption, Permissions


APP_TITLE = "PDF Lock (Qt) — Open Password or No-Copy/Print"


def default_outname(src: str, mode_open: bool) -> str:
    """
    Suggest an output filename next to the input:
      - *_locked.pdf for open-password mode
      - *_nocopy.pdf for no-copy/print mode
    """
    root, _ = os.path.splitext(src)
    suffix = "_locked" if mode_open else "_nocopy"
    return f"{root}{suffix}.pdf"


def reveal_in_explorer(path: str) -> None:
    """
    Open the file’s folder and select the file (Windows),
    or reveal in Finder (macOS), or open the folder (Linux).
    """
    try:
        if os.name == "nt":
            subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-R", path])
        else:
            subprocess.Popen(["xdg-open", os.path.dirname(path)])
    except Exception:
        # Non-critical if this fails; just ignore.
        pass


class Main(QWidget):
    """
    Main application window.
    """

    def __init__(self, initial_pdf: Optional[str] = None):
        super().__init__()
        self.setWindowTitle(APP_TITLE)

        # Widgets (defined in _build_ui)
        self.in_edit: QLineEdit
        self.in_browse: QPushButton
        self.out_edit: QLineEdit
        self.out_browse: QPushButton
        self.radio_open: QRadioButton
        self.radio_restrict: QRadioButton
        self.mode_group: QButtonGroup
        self.open_pw_edit: QLineEdit
        self.owner_pw_edit: QLineEdit
        self.open_pw_eye_btn: QPushButton
        self.owner_pw_eye_btn: QPushButton
        self.chk_copy: QCheckBox
        self.chk_print: QCheckBox
        self.apply_btn: QPushButton

        self._build_ui()
        self._wire_events()

        # Prefill input path if provided (e.g., passed by a .bat as %1)
        if initial_pdf and os.path.isfile(initial_pdf):
            self.in_edit.setText(initial_pdf)

        # Sync dependent UI
        self.on_mode_change()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        # Row: input PDF
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("PDF file:"))
        self.in_edit = QLineEdit()
        self.in_browse = QPushButton("Browse…")
        row1.addWidget(self.in_edit, 1)
        row1.addWidget(self.in_browse)
        root.addLayout(row1)

        # Protection type
        root.addWidget(QLabel("Protection type:"))
        self.radio_open = QRadioButton("Require password to open")
        self.radio_restrict = QRadioButton(
            "No-copy/print (viewer-enforced; no password to open)"
        )
        self.radio_open.setChecked(True)
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.radio_open)
        self.mode_group.addButton(self.radio_restrict)
        root.addWidget(self.radio_open)
        root.addWidget(self.radio_restrict)

        # Passwords (Open)
        row_pw1 = QHBoxLayout()
        row_pw1.addWidget(QLabel("Open password:"))
        self.open_pw_edit = QLineEdit()
        self.open_pw_edit.setEchoMode(QLineEdit.Password)  # masked by default
        row_pw1.addWidget(self.open_pw_edit, 1)
        # Eye toggle for Open password
        self.open_pw_eye_btn = QPushButton("👁")
        self.open_pw_eye_btn.setCheckable(True)
        self.open_pw_eye_btn.setToolTip("Show/Hide Open password")
        self.open_pw_eye_btn.setFixedWidth(32)
        row_pw1.addWidget(self.open_pw_eye_btn)
        root.addLayout(row_pw1)

        # Passwords (Owner)
        row_pw2 = QHBoxLayout()
        row_pw2.addWidget(QLabel("Owner password (required):"))
        self.owner_pw_edit = QLineEdit()
        self.owner_pw_edit.setEchoMode(QLineEdit.Password)  # masked by default
        row_pw2.addWidget(self.owner_pw_edit, 1)
        # Eye toggle for Owner password
        self.owner_pw_eye_btn = QPushButton("👁")
        self.owner_pw_eye_btn.setCheckable(True)
        self.owner_pw_eye_btn.setToolTip("Show/Hide Owner password")
        self.owner_pw_eye_btn.setFixedWidth(32)
        row_pw2.addWidget(self.owner_pw_eye_btn)
        root.addLayout(row_pw2)

        # Restrictions (visible only in no-copy/print mode)
        opts_row = QHBoxLayout()
        opts_row.addWidget(QLabel("Restrictions:"))
        self.chk_copy = QCheckBox("Block Copy/Extract")
        self.chk_copy.setChecked(True)
        self.chk_print = QCheckBox("Block Printing")
        self.chk_print.setChecked(True)
        opts_row.addWidget(self.chk_copy)
        opts_row.addWidget(self.chk_print)
        opts_row.addStretch(1)
        root.addLayout(opts_row)

        # Row: output file
        row_out = QHBoxLayout()
        row_out.addWidget(QLabel("Output file:"))
        self.out_edit = QLineEdit()
        self.out_browse = QPushButton("Change…")
        row_out.addWidget(self.out_edit, 1)
        row_out.addWidget(self.out_browse)
        root.addLayout(row_out)

        # Action
        self.apply_btn = QPushButton("Apply Protection")
        root.addWidget(self.apply_btn)

        # Note
        note = QLabel(
            "Note: 'No-copy/print' relies on PDF viewers to honor permissions. "
            "For strong protection, use an Open password."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color:#666;")
        root.addWidget(note)

    def _wire_events(self) -> None:
        self.in_browse.clicked.connect(self.browse_in)
        self.out_browse.clicked.connect(self.browse_out)
        self.apply_btn.clicked.connect(self.apply)
        self.radio_open.toggled.connect(self.on_mode_change)
        self.in_edit.textChanged.connect(self.update_out_suggestion)

        # Eye toggles: show/hide passwords
        # Open password eye button
        self.open_pw_eye_btn.toggled.connect(
            lambda checked: self.open_pw_edit.setEchoMode(
                QLineEdit.Normal if checked else QLineEdit.Password
            )
        )
        # Owner password eye button (FIX: ensure correct class name QLineEdit.Password)
        self.owner_pw_eye_btn.toggled.connect(
            lambda checked: self.owner_pw_edit.setEchoMode(
                QLineEdit.Normal if checked else QLineEdit.Password
            )
        )

    # ---------- UI helpers ----------

    def on_mode_change(self) -> None:
        """
        Toggle widgets depending on protection mode.
        """
        is_open = self.radio_open.isChecked()
        self.open_pw_edit.setEnabled(is_open)
        self.open_pw_eye_btn.setEnabled(is_open)
        # Show restriction checkboxes only for no-copy/print mode
        self.chk_copy.setVisible(not is_open)
        self.chk_print.setVisible(not is_open)
        self.update_out_suggestion()

    def update_out_suggestion(self) -> None:
        """
        Suggest an output filename once an input is chosen or mode changes.
        """
        src = self.in_edit.text().strip()
        if src:
            self.out_edit.setText(default_outname(src, self.radio_open.isChecked()))

    def browse_in(self) -> None:
        """
        Choose input PDF.
        """
        path, _ = QFileDialog.getOpenFileName(
            self, "Choose a PDF", "", "PDF files (*.pdf)"
        )
        if path:
            self.in_edit.setText(path)

    def browse_out(self) -> None:
        """
        Choose output PDF path.
        """
        default = self.out_edit.text().strip() or "output_locked.pdf"
        path, _ = QFileDialog.getSaveFileName(
            self, "Save protected PDF as…", default, "PDF files (*.pdf)"
        )
        if path:
            self.out_edit.setText(path)

    # ---------- Core action ----------

    def apply(self) -> None:
        """
        Perform the encryption or permission restriction using pikepdf.
        This version avoids passing allow=None (which can cause a NoneType error)
        and uses only Permissions arguments supported by pikepdf 9.10.2.
        """
        in_path = self.in_edit.text().strip()
        out_path = self.out_edit.text().strip()

        if not in_path or not os.path.isfile(in_path):
            QMessageBox.critical(self, "Error", "Please choose a valid PDF file.")
            return

        owner = self.owner_pw_edit.text()
        if not owner:
            QMessageBox.critical(
                self, "Error", "Owner password is required (controls permissions)."
            )
            return

        # Build kwargs for Encryption(...) carefully.
        # We never pass allow=None; we only add "allow" when we actually build Permissions.
        encryption_kwargs = dict(owner=owner, R=6)  # R=6 -> AES-256

        if self.radio_open.isChecked():
            # Require a password to open the PDF
            user = self.open_pw_edit.text()
            if not user:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Enter an Open password (or choose the No-copy/print mode).",
                )
                return
            encryption_kwargs["user"] = user
            # Do NOT set "allow" at all (no permissions object in open-password mode)
        else:
            # No-copy/print mode: open without a password, set viewer-enforced permissions
            user = ""
            encryption_kwargs["user"] = user

            # pikepdf 9.10.2 Permissions uses "modify_annotation" (not "modify_annotate");
            # do not include "assemble" in this version.
            perms = Permissions(
                accessibility=True,
                extract=not self.chk_copy.isChecked(),        # block copy -> extract=False
                print_lowres=not self.chk_print.isChecked(),  # block print -> False
                print_highres=not self.chk_print.isChecked(),
                modify_annotation=False,
                modify_form=False,
                modify_other=False,
            )
            encryption_kwargs["allow"] = perms

        if not out_path:
            out_path = default_outname(in_path, self.radio_open.isChecked())

        # Safety: output must differ from input
        if os.path.abspath(in_path) == os.path.abspath(out_path):
            QMessageBox.critical(
                self, "Error", "Output file must be different from the input file."
            )
            return

        try:
            with pikepdf.open(in_path) as pdf:
                pdf.save(out_path, encryption=Encryption(**encryption_kwargs))
            QMessageBox.information(self, "Success", f"Protected PDF written:\n{out_path}")
            if (
                QMessageBox.question(
                    self,
                    "Open Folder?",
                    "Open the output folder?",
                    QMessageBox.Yes | QMessageBox.No,
                )
                == QMessageBox.Yes
            ):
                reveal_in_explorer(out_path)

        except pikepdf.PasswordError:
            QMessageBox.critical(
                self,
                "Error",
                "This PDF is already encrypted and requires a password to open.",
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save protected PDF:\n{e}")


def main() -> None:
    """
    Entry point. Accepts an optional first CLI argument as the initial PDF path
    (useful when launching via a .bat with drag & drop).
    """
    initial = sys.argv[1] if len(sys.argv) >= 2 else None
    app = QApplication(sys.argv)
    w = Main(initial_pdf=initial)
    w.resize(740, 260)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
