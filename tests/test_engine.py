"""
Unit tests for PrimeQC Amazon Prime Video Quality Control Engine.
"""

import os
import sys
import unittest

# Ensure src is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.constants import ProfileType, Severity, PRIME_PROFILES
from src.core.utils import seconds_to_timecode, timecode_to_seconds, parse_fps, format_bytes
from src.engine.models import StreamInfo, QCReportData, QCIssue
from src.engine.rules_amazon import AmazonRulesValidator
from src.engine.remediation import RemediationEngine
from src.reports.pdf_report import PDFReportExporter
from src.reports.json_manifest import JSONManifestExporter


class TestPrimeQC(unittest.TestCase):

    def test_timecode_math(self):
        """Test SMPTE timecode conversions."""
        self.assertEqual(seconds_to_timecode(0.0, 24.0), "00:00:00:00")
        self.assertEqual(seconds_to_timecode(1.0, 24.0), "00:00:01:00")
        self.assertEqual(seconds_to_timecode(3661.5, 24.0), "01:01:01:12")
        self.assertAlmostEqual(timecode_to_seconds("01:01:01:12", 24.0), 3661.5, places=2)
        self.assertEqual(parse_fps("24000/1001"), 23.976)
        self.assertEqual(format_bytes(1024 * 1024 * 500), "500.00 MB")

    def test_pvd_hd_video_rules(self):
        """Test Prime Video Direct HD video rules validation."""
        profile = PRIME_PROFILES[ProfileType.PVD_HD]
        validator = AmazonRulesValidator(profile)

        # 1. Compliant ProRes 422 HQ Progressive 1080p24
        v_good = StreamInfo(
            index=0,
            codec_type="video",
            codec_name="prores",
            profile="ProRes 422 HQ",
            width=1920,
            height=1080,
            fps=23.976,
            field_order="progressive",
            bits_per_raw_sample=10,
            bitrate=180_000_000,
            duration=100.0,
            color_primaries="bt709"
        )
        issues = validator.validate_video_stream(v_good, 100.0)
        fails = [i for i in issues if i.severity == Severity.FAIL]
        self.assertEqual(len(fails), 0, f"Expected 0 fails, got: {fails}")

        # 2. Non-compliant Interlaced Video (Telecine / 1080i)
        v_interlaced = StreamInfo(
            index=0,
            codec_type="video",
            codec_name="prores",
            profile="ProRes 422 HQ",
            width=1920,
            height=1080,
            fps=29.97,
            field_order="tt",  # Top field first (Interlaced)
            bits_per_raw_sample=10,
            duration=100.0
        )
        issues_int = validator.validate_video_stream(v_interlaced, 100.0)
        fail_int = [i for i in issues_int if i.parameter == "Scan Type" and i.severity == Severity.FAIL]
        self.assertEqual(len(fail_int), 1)

    def test_loudness_rules(self):
        """Test ITU-R BS.1770-4 / EBU R128 loudness validation."""
        profile = PRIME_PROFILES[ProfileType.PVD_HD]
        validator = AmazonRulesValidator(profile)

        # Compliant loudness (-24.0 LUFS, -2.5 dBTP)
        loud_good = {
            "integrated": -24.1,
            "true_peak": -2.5,
            "lra": 8.0
        }
        issues = validator.validate_loudness(loud_good)
        fails = [i for i in issues if i.severity == Severity.FAIL]
        self.assertEqual(len(fails), 0)

        # Violation: Too loud (-20.0 LUFS) and True Peak clipping (+0.5 dBTP)
        loud_bad = {
            "integrated": -20.0,
            "true_peak": 0.5,
            "lra": 10.0
        }
        issues_bad = validator.validate_loudness(loud_bad)
        fails_bad = [i for i in issues_bad if i.severity == Severity.FAIL]
        self.assertGreaterEqual(len(fails_bad), 2)

    def test_remediation_command_generation(self):
        """Test that remediation engine produces valid FFmpeg command."""
        report = QCReportData(
            file_path="E:\\Media\\test_master.mov",
            file_name="test_master.mov",
            file_size_bytes=1024*1024*100,
            duration_sec=60.0,
            profile_name="Prime Video Direct - HD Mezzanine",
            issues=[
                QCIssue(
                    id="LOUD-001",
                    severity=Severity.FAIL,
                    stream_type="Audio",
                    parameter="Integrated Loudness",
                    measured_value="-20.0 LUFS",
                    expected_value="-24.0 LUFS",
                    description="Too loud",
                    remediation_tip="Normalize"
                )
            ]
        )
        cmd = RemediationEngine.generate_ffmpeg_fix_command(report)
        self.assertIn("ffmpeg", cmd)
        self.assertIn("loudnorm", cmd)
        self.assertIn("prores_ks", cmd)

    def test_pdf_and_json_export(self):
        """Test PDF Certificate and JSON manifest generation."""
        os.makedirs("tests/output", exist_ok=True)
        report = QCReportData(
            file_path="E:\\Media\\sample_amazon_master.mov",
            file_name="sample_amazon_master.mov",
            file_size_bytes=500_000_000,
            duration_sec=120.0,
            profile_name=ProfileType.PVD_HD.value,
            verdict=Severity.PASS,
            compliance_score=100.0,
            issues=[
                QCIssue(
                    id="VID-001",
                    severity=Severity.PASS,
                    stream_type="Video",
                    parameter="Video Codec",
                    measured_value="ProRes 422 HQ",
                    expected_value="Approved Mezzanine Codec",
                    description="Valid codec",
                    remediation_tip="None"
                )
            ],
            container_info={"format_name": "mov", "size": 500_000_000, "duration": 120.0},
            video_streams=[
                StreamInfo(index=0, codec_type="video", codec_name="prores", profile="HQ", width=1920, height=1080, fps=24.0, field_order="progressive", bits_per_raw_sample=10, duration=120.0)
            ],
            audio_streams=[
                StreamInfo(index=1, codec_type="audio", codec_name="pcm_s24le", sample_rate=48000, channels=2, bits_per_raw_sample=24, duration=120.0)
            ],
            loudness_data={"integrated": -24.0, "true_peak": -2.0, "lra": 8.0}
        )

        pdf_path = "tests/output/test_report.pdf"
        json_path = "tests/output/test_manifest.json"

        PDFReportExporter.export(report, pdf_path)
        self.assertTrue(os.path.isfile(pdf_path))
        self.assertGreater(os.path.getsize(pdf_path), 1000)

        JSONManifestExporter.export(report, json_path)
        self.assertTrue(os.path.isfile(json_path))
        self.assertGreater(os.path.getsize(json_path), 100)


if __name__ == "__main__":
    unittest.main()
