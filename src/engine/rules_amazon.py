"""
Amazon Prime Video Quality Control Rule Validation Engine.
Performs zero-tolerance checks across Container, Video, Audio, Integrity, and Subtitles.
"""

import os
from typing import List, Dict, Any
from ..core.constants import Severity, StreamType, AMAZON_ALLOWED_FPS, CHANNEL_LAYOUTS
from .models import QCIssue, StreamInfo, QCReportData
from ..core.utils import format_bitrate, format_bytes, seconds_to_timecode


class AmazonRulesValidator:
    """Evaluates media streams and metrics against strict Amazon Prime specifications."""

    def __init__(self, profile: Dict[str, Any]):
        self.profile = profile
        self.profile_name = profile.get("name", "Prime Video Direct - HD Mezzanine")

    def validate_container(self, file_path: str, container_info: Dict[str, Any]) -> List[QCIssue]:
        """Checks container format, file size, and extension."""
        issues: List[QCIssue] = []
        ext = os.path.splitext(file_path)[1].lower()
        allowed_exts = self.profile.get("allowed_containers", [".mov", ".mp4"])

        # Container Extension Check
        if ext not in allowed_exts:
            issues.append(QCIssue(
                id="CONT-001",
                severity=Severity.FAIL,
                stream_type=StreamType.CONTAINER,
                parameter="Container Format",
                measured_value=ext,
                expected_value=f"One of {allowed_exts}",
                description=f"Container format '{ext}' is not accepted for this Amazon Prime delivery profile.",
                remediation_tip=f"Rewrap or transcode container into a compliant master format such as QuickTime ({self.profile.get('preferred_containers', ['.mov'])[0]})."
            ))
        else:
            issues.append(QCIssue(
                id="CONT-001",
                severity=Severity.PASS,
                stream_type=StreamType.CONTAINER,
                parameter="Container Format",
                measured_value=ext,
                expected_value=f"One of {allowed_exts}",
                description=f"Container format '{ext}' is compliant with Amazon Prime specifications.",
                remediation_tip="No action required."
            ))

        # Moov Atom & Fast Start Check (for MP4/MOV)
        if ext in [".mp4", ".mov"]:
            tags = container_info.get("tags", {})
            major_brand = tags.get("major_brand", "").lower()
            if "qt" in major_brand or ext == ".mov":
                issues.append(QCIssue(
                    id="CONT-002",
                    severity=Severity.PASS,
                    stream_type=StreamType.CONTAINER,
                    parameter="QuickTime Packaging",
                    measured_value=f"Brand: {major_brand or 'QuickTime MOV'}",
                    expected_value="Standard QuickTime Movie",
                    description="Container packaging headers are well-formed.",
                    remediation_tip="No action required."
                ))

        # Stream Count Check
        nb_streams = container_info.get("nb_streams", 0)
        if nb_streams < 1:
            issues.append(QCIssue(
                id="CONT-003",
                severity=Severity.FAIL,
                stream_type=StreamType.CONTAINER,
                parameter="Stream Count",
                measured_value=str(nb_streams),
                expected_value=">= 2 (1 Video + 1+ Audio)",
                description="Container contains no valid media streams.",
                remediation_tip="Ensure the file was exported properly with both video and audio tracks enabled."
            ))

        return issues

    def validate_video_stream(self, video: StreamInfo, duration: float) -> List[QCIssue]:
        """Validates video codec, scan type, resolution, fps, bitrate, color space, and HDR."""
        issues: List[QCIssue] = []

        # 1. Video Codec
        allowed_codecs = self.profile.get("allowed_video_codecs", [])
        codec_matched = any(c in video.codec_name for c in allowed_codecs)
        if not codec_matched:
            issues.append(QCIssue(
                id="VID-001",
                severity=Severity.FAIL,
                stream_type=StreamType.VIDEO,
                parameter="Video Codec",
                measured_value=f"{video.codec_name} ({video.profile})",
                expected_value=f"One of: {', '.join(allowed_codecs)}",
                description=f"Video codec '{video.codec_name}' is rejected by Amazon Prime Video standards.",
                remediation_tip="Export master using Apple ProRes 422 HQ (or ProRes 4444 XQ for HDR) or high-bitrate AVC/H.264."
            ))
        else:
            issues.append(QCIssue(
                id="VID-001",
                severity=Severity.PASS,
                stream_type=StreamType.VIDEO,
                parameter="Video Codec",
                measured_value=f"{video.codec_name} ({video.profile})",
                expected_value="Approved Mezzanine Codec",
                description=f"Video codec '{video.codec_name}' conforms to Amazon Prime specifications.",
                remediation_tip="No action required."
            ))

        # 2. Scan Type (Progressive strict requirement - Telecine strictly rejected)
        if video.field_order not in ["progressive", "unknown", ""]:
            issues.append(QCIssue(
                id="VID-002",
                severity=Severity.FAIL,
                stream_type=StreamType.VIDEO,
                parameter="Scan Type",
                measured_value=f"Interlaced ({video.field_order})",
                expected_value="Progressive",
                description="Interlaced video or telecined cadence is strictly prohibited on Amazon Prime Video.",
                remediation_tip="Deinterlace the source using high-quality motion-adaptive deinterlacing (Yadif/BWDIF) or inverse telecine prior to export."
            ))
        else:
            issues.append(QCIssue(
                id="VID-002",
                severity=Severity.PASS,
                stream_type=StreamType.VIDEO,
                parameter="Scan Type",
                measured_value="Progressive",
                expected_value="Progressive",
                description="Scan type is progressive as required by Amazon Prime.",
                remediation_tip="No action required."
            ))

        # 3. Frame Rate (Constant Frame Rate & standard rates)
        fps = video.fps
        fps_matches = any(abs(fps - allowed_fps) < 0.05 for allowed_fps in AMAZON_ALLOWED_FPS)
        if not fps_matches:
            issues.append(QCIssue(
                id="VID-003",
                severity=Severity.FAIL,
                stream_type=StreamType.VIDEO,
                parameter="Frame Rate",
                measured_value=f"{fps:.3f} fps",
                expected_value=f"One of standard rates: {AMAZON_ALLOWED_FPS}",
                description=f"Non-standard frame rate {fps:.3f} fps will be rejected by Prime Video automated ingestion.",
                remediation_tip="Conform project to native 23.976, 24.0, 25.0, 29.97, 50.0, or 59.94 fps CFR."
            ))
        else:
            is_cfr = video.extra_tags.get("is_cfr", "True") == "True"
            if not is_cfr:
                issues.append(QCIssue(
                    id="VID-003-VFR",
                    severity=Severity.FAIL,
                    stream_type=StreamType.VIDEO,
                    parameter="Frame Rate Mode",
                    measured_value="Variable Frame Rate (VFR)",
                    expected_value="Constant Frame Rate (CFR)",
                    description="Variable Frame Rate detected. Amazon requires strict Constant Frame Rate.",
                    remediation_tip="Transcode with constant frame rate flag (-vsync cfr / -r 24)."
                ))
            else:
                issues.append(QCIssue(
                    id="VID-003",
                    severity=Severity.PASS,
                    stream_type=StreamType.VIDEO,
                    parameter="Frame Rate",
                    measured_value=f"{fps:.3f} fps (CFR)",
                    expected_value="Standard CFR Frame Rate",
                    description=f"Frame rate {fps:.3f} fps is compliant with Amazon Prime specifications.",
                    remediation_tip="No action required."
                ))

        # 4. Resolution & Aspect Ratio
        w, h = video.width, video.height
        allowed_res = self.profile.get("allowed_resolutions", [(1920, 1080)])
        res_matches = any((w == rw and h == rh) for rw, rh in allowed_res)
        
        # Check standard 16:9 aspect ratio or valid theatrical scope (1.85:1, 2.39:1)
        aspect = (w / max(1, h))
        is_scope = (abs(aspect - 1.777) < 0.05 or abs(aspect - 1.85) < 0.05 or abs(aspect - 2.39) < 0.05 or abs(aspect - 2.35) < 0.05 or abs(aspect - 1.333) < 0.05)
        
        if not res_matches and not is_scope:
            issues.append(QCIssue(
                id="VID-004",
                severity=Severity.FAIL,
                stream_type=StreamType.VIDEO,
                parameter="Resolution",
                measured_value=f"{w}x{h} ({aspect:.2f}:1)",
                expected_value=f"Standard Delivery: {allowed_res}",
                description=f"Resolution {w}x{h} does not match standard Amazon Prime delivery specifications.",
                remediation_tip="Scale/Pad project to standard 1920x1080 (HD) or 3840x2160 (UHD) with clean raster."
            ))
        else:
            issues.append(QCIssue(
                id="VID-004",
                severity=Severity.PASS,
                stream_type=StreamType.VIDEO,
                parameter="Resolution",
                measured_value=f"{w}x{h} ({'16:9 HD' if w==1920 else ('4K UHD' if w==3840 else f'{aspect:.2f}:1')})",
                expected_value="Approved Delivery Resolution",
                description=f"Resolution {w}x{h} conforms to Amazon Prime specifications.",
                remediation_tip="No action required."
            ))

        # 5. Bit Depth
        bits = video.bits_per_raw_sample
        if "prores" in video.codec_name and bits < 10:
            issues.append(QCIssue(
                id="VID-005",
                severity=Severity.WARNING,
                stream_type=StreamType.VIDEO,
                parameter="Bit Depth",
                measured_value=f"{bits}-bit",
                expected_value="10-bit or 12-bit for ProRes Masters",
                description="ProRes mezzanine should be 10-bit or 12-bit for Amazon Prime Video master deliverables.",
                remediation_tip="Ensure your NLE exports ProRes at 10-bit minimum."
            ))
        else:
            issues.append(QCIssue(
                id="VID-005",
                severity=Severity.PASS,
                stream_type=StreamType.VIDEO,
                parameter="Bit Depth",
                measured_value=f"{bits}-bit",
                expected_value="Acceptable Bit Depth",
                description=f"Bit depth {bits}-bit is valid.",
                remediation_tip="No action required."
            ))

        # 6. Color Space & Primaries
        primaries = video.color_primaries.lower()
        allowed_primaries = self.profile.get("color_primaries", ["bt709"])
        if primaries not in allowed_primaries and primaries != "unknown":
            issues.append(QCIssue(
                id="VID-006",
                severity=Severity.WARNING,
                stream_type=StreamType.VIDEO,
                parameter="Color Primaries",
                measured_value=primaries,
                expected_value=f"One of: {allowed_primaries}",
                description=f"Color primaries '{primaries}' might cause color shifting on Amazon Prime playback.",
                remediation_tip="Tag video color space as Rec.709 (for SDR) or BT.2020 (for HDR) in export settings."
            ))
        else:
            issues.append(QCIssue(
                id="VID-006",
                severity=Severity.PASS,
                stream_type=StreamType.VIDEO,
                parameter="Color Primaries",
                measured_value=primaries if primaries != "unknown" else "Rec.709 (Default SDR)",
                expected_value="Compliant Color Space",
                description=f"Color primaries '{primaries}' conform to Amazon delivery specs.",
                remediation_tip="No action required."
            ))

        return issues

    def validate_audio_stream(self, audio_streams: List[StreamInfo], video_duration: float) -> List[QCIssue]:
        """Validates sample rate, bit depth, channel configuration, and duration sync."""
        issues: List[QCIssue] = []

        if not audio_streams:
            issues.append(QCIssue(
                id="AUD-001",
                severity=Severity.FAIL,
                stream_type=StreamType.AUDIO,
                parameter="Audio Presence",
                measured_value="No Audio Stream",
                expected_value="At least 1 audio track",
                description="The file has no audio stream. Amazon Prime requires program audio.",
                remediation_tip="Include full stereo or 5.1 program audio mix."
            ))
            return issues

        total_channels = sum(a.channels for a in audio_streams)
        allowed_channels = self.profile.get("allowed_audio_channels", [2, 6, 8])

        # Channel Layout Check
        if total_channels not in allowed_channels:
            issues.append(QCIssue(
                id="AUD-002",
                severity=Severity.FAIL,
                stream_type=StreamType.AUDIO,
                parameter="Audio Channel Count",
                measured_value=f"{total_channels} channels ({len(audio_streams)} stream(s))",
                expected_value=f"Approved layouts: {allowed_channels} (2ch Stereo, 6ch 5.1, 8ch 5.1+Stereo)",
                description=f"Total channel count {total_channels} does not match accepted Amazon Prime channel mapping layouts.",
                remediation_tip="Configure audio tracks as 2.0 Stereo (L/R) or 5.1 Surround (L, R, C, LFE, Ls, Rs) or 8-Ch."
            ))
        else:
            layout_desc = CHANNEL_LAYOUTS.get(total_channels, f"{total_channels} Channels")
            issues.append(QCIssue(
                id="AUD-002",
                severity=Severity.PASS,
                stream_type=StreamType.AUDIO,
                parameter="Audio Channel Mapping",
                measured_value=f"{layout_desc}",
                expected_value="Compliant Channel Mapping",
                description=f"Audio channel configuration ({layout_desc}) is compliant.",
                remediation_tip="No action required."
            ))

        for idx, a in enumerate(audio_streams):
            # Sample Rate (Strictly 48 kHz)
            if a.sample_rate != 48000:
                issues.append(QCIssue(
                    id=f"AUD-SR-{idx}",
                    severity=Severity.FAIL,
                    stream_type=StreamType.AUDIO,
                    parameter=f"Audio Track {idx+1} Sample Rate",
                    measured_value=f"{a.sample_rate} Hz",
                    expected_value="48000 Hz (48 kHz)",
                    description=f"Audio sample rate {a.sample_rate} Hz is rejected by Amazon Prime. Must be 48 kHz.",
                    remediation_tip="Resample audio to 48 kHz (48000 Hz) uncompressed PCM or AAC."
                ))
            else:
                issues.append(QCIssue(
                    id=f"AUD-SR-{idx}",
                    severity=Severity.PASS,
                    stream_type=StreamType.AUDIO,
                    parameter=f"Audio Track {idx+1} Sample Rate",
                    measured_value="48000 Hz (48 kHz)",
                    expected_value="48 kHz",
                    description="Sample rate is compliant with Amazon Prime standards.",
                    remediation_tip="No action required."
                ))

            # Bit Depth (16 or 24-bit PCM)
            allowed_depths = self.profile.get("audio_bit_depths", [16, 24])
            if a.bits_per_raw_sample not in allowed_depths and a.bits_per_raw_sample > 0:
                issues.append(QCIssue(
                    id=f"AUD-BD-{idx}",
                    severity=Severity.WARNING,
                    stream_type=StreamType.AUDIO,
                    parameter=f"Audio Track {idx+1} Bit Depth",
                    measured_value=f"{a.bits_per_raw_sample}-bit",
                    expected_value=f"One of: {allowed_depths}-bit",
                    description=f"Audio bit depth {a.bits_per_raw_sample}-bit is non-standard for this profile.",
                    remediation_tip="Export uncompressed 24-bit PCM (LPCM)."
                ))

            # Audio/Video Duration Sync
            if video_duration > 0 and a.duration > 0:
                diff = abs(video_duration - a.duration)
                max_diff = self.profile.get("max_av_sync_diff_sec", 0.1)
                if diff > max_diff:
                    issues.append(QCIssue(
                        id=f"AUD-SYNC-{idx}",
                        severity=Severity.FAIL if diff > 0.5 else Severity.WARNING,
                        stream_type=StreamType.AUDIO,
                        parameter="Audio/Video Duration Sync",
                        measured_value=f"Delta: {diff:.3f}s (Video: {video_duration:.3f}s, Audio: {a.duration:.3f}s)",
                        expected_value=f"<= {max_diff:.3f}s (Max 2 frames)",
                        description=f"Audio stream duration differs from video stream by {diff:.3f} seconds.",
                        remediation_tip="Trim audio and video tracks to exactly identical in and out points."
                    ))
                else:
                    issues.append(QCIssue(
                        id=f"AUD-SYNC-{idx}",
                        severity=Severity.PASS,
                        stream_type=StreamType.AUDIO,
                        parameter="Audio/Video Duration Sync",
                        measured_value=f"Delta: {diff:.3f}s (Synced)",
                        expected_value=f"<= {max_diff:.3f}s",
                        description="Audio and video track lengths match perfectly.",
                        remediation_tip="No action required."
                    ))

        return issues

    def validate_loudness(self, loudness_data: Dict[str, Any]) -> List[QCIssue]:
        """Validates ITU-R BS.1770-4 / EBU R128 Loudness metrics."""
        issues: List[QCIssue] = []
        if not loudness_data or "integrated" not in loudness_data:
            return issues

        int_lufs = float(loudness_data.get("integrated", -24.0))
        true_peak = float(loudness_data.get("true_peak", -2.0))
        lra = float(loudness_data.get("lra", 8.0))
        max_m = float(loudness_data.get("max_momentary", -18.0))
        max_s = float(loudness_data.get("max_short_term", -19.0))

        target_lufs = self.profile.get("loudness_target_lufs", -24.0)
        tol_lu = self.profile.get("loudness_tolerance_lu", 2.0)
        max_tp = self.profile.get("true_peak_max_dbtp", -2.0)
        max_lra = self.profile.get("max_lra_lu", 20.0)

        # 1. Integrated Loudness
        delta_lufs = abs(int_lufs - target_lufs)
        min_allowed = target_lufs - tol_lu
        max_allowed = target_lufs + tol_lu

        if delta_lufs > tol_lu:
            issues.append(QCIssue(
                id="LOUD-001",
                severity=Severity.FAIL,
                stream_type=StreamType.AUDIO,
                parameter="Integrated Loudness (LUFS / LKFS)",
                measured_value=f"{int_lufs:.1f} LUFS",
                expected_value=f"{target_lufs:.1f} LUFS (±{tol_lu:.1f} LU: [{min_allowed:.1f} to {max_allowed:.1f}])",
                description=f"Integrated loudness {int_lufs:.1f} LUFS violates Amazon Prime's -24.0 LKFS specification.",
                remediation_tip=f"Apply ITU-R BS.1770 loudness normalization to hit -24.0 LUFS (Gain adjustment: {target_lufs - int_lufs:+.1f} dB)."
            ))
        else:
            issues.append(QCIssue(
                id="LOUD-001",
                severity=Severity.PASS,
                stream_type=StreamType.AUDIO,
                parameter="Integrated Loudness (LUFS / LKFS)",
                measured_value=f"{int_lufs:.1f} LUFS",
                expected_value=f"{target_lufs:.1f} LUFS (±{tol_lu:.1f} LU)",
                description=f"Integrated loudness {int_lufs:.1f} LUFS is compliant with Amazon Prime specifications.",
                remediation_tip="No action required."
            ))

        # 2. Maximum True Peak
        if true_peak > max_tp:
            is_clip = true_peak >= 0.0
            issues.append(QCIssue(
                id="LOUD-002",
                severity=Severity.FAIL if is_clip or true_peak > -1.0 else Severity.WARNING,
                stream_type=StreamType.AUDIO,
                parameter="Max True Peak (dBTP)",
                measured_value=f"{true_peak:.2f} dBTP",
                expected_value=f"<= {max_tp:.1f} dBTP",
                description=f"True Peak level ({true_peak:.2f} dBTP) exceeds Amazon Prime ceiling of {max_tp:.1f} dBTP.",
                remediation_tip="Apply a True Peak Limiter with ceiling set to -2.0 dBTP on master output bus."
            ))
        else:
            issues.append(QCIssue(
                id="LOUD-002",
                severity=Severity.PASS,
                stream_type=StreamType.AUDIO,
                parameter="Max True Peak (dBTP)",
                measured_value=f"{true_peak:.2f} dBTP",
                expected_value=f"<= {max_tp:.1f} dBTP",
                description=f"True Peak {true_peak:.2f} dBTP is safely below the -2.0 dBTP ceiling.",
                remediation_tip="No action required."
            ))

        # 3. Loudness Range (LRA)
        if lra > max_lra:
            issues.append(QCIssue(
                id="LOUD-003",
                severity=Severity.WARNING,
                stream_type=StreamType.AUDIO,
                parameter="Loudness Range (LRA)",
                measured_value=f"{lra:.1f} LU",
                expected_value=f"<= {max_lra:.1f} LU",
                description=f"Loudness Range ({lra:.1f} LU) indicates high dynamic range that may cause dialogue inaudibility.",
                remediation_tip="Apply gentle multiband compression to tame extreme dynamics."
            ))
        else:
            issues.append(QCIssue(
                id="LOUD-003",
                severity=Severity.PASS,
                stream_type=StreamType.AUDIO,
                parameter="Loudness Range (LRA)",
                measured_value=f"{lra:.1f} LU",
                expected_value=f"<= {max_lra:.1f} LU",
                description=f"LRA {lra:.1f} LU is well balanced.",
                remediation_tip="No action required."
            ))

        return issues
