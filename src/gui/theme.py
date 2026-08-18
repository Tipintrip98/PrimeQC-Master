"""
Dark Studio Broadcast Design System & Stylesheets for PySide6.
"""

DARK_THEME_QSS = """
/* Master Dark Studio Theme */
QWidget {
    background-color: #0b0f19;
    color: #e2e8f0;
    font-family: 'Segoe UI', 'SF Pro Display', -apple-system, sans-serif;
    font-size: 13px;
    selection-background-color: #0284c7;
    selection-color: #ffffff;
}

QMainWindow {
    background-color: #0b0f19;
}

/* Header & Toolbars */
QFrame#HeaderFrame {
    background-color: #111827;
    border-bottom: 1px solid #1f2937;
    padding: 8px 16px;
}

QLabel#LogoTitle {
    font-size: 16px;
    font-weight: bold;
    color: #ffffff;
    letter-spacing: 0.5px;
}

QLabel#LogoSubtitle {
    font-size: 10px;
    font-weight: 600;
    color: #0ea5e9;
    letter-spacing: 1px;
}

/* Cards & Containers */
QFrame.CardFrame {
    background-color: #111827;
    border: 1px solid #1f2937;
    border-radius: 8px;
    padding: 12px;
}

QFrame.SubCardFrame {
    background-color: #1a2234;
    border: 1px solid #273549;
    border-radius: 6px;
    padding: 10px;
}

/* Buttons */
QPushButton {
    background-color: #1e293b;
    color: #f1f5f9;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #334155;
    border-color: #475569;
}

QPushButton:pressed {
    background-color: #0f172a;
}

QPushButton:disabled {
    background-color: #1e293b;
    color: #475569;
    border-color: #1e293b;
}

QPushButton#PrimaryButton {
    background-color: #0284c7;
    color: #ffffff;
    border: 1px solid #0369a1;
}

QPushButton#PrimaryButton:hover {
    background-color: #0369a1;
}

QPushButton#SuccessButton {
    background-color: #059669;
    color: #ffffff;
    border: 1px solid #047857;
}

QPushButton#SuccessButton:hover {
    background-color: #047857;
}

QPushButton#DangerButton {
    background-color: #dc2626;
    color: #ffffff;
    border: 1px solid #b91c1c;
}

/* Combo Box */
QComboBox {
    background-color: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 5px 12px;
    min-height: 24px;
    font-weight: 500;
}

QComboBox:hover {
    border-color: #0284c7;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #1e293b;
    border: 1px solid #334155;
    color: #f8fafc;
    selection-background-color: #0284c7;
    selection-color: #ffffff;
    padding: 4px;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #1f2937;
    background-color: #0f172a;
    border-radius: 6px;
    top: -1px;
}

QTabBar::tab {
    background-color: #111827;
    color: #94a3b8;
    border: 1px solid #1f2937;
    border-bottom: none;
    padding: 8px 18px;
    font-weight: 600;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}

QTabBar::tab:selected {
    background-color: #0f172a;
    color: #38bdf8;
    border-bottom: 2px solid #38bdf8;
}

QTabBar::tab:hover:!selected {
    background-color: #1e293b;
    color: #f1f5f9;
}

/* Tables */
QTableWidget, QTableView {
    background-color: #0f172a;
    gridline-color: #1e293b;
    border: 1px solid #1f2937;
    border-radius: 6px;
    color: #e2e8f0;
    selection-background-color: #1e3a5f;
    selection-color: #ffffff;
}

QHeaderView::section {
    background-color: #111827;
    color: #94a3b8;
    padding: 6px 10px;
    border: none;
    border-bottom: 1px solid #1f2937;
    border-right: 1px solid #1f2937;
    font-weight: 600;
    font-size: 11px;
}

/* Scroll Bars */
QScrollBar:vertical {
    background-color: #0b0f19;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #334155;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #475569;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #0b0f19;
    height: 8px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #334155;
    border-radius: 4px;
    min-width: 20px;
}

/* Progress Bar */
QProgressBar {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 4px;
    text-align: center;
    color: #ffffff;
    font-weight: bold;
    font-size: 11px;
    height: 16px;
}

QProgressBar::chunk {
    background-color: #0284c7;
    border-radius: 3px;
}

/* Line Edit & Text Edit */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #111827;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 10px;
    color: #f8fafc;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #0284c7;
}

/* Status Bar */
QStatusBar {
    background-color: #111827;
    border-top: 1px solid #1f2937;
    color: #94a3b8;
    font-size: 11px;
}
"""
