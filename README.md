# PrimeQC Master - Amazon Prime Video Quality Control Suite

**PrimeQC Master** is a broadcast-grade, standalone Windows desktop application with zero margin of error, engineered specifically for **Amazon Prime Video** delivery specifications (Prime Video Direct and Amazon Studios / Video Central Partner operations).

---

## Key Features & QC Checks

### 1. Delivery Standards & Compliance
- **Prime Video Direct (PVD) - HD Mezzanine**: ProRes 422 HQ / AVC H.264 / MPEG-2, Progressive CFR, 1920x1080, Rec.709.
- **Prime Video Direct (PVD) - 4K UHD Mezzanine**: ProRes 422 HQ / ProRes 4444 / HEVC Main 10, 3840x2160 / 4096x2160, BT.2020 / BT.709.
- **Amazon Studios / Original Content Partner SDR**: ProRes 422 HQ / IMF SMPTE App 2e, Rec.709 Gamma 2.4, Legal Range.
- **Amazon Studios / Original Content Partner HDR**: ProRes 4444 XQ, Rec.2020 ST.2084 (PQ) / Dolby Vision / HLG.
- **Amazon Trailer & Promo Delivery**.

### 2. Deep Audio & ITU-R BS.1770-4 Loudness Engine
- **Integrated Loudness**: Target **-24.0 LKFS / LUFS** (Strict tolerance $\pm 1.0$ LU or $\pm 2.0$ LU).
- **Maximum True Peak**: Strict **$\le -2.0$ dBTP** ceiling limit.
- **Loudness Range (LRA)**: Dynamic range evaluation (4 - 18 LU).
- **Inter-Channel Stereo Phase Correlation**: Identifies anti-phase components ($r < 0.0$) preventing mono downmix phase cancellation.
- **Dual-Mono vs Stereo Detection**: Flags fake stereo channels.
- **Discrete Channel Mapping**: Enforces 2.0 Stereo (L, R), 5.1 Surround (L, R, C, LFE, Ls, Rs SMPTE order), and 8.0 Discrete.
- **Audio/Video Sync**: Enforces duration alignment within $\le 0.1\text{s}$ (max 2 frames).

### 3. Video Signal Integrity & Broadcast Artifact Detection
- **Scan Type**: Strict progressive validation (Interlaced and telecine 3:2 pulldown strictly rejected).
- **Frame Rates**: Standard CFR rates only (23.976, 24.0, 25.0, 29.97, 50.0, 59.94, 60.0 fps).
- **Clean Master Check**: Flags non-program content (Bars & Tone, Countdown Slates).
- **Black Frames**: Flags leading black ($>2.0\text{s}$), trailing black ($>5.0\text{s}$), or mid-program black frames.
- **Freeze Frames**: Detects frozen video sequences ($>3.0\text{s}$).
- **Photosensitive Epilepsy (PSE)**: Screen flash frequency monitoring ($>3\text{Hz}$).
- **Broadcast Gamut**: Out-of-range IRE luma ($<0\%$ or $>100\%$) and illegal chroma violations.

### 4. Subtitle & Timed Text QC
- Validates SRT, WebVTT, TTML, DFXP, SCC sidecars.
- Enforces Reading Speed ($\le 20\text{ CPS}$), Line Length ($\le 42\text{ CPL}$), Max 2 Lines per event, and non-overlapping timecodes.

### 5. Reporting & Remediation
- **Official PDF Compliance Certificate**: Multi-page high-resolution report with official compliance stamp, parameter tables, and sign-off block.
- **JSON Manifest**: Machine-readable log for automated pipelines.
- **CSV Log**: Spreadsheet output for post-production facility logs.
- **1-Click Remediation**: Generates exact FFmpeg commands and DaVinci Resolve / Premiere Pro project configuration steps to fix all issues with one click.

---

## Installation & Distribution

### 1. Dedicated Windows Installer
Run `dist/PrimeQC_Setup.exe` to install PrimeQC Master to your computer with Start Menu and Desktop shortcuts.

### 2. Standalone Portable Executable
Run `dist/PrimeQC/PrimeQC.exe` directly without installation.

### 3. CLI Mode (Headless Automation)
```bash
python src/main.py --cli -i "path/to/master.mov" -p "Prime Video Direct - HD Mezzanine" --pdf "report.pdf" --json "manifest.json"
```
