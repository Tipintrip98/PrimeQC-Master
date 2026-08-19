"""
Main Window for PrimeQC Master - Amazon Prime Video Quality Control Suite.
Features full multi-language switching (i18n), dropdown menu bar with utilities,
About/Help sections, and official Amazon Prime Video QC reporting.
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
from PySide6.QtGui import QIcon, QKeySequence, QAction, QActionGroup

from .widgets.drop_zone import DropZoneWidget
from .widgets.summary_card import SummaryCardWidget
from .widgets.issue_table import IssueTableWidget
from .widgets.loudness_view import LoudnessViewWidget
from .widgets.video_preview import VideoPreviewWidget
from .widgets.remediation_panel import RemediationPanelWidget
from .widgets.prime_report_view import PrimeReportViewWidget
from .theme import DARK_THEME_QSS

from .dialogs.profile_dialog import ProfileManagerDialog
from .dialogs.export_dialog import ExportReportDialog
from .dialogs.about_dialog import AboutDialog
from .dialogs.help_guide_dialog import HelpGuideDialog
from .dialogs.utilities_dialog import UtilitiesDialog

from ..core.config import ConfigManager
from ..core.constants import ProfileType, PROFILES, Severity
from ..core.i18n import I18nManager, LANGUAGES, _t
from ..engine.analyzer import PrimeQCAnalyzer, QCAnalyzer
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

    def run(self):
        try:
            analyzer = PrimeQCAnalyzer(ConfigManager())
            def prog_cb(stage: str, pct: int, msg: str):
                self.sig_progress.emit(pct, f"[{stage}] {msg}")

            report = analyzer.run_qc(
                file_path=self.media_path,
                profile_name=self.profile_name,
                sidecar_subtitle_path=self.subtitle_path,
                progress_callback=prog_cb
            )
            self.sig_done.emit(report)
        except Exception as e:
            self.sig_error.emit(str(e))



class MainWindow(QMainWindow):
    """Main application window for PrimeQC Master."""

    def __init__(self):
        super().__init__()
        self.i18n = I18nManager()
        self.config_mgr = ConfigManager()
        self.current_report: QCReportData = None
        self.worker: QCWorker = None
        self.start_time = 0

        self.setWindowTitle(self.i18n.translate("app_title"))
        self.resize(1260, 840)
        self.setMinimumSize(1020, 680)
        self.setStyleSheet(DARK_THEME_QSS)

        self._build_menu_bar()
        self._init_ui()
        self._set_app_icon()

        # Subscribe to i18n changes
        self.i18n.subscribe(self.retranslate_ui)

    def _set_app_icon(self):
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "resources", "app_icon.png")
        if os.path.isfile(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def _build_menu_bar(self):
        """Builds comprehensive top dropdown menu bar."""
        mb = self.menuBar()
        mb.clear()

        # 1. Menu File
        self.menu_file = mb.addMenu(_t("menu_file"))

        self.act_open = QAction(_t("menu_open"), self)
        self.act_open.setShortcut(QKeySequence("Ctrl+O"))
        self.act_open.triggered.connect(self._browse_media_file)
        self.menu_file.addAction(self.act_open)

        self.act_sub = QAction(_t("menu_subtitles"), self)
        self.act_sub.triggered.connect(self._browse_subtitle_file)
        self.menu_file.addAction(self.act_sub)

        self.menu_file.addSeparator()

        self.act_save = QAction(_t("menu_save"), self)
        self.act_save.setShortcut(QKeySequence("Ctrl+S"))
        self.act_save.triggered.connect(self._open_export_dialog)
        self.menu_file.addAction(self.act_save)

        self.act_reset = QAction(_t("menu_reset"), self)
        self.act_reset.setShortcut(QKeySequence("Ctrl+N"))
        self.act_reset.triggered.connect(self._reset_ui)
        self.menu_file.addAction(self.act_reset)

        self.menu_file.addSeparator()

        self.act_exit = QAction(_t("menu_exit"), self)
        self.act_exit.setShortcut(QKeySequence("Ctrl+Q"))
        self.act_exit.triggered.connect(self.close)
        self.menu_file.addAction(self.act_exit)

        # 2. Menu Profili Prime Video
        self.menu_profiles = mb.addMenu(_t("menu_profiles"))

        self.prof_actions = {}
        for p_name in [ProfileType.PVD_HD.value, ProfileType.PVD_4K.value, ProfileType.STUDIOS_SDR.value, ProfileType.STUDIOS_HDR.value, ProfileType.TRAILER.value]:
            act = QAction(f"🎯 {p_name}", self)
            act.setCheckable(True)
            act.triggered.connect(lambda checked, name=p_name: self._select_profile(name))
            self.menu_profiles.addAction(act)
            self.prof_actions[p_name] = act

        self.prof_actions[ProfileType.PVD_HD.value].setChecked(True)

        self.menu_profiles.addSeparator()
        self.act_mgr = QAction(_t("menu_profile_settings"), self)
        self.act_mgr.triggered.connect(self._open_profile_dialog)
        self.menu_profiles.addAction(self.act_mgr)

        # 3. Menu Utility / Strumenti
        self.menu_util = mb.addMenu(_t("menu_utilities"))

        self.act_u_loud = QAction(_t("util_loudness"), self)
        self.act_u_loud.triggered.connect(lambda: self._open_utilities_dialog(tab_idx=0))
        self.menu_util.addAction(self.act_u_loud)

        self.act_u_prores = QAction(_t("util_prores"), self)
        self.act_u_prores.triggered.connect(lambda: self._open_utilities_dialog(tab_idx=1))
        self.menu_util.addAction(self.act_u_prores)

        self.act_u_calc = QAction(_t("util_calc"), self)
        self.act_u_calc.triggered.connect(lambda: self._open_utilities_dialog(tab_idx=2))
        self.menu_util.addAction(self.act_u_calc)

        self.act_u_pat = QAction(_t("util_pattern"), self)
        self.act_u_pat.triggered.connect(lambda: self._open_utilities_dialog(tab_idx=3))
        self.menu_util.addAction(self.act_u_pat)

        # 4. Menu Reportistica
        self.menu_rep = mb.addMenu(_t("menu_reports"))

        self.act_rep_pdf = QAction(_t("menu_rep_pdf"), self)
        self.act_rep_pdf.triggered.connect(self._quick_export_pdf)
        self.menu_rep.addAction(self.act_rep_pdf)

        self.act_rep_json = QAction(_t("menu_rep_json"), self)
        self.act_rep_json.triggered.connect(self._quick_export_json)
        self.menu_rep.addAction(self.act_rep_json)

        self.act_rep_csv = QAction(_t("menu_rep_csv"), self)
        self.act_rep_csv.triggered.connect(self._quick_export_csv)
        self.menu_rep.addAction(self.act_rep_csv)

        # 5. Menu Lingua / Language (i18n)
        self.menu_lang = mb.addMenu(_t("menu_language"))
        self.lang_action_group = QActionGroup(self)
        self.lang_actions = {}

        current_code = self.i18n.get_current_language()
        for code, info in LANGUAGES.items():
            act = QAction(f"{info['flag']} {info['name']}", self)
            act.setCheckable(True)
            if code == current_code:
                act.setChecked(True)
            act.triggered.connect(lambda checked, c=code: self._change_language(c))
            self.lang_action_group.addAction(act)
            self.menu_lang.addAction(act)
            self.lang_actions[code] = act

        # 6. Menu Aiuto / Help
        self.menu_help = mb.addMenu(_t("menu_help"))

        self.act_h_guide = QAction(_t("menu_help_guide"), self)
        self.act_h_guide.setShortcut(QKeySequence("F1"))
        self.act_h_guide.triggered.connect(self._open_help_guide)
        self.menu_help.addAction(self.act_h_guide)

        self.menu_help.addSeparator()

        self.act_h_about = QAction(_t("menu_about"), self)
        self.act_h_about.triggered.connect(self._open_about_dialog)
        self.menu_help.addAction(self.act_h_about)

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(14, 10, 14, 10)
        main_layout.setSpacing(10)

        # --- Top Header Frame ---
        header_card = QFrame()
        header_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0f172a, stop:1 #080c14);
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 6px 14px;
            }
        """)
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(6, 4, 6, 4)
        header_layout.setSpacing(14)

        # Branding
        lbl_brand = QLabel("<b style='font-size: 16px; color: #ffffff;'>PRIMEQC</b> <span style='font-size: 16px; font-weight: 900; color: #00a8e8;'>MASTER</span> <span style='background: #064e3b; color: #34d399; font-size: 10px; font-weight: bold; padding: 2px 6px; border-radius: 4px;'>PRIME VIDEO DIRECT</span>")
        header_layout.addWidget(lbl_brand)
        header_layout.addStretch()

        # Profile Selector Pill
        self.lbl_p = QLabel(f"<b>{_t('lbl_profile')}:</b>")
        self.lbl_p.setStyleSheet("color: #94a3b8; font-size: 11px;")
        header_layout.addWidget(self.lbl_p)

        self.cb_profiles = QComboBox()
        self.cb_profiles.addItems([
            ProfileType.PVD_HD.value,
            ProfileType.PVD_4K.value,
            ProfileType.STUDIOS_SDR.value,
            ProfileType.STUDIOS_HDR.value,
            ProfileType.TRAILER.value
        ])
        self.cb_profiles.setMinimumWidth(230)
        self.cb_profiles.currentTextChanged.connect(self._on_combo_profile_changed)
        header_layout.addWidget(self.cb_profiles)

        # Language Quick Selector
        self.cb_lang = QComboBox()
        for code, info in LANGUAGES.items():
            self.cb_lang.addItem(f"{info['flag']} {info['name']}", code)
        
        cur_idx = list(LANGUAGES.keys()).index(self.i18n.get_current_language())
        self.cb_lang.setCurrentIndex(cur_idx)
        self.cb_lang.currentIndexChanged.connect(self._on_combo_lang_changed)
        self.cb_lang.setFixedWidth(130)
        header_layout.addWidget(self.cb_lang)

        # Quick Export Buttons
        btn_quick_pdf = QPushButton("📄 PDF")
        btn_quick_pdf.setToolTip("Quick Export PDF Certificate")
        btn_quick_pdf.clicked.connect(self._quick_export_pdf)
        header_layout.addWidget(btn_quick_pdf)

        main_layout.addWidget(header_card)

        # --- Ingestion & Start QC Bar ---
        ingest_card = QFrame()
        ingest_card.setStyleSheet("""
            QFrame {
                background-color: #0c121e;
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 6px;
            }
        """)
        ingest_layout = QHBoxLayout(ingest_card)
        ingest_layout.setContentsMargins(6, 4, 6, 4)
        ingest_layout.setSpacing(10)

        # Drop Zone (Takes majority of width)
        self.drop_zone = DropZoneWidget()
        self.drop_zone.sig_file_selected.connect(self._on_file_selected)
        ingest_layout.addWidget(self.drop_zone, 1)

        # START QC Action Button
        self.btn_start = QPushButton(_t("btn_start_qc"))
        self.btn_start.setObjectName("PrimaryButton")
        self.btn_start.setFixedHeight(48)
        self.btn_start.setMinimumWidth(210)
        self.btn_start.setStyleSheet("""
            QPushButton#PrimaryButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0284c7, stop:1 #0369a1);
                color: #ffffff;
                font-weight: 800;
                font-size: 13px;
                border: 1px solid #38bdf8;
                border-radius: 6px;
                letter-spacing: 0.5px;
            }
            QPushButton#PrimaryButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #38bdf8, stop:1 #0284c7);
                border-color: #ffffff;
            }
            QPushButton#PrimaryButton:disabled {
                background: #1e293b;
                color: #475569;
                border: 1px solid #1e293b;
            }
        """)
        self.btn_start.clicked.connect(self._start_qc)
        ingest_layout.addWidget(self.btn_start)

        main_layout.addWidget(ingest_card)

        # --- Progress Bar ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(5)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)

        # --- Main Tabbed Content Area ---
        self.tabs = QTabWidget()

        # Tab 1: Amazon Prime Styled QC Report (Primary View)
        self.prime_report_view = PrimeReportViewWidget()
        self.tabs.addTab(self.prime_report_view, f"📊 {_t('tab_prime_report')}")

        # Tab 2: Full Checkpoints Table
        self.issue_table = IssueTableWidget()
        self.issue_table.sig_issue_selected.connect(self._on_issue_selected)
        self.tabs.addTab(self.issue_table, f"📋 {_t('tab_checkpoints')}")

        # Tab 3: Audio Studio & Loudness Radar
        self.loudness_view = LoudnessViewWidget()
        self.tabs.addTab(self.loudness_view, f"🔊 {_t('tab_audio_studio')}")

        # Tab 4: Frame Inspector Player
        self.video_preview = VideoPreviewWidget()
        self.tabs.addTab(self.video_preview, f"👁️ {_t('tab_frame_inspector')}")

        # Tab 5: Remediation
        self.remediation_panel = RemediationPanelWidget()
        self.tabs.addTab(self.remediation_panel, f"🛠️ {_t('tab_remediation')}")

        main_layout.addWidget(self.tabs, 1)

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.lbl_status = QLabel(_t("status_ready"))
        self.lbl_status.setStyleSheet("color: #94a3b8; font-size: 11px;")
        self.status_bar.addWidget(self.lbl_status)

    def _change_language(self, lang_code: str):
        self.i18n.set_language(lang_code)

    def _on_combo_lang_changed(self, idx: int):
        code = self.cb_lang.itemData(idx)
        if code:
            self._change_language(code)

    def retranslate_ui(self, lang_code: str = None):
        """Dynamically translates all UI elements when language changes."""
        if not lang_code:
            lang_code = self.i18n.get_current_language()

        self.setWindowTitle(_t("app_title"))
        self._build_menu_bar()


        # Update controls
        self.lbl_p.setText(f"<b>{_t('lbl_profile')}</b>")
        self.btn_start.setText(_t("btn_start_qc"))

        # Update tabs
        self.tabs.setTabText(0, _t("tab_prime_report"))
        self.tabs.setTabText(1, _t("tab_checkpoints"))
        self.tabs.setTabText(2, _t("tab_audio_studio"))
        self.tabs.setTabText(3, _t("tab_frame_inspector"))
        self.tabs.setTabText(4, _t("tab_remediation"))

        # Update combo if needed
        cur_idx = list(LANGUAGES.keys()).index(lang_code)
        if self.cb_lang.currentIndex() != cur_idx:
            self.cb_lang.blockSignals(True)
            self.cb_lang.setCurrentIndex(cur_idx)
            self.cb_lang.blockSignals(False)

        if not self.current_report:
            self.lbl_status.setText(_t("status_ready"))
        else:
            self.prime_report_view.update_report(self.current_report)

    # --- Actions & Slots ---
    def _browse_media_file(self):
        f, _ = QFileDialog.getOpenFileName(
            self, "Select Video Master", "",
            "Video Master Files (*.mov *.mp4 *.mxf *.ts *.mkv);;All Files (*.*)"
        )
        if f:
            self.drop_zone.set_media_file(f)

    def _browse_subtitle_file(self):
        f, _ = QFileDialog.getOpenFileName(
            self, "Select Sidecar Subtitle", "",
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
            self.lbl_status.setText(f"File: {os.path.basename(media_path)} - {_t('status_ready')}")

    def _start_qc(self):
        media_path = self.drop_zone.get_media_path()
        if not media_path or not os.path.isfile(media_path):
            QMessageBox.warning(self, "Warning", "Please drag & drop or select a valid video master file before starting QC.")
            return

        subtitle_path = self.drop_zone.get_subtitle_path()
        profile_name = self.cb_profiles.currentText()

        self.btn_start.setEnabled(False)
        self.progress_bar.show()
        self.progress_bar.setValue(5)
        self.lbl_status.setText(f"Analyzing '{os.path.basename(media_path)}' ({profile_name})...")
        self.start_time = time.time()

        if self.worker and self.worker.isRunning():
            return

        self.worker = QCWorker(media_path, profile_name, subtitle_path)
        self.worker.sig_progress.connect(self._on_progress)
        self.worker.sig_done.connect(self._on_qc_done)
        self.worker.sig_error.connect(self._on_qc_error)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()

    def _on_progress(self, pct: int, msg: str):
        self.progress_bar.setValue(pct)
        self.lbl_status.setText(f"[{pct}%] {msg}")

    def _on_qc_done(self, report: QCReportData):
        self.current_report = report
        self.btn_start.setEnabled(True)
        self.progress_bar.hide()
        self.worker = None
        elapsed = time.time() - self.start_time

        # Update all UI views
        self.prime_report_view.update_report(report)
        self.issue_table.set_issues(report.issues)
        self.loudness_view.update_loudness(report.loudness_data, report.phase_correlation_data)
        self.remediation_panel.set_report(report)

        if report.video_streams:
            fps = report.video_streams[0].fps
            self.video_preview.load_media(report.file_path, report.duration_sec, fps)

        status_text = "ACCEPTED (100% PASS)" if report.verdict == Severity.PASS else f"REJECTED ({report.fail_count} Errors)"
        self.lbl_status.setText(f"QC Completed in {elapsed:.2f}s | Verdict: {status_text} | {_t('score_label')}: {report.compliance_score:.1f}%")

        # Focus primary Prime Video report tab
        self.tabs.setCurrentIndex(0)

    def _on_qc_error(self, err_msg: str):
        self.btn_start.setEnabled(True)
        self.progress_bar.hide()
        self.worker = None
        self.lbl_status.setText("Error during inspection.")
        QMessageBox.critical(self, "QC Error", f"An error occurred during inspection:\n\n{err_msg}")

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
        self.loudness_view.update_loudness({}, {})
        self.remediation_panel.set_report(None)
        self.lbl_status.setText(_t("status_ready"))


    def _open_export_dialog(self):
        if not self.current_report:
            QMessageBox.information(self, "Info", "Run a QC inspection first before exporting reports.")
            return
        dlg = ExportReportDialog(self.current_report, self)
        dlg.exec()

    def _quick_export_pdf(self):
        if not self.current_report:
            QMessageBox.information(self, "Info", "Run a QC inspection first before exporting reports.")
            return
        def_path = os.path.splitext(self.current_report.file_path)[0] + "_PrimeQC_Certificate.pdf"
        f, _ = QFileDialog.getSaveFileName(self, "Save Prime Video PDF Certificate", def_path, "PDF Documents (*.pdf)")
        if f:
            PDFReportExporter.export(self.current_report, f)
            QMessageBox.information(self, "Success", f"Official PDF Certificate saved successfully:\n{f}")

    def _quick_export_json(self):
        if not self.current_report:
            QMessageBox.information(self, "Info", "Run a QC inspection first.")
            return
        def_path = os.path.splitext(self.current_report.file_path)[0] + "_PrimeQC_Manifest.json"
        f, _ = QFileDialog.getSaveFileName(self, "Save JSON Manifest", def_path, "JSON Files (*.json)")
        if f:
            JSONManifestExporter.export(self.current_report, f)
            QMessageBox.information(self, "Success", f"JSON Manifest saved successfully:\n{f}")

    def _quick_export_csv(self):
        if not self.current_report:
            QMessageBox.information(self, "Info", "Run a QC inspection first.")
            return
        def_path = os.path.splitext(self.current_report.file_path)[0] + "_PrimeQC_Issues.csv"
        f, _ = QFileDialog.getSaveFileName(self, "Save CSV Issues Log", def_path, "CSV Files (*.csv)")
        if f:
            CSVReportExporter.export(self.current_report, f)
            QMessageBox.information(self, "Success", f"CSV Log saved successfully:\n{f}")

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
