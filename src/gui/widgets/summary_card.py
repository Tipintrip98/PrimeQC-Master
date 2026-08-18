"""
Executive Summary Card displaying official Amazon Prime QC Verdict, Compliance Score, and Metadata Grid.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
)
from PySide6.QtCore import Qt
from ...core.constants import Severity
from ...core.utils import format_bytes, seconds_to_timecode
from ...engine.models import QCReportData


class SummaryCardWidget(QFrame):
    """Visual executive overview of QC results."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "CardFrame")
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        # 1. Top Verdict Banner
        self.banner_frame = QFrame()
        self.banner_frame.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        banner_layout = QHBoxLayout(self.banner_frame)
        banner_layout.setContentsMargins(12, 8, 12, 8)

        self.lbl_verdict_badge = QLabel("READY FOR INSPECTION")
        self.lbl_verdict_badge.setStyleSheet("font-size: 15px; font-weight: bold; color: #94a3b8;")

        self.lbl_score_badge = QLabel("Score: --")
        self.lbl_score_badge.setStyleSheet("font-size: 15px; font-weight: bold; color: #38bdf8;")

        banner_layout.addWidget(self.lbl_verdict_badge)
        banner_layout.addStretch()
        banner_layout.addWidget(self.lbl_score_badge)

        main_layout.addWidget(self.banner_frame)

        # 2. Issue Counters Row
        counters_layout = QHBoxLayout()
        counters_layout.setSpacing(10)

        self.lbl_cnt_fails = self._create_pill("0 ERRORS", "#dc2626", "#450a0a")
        self.lbl_cnt_warnings = self._create_pill("0 WARNINGS", "#d97706", "#451a03")
        self.lbl_cnt_notices = self._create_pill("0 NOTICES", "#0284c7", "#082f49")
        self.lbl_cnt_passes = self._create_pill("0 PASSED", "#059669", "#064e3b")

        counters_layout.addWidget(self.lbl_cnt_fails)
        counters_layout.addWidget(self.lbl_cnt_warnings)
        counters_layout.addWidget(self.lbl_cnt_notices)
        counters_layout.addWidget(self.lbl_cnt_passes)

        main_layout.addLayout(counters_layout)

        # 3. Technical Parameters Grid
        grid_frame = QFrame()
        grid_frame.setProperty("class", "SubCardFrame")
        grid_layout = QGridLayout(grid_frame)
        grid_layout.setContentsMargins(12, 12, 12, 12)
        grid_layout.setSpacing(10)

        self.val_file_name = self._add_grid_row(grid_layout, 0, 0, "File Name:", "--")
        self.val_file_size = self._add_grid_row(grid_layout, 0, 2, "File Size:", "--")
        self.val_duration = self._add_grid_row(grid_layout, 1, 0, "Duration:", "--")
        self.val_container = self._add_grid_row(grid_layout, 1, 2, "Container:", "--")
        self.val_codec = self._add_grid_row(grid_layout, 2, 0, "Video Codec:", "--")
        self.val_res_fps = self._add_grid_row(grid_layout, 2, 2, "Resolution / FPS:", "--")
        self.val_scan = self._add_grid_row(grid_layout, 3, 0, "Scan Type:", "--")
        self.val_color = self._add_grid_row(grid_layout, 3, 2, "Color Primaries:", "--")
        self.val_audio = self._add_grid_row(grid_layout, 4, 0, "Audio Channels:", "--")
        self.val_loudness = self._add_grid_row(grid_layout, 4, 2, "Integrated Loudness:", "--")

        main_layout.addWidget(grid_frame)

    def _create_pill(self, text: str, text_color: str, bg_color: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                font-weight: bold;
                font-size: 11px;
                padding: 6px 12px;
                border-radius: 4px;
                border: 1px solid {text_color};
            }}
        """)
        return lbl

    def _add_grid_row(self, layout: QGridLayout, row: int, col: int, label: str, default_val: str) -> QLabel:
        lbl_title = QLabel(label)
        lbl_title.setStyleSheet("color: #94a3b8; font-weight: 600; font-size: 12px;")
        lbl_val = QLabel(default_val)
        lbl_val.setStyleSheet("color: #f1f5f9; font-weight: 500; font-size: 12px;")
        layout.addWidget(lbl_title, row, col)
        layout.addWidget(lbl_val, row, col + 1)
        return lbl_val

    def update_report(self, report: QCReportData):
        """Updates summary view with new QC report data."""
        if report.verdict == Severity.PASS:
            self.lbl_verdict_badge.setText("PASSED - OFFICIAL AMAZON PRIME COMPLIANCE")
            self.lbl_verdict_badge.setStyleSheet("font-size: 15px; font-weight: bold; color: #34d399;")
            self.banner_frame.setStyleSheet("QFrame { background-color: #064e3b; border: 1px solid #059669; border-radius: 6px; }")
        elif report.verdict == Severity.WARNING:
            self.lbl_verdict_badge.setText("WARNING - REVIEW REQUIRED")
            self.lbl_verdict_badge.setStyleSheet("font-size: 15px; font-weight: bold; color: #fbbf24;")
            self.banner_frame.setStyleSheet("QFrame { background-color: #451a03; border: 1px solid #d97706; border-radius: 6px; }")
        else:
            self.lbl_verdict_badge.setText("FAILED - OUT OF SPECIFICATION")
            self.lbl_verdict_badge.setStyleSheet("font-size: 15px; font-weight: bold; color: #f87171;")
            self.banner_frame.setStyleSheet("QFrame { background-color: #450a0a; border: 1px solid #dc2626; border-radius: 6px; }")

        self.lbl_score_badge.setText(f"Score: {report.compliance_score:.1f}%")

        # Update counter pills
        self.lbl_cnt_fails.setText(f"{report.fail_count} ERRORS")
        self.lbl_cnt_warnings.setText(f"{report.warning_count} WARNINGS")
        self.lbl_cnt_notices.setText(f"{report.notice_count} NOTICES")
        self.lbl_cnt_passes.setText(f"{report.pass_count} PASSED")

        # Update grid values
        v_stream = report.video_streams[0] if report.video_streams else None
        fps = v_stream.fps if v_stream else 24.0

        self.val_file_name.setText(report.file_name)
        self.val_file_size.setText(format_bytes(report.file_size_bytes))
        self.val_duration.setText(f"{report.duration_sec:.2f}s ({seconds_to_timecode(report.duration_sec, fps)})")
        self.val_container.setText(report.container_info.get("format_name", "N/A").upper())

        if v_stream:
            self.val_codec.setText(f"{v_stream.codec_name} ({v_stream.profile})")
            self.val_res_fps.setText(f"{v_stream.width}x{v_stream.height} @ {v_stream.fps:.3f} fps")
            self.val_scan.setText(v_stream.field_order.capitalize())
            self.val_color.setText(v_stream.color_primaries.upper())
        else:
            self.val_codec.setText("No Video Stream")

        a_channels = sum(a.channels for a in report.audio_streams)
        self.val_audio.setText(f"{a_channels} Channels ({len(report.audio_streams)} track(s))")

        loud_i = report.loudness_data.get("integrated", -24.0)
        true_p = report.loudness_data.get("true_peak", -2.0)
        self.val_loudness.setText(f"{loud_i:.1f} LUFS | TP: {true_p:.2f} dBTP")
