"""
PrimeQC Master - Modern Universal Windows Setup Installer.
Single-window streamlined installation wizard with multi-language support,
dependency self-extraction, desktop/start menu shortcut creation, and auto-launch.
"""

import sys
import os
import zipfile
import shutil
import subprocess
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QCheckBox, QProgressBar, QMessageBox,
    QFrame, QStackedWidget
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon, QFont, QPixmap


# Translations for Installer
INSTALLER_TRANSLATIONS = {
    "it": {
        "title": "Installazione PrimeQC Master - Quality Control Amazon Prime Video",
        "header_title": "PrimeQC Master v2.5",
        "header_sub": "Installazione Suite Quality Control per Amazon Prime Video",
        "dest_label": "Cartella di destinazione:",
        "browse": "Sfoglia...",
        "chk_desktop": "Crea icona sul Desktop",
        "chk_start": "Crea collegamento nel Menu Start",
        "btn_install": "🚀 INSTALLA ORA",
        "btn_cancel": "Annulla",
        "installing_title": "Installazione in corso...",
        "installing_sub": "Estrazione delle librerie e configurazione dei motori di analisi...",
        "complete_title": "🎉 Installazione Completata!",
        "complete_sub": "PrimeQC Master è stato installato con successo sul tuo computer.",
        "chk_launch": "Avvia PrimeQC Master adesso",
        "btn_finish": "FINE / AVVIA",
        "btn_close": "Chiudi",
        "err_title": "Errore di Installazione",
        "err_payload": "Archivio di installazione (payload.zip) non trovato nell'installer.",
        "err_in_use": "PrimeQC.exe è attualmente aperto. Chiudilo e riprova."
    },
    "en": {
        "title": "PrimeQC Master Setup - Amazon Prime Video Quality Control",
        "header_title": "PrimeQC Master v2.5",
        "header_sub": "Quality Control Suite Installation for Amazon Prime Video",
        "dest_label": "Destination Folder:",
        "browse": "Browse...",
        "chk_desktop": "Create Desktop Shortcut",
        "chk_start": "Create Start Menu Shortcut",
        "btn_install": "🚀 INSTALL NOW",
        "btn_cancel": "Cancel",
        "installing_title": "Installing PrimeQC Master...",
        "installing_sub": "Extracting application binaries, FFmpeg engines, and libraries...",
        "complete_title": "🎉 Installation Complete!",
        "complete_sub": "PrimeQC Master has been installed successfully on your computer.",
        "chk_launch": "Launch PrimeQC Master now",
        "btn_finish": "FINISH / LAUNCH",
        "btn_close": "Close",
        "err_title": "Installation Error",
        "err_payload": "Installation payload archive (payload.zip) not found.",
        "err_in_use": "PrimeQC.exe is currently running. Please close it and retry."
    }
}


def get_t(key: str, lang: str = "it") -> str:
    lang_dict = INSTALLER_TRANSLATIONS.get(lang, INSTALLER_TRANSLATIONS["it"])
    return lang_dict.get(key, INSTALLER_TRANSLATIONS["en"].get(key, key))


def create_windows_shortcut(target_exe: str, shortcut_path: str, icon_path: str = ""):
    """Creates a Windows .lnk shortcut using PowerShell COM object."""
    try:
        ps_cmd = (
            f"$WshShell = New-Object -ComObject WScript.Shell; "
            f"$Shortcut = $WshShell.CreateShortcut('{shortcut_path}'); "
            f"$Shortcut.TargetPath = '{target_exe}'; "
            f"$Shortcut.WorkingDirectory = '{os.path.dirname(target_exe)}'; "
        )
        if icon_path and os.path.isfile(icon_path):
            ps_cmd += f"$Shortcut.IconLocation = '{icon_path}'; "
        ps_cmd += "$Shortcut.Save();"

        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, timeout=5)
    except Exception:
        pass


