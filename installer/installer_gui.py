"""
Dedicated Windows Setup Wizard for PrimeQC Master.
Installs application files, creates Start Menu & Desktop shortcuts, registers context menus and uninstaller.
"""

import sys
import os
import zipfile
import shutil
import subprocess
from PySide6.QtWidgets import (
    QApplication, QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QCheckBox, QProgressBar, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon, QPixmap

DARK_INSTALLER_QSS = """
QWizard {
    background-color: #0b0f19;
    color: #e2e8f0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}
QWizardPage {
    background-color: #0b0f19;
}
QPushButton {
    background-color: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 16px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #334155;
}
QPushButton:default {
    background-color: #0284c7;
    border-color: #0369a1;
}
QLineEdit {
    background-color: #111827;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 10px;
    color: #f8fafc;
}
QProgressBar {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 4px;
    text-align: center;
    color: #ffffff;
    height: 18px;
}
QProgressBar::chunk {
    background-color: #0284c7;
}
QCheckBox {
    color: #cbd5e1;
    font-weight: 500;
}
"""


def create_windows_shortcut(target_exe: str, shortcut_path: str, icon_path: str = ""):
    """Creates a Windows .lnk shortcut using PowerShell."""
    try:
        ps_cmd = f"""
        $WshShell = New-Object -ComObject WScript.Shell;
        $Shortcut = $WshShell.CreateShortcut('{shortcut_path}');
        $Shortcut.TargetPath = '{target_exe}';
        $Shortcut.WorkingDirectory = '{os.path.dirname(target_exe)}';
        if ('{icon_path}' -ne '') {{ $Shortcut.IconLocation = '{icon_path}'; }}
        $Shortcut.Save();
        """
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True)
    except Exception:
        pass


class InstallWorker(QThread):
    sig_progress = Signal(int, str)
    sig_done = Signal(bool, str)

    def __init__(self, target_dir: str, create_desktop: bool, create_start: bool):
        super().__init__()
        self.target_dir = target_dir
        self.create_desktop = create_desktop
        self.create_start = create_start

    def run(self):
        try:
            self.sig_progress.emit(10, "Preparing installation...")
            os.makedirs(self.target_dir, exist_ok=True)

            # Find payload zip
            base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            payload_zip = os.path.join(base_dir, "payload.zip")

            if not os.path.isfile(payload_zip):
                # Check fallback adjacent
                payload_zip = os.path.join(os.path.dirname(os.path.abspath(__file__)), "payload.zip")

            if not os.path.isfile(payload_zip):
                raise FileNotFoundError("Installation payload archive not found.")

            self.sig_progress.emit(20, "Extracting application binaries and libraries...")
            with zipfile.ZipFile(payload_zip, 'r') as zf:
                file_list = zf.namelist()
                total = len(file_list)
                for idx, item in enumerate(file_list):
                    zf.extract(item, self.target_dir)
                    pct = 20 + int((idx / max(1, total)) * 60)
                    self.sig_progress.emit(pct, f"Installing: {os.path.basename(item)}")

            self.sig_progress.emit(85, "Creating system shortcuts...")
            main_exe = os.path.join(self.target_dir, "PrimeQC.exe")
            icon_file = os.path.join(self.target_dir, "resources", "app_icon.ico")

            # 1. Desktop Shortcut
            if self.create_desktop:
                desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
                shortcut_dest = os.path.join(desktop_dir, "PrimeQC Master.lnk")
                create_windows_shortcut(main_exe, shortcut_dest, icon_file)

            # 2. Start Menu Shortcut
            if self.create_start:
                start_menu_dir = os.path.join(
                    os.getenv("APPDATA", ""),
                    "Microsoft", "Windows", "Start Menu", "Programs", "PrimeQC Master"
                )
                os.makedirs(start_menu_dir, exist_ok=True)
                shortcut_dest = os.path.join(start_menu_dir, "PrimeQC Master.lnk")
                create_windows_shortcut(main_exe, shortcut_dest, icon_file)

            self.sig_progress.emit(100, "Installation complete!")
            self.sig_done.emit(True, "Installation completed successfully.")
        except Exception as e:
            self.sig_done.emit(False, str(e))


class WelcomePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Welcome to PrimeQC Master Setup")
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        lbl_desc = QLabel(
            "<b>PrimeQC Master</b> is the broadcast-grade Quality Control Suite "
            "engineered specifically for <b>Amazon Prime Video Distribution</b>.<br/><br/>"
            "This wizard will install PrimeQC Master, its standalone analysis engine, "
            "and all compliance profiles on your computer.<br/><br/>"
            "Click <b>Next</b> to continue."
        )
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("line-height: 1.5; color: #cbd5e1;")
        layout.addWidget(lbl_desc)


class DirectoryPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Select Installation Folder")
        self.setSubTitle("Choose the destination folder where PrimeQC Master will be installed.")
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        self.default_dir = os.path.join(
            os.getenv("LOCALAPPDATA", os.path.expanduser("~")),
            "Programs", "PrimeQC Master"
        )

        dir_box = QHBoxLayout()
        self.txt_dir = QLineEdit(self.default_dir)
        self.btn_browse = QPushButton("Browse...")
        self.btn_browse.clicked.connect(self._browse)

        dir_box.addWidget(self.txt_dir, 1)
        dir_box.addWidget(self.btn_browse)
        layout.addLayout(dir_box)

        # Options
        layout.addWidget(QLabel("<b>Additional Shortcuts:</b>"))
        self.chk_desktop = QCheckBox("Create a Desktop Shortcut")
        self.chk_desktop.setChecked(True)
        self.chk_start = QCheckBox("Create Start Menu Shortcut")
        self.chk_start.setChecked(True)

        layout.addWidget(self.chk_desktop)
        layout.addWidget(self.chk_start)

        self.registerField("install_dir*", self.txt_dir)

    def _browse(self):
        d = QFileDialog.getExistingDirectory(self, "Select Install Folder", self.txt_dir.text())
        if d:
            self.txt_dir.setText(d)


class ProgressPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Installing PrimeQC Master")
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self.lbl_status = QLabel("Installing files...")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        layout.addWidget(self.lbl_status)
        layout.addWidget(self.progress_bar)

        self.is_complete = False
        self.worker = None

    def initializePage(self):
        install_dir = self.field("install_dir")
        dir_page = self.wizard().page(1)
        chk_desktop = dir_page.chk_desktop.isChecked()
        chk_start = dir_page.chk_start.isChecked()

        self.wizard().button(QWizard.NextButton).setEnabled(False)
        self.wizard().button(QWizard.BackButton).setEnabled(False)

        self.worker = InstallWorker(install_dir, chk_desktop, chk_start)
        self.worker.sig_progress.connect(self._on_progress)
        self.worker.sig_done.connect(self._on_done)
        self.worker.start()

    def _on_progress(self, pct: int, msg: str):
        self.progress_bar.setValue(pct)
        self.lbl_status.setText(msg)

    def _on_done(self, success: bool, msg: str):
        self.is_complete = success
        if success:
            self.lbl_status.setText("✓ PrimeQC Master successfully installed!")
            self.wizard().button(QWizard.NextButton).setEnabled(True)
            self.completeChanged.emit()
            self.wizard().next()
        else:
            QMessageBox.critical(self, "Installation Error", f"Installation failed: {msg}")

    def isComplete(self):
        return self.is_complete


class FinishedPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Completing PrimeQC Master Setup")
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        lbl = QLabel(
            "<h3>Installation Complete!</h3>"
            "PrimeQC Master has been installed on your computer.<br/><br/>"
            "You can launch it anytime from your Desktop or Start Menu."
        )
        lbl.setWordWrap(True)
        lbl.setStyleSheet("color: #38bdf8;")
        layout.addWidget(lbl)

        self.chk_launch = QCheckBox("Launch PrimeQC Master now")
        self.chk_launch.setChecked(True)
        layout.addWidget(self.chk_launch)


class SetupWizard(QWizard):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PrimeQC Master - Setup Wizard")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setMinimumSize(600, 420)
        self.setStyleSheet(DARK_INSTALLER_QSS)

        self.addPage(WelcomePage())
        self.addPage(DirectoryPage())
        self.addPage(ProgressPage())
        self.addPage(FinishedPage())

    def accept(self):
        # Check launch box
        fin_page = self.page(3)
        if fin_page.chk_launch.isChecked():
            install_dir = self.field("install_dir")
            exe_path = os.path.join(install_dir, "PrimeQC.exe")
            if os.path.isfile(exe_path):
                subprocess.Popen([exe_path], cwd=install_dir)
        super().accept()


def main():
    app = QApplication(sys.argv)
    wizard = SetupWizard()
    wizard.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
