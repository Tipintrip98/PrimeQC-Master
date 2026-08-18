"""
Automated Remediation and Fix Command Generator for Amazon Prime Delivery Failures.
Generates copyable FFmpeg commands and NLE (Premiere Pro, DaVinci Resolve) instructions.
"""

import os
from typing import List, Dict, Any
from .models import QCIssue, QCReportData
from ..core.constants import Severity


class RemediationEngine:
    """Generates precise repair commands and NLE workarounds based on QC results."""

    @staticmethod
    def generate_ffmpeg_fix_command(report: QCReportData) -> str:
        """
        Builds a single FFmpeg command to resolve all detected issues (loudness normalization,
        deinterlacing, ProRes 422 HQ transcoding, 48kHz audio resampling, channel layout mapping, etc.).
        """
        input_file = f'"{report.file_path}"'
        dir_name = os.path.dirname(report.file_path)
        base_name = os.path.splitext(report.file_name)[0]
        output_file = f'"{os.path.join(dir_name, base_name + "_PrimeQC_Conformed.mov")}"'

        # Analyze issues
        needs_deinterlace = any(i.parameter == "Scan Type" and i.severity == Severity.FAIL for i in report.issues)
        needs_loudnorm = any(i.parameter.startswith("Integrated Loudness") and i.severity == Severity.FAIL for i in report.issues)
        needs_truepeak = any(i.parameter.startswith("Max True Peak") and i.severity == Severity.FAIL for i in report.issues)
        needs_audio_resample = any("Sample Rate" in i.parameter and i.severity == Severity.FAIL for i in report.issues)
        needs_prores_transcode = any(i.parameter == "Video Codec" and i.severity == Severity.FAIL for i in report.issues)
        needs_cfr = any("Frame Rate" in i.parameter and i.severity == Severity.FAIL for i in report.issues)

        vf_filters = []
        af_filters = []

        # Video filters
        if needs_deinterlace:
            vf_filters.append("yadif=mode=send_frame:parity=auto:deint=all")

        # Set color tags & format
        vf_filters.append("format=yuv422p10le")
        vf_filters.append("colorspace=all=bt709:trc=bt709:pri=bt709")

        # Audio filters
        if needs_loudnorm or needs_truepeak:
            af_filters.append("loudnorm=I=-24.0:TP=-2.0:LRA=11.0")
        if needs_audio_resample:
            af_filters.append("aresample=48000:resampler=soxr")

        # Assemble FFmpeg Command
        cmd_parts = ["ffmpeg", "-y", "-i", input_file]

        if vf_filters:
            cmd_parts.extend(["-vf", f'"{",".join(vf_filters)}"'])

        # Video encoding parameters
        cmd_parts.extend([
            "-c:v", "prores_ks",
            "-profile:v", "3",      # ProRes 422 HQ
            "-vendor", "apl0",
            "-bits_per_mb", "8000",
            "-color_primaries", "bt709",
            "-color_trc", "bt709",
            "-colorspace", "bt709",
            "-color_range", "tv"
        ])

        if needs_cfr:
            cmd_parts.extend(["-vsync", "cfr", "-r", "24000/1001"])

        # Audio encoding parameters
        if af_filters:
            cmd_parts.extend(["-af", f'"{",".join(af_filters)}"'])

        cmd_parts.extend([
            "-c:a", "pcm_s24le",
            "-ar", "48000"
        ])

        cmd_parts.append(output_file)

        return " ".join(cmd_parts)

    @staticmethod
    def get_nle_instructions(report: QCReportData) -> List[Dict[str, str]]:
        """Provides NLE-specific instructions (DaVinci Resolve / Premiere Pro)."""
        instructions = []

        # Loudness
        if any("Loudness" in i.parameter for i in report.issues if i.severity == Severity.FAIL):
            instructions.append({
                "title": "Audio Loudness (-24.0 LKFS / -2.0 dBTP)",
                "davinci": "In Fairlight page, open Master bus dynamics. Add Limiter with Ceiling set to -2.0 dBFS. Use Fairlight > Loudness History to verify Integrated Loudness sits at -24.0 LUFS (±1 LU).",
                "premiere": "In Window > Essential Sound > Dialogue, set Loudness to Auto-Match (-24 LKFS). On Master Track in Audio Track Mixer, insert Loudness Radar and True Peak Limiter."
            })

        # Scan Type / Interlacing
        if any(i.parameter == "Scan Type" for i in report.issues if i.severity == Severity.FAIL):
            instructions.append({
                "title": "Scan Type (Deinterlacing to Progressive)",
                "davinci": "Right-click clip in Media Pool > Clip Attributes > Video > Enable Deinterlace (Neural Engine / Motion Adaptive). Set Timeline settings to Progressive.",
                "premiere": "Right-click clip in Project panel > Modify > Interpret Footage > Field Order: Conform to Progressive."
            })

        # Export Format
        instructions.append({
            "title": "Master Export Settings",
            "davinci": "Deliver Page: Format QuickTime, Codec Apple ProRes, Type ProRes 422 HQ, Color Space Tag: Same as Project (Rec.709), Audio: Linear PCM, 24 Bit, 48000 Hz.",
            "premiere": "Export Settings: Format QuickTime, Preset Apple ProRes 422 HQ, Audio: Uncompressed PCM, 48 kHz, 24 bit."
        })

        return instructions
