"""
Amazon Prime Video Style Interactive QC Report Viewer.
Presents issues and compliance reports formatted in official Amazon Prime Delivery style,
explaining clearly why files fail and providing step-by-step NLE / FFmpeg fixes.
Supports dynamic multi-language localization (i18n).
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextBrowser, QPushButton,
    QFrame, QScrollArea, QApplication, QMessageBox
)
from PySide6.QtCore import Qt
from ...engine.models import QCReportData, QCIssue
from ...core.constants import Severity, StreamType
from ...core.utils import format_bytes, seconds_to_timecode
from ...core.i18n import _t


class PrimeReportViewWidget(QFrame):
    """Amazon Prime Video Style QC Report Viewer."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "CardFrame")
        self.current_report: QCReportData = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Scrollable Report Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(8, 8, 8, 8)
        self.content_layout.setSpacing(12)

        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)

        self._show_empty_placeholder()

    def _show_empty_placeholder(self):
        """Displays placeholder when no file is analyzed yet."""
        # Clear layout
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        empty_box = QFrame()
        empty_box.setStyleSheet("background-color: #111827; border: 1px dashed #1f2937; border-radius: 8px; padding: 40px;")
        eb_layout = QVBoxLayout(empty_box)
        eb_layout.setAlignment(Qt.AlignCenter)
        eb_layout.setSpacing(10)

        lbl_icon = QLabel("📋")
        lbl_icon.setStyleSheet("font-size: 40px; background: transparent;")
        lbl_icon.setAlignment(Qt.AlignCenter)

        lbl_title = QLabel(f"<b>{_t('tab_prime_report').upper()}</b>")
        lbl_title.setStyleSheet("font-size: 15px; color: #94a3b8; background: transparent;")
        lbl_title.setAlignment(Qt.AlignCenter)

        lbl_desc = QLabel(_t("drop_prompt"))
        lbl_desc.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")
        lbl_desc.setAlignment(Qt.AlignCenter)

        eb_layout.addWidget(lbl_icon)
        eb_layout.addWidget(lbl_title)
        eb_layout.addWidget(lbl_desc)

        self.content_layout.addWidget(empty_box)

    def update_report(self, report: QCReportData):
        """Builds and renders the full Amazon Prime Video styled report."""
        self.current_report = report

        # Clear layout
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 1. Official Header Banner
        header_card = QFrame()
        header_card.setStyleSheet("background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 14px;")
        h_layout = QVBoxLayout(header_card)
        h_layout.setSpacing(10)

        title_row = QHBoxLayout()
        lbl_amz = QLabel("prime video")
        lbl_amz.setStyleSheet("font-size: 16px; font-weight: bold; color: #0ea5e9; letter-spacing: 1px;")

        lbl_qc_title = QLabel("<b>| TECHNICAL QUALITY CONTROL INGESTION REPORT</b>")
        lbl_qc_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #cbd5e1;")

        title_row.addWidget(lbl_amz)
        title_row.addWidget(lbl_qc_title)
        title_row.addStretch()

        lbl_date = QLabel(f"{report.generated_at}")
        lbl_date.setStyleSheet("color: #94a3b8; font-size: 11px;")
        title_row.addWidget(lbl_date)

        h_layout.addLayout(title_row)

        # Status Badge
        badge_frame = QFrame()
        b_layout = QHBoxLayout(badge_frame)
        b_layout.setContentsMargins(12, 10, 12, 10)

        if report.verdict == Severity.PASS:
            badge_frame.setStyleSheet("background-color: #064e3b; border: 1px solid #059669; border-radius: 6px;")
            lbl_badge = QLabel(f"<b>✓ {_t('verdict_pass')}</b>")
            lbl_badge.setStyleSheet("color: #34d399; font-size: 13px;")
        elif report.verdict == Severity.WARNING:
            badge_frame.setStyleSheet("background-color: #451a03; border: 1px solid #d97706; border-radius: 6px;")
            lbl_badge = QLabel(f"<b>⚠️ {_t('verdict_warn')}</b>")
            lbl_badge.setStyleSheet("color: #fbbf24; font-size: 13px;")
        else:
            badge_frame.setStyleSheet("background-color: #450a0a; border: 1px solid #dc2626; border-radius: 6px;")
            lbl_badge = QLabel(f"<b>❌ {_t('verdict_fail')} ({report.fail_count})</b>")
            lbl_badge.setStyleSheet("color: #f87171; font-size: 13px;")

        lbl_score = QLabel(f"<b>{_t('score_label')}: {report.compliance_score:.1f}%</b>")
        lbl_score.setStyleSheet("color: #ffffff; font-size: 13px;")

        b_layout.addWidget(lbl_badge)
        b_layout.addStretch()
        b_layout.addWidget(lbl_score)

        h_layout.addWidget(badge_frame)

        # Summary Grid
        v_stream = report.video_streams[0] if report.video_streams else None
        fps = v_stream.fps if v_stream else 24.0
        v_res = f"{v_stream.width}x{v_stream.height}" if v_stream else "N/A"
        v_codec = f"{v_stream.codec_name} ({v_stream.profile})" if v_stream else "N/A"
        a_channels = sum(a.channels for a in report.audio_streams)
        loud_i = f"{report.loudness_data.get('integrated', -24.0):.1f} LUFS" if report.loudness_data else "N/A"
        true_p = f"{report.loudness_data.get('true_peak', -2.0):.2f} dBTP" if report.loudness_data else "N/A"

        meta_html = f"""
        <table style='width: 100%; border-collapse: collapse; font-size: 11px; color: #cbd5e1;'>
            <tr>
                <td style='padding: 3px 0;'><b>File:</b> {report.file_name}</td>
                <td style='padding: 3px 0;'><b>Size:</b> {format_bytes(report.file_size_bytes)}</td>
                <td style='padding: 3px 0;'><b>Duration:</b> {report.duration_sec:.2f}s ({seconds_to_timecode(report.duration_sec, fps)})</td>
            </tr>
            <tr>
                <td style='padding: 3px 0;'><b>Video:</b> {v_codec} | {v_res} @ {fps:.3f} fps</td>
                <td style='padding: 3px 0;'><b>Audio:</b> {a_channels} Channels (48 kHz)</td>
                <td style='padding: 3px 0;'><b>Loudness:</b> {loud_i} (TP: {true_p})</td>
            </tr>
        </table>
        """
        lbl_meta = QLabel(meta_html)
        lbl_meta.setTextFormat(Qt.RichText)
        h_layout.addWidget(lbl_meta)

        self.content_layout.addWidget(header_card)

        # 2. Issues Breakdown Section
        failed_or_warn = [i for i in report.issues if i.severity in [Severity.FAIL, Severity.WARNING]]

        if failed_or_warn:
            lbl_sec_title = QLabel("<b>🚨 DETAILED ISSUES BREAKDOWN & RESOLUTION GUIDELINES:</b>")
            lbl_sec_title.setStyleSheet("color: #f87171; font-size: 13px; margin-top: 6px;")
            self.content_layout.addWidget(lbl_sec_title)

            for idx, issue in enumerate(failed_or_warn):
                issue_card = self._create_issue_explanation_card(idx + 1, issue, report)
                self.content_layout.addWidget(issue_card)
        else:
            # All Passed Congratulatory Card
            pass_card = QFrame()
            pass_card.setStyleSheet("background-color: #064e3b; border: 1px solid #059669; border-radius: 8px; padding: 20px;")
            p_layout = QVBoxLayout(pass_card)
            p_layout.setSpacing(10)

            lbl_p_title = QLabel("<b>🎉 100% COMPLIANT MASTER - READY FOR AMAZON PRIME VIDEO PUBLISHING</b>")
            lbl_p_title.setStyleSheet("color: #34d399; font-size: 14px;")

            lbl_p_desc = QLabel(
                "All checkpoints (Codec ProRes/AVC, Progressive Scan, Constant Frame Rate CFR, "
                "Integrated Loudness -24.0 LKFS, True Peak <= -2.0 dBTP, Discrete Channel Mapping, Rec.709 Color Space, "
                "No Bars/Slates and A/V duration sync) are fully compliant with Amazon Prime Video specifications."
            )
            lbl_p_desc.setWordWrap(True)
            lbl_p_desc.setStyleSheet("color: #e2e8f0; font-size: 12px; line-height: 1.5;")

            p_layout.addWidget(lbl_p_title)
            p_layout.addWidget(lbl_p_desc)
            self.content_layout.addWidget(pass_card)

        self.content_layout.addStretch()

    def _create_issue_explanation_card(self, num: int, issue: QCIssue, report: QCReportData) -> QFrame:
        """Builds an Amazon Prime style failure/warning card explaining the error and fix."""
        card = QFrame()
        is_fail = issue.severity == Severity.FAIL
        border_col = "#dc2626" if is_fail else "#d97706"
        bg_col = "#111827"

        card.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_col};
                border: 1px solid {border_col};
                border-radius: 8px;
                padding: 14px;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setSpacing(10)

        # Header Row
        h_row = QHBoxLayout()
        badge_text = "❌ BLOCKING ERROR (REJECTED)" if is_fail else "⚠️ COMPLIANCE WARNING"
        badge_col = "#f87171" if is_fail else "#fbbf24"

        lbl_id = QLabel(f"<b>#{num} | CODE: {issue.id} - {issue.parameter}</b>")
        lbl_id.setStyleSheet(f"font-size: 13px; font-weight: bold; color: #ffffff;")

        lbl_badge = QLabel(f"<b>{badge_text}</b>")
        lbl_badge.setStyleSheet(f"color: {badge_col}; font-size: 11px; font-weight: bold;")

        h_row.addWidget(lbl_id)
        h_row.addStretch()
        h_row.addWidget(lbl_badge)
        layout.addLayout(h_row)

        # Values Grid
        tc_str = f" @ Timecode: <b>{issue.timecode}</b>" if issue.timecode and issue.timecode != "00:00:00:00" else ""
        val_html = f"""
        <table style='width: 100%; border-collapse: collapse; font-size: 11px; background: #0d1527; padding: 6px; border-radius: 4px;'>
            <tr>
                <td style='color: #94a3b8; width: 130px; padding: 4px;'><b>Measured Value:</b></td>
                <td style='color: {badge_col}; padding: 4px;'><b>{issue.measured_value}</b>{tc_str}</td>
            </tr>
            <tr>
                <td style='color: #94a3b8; padding: 4px;'><b>Amazon Spec:</b></td>
                <td style='color: #34d399; padding: 4px;'><b>{issue.expected_value}</b></td>
            </tr>
        </table>
        """
        lbl_vals = QLabel(val_html)
        lbl_vals.setTextFormat(Qt.RichText)
        layout.addWidget(lbl_vals)

        # Why Amazon Rejects it
        lbl_why_title = QLabel(f"<b>{_t('why_reject_title')}</b>")
        lbl_why_title.setStyleSheet("color: #38bdf8; font-size: 11px; margin-top: 4px;")
        lbl_why_desc = QLabel(issue.description)
        lbl_why_desc.setWordWrap(True)
        lbl_why_desc.setStyleSheet("color: #cbd5e1; font-size: 11px; line-height: 1.4;")
        layout.addWidget(lbl_why_title)
        layout.addWidget(lbl_why_desc)

        # How to Fix it for QC Pass
        lbl_fix_title = QLabel(f"<b>{_t('how_fix_title')}</b>")
        lbl_fix_title.setStyleSheet("color: #34d399; font-size: 11px; margin-top: 4px;")
        lbl_fix_desc = QLabel(issue.remediation_tip)
        lbl_fix_desc.setWordWrap(True)
        lbl_fix_desc.setStyleSheet("color: #f1f5f9; font-size: 11px; line-height: 1.4;")
        layout.addWidget(lbl_fix_title)
        layout.addWidget(lbl_fix_desc)

        return card
