from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout, QFrame, QToolButton
)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QPalette, QColor, QPainter
from PyQt5.QtCore import Qt
from settings import ICO_PATH, LOGO_PATH, USE_LDAP, EYE_CLOSED, EYE_OPEN, resource_path
from core.audit import AuditLogger
from core.auth import autenticar_ad, is_user_in_group
import os
import sys

FIELD_WIDTH = 330



class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Curso IA - Protec")
        self.setWindowIcon(QIcon(resource_path(ICO_PATH)))
        self.setFixedSize(480, 320)
        self.username = ''
        self.password = ''
        self.is_manager = False

        pal = self.palette()
        pal.setColor(QPalette.Window, QColor("#18544c"))
        self.setPalette(pal)
        self.setAutoFillBackground(True)
        
        #self.setStyleSheet("background-color: #18544c;")


        # --- Marca d'água logo centralizada ---
        self.bg_logo = QLabel(self)
        self.bg_logo.setAlignment(Qt.AlignCenter)
        self.bg_logo.setAttribute(Qt.WA_TransparentForMouseEvents)
        if os.path.exists(resource_path(LOGO_PATH)):
            self.logo_pix = QPixmap(resource_path(LOGO_PATH))
        else:
            self.logo_pix = None

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setSpacing(13)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch(1)

        # Usuário (centralizado)
        self.username_entry = QLineEdit()
        self.username_entry.setPlaceholderText("Nome de Usuário")
        self.username_entry.setFixedSize(FIELD_WIDTH, 38)
        self.username_entry.setFont(QFont("Segoe UI", 15))
        self.username_entry.setStyleSheet("""
            QLineEdit {
                background: #fff; color: #222; border: 1px solid #e5e5e5;
                border-radius: 4px; padding-left: 12px;
            }
            QLineEdit:focus { border: 1.5px solid #269a8a; }
        """)
        user_row = QHBoxLayout()
        user_row.addStretch(1)
        user_row.addWidget(self.username_entry)
        user_row.addStretch(1)
        layout.addLayout(user_row)

        # Senha + olho mágico (centralizado)
        pw_row = QHBoxLayout()
        pw_row.setContentsMargins(0, 0, 0, 0)
        pw_row.setSpacing(0)

        self.password_entry = QLineEdit()
        self.password_entry.setPlaceholderText("Senha do Usuário")
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.password_entry.setFixedHeight(38)
        self.password_entry.setFixedWidth(FIELD_WIDTH - 38)
        self.password_entry.setFont(QFont("Segoe UI", 15))
        self.password_entry.setStyleSheet("""
            QLineEdit {
                background: #fff; color: #222; border: 1px solid #e5e5e5;
                border-top-left-radius: 4px; border-bottom-left-radius: 4px;
                border-top-right-radius: 0px; border-bottom-right-radius: 0px;
                padding-left: 12px;
            }
            QLineEdit:focus { border: 1.5px solid #269a8a; }
        """)
        pw_row.addWidget(self.password_entry)

        eye_open_icon = QIcon(resource_path(EYE_OPEN))
        eye_closed_icon = QIcon(resource_path(EYE_CLOSED))

        self.show_pw_btn = QToolButton()
        self.show_pw_btn.setIcon(eye_closed_icon)
        self.show_pw_btn.setCheckable(True)
        self.show_pw_btn.setFixedSize(38, 38)
        self.show_pw_btn.setCursor(Qt.PointingHandCursor)
        self.show_pw_btn.setStyleSheet("""
            QToolButton {
                background: #fff; border: 1px solid #e5e5e5;
                border-top-right-radius: 4px; border-bottom-right-radius: 4px;
                border-left: none;
            }
            QToolButton:pressed { background: #ececec; }
        """)
        self.show_pw_btn.clicked.connect(lambda: self.toggle_password(EYE_OPEN, EYE_CLOSED))
        pw_row.addWidget(self.show_pw_btn)
        pw_container = QFrame()
        pw_container.setLayout(pw_row)
        pw_container.setFixedWidth(FIELD_WIDTH)
        pw_wrap = QHBoxLayout()
        pw_wrap.addStretch(1)
        pw_wrap.addWidget(pw_container)
        pw_wrap.addStretch(1)
        layout.addLayout(pw_wrap)

        # Botão entrar (centralizado)
        self.login_btn = QPushButton("Entrar")
        self.login_btn.setFixedSize(FIELD_WIDTH, 38)
        self.login_btn.setFont(QFont("Segoe UI", 17, QFont.Bold))
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: #269a8a; color: #fff; border: none; border-radius: 2px;
                font-weight: bold;
            }
            QPushButton:hover { background: #217e70; }
        """)
        self.login_btn.clicked.connect(self.try_login)
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        btn_row.addWidget(self.login_btn)
        btn_row.addStretch(1)
        layout.addLayout(btn_row)

        layout.addStretch(2)

        self.username_entry.returnPressed.connect(self.try_login)
        self.password_entry.returnPressed.connect(self.try_login)
        self.update_logo()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_logo()

    def update_logo(self):
        if not self.logo_pix:
            return
        win_w, win_h = self.width(), self.height()
        logo_w, logo_h = self.logo_pix.width(), self.logo_pix.height()
        scale = min(win_w / logo_w, win_h / logo_h) * 1.23
        new_w, new_h = int(logo_w * scale), int(logo_h * scale)
        pix = self.logo_pix.scaled(new_w, new_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        # Deixa translúcido (marca d'água)
        transp_pix = QPixmap(pix.size())
        transp_pix.fill(Qt.transparent)
        painter = QPainter(transp_pix)
        #painter.setOpacity(0.32)   # Ajuste conforme desejar!
        painter.drawPixmap(0, 0, pix)
        painter.end()
        self.bg_logo.setPixmap(transp_pix)
        self.bg_logo.resize(new_w, new_h)
        self.bg_logo.move(
            (win_w - new_w) // 2,
            (win_h - new_h) // 2
        )

    def toggle_password(self, eye_open, eye_closed):
        if self.show_pw_btn.isChecked():
            self.password_entry.setEchoMode(QLineEdit.Normal)
            self.show_pw_btn.setIcon(QIcon(resource_path(eye_open)))
        else:
            self.password_entry.setEchoMode(QLineEdit.Password)
            self.show_pw_btn.setIcon(QIcon(resource_path(eye_closed)))

    def try_login(self):
        usuario = self.username_entry.text().strip()
        senha = self.password_entry.text()
        if not usuario or not senha:
            self.msg_box("Preencha todos os campos")
            return
        if USE_LDAP:
            from core.auth import autenticar_ad
            ok = autenticar_ad(usuario, senha)
        else:
            ok = True
        if ok:
            AuditLogger().record_login(usuario)
            self.is_manager = is_user_in_group(usuario, senha, "GRP_TIME_IA")
            self.username = usuario
            
            self.accept()  # Fecha o diálogo com sucesso
        else:
            self.msg_box("Usuário ou senha inválidos!")

    def msg_box(self, msg):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Atenção", msg)
