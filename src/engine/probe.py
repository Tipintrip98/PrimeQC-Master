"""
Container and Stream Prober for Video, Audio, and Metadata inspection.
Uses ffprobe/ffmpeg with resilient JSON and stream text parsing.
"""

import os
import re
import json
import subprocess
from typing import Dict, Any, List, Tuple, Optional
from .models import StreamInfo
from ..core.utils import get_binary_path, parse_fps


class MediaProber:
    """Probes media files for deep technical metadata."""

    def __init__(self):
        self.ffprobe_bin = get_binary_path("ffprobe")
        self.ffmpeg_bin = get_binary_path("ffmpeg")

    def probe(self, file_path: str) -> Dict[str, Any]:
        """
        Extracts complete container and stream information using ffprobe or ffmpeg fallback.
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Try ffprobe first if available
        if os.path.isfile(self.ffprobe_bin) or self.ffprobe_bin != "ffprobe.exe":
            result = self._probe_with_ffprobe(file_path)
            if result:
                return self._parse_probe_data(file_path, result)

        # Resilient ffmpeg fallback
        return self._probe_with_ffmpeg(file_path)

    def _probe_with_ffprobe(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Runs ffprobe with JSON output."""
        try:
            cmd = [
                self.ffprobe_bin,
                "-nostdin",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                "-show_chapters",
                "-show_error",
                file_path
            ]
            startupinfo = None
            creationflags = 0
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                creationflags = 0x08000000

            proc = subprocess.run(
                cmd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='ignore',
                startupinfo=startupinfo,
                creationflags=creationflags,
                timeout=30
            )

            if proc.returncode == 0 and proc.stdout.strip():
                return json.loads(proc.stdout)
        except Exception:
            pass
        return None

    def _probe_with_ffmpeg(self, file_path: str) -> Dict[str, Any]:
        """Fallback prober using ffmpeg -i stderr output."""
        cmd = [self.ffmpeg_bin, "-nostdin", "-hide_banner", "-i", file_path]
        startupinfo = None
        creationflags = 0
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            creationflags = 0x08000000

        proc = subprocess.run(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='ignore',
            startupinfo=startupinfo,
            creationflags=creationflags,
            timeout=30
        )
        return self._parse_ffmpeg_stderr(file_path, proc.stderr)


    def _parse_probe_data(self, file_path: str, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Processes raw ffprobe JSON into structured dictionary with StreamInfo models."""
        fmt = raw.get("format", {})
        streams = raw.get("streams", [])

        container_info = {
            "format_name": fmt.get("format_name", ""),
            "format_long_name": fmt.get("format_long_name", ""),
            "duration": float(fmt.get("duration", 0.0) or 0.0),
            "size": int(fmt.get("size", os.path.getsize(file_path)) or os.path.getsize(file_path)),
            "bitrate": int(fmt.get("bit_rate", 0) or 0),
            "nb_streams": int(fmt.get("nb_streams", len(streams))),
            "start_time": float(fmt.get("start_time", 0.0) or 0.0),
            "tags": fmt.get("tags", {})
        }

        video_streams: List[StreamInfo] = []
        audio_streams: List[StreamInfo] = []
        subtitle_streams: List[StreamInfo] = []

        for st in streams:
            c_type = st.get("codec_type", "").lower()
            idx = int(st.get("index", 0))
            c_name = st.get("codec_name", "").lower()
            c_long = st.get("codec_long_name", "")
            prof = st.get("profile", "")
            tags = st.get("tags", {})
            dur = float(st.get("duration", container_info["duration"]) or container_info["duration"])
            br = int(st.get("bit_rate", 0) or 0)

            if c_type == "video":
                w = int(st.get("width", 0) or 0)
                h = int(st.get("height", 0) or 0)
                r_fps = parse_fps(st.get("r_frame_rate", "24/1"))
                avg_fps = parse_fps(st.get("avg_frame_rate", str(r_fps)))
                fps = r_fps if r_fps > 0 else avg_fps

                pix_fmt = st.get("pix_fmt", "")
                bits = int(st.get("bits_per_raw_sample", 0) or 0)
                if bits <= 0:
                    if "12" in pix_fmt or "4444 xq" in prof.lower(): bits = 12
                    elif "10" in pix_fmt or "prores" in c_name: bits = 10
                    else: bits = 8

                field_order = st.get("field_order", "progressive")
                if field_order in ["unknown", "", None]:
                    field_order = "progressive"

                v_info = StreamInfo(
                    index=idx,
                    codec_type="video",
                    codec_name=c_name,
                    codec_long_name=c_long,
                    profile=prof,
                    width=w,
                    height=h,
                    fps=fps,
                    field_order=field_order,
                    pix_fmt=pix_fmt,
                    bits_per_raw_sample=bits,
                    bitrate=br,
                    duration=dur,
                    color_primaries=st.get("color_primaries", "unknown"),
                    color_space=st.get("color_space", "unknown"),
                    color_transfer=st.get("color_transfer", "unknown"),
                    color_range=st.get("color_range", "unknown"),
                    extra_tags=tags
                )
                v_info.extra_tags["sample_aspect_ratio"] = st.get("sample_aspect_ratio", "1:1")
                v_info.extra_tags["display_aspect_ratio"] = st.get("display_aspect_ratio", "16:9" if w==1920 or w==3840 else "")
                v_info.extra_tags["is_cfr"] = str(abs(r_fps - avg_fps) < 0.005)
                video_streams.append(v_info)

            elif c_type == "audio":
                sr = int(st.get("sample_rate", 48000) or 48000)
                channels = int(st.get("channels", 2) or 2)
                ch_layout = st.get("channel_layout", "")
                if not ch_layout:
                    if channels == 1: ch_layout = "mono"
                    elif channels == 2: ch_layout = "stereo"
                    elif channels == 6: ch_layout = "5.1(side)"
                    elif channels == 8: ch_layout = "7.1"
                    else: ch_layout = f"{channels} channels"

                bits = int(st.get("bits_per_sample", 0) or 0)
                if bits <= 0:
                    s_fmt = st.get("sample_fmt", "")
                    if "s32" in s_fmt or "32" in c_name: bits = 32
                    elif "s24" in s_fmt or "24" in c_name: bits = 24
                    elif "s16" in s_fmt or "16" in c_name: bits = 16
                    elif "flt" in s_fmt: bits = 32
                    else: bits = 24

                a_info = StreamInfo(
                    index=idx,
                    codec_type="audio",
                    codec_name=c_name,
                    codec_long_name=c_long,
                    profile=prof,
                    sample_rate=sr,
                    channels=channels,
                    channel_layout=ch_layout,
                    bits_per_raw_sample=bits,
                    bitrate=br,
                    duration=dur,
                    language=tags.get("language", "und"),
                    title=tags.get("title", ""),
                    extra_tags=tags
                )
                audio_streams.append(a_info)

            elif c_type == "subtitle":
                s_info = StreamInfo(
                    index=idx,
                    codec_type="subtitle",
                    codec_name=c_name,
                    codec_long_name=c_long,
                    duration=dur,
                    language=tags.get("language", "und"),
                    title=tags.get("title", ""),
                    extra_tags=tags
                )
                subtitle_streams.append(s_info)

        return {
            "container": container_info,
            "video_streams": video_streams,
            "audio_streams": audio_streams,
            "subtitle_streams": subtitle_streams,
            "raw": raw
        }

    def _parse_ffmpeg_stderr(self, file_path: str, stderr: str) -> Dict[str, Any]:
        """Deep fallback parser when ffprobe json is unavailable."""
        duration = 0.0
        bitrate = 0
        video_streams: List[StreamInfo] = []
        audio_streams: List[StreamInfo] = []
        subtitle_streams: List[StreamInfo] = []

        dur_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", stderr)
        if dur_match:
            h, m, s = dur_match.groups()
            duration = int(h) * 3600 + int(m) * 60 + float(s)

        br_match = re.search(r"bitrate:\s*(\d+)\s*kb/s", stderr)
        if br_match:
            bitrate = int(br_match.group(1)) * 1000

        # Find streams: Stream #0:0[0x1](und): Video: prores (HQ) (apch / 0x68637061), yuv422p10le(tv, progressive), 1920x1080 [SAR 1:1 DAR 16:9], 200 kb/s, 24 fps...
        stream_matches = re.finditer(r"Stream #\d+:(\d+)(?:\[0x[0-9a-fA-F]+\])?(?:\([a-zA-Z]+\))?: (Video|Audio|Subtitle): (.*)", stderr)
        for sm in stream_matches:
            idx = int(sm.group(1))
            st_type = sm.group(2).lower()
            details = sm.group(3)

            if st_type == "video":
                # Parse codec
                c_name = details.split(",")[0].strip().split(" ")[0].lower()
                profile = ""
                if "(" in details.split(",")[0]:
                    p_match = re.search(r"\(([^)]+)\)", details.split(",")[0])
                    if p_match:
                        profile = p_match.group(1)

                w, h = 1920, 1080
                res_m = re.search(r"(\d{3,4})x(\d{3,4})", details)
                if res_m:
                    w, h = int(res_m.group(1)), int(res_m.group(2))

                fps = 24.0
                fps_m = re.search(r"(\d+(?:\.\d+)?)\s*fps", details)
                if fps_m:
                    fps = float(fps_m.group(1))
                else:
                    tbr_m = re.search(r"(\d+(?:\.\d+)?)\s*tbr", details)
                    if tbr_m:
                        fps = float(tbr_m.group(1))

                # Field order
                field_order = "progressive"
                if "top coded first" in details or "tff" in details or "interlaced" in details:
                    field_order = "tt"
                elif "bottom coded first" in details or "bff" in details:
                    field_order = "bb"

                # Bit depth
                bits = 10 if ("10le" in details or "10be" in details or "10-bit" in details or "prores" in c_name) else (12 if "12" in details else 8)

                # Color space & primaries
                primaries = "bt709" if "bt709" in details else ("bt2020" if "bt2020" in details else "unknown")
                color_range = "tv" if "tv" in details else ("pc" if "pc" in details or "full" in details else "unknown")

                v_info = StreamInfo(
                    index=idx,
                    codec_type="video",
                    codec_name=c_name,
                    profile=profile,
                    width=w,
                    height=h,
                    fps=fps,
                    field_order=field_order,
                    bits_per_raw_sample=bits,
                    duration=duration,
                    color_primaries=primaries,
                    color_range=color_range
                )
                v_info.extra_tags["is_cfr"] = "True"
                video_streams.append(v_info)

            elif st_type == "audio":
                c_name = details.split(",")[0].strip().split(" ")[0].lower()
                sr = 48000
                sr_m = re.search(r"(\d+)\s*Hz", details)
                if sr_m:
                    sr = int(sr_m.group(1))

                channels = 2
                if "mono" in details: channels = 1
                elif "stereo" in details: channels = 2
                elif "5.1" in details: channels = 6
                elif "7.1" in details: channels = 8

                # Bits
                bits = 24
                if "s24" in details or "24 bit" in details or "in24" in details:
                    bits = 24
                elif "s16" in details or "16 bit" in details or "in16" in details:
                    bits = 16
                elif "s32" in details or "32 bit" in details or "fltp" in details:
                    bits = 24

                a_info = StreamInfo(
                    index=idx,
                    codec_type="audio",
                    codec_name=c_name,
                    sample_rate=sr,
                    channels=channels,
                    bits_per_raw_sample=bits,
                    duration=duration
                )
                audio_streams.append(a_info)

        container_info = {
            "format_name": os.path.splitext(file_path)[1].lower().replace(".", ""),
            "duration": duration,
            "size": os.path.getsize(file_path),
            "bitrate": bitrate,
            "nb_streams": len(video_streams) + len(audio_streams) + len(subtitle_streams),
            "start_time": 0.0,
            "tags": {}
        }

        return {
            "container": container_info,
            "video_streams": video_streams,
            "audio_streams": audio_streams,
            "subtitle_streams": subtitle_streams,
            "raw": {}
        }
