# themes.py
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

def apply_dark_theme(app):
    dark = QPalette()
    dark.setColor(QPalette.Window, QColor(30, 30, 30))
    dark.setColor(QPalette.WindowText, Qt.white)
    dark.setColor(QPalette.Base, QColor(22, 22, 22))
    dark.setColor(QPalette.AlternateBase, QColor(40, 40, 40))
    dark.setColor(QPalette.ToolTipBase, Qt.white)
    dark.setColor(QPalette.ToolTipText, Qt.white)
    dark.setColor(QPalette.Text, Qt.white)
    dark.setColor(QPalette.Button, QColor(40, 40, 40))
    dark.setColor(QPalette.ButtonText, Qt.white)
    dark.setColor(QPalette.BrightText, Qt.red)
    dark.setColor(QPalette.Link, QColor("#8cbaff"))
    dark.setColor(QPalette.Highlight, QColor("#2295f2"))
    dark.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(dark)
    app.setStyleSheet("""
    QToolTip { color: #fff; background-color: #299fff; border: none; }
    QPushButton { background: #299fff; color: #fff; border-radius: 5px; }
    QPushButton:hover { background: #2176b5; }
    QTreeWidget, QTreeView {
        background: #1c232b;
        color: #e4eaf2;
        border: 1px solid #273444;
        selection-background-color: #2566a6;
        selection-color: #fff;
        alternate-background-color: #232c36;
        outline: 0;
    }
    QTreeWidget::item, QTreeView::item {
        background: transparent;
        color: #e4eaf2;
    }
    QTreeWidget::item:hover {
    background: #253142;
    }
    QTreeWidget::item:selected, QTreeView::item:selected {
        background: #2566a6;
        color: #fff;
    }
    QHeaderView::section {
        background: #222d36;
        color: #b1c4db;
        font-size: 14px;
        font-weight: bold;
        border: 1px solid #273444;
       padding: 4px;
    }
    QFrame, QDialog, QWidget {
        background: #151c23; /* Fundo escuro para o app todo */
        color: #e4eaf2;
        border: 1px solid #273444;
    }
    QFrame[role="topbar"] {
        background: #18544c;
        border: none;
    }
    QLineEdit, QTextEdit {
        background: #232c36;
        color: #e4eaf2;
        border: 1px solid #314056;
    }
    QTextEdit, QPlainTextEdit {
        background: #232c36;
        color: #e4eaf2;
    }
    QLabel {
        color: #e4eaf2;
    }
    QMenu, QMenuBar {
        background: #232c36;
        color: #e4eaf2;
        border: 1px solid #273444;
    }
    QMenu::item:selected {
        background: #299fff;
        color: #fff;
    }
""")


def apply_light_theme(app):
    app.setPalette(app.style().standardPalette())
    app.setStyleSheet("")  # Remove o CSS customizado