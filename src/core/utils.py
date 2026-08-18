"""
Utility functions for Amazon Prime QC Engine:
- Broadcast Timecode math (SMPTE HH:MM:SS:FF)
- Binary path resolution for bundled executables
- Signal processing and math helpers
- Formatting functions
"""

import os
import sys
import math
import shutil
from typing import Optional, Tuple


def get_base_dir() -> str:
    """Returns application base directory whether running in source or PyInstaller bundle."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS  # type: ignore
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def get_binary_path(binary_name: str) -> str:
    """
    Finds the executable binary (ffmpeg.exe or ffprobe.exe).
    Checks:
    1. PyInstaller bundled dir (_MEIPASS / bin)
    2. Local workspace 'bin' folder
    3. System PATH
    """
    base_dir = get_base_dir()
    
    # 1. Bundled bin folder
    candidate_1 = os.path.join(base_dir, "bin", f"{binary_name}.exe")
    if os.path.isfile(candidate_1):
        return candidate_1
    
    candidate_1_noext = os.path.join(base_dir, "bin", binary_name)
    if os.path.isfile(candidate_1_noext):
        return candidate_1_noext

    # 2. Local workspace bin folder
    candidate_2 = os.path.abspath(os.path.join(os.getcwd(), "bin", f"{binary_name}.exe"))
    if os.path.isfile(candidate_2):
        return candidate_2

    # 3. System PATH
    found = shutil.which(binary_name)
    if found:
        return found

    # 4. Fallback for imageio-ffmpeg if ffmpeg requested
    if binary_name == "ffmpeg":
        try:
            import imageio_ffmpeg
            return imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            pass

    return f"{binary_name}.exe"


def seconds_to_timecode(seconds: float, fps: float = 24.0, drop_frame: bool = False) -> str:
    """
    Converts floating point seconds to SMPTE timecode (HH:MM:SS:FF or HH:MM:SS;FF).
    """
    if seconds is None or math.isnan(seconds) or seconds < 0:
        return "00:00:00:00"
    
    fps = max(1.0, fps)
    total_frames = int(round(seconds * fps))
    
    if drop_frame and (abs(fps - 29.97) < 0.01 or abs(fps - 59.94) < 0.01):
        # Drop frame calculation
        drop_frames = 2 if fps < 40 else 4
        frames_per_minute = int(round(fps * 60))
        frames_per_10min = frames_per_minute * 10 - drop_frames * 9
        
        d = total_frames // frames_per_10min
        m = total_frames % frames_per_10min
        
        if m > drop_frames:
            total_frames += drop_frames * 9 * d + drop_frames * ((m - drop_frames) // (frames_per_minute - drop_frames))
        else:
            total_frames += drop_frames * 9 * d
        
        delimiter = ";"
    else:
        delimiter = ":"

    int_fps = int(round(fps))
    frames = total_frames % int_fps
    total_seconds = total_frames // int_fps
    secs = total_seconds % 60
    total_minutes = total_seconds // 60
    mins = total_minutes % 60
    hours = total_minutes // 60

    return f"{hours:02d}:{mins:02d}:{secs:02d}{delimiter}{frames:02d}"


def timecode_to_seconds(tc: str, fps: float = 24.0) -> float:
    """
    Converts timecode string (HH:MM:SS:FF or HH:MM:SS;FF or HH:MM:SS.mmm) to seconds.
    """
    if not tc or not isinstance(tc, str):
        return 0.0
    
    tc = tc.strip().replace(";", ":")
    parts = tc.split(":")
    
    if len(parts) == 4:
        try:
            h = int(parts[0])
            m = int(parts[1])
            s = int(parts[2])
            f = int(parts[3])
            return h * 3600 + m * 60 + s + (f / max(1.0, fps))
        except ValueError:
            return 0.0
    elif len(parts) == 3:
        try:
            h = int(parts[0])
            m = int(parts[1])
            s = float(parts[2])
            return h * 3600 + m * 60 + s
        except ValueError:
            return 0.0
    return 0.0


def frame_to_timecode(frame: int, fps: float = 24.0) -> str:
    """Converts a frame number to SMPTE timecode."""
    if frame is None or frame < 0:
        return "00:00:00:00"
    seconds = frame / max(1.0, fps)
    return seconds_to_timecode(seconds, fps)


def format_bytes(num_bytes: int) -> str:
    """Formats bytes into readable string (e.g., 2.45 GB)."""
    if num_bytes is None:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:3.2f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} PB"


def format_bitrate(bps: float) -> str:
    """Formats bits per second into Mbps or kbps."""
    if bps is None or bps <= 0:
        return "N/A"
    mbps = bps / 1_000_000.0
    if mbps >= 1.0:
        return f"{mbps:.2f} Mbps"
    kbps = bps / 1_000.0
    return f"{kbps:.1f} kbps"


def parse_fps(fps_str: str) -> float:
    """Parses fractional or float FPS string (e.g., '24000/1001' -> 23.976)."""
    if not fps_str:
        return 24.0
    try:
        if "/" in str(fps_str):
            num, den = str(fps_str).split("/")
            den_val = float(den)
            if den_val == 0:
                return 24.0
            return round(float(num) / den_val, 3)
        return round(float(fps_str), 3)
    except Exception:
        return 24.0


def sanitize_filename(name: str) -> str:
    """Sanitizes filename removing illegal characters."""
    for ch in ['<', '>', ':', '"', '/', '\\', '|', '?', '*']:
        name = name.replace(ch, '_')
    return name
