"""
Video Frame Inspector Widget with Timecode Scrubbing and Jump-to-Issue support.
Extracts and renders high-quality preview frames using OpenCV / FFmpeg.
"""

import os
import cv2
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QImage, QPixmap
from ...core.utils import seconds_to_timecode, timecode_to_seconds


class VideoPreviewWidget(QFrame):
    """Inspects video frames at specific timecodes."""
    timecode_changed = Signal(str, float)  # (timecode, seconds)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "CardFrame")
        self.file_path = ""
        self.duration_sec = 0.0
        self.fps = 24.0
        self.cap = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Header
        top_row = QHBoxLayout()
        lbl_title = QLabel("<b>👁️ VIDEO FRAME INSPECTOR & TIMELINE SCRUBBER</b>")
        lbl_title.setStyleSheet("font-size: 13px; color: #38bdf8;")
        top_row.addWidget(lbl_title)
        top_row.addStretch()

        self.lbl_current_tc = QLabel("00:00:00:00")
        self.lbl_current_tc.setStyleSheet("font-family: monospace; font-size: 14px; font-weight: bold; color: #38bdf8; background: #0f172a; padding: 4px 8px; border-radius: 4px;")
        top_row.addWidget(self.lbl_current_tc)

        layout.addLayout(top_row)

        # Video Frame Display Canvas
        self.lbl_frame_canvas = QLabel()
        self.lbl_frame_canvas.setAlignment(Qt.AlignCenter)
        self.lbl_frame_canvas.setMinimumHeight(240)
        self.lbl_frame_canvas.setStyleSheet("""
            QLabel {
                background-color: #050811;
                border: 1px solid #1f2937;
                border-radius: 6px;
            }
        """)
        self.lbl_frame_canvas.setText("No video loaded for inspection")
        layout.addWidget(self.lbl_frame_canvas, 1)

        # Timeline Scrubber Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 1000)
        self.slider.setValue(0)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #1e293b;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #0284c7;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #38bdf8;
                width: 14px;
                margin-top: -4px;
                margin-bottom: -4px;
                border-radius: 7px;
            }
        """)
        self.slider.valueChanged.connect(self._on_slider_moved)
        layout.addWidget(self.slider)

        # Controls Row
        controls_row = QHBoxLayout()
        self.btn_start = QPushButton("⏮️ Head")
        self.btn_start.clicked.connect(lambda: self.seek_seconds(0.0))

        self.btn_prev_frame = QPushButton("◀ Step -1 Frame")
        self.btn_prev_frame.clicked.connect(self._step_back_frame)

        self.btn_next_frame = QPushButton("Step +1 Frame ▶")
        self.btn_next_frame.clicked.connect(self._step_fwd_frame)

        self.btn_end = QPushButton("Tail ⏭️")
        self.btn_end.clicked.connect(lambda: self.seek_seconds(max(0, self.duration_sec - 0.1)))

        controls_row.addWidget(self.btn_start)
        controls_row.addWidget(self.btn_prev_frame)
        controls_row.addWidget(self.btn_next_frame)
        controls_row.addWidget(self.btn_end)
        controls_row.addStretch()

        layout.addLayout(controls_row)

    def load_video(self, file_path: str, duration: float, fps: float = 24.0):
        """Loads video file for frame extraction."""
        self.file_path = file_path
        self.duration_sec = duration
        self.fps = max(1.0, fps)
        if self.cap:
            self.cap.release()

        try:
            self.cap = cv2.VideoCapture(file_path)
            self.seek_seconds(0.0)
        except Exception:
            pass

    def seek_seconds(self, sec: float):
        """Seeks to specific timestamp in seconds."""
        if not self.cap or self.duration_sec <= 0:
            return

        sec = max(0.0, min(self.duration_sec, sec))
        self.slider.blockSignals(True)
        pct = int((sec / self.duration_sec) * 1000)
        self.slider.setValue(pct)
        self.slider.blockSignals(False)

        tc_str = seconds_to_timecode(sec, self.fps)
        self.lbl_current_tc.setText(tc_str)

        # Seek in OpenCV
        try:
            self.cap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000.0)
            ret, frame = self.cap.read()
            if ret and frame is not None:
                self._render_frame(frame)
        except Exception:
            pass

    def seek_timecode(self, tc: str):
        """Seeks to specific SMPTE timecode."""
        sec = timecode_to_seconds(tc, self.fps)
        self.seek_seconds(sec)

    def _render_frame(self, frame_bgr):
        """Converts OpenCV BGR frame to QPixmap and displays it scaled."""
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pix = QPixmap.fromImage(q_img)
        scaled = pix.scaled(self.lbl_frame_canvas.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.lbl_frame_canvas.setPixmap(scaled)

    def _on_slider_moved(self, val: int):
        if self.duration_sec > 0:
            sec = (val / 1000.0) * self.duration_sec
            self.seek_seconds(sec)

    def _step_back_frame(self):
        current_sec = timecode_to_seconds(self.lbl_current_tc.text(), self.fps)
        self.seek_seconds(max(0.0, current_sec - (1.0 / self.fps)))

    def _step_fwd_frame(self):
        current_sec = timecode_to_seconds(self.lbl_current_tc.text(), self.fps)
        self.seek_seconds(min(self.duration_sec, current_sec + (1.0 / self.fps)))
