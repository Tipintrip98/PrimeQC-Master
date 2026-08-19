"""
Drag-and-Drop Ingestion Widget for Video and Subtitle files.
Supports both drag & drop and manual file selection with status updates.
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
    sig_file_selected = Signal(str)    # (video_path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.video_path = ""
        self.subtitle_path = ""
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Drop Area Frame
        self.drop_box = QFrame()
        self.drop_box.setObjectName("DropFrame")
        self.drop_box.setStyleSheet("""
            QFrame#DropFrame {
                border: 2px dashed #0284c7;
                border-radius: 8px;
                background-color: #0d1527;
                min-height: 48px;
                padding: 4px 12px;
            }
            QFrame#DropFrame:hover {
                background-color: #13223f;
                border-color: #38bdf8;
            }
        """)
        drop_layout = QHBoxLayout(self.drop_box)
        drop_layout.setContentsMargins(8, 4, 8, 4)
        drop_layout.setSpacing(10)

        self.lbl_icon = QLabel("🎬")
        self.lbl_icon.setStyleSheet("font-size: 20px; background: transparent;")

        self.lbl_prompt = QLabel("<b>Drop Master Media</b> <span style='color: #64748b;'>(ProRes / AVC / MXF / MOV / MP4)</span>")
        self.lbl_prompt.setStyleSheet("font-size: 12px; color: #f8fafc; background: transparent;")

        self.btn_select_video = QPushButton("📂 Browse...")
        self.btn_select_video.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                color: #f8fafc;
                border: 1px solid #334155;
                border-radius: 5px;
                padding: 5px 12px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0284c7;
                border-color: #38bdf8;
            }
        """)
        self.btn_select_video.clicked.connect(self._browse_video)

        self.btn_select_sub = QPushButton("🔤 Subtitle...")
        self.btn_select_sub.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                color: #cbd5e1;
                border: 1px solid #334155;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #334155;
                color: #38bdf8;
            }
        """)
        self.btn_select_sub.clicked.connect(self._browse_subtitle)

        self.lbl_selected_file = QLabel("No file loaded")
        self.lbl_selected_file.setStyleSheet("color: #64748b; font-style: italic; font-size: 11px; background: transparent;")

        self.btn_clear = QPushButton("✕")
        self.btn_clear.setToolTip("Clear loaded files")
        self.btn_clear.setFixedSize(22, 22)
        self.btn_clear.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #64748b;
                border: none;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #ef4444;
                background-color: #1f2937;
                border-radius: 11px;
            }
        """)
        self.btn_clear.clicked.connect(self.clear)
        self.btn_clear.hide()

        drop_layout.addWidget(self.lbl_icon)
        drop_layout.addWidget(self.lbl_prompt)
        drop_layout.addWidget(self.btn_select_video)
        drop_layout.addWidget(self.btn_select_sub)
        drop_layout.addWidget(self.lbl_selected_file, 1)
        drop_layout.addWidget(self.btn_clear)

        layout.addWidget(self.drop_box)

    def set_media_file(self, path: str):
        """Sets active master video file."""
        if path and os.path.isfile(path):
            self.video_path = path
            self._update_display()

    def set_subtitle_file(self, path: str):
        """Sets sidecar subtitle file."""
        if path and os.path.isfile(path):
            self.subtitle_path = path
            self._update_display()

    def get_media_path(self) -> str:
        return self.video_path

    def get_subtitle_path(self) -> str:
        return self.subtitle_path

    def clear(self):
        self.video_path = ""
        self.subtitle_path = ""
        self.lbl_selected_file.setText("No file loaded")
        self.lbl_selected_file.setStyleSheet("color: #64748b; font-style: italic; font-size: 11px; background: transparent;")
        self.btn_clear.hide()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.drop_box.setStyleSheet("""
                QFrame#DropFrame {
                    border: 2px solid #38bdf8;
                    border-radius: 8px;
                    background-color: #1e3a5f;
                    min-height: 48px;
                    padding: 4px 12px;
                }
            """)

    def dragLeaveEvent(self, event):
        self.drop_box.setStyleSheet("""
            QFrame#DropFrame {
                border: 2px dashed #0284c7;
                border-radius: 8px;
                background-color: #0d1527;
                min-height: 48px;
                padding: 4px 12px;
            }
            QFrame#DropFrame:hover {
                background-color: #13223f;
                border-color: #38bdf8;
            }
        """)

    def dropEvent(self, event: QDropEvent):
        self.dragLeaveEvent(None)
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
            "Select Master Media File for Amazon Prime QC",
            "",
            "Video Master (*.mov *.mp4 *.mxf *.ts *.m2ts *.mkv);;All Files (*.*)"
        )
        if file_path:
            self.video_path = file_path
            self._update_display()

    def _browse_subtitle(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Sidecar Subtitle / Timed Text File",
            "",
            "Subtitles (*.srt *.vtt *.ttml *.dfxp *.scc);;All Files (*.*)"
        )
        if file_path:
            self.subtitle_path = file_path
            self._update_display()

    def _update_display(self):
        if self.video_path:
            base = os.path.basename(self.video_path)
            sub_text = f" + [Sub: {os.path.basename(self.subtitle_path)}]" if self.subtitle_path else ""
            self.lbl_selected_file.setText(f"✓ {base}{sub_text}")
            self.lbl_selected_file.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 11px; background: transparent;")
            self.btn_clear.show()
            self.file_selected.emit(self.video_path, self.subtitle_path)
            self.sig_file_selected.emit(self.video_path)

