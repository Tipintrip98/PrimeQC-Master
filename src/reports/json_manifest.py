"""
JSON Machine-Readable QC Manifest Exporter for Amazon Prime Pipelines.
"""

import json
import os
from ..engine.models import QCReportData


class JSONManifestExporter:
    """Exports structured QC report data as JSON."""

    @staticmethod
    def export(report: QCReportData, output_path: str) -> str:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
        return output_path
