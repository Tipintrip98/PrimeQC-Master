"""
Multi-tool Utility Suite for PrimeQC:
- Automated Loudness Conformer (-24 LUFS / -2 dBTP)
- ProRes 422 HQ Transcoder & Deinterlacer
- Amazon Bitrate & Storage Calculator
- EBU / SMPTE Test Pattern & 1kHz -24 LKFS Tone Generator
"""

import os
import subprocess
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget,
    QLineEdit, QFileDialog, QProgressBar, QFrame, QSpinBox, QDoubleSpinBox,
    QComboBox, QMessageBox, QGridLayout
)

from PySide6.QtCore import Qt, QThread, Signal
from ...core.utils import get_binary_path, format_bytes, format_bitrate


class UtilityWorker(QThread):
    sig_progress = Signal(int, str)
    sig_done = Signal(bool, str)

    def __init__(self, cmd: list, output_file: str):
        super().__init__()
        self.cmd = cmd
        self.output_file = output_file

    def run(self):
        try:
            self.sig_progress.emit(10, "Avvio elaborazione FFmpeg...")
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            proc = subprocess.Popen(
                self.cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='ignore',
                startupinfo=startupinfo
            )

            # Wait for completion
            _, stderr = proc.communicate()
            if proc.returncode == 0:
                self.sig_progress.emit(100, "Elaborazione completata con successo!")
                self.sig_done.emit(True, f"File generato:\n{self.output_file}")
            else:
                self.sig_done.emit(False, f"Errore durante l'elaborazione:\n{stderr[-400:]}")
        except Exception as e:
            self.sig_done.emit(False, str(e))


