"""
Profile Manager Dialog for viewing and configuring Amazon Prime Delivery standards.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QFrame,
    QGridLayout, QDoubleSpinBox, QCheckBox, QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt
from ...core.constants import PRIME_PROFILES, ProfileType
from ...core.config import AppConfig


class ProfileManagerDialog(QDialog):
    """Allows inspection and customization of Amazon Prime delivery standards."""

    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Amazon Prime Delivery Profiles & Tolerances")
        self.setMinimumSize(600, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #0f172a;
                color: #e2e8f0;
            }
        """)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # Profile Selector
        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("<b>Active QC Profile:</b>"))
        self.cb_profile = QComboBox()
        for p_name in self.config.get_all_profiles().keys():
            self.cb_profile.addItem(p_name)
        self.cb_profile.currentTextChanged.connect(self._load_profile_data)
        top_row.addWidget(self.cb_profile, 1)
        layout.addLayout(top_row)

        self.lbl_desc = QLabel()
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet("color: #94a3b8; font-style: italic; font-size: 11px;")
        layout.addWidget(self.lbl_desc)

        # Settings Card
        card = QFrame()
        card.setStyleSheet("background-color: #1e293b; border-radius: 6px; padding: 12px;")
        grid = QGridLayout(card)
        grid.setSpacing(10)

        # Loudness
        grid.addWidget(QLabel("Target Loudness (LKFS/LUFS):"), 0, 0)
        self.sp_target_lufs = QDoubleSpinBox()
        self.sp_target_lufs.setRange(-40.0, 0.0)
        self.sp_target_lufs.setSingleStep(0.5)
        self.sp_target_lufs.setValue(-24.0)
        grid.addWidget(self.sp_target_lufs, 0, 1)

        grid.addWidget(QLabel("Loudness Tolerance (±LU):"), 1, 0)
        self.sp_tol_lu = QDoubleSpinBox()
        self.sp_tol_lu.setRange(0.1, 5.0)
        self.sp_tol_lu.setSingleStep(0.5)
        self.sp_tol_lu.setValue(1.0)
        grid.addWidget(self.sp_tol_lu, 1, 1)

        # True Peak
        grid.addWidget(QLabel("Max True Peak Ceiling (dBTP):"), 2, 0)
        self.sp_true_peak = QDoubleSpinBox()
        self.sp_true_peak.setRange(-10.0, 0.0)
        self.sp_true_peak.setSingleStep(0.5)
        self.sp_true_peak.setValue(-2.0)
        grid.addWidget(self.sp_true_peak, 2, 1)

        # Max Leading Black
        grid.addWidget(QLabel("Max Leading Black (sec):"), 3, 0)
        self.sp_lead_black = QDoubleSpinBox()
        self.sp_lead_black.setRange(0.0, 10.0)
        self.sp_lead_black.setSingleStep(0.5)
        self.sp_lead_black.setValue(2.0)
        grid.addWidget(self.sp_lead_black, 3, 1)

        layout.addWidget(card)

        # Codecs and Formats Summary
        self.txt_summary = QTextEdit()
        self.txt_summary.setReadOnly(True)
        self.txt_summary.setStyleSheet("background-color: #0b0f19; border: 1px solid #1f2937; color: #cbd5e1; font-size: 11px;")
        layout.addWidget(self.txt_summary, 1)

        # Buttons
        btn_box = QHBoxLayout()
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.accept)
        btn_box.addStretch()
        btn_box.addWidget(self.btn_close)
        layout.addLayout(btn_box)

        # Initial load
        self._load_profile_data(self.cb_profile.currentText())

    def _load_profile_data(self, profile_name: str):
        profile = self.config.get_profile(profile_name)
        self.lbl_desc.setText(profile.get("description", ""))
        self.sp_target_lufs.setValue(profile.get("loudness_target_lufs", -24.0))
        self.sp_tol_lu.setValue(profile.get("loudness_tolerance_lu", 1.0))
        self.sp_true_peak.setValue(profile.get("true_peak_max_dbtp", -2.0))
        self.sp_lead_black.setValue(profile.get("max_leading_black_sec", 2.0))

        containers = ", ".join(profile.get("allowed_containers", []))
        codecs = ", ".join(profile.get("allowed_video_codecs", []))
        res = ", ".join([f"{w}x{h}" for w, h in profile.get("allowed_resolutions", [])])
        channels = ", ".join([str(c) for c in profile.get("allowed_audio_channels", [])])

        summary_text = f"""<b>Container Formats:</b> {containers}<br/>
<b>Allowed Video Codecs:</b> {codecs}<br/>
<b>Scan Type:</b> Strict Progressive (Interlaced/Telecine strictly rejected)<br/>
<b>Standard Resolutions:</b> {res}<br/>
<b>Audio Sample Rate:</b> 48000 Hz (48 kHz) Strict<br/>
<b>Audio Channel Configurations:</b> {channels} channels (Stereo / 5.1 / 8-Ch)<br/>
<b>Loudness Specification:</b> ITU-R BS.1770-4 / EBU R128 (-24.0 LKFS ± {profile.get('loudness_tolerance_lu', 1.0)} LU)<br/>
<b>True Peak Ceiling:</b> <= {profile.get('true_peak_max_dbtp', -2.0)} dBTP<br/>
<b>Clean Master Requirement:</b> No test bars, no audio tone, no countdown slates.
"""
        self.txt_summary.setHtml(summary_text)