class ExtractWorker(QThread):
    """Background worker that extracts payload and creates system shortcuts."""
    sig_progress = Signal(int, str)
    sig_done = Signal(bool, str)

    def __init__(self, target_dir: str, create_desktop: bool, create_start: bool):
        super().__init__()
        self.target_dir = target_dir
        self.create_desktop = create_desktop
        self.create_start = create_start

    def run(self):
        try:
            self.sig_progress.emit(5, "Inizializzazione cartella...")
            os.makedirs(self.target_dir, exist_ok=True)

            # Locate payload.zip in PyInstaller temp dir or adjacent
            base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            payload_zip = os.path.join(base_dir, "payload.zip")

            if not os.path.isfile(payload_zip):
                payload_zip = os.path.join(os.path.dirname(os.path.abspath(__file__)), "payload.zip")

            if not os.path.isfile(payload_zip):
                raise FileNotFoundError("File 'payload.zip' non trovato nel pacchetto di installazione.")

            self.sig_progress.emit(15, "Estrazione file dell'applicazione...")
            with zipfile.ZipFile(payload_zip, 'r') as zf:
                members = zf.namelist()
                total = len(members)
                for idx, member in enumerate(members):
                    zf.extract(member, self.target_dir)
                    if idx % 10 == 0 or idx == total - 1:
                        pct = 15 + int((idx / max(1, total)) * 70)
                        self.sig_progress.emit(pct, f"Copia: {os.path.basename(member)}")

            self.sig_progress.emit(90, "Configurazione collegamenti di sistema...")
            main_exe = os.path.join(self.target_dir, "PrimeQC.exe")
            icon_file = os.path.join(self.target_dir, "resources", "app_icon.ico")

            # 1. Desktop Shortcut
            if self.create_desktop:
                desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
                shortcut_path = os.path.join(desktop_dir, "PrimeQC Master.lnk")
                create_windows_shortcut(main_exe, shortcut_path, icon_file)

            # 2. Start Menu Shortcut
            if self.create_start:
                start_dir = os.path.join(
                    os.getenv("APPDATA", ""),
                    "Microsoft", "Windows", "Start Menu", "Programs", "PrimeQC Master"
                )
                os.makedirs(start_dir, exist_ok=True)
                shortcut_path = os.path.join(start_dir, "PrimeQC Master.lnk")
                create_windows_shortcut(main_exe, shortcut_path, icon_file)

            self.sig_progress.emit(100, "Installazione completata con successo!")
            self.sig_done.emit(True, "OK")
        except Exception as e:
            self.sig_done.emit(False, str(e))


