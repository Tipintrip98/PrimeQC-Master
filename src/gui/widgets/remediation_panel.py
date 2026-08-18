"""
Remediation and Auto-Conform Assistant Panel.
Provides instant, copyable FFmpeg commands and NLE instructions to make assets 100% compliant.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QFrame, QMessageBox, QApplication
)
from PySide6.QtCore import Qt
from ...engine.models import QCReportData
from ...engine.remediation import RemediationEngine


class RemediationPanelWidget(QFrame):
    """Displays corrective actions and FFmpeg conforming scripts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "CardFrame")
        self.current_report = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        # Header
        top_row = QHBoxLayout()
        lbl_title = QLabel("<b>🛠️ 1-CLICK COMPLIANCE REMEDIATION & CONFORM ENGINE</b>")
        lbl_title.setStyleSheet("font-size: 13px; color: #38bdf8;")
        top_row.addWidget(lbl_title)
        top_row.addStretch()

        self.btn_copy_cmd = QPushButton("📋 Copy FFmpeg Conform Command")
        self.btn_copy_cmd.setObjectName("PrimaryButton")
        self.btn_copy_cmd.clicked.connect(self._copy_command)
        top_row.addWidget(self.btn_copy_cmd)

        layout.addLayout(top_row)

        lbl_desc = QLabel("Automated script to transcode, correct loudness to -24.0 LUFS, deinterlace, and tag color space according to Amazon Prime specifications:")
        lbl_desc.setStyleSheet("color: #94a3b8; font-size: 11px;")
        layout.addWidget(lbl_desc)

        # FFmpeg Command Box
        self.txt_command = QTextEdit()
        self.txt_command.setReadOnly(True)
        self.txt_command.setFixedHeight(90)
        self.txt_command.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                background-color: #050811;
                border: 1px solid #1e293b;
                color: #38bdf8;
                padding: 8px;
            }
        """)
        layout.addWidget(self.txt_command)

        # NLE Instructions Box
        lbl_nle_title = QLabel("<b>NLE WORKFLOW GUIDELINES (DaVinci Resolve / Premiere Pro):</b>")
        lbl_nle_title.setStyleSheet("color: #e2e8f0; font-weight: bold; font-size: 12px; margin-top: 6px;")
        layout.addWidget(lbl_nle_title)

        self.txt_nle = QTextEdit()
        self.txt_nle.setReadOnly(True)
        self.txt_nle.setStyleSheet("""
            QTextEdit {
                background-color: #0d1527;
                border: 1px solid #1f2937;
                color: #cbd5e1;
                font-size: 11px;
                line-height: 1.4;
            }
        """)
        layout.addWidget(self.txt_nle, 1)

    def set_report(self, report: QCReportData):
        """Sets active QC report and updates remediation instructions."""
        if report:
            self.update_remediation(report)
        else:
            self.clear()

    def clear(self):
        """Clears the remediation panel."""
        self.current_report = None
        self.txt_command.clear()
        self.txt_nle.clear()

    def update_remediation(self, report: QCReportData):
        """Generates and updates conform scripts and NLE instructions."""
        self.current_report = report
        if not report:
            self.clear()
            return
        cmd = RemediationEngine.generate_ffmpeg_fix_command(report)
        self.txt_command.setPlainText(cmd)

        nle_steps = RemediationEngine.get_nle_instructions(report)
        nle_html = ""
        for step in nle_steps:
            nle_html += f"<h4 style='color:#38bdf8; margin: 4px 0;'>📌 {step['title']}</h4>"
            nle_html += f"<p><b>DaVinci Resolve:</b> {step['davinci']}</p>"
            nle_html += f"<p><b>Premiere Pro:</b> {step['premiere']}</p>"
            nle_html += "<hr style='border: 0; border-top: 1px solid #1e293b;'>"

        self.txt_nle.setHtml(nle_html)


    def _copy_command(self):
        cmd = self.txt_command.toPlainText().strip()
        if cmd:
            clipboard = QApplication.clipboard()
            clipboard.setText(cmd)
            QMessageBox.information(self, "Copied", "FFmpeg conforming command copied to clipboard!")
