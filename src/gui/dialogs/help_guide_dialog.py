"""
Amazon Prime Video Standards & User Guide Dialog.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextBrowser, QPushButton
)
from PySide6.QtCore import Qt


class HelpGuideDialog(QDialog):
    """Interactive guide to Amazon Prime Video QC specifications and export workflows."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Guida agli Standard di Consegna Amazon Prime Video")
        self.resize(750, 580)
        self.setStyleSheet("""
            QDialog {
                background-color: #0b0f19;
                color: #e2e8f0;
                font-family: 'Segoe UI', sans-serif;
            }
            QTextBrowser {
                background-color: #111827;
                border: 1px solid #1f2937;
                border-radius: 6px;
                padding: 14px;
                color: #cbd5e1;
                font-size: 12px;
                line-height: 1.5;
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
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        lbl_header = QLabel("<b>📚 GUIDA UFFICIALE AGLI STANDARD AMAZON PRIME VIDEO</b>")
        lbl_header.setStyleSheet("font-size: 14px; color: #38bdf8;")
        layout.addWidget(lbl_header)

        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)

        guide_html = """
        <h2 style='color:#38bdf8;'>1. Standard Video Mezzanine per Amazon Prime</h2>
        <ul>
            <li><b>Codec Raccomandato:</b> Apple ProRes 422 HQ (in container .mov). Per master HDR10/Dolby Vision è richiesto ProRes 4444 XQ.</li>
            <li><b>Altri Codec Accettati (PVD):</b> H.264 / AVC (High Profile Level 4.1-5.2) ad alto bitrate (&ge; 25 Mbps), MPEG-2.</li>
            <li><b>Tipo di Scansione (Scan Type):</b> <u>ESCLUSIVAMENTE PROGRESSIVO</u>. I contenuti interlacciati (1080i) o con cadenza telecine (3:2 pulldown) vengono <b>rigettati automaticamente</b> dai sistemi di ingestione di Amazon.</li>
            <li><b>Frame Rate:</b> Deve essere rigorosamente Costante (CFR). Standard supportati: 23.976, 24.0, 25.0, 29.97, 30.0, 50.0, 59.94, 60.0 fps.</li>
            <li><b>Risoluzione e Aspect Ratio:</b> 1920x1080 (HD), 3840x2160 (UHD), o formati cinematografici 1.85:1 / 2.39:1 con raster pulito.</li>
            <li><b>Spazio Colore e Livelli:</b> Rec.709 con Gamma 2.4 e Legal/Limited Range (16-235 a 8-bit / 64-940 a 10-bit) per SDR. Rec.2020 PQ ST.2084 per HDR.</li>
        </ul>

        <h2 style='color:#38bdf8;'>2. Standard Audio e Loudness (ITU-R BS.1770-4 / EBU R128)</h2>
        <ul>
            <li><b>Loudness Integrata (Integrated LUFS / LKFS):</b> Target obbligatorio di <b>-24.0 LKFS/LUFS</b> (&plusmn;1.0 LU per Amazon Studios, &plusmn;2.0 LU per Prime Video Direct).</li>
            <li><b>True Peak Massimo (dBTP):</b> Massimo consentito <b>-2.0 dBTP</b> (per prevenire distorsioni e clipping negli algoritmi di compressione streaming).</li>
            <li><b>Frequenza di Campionamento:</b> Tassativamente <b>48.000 Hz (48 kHz)</b> a 24-bit (o 16-bit) PCM lineare non compresso.</li>
            <li><b>Mappatura Canali (Discrete Tracks):</b>
                <ul>
                    <li><b>Stereo (2 canali):</b> Traccia 1 = Left, Traccia 2 = Right.</li>
                    <li><b>5.1 Surround (6 canali):</b> 1: L, 2: R, 3: C, 4: LFE, 5: Ls, 6: Rs (ordine SMPTE obbligatorio).</li>
                    <li><b>8 Canali (5.1 + Stereo):</b> 1-6 Surround 5.1, 7: Left Stereo, 8: Right Stereo.</li>
                </ul>
            </li>
            <li><b>Correlazione di Fase:</b> Deve essere positiva (&gt; 0.0) per garantire la piena compatibilità mono ed evitare cancellazioni acustiche.</li>
            <li><b>Sincronizzazione A/V:</b> La durata della traccia audio deve coincidere con il video con uno scarto massimo &le; 0.1s (max 2 fotogrammi).</li>
        </ul>

        <h2 style='color:#38bdf8;'>3. Requisiti Clean Master & Integrità del Segnale</h2>
        <ul>
            <li><b>Nessun materiale non-program:</b> Il file deve essere tagliato esattamente all'inizio e alla fine del programma. <b>Rimuovere barre di colore, toni a 1kHz, cartelli di ciak/slate e countdown</b>.</li>
            <li><b>Fotogrammi Neri (Black Frames):</b> Massimo 0.5s - 2.0s di nero in testa e massimo 2.0s - 5.0s in coda. Nessun blackout immotivato durante il programma.</li>
            <li><b>Filtro Epilessia Fotosensibile (PSE):</b> La frequenza di lampeggiamento luminoso ad alto contrasto non deve superare i 3 Hz (Standard ITU-R BT.1702).</li>
        </ul>

        <h2 style='color:#38bdf8;'>4. Come esportare master conformi dai principali NLE</h2>
        <h3 style='color:#34d399;'>DaVinci Resolve:</h3>
        <p>1. Pagina <b>Fairlight</b>: Inserire nel Bus Master il <i>Fairlight FX > Limiter</i> con Ceiling impostato a <b>-2.0 dBFS</b>. Usare il <i>Loudness Meter</i> per verificare che l'Integrated Loudness sia a <b>-24.0 LUFS</b>.<br/>
        2. Pagina <b>Deliver</b>: Formato <i>QuickTime</i>, Codec <i>Apple ProRes</i>, Tipo <i>ProRes 422 HQ</i>. Audio: <i>Linear PCM, 24 Bit, 48000 Hz</i>.</p>

        <h3 style='color:#34d399;'>Adobe Premiere Pro:</h3>
        <p>1. Menu <i>Finestra > Mixer traccia audio</i>: Inserire nel canale Master il plugin <i>Loudness Radar</i> e un <i>Limitatore di picco</i> con soglia -2.0 dB.<br/>
        2. Finestra <i>Esporta</i>: Formato <i>QuickTime</i>, Preset <i>Apple ProRes 422 HQ</i>, Scansione <i>Progressiva</i>, Audio <i>Non compresso a 48 kHz, 24 bit</i>.</p>
        """

        self.browser.setHtml(guide_html)
        layout.addWidget(self.browser)

        btn_box = QHBoxLayout()
        btn_box.addStretch()
        btn_close = QPushButton("Ho Capito")
        btn_close.clicked.connect(self.accept)
        btn_box.addWidget(btn_close)
        layout.addLayout(btn_box)
