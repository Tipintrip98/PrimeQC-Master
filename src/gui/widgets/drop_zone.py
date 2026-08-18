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
        self.setProperty("class", "CardFrame")
        self.video_path = ""
        self.subtitle_path = ""
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        # Drop Area Frame
        self.drop_box = QFrame()
        self.drop_box.setStyleSheet("""
            QFrame {
                border: 2px dashed #0284c7;
                border-radius: 8px;
                background-color: #0d1527;
                min-height: 48px;
                padding: 6px;
            }
            QFrame:hover {
                background-color: #13223f;
                border-color: #38bdf8;
            }
        """)
        drop_layout = QHBoxLayout(self.drop_box)
        drop_layout.setContentsMargins(10, 4, 10, 4)
        drop_layout.setSpacing(10)

        self.lbl_icon = QLabel("📥")
        self.lbl_icon.setStyleSheet("font-size: 22px; background: transparent;")

        self.lbl_prompt = QLabel("<b>Trascina Master Video (.mov, .mp4, .mxf, .ts)</b>")
        self.lbl_prompt.setStyleSheet("font-size: 12px; color: #f8fafc; background: transparent;")

        self.btn_select_video = QPushButton("📂 Sfoglia...")
        self.btn_select_video.setStyleSheet("background-color: #1e293b; color: #f8fafc; border: 1px solid #334155; border-radius: 4px; padding: 4px 10px; font-size: 11px;")
        self.btn_select_video.clicked.connect(self._browse_video)

        self.btn_select_sub = QPushButton("🔤 Sottotitoli...")
        self.btn_select_sub.setStyleSheet("background-color: #1e293b; color: #f8fafc; border: 1px solid #334155; border-radius: 4px; padding: 4px 10px; font-size: 11px;")
        self.btn_select_sub.clicked.connect(self._browse_subtitle)

        self.lbl_selected_file = QLabel("Nessun file selezionato")
        self.lbl_selected_file.setStyleSheet("color: #64748b; font-style: italic; font-size: 11px; background: transparent;")

        drop_layout.addWidget(self.lbl_icon)
        drop_layout.addWidget(self.lbl_prompt)
        drop_layout.addWidget(self.btn_select_video)
        drop_layout.addWidget(self.btn_select_sub)
        drop_layout.addWidget(self.lbl_selected_file, 1)

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
        self.lbl_selected_file.setText("Nessun file selezionato")
        self.lbl_selected_file.setStyleSheet("color: #64748b; font-style: italic; font-size: 11px; background: transparent;")

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
            "Seleziona Master Video per QC Amazon Prime",
            "",
            "Video Master (*.mov *.mp4 *.mxf *.ts *.m2ts *.mkv);;Tutti i File (*.*)"
        )
        if file_path:
            self.video_path = file_path
            self._update_display()

    def _browse_subtitle(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleziona File Sottotitoli Sidecar",
            "",
            "Sottotitoli (*.srt *.vtt *.ttml *.dfxp *.scc);;Tutti i File (*.*)"
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
            self.file_selected.emit(self.video_path, self.subtitle_path)
            self.sig_file_selected.emit(self.video_path)
