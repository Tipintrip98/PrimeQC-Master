"""
About Dialog for PrimeQC Master.
Displays Developer, Version, Release Date, Architecture, and Licensing info.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont
import os


class AboutDialog(QDialog):
    """About dialog with developer, version, release date, and tech stack details."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Informazioni su PrimeQC Master")
        self.setFixedSize(540, 480)
        self.setStyleSheet("""
            QDialog {
                background-color: #0b0f19;
                color: #e2e8f0;
                font-family: 'Segoe UI', sans-serif;
            }
            QFrame#Card {
                background-color: #111827;
                border: 1px solid #1f2937;
                border-radius: 8px;
                padding: 16px;
            }
            QPushButton {
                background-color: #0284c7;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0369a1;
            }
        """)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        card = QFrame()
        card.setObjectName("Card")
        c_layout = QVBoxLayout(card)
        c_layout.setSpacing(12)

        # App Icon & Title Header
        header_row = QHBoxLayout()
        header_row.setSpacing(14)

        lbl_icon = QLabel("🛡️")
        lbl_icon.setStyleSheet("font-size: 38px; background: transparent;")
        lbl_icon.setAlignment(Qt.AlignCenter)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        lbl_title = QLabel("PRIME<b>QC</b> MASTER")
        lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff; letter-spacing: 0.5px;")

        lbl_sub = QLabel("Amazon Prime Video Quality Control Suite")
        lbl_sub.setStyleSheet("font-size: 12px; font-weight: 600; color: #38bdf8;")

        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)

        header_row.addWidget(lbl_icon)
        header_row.addLayout(title_box)
        header_row.addStretch()

        c_layout.addLayout(header_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #1f2937; max-height: 1px;")
        c_layout.addWidget(sep)

        # Meta Information Grid
        info_html = """
        <table style='width: 100%; border-collapse: collapse; font-size: 12px; line-height: 1.6;'>
            <tr>
                <td style='color: #94a3b8; width: 140px; padding: 4px 0;'><b>👤 Sviluppatore:</b></td>
                <td style='color: #f1f5f9;'><b>DECA VFX / Advanced Engineering Team</b></td>
            </tr>
            <tr>
                <td style='color: #94a3b8; padding: 4px 0;'><b>📦 Versione:</b></td>
                <td style='color: #38bdf8;'><b>v2.5 (Broadcast Production Release)</b></td>
            </tr>
            <tr>
                <td style='color: #94a3b8; padding: 4px 0;'><b>📅 Data di Rilascio:</b></td>
                <td style='color: #f1f5f9;'>18 Agosto 2026</td>
            </tr>
            <tr>
                <td style='color: #94a3b8; padding: 4px 0;'><b>🎯 Standard Target:</b></td>
                <td style='color: #f1f5f9;'>Amazon Prime Video Direct & Amazon Studios</td>
            </tr>
            <tr>
                <td style='color: #94a3b8; padding: 4px 0;'><b>🔊 Motore Audio:</b></td>
                <td style='color: #f1f5f9;'>ITU-R BS.1770-4 / EBU R128 (-24 LKFS / -2 dBTP)</td>
            </tr>
            <tr>
                <td style='color: #94a3b8; padding: 4px 0;'><b>🎞️ Motore Video:</b></td>
                <td style='color: #f1f5f9;'>FFmpeg 7.1 / ProRes 422 HQ / SignalStats / YADIF</td>
            </tr>
            <tr>
                <td style='color: #94a3b8; padding: 4px 0;'><b>🖥️ Framework GUI:</b></td>
                <td style='color: #f1f5f9;'>PySide6 (Qt 6.11) High-DPI Desktop Native</td>
            </tr>
            <tr>
                <td style='color: #94a3b8; padding: 4px 0;'><b>📄 Reportistica:</b></td>
                <td style='color: #f1f5f9;'>ReportLab Vector PDF & JSON Manifest</td>
            </tr>
        </table>
        """
        lbl_info = QLabel(info_html)
        lbl_info.setTextFormat(Qt.RichText)
        c_layout.addWidget(lbl_info)

        c_layout.addWidget(sep)

        lbl_desc = QLabel(
            "Software sviluppato per garantire la totale conformità dei master audio e video alle "
            "rigide linee guida di ingestione di Amazon Prime Video, con margine di errore nullo."
        )
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("color: #94a3b8; font-size: 11px; line-height: 1.4;")
        c_layout.addWidget(lbl_desc)

        layout.addWidget(card)

        # Bottom Close Button
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        btn_close = QPushButton("Chiudi")
        btn_close.clicked.connect(self.accept)
        btn_box.addWidget(btn_close)
        layout.addLayout(btn_box)
