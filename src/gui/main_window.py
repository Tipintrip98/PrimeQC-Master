"""
Main Window for PrimeQC Master - Amazon Prime Video Quality Control Suite.
Features a streamlined, high-contrast Dark Studio UI, full Dropdown Menu Bar with Utilities,
About/Help sections, and Amazon Prime Video styled QC reporting.
"""

import os
import sys
import time
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTabWidget, QProgressBar, QStatusBar, QFileDialog, QMessageBox,
    QMenuBar, QMenu, QFrame, QSplitter
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon, QKeySequence, QAction

from .widgets.drop_zone import DropZoneWidget
from .widgets.summary_card import SummaryCardWidget
from .widgets.issue_table import IssueTableWidget
from .widgets.loudness_view import LoudnessViewWidget
from .widgets.video_preview import VideoPreviewWidget
from .widgets.remediation_panel import RemediationPanelWidget
from .widgets.prime_report_view import PrimeReportViewWidget

from .dialogs.profile_dialog import ProfileManagerDialog
from .dialogs.export_dialog import ExportReportDialog
from .dialogs.about_dialog import AboutDialog
from .dialogs.help_guide_dialog import HelpGuideDialog
from .dialogs.utilities_dialog import UtilitiesDialog

from ..core.config import ConfigManager
from ..core.constants import ProfileType, PROFILES, Severity
from ..engine.analyzer import QCAnalyzer
from ..engine.models import QCReportData
from ..reports.pdf_report import PDFReportExporter
from ..reports.json_manifest import JSONManifestExporter
from ..reports.csv_report import CSVReportExporter


