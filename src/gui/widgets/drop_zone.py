"""
Drag-and-Drop Ingestion Widget for Video and Subtitle files.
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent


class DropZoneWidget(QFrame):
    """File ingestion area supporting drag and drop and file dialogs."""
    file_selected = Signal(str, str)  # (video_path, subtitle_path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setProperty("class", "CardFrame")
        self.video_path = ""
        self.subtitle_path = ""
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Drop Area Frame
        self.drop_box = QFrame()
        self.drop_box.setStyleSheet("""
            QFrame {
                border: 2px dashed #0284c7;
                border-radius: 8px;
                background-color: #0d1527;
                min-height: 120px;
            }
            QFrame:hover {
                background-color: #13223f;
                border-color: #38bdf8;
            }
        """)
        drop_layout = QVBoxLayout(self.drop_box)
        drop_layout.setAlignment(Qt.AlignCenter)
        drop_layout.setSpacing(8)

        self.lbl_icon = QLabel("📥")
        self.lbl_icon.setStyleSheet("font-size: 32px; background: transparent;")
        self.lbl_icon.setAlignment(Qt.AlignCenter)

        self.lbl_prompt = QLabel("<b>DRAG & DROP MASTER VIDEO FILE HERE</b>")
        self.lbl_prompt.setStyleSheet("font-size: 14px; color: #f8fafc; background: transparent;")
        self.lbl_prompt.setAlignment(Qt.AlignCenter)

        self.lbl_formats = QLabel("Supported: Apple ProRes (.mov), H.264/HEVC (.mp4), MXF (IMF/OP1a), MPEG-2 (.ts)")
        self.lbl_formats.setStyleSheet("font-size: 11px; color: #94a3b8; background: transparent;")
        self.lbl_formats.setAlignment(Qt.AlignCenter)

        drop_layout.addWidget(self.lbl_icon)
        drop_layout.addWidget(self.lbl_prompt)
        drop_layout.addWidget(self.lbl_formats)

        layout.addWidget(self.drop_box)

        # File Selection Actions Row
        actions_row = QHBoxLayout()
        actions_row.setSpacing(10)

        self.btn_select_video = QPushButton("Browse Video Master...")
        self.btn_select_video.setObjectName("PrimaryButton")
        self.btn_select_video.clicked.connect(self._browse_video)

        self.btn_select_sub = QPushButton("Attach Subtitles (.srt, .vtt, .ttml)...")
        self.btn_select_sub.clicked.connect(self._browse_subtitle)

        self.lbl_selected_file = QLabel("No file selected")
        self.lbl_selected_file.setStyleSheet("color: #64748b; font-style: italic;")

        actions_row.addWidget(self.btn_select_video)
        actions_row.addWidget(self.btn_select_sub)
        actions_row.addWidget(self.lbl_selected_file, 1)

        layout.addLayout(actions_row)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            for url in urls:
                path = url.toLocalFile()
                if os.path.isfile(path):
                    ext = os.path.splitext(path)[1].lower()
                    if ext in [".mov", ".mp4", ".mxf", ".ts", ".m2ts", ".mkv", ".avi"]:
                        self.video_path = path
                    elif ext in [".srt", ".vtt", ".ttml", ".dfxp", ".scc"]:
                        self.subtitle_path = path
            self._update_display()

    def _browse_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Master Video for Amazon Prime QC",
            "",
            "Video Files (*.mov *.mp4 *.mxf *.ts *.m2ts);;All Files (*.*)"
        )
        if file_path:
            self.video_path = file_path
            self._update_display()

    def _browse_subtitle(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Subtitle / Timed Text Sidecar",
            "",
            "Subtitle Files (*.srt *.vtt *.ttml *.dfxp *.scc);;All Files (*.*)"
        )
        if file_path:
            self.subtitle_path = file_path
            self._update_display()

    def _update_display(self):
        if self.video_path:
            base = os.path.basename(self.video_path)
            sub_text = f" + Sub: {os.path.basename(self.subtitle_path)}" if self.subtitle_path else ""
            self.lbl_selected_file.setText(f"✓ {base}{sub_text}")
            self.lbl_selected_file.setStyleSheet("color: #38bdf8; font-weight: bold;")
            self.file_selected.emit(self.video_path, self.subtitle_path)
