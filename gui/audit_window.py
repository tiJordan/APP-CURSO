from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QPushButton,
    QDateEdit, QComboBox, QFileDialog
)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime
from core.audit import AuditLogger

class AuditWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Auditoria de Sessões")
        self.logger = AuditLogger()
        self.is_active_mode = True
        self._build_ui()
        self._load_users()
        self._show_active()

    def _build_ui(self):
        self.main_layout = QVBoxLayout(self)

         # —— Modo de exibição ——
        self.btn_active   = QPushButton("Ativos")
        self.btn_active.setFixedSize(100, 40)
        self.btn_active.setStyleSheet("font-weight: bold;")  # Destaque para o botão ativo
        self.btn_history  = QPushButton("Histórico")
        self.btn_history.setFixedSize(100, 40)
        self.btn_history.setStyleSheet("font-weight: normal;")  # Normal para o botão histórico
        self.btn_refresh  = QPushButton("🔄")

        # ToolTip e cursor do botão de refresh
        self.btn_refresh.setToolTip("Atualizar")
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        # Aumenta o tamanho do botão de refresh
        self.btn_refresh.setFixedSize(40, 40)
        self.btn_refresh.setStyleSheet("font-size: 18px;")  # Aumenta o ícone

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_active)
        btn_layout.addWidget(self.btn_history)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_refresh)
        self.main_layout.addLayout(btn_layout)

        self.btn_active.clicked.connect(self._show_active)
        self.btn_history.clicked.connect(self._show_history)
        self.btn_refresh.clicked.connect(self._on_refresh)

        # —— Layout de Filtros ——
        f_layout = QHBoxLayout()
        f_layout.addWidget(QLabel("Usuário:"))
        self.user_cb = QComboBox()
        self.user_cb.addItem("Todos")
        f_layout.addWidget(self.user_cb)

        f_layout.addWidget(QLabel("De:"))
        self.date_from = QDateEdit(calendarPopup=True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        f_layout.addWidget(self.date_from)

        f_layout.addWidget(QLabel("Até:"))
        self.date_to = QDateEdit(calendarPopup=True)
        self.date_to.setDate(QDate.currentDate())
        f_layout.addWidget(self.date_to)

        self.filter_btn = QPushButton("Filtrar")
        f_layout.addWidget(self.filter_btn)
        self.main_layout.addLayout(f_layout)

        # O botão “Filtrar” aciona o modo Histórico
        self.filter_btn.clicked.connect(self._show_history)

        # —— Tabela de Sessões ——
        self.table = QTableWidget()
        self.main_layout.addWidget(self.table)

        # —— Exportar CSV ——
        self.export_btn = QPushButton("Exportar CSV")
        self.export_btn.clicked.connect(self._export_csv)
        self.main_layout.addWidget(self.export_btn, alignment=Qt.AlignRight)

    def _load_users(self):
        users = sorted({s['user'] for s in self.logger.get_sessions()})
        for u in users:
            self.user_cb.addItem(u)

    def _on_refresh(self):
        if self.is_active_mode:
            self._show_active()
        else:
            self._show_history()

    def _show_active(self):
        """Modo ‘Ativos’: limpa tudo e exibe sessões ativas."""
        self.is_active_mode = True
        self.user_cb.hide()
        self.date_from.hide()
        self.date_to.hide()
        self.filter_btn.hide()

        sessions = self.logger.get_active_sessions()

        # 1) Limpa completamente a tabela
        self.table.clear()
        self.table.setRowCount(0)
        # 2) Define 3 colunas e cabeçalhos
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Usuário", "Login", "Duração"])

        # 3) Insere cada sessão ativa
        for sess in sessions:
            row = self.table.rowCount()
            self.table.insertRow(row)
            login_str = sess['login_time'].strftime("%H:%M:%S - %d/%m/%Y")
            total_sec = int(sess['duration'].total_seconds())
            h, rem = divmod(total_sec, 3600)
            m, s_ = divmod(rem, 60)
            dur_str = f"{h:02d}:{m:02d}:{s_:02d}"

            self.table.setItem(row, 0, QTableWidgetItem(sess['user']))
            self.table.setItem(row, 1, QTableWidgetItem(login_str))
            self.table.setItem(row, 2, QTableWidgetItem(dur_str))
            

        self.table.resizeColumnsToContents()
        self.table.setSortingEnabled(True)
        
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # Desabilita edição

    def _show_history(self):
        """Modo ‘Histórico’: limpa tudo e exibe histórico filtrado."""
        self.is_active_mode = False
        self.user_cb.show()
        self.date_from.show()
        self.date_to.show()
        self.filter_btn.show()

        # 1) Obtém sessões filtradas
        sessions = self.logger.get_sessions(
            user=None if self.user_cb.currentText() == "Todos" else self.user_cb.currentText(),
            start=datetime.combine(self.date_from.date().toPyDate(), datetime.min.time()),
            end=datetime.combine(self.date_to.date().toPyDate(), datetime.max.time())
        )

        # 2) Limpa e reconfigura a tabela
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Usuário", "Login", "Logout", "Duração"])

        # 3) Insere cada registro de histórico
        for sess in sessions:
            row = self.table.rowCount()
            self.table.insertRow(row)
            login_str  = sess['login_time'].strftime("%H:%M:%S - %d/%m/%Y")
            logout_str = (sess['logout_time'].strftime("%H:%M:%S - %d/%m/%Y")
                          if sess['logout_time'] else "—")
            total_sec = int(sess['duration'].total_seconds())
            h, rem = divmod(total_sec, 3600)
            m, s_ = divmod(rem, 60)
            dur_str = f"{h:02d}:{m:02d}:{s_:02d}"

            self.table.setItem(row, 0, QTableWidgetItem(sess['user']))
            self.table.setItem(row, 1, QTableWidgetItem(login_str))
            self.table.setItem(row, 2, QTableWidgetItem(logout_str))
            self.table.setItem(row, 3, QTableWidgetItem(dur_str))

        self.table.resizeColumnsToContents()
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # Desabilita edição
            
        
        

    def _export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Salvar CSV", filter="CSV Files (*.csv)")
        if not path:
            return
        import csv

        # escolhe colunas e cabeçalhos conforme o modo
        if self.is_active_mode:
            cols, headers = 3, ["Usuário", "Login", "Duração"]
        else:
            cols, headers = 4, ["Usuário", "Login", "Logout", "Duração"]

        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for r in range(self.table.rowCount()):
                rowdata = [self.table.item(r, c).text() for c in range(cols)]
                writer.writerow(rowdata)
