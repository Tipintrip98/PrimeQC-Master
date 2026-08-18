"""
Application configuration and user profile settings manager.
"""

import os
import json
from typing import Dict, Any, Optional
from .constants import ProfileType, PRIME_PROFILES


class AppConfig:
    """Manages application settings and custom profile overrides."""

    def __init__(self):
        self.app_data_dir = os.path.join(
            os.getenv("APPDATA", os.path.expanduser("~")),
            "PrimeQC_Master"
        )
        os.makedirs(self.app_data_dir, exist_ok=True)
        self.config_path = os.path.join(self.app_data_dir, "config.json")
        self.profiles_path = os.path.join(self.app_data_dir, "custom_profiles.json")
        
        self.settings: Dict[str, Any] = {
            "default_profile": ProfileType.PVD_HD.value,
            "export_dir": os.path.join(os.path.expanduser("~"), "Documents", "PrimeQC_Reports"),
            "auto_export_pdf": False,
            "auto_export_json": False,
            "theme": "dark",
            "threads": 4,
            "deep_analysis": True,  # Full EBU R128, silence, black, PSE scan
            "fast_mode_sample_sec": 0  # 0 means full deep pass
        }
        self.custom_profiles: Dict[str, Dict[str, Any]] = {}
        
        self.load()

    def load(self):
        """Loads configuration and custom profiles from disk."""
        if os.path.isfile(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.settings.update(data)
            except Exception:
                pass

        if os.path.isfile(self.profiles_path):
            try:
                with open(self.profiles_path, "r", encoding="utf-8") as f:
                    self.custom_profiles = json.load(f)
            except Exception:
                pass

    def save(self):
        """Saves configuration and custom profiles to disk."""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
            with open(self.profiles_path, "w", encoding="utf-8") as f:
                json.dump(self.custom_profiles, f, indent=2)
        except Exception:
            pass

    def get_profile(self, profile_name: str) -> Dict[str, Any]:
        """Returns standard Prime profile or custom profile by name."""
        if profile_name in PRIME_PROFILES:
            return PRIME_PROFILES[profile_name]
        for k, v in PRIME_PROFILES.items():
            if v.get("name") == profile_name:
                return v
        if profile_name in self.custom_profiles:
            return self.custom_profiles[profile_name]
        return PRIME_PROFILES[ProfileType.PVD_HD]

    def get_all_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Returns merged dictionary of standard and custom profiles."""
        merged = {k.value: v for k, v in PRIME_PROFILES.items()}
        merged.update(self.custom_profiles)
        return merged
