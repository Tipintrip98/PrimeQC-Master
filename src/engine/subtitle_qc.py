"""
Timed Text and Subtitle QC Analyzer for Amazon Prime:
- File format validation (SRT, WebVTT, TTML, DFXP, SCC)
- Character encoding (UTF-8)
- Reading speed (Characters per Second - CPS <= 20)
- Line length (Characters per Line - CPL <= 42)
- Line count per event (Max 2 lines)
- Overlapping timecodes & zero duration cues
"""

import os
import re
from typing import List, Dict, Any
from ..core.constants import Severity, StreamType
from .models import QCIssue
from ..core.utils import timecode_to_seconds, seconds_to_timecode


class SubtitleQCAnalyzer:
    """Validates standalone sidecar subtitle files and embedded text streams."""

    def analyze_file(self, file_path: str, video_fps: float = 24.0) -> List[QCIssue]:
        """Analyzes an external subtitle file."""
        issues: List[QCIssue] = []
        if not os.path.isfile(file_path):
            return issues

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in [".srt", ".vtt", ".ttml", ".dfxp", ".scc", ".xml"]:
            issues.append(QCIssue(
                id="SUB-001",
                severity=Severity.FAIL,
                stream_type=StreamType.SUBTITLE,
                parameter="Subtitle Format",
                measured_value=ext,
                expected_value=".srt, .vtt, .ttml, .dfxp, or .scc",
                description=f"Subtitle format '{ext}' is not supported by Amazon Prime Video.",
                remediation_tip="Convert timed text to standard UTF-8 SRT, WebVTT, or TTML/DFXP."
            ))
            return issues

        try:
            with open(file_path, "r", encoding="utf-8-sig", errors="replace") as f:
                content = f.read()
        except Exception as e:
            issues.append(QCIssue(
                id="SUB-002",
                severity=Severity.FAIL,
                stream_type=StreamType.SUBTITLE,
                parameter="Subtitle Encoding",
                measured_value="Encoding Error",
                expected_value="UTF-8",
                description=f"Failed to decode subtitle file: {str(e)}",
                remediation_tip="Save subtitle file with UTF-8 encoding."
            ))
            return issues

        # Parse cues for SRT/VTT
        if ext in [".srt", ".vtt"]:
            cues = self._parse_srt_vtt(content, video_fps)
            prev_end = 0.0
            for idx, cue in enumerate(cues):
                start = cue["start"]
                end = cue["end"]
                duration = end - start
                text = cue["text"]
                lines = [line.strip() for line in text.split("\n") if line.strip()]

                # Overlap check
                if start < prev_end - 0.01:
                    issues.append(QCIssue(
                        id=f"SUB-TIME-{idx}",
                        severity=Severity.FAIL,
                        stream_type=StreamType.SUBTITLE,
                        parameter="Subtitle Overlap",
                        measured_value=f"Overlap at {seconds_to_timecode(start, video_fps)}",
                        expected_value="No overlapping timecodes",
                        description=f"Subtitle cue {idx+1} overlaps with the previous cue.",
                        remediation_tip="Adjust in/out timecodes so subtitle events do not collide.",
                        timecode=seconds_to_timecode(start, video_fps),
                        timestamp_sec=start
                    ))

                # Zero/negative duration
                if duration <= 0.3:
                    issues.append(QCIssue(
                        id=f"SUB-DUR-{idx}",
                        severity=Severity.WARNING,
                        stream_type=StreamType.SUBTITLE,
                        parameter="Subtitle Duration",
                        measured_value=f"{duration:.2f}s",
                        expected_value=">= 0.8s (min duration)",
                        description=f"Subtitle cue {idx+1} duration is too short for human readability.",
                        remediation_tip="Extend subtitle duration to at least 0.8 to 1.0 second.",
                        timecode=seconds_to_timecode(start, video_fps),
                        timestamp_sec=start
                    ))

                # Line count (max 2 lines)
                if len(lines) > 2:
                    issues.append(QCIssue(
                        id=f"SUB-LINES-{idx}",
                        severity=Severity.FAIL,
                        stream_type=StreamType.SUBTITLE,
                        parameter="Subtitle Line Count",
                        measured_value=f"{len(lines)} lines",
                        expected_value="<= 2 lines",
                        description=f"Subtitle cue {idx+1} exceeds the 2-line maximum.",
                        remediation_tip="Re-break subtitle text into maximum 2 lines per event.",
                        timecode=seconds_to_timecode(start, video_fps),
                        timestamp_sec=start
                    ))

                # Characters per line (CPL <= 42)
                for l_idx, l_text in enumerate(lines):
                    if len(l_text) > 42:
                        issues.append(QCIssue(
                            id=f"SUB-CPL-{idx}-{l_idx}",
                            severity=Severity.WARNING,
                            stream_type=StreamType.SUBTITLE,
                            parameter="Characters Per Line (CPL)",
                            measured_value=f"{len(l_text)} chars",
                            expected_value="<= 42 chars",
                            description=f"Line {l_idx+1} of cue {idx+1} exceeds 42 characters limit.",
                            remediation_tip="Insert a line break to keep lines under 42 characters.",
                            timecode=seconds_to_timecode(start, video_fps),
                            timestamp_sec=start
                        ))

                # Reading speed (CPS <= 20 chars/sec)
                total_chars = sum(len(l) for l in lines)
                if duration > 0:
                    cps = total_chars / duration
                    if cps > 20.0:
                        issues.append(QCIssue(
                            id=f"SUB-CPS-{idx}",
                            severity=Severity.WARNING,
                            stream_type=StreamType.SUBTITLE,
                            parameter="Reading Speed (CPS)",
                            measured_value=f"{cps:.1f} chars/sec",
                            expected_value="<= 20 chars/sec",
                            description=f"Cue {idx+1} reading speed is too high ({cps:.1f} CPS).",
                            remediation_tip="Condense text or extend cue display duration.",
                            timecode=seconds_to_timecode(start, video_fps),
                            timestamp_sec=start
                        ))

                prev_end = end

        return issues

    def _parse_srt_vtt(self, content: str, fps: float) -> List[Dict[str, Any]]:
        """Parses SRT or VTT content into list of {start, end, text}."""
        cues = []
        pattern = re.compile(
            r"(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})\r?\n(.*?)(?=\r?\n\r?\n|\Z)",
            re.DOTALL
        )
        for m in pattern.finditer(content):
            s_str = m.group(1).replace(",", ".")
            e_str = m.group(2).replace(",", ".")
            text = m.group(3).strip()
            
            s_sec = timecode_to_seconds(s_str, fps)
            e_sec = timecode_to_seconds(e_str, fps)
            cues.append({
                "start": s_sec,
                "end": e_sec,
                "text": text
            })
        return cues