class ModernInstallerWindow(QMainWindow):
    """Clean, high-reliability single-window installer."""

    def __init__(self):
        super().__init__()
        self.lang = "it"
        self.setWindowTitle(get_t("title", self.lang))
        self.setFixedSize(620, 440)
        self.worker = None

        self._init_ui()
        self._set_icon()

    def _set_icon(self):
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_dir, "resources", "app_icon.ico")
        if os.path.isfile(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def _init_ui(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0b0f19;
            }
            QLabel {
                color: #f8fafc;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit {
                background-color: #111827;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 8px 12px;
                color: #f8fafc;
                font-size: 13px;
            }
            QPushButton {
                background-color: #1e293b;
                color: #f8fafc;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 8px 18px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #334155;
            }
            QPushButton#PrimaryBtn {
                background-color: #0284c7;
                border: 1px solid #0369a1;
                color: #ffffff;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton#PrimaryBtn:hover {
                background-color: #0369a1;
            }
            QProgressBar {
                background-color: #111827;
                border: 1px solid #334155;
                border-radius: 6px;
                text-align: center;
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
                height: 24px;
            }
            QProgressBar::chunk {
                background-color: #0284c7;
                border-radius: 5px;
            }
            QCheckBox {
                color: #cbd5e1;
                font-size: 13px;
                spacing: 8px;
            }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # Header Card
        header_card = QFrame()
        header_card.setStyleSheet("background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 12px 16px;")
        h_layout = QHBoxLayout(header_card)
        h_layout.setContentsMargins(4, 4, 4, 4)

        icon_lbl = QLabel("🛡️")
        icon_lbl.setStyleSheet("font-size: 32px; background: transparent;")
        h_layout.addWidget(icon_lbl)

        txt_v = QVBoxLayout()
        lbl_h_title = QLabel(f"<b>{get_t('header_title', self.lang)}</b>")
        lbl_h_title.setStyleSheet("font-size: 17px; color: #38bdf8; background: transparent;")
        lbl_h_sub = QLabel(get_t("header_sub", self.lang))
        lbl_h_sub.setStyleSheet("font-size: 12px; color: #94a3b8; background: transparent;")
        txt_v.addWidget(lbl_h_title)
        txt_v.addWidget(lbl_h_sub)
        h_layout.addLayout(txt_v, 1)

        main_layout.addWidget(header_card)

        # Stacked Pages
        self.stack = QStackedWidget()

        # Page 0: Options & Destination
        self.page_options = self._build_page_options()
        self.stack.addWidget(self.page_options)

        # Page 1: Progress
        self.page_progress = self._build_page_progress()
        self.stack.addWidget(self.page_progress)

        # Page 2: Finished
        self.page_finished = self._build_page_finished()
        self.stack.addWidget(self.page_finished)

        main_layout.addWidget(self.stack, 1)

    def _build_page_options(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(14)

        # Destination Folder
        layout.addWidget(QLabel(f"<b>{get_t('dest_label', self.lang)}</b>"))
        dir_row = QHBoxLayout()
        self.default_dir = os.path.join(
            os.getenv("LOCALAPPDATA", os.path.expanduser("~")),
            "Programs", "PrimeQC Master"
        )
        self.txt_dest = QLineEdit(self.default_dir)
        self.btn_browse = QPushButton(get_t("browse", self.lang))
        self.btn_browse.clicked.connect(self._browse_dir)
        dir_row.addWidget(self.txt_dest, 1)
        dir_row.addWidget(self.btn_browse)
        layout.addLayout(dir_row)

        layout.addSpacing(6)

        # Checkboxes
        self.chk_desktop = QCheckBox(get_t("chk_desktop", self.lang))
        self.chk_desktop.setChecked(True)
        self.chk_start = QCheckBox(get_t("chk_start", self.lang))
        self.chk_start.setChecked(True)
        layout.addWidget(self.chk_desktop)
        layout.addWidget(self.chk_start)

        layout.addStretch()

        # Bottom Buttons
        btn_row = QHBoxLayout()
        self.btn_cancel = QPushButton(get_t("btn_cancel", self.lang))
        self.btn_cancel.clicked.connect(self.close)

        self.btn_install = QPushButton(get_t("btn_install", self.lang))
        self.btn_install.setObjectName("PrimaryBtn")
        self.btn_install.setFixedHeight(42)
        self.btn_install.clicked.connect(self._start_install)

        btn_row.addWidget(self.btn_cancel)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_install)
        layout.addLayout(btn_row)

        return w

    def _build_page_progress(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 20, 0, 0)
        layout.setSpacing(16)

        self.lbl_prog_title = QLabel(f"<h3>{get_t('installing_title', self.lang)}</h3>")
        self.lbl_prog_title.setStyleSheet("color: #38bdf8;")
        self.lbl_prog_sub = QLabel(get_t("installing_sub", self.lang))
        self.lbl_prog_sub.setStyleSheet("color: #94a3b8; font-size: 12px;")

        self.prog_bar = QProgressBar()
        self.prog_bar.setRange(0, 100)
        self.prog_bar.setValue(0)

        self.lbl_prog_status = QLabel("Preparazione...")
        self.lbl_prog_status.setStyleSheet("color: #cbd5e1; font-size: 11px;")

        layout.addWidget(self.lbl_prog_title)
        layout.addWidget(self.lbl_prog_sub)
        layout.addWidget(self.prog_bar)
        layout.addWidget(self.lbl_prog_status)
        layout.addStretch()

        return w

    def _build_page_finished(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(16)

        card = QFrame()
        card.setStyleSheet("background-color: #064e3b; border: 1px solid #059669; border-radius: 8px; padding: 18px;")
        c_layout = QVBoxLayout(card)
        c_layout.setSpacing(8)

        lbl_f_title = QLabel(f"<b>{get_t('complete_title', self.lang)}</b>")
        lbl_f_title.setStyleSheet("font-size: 16px; color: #34d399; background: transparent;")
        lbl_f_sub = QLabel(get_t("complete_sub", self.lang))
        lbl_f_sub.setStyleSheet("font-size: 13px; color: #e2e8f0; background: transparent; line-height: 1.4;")
        lbl_f_sub.setWordWrap(True)

        c_layout.addWidget(lbl_f_title)
        c_layout.addWidget(lbl_f_sub)
        layout.addWidget(card)

        self.chk_launch = QCheckBox(get_t("chk_launch", self.lang))
        self.chk_launch.setChecked(True)
        layout.addWidget(self.chk_launch)

        layout.addStretch()

        btn_row = QHBoxLayout()
        self.btn_finish = QPushButton(get_t("btn_finish", self.lang))
        self.btn_finish.setObjectName("PrimaryBtn")
        self.btn_finish.setFixedHeight(42)
        self.btn_finish.clicked.connect(self._finish_and_exit)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_finish)
        layout.addLayout(btn_row)

        return w

    def _browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Seleziona cartella", self.txt_dest.text())
        if d:
            self.txt_dest.setText(d)

    def _start_install(self):
        target_dir = self.txt_dest.text().strip()
        if not target_dir:
            QMessageBox.warning(self, "Attenzione", "Specificare una cartella di destinazione valida.")
            return

        create_desktop = self.chk_desktop.isChecked()
        create_start = self.chk_start.isChecked()

        self.stack.setCurrentIndex(1)

        self.worker = ExtractWorker(target_dir, create_desktop, create_start)
        self.worker.sig_progress.connect(self._on_progress)
        self.worker.sig_done.connect(self._on_done)
        self.worker.start()

    def _on_progress(self, pct: int, msg: str):
        self.prog_bar.setValue(pct)
        self.lbl_prog_status.setText(msg)

    def _on_done(self, success: bool, msg: str):
        if success:
            self.stack.setCurrentIndex(2)
        else:
            QMessageBox.critical(self, get_t("err_title", self.lang), f"Errore durante l'installazione:\n\n{msg}")
            self.stack.setCurrentIndex(0)

    def _finish_and_exit(self):
        if self.chk_launch.isChecked():
            target_dir = self.txt_dest.text().strip()
            exe_path = os.path.join(target_dir, "PrimeQC.exe")
            if os.path.isfile(exe_path):
                try:
                    subprocess.Popen([exe_path], cwd=target_dir)
                except Exception:
                    pass
        self.close()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PrimeQC Master Setup")
    win = ModernInstallerWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