class UtilitiesDialog(QDialog):
    """Utilities toolbox dialog."""

    def __init__(self, parent=None, initial_file: str = ""):
        super().__init__(parent)
        self.initial_file = initial_file
        self.ffmpeg_bin = get_binary_path("ffmpeg")
        self.worker = None

        self.setWindowTitle("Strumenti & Utility PrimeQC per Amazon Prime Video")
        self.resize(680, 520)
        self.setStyleSheet("""
            QDialog {
                background-color: #0b0f19;
                color: #e2e8f0;
                font-family: 'Segoe UI', sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #1f2937;
                background-color: #111827;
                border-radius: 6px;
            }
            QTabBar::tab {
                background-color: #0b0f19;
                color: #94a3b8;
                padding: 8px 16px;
                font-weight: 600;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: #111827;
                color: #38bdf8;
                border-bottom: 2px solid #38bdf8;
            }
            QFrame.CardFrame {
                background-color: #111827;
                border: 1px solid #1f2937;
                border-radius: 6px;
                padding: 12px;
            }
            QPushButton {
                background-color: #1e293b;
                color: #f8fafc;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #334155;
            }
            QPushButton#PrimaryButton {
                background-color: #0284c7;
                color: #ffffff;
                border: none;
            }
            QPushButton#PrimaryButton:hover {
                background-color: #0369a1;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #0d1527;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 5px 10px;
                color: #f8fafc;
            }
            QProgressBar {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 4px;
                text-align: center;
                color: #ffffff;
                height: 16px;
            }
            QProgressBar::chunk {
                background-color: #0284c7;
            }
        """)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(12)

        self.tabs = QTabWidget()

        # Tab 1: Loudness Conformer
        self.tabs.addTab(self._create_loudness_tab(), "🎚️ Correttore Loudness (-24 LKFS)")

        # Tab 2: ProRes Transcoder
        self.tabs.addTab(self._create_prores_tab(), "🎞️ Transcoder ProRes 422 HQ")

        # Tab 3: Bitrate Calculator
        self.tabs.addTab(self._create_calc_tab(), "📏 Calcolatore Spazio & Bitrate")

        # Tab 4: Test Pattern Generator
        self.tabs.addTab(self._create_pattern_tab(), "🎨 Generatore Test Pattern")

        main_layout.addWidget(self.tabs, 1)

        # Bottom Progress & Close
        bottom_box = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.lbl_status = QLabel("Pronto")
        self.lbl_status.setStyleSheet("color: #94a3b8; font-size: 11px;")

        btn_close = QPushButton("Chiudi")
        btn_close.clicked.connect(self.accept)

        bottom_box.addWidget(self.lbl_status)
        bottom_box.addWidget(self.progress_bar, 1)
        bottom_box.addWidget(btn_close)
        main_layout.addLayout(bottom_box)

    # 1. Loudness Conformer Tab
    def _create_loudness_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)

        lbl = QLabel("<b>Normalizzazione Audio ITU-R BS.1770-4 conforme per Amazon Prime</b>")
        lbl.setStyleSheet("color: #38bdf8; font-size: 13px;")
        layout.addWidget(lbl)

        grid = QGridLayout()
        grid.setSpacing(10)

        # File Input
        grid.addWidget(QLabel("File Video / Audio Sorgente:"), 0, 0)
        self.txt_loud_in = QLineEdit(self.initial_file)
        btn_b_in = QPushButton("Sfoglia...")
        btn_b_in.clicked.connect(lambda: self._browse_file(self.txt_loud_in))
        grid.addWidget(self.txt_loud_in, 0, 1)
        grid.addWidget(btn_b_in, 0, 2)

        # Target Specs
        grid.addWidget(QLabel("Target Loudness Integrata:"), 1, 0)
        lbl_target = QLabel("<b>-24.0 LKFS / LUFS</b> (Standard Obbligatorio Amazon Prime)")
        lbl_target.setStyleSheet("color: #34d399;")
        grid.addWidget(lbl_target, 1, 1)

        grid.addWidget(QLabel("Soglia True Peak Ceiling:"), 2, 0)
        lbl_tp = QLabel("<b>-2.0 dBTP</b> (Tassativo per evitare distorsioni inter-sample)")
        lbl_tp.setStyleSheet("color: #34d399;")
        grid.addWidget(lbl_tp, 2, 1)

        layout.addLayout(grid)

        layout.addStretch()

        btn_run = QPushButton("⚡ Conforma & Normalizza Audio a -24 LUFS / -2 dBTP")
        btn_run.setObjectName("PrimaryButton")
        btn_run.setFixedHeight(34)
        btn_run.clicked.connect(self._run_loudness_conform)
        layout.addWidget(btn_run)

        return w

    # 2. ProRes Transcoder Tab
    def _create_prores_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)

        lbl = QLabel("<b>Convertitore Apple ProRes 422 HQ 10-bit & Deinterlacciatore Progressivo</b>")
        lbl.setStyleSheet("color: #38bdf8; font-size: 13px;")
        layout.addWidget(lbl)

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(QLabel("File Video da Convertire:"), 0, 0)
        self.txt_prores_in = QLineEdit(self.initial_file)
        btn_b = QPushButton("Sfoglia...")
        btn_b.clicked.connect(lambda: self._browse_file(self.txt_prores_in))
        grid.addWidget(self.txt_prores_in, 0, 1)
        grid.addWidget(btn_b, 0, 2)

        grid.addWidget(QLabel("Profilo ProRes:"), 1, 0)
        self.cb_prores_profile = QComboBox()
        self.cb_prores_profile.addItems(["ProRes 422 HQ (Raccomandato Master Prime Video)", "ProRes 422 Standard", "ProRes 4444 (Master HDR)"])
        grid.addWidget(self.cb_prores_profile, 1, 1)

        grid.addWidget(QLabel("Scansione:"), 2, 0)
        self.cb_deint = QComboBox()
        self.cb_deint.addItems(["Forza Deinterlacciamento Progressivo (YADIF)", "Mantieni Originale (se già progressivo)"])
        grid.addWidget(self.cb_deint, 2, 1)

        layout.addLayout(grid)
        layout.addStretch()

        btn_run = QPushButton("🎞️ Avvia Transcoding Master ProRes 422 HQ")
        btn_run.setObjectName("PrimaryButton")
        btn_run.setFixedHeight(34)
        btn_run.clicked.connect(self._run_prores_transcode)
        layout.addWidget(btn_run)

        return w

    # 3. Bitrate & Storage Calculator Tab
    def _create_calc_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)

        lbl = QLabel("<b>Calcolatore Bitrate & Spazio di Archiviazione Master per Amazon</b>")
        lbl.setStyleSheet("color: #38bdf8; font-size: 13px;")
        layout.addWidget(lbl)

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(QLabel("Durata Contenuto (Minuti):"), 0, 0)
        self.sp_duration_min = QSpinBox()
        self.sp_duration_min.setRange(1, 600)
        self.sp_duration_min.setValue(90)
        self.sp_duration_min.valueChanged.connect(self._recalc_storage)
        grid.addWidget(self.sp_duration_min, 0, 1)

        grid.addWidget(QLabel("Formato / Risoluzione:"), 1, 0)
        self.cb_calc_format = QComboBox()
        self.cb_calc_format.addItems([
            "HD 1080p - Apple ProRes 422 HQ (~220 Mbps)",
            "HD 1080p - H.264 High Bitrate (~25 Mbps)",
            "4K UHD 2160p - Apple ProRes 422 HQ (~880 Mbps)",
            "4K UHD 2160p - HEVC Main 10 (~50 Mbps)"
        ])
        self.cb_calc_format.currentIndexChanged.connect(self._recalc_storage)
        grid.addWidget(self.cb_calc_format, 1, 1)

        # Output Cards
        res_card = QFrame()
        res_card.setStyleSheet("background-color: #0d1527; border: 1px solid #1f2937; border-radius: 6px; padding: 12px;")
        res_layout = QGridLayout(res_card)

        self.lbl_est_size = QLabel("148.5 GB")
        self.lbl_est_size.setStyleSheet("font-size: 16px; font-weight: bold; color: #38bdf8;")

        self.lbl_est_bitrate = QLabel("220.0 Mbps")
        self.lbl_est_bitrate.setStyleSheet("font-size: 16px; font-weight: bold; color: #34d399;")

        self.lbl_upload_time = QLabel("~20 minuti (su fibra 1 Gbps)")
        self.lbl_upload_time.setStyleSheet("font-size: 14px; font-weight: 500; color: #f1f5f9;")

        res_layout.addWidget(QLabel("<b>Dimensione File Stimata:</b>"), 0, 0)
        res_layout.addWidget(self.lbl_est_size, 0, 1)

        res_layout.addWidget(QLabel("<b>Bitrate Medio Richiesto:</b>"), 1, 0)
        res_layout.addWidget(self.lbl_est_bitrate, 1, 1)

        res_layout.addWidget(QLabel("<b>Tempo Upload Stimato:</b>"), 2, 0)
        res_layout.addWidget(self.lbl_upload_time, 2, 1)

        grid.addWidget(res_card, 2, 0, 1, 2)

        layout.addLayout(grid)
        layout.addStretch()

        self._recalc_storage()
        return w

    # 4. Test Pattern Generator Tab
    def _create_pattern_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)

        lbl = QLabel("<b>Generatore Test Pattern SMPTE/EBU con Tono 1kHz a -24.0 LKFS</b>")
        lbl.setStyleSheet("color: #38bdf8; font-size: 13px;")
        layout.addWidget(lbl)

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(QLabel("Risoluzione:"), 0, 0)
        self.cb_pat_res = QComboBox()
        self.cb_pat_res.addItems(["1920x1080 (HD 16:9)", "3840x2160 (4K UHD 16:9)"])
        grid.addWidget(self.cb_pat_res, 0, 1)

        grid.addWidget(QLabel("Frame Rate:"), 1, 0)
        self.cb_pat_fps = QComboBox()
        self.cb_pat_fps.addItems(["24.0 fps", "23.976 fps", "25.0 fps (PAL)", "29.97 fps (NTSC)"])
        grid.addWidget(self.cb_pat_fps, 1, 1)

        grid.addWidget(QLabel("Durata (Secondi):"), 2, 0)
        self.sp_pat_dur = QSpinBox()
        self.sp_pat_dur.setRange(1, 60)
        self.sp_pat_dur.setValue(10)
        grid.addWidget(self.sp_pat_dur, 2, 1)

        layout.addLayout(grid)
        layout.addStretch()

        btn_run = QPushButton("🎨 Genera File Master di Calibrazione (.mov)")
        btn_run.setObjectName("PrimaryButton")
        btn_run.setFixedHeight(34)
        btn_run.clicked.connect(self._run_generate_pattern)
        layout.addWidget(btn_run)

        return w

    def _browse_file(self, target_line_edit: QLineEdit):
        f, _ = QFileDialog.getOpenFileName(self, "Seleziona File", "", "Media Files (*.mov *.mp4 *.mxf *.wav *.mkv);;All Files (*.*)")
        if f:
            target_line_edit.setText(f)

    def _run_loudness_conform(self):
        in_file = self.txt_loud_in.text().strip()
        if not in_file or not os.path.isfile(in_file):
            QMessageBox.warning(self, "Attenzione", "Seleziona un file multimediale valido.")
            return

        base, ext = os.path.splitext(in_file)
        out_file = f"{base}_LoudnessConformed_24LKFS{ext}"

        cmd = [
            self.ffmpeg_bin, "-y",
            "-i", in_file,
            "-c:v", "copy",
            "-af", "loudnorm=I=-24.0:TP=-2.0:LRA=11.0",
            "-c:a", "pcm_s24le" if ext.lower() == ".mov" else "aac",
            "-ar", "48000",
            out_file
        ]

        self._start_task(cmd, out_file, "Normalizzazione Loudness a -24 LUFS in corso...")

    def _run_prores_transcode(self):
        in_file = self.txt_prores_in.text().strip()
        if not in_file or not os.path.isfile(in_file):
            QMessageBox.warning(self, "Attenzione", "Seleziona un file sorgente valido.")
            return

        base, _ = os.path.splitext(in_file)
        out_file = f"{base}_ProRes422HQ_Master.mov"

        profile_idx = self.cb_prores_profile.currentIndex()
        prof_code = "3" if profile_idx == 0 else ("2" if profile_idx == 1 else "4")

        vf = ["format=yuv422p10le", "colorspace=all=bt709:trc=bt709:pri=bt709"]
        if self.cb_deint.currentIndex() == 0:
            vf.insert(0, "yadif=mode=send_frame:parity=auto:deint=all")

        cmd = [
            self.ffmpeg_bin, "-y",
            "-i", in_file,
            "-vf", ",".join(vf),
            "-c:v", "prores_ks",
            "-profile:v", prof_code,
            "-vendor", "apl0",
            "-bits_per_mb", "8000",
            "-color_primaries", "bt709",
            "-color_trc", "bt709",
            "-colorspace", "bt709",
            "-color_range", "tv",
            "-c:a", "pcm_s24le",
            "-ar", "48000",
            out_file
        ]

        self._start_task(cmd, out_file, "Transcoding in Apple ProRes 422 HQ in corso...")

    def _run_generate_pattern(self):
        out_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        out_file = os.path.join(out_dir, "Amazon_Calibration_TestPattern_24LKFS.mov")

        res_str = "1920x1080" if self.cb_pat_res.currentIndex() == 0 else "3840x2160"
        fps_map = ["24", "24000/1001", "25", "30000/1001"]
        fps_str = fps_map[self.cb_pat_fps.currentIndex()]
        dur = self.sp_pat_dur.value()

        cmd = [
            self.ffmpeg_bin, "-y",
            "-f", "lavfi", "-i", f"smptehdbars=size={res_str}:rate={fps_str}:duration={dur}",
            "-f", "lavfi", "-i", f"sine=frequency=1000:duration={dur}:sample_rate=48000",
            "-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le",
            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
            "-af", "loudnorm=I=-24.0:TP=-2.0:LRA=7.0",
            "-c:a", "pcm_s24le", "-ar", "48000",
            out_file
        ]

        self._start_task(cmd, out_file, "Generazione Test Pattern in corso...")

    def _recalc_storage(self):
        mins = self.sp_duration_min.value()
        sec = mins * 60
        idx = self.cb_calc_format.currentIndex()

        if idx == 0:  # ProRes HD
            mbps = 220.0
        elif idx == 1:  # H.264 HD
            mbps = 25.0
        elif idx == 2:  # ProRes 4K
            mbps = 880.0
        else:  # HEVC 4K
            mbps = 50.0

        bytes_total = int((mbps * 1_000_000 / 8.0) * sec)
        self.lbl_est_size.setText(format_bytes(bytes_total))
        self.lbl_est_bitrate.setText(f"{mbps:.1f} Mbps")

        # Upload estimate (1 Gbps fiber ~ 100 MB/sec, 100 Mbps ~ 10 MB/sec)
        sec_upload = bytes_total / (100 * 1024 * 1024)
        if sec_upload < 60:
            up_str = f"~{int(sec_upload)} secondi (su fibra Gigabit)"
        else:
            up_str = f"~{int(sec_upload / 60)} minuti (su fibra Gigabit)"
        self.lbl_upload_time.setText(up_str)

    def _start_task(self, cmd: list, output_file: str, status_msg: str):
        self.lbl_status.setText(status_msg)
        self.progress_bar.setRange(0, 0)  # Indeterminate

        self.worker = UtilityWorker(cmd, output_file)
        self.worker.sig_done.connect(self._on_task_done)
        self.worker.start()

    def _on_task_done(self, success: bool, msg: str):
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100 if success else 0)
        self.lbl_status.setText("Completato!" if success else "Errore.")
        if success:
            QMessageBox.information(self, "Successo", f"Operazione completata con successo!\n\n{msg}")
        else:
            QMessageBox.critical(self, "Errore", f"Si è verificato un errore:\n\n{msg}")
