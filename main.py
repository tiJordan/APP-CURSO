import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QPushButton
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt
from settings import ICO_PATH, resource_path

from gui.login_window import LoginWindow
from gui.main_window import MainWindow
from core.db import init_db


def centralize_widget(widget):
    qr = widget.frameGeometry()
    cp = widget.screen().availableGeometry().center()
    qr.moveCenter(cp)
    widget.move(qr.topLeft())
    
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR"] = "1"

    

class CursoIAApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(resource_path(ICO_PATH)))
        self.setWindowTitle("PROTEC - Curso IA na Contabilidade")
        self.setGeometry(100, 100, 1000, 700)
        self.usuario = None
        
        from PyQt5.QtWidgets import QHBoxLayout, QWidget

        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setFixedWidth(36)
        self.theme_btn.setStyleSheet("background: transparent; color: #fff; border: none; font-size: 18px;")
        self.theme_btn.clicked.connect(self.toggle_theme)
        
        # Create a top layout and add the theme button
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.theme_btn)
        top_widget = QWidget()
        top_widget.setLayout(top_layout)
        self.setMenuWidget(top_widget)  # Add the top widget to the main window


        # Login modal
        login = LoginWindow(self)
        centralize_widget(login)
        if login.exec_() == 1:
            self.usuario = login.username
            self.main_widget = MainWindow(self, usuario=self.usuario, is_manager=login.is_manager)
            self.setCentralWidget(self.main_widget)
        else:
            self.close()

def main():
    app = QApplication(sys.argv)
    #apply_dark_theme(app)  # Aplicar tema escuro por padrão
    login = LoginWindow()
    login.show()
    centralize_widget(login)
    result = login.exec_()
    if result == QDialog.Accepted and login.username:
        window = MainWindow(usuario=login.username, is_manager=login.is_manager)
        window.show()
        centralize_widget(window)
        sys.exit(app.exec_())
    else:
        sys.exit(0)


if __name__ == "__main__":
    init_db()  # Inicializa o banco de dados    
    main()