"""
QC Report Export Dialog supporting PDF, JSON, and CSV outputs.
"""

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QPushButton,
    QLineEdit, QFileDialog, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from ...engine.models import QCReportData
from ...reports.pdf_report import PDFReportExporter
from ...reports.json_manifest import JSONManifestExporter
from ...reports.csv_report import CSVReportExporter


class ExportReportDialog(QDialog):
    """Dialog for exporting QC Certificates and Manifests."""

    def __init__(self, report: QCReportData, parent=None):
        super().__init__(parent)
        self.report = report
        self.setWindowTitle("Export Amazon Prime QC Reports")
        self.setMinimumWidth(520)
        self.setStyleSheet("QDialog { background-color: #0f172a; color: #e2e8f0; }")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        layout.addWidget(QLabel("<b>Select QC Report Formats to Export:</b>"))

        # Formats Box
        box = QFrame()
        box.setStyleSheet("background-color: #1e293b; border-radius: 6px; padding: 10px;")
        box_layout = QVBoxLayout(box)
        box_layout.setSpacing(8)

        self.chk_pdf = QCheckBox("📄 Official PDF Quality Control Certificate (Recommended for delivery sign-off)")
        self.chk_pdf.setChecked(True)
        self.chk_json = QCheckBox("⚙️ JSON Machine-Readable Manifest (For automated pipeline integration)")
        self.chk_json.setChecked(True)
        self.chk_csv = QCheckBox("📊 CSV Spreadsheet Log (For quality archives)")
        self.chk_csv.setChecked(True)

        box_layout.addWidget(self.chk_pdf)
        box_layout.addWidget(self.chk_json)
        box_layout.addWidget(self.chk_csv)

        layout.addWidget(box)

        # Output Folder Row
        layout.addWidget(QLabel("<b>Output Folder:</b>"))
        folder_row = QHBoxLayout()
        default_dir = os.path.join(os.path.expanduser("~"), "Documents", "PrimeQC_Reports")
        os.makedirs(default_dir, exist_ok=True)

        self.txt_dir = QLineEdit(default_dir)
        self.btn_browse = QPushButton("Browse...")
        self.btn_browse.clicked.connect(self._browse_dir)

        folder_row.addWidget(self.txt_dir, 1)
        folder_row.addWidget(self.btn_browse)
        layout.addLayout(folder_row)

        # Action Buttons
        btn_box = QHBoxLayout()
        btn_box.addStretch()

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_export = QPushButton("Export Reports Now")
        self.btn_export.setObjectName("PrimaryButton")
        self.btn_export.clicked.connect(self._do_export)

        btn_box.addWidget(self.btn_cancel)
        btn_box.addWidget(self.btn_export)
        layout.addLayout(btn_box)

    def _browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select Export Directory", self.txt_dir.text())
        if d:
            self.txt_dir.setText(d)

    def _do_export(self):
        out_dir = self.txt_dir.text().strip()
        if not out_dir:
            return

        base_name = os.path.splitext(self.report.file_name)[0]
        exported = []

        try:
            if self.chk_pdf.isChecked():
                pdf_path = os.path.join(out_dir, f"{base_name}_PrimeQC_Certificate.pdf")
                PDFReportExporter.export(self.report, pdf_path)
                exported.append(pdf_path)

            if self.chk_json.isChecked():
                json_path = os.path.join(out_dir, f"{base_name}_PrimeQC_Manifest.json")
                JSONManifestExporter.export(self.report, json_path)
                exported.append(json_path)

            if self.chk_csv.isChecked():
                csv_path = os.path.join(out_dir, f"{base_name}_PrimeQC_Log.csv")
                CSVReportExporter.export(self.report, csv_path)
                exported.append(csv_path)

            QMessageBox.information(
                self,
                "Export Successful",
                f"Successfully exported {len(exported)} QC report(s) to:\n{out_dir}"
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Error exporting reports:\n{str(e)}")
