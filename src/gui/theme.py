"""
Dark Studio Broadcast Design System & Stylesheets for PySide6.
"""

DARK_THEME_QSS = """
/* ==========================================================================
   MASTER BROADCAST DARK THEME - PRIMEQC MASTER
   ========================================================================== */

* {
    outline: none;
}

QWidget {
    background-color: #080c14;
    color: #e2e8f0;
    font-family: 'Segoe UI', 'SF Pro Display', -apple-system, system-ui, sans-serif;
    font-size: 13px;
    selection-background-color: #0284c7;
    selection-color: #ffffff;
}

QMainWindow {
    background-color: #080c14;
}

/* --- Menus & Menu Bar --- */
QMenuBar {
    background-color: #0d131f;
    border-bottom: 1px solid #1e293b;
    color: #cbd5e1;
    font-weight: 500;
    padding: 2px 8px;
}

QMenuBar::item {
    background: transparent;
    padding: 6px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #1e293b;
    color: #38bdf8;
}

QMenu {
    background-color: #0d1527;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 4px;
    color: #f1f5f9;
}

QMenu::item {
    padding: 6px 24px 6px 12px;
    border-radius: 4px;
    font-size: 12px;
}

QMenu::item:selected {
    background-color: #0284c7;
    color: #ffffff;
}

QMenu::separator {
    height: 1px;
    background-color: #1e293b;
    margin: 4px 8px;
}

/* --- Cards & Structural Frames --- */
QFrame.CardFrame, QFrame#CardFrame {
    background-color: #0d131f;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 10px;
}

QFrame.SubCardFrame, QFrame#SubCardFrame {
    background-color: #111827;
    border: 1px solid #1f2937;
    border-radius: 6px;
    padding: 10px;
}

/* --- Buttons --- */
QPushButton {
    background-color: #1e293b;
    color: #f1f5f9;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 600;
    font-size: 12px;
}

QPushButton:hover {
    background-color: #273549;
    border-color: #475569;
    color: #38bdf8;
}

QPushButton:pressed {
    background-color: #0f172a;
}

QPushButton:disabled {
    background-color: #111827;
    color: #475569;
    border-color: #1e293b;
}

QPushButton#PrimaryButton, QPushButton.PrimaryButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0284c7, stop:1 #0369a1);
    color: #ffffff;
    border: 1px solid #0284c7;
    font-weight: bold;
    letter-spacing: 0.5px;
}

QPushButton#PrimaryButton:hover, QPushButton.PrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #38bdf8, stop:1 #0284c7);
    border-color: #38bdf8;
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

/* --- Combo Box --- */
QComboBox {
    background-color: #111827;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 12px;
    min-height: 24px;
    font-weight: 500;
}

QComboBox:hover {
    border-color: #0284c7;
    background-color: #162032;
}

QComboBox:focus {
    border-color: #38bdf8;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #0d1527;
    border: 1px solid #334155;
    border-radius: 6px;
    color: #f8fafc;
    selection-background-color: #0284c7;
    selection-color: #ffffff;
    padding: 4px;
}

/* --- Tab Widget --- */
QTabWidget::pane {
    border: 1px solid #1e293b;
    background-color: #0d131f;
    border-radius: 8px;
    top: -1px;
}

QTabBar {
    background: transparent;
}

QTabBar::tab {
    background-color: #0b0f19;
    color: #94a3b8;
    border: 1px solid #1e293b;
    border-bottom: none;
    padding: 9px 20px;
    font-weight: 600;
    font-size: 12px;
    margin-right: 3px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}

QTabBar::tab:selected {
    background-color: #0d131f;
    color: #38bdf8;
    border-top: 2px solid #38bdf8;
    border-bottom: 1px solid #0d131f;
}

QTabBar::tab:hover:!selected {
    background-color: #162032;
    color: #f1f5f9;
}

/* --- Tables & Lists --- */
QTableWidget, QTableView {
    background-color: #090d16;
    gridline-color: #1e293b;
    border: 1px solid #1e293b;
    border-radius: 6px;
    color: #e2e8f0;
    selection-background-color: #1e3a5f;
    selection-color: #ffffff;
    alternate-background-color: #0d131f;
}

QHeaderView::section {
    background-color: #111827;
    color: #94a3b8;
    padding: 8px 10px;
    border: none;
    border-bottom: 2px solid #1e293b;
    border-right: 1px solid #1e293b;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 0.5px;
}

/* --- Scroll Bars --- */
QScrollBar:vertical {
    background-color: #080c14;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #1e293b;
    border-radius: 4px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background-color: #38bdf8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #080c14;
    height: 8px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #1e293b;
    border-radius: 4px;
    min-width: 24px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #38bdf8;
}

/* --- Progress Bar --- */
QProgressBar {
    background-color: #111827;
    border: 1px solid #1e293b;
    border-radius: 4px;
    text-align: center;
    color: #ffffff;
    font-weight: bold;
    font-size: 11px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #38bdf8);
    border-radius: 3px;
}

/* --- Input Fields --- */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #0b0f19;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 7px 10px;
    color: #f8fafc;
    font-size: 12px;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #38bdf8;
    background-color: #0d1527;
}

/* --- Status Bar --- */
QStatusBar {
    background-color: #0d131f;
    border-top: 1px solid #1e293b;
    color: #94a3b8;
    font-size: 11px;
    padding: 2px 8px;
}

/* --- Dialogs --- */
QDialog {
    background-color: #0d131f;
}

QGroupBox {
    border: 1px solid #1e293b;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 10px;
    font-weight: bold;
    color: #38bdf8;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    background-color: #0d131f;
}

QToolTip {
    background-color: #0f172a;
    border: 1px solid #38bdf8;
    color: #f8fafc;
    padding: 5px;
    border-radius: 4px;
    font-size: 11px;
}
"""
