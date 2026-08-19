"""
PrimeQC Master - Amazon Prime Video Quality Control Application Entry Point.
Supports both Desktop GUI Mode and Headless Automated CLI Pipeline Mode.
"""

import sys
import os
import argparse

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Enable High DPI scaling for crisp display on Windows 4K/retina monitors
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"


def run_cli(args):
    """Executes QC in command-line headless mode."""
    from src.engine.analyzer import PrimeQCAnalyzer
    from src.core.config import AppConfig
    from src.reports.pdf_report import PDFReportExporter
    from src.reports.json_manifest import JSONManifestExporter
    from src.reports.csv_report import CSVReportExporter
    from src.core.constants import Severity

    input_path = args.input or args.file
    if not input_path:
        print("Error: No input media file specified. Use -i <path> or provide file path.")
        sys.exit(1)

    input_file = os.path.abspath(input_path)
    if not os.path.isfile(input_file):
        print(f"Error: Media file not found: {input_file}")
        sys.exit(1)

    print(f"\n=======================================================")
    print(f"  PRIMEQC MASTER - AMAZON PRIME VIDEO QUALITY CONTROL  ")
    print(f"=======================================================")
    print(f"Input File: {input_file}")
    print(f"Profile:    {args.profile}")
    print(f"Starting inspection...\n")

    analyzer = PrimeQCAnalyzer(AppConfig())

    def progress_cb(stage, pct, msg):
        print(f"[{pct:3d}%] [{stage:15s}] {msg}")

    report = analyzer.run_qc(
        file_path=input_file,
        profile_name=args.profile,
        sidecar_subtitle_path=args.subtitle,
        progress_callback=progress_cb
    )

    print(f"\n-------------------------------------------------------")
    verdict_str = report.verdict.value if hasattr(report.verdict, "value") else str(report.verdict)
    print(f"VERDICT:          {verdict_str}")
    print(f"COMPLIANCE SCORE: {report.compliance_score:.1f}%")
    print(f"ERRORS:           {report.fail_count}")
    print(f"WARNINGS:         {report.warning_count}")
    print(f"PASSED CHECKS:    {report.pass_count}")
    print(f"-------------------------------------------------------")

    # Export requested reports
    if args.pdf:
        pdf_out = os.path.abspath(args.pdf)
        PDFReportExporter.export(report, pdf_out)
        print(f"[OK] PDF Certificate saved to: {pdf_out}")

    if args.json:
        json_out = os.path.abspath(args.json)
        JSONManifestExporter.export(report, json_out)
        print(f"[OK] JSON Manifest saved to:    {json_out}")

    if args.csv:
        csv_out = os.path.abspath(args.csv)
        CSVReportExporter.export(report, csv_out)
        print(f"[OK] CSV Log saved to:          {csv_out}")

    sys.exit(0 if verdict_str == Severity.PASS.value else (2 if verdict_str == Severity.WARNING.value else 1))


def run_gui(initial_file: str = None):
    """Launches the PySide6 Desktop GUI."""
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QIcon
    from src.gui.main_window import MainWindow
    from src.gui.theme import DARK_THEME_QSS

    app = QApplication(sys.argv)
    app.setApplicationName("PrimeQC Master")
    app.setOrganizationName("PrimeQC Studio")
    app.setStyleSheet(DARK_THEME_QSS)

    # Set icon if exists
    icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "app_icon.ico")
    if os.path.isfile(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    if initial_file and os.path.isfile(initial_file):
        window.drop_zone.set_media_file(initial_file)
    window.show()

    sys.exit(app.exec())


def main():
    parser = argparse.ArgumentParser(description="PrimeQC Master - Amazon Prime Video Quality Control Suite")
    parser.add_argument("file", nargs="?", help="Optional path to master media file")
    parser.add_argument("--cli", action="store_true", help="Run in headless CLI mode without GUI")
    parser.add_argument("-i", "--input", help="Path to master media file for QC")
    parser.add_argument("-p", "--profile", default="Prime Video Direct - HD Mezzanine", help="Amazon QC Profile name")
    parser.add_argument("-s", "--subtitle", help="Path to subtitle/timed text sidecar file (.srt, .vtt, .ttml)")
    parser.add_argument("--pdf", help="Export path for PDF QC Certificate")
    parser.add_argument("--json", help="Export path for JSON QC Manifest")
    parser.add_argument("--csv", help="Export path for CSV QC Log")

    args = parser.parse_args()

    if args.cli or (args.input and not sys.stdin.isatty()):
        run_cli(args)
    else:
        run_gui(initial_file=args.input or args.file)


if __name__ == "__main__":
    main()
