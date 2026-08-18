"""
Amazon Prime Video Quality Control - Specifications & Standards Constants
Covers Prime Video Direct (PVD) and Amazon Studios / Video Central Partner specifications.
"""

from enum import Enum
from typing import Dict, List, Any


class ProfileType(str, Enum):
    PVD_HD = "Prime Video Direct - HD Mezzanine"
    PVD_4K = "Prime Video Direct - 4K UHD Mezzanine"
    STUDIOS_SDR = "Amazon Studios - Broadcast Mezzanine SDR"
    STUDIOS_HDR = "Amazon Studios - Master Mezzanine HDR10 / Dolby Vision"
    TRAILER = "Amazon Prime - Trailer & Short Promo"
    CUSTOM = "Custom Prime Profile"


class Severity(str, Enum):
    PASS = "PASS"
    NOTICE = "NOTICE"
    WARNING = "WARNING"
    FAIL = "FAIL"


class StreamType(str, Enum):
    CONTAINER = "Container"
    VIDEO = "Video"
    AUDIO = "Audio"
    SUBTITLE = "Subtitle"
    INTEGRITY = "Signal Integrity"


# Allowed Frame Rates for Amazon Prime Delivery (CFR only)
AMAZON_ALLOWED_FPS = [
    23.976,
    24.0,
    25.0,
    29.97,
    30.0,
    50.0,
    59.94,
    60.0
]

# Audio Channel Configurations
CHANNEL_LAYOUTS = {
    1: "1.0 Mono (C)",
    2: "2.0 Stereo (L, R)",
    6: "5.1 Surround (L, R, C, LFE, Ls, Rs)",
    8: "8.0 Discrete (5.1 + Stereo L/R)"
}

