"""
Data models for Quality Control Analysis, Stream Metadata, and Verification Issues.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..core.constants import Severity, StreamType


@dataclass
class QCIssue:
    """Represents a single detected compliance issue or passing checkpoint."""
    id: str
    severity: Any  # Severity enum or str
    stream_type: Any  # StreamType enum or str
    parameter: str
    measured_value: str
    expected_value: str
    description: str
    remediation_tip: str
    timecode: str = "00:00:00:00"
    frame: int = 0
    timestamp_sec: float = 0.0
    thumbnail_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        sev = self.severity.value if hasattr(self.severity, "value") else str(self.severity)
        st = self.stream_type.value if hasattr(self.stream_type, "value") else str(self.stream_type)
        return {
            "id": self.id,
            "severity": sev,
            "stream_type": st,
            "parameter": self.parameter,
            "measured_value": self.measured_value,
            "expected_value": self.expected_value,
            "description": self.description,
            "remediation_tip": self.remediation_tip,
            "timecode": self.timecode,
            "frame": self.frame,
            "timestamp_sec": self.timestamp_sec,
            "thumbnail_path": self.thumbnail_path
        }


@dataclass
class StreamInfo:
    """Detailed stream metadata."""
    index: int
    codec_type: str  # 'video', 'audio', 'subtitle'
    codec_name: str
    codec_long_name: str = ""
    profile: str = ""
    width: int = 0
    height: int = 0
    fps: float = 0.0
    field_order: str = "progressive"  # 'progressive', 'tt', 'bb', 'tb', 'bt'
    pix_fmt: str = ""
    bits_per_raw_sample: int = 8
    bitrate: int = 0
    duration: float = 0.0
    color_primaries: str = "unknown"
    color_space: str = "unknown"
    color_transfer: str = "unknown"
    color_range: str = "unknown"
    sample_rate: int = 0
    channels: int = 0
    channel_layout: str = ""
    language: str = "und"
    title: str = ""
    extra_tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class QCReportData:
    """Complete QC analysis result dataset for a media file."""
    file_path: str
    file_name: str
    file_size_bytes: int
    duration_sec: float
    profile_name: str
    verdict: Any = Severity.PASS
    compliance_score: float = 100.0  # 0.0 to 100.0%
    issues: List[QCIssue] = field(default_factory=list)
    container_info: Dict[str, Any] = field(default_factory=dict)
    video_streams: List[StreamInfo] = field(default_factory=list)
    audio_streams: List[StreamInfo] = field(default_factory=list)
    subtitle_streams: List[StreamInfo] = field(default_factory=list)
    loudness_data: Dict[str, Any] = field(default_factory=dict)
    phase_correlation_data: Dict[str, Any] = field(default_factory=dict)
    artifacts_data: Dict[str, Any] = field(default_factory=dict)
    generated_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    analysis_duration_sec: float = 0.0

    def _is_sev(self, issue: QCIssue, target: Severity) -> bool:
        v = issue.severity.value if hasattr(issue.severity, "value") else str(issue.severity)
        return v == target.value

    def get_issues_by_severity(self, severity: Severity) -> List[QCIssue]:
        return [i for i in self.issues if self._is_sev(i, severity)]

    @property
    def fail_count(self) -> int:
        return len([i for i in self.issues if self._is_sev(i, Severity.FAIL)])

    @property
    def warning_count(self) -> int:
        return len([i for i in self.issues if self._is_sev(i, Severity.WARNING)])

    @property
    def notice_count(self) -> int:
        return len([i for i in self.issues if self._is_sev(i, Severity.NOTICE)])

    @property
    def pass_count(self) -> int:
        return len([i for i in self.issues if self._is_sev(i, Severity.PASS)])

    def to_dict(self) -> Dict[str, Any]:
        verdict_str = self.verdict.value if hasattr(self.verdict, "value") else str(self.verdict)
        return {
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_size_bytes": self.file_size_bytes,
            "duration_sec": self.duration_sec,
            "profile_name": self.profile_name,
            "verdict": verdict_str,
            "compliance_score": round(self.compliance_score, 1),
            "summary": {
                "fails": self.fail_count,
                "warnings": self.warning_count,
                "notices": self.notice_count,
                "passes": self.pass_count,
            },
            "container_info": self.container_info,
            "video_streams": [s.to_dict() for s in self.video_streams],
            "audio_streams": [s.to_dict() for s in self.audio_streams],
            "subtitle_streams": [s.to_dict() for s in self.subtitle_streams],
            "loudness_data": self.loudness_data,
            "phase_correlation_data": self.phase_correlation_data,
            "artifacts_data": self.artifacts_data,
            "issues": [i.to_dict() for i in self.issues],
            "generated_at": self.generated_at,
            "analysis_duration_sec": round(self.analysis_duration_sec, 2)
        }