class QCWorker(QThread):
    """Background analysis thread."""
    sig_progress = Signal(int, str)
    sig_done = Signal(object)
    sig_error = Signal(str)

    def __init__(self, media_path: str, profile_name: str, subtitle_path: str = None):
        super().__init__()
        self.media_path = media_path
        self.profile_name = profile_name
        self.subtitle_path = subtitle_path
        self.analyzer = None

    def run(self):
        try:
            profile = PROFILES.get(self.profile_name, PROFILES[ProfileType.PVD_HD.value])
            self.analyzer = QCAnalyzer(profile=profile)

            def progress_hook(pct, msg):
                self.sig_progress.emit(pct, msg)

            report = self.analyzer.analyze(
                media_path=self.media_path,
                subtitle_path=self.subtitle_path,
                progress_cb=progress_hook
            )
            self.sig_done.emit(report)
        except Exception as e:
            self.sig_error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window for PrimeQC Master."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PrimeQC Master - Amazon Prime Video Quality Control Suite")
        self.resize(1200, 800)
        self.setMinimumSize(960, 640)

        self.config_mgr = ConfigManager()
        self.current_report: QCReportData = None
        self.worker: QCWorker = None
        self.start_time = 0

        self._build_menu_bar()
        self._init_ui()
        self._set_app_icon()

    def _set_app_icon(self):
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "resources", "app_icon.png")
        if os.path.isfile(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def _build_menu_bar(self):
        """Builds comprehensive top dropdown menu bar."""
        mb = self.menuBar()

        # 1. Menu File
        menu_file = mb.addMenu("&File")

        act_open = QAction("📂 &Apri Master Video...", self)
        act_open.setShortcut(QKeySequence("Ctrl+O"))
        act_open.triggered.connect(self._browse_media_file)
        menu_file.addAction(act_open)

        act_sub = QAction("🔤 Carica Sottotitoli Sidecar (SRT/VTT)...", self)
        act_sub.triggered.connect(self._browse_subtitle_file)
        menu_file.addAction(act_sub)

        menu_file.addSeparator()

        act_save = QAction("💾 &Salva / Esporta Report QC...", self)
        act_save.setShortcut(QKeySequence("Ctrl+S"))
        act_save.triggered.connect(self._open_export_dialog)
        menu_file.addAction(act_save)

        act_reset = QAction("🔄 Nuovo Controllo / Resetta", self)
        act_reset.setShortcut(QKeySequence("Ctrl+N"))
        act_reset.triggered.connect(self._reset_ui)
        menu_file.addAction(act_reset)

        menu_file.addSeparator()

        act_exit = QAction("🚪 &Esci", self)
        act_exit.setShortcut(QKeySequence("Ctrl+Q"))
        act_exit.triggered.connect(self.close)
        menu_file.addAction(act_exit)

        # 2. Menu Profili Prime Video
        menu_profiles = mb.addMenu("&Profili Amazon")

        self.prof_actions = {}
        for p_name in [ProfileType.PVD_HD.value, ProfileType.PVD_4K.value, ProfileType.STUDIOS_SDR.value, ProfileType.STUDIOS_HDR.value, ProfileType.TRAILER.value]:
            act = QAction(f"🎯 {p_name}", self)
            act.setCheckable(True)
            act.triggered.connect(lambda checked, name=p_name: self._select_profile(name))
            menu_profiles.addAction(act)
            self.prof_actions[p_name] = act

        self.prof_actions[ProfileType.PVD_HD.value].setChecked(True)

        menu_profiles.addSeparator()
        act_mgr = QAction("⚙️ Gestione Standard & Tolleranze...", self)
        act_mgr.triggered.connect(self._open_profile_dialog)
        menu_profiles.addAction(act_mgr)

        # 3. Menu Utility / Strumenti
        menu_util = mb.addMenu("&Utility")

        act_u_loud = QAction("🎚️ Correttore Automatico Loudness (-24 LKFS / -2 dBTP)", self)
        act_u_loud.triggered.connect(lambda: self._open_utilities_dialog(tab_idx=0))
        menu_util.addAction(act_u_loud)

        act_u_prores = QAction("🎞️ Transcoder Master ProRes 422 HQ & Deinterlacciatore", self)
        act_u_prores.triggered.connect(lambda: self._open_utilities_dialog(tab_idx=1))
        menu_util.addAction(act_u_prores)

        act_u_calc = QAction("📏 Calcolatore Spazio & Bitrate per Amazon", self)
        act_u_calc.triggered.connect(lambda: self._open_utilities_dialog(tab_idx=2))
        menu_util.addAction(act_u_calc)

        act_u_pat = QAction("🎨 Generatore Test Pattern SMPTE & Tono 1kHz", self)
        act_u_pat.triggered.connect(lambda: self._open_utilities_dialog(tab_idx=3))
        menu_util.addAction(act_u_pat)

        menu_util.addSeparator()
        act_u_all = QAction("🛠️ Tutte le Utility & Strumenti...", self)
        act_u_all.triggered.connect(lambda: self._open_utilities_dialog(tab_idx=0))
        menu_util.addAction(act_u_all)

        # 4. Menu Reportistica
        menu_rep = mb.addMenu("&Reportistica")

        act_rep_pdf = QAction("📄 Genera Certificato PDF Ufficiale Amazon Prime", self)
        act_rep_pdf.triggered.connect(self._quick_export_pdf)
        menu_rep.addAction(act_rep_pdf)

        act_rep_json = QAction("📦 Esporta Manifest Tecnico JSON", self)
        act_rep_json.triggered.connect(self._quick_export_json)
        menu_rep.addAction(act_rep_json)

        act_rep_csv = QAction("📊 Esporta Tabella Errori CSV", self)
        act_rep_csv.triggered.connect(self._quick_export_csv)
        menu_rep.addAction(act_rep_csv)

        # 5. Menu Aiuto / Help
        menu_help = mb.addMenu("&Aiuto")

        act_h_guide = QAction("📚 &Guida agli Standard Amazon Prime Video", self)
        act_h_guide.setShortcut(QKeySequence("F1"))
        act_h_guide.triggered.connect(self._open_help_guide)
        menu_help.addAction(act_h_guide)

        menu_help.addSeparator()

        act_h_about = QAction("🛡️ &Informazioni su PrimeQC Master (Sviluppatore & Versione)...", self)
        act_h_about.triggered.connect(self._open_about_dialog)
        menu_help.addAction(act_h_about)

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(10)

        # --- Top Ingest Bar ---
        top_card = QFrame()
        top_card.setStyleSheet("background-color: #111827; border: 1px solid #1f2937; border-radius: 8px; padding: 6px 10px;")
        top_layout = QHBoxLayout(top_card)
        top_layout.setContentsMargins(4, 4, 4, 4)
        top_layout.setSpacing(10)

        # Profile Selector
        lbl_p = QLabel("<b>Profilo Amazon:</b>")
        lbl_p.setStyleSheet("color: #94a3b8; font-size: 11px;")
        top_layout.addWidget(lbl_p)

        self.cb_profiles = QComboBox()
        self.cb_profiles.addItems([
            ProfileType.PVD_HD.value,
            ProfileType.PVD_4K.value,
            ProfileType.STUDIOS_SDR.value,
            ProfileType.STUDIOS_HDR.value,
            ProfileType.TRAILER.value
        ])
        self.cb_profiles.setMinimumWidth(260)
        self.cb_profiles.currentTextChanged.connect(self._on_combo_profile_changed)
        top_layout.addWidget(self.cb_profiles)

        top_layout.addSpacing(10)

        # Compact Ingestion Zone
        self.drop_zone = DropZoneWidget()
        self.drop_zone.sig_file_selected.connect(self._on_file_selected)
        top_layout.addWidget(self.drop_zone, 1)

        # Start QC Button
        self.btn_start = QPushButton("⚡ START QC INSPECTION")
        self.btn_start.setObjectName("PrimaryButton")
        self.btn_start.setFixedHeight(44)
        self.btn_start.setMinimumWidth(200)
        self.btn_start.setStyleSheet("""
            QPushButton#PrimaryButton {
                background-color: #0284c7;
                color: #ffffff;
                font-weight: bold;
                font-size: 13px;
                border-radius: 6px;
                letter-spacing: 0.5px;
            }
            QPushButton#PrimaryButton:hover {
                background-color: #0369a1;
            }
            QPushButton#PrimaryButton:disabled {
                background-color: #334155;
                color: #64748b;
            }
        """)
        self.btn_start.clicked.connect(self._start_qc)
        top_layout.addWidget(self.btn_start)

        main_layout.addWidget(top_card)

        # --- Progress Bar ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)

        # --- Main Tabbed Content Area ---
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #1f2937;
                background-color: #0d1527;
                border-radius: 6px;
            }
            QTabBar::tab {
                background-color: #0b0f19;
                color: #94a3b8;
                padding: 8px 18px;
                font-weight: 600;
                font-size: 12px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #0d1527;
                color: #38bdf8;
                border-bottom: 2px solid #38bdf8;
            }
        """)

        # Tab 1: Amazon Prime Styled QC Report (Primary View)
        self.prime_report_view = PrimeReportViewWidget()
        self.tabs.addTab(self.prime_report_view, "📋 Report Ufficiale Amazon Prime")

        # Tab 2: Full Checkpoints Table
        self.issue_table = IssueTableWidget()
        self.issue_table.sig_issue_selected.connect(self._on_issue_selected)
        self.tabs.addTab(self.issue_table, "📊 Tabella Checkpoint & Anomaly Log")

        # Tab 3: Audio Studio & Loudness Radar
        self.loudness_view = LoudnessViewWidget()
        self.tabs.addTab(self.loudness_view, "🔊 Studio Audio & Radar Loudness")

        # Tab 4: Frame Inspector Player
        self.video_preview = VideoPreviewWidget()
        self.tabs.addTab(self.video_preview, "👁️ Ispettore Fotogrammi & Player")

        # Tab 5: Remediation
        self.remediation_panel = RemediationPanelWidget()
        self.tabs.addTab(self.remediation_panel, "🔧 Guida Correzione NLE & FFmpeg")

        main_layout.addWidget(self.tabs, 1)

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.lbl_status = QLabel("Pronto per l'ingestione. Seleziona un master video.")
        self.lbl_status.setStyleSheet("color: #94a3b8; font-size: 11px;")
        self.status_bar.addWidget(self.lbl_status)

    # --- Actions & Slots ---
    def _browse_media_file(self):
        f, _ = QFileDialog.getOpenFileName(
            self, "Seleziona Master Video", "",
            "Video Master Files (*.mov *.mp4 *.mxf *.ts *.mkv);;All Files (*.*)"
        )
        if f:
            self.drop_zone.set_media_file(f)

    def _browse_subtitle_file(self):
        f, _ = QFileDialog.getOpenFileName(
            self, "Seleziona Sottotitoli Sidecar", "",
            "Subtitle Files (*.srt *.vtt *.ttml *.dfxp *.scc);;All Files (*.*)"
        )
        if f:
            self.drop_zone.set_subtitle_file(f)

    def _select_profile(self, name: str):
        self.cb_profiles.setCurrentText(name)
        for p_name, act in self.prof_actions.items():
            act.setChecked(p_name == name)

    def _on_combo_profile_changed(self, name: str):
        for p_name, act in self.prof_actions.items():
            act.setChecked(p_name == name)

    def _on_file_selected(self, media_path: str):
        if media_path:
            self.lbl_status.setText(f"File caricato: {os.path.basename(media_path)} - Pronto per il controllo.")

    def _start_qc(self):
        media_path = self.drop_zone.get_media_path()
        if not media_path or not os.path.isfile(media_path):
            QMessageBox.warning(self, "Attenzione", "Trascina o seleziona un file master video valido prima di avviare il QC.")
            return

        subtitle_path = self.drop_zone.get_subtitle_path()
        profile_name = self.cb_profiles.currentText()

        self.btn_start.setEnabled(False)
        self.progress_bar.show()
        self.progress_bar.setValue(5)
        self.lbl_status.setText(f"Analisi in corso su '{os.path.basename(media_path)}' con profilo '{profile_name}'...")
        self.start_time = time.time()

        self.worker = QCWorker(media_path, profile_name, subtitle_path)
        self.worker.sig_progress.connect(self._on_progress)
        self.worker.sig_done.connect(self._on_qc_done)
        self.worker.sig_error.connect(self._on_qc_error)
        self.worker.start()

    def _on_progress(self, pct: int, msg: str):
        self.progress_bar.setValue(pct)
        self.lbl_status.setText(f"[{pct}%] {msg}")

    def _on_qc_done(self, report: QCReportData):
        self.current_report = report
        self.btn_start.setEnabled(True)
        self.progress_bar.hide()
        elapsed = time.time() - self.start_time

        # Update all UI views
        self.prime_report_view.update_report(report)
        self.issue_table.set_issues(report.issues)
        self.loudness_view.update_loudness(report.loudness_data, report.issues)
        self.remediation_panel.set_report(report)

        if report.video_streams:
            fps = report.video_streams[0].fps
            self.video_preview.load_media(report.file_path, report.duration_sec, fps)

        status_text = "APPROVATO (100% CONFORME)" if report.verdict == Severity.PASS else f"RIGETTATO ({report.fail_count} Errori)"
        self.lbl_status.setText(f"QC completato in {elapsed:.2f}s | Esito: {status_text} | Punteggio: {report.compliance_score:.1f}%")

        # Focus primary Prime Video report tab
        self.tabs.setCurrentIndex(0)

    def _on_qc_error(self, err_msg: str):
        self.btn_start.setEnabled(True)
        self.progress_bar.hide()
        self.lbl_status.setText("Errore durante l'analisi.")
        QMessageBox.critical(self, "Errore QC", f"Si è verificato un errore durante l'ispezione:\n\n{err_msg}")

    def _on_issue_selected(self, issue):
        """Jump to timecode in video preview when issue is clicked."""
        if issue.timecode and self.video_preview:
            self.tabs.setCurrentWidget(self.video_preview)
            self.video_preview.seek_timecode(issue.timecode)

    def _reset_ui(self):
        self.current_report = None
        self.drop_zone.clear()
        self.prime_report_view._show_empty_placeholder()
        self.issue_table.set_issues([])
        self.loudness_view.update_loudness({}, [])
        self.remediation_panel.set_report(None)
        self.lbl_status.setText("Pronto per l'ingestione. Seleziona un master video.")

    def _open_export_dialog(self):
        if not self.current_report:
            QMessageBox.information(self, "Info", "Esegui prima un'analisi QC su un file per esportare il report.")
            return
        dlg = ExportReportDialog(self.current_report, self)
        dlg.exec()

    def _quick_export_pdf(self):
        if not self.current_report:
            QMessageBox.information(self, "Info", "Esegui prima un'analisi QC su un file.")
            return
        def_path = os.path.splitext(self.current_report.file_path)[0] + "_PrimeQC_Certificate.pdf"
        f, _ = QFileDialog.getSaveFileName(self, "Salva Certificato PDF Prime Video", def_path, "PDF Documents (*.pdf)")
        if f:
            PDFReportExporter.export(self.current_report, f)
            QMessageBox.information(self, "Successo", f"Certificato PDF generato con successo:\n{f}")

    def _quick_export_json(self):
        if not self.current_report:
            QMessageBox.information(self, "Info", "Esegui prima un'analisi QC su un file.")
            return
        def_path = os.path.splitext(self.current_report.file_path)[0] + "_PrimeQC_Manifest.json"
        f, _ = QFileDialog.getSaveFileName(self, "Salva Manifest JSON", def_path, "JSON Files (*.json)")
        if f:
            JSONManifestExporter.export(self.current_report, f)
            QMessageBox.information(self, "Successo", f"Manifest JSON generato con successo:\n{f}")

    def _quick_export_csv(self):
        if not self.current_report:
            QMessageBox.information(self, "Info", "Esegui prima un'analisi QC su un file.")
            return
        def_path = os.path.splitext(self.current_report.file_path)[0] + "_PrimeQC_Issues.csv"
        f, _ = QFileDialog.getSaveFileName(self, "Salva Tabella CSV", def_path, "CSV Files (*.csv)")
        if f:
            CSVReportExporter.export(self.current_report, f)
            QMessageBox.information(self, "Successo", f"Tabella CSV generata con successo:\n{f}")

    def _open_profile_dialog(self):
        dlg = ProfileManagerDialog(self)
        dlg.exec()

    def _open_utilities_dialog(self, tab_idx: int = 0):
        initial_file = self.drop_zone.get_media_path() if hasattr(self, 'drop_zone') else ""
        dlg = UtilitiesDialog(self, initial_file=initial_file)
        dlg.tabs.setCurrentIndex(tab_idx)
        dlg.exec()

    def _open_help_guide(self):
        dlg = HelpGuideDialog(self)
        dlg.exec()

    def _open_about_dialog(self):
        dlg = AboutDialog(self)
        dlg.exec()