# Profile Standards Definitions
PRIME_PROFILES: Dict[str, Dict[str, Any]] = {
    ProfileType.PVD_HD: {
        "name": ProfileType.PVD_HD.value,
        "description": "Amazon Prime Video Direct HD delivery profile for self-publishing.",
        "allowed_containers": [".mov", ".mp4", ".ts", ".m2ts"],
        "preferred_containers": [".mov"],
        "allowed_video_codecs": [
            "prores", "prores_ks", "apch", "apcn", "apcs", "apco",  # ProRes 422 HQ / 422
            "h264", "avc", "avc1",
            "mpeg2video", "mpgv"
        ],
        "allowed_audio_codecs": ["pcm_s24le", "pcm_s16le", "pcm_s24be", "pcm_s16be", "aac"],
        "allowed_resolutions": [
            (1920, 1080),
            (1280, 720)
        ],
        "allow_4k": False,
        "scan_type": "progressive",  # Interlaced / telecine is strictly rejected
        "min_video_bitrate_mbps": {
            "prores": 175.0,
            "h264": 15.0,
            "mpeg2video": 50.0
        },
        "color_primaries": ["bt709", "unknown", "unspecified"],
        "matrix_coefficients": ["bt709", "unknown", "unspecified"],
        "transfer_characteristics": ["bt709", "srgb", "unknown", "unspecified"],
        "color_range": ["tv", "limited"],
        "audio_sample_rates": [48000],
        "audio_bit_depths": [16, 24],
        "allowed_audio_channels": [1, 2, 6, 8],
        # Loudness Requirements (ITU-R BS.1770-4 / EBU R128)
        "loudness_target_lufs": -24.0,
        "loudness_tolerance_lu": 2.0,       # -26.0 to -22.0 LUFS
        "true_peak_max_dbtp": -2.0,         # Maximum ceiling -2.0 dBTP
        "max_lra_lu": 20.0,
        "min_lra_lu": 4.0,
        "max_short_term_lufs": -18.0,
        # Integrity Constraints
        "max_leading_black_sec": 2.0,
        "max_trailing_black_sec": 5.0,
        "max_mid_black_sec": 1.0,
        "max_freeze_frame_sec": 3.0,
        "max_silence_sec": 2.0,
        "max_av_sync_diff_sec": 0.1,        # 100ms / 2 frames max duration delta
        "require_clean_master": True,       # No slates, bars & tone
        "pse_flash_limit_hz": 3.0           # Photosensitive Epilepsy limit
    },
    ProfileType.PVD_4K: {
        "name": ProfileType.PVD_4K.value,
        "description": "Amazon Prime Video Direct 4K UHD Mezzanine delivery profile.",
        "allowed_containers": [".mov", ".mp4"],
        "preferred_containers": [".mov"],
        "allowed_video_codecs": [
            "prores", "prores_ks", "apch", "ap4h",  # ProRes 422 HQ / 4444
            "h264", "avc", "avc1",
            "hevc", "h265", "hev1", "hvc1"
        ],
        "allowed_audio_codecs": ["pcm_s24le", "pcm_s16le", "aac"],
        "allowed_resolutions": [
            (3840, 2160),
            (4096, 2160)
        ],
        "allow_4k": True,
        "scan_type": "progressive",
        "min_video_bitrate_mbps": {
            "prores": 700.0,
            "h264": 40.0,
            "hevc": 35.0
        },
        "color_primaries": ["bt2020", "bt709", "unknown", "unspecified"],
        "matrix_coefficients": ["bt2020nc", "bt2020c", "bt709", "unknown", "unspecified"],
        "transfer_characteristics": ["smpte2084", "arib-std-b67", "bt709", "unknown", "unspecified"],
        "color_range": ["tv", "limited"],
        "audio_sample_rates": [48000],
        "audio_bit_depths": [16, 24],
        "allowed_audio_channels": [2, 6, 8],
        "loudness_target_lufs": -24.0,
        "loudness_tolerance_lu": 2.0,
        "true_peak_max_dbtp": -2.0,
        "max_lra_lu": 20.0,
        "min_lra_lu": 4.0,
        "max_short_term_lufs": -18.0,
        "max_leading_black_sec": 2.0,
        "max_trailing_black_sec": 5.0,
        "max_mid_black_sec": 1.0,
        "max_freeze_frame_sec": 3.0,
        "max_silence_sec": 2.0,
        "max_av_sync_diff_sec": 0.1,
        "require_clean_master": True,
        "pse_flash_limit_hz": 3.0
    },
    ProfileType.STUDIOS_SDR: {
        "name": ProfileType.STUDIOS_SDR.value,
        "description": "Amazon Studios & Original Content Partner delivery (HD/UHD SDR Mezzanine).",
        "allowed_containers": [".mov", ".mxf"],
        "preferred_containers": [".mov", ".mxf"],
        "allowed_video_codecs": [
            "prores", "prores_ks", "apch",  # Apple ProRes 422 HQ
            "jpeg2000", "dnxhd", "dnxhr"
        ],
        "allowed_audio_codecs": ["pcm_s24le", "pcm_s24be"],  # Uncompressed 24-bit discrete LPCM only
        "allowed_resolutions": [
            (1920, 1080),
            (3840, 2160),
            (4096, 2160)
        ],
        "allow_4k": True,
        "scan_type": "progressive",
        "min_video_bitrate_mbps": {
            "prores": 180.0
        },
        "color_primaries": ["bt709"],
        "matrix_coefficients": ["bt709"],
        "transfer_characteristics": ["bt709"],
        "color_range": ["tv", "limited"],
        "audio_sample_rates": [48000],
        "audio_bit_depths": [24],       # Strict 24-bit
        "allowed_audio_channels": [6, 8], # Strict 5.1 or 8-Channel Layout
        "loudness_target_lufs": -24.0,
        "loudness_tolerance_lu": 1.0,   # Strict ±1.0 LU
        "true_peak_max_dbtp": -2.0,
        "max_lra_lu": 18.0,
        "min_lra_lu": 5.0,
        "max_short_term_lufs": -18.0,
        "max_leading_black_sec": 0.5,   # Exact program start
        "max_trailing_black_sec": 2.0,
        "max_mid_black_sec": 0.5,
        "max_freeze_frame_sec": 2.0,
        "max_silence_sec": 1.5,
        "max_av_sync_diff_sec": 0.04,   # 1 frame tolerance (~40ms)
        "require_clean_master": True,
        "pse_flash_limit_hz": 3.0
    },
    ProfileType.STUDIOS_HDR: {
        "name": ProfileType.STUDIOS_HDR.value,
        "description": "Amazon Studios HDR10 / Dolby Vision Master Mezzanine Delivery.",
        "allowed_containers": [".mov", ".mxf"],
        "preferred_containers": [".mov", ".mxf"],
        "allowed_video_codecs": [
            "prores", "prores_ks", "ap4x", "ap4h",  # Apple ProRes 4444 XQ / 4444
            "jpeg2000"
        ],
        "allowed_audio_codecs": ["pcm_s24le", "pcm_s24be"],
        "allowed_resolutions": [
            (3840, 2160),
            (4096, 2160)
        ],
        "allow_4k": True,
        "scan_type": "progressive",
        "min_video_bitrate_mbps": {
            "prores": 1000.0
        },
        "color_primaries": ["bt2020"],
        "matrix_coefficients": ["bt2020nc", "bt2020c"],
        "transfer_characteristics": ["smpte2084", "arib-std-b67"],  # PQ ST.2084 or HLG
        "color_range": ["tv", "limited", "pc", "full"],
        "audio_sample_rates": [48000],
        "audio_bit_depths": [24],
        "allowed_audio_channels": [6, 8],
        "loudness_target_lufs": -24.0,
        "loudness_tolerance_lu": 1.0,
        "true_peak_max_dbtp": -2.0,
        "max_lra_lu": 18.0,
        "min_lra_lu": 5.0,
        "max_short_term_lufs": -18.0,
        "max_leading_black_sec": 0.5,
        "max_trailing_black_sec": 2.0,
        "max_mid_black_sec": 0.5,
        "max_freeze_frame_sec": 2.0,
        "max_silence_sec": 1.5,
        "max_av_sync_diff_sec": 0.04,
        "require_clean_master": True,
        "pse_flash_limit_hz": 3.0
    },
    ProfileType.TRAILER: {
        "name": ProfileType.TRAILER.value,
        "description": "Amazon Prime Trailer and Short Promotional Video Delivery.",
        "allowed_containers": [".mov", ".mp4"],
        "preferred_containers": [".mov"],
        "allowed_video_codecs": [
            "prores", "prores_ks", "apch", "apcn",
            "h264", "avc", "avc1"
        ],
        "allowed_audio_codecs": ["pcm_s24le", "pcm_s16le", "aac"],
        "allowed_resolutions": [
            (1920, 1080),
            (3840, 2160)
        ],
        "allow_4k": True,
        "scan_type": "progressive",
        "min_video_bitrate_mbps": {
            "prores": 175.0,
            "h264": 20.0
        },
        "color_primaries": ["bt709", "bt2020", "unknown", "unspecified"],
        "matrix_coefficients": ["bt709", "bt2020nc", "unknown", "unspecified"],
        "transfer_characteristics": ["bt709", "smpte2084", "unknown", "unspecified"],
        "color_range": ["tv", "limited"],
        "audio_sample_rates": [48000],
        "audio_bit_depths": [16, 24],
        "allowed_audio_channels": [2, 6],
        "loudness_target_lufs": -24.0,
        "loudness_tolerance_lu": 1.5,
        "true_peak_max_dbtp": -2.0,
        "max_lra_lu": 16.0,
        "min_lra_lu": 3.0,
        "max_short_term_lufs": -16.0,
        "max_leading_black_sec": 0.2,
        "max_trailing_black_sec": 1.5,
        "max_mid_black_sec": 0.5,
        "max_freeze_frame_sec": 1.5,
        "max_silence_sec": 1.0,
        "max_av_sync_diff_sec": 0.05,
        "require_clean_master": True,
        "pse_flash_limit_hz": 3.0
    }
}
