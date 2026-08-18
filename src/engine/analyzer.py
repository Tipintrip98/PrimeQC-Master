"""
Master Quality Control Analyzer for Amazon Prime Video.
Coordinates probers, stream checkers, audio loudness analyzers, artifact detectors, and rules.
"""

import os
import time
from typing import Dict, Any, Optional, Callable, List
from .models import QCReportData, QCIssue, StreamInfo
from .probe import MediaProber
from .rules_amazon import AmazonRulesValidator
from .audio_qc import AudioQCAnalyzer
from .artifact_qc import ArtifactsQCAnalyzer
from .subtitle_qc import SubtitleQCAnalyzer
from ..core.constants import Severity, StreamType, PRIME_PROFILES, ProfileType
from ..core.config import AppConfig


class PrimeQCAnalyzer:
    """Orchestrates comprehensive, multi-layered QC verification against Amazon Prime standards."""

    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or AppConfig()
        self.prober = MediaProber()
        self.audio_analyzer = AudioQCAnalyzer()
        self.artifact_analyzer = ArtifactsQCAnalyzer()
        self.subtitle_analyzer = SubtitleQCAnalyzer()

    def run_qc(
        self,
        file_path: str,
        profile_name: str = ProfileType.PVD_HD.value,
        sidecar_subtitle_path: Optional[str] = None,
        progress_callback: Optional[Callable[[str, int, str], None]] = None
    ) -> QCReportData:
        """
        Executes full Amazon Prime QC inspection.
        progress_callback: fn(stage: str, percentage: int, detail: str)
        """
        start_time = time.time()
        file_name = os.path.basename(file_path)
        profile = self.config.get_profile(profile_name)
        validator = AmazonRulesValidator(profile)

        def update_prog(stage: str, pct: int, msg: str):
            if progress_callback:
                progress_callback(stage, pct, msg)

        # 1. Container & Streams Probing (10%)
        update_prog("Probing", 10, f"Probing container and codecs for {file_name}...")
        probe_data = self.prober.probe(file_path)
        container_info = probe_data["container"]
        video_streams: List[StreamInfo] = probe_data["video_streams"]
        audio_streams: List[StreamInfo] = probe_data["audio_streams"]
        subtitle_streams: List[StreamInfo] = probe_data["subtitle_streams"]
        duration = container_info["duration"]
        primary_fps = video_streams[0].fps if video_streams else 24.0

        all_issues: List[QCIssue] = []

        # 2. Container Rule Verification (20%)
        update_prog("Container QC", 20, "Validating container packaging and tracks...")
        all_issues.extend(validator.validate_container(file_path, container_info))

        # 3. Video Stream Parameters Verification (35%)
        update_prog("Video QC", 35, "Validating video codec, scan type, resolution, and color tags...")
        for v in video_streams:
            all_issues.extend(validator.validate_video_stream(v, duration))

        # 4. Audio Stream Metadata Verification (45%)
        update_prog("Audio QC", 45, "Validating audio sample rate, channels, and bit depth...")
        all_issues.extend(validator.validate_audio_stream(audio_streams, duration))

        # 5. Deep Audio & Loudness Inspection (70%)
        update_prog("Audio Loudness", 60, "Running ITU-R BS.1770-4 EBU R128 Loudness and phase analysis...")
        audio_analysis_data = {}
        if audio_streams:
            audio_analysis_data = self.audio_analyzer.analyze(file_path, duration, primary_fps)
            loudness_issues = validator.validate_loudness(audio_analysis_data.get("loudness", {}))
            all_issues.extend(loudness_issues)

            # Phase check
            phase = audio_analysis_data.get("phase", {})
            if phase.get("anti_phase_detected"):
                all_issues.append(QCIssue(
                    id="AUD-PHASE-001",
                    severity=Severity.WARNING,
                    stream_type=StreamType.AUDIO,
                    parameter="Stereo Phase Correlation",
                    measured_value=f"Mean: {phase.get('mean_phase', 0):.2f}, Min: {phase.get('min_phase', 0):.2f}",
                    expected_value="Phase Correlation > 0.0",
                    description="Anti-phase components detected between channels. Mono downmix will suffer cancellation.",
                    remediation_tip="Check stereo pan balance and correct out-of-phase audio components in mix."
                ))
            else:
                all_issues.append(QCIssue(
                    id="AUD-PHASE-001",
                    severity=Severity.PASS,
                    stream_type=StreamType.AUDIO,
                    parameter="Stereo Phase Correlation",
                    measured_value=f"Mean: {phase.get('mean_phase', 0.85):.2f}",
                    expected_value="Phase Correlation > 0.0",
                    description="Audio phase correlation is positive and mono-compatible.",
                    remediation_tip="No action required."
                ))

            # Dual Mono check
            if phase.get("dual_mono_detected") and len(audio_streams) > 0 and audio_streams[0].channels == 2:
                all_issues.append(QCIssue(
                    id="AUD-DUALMONO-001",
                    severity=Severity.NOTICE,
                    stream_type=StreamType.AUDIO,
                    parameter="Stereo Channel Content",
                    measured_value="Dual Mono (Identical L/R)",
                    expected_value="True Stereo or Flagged Dual-Mono",
                    description="Audio track is flagged as stereo but contains identical audio on Left and Right channels.",
                    remediation_tip="Deliver true stereo mix or tag track as Dual Mono."
                ))

            # Silence Check
            silences = audio_analysis_data.get("silences", [])
            for s in silences:
                if s["is_start"] and s["duration"] > profile.get("max_silence_sec", 2.0):
                    all_issues.append(QCIssue(
                        id="AUD-SILENCE-START",
                        severity=Severity.FAIL if profile.get("require_clean_master", True) else Severity.WARNING,
                        stream_type=StreamType.AUDIO,
                        parameter="Head Audio Silence",
                        measured_value=f"{s['duration']:.2f}s leading silence",
                        expected_value=f"<= {profile.get('max_silence_sec', 2.0)}s",
                        description=f"Long silence at start of asset ({s['duration']:.2f}s). Asset must start cleanly.",
                        remediation_tip="Trim head audio to start cleanly with program video."
                    ))

        # 6. Video Signal Integrity & Artifacts (85%)
        update_prog("Signal Integrity", 80, "Checking black frames, frozen sequences, and gamut limits...")
        artifact_analysis_data = {}
        if video_streams:
            artifact_analysis_data = self.artifact_analyzer.analyze(file_path, duration, primary_fps)
            # Evaluate Black frames
            for b in artifact_analysis_data.get("black_frames", []):
                if b["type"] == "leading" and b["duration"] > profile.get("max_leading_black_sec", 2.0):
                    all_issues.append(QCIssue(
                        id="ART-BLK-HEAD",
                        severity=Severity.FAIL,
                        stream_type=StreamType.INTEGRITY,
                        parameter="Leading Black Frames",
                        measured_value=f"{b['duration']:.2f}s black",
                        expected_value=f"<= {profile.get('max_leading_black_sec', 2.0)}s",
                        description=f"Asset contains {b['duration']:.2f}s of black frames before program start.",
                        remediation_tip="Trim initial black frames to program first active frame."
                    ))
                elif b["type"] == "trailing" and b["duration"] > profile.get("max_trailing_black_sec", 5.0):
                    all_issues.append(QCIssue(
                        id="ART-BLK-TAIL",
                        severity=Severity.WARNING,
                        stream_type=StreamType.INTEGRITY,
                        parameter="Trailing Black Frames",
                        measured_value=f"{b['duration']:.2f}s black",
                        expected_value=f"<= {profile.get('max_trailing_black_sec', 5.0)}s",
                        description=f"Asset ends with {b['duration']:.2f}s of black frames.",
                        remediation_tip="Trim trailing black to maximum 2-5 seconds."
                    ))

            # Freeze frames
            for fz in artifact_analysis_data.get("freeze_frames", []):
                if fz["duration"] > profile.get("max_freeze_frame_sec", 3.0):
                    all_issues.append(QCIssue(
                        id="ART-FRZ-001",
                        severity=Severity.WARNING,
                        stream_type=StreamType.INTEGRITY,
                        parameter="Freeze Frame Sequence",
                        measured_value=f"{fz['duration']:.2f}s static",
                        expected_value=f"<= {profile.get('max_freeze_frame_sec', 3.0)}s",
                        description=f"Static freeze frame detected from {fz['start']:.2f}s to {fz['end']:.2f}s.",
                        remediation_tip="Inspect timeline for video dropouts or unintentional static holds."
                    ))

            # Gamut
            gamut = artifact_analysis_data.get("gamut", {})
            if gamut.get("illegal_luma_detected"):
                all_issues.append(QCIssue(
                    id="ART-GAMUT-001",
                    severity=Severity.WARNING,
                    stream_type=StreamType.INTEGRITY,
                    parameter="Broadcast Gamut (IRE Luma)",
                    measured_value=f"YMin: {gamut.get('ymin', 0)}, YMax: {gamut.get('ymax', 255)}",
                    expected_value="Legal Range: Y [16 - 235] in 8-bit / [64 - 940] in 10-bit",
                    description="Out-of-gamut luma levels detected exceeding legal broadcast limits.",
                    remediation_tip="Apply broadcast-safe legal limiter or adjust contrast in color grading."
                ))
            else:
                all_issues.append(QCIssue(
                    id="ART-GAMUT-001",
                    severity=Severity.PASS,
                    stream_type=StreamType.INTEGRITY,
                    parameter="Broadcast Gamut (IRE Luma)",
                    measured_value=f"YMin: {gamut.get('ymin', 16)}, YMax: {gamut.get('ymax', 235)} (Legal)",
                    expected_value="Legal Range",
                    description="Video luma and chroma are within broadcast safe legal range.",
                    remediation_tip="No action required."
                ))

        # 7. Subtitles QC (92%)
        if sidecar_subtitle_path:
            update_prog("Subtitles QC", 92, "Validating subtitle sidecar timings and rules...")
            sub_issues = self.subtitle_analyzer.analyze_file(sidecar_subtitle_path, primary_fps)
            all_issues.extend(sub_issues)

        # 8. Verdict & Score Calculation (100%)
        update_prog("Finalizing", 98, "Calculating Amazon Prime compliance verdict...")
        fail_count = len([i for i in all_issues if i.severity == Severity.FAIL])
        warning_count = len([i for i in all_issues if i.severity == Severity.WARNING])

        if fail_count > 0:
            verdict = Severity.FAIL
            score = max(0.0, 100.0 - (fail_count * 20.0 + warning_count * 5.0))
        elif warning_count > 0:
            verdict = Severity.WARNING
            score = max(70.0, 100.0 - (warning_count * 5.0))
        else:
            verdict = Severity.PASS
            score = 100.0

        elapsed = time.time() - start_time
        update_prog("Complete", 100, f"QC Analysis Complete in {elapsed:.2f}s! Verdict: {verdict.value}")

        report = QCReportData(
            file_path=file_path,
            file_name=file_name,
            file_size_bytes=container_info.get("size", os.path.getsize(file_path)),
            duration_sec=duration,
            profile_name=profile_name,
            verdict=verdict,
            compliance_score=score,
            issues=all_issues,
            container_info=container_info,
            video_streams=video_streams,
            audio_streams=audio_streams,
            subtitle_streams=subtitle_streams,
            loudness_data=audio_analysis_data.get("loudness", {}),
            phase_correlation_data=audio_analysis_data.get("phase", {}),
            artifacts_data=artifact_analysis_data,
            analysis_duration_sec=elapsed
        )

        return report


QCAnalyzer = PrimeQCAnalyzer
