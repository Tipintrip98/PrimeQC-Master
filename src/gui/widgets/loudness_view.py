from typing import Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QFrame, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush


class PhaseGaugeWidget(QWidget):
    """Custom painted phase correlation meter (-1.0 to +1.0)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(46)
        self.phase_val = 0.85

    def set_phase(self, val: float):
        self.phase_val = max(-1.0, min(1.0, val))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # Background track
        painter.setBrush(QBrush(QColor("#090d16")))
        painter.setPen(QPen(QColor("#1e293b"), 1))
        painter.drawRoundedRect(10, 12, w - 20, 18, 5, 5)

        # Center line (0.0)
        center_x = w / 2.0

        # Safe in-phase zone (> 0.0)
        painter.setBrush(QBrush(QColor("#064e3b")))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(int(center_x), 13, int(center_x - 11), 16, 0, 4)

        # Danger anti-phase zone (< 0.0)
        painter.setBrush(QBrush(QColor("#450a0a")))
        painter.drawRoundedRect(11, 13, int(center_x - 11), 16, 4, 0)

        # Zero center reference line
        painter.setPen(QPen(QColor("#94a3b8"), 1, Qt.SolidLine))
        painter.drawLine(int(center_x), 8, int(center_x), 34)

        # Value needle/pill
        val_x = center_x + (self.phase_val * (center_x - 15))
        marker_color = QColor("#10b981") if self.phase_val >= 0.2 else (QColor("#f59e0b") if self.phase_val >= 0.0 else QColor("#ef4444"))
        painter.setBrush(QBrush(marker_color))
        painter.setPen(QPen(QColor("#ffffff"), 1.5))
        painter.drawRoundedRect(int(val_x - 5), 8, 10, 26, 3, 3)

        # Labels
        painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
        painter.setPen(QColor("#ef4444"))
        painter.drawText(12, 42, "-1.0 (Out of Phase)")
        painter.setPen(QColor("#94a3b8"))
        painter.drawText(int(center_x - 8), 42, "0.0")
        painter.setPen(QColor("#10b981"))
        painter.drawText(w - 115, 42, "+1.0 (Mono Safe)")


class LoudnessViewWidget(QFrame):
    """Loudness parameters, radar, and True Peak level meters."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # Title
        title_row = QHBoxLayout()
        lbl_title = QLabel("<b>🔊 ITU-R BS.1770-4 / EBU R128 LOUDNESS & PHASE METERING</b>")
        lbl_title.setStyleSheet("font-size: 13px; font-weight: 800; color: #38bdf8; letter-spacing: 0.5px;")
        title_row.addWidget(lbl_title)
        title_row.addStretch()

        lbl_std = QLabel("<span style='background: #1e3a5f; color: #38bdf8; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: bold;'>AMAZON PRIME TARGET: -24 LKFS (±1.0)</span>")
        title_row.addWidget(lbl_std)
        layout.addLayout(title_row)

        # Loudness Metrics Grid
        grid_frame = QFrame()
        grid_frame.setStyleSheet("""
            QFrame {
                background-color: #0c121e;
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 14px;
            }
        """)
        grid_layout = QGridLayout(grid_frame)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        grid_layout.setSpacing(14)

        # 1. Integrated Loudness
        self.lbl_int_val = QLabel("-24.0 LUFS")
        self.lbl_int_val.setStyleSheet("font-size: 16px; font-weight: 800; color: #34d399;")
        self.bar_int = self._create_bar()

        # 2. True Peak
        self.lbl_tp_val = QLabel("-2.00 dBTP")
        self.lbl_tp_val.setStyleSheet("font-size: 16px; font-weight: 800; color: #34d399;")
        self.bar_tp = self._create_bar()

        # 3. Loudness Range (LRA)
        self.lbl_lra_val = QLabel("8.0 LU")
        self.lbl_lra_val.setStyleSheet("font-size: 16px; font-weight: 800; color: #38bdf8;")
        self.bar_lra = self._create_bar()

        grid_layout.addWidget(QLabel("<b style='color: #f8fafc;'>Integrated Loudness:</b><br><span style='color: #64748b; font-size: 11px;'>Target: -24.0 LKFS (±1.0 LU)</span>"), 0, 0)
        grid_layout.addWidget(self.lbl_int_val, 0, 1)
        grid_layout.addWidget(self.bar_int, 0, 2)

        grid_layout.addWidget(QLabel("<b style='color: #f8fafc;'>Max True Peak (dBTP):</b><br><span style='color: #64748b; font-size: 11px;'>Ceiling Limit: ≤ -2.0 dBTP</span>"), 1, 0)
        grid_layout.addWidget(self.lbl_tp_val, 1, 1)
        grid_layout.addWidget(self.bar_tp, 1, 2)

        grid_layout.addWidget(QLabel("<b style='color: #f8fafc;'>Loudness Range (LRA):</b><br><span style='color: #64748b; font-size: 11px;'>Recommended: ≤ 14.0 LU</span>"), 2, 0)
        grid_layout.addWidget(self.lbl_lra_val, 2, 1)
        grid_layout.addWidget(self.bar_lra, 2, 2)

        layout.addWidget(grid_frame)

        # Phase Correlation Section
        phase_frame = QFrame()
        phase_frame.setStyleSheet("""
            QFrame {
                background-color: #0c121e;
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 14px;
            }
        """)
        phase_layout = QVBoxLayout(phase_frame)
        phase_layout.setContentsMargins(10, 10, 10, 10)
        phase_layout.setSpacing(8)

        phase_title_row = QHBoxLayout()
        phase_title_row.addWidget(QLabel("<b style='color: #f8fafc;'>Inter-Channel Stereo Phase Correlation:</b>"))
        self.lbl_phase_val = QLabel("+0.85 (Mono Safe)")
        self.lbl_phase_val.setStyleSheet("color: #34d399; font-weight: bold; font-size: 13px;")
        phase_title_row.addStretch()
        phase_title_row.addWidget(self.lbl_phase_val)
        phase_layout.addLayout(phase_title_row)

        self.phase_gauge = PhaseGaugeWidget()
        phase_layout.addWidget(self.phase_gauge)

        layout.addWidget(phase_frame)
        layout.addStretch()

    def _create_bar(self) -> QProgressBar:
        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(50)
        bar.setTextVisible(False)
        bar.setFixedHeight(14)
        bar.setStyleSheet("""
            QProgressBar {
                background-color: #080c14;
                border: 1px solid #1e293b;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #10b981;
                border-radius: 3px;
            }
        """)
        return bar

    def update_loudness(self, loudness_data: dict = None, phase_data: Any = None):
        """Updates meters with analysis data."""
        if not loudness_data or not isinstance(loudness_data, dict):
            # Reset gauges
            self.lbl_int_val.setText("-24.0 LUFS")
            self.bar_int.setValue(40)
            self.lbl_tp_val.setText("-2.00 dBTP")
            self.bar_tp.setValue(90)
            self.lbl_lra_val.setText("8.0 LU")
            self.bar_lra.setValue(32)
            self.phase_gauge.set_phase(0.85)
            self.lbl_phase_val.setText("+0.85 (Mono Safe)")
            return

        int_lufs = float(loudness_data.get("integrated", -24.0))
        tp = float(loudness_data.get("true_peak", -2.0))
        lra = float(loudness_data.get("lra", 8.0))

        # Update Integrated
        self.lbl_int_val.setText(f"{int_lufs:.1f} LUFS")
        int_pct = int(max(0, min(100, (int_lufs + 40) * 2.5)))
        self.bar_int.setValue(int_pct)
        if abs(int_lufs - (-24.0)) <= 1.0:
            self.lbl_int_val.setStyleSheet("font-size: 16px; font-weight: 800; color: #34d399;")
            self.bar_int.setStyleSheet("QProgressBar::chunk { background-color: #10b981; }")
        elif abs(int_lufs - (-24.0)) <= 2.0:
            self.lbl_int_val.setStyleSheet("font-size: 16px; font-weight: 800; color: #fbbf24;")
            self.bar_int.setStyleSheet("QProgressBar::chunk { background-color: #f59e0b; }")
        else:
            self.lbl_int_val.setStyleSheet("font-size: 16px; font-weight: 800; color: #f87171;")
            self.bar_int.setStyleSheet("QProgressBar::chunk { background-color: #ef4444; }")

        # Update True Peak
        self.lbl_tp_val.setText(f"{tp:.2f} dBTP")
        tp_pct = int(max(0, min(100, (tp + 20) * 5.0)))
        self.bar_tp.setValue(tp_pct)
        if tp <= -2.0:
            self.lbl_tp_val.setStyleSheet("font-size: 16px; font-weight: 800; color: #34d399;")
            self.bar_tp.setStyleSheet("QProgressBar::chunk { background-color: #10b981; }")
        else:
            self.lbl_tp_val.setStyleSheet("font-size: 16px; font-weight: 800; color: #f87171;")
            self.bar_tp.setStyleSheet("QProgressBar::chunk { background-color: #ef4444; }")

        # Update LRA
        self.lbl_lra_val.setText(f"{lra:.1f} LU")
        lra_pct = int(max(0, min(100, lra * 4.0)))
        self.bar_lra.setValue(lra_pct)

        # Update Phase
        if isinstance(phase_data, dict):
            mean_p = float(phase_data.get("mean_phase", 0.85))
        elif isinstance(phase_data, (int, float)):
            mean_p = float(phase_data)
        elif isinstance(phase_data, list) and len(phase_data) > 0 and isinstance(phase_data[0], dict):
            mean_p = float(phase_data[0].get("mean_phase", 0.85))
        else:
            mean_p = 0.85

        self.phase_gauge.set_phase(mean_p)
        if mean_p >= 0.2:
            self.lbl_phase_val.setText(f"{mean_p:+.2f} (Mono Safe)")
            self.lbl_phase_val.setStyleSheet("color: #34d399; font-weight: bold; font-size: 13px;")
        elif mean_p >= 0.0:
            self.lbl_phase_val.setText(f"{mean_p:+.2f} (Wide Stereo)")
            self.lbl_phase_val.setStyleSheet("color: #fbbf24; font-weight: bold; font-size: 13px;")
        else:
            self.lbl_phase_val.setText(f"{mean_p:+.2f} (Anti-Phase Risk)")
            self.lbl_phase_val.setStyleSheet("color: #f87171; font-weight: bold; font-size: 13px;")


