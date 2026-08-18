"""GUI widgets module for PrimeQC."""

from .drop_zone import DropZoneWidget
from .summary_card import SummaryCardWidget
from .issue_table import IssueTableWidget
from .loudness_view import LoudnessViewWidget
from .video_preview import VideoPreviewWidget
from .remediation_panel import RemediationPanelWidget
from .prime_report_view import PrimeReportViewWidget

__all__ = [
    "DropZoneWidget",
    "SummaryCardWidget",
    "IssueTableWidget",
    "LoudnessViewWidget",
    "VideoPreviewWidget",
    "RemediationPanelWidget",
    "PrimeReportViewWidget",
]
