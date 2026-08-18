"""
CSV Log Exporter for Quality Control Reports.
"""

import csv
import os
from ..engine.models import QCReportData


class CSVReportExporter:
    """Exports QC issue logs and summary as CSV."""

    @staticmethod
    def export(report: QCReportData, output_path: str) -> str:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            
            # Header summary
            writer.writerow(["AMAZON PRIME VIDEO QUALITY CONTROL REPORT"])
            writer.writerow(["File Name", report.file_name])
            writer.writerow(["File Path", report.file_path])
            writer.writerow(["Duration (sec)", f"{report.duration_sec:.2f}"])
            writer.writerow(["Profile", report.profile_name])
            writer.writerow(["Verdict", report.verdict.value])
            writer.writerow(["Compliance Score (%)", f"{report.compliance_score:.1f}%"])
            writer.writerow(["Generated At", report.generated_at])
            writer.writerow([])

            # Issues table
            writer.writerow([
                "ID", "Severity", "Stream Type", "Parameter",
                "Timecode", "Measured Value", "Expected Value",
                "Description", "Remediation Tip"
            ])

            for i in report.issues:
                writer.writerow([
                    i.id,
                    i.severity.value,
                    i.stream_type.value,
                    i.parameter,
                    i.timecode,
                    i.measured_value,
                    i.expected_value,
                    i.description,
                    i.remediation_tip
                ])

        return output_path
