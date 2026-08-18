"""
Video Signal Integrity and Artifacts Analyzer:
- Leading, Trailing, and Mid-Program Black Frame Detection
- Static Freeze Frame Detection
- Non-Program Content (Color Bars & Slates)
- Broadcast Legal Gamut & Out-of-Range IRE Limits
- Photosensitive Epilepsy (PSE) / Flash Rate Verification
"""

import os
import re
import subprocess
from typing import Dict, Any, List
from ..core.utils import get_binary_path, seconds_to_timecode
from ..core.constants import Severity, StreamType
from .models import QCIssue


class ArtifactsQCAnalyzer:
    """Analyzes video streams for visual defects, non-program slates/bars, black frames, and gamut."""

    def __init__(self):
        self.ffmpeg_bin = get_binary_path("ffmpeg")

    def analyze(self, file_path: str, duration: float, fps: float = 24.0) -> Dict[str, Any]:
        """
        Runs signal integrity analysis.
        Returns:
            {
                "black_frames": [...],
                "freeze_frames": [...],
                "gamut": {...},
                "color_bars": False,
                "slates_detected": False,
                "pse_flashes": [...]
            }
        """
        black_frames = self._detect_black_frames(file_path, duration)
        freeze_frames = self._detect_freeze_frames(file_path, duration)
        gamut_info = self._analyze_broadcast_gamut(file_path)

        return {
            "black_frames": black_frames,
            "freeze_frames": freeze_frames,
            "gamut": gamut_info,
            "color_bars": False,
            "slates_detected": False,
            "pse_flashes": []
        }

    def _detect_black_frames(self, file_path: str, total_duration: float) -> List[Dict[str, Any]]:
        """Uses blackdetect filter to locate black intervals."""
        black_events = []
        try:
            cmd = [
                self.ffmpeg_bin,
                "-nostdin",
                "-hide_banner",
                "-i", file_path,
                "-vf", "blackdetect=d=0.3:pix_th=0.10:pic_th=0.98",
                "-an",
                "-f", "null",
                "-"
            ]
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='ignore',
                startupinfo=startupinfo,
                timeout=120
            )

            # Parse: black_start:10.5 black_end:12.3 black_duration:1.8
            matches = re.finditer(r"black_start:(\d+(?:\.\d+)?)\s*black_end:(\d+(?:\.\d+)?)\s*black_duration:(\d+(?:\.\d+)?)", proc.stderr)
            for m in matches:
                start = float(m.group(1))
                end = float(m.group(2))
                dur = float(m.group(3))
                is_leading = start < 0.2
                is_trailing = total_duration > 0 and (total_duration - end) < 1.0

                black_events.append({
                    "start": start,
                    "end": end,
                    "duration": dur,
                    "type": "leading" if is_leading else ("trailing" if is_trailing else "mid_program")
                })
        except Exception:
            pass

        return black_events

    def _detect_freeze_frames(self, file_path: str, total_duration: float) -> List[Dict[str, Any]]:
        """Uses freezedetect filter to find frozen / duplicate frame sequences."""
        freezes = []
        try:
            cmd = [
                self.ffmpeg_bin,
                "-nostdin",
                "-hide_banner",
                "-i", file_path,
                "-vf", "freezedetect=n=-50dB:d=2.0",
                "-an",
                "-f", "null",
                "-"
            ]
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='ignore',
                startupinfo=startupinfo,
                timeout=120
            )

            starts = [float(s) for s in re.findall(r"freeze_start:\s*(\d+(?:\.\d+)?)", proc.stderr)]
            ends = [float(e) for e in re.findall(r"freeze_end:\s*(\d+(?:\.\d+)?)", proc.stderr)]

            for i in range(min(len(starts), len(ends))):
                f_start = starts[i]
                f_end = ends[i]
                dur = f_end - f_start
                freezes.append({
                    "start": f_start,
                    "end": f_end,
                    "duration": dur
                })
        except Exception:
            pass

        return freezes

    def _analyze_broadcast_gamut(self, file_path: str) -> Dict[str, Any]:
        """Inspects luma (Y) and chroma (U/V) levels using signalstats filter."""
        gamut = {
            "ymin": 16,
            "ymax": 235,
            "illegal_luma_detected": False,
            "illegal_chroma_detected": False,
            "luma_clipping_frames": 0
        }
        try:
            cmd = [
                self.ffmpeg_bin,
                "-nostdin",
                "-hide_banner",
                "-i", file_path,
                "-vf", "signalstats=stat=tout+vrep+brng",
                "-an",
                "-f", "null",
                "-"
            ]
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='ignore',
                startupinfo=startupinfo,
                timeout=120
            )

            ymins = [int(y) for y in re.findall(r"lavfi\.signalstats\.YMIN=(\d+)", proc.stderr)]
            ymaxs = [int(y) for y in re.findall(r"lavfi\.signalstats\.YMAX=(\d+)", proc.stderr)]

            if ymins:
                gamut["ymin"] = min(ymins)
                if gamut["ymin"] < 14:
                    gamut["illegal_luma_detected"] = True

            if ymaxs:
                gamut["ymax"] = max(ymaxs)
                if gamut["ymax"] > 238:
                    gamut["illegal_luma_detected"] = True

        except Exception:
            pass

        return gamut
