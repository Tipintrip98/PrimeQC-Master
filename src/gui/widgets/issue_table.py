"""
Searchable and Filterable Compliance Checkpoints Table.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QLineEdit, QComboBox, QHeaderView, QPushButton, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from ...core.constants import Severity, StreamType
from ...engine.models import QCIssue


class IssueTableWidget(QFrame):
    """Table showing itemized compliance issues and checkpoints."""
    issue_selected = Signal(object)  # QCIssue
    sig_issue_selected = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_issues = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Filters Row
        filters_row = QHBoxLayout()
        filters_row.setSpacing(10)

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍 Search parameter, code, value or timecode...")
        self.txt_search.textChanged.connect(self._apply_filters)

        self.cb_severity_filter = QComboBox()
        self.cb_severity_filter.addItems(["All Severities", "❌ Errors (FAIL) Only", "⚠️ Warnings (WARN) Only", "ℹ️ Notices Only", "✓ Passed Only"])
        self.cb_severity_filter.currentIndexChanged.connect(self._apply_filters)

        self.cb_type_filter = QComboBox()
        self.cb_type_filter.addItems(["All Stream Types", "📦 Container", "🎥 Video", "🔊 Audio", "⚡ Signal Integrity", "🔤 Subtitle"])
        self.cb_type_filter.currentIndexChanged.connect(self._apply_filters)

        filters_row.addWidget(self.txt_search, 2)
        filters_row.addWidget(self.cb_severity_filter, 1)
        filters_row.addWidget(self.cb_type_filter, 1)

        layout.addLayout(filters_row)

        # Issues Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "STATUS", "STREAM", "PARAMETER", "TIMECODE", "DETECTED VALUE", "AMAZON PRIME SPECIFICATION"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #1e293b;
                border-radius: 8px;
                background-color: #080c14;
                alternate-background-color: #0d131f;
            }
            QTableWidget::item {
                padding: 6px 10px;
                border-bottom: 1px solid #141d2c;
            }
            QTableWidget::item:selected {
                background-color: #1e3a5f;
                color: #ffffff;
            }
        """)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

        layout.addWidget(self.table)

        # Set default column widths
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 110)
        self.table.setColumnWidth(2, 200)
        self.table.setColumnWidth(3, 110)
        self.table.setColumnWidth(4, 200)

    def set_issues(self, issues: list):
        """Loads issue list into table."""
        self.all_issues = issues
        self._apply_filters()

    def _apply_filters(self):
        search_query = self.txt_search.text().lower().strip()
        sev_idx = self.cb_severity_filter.currentIndex()
        type_idx = self.cb_type_filter.currentIndex()

        filtered = []
        for issue in self.all_issues:
            # Severity Filter
            if sev_idx == 1 and issue.severity != Severity.FAIL: continue
            elif sev_idx == 2 and issue.severity != Severity.WARNING: continue
            elif sev_idx == 3 and issue.severity != Severity.NOTICE: continue
            elif sev_idx == 4 and issue.severity != Severity.PASS: continue

            # Stream Type Filter
            if type_idx == 1 and issue.stream_type != StreamType.CONTAINER: continue
            elif type_idx == 2 and issue.stream_type != StreamType.VIDEO: continue
            elif type_idx == 3 and issue.stream_type != StreamType.AUDIO: continue
            elif type_idx == 4 and issue.stream_type != StreamType.INTEGRITY: continue
            elif type_idx == 5 and issue.stream_type != StreamType.SUBTITLE: continue

            # Search Query
            if search_query:
                text_corpus = f"{issue.id} {issue.parameter} {issue.measured_value} {issue.expected_value} {issue.description} {issue.timecode}".lower()
                if search_query not in text_corpus:
                    continue

            filtered.append(issue)

        self._populate_table(filtered)

    def _populate_table(self, issues: list):
        self.table.setRowCount(len(issues))
        for row, issue in enumerate(issues):
            # Status Item
            status_item = QTableWidgetItem()
            if issue.severity == Severity.FAIL:
                status_item.setText("❌ FAIL")
                status_item.setForeground(QColor("#f87171"))
            elif issue.severity == Severity.WARNING:
                status_item.setText("⚠️ WARN")
                status_item.setForeground(QColor("#fbbf24"))
            elif issue.severity == Severity.NOTICE:
                status_item.setText("ℹ️ INFO")
                status_item.setForeground(QColor("#38bdf8"))
            else:
                status_item.setText("✓ PASS")
                status_item.setForeground(QColor("#34d399"))

            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setData(Qt.UserRole, issue)

            type_item = QTableWidgetItem(issue.stream_type.value.upper())
            type_item.setTextAlignment(Qt.AlignCenter)
            type_item.setForeground(QColor("#94a3b8"))

            param_item = QTableWidgetItem(issue.parameter)
            param_item.setForeground(QColor("#f8fafc"))

            tc_item = QTableWidgetItem(issue.timecode or "--:--:--:--")
            tc_item.setTextAlignment(Qt.AlignCenter)
            tc_item.setForeground(QColor("#38bdf8") if issue.timecode and issue.timecode != "00:00:00:00" else QColor("#64748b"))

            measured_item = QTableWidgetItem(issue.measured_value)
            if issue.severity == Severity.FAIL:
                measured_item.setForeground(QColor("#f87171"))
            elif issue.severity == Severity.WARNING:
                measured_item.setForeground(QColor("#fbbf24"))
            else:
                measured_item.setForeground(QColor("#e2e8f0"))

            expected_item = QTableWidgetItem(issue.expected_value)
            expected_item.setForeground(QColor("#34d399"))

            self.table.setItem(row, 0, status_item)
            self.table.setItem(row, 1, type_item)
            self.table.setItem(row, 2, param_item)
            self.table.setItem(row, 3, tc_item)
            self.table.setItem(row, 4, measured_item)
            self.table.setItem(row, 5, expected_item)

    def _on_selection_changed(self):
        selected_rows = self.table.selectedItems()
        if selected_rows:
            issue = self.table.item(selected_rows[0].row(), 0).data(Qt.UserRole)
            if issue:
                self.issue_selected.emit(issue)
                self.sig_issue_selected.emit(issue)


