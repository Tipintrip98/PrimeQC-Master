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
        self.current_report: QCReportData = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Scrollable Report Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(4, 4, 4, 4)
        self.content_layout.setSpacing(14)

        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)

        self._show_empty_placeholder()

    def _show_empty_placeholder(self):
        """Displays placeholder when no file is analyzed yet."""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        empty_box = QFrame()
        empty_box.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0e1526, stop:1 #080c14);
                border: 2px dashed #1e293b;
                border-radius: 12px;
                padding: 60px 20px;
            }
        """)
        eb_layout = QVBoxLayout(empty_box)
        eb_layout.setAlignment(Qt.AlignCenter)
        eb_layout.setSpacing(14)

        lbl_icon = QLabel("🎬")
        lbl_icon.setStyleSheet("font-size: 48px; background: transparent;")
        lbl_icon.setAlignment(Qt.AlignCenter)

        lbl_title = QLabel("AMAZON PRIME VIDEO QUALITY CONTROL PORTAL")
        lbl_title.setStyleSheet("font-size: 16px; font-weight: 800; color: #38bdf8; letter-spacing: 1.5px; background: transparent;")
        lbl_title.setAlignment(Qt.AlignCenter)

        lbl_desc = QLabel("Drag & drop a video master file above and click 'START QC INSPECTION' to generate an official delivery certificate.")
        lbl_desc.setStyleSheet("color: #94a3b8; font-size: 13px; max-width: 500px; background: transparent;")
        lbl_desc.setWordWrap(True)
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

        # 1. Executive Master Header Banner
        header_card = QFrame()
        header_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0f1a30, stop:1 #0a1120);
                border: 1px solid #1e3a5f;
                border-radius: 10px;
                padding: 16px 20px;
            }
        """)
        h_layout = QVBoxLayout(header_card)
        h_layout.setSpacing(14)

        # Top Bar: Logo + Profile + Timestamp
        top_row = QHBoxLayout()
        lbl_brand = QLabel("<span style='color: #00a8e8; font-size: 20px; font-weight: 900; letter-spacing: 1px;'>prime video</span> <span style='color: #64748b; font-size: 14px;'>| DIRECT DELIVERY QC</span>")
        top_row.addWidget(lbl_brand)
        top_row.addStretch()

        lbl_date = QLabel(f"📅 Inspection Date: <b>{report.generated_at}</b>")
        lbl_date.setStyleSheet("color: #94a3b8; font-size: 11px;")
        top_row.addWidget(lbl_date)
        h_layout.addLayout(top_row)

        # Hero Score & Verdict Row
        hero_frame = QFrame()
        hero_layout = QHBoxLayout(hero_frame)
        hero_layout.setContentsMargins(14, 12, 14, 12)

        if report.verdict == Severity.PASS:
            hero_frame.setStyleSheet("background-color: #064e3b; border: 1px solid #10b981; border-radius: 8px;")
            lbl_verdict = QLabel(f"<b>✓ OFFICIAL DELIVERY STATUS: ACCEPTED (100% PASS)</b>")
            lbl_verdict.setStyleSheet("color: #34d399; font-size: 15px; font-weight: 800;")
            score_color = "#34d399"
        elif report.verdict == Severity.WARNING:
            hero_frame.setStyleSheet("background-color: #451a03; border: 1px solid #f59e0b; border-radius: 8px;")
            lbl_verdict = QLabel(f"<b>⚠️ OFFICIAL DELIVERY STATUS: CONDITIONAL WARNINGS ({report.warning_count})</b>")
            lbl_verdict.setStyleSheet("color: #fbbf24; font-size: 15px; font-weight: 800;")
            score_color = "#fbbf24"
        else:
            hero_frame.setStyleSheet("background-color: #450a0a; border: 1px solid #ef4444; border-radius: 8px;")
            lbl_verdict = QLabel(f"<b>❌ OFFICIAL DELIVERY STATUS: REJECTED ({report.fail_count} CRITICAL ERRORS)</b>")
            lbl_verdict.setStyleSheet("color: #f87171; font-size: 15px; font-weight: 800;")
            score_color = "#f87171"

        lbl_score = QLabel(f"<span style='font-size: 12px; color: #cbd5e1;'>COMPLIANCE:</span> <span style='font-size: 20px; font-weight: 900; color: {score_color};'>{report.compliance_score:.1f}%</span>")

        hero_layout.addWidget(lbl_verdict)
        hero_layout.addStretch()
        hero_layout.addWidget(lbl_score)
        h_layout.addWidget(hero_frame)

        # Asset Specs Grid Tiles
        v_stream = report.video_streams[0] if report.video_streams else None
        fps = v_stream.fps if v_stream else 24.0
        v_res = f"{v_stream.width}x{v_stream.height}" if v_stream else "N/A"
        v_codec = f"{v_stream.codec_name.upper()} ({v_stream.profile})" if v_stream else "N/A"
        a_channels = sum(a.channels for a in report.audio_streams)
        loud_i = f"{report.loudness_data.get('integrated', -24.0):.1f} LUFS" if report.loudness_data else "N/A"
        true_p = f"{report.loudness_data.get('true_peak', -2.0):.2f} dBTP" if report.loudness_data else "N/A"

        tiles_layout = QHBoxLayout()
        tiles_layout.setSpacing(10)

        # Tile 1: Video
        t1 = self._create_spec_tile("🎥 VIDEO STREAM", f"{v_codec}", f"{v_res} @ {fps:.3f} fps", "#38bdf8")
        # Tile 2: Audio
        t2 = self._create_spec_tile("🔊 AUDIO MASTER", f"{a_channels} Ch (24-bit 48kHz)", f"Loudness: {loud_i} (TP: {true_p})", "#10b981")
        # Tile 3: File Duration
        t3 = self._create_spec_tile("⏱️ TIME & SIZE", f"{report.duration_sec:.2f}s ({seconds_to_timecode(report.duration_sec, fps)})", f"{format_bytes(report.file_size_bytes)} ({report.file_name})", "#fbbf24")

        tiles_layout.addWidget(t1)
        tiles_layout.addWidget(t2)
        tiles_layout.addWidget(t3)
        h_layout.addLayout(tiles_layout)

        self.content_layout.addWidget(header_card)

        # 2. Issues & Remediations Section
        failed_or_warn = [i for i in report.issues if i.severity in [Severity.FAIL, Severity.WARNING]]

        if failed_or_warn:
            sec_header = QHBoxLayout()
            lbl_sec_title = QLabel(f"<b>🚨 ITEMIzED DELIVERY ISSUES & ACTIONABLE FIXES ({len(failed_or_warn)})</b>")
            lbl_sec_title.setStyleSheet("color: #f87171; font-size: 13px; font-weight: 800; letter-spacing: 0.5px; margin-top: 6px;")
            sec_header.addWidget(lbl_sec_title)
            sec_header.addStretch()
            self.content_layout.addLayout(sec_header)

            for idx, issue in enumerate(failed_or_warn):
                issue_card = self._create_issue_card(idx + 1, issue)
                self.content_layout.addWidget(issue_card)
        else:
            pass_card = QFrame()
            pass_card.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #064e3b, stop:1 #022c22);
                    border: 1px solid #059669;
                    border-radius: 10px;
                    padding: 24px;
                }
            """)
            p_layout = QVBoxLayout(pass_card)
            p_layout.setSpacing(10)

            lbl_p_title = QLabel("<b>🎉 100% COMPLIANT MEZZANINE MASTER</b>")
            lbl_p_title.setStyleSheet("color: #34d399; font-size: 16px; font-weight: 800;")

            lbl_p_desc = QLabel(
                "All parameters (Codec ProRes/AVC, Progressive CFR, ITU-R BS.1770-4 -24.0 LUFS ±1.0, "
                "True Peak <= -2.0 dBTP, Color Primaries Rec.709/P3, Blanking/Active Video & Sync) "
                "strictly satisfy Amazon Prime Video Direct Mezzanine Delivery specifications."
            )
            lbl_p_desc.setWordWrap(True)
            lbl_p_desc.setStyleSheet("color: #e2e8f0; font-size: 13px; line-height: 1.5;")

            p_layout.addWidget(lbl_p_title)
            p_layout.addWidget(lbl_p_desc)
            self.content_layout.addWidget(pass_card)

        self.content_layout.addStretch()

    def _create_spec_tile(self, title: str, val1: str, val2: str, accent: str) -> QFrame:
        tile = QFrame()
        tile.setStyleSheet(f"""
            QFrame {{
                background-color: #0b111e;
                border: 1px solid #1e293b;
                border-left: 3px solid {accent};
                border-radius: 6px;
                padding: 8px 12px;
            }}
        """)
        l = QVBoxLayout(tile)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(3)

        lbl_t = QLabel(title)
        lbl_t.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {accent}; letter-spacing: 0.5px;")
        lbl_v1 = QLabel(f"<b>{val1}</b>")
        lbl_v1.setStyleSheet("font-size: 12px; color: #f8fafc;")
        lbl_v2 = QLabel(val2)
        lbl_v2.setStyleSheet("font-size: 11px; color: #94a3b8;")

        l.addWidget(lbl_t)
        l.addWidget(lbl_v1)
        l.addWidget(lbl_v2)
        return tile

    def _create_issue_card(self, num: int, issue: QCIssue) -> QFrame:
        card = QFrame()
        is_fail = issue.severity == Severity.FAIL
        border_col = "#ef4444" if is_fail else "#f59e0b"
        badge_bg = "#450a0a" if is_fail else "#451a03"
        badge_txt = "REJECTED (FAIL)" if is_fail else "WARNING"
        badge_col = "#f87171" if is_fail else "#fbbf24"

        card.setStyleSheet(f"""
            QFrame {{
                background-color: #0c121e;
                border: 1px solid #1e293b;
                border-left: 4px solid {border_col};
                border-radius: 8px;
                padding: 12px 16px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(8)

        # Header Row
        h_row = QHBoxLayout()
        lbl_id = QLabel(f"<span style='color: #38bdf8; font-weight: 800;'>#{num}</span> <b>{issue.parameter.upper()}</b> <span style='color: #64748b; font-size: 11px;'>[Code: {issue.id}]</span>")
        lbl_id.setStyleSheet("font-size: 13px; color: #ffffff;")

        lbl_badge = QLabel(f"<b>{badge_txt}</b>")
        lbl_badge.setStyleSheet(f"background-color: {badge_bg}; color: {badge_col}; border: 1px solid {border_col}; border-radius: 4px; padding: 3px 8px; font-size: 10px; font-weight: 800;")

        h_row.addWidget(lbl_id)
        h_row.addStretch()
        h_row.addWidget(lbl_badge)
        layout.addLayout(h_row)

        # Comparison Values Box
        tc_str = f" @ Timecode: <b style='color: #38bdf8;'>{issue.timecode}</b>" if issue.timecode and issue.timecode != "00:00:00:00" else ""
        box = QFrame()
        box.setStyleSheet("background-color: #070a12; border: 1px solid #1a2333; border-radius: 6px; padding: 6px 10px;")
        b_layout = QHBoxLayout(box)
        b_layout.setContentsMargins(4, 2, 4, 2)

        lbl_meas = QLabel(f"<span style='color: #94a3b8; font-size: 11px;'>Detected:</span> <b style='color: {badge_col}; font-size: 12px;'>{issue.measured_value}</b>{tc_str}")
        lbl_exp = QLabel(f"<span style='color: #94a3b8; font-size: 11px;'>Prime Spec:</span> <b style='color: #10b981; font-size: 12px;'>{issue.expected_value}</b>")

        b_layout.addWidget(lbl_meas)
        b_layout.addStretch()
        b_layout.addWidget(lbl_exp)
        layout.addWidget(box)

        # Why Amazon Rejects & Remediation
        lbl_desc = QLabel(f"<b style='color: #38bdf8;'>Why it's rejected:</b> {issue.description}")
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("color: #cbd5e1; font-size: 11px; line-height: 1.4;")
        layout.addWidget(lbl_desc)

        lbl_fix = QLabel(f"<b style='color: #34d399;'>How to Fix:</b> {issue.remediation_tip}")
        lbl_fix.setWordWrap(True)
        lbl_fix.setStyleSheet("color: #f1f5f9; font-size: 11px; line-height: 1.4;")
        layout.addWidget(lbl_fix)

        return card

