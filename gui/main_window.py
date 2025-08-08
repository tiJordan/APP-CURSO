import sys
import os
import json
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QTextEdit, QTreeWidget, QTreeWidgetItem, QPushButton,
    QFrame, QSizePolicy, QSpacerItem, QMenu, QAction, QMenuBar, QApplication, QMainWindow, qApp
)
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from settings import LOGO_PATH, CURSO_PATH, ICO_PATH, ICON_PLAYER,NOTES_DIR, SEEN_FILE, resource_path, note_filename
from themes import apply_dark_theme, apply_light_theme
from ajuda import mostrar_versao, buscar_atualizacao, mostrar_sobre, mostrar_ajuda
from gui.video_player import VideoPlayer  # <-- importe o player
from gui.audit_window import AuditWindow  # <-- importe a janela de auditoria
from core.audit import AuditLogger          

if not os.path.exists(NOTES_DIR): os.makedirs(NOTES_DIR)

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_seen(data):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)
 
# Para carregar anotação de um item
def carregar_anotacao(rel_path):
        try:
            with open(note_filename(rel_path), "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""
        
     # Para salvar anotação de um item
def salvar_anotacao(rel_path, texto):
        try:
            with open(note_filename(rel_path), "w", encoding="utf-8") as f:
                f.write(texto)
        except Exception:
            pass
                
def centralize_widget(widget):
    qr = widget.frameGeometry()
    cp = widget.screen().availableGeometry().center()
    qr.moveCenter(cp)
    widget.move(qr.topLeft())     

ICON_VIDEO = "assets/video.svg"       # Troque por seu PNG/SVG
ICON_VISTO = "assets/visto.svg"
ICON_PDF = "assets/pdf.svg"

class MainWindow(QWidget):
    def __init__(self, parent=None, usuario=None, is_manager=False):
        super().__init__(parent)
        self.setFixedSize(1200, 800)
        self.setWindowIcon(QIcon(resource_path(ICO_PATH)))
        self.usuario = usuario
        self.is_manager = is_manager
        self.seen_status = load_seen()
        self.dark_theme = False
        self.installEventFilter(self)
        self.setMouseTracking(True)
        
       
        #self.centralWidget().setMouseTracking(True)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # TOPO
        top_frame = QFrame()
        top_frame.setStyleSheet("background: #18544c;")
        top_frame.setProperty("role", "topbar")
        top_frame.setFixedHeight(60)
        top_layout = QHBoxLayout(top_frame)
        top_layout.setContentsMargins(18, 8, 18, 8)
        top_layout.setSpacing(16)
        top_frame.setMouseTracking(True)
        # CENTRO
        center_layout = QHBoxLayout()
        center_layout.setContentsMargins(12, 12, 12, 12)
        center_layout.setSpacing(14)
        
        logo_label = QLabel()
        if os.path.exists(LOGO_PATH):
            logo_label.setPixmap(QPixmap(LOGO_PATH).scaled(44, 44, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        top_layout.addWidget(logo_label)

        title_label = QLabel("Curso IA no Escritório")
        title_label.setFont(QFont("Segoe UI", 23, QFont.Bold))
        title_label.setStyleSheet("color: #fff;")
        top_layout.addWidget(title_label)
        top_layout.addStretch()

        top_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))

        user_label = QLabel(f"Usuário: <b>{self.usuario}</b>")
        user_label.setFont(QFont("Segoe UI", 13))
        user_label.setStyleSheet("color: #fff;")
        top_layout.addWidget(user_label)
        
        self.theme_btn = QPushButton("☀️")
        self.theme_btn.setFixedWidth(36)
        self.theme_btn.setStyleSheet("background: transparent; color: #fff; border: none; font-size: 18px;")
        self.theme_btn.clicked.connect(self.toggle_theme)
        top_layout.addWidget(self.theme_btn)
        top_layout.addSpacing(38)
        

        main_layout.addWidget(top_frame)
        
         # Barra de menu (adicione no topo do layout principal)
        #self.menu_bar = QMenuBar(self)
        #ajuda_menu = QMenu("Ajuda", self)

        self.ajuda_btn = QPushButton("Ajuda")
        self.ajuda_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #fff;
                font-weight: bold;
                font-size: 15px;
                border: none;
                padding: 6px 14px;
            }
            QPushButton::menu-indicator { image: none; }
            QPushButton:hover { background: #2271c9; color: #fff; }
        """)
        self.ajuda_btn.setVisible(False)  # Começa invisível
        self.ajuda_btn.setCursor(Qt.PointingHandCursor)
        top_layout.addWidget(self.ajuda_btn, alignment=Qt.AlignRight)
        
        self.ajuda_menu = QMenu(self)
        # Adicione as ações, igual antes
        
        
        if self.is_manager:
            self.ajuda_menu.addAction("Auditoria", lambda: AuditWindow(self).exec_())
            
        
        
        self.ajuda_menu.addAction("Versão", lambda: mostrar_versao(self))
        versao_action = QAction("Versão", self)
        versao_action.triggered.connect(lambda: mostrar_versao(self))
        
        self.ajuda_menu.addAction("Buscar Atualizações", lambda: buscar_atualizacao(self))
        update_action = QAction("Buscar Atualizações", self)
        update_action.triggered.connect(lambda: buscar_atualizacao(self))
        
        self.ajuda_menu.addAction("Sobre", lambda: mostrar_sobre(self))
        sobre_action = QAction("Sobre", self)
        sobre_action.triggered.connect(lambda: mostrar_sobre(self))
        
        self.ajuda_menu.addAction("Ajuda", lambda: mostrar_ajuda(self))
        ajuda_action = QAction("Ajuda", self)
        ajuda_action.triggered.connect(lambda: mostrar_ajuda(self))
        
        self.ajuda_btn.setMenu(self.ajuda_menu)
        

        
        
        self.ajuda_btn.setMenu(self.ajuda_menu)
        #self.menu_bar.addMenu(ajuda_menu)
        #main_layout.setMenuBar(self.menu_bar) 
        
        
        # TREEVIEW (2/3)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Conteúdo do Curso")
        self.tree.setMinimumWidth(350)
        self.tree.setFont(QFont("Segoe UI", 13))
        
        self.tree.itemClicked.connect(self.on_tree_select)
        self.tree.itemDoubleClicked.connect(self.on_tree_double_click)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.populate_tree()
        center_layout.addWidget(self.tree, 2)

        # ANOTAÇÕES (1/3)
        anot_frame = QFrame()
        anot_frame.setStyleSheet("border: 1px solid #ccc; border-radius: 4px;")
        anot_layout = QVBoxLayout(anot_frame)
        anot_layout.setContentsMargins(16, 16, 16, 16)
        anot_layout.setSpacing(8)

        self.anot_label = QLabel("Anotações do Módulo")
        self.anot_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        anot_layout.addWidget(self.anot_label)
        
         
            
      

        self.notes = QTextEdit()
        self.notes.setFont(QFont("Segoe UI", 13))
        self.notes.setStyleSheet("border: 1px solid #e1e1e1; border-radius: 4px;")
        self.notes.textChanged.connect(self.save_notes)
        anot_layout.addWidget(self.notes, 1)

        center_layout.addWidget(anot_frame, 1)
        main_layout.addLayout(center_layout)

        self.current_note_path = None
        self.ignore_change = False
        
        
    def save_notes(self):
        if self.ignore_change or not self.current_note_path:
            return
        salvar_anotacao(self.current_note_path, self.notes.toPlainText())      

    def toggle_theme(self):
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if not self.dark_theme:
            apply_dark_theme(app)
            self.theme_btn.setText("☀️")
            self.dark_theme = True
        else:
            apply_light_theme(app)
            self.theme_btn.setText("🌙")
            self.dark_theme = False


    def populate_tree(self):
        self.tree.clear()
        if os.path.exists(CURSO_PATH):
            for nome_modulo in sorted(os.listdir(CURSO_PATH)):
                mod_path = os.path.join(CURSO_PATH, nome_modulo)
                if os.path.isdir(mod_path):
                    # Módulos começam "fechados"!
                    mod_item = QTreeWidgetItem([f"📁 {nome_modulo}"])
                    mod_item.setData(0, Qt.UserRole, os.path.relpath(mod_path, CURSO_PATH))
                    mod_item.setExpanded(False)
                    self.tree.addTopLevelItem(mod_item)
                    self.add_tree_parts(mod_item, mod_path)
        self.tree.collapseAll()

    def add_tree_parts(self, parent_item, current_path):
        for item in sorted(os.listdir(current_path)):
            item_path = os.path.join(current_path, item)
            rel_path = os.path.relpath(item_path, CURSO_PATH)
            if os.path.isdir(item_path):
                sub_item = QTreeWidgetItem([f"📁 {item}"])
                sub_item.setData(0, Qt.UserRole, rel_path)
                sub_item.setExpanded(False)
                parent_item.addChild(sub_item)
                self.add_tree_parts(sub_item, item_path)
            else:
                file_item = QTreeWidgetItem([item])
                file_item.setData(0, Qt.UserRole, rel_path)
                # Diferencia PDF e vídeo
                if item.lower().endswith('.pdf'):
                    file_item.setIcon(0, QIcon(resource_path(ICON_PDF)))
                elif item.lower().endswith(('.mp4', '.mov', '.mkv', '.avi')):
                    if self.seen_status.get(rel_path):
                        file_item.setIcon(0, QIcon(resource_path(ICON_VISTO)))
                    else:
                        file_item.setIcon(0, QIcon(resource_path(ICON_VIDEO)))
                else:
                    # Outros arquivos: pode usar um ícone genérico ou nenhum
                    pass
                parent_item.addChild(file_item)

    def on_tree_select(self, item, column):
        rel_path = item.data(0, Qt.UserRole)
        if rel_path is None:
            self.notes.setReadOnly(True)
            self.anot_label.setText("Anotações")
            self.notes.setPlainText(carregar_anotacao(rel_path))
            self.notes.clear()
            return

        # Título dinâmico (como já fazia)
        if os.path.isdir(os.path.join(CURSO_PATH, rel_path)):
            parent = item.parent()
            if parent is None:
                self.anot_label.setText("Anotações do Módulo")
            else:
                self.anot_label.setText("Anotações da Pasta")
        else:
            self.anot_label.setText("Anotações do Vídeo")

        self.current_note_path = rel_path
        self.ignore_change = True
        self.notes.setPlainText(carregar_anotacao(rel_path))  # <-- correto!
        self.ignore_change = False
        self.notes.setReadOnly(False)

    def on_tree_double_click(self, item, column):
        rel_path = item.data(0, Qt.UserRole)
        full_path = os.path.join(CURSO_PATH, rel_path)
        if rel_path:
            if item.text(0).lower().endswith('.pdf'):
                # Abre PDF com visualizador padrão
                import platform
                if platform.system() == "Windows":
                    os.startfile(full_path)
                elif platform.system() == "Darwin":
                    os.system(f"open '{full_path}'")
                else:
                    os.system(f"xdg-open '{full_path}'")
            elif item.text(0).lower().endswith(('.mp4', '.mov', '.mkv', '.avi')):
                # Marca como visto e abre o player
                self.seen_status[rel_path] = True
                save_seen(self.seen_status)
                item.setIcon(0, QIcon(resource_path(ICON_VISTO)))
                from gui.video_player import VideoPlayer
                VideoPlayer(self, full_path).exec_()

        
            
    def eventFilter(self, obj, event):
        from PyQt5.QtCore import QEvent, Qt
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Alt:
            self.ajuda_btn.setVisible(True)
        elif event.type() == QEvent.KeyRelease and event.key() == Qt.Key_Alt:
            # Oculta após soltar Alt se não estiver com o mouse sobre
            if not self.ajuda_btn.underMouse():
                self.ajuda_btn.setVisible(False)
        elif event.type() == QEvent.MouseMove:
            # Exibe se mouse no canto direito
            if event.pos().x() > self.width() - 45 and event.pos().y() < 50:
                self.ajuda_btn.setVisible(True)
            elif not self.ajuda_btn.underMouse() and not QApplication.keyboardModifiers() & Qt.AltModifier:
                self.ajuda_btn.setVisible(False)
        return super().eventFilter(obj, event)        

    def show_context_menu(self, position):
        item = self.tree.itemAt(position)
        if not item:
            return
        rel_path = item.data(0, Qt.UserRole)
        if rel_path and not os.path.isdir(os.path.join(CURSO_PATH, rel_path)):
            menu = QMenu()
            if self.seen_status.get(rel_path):
                action = menu.addAction("Desmarcar como visto")
            else:
                action = menu.addAction("Marcar como visto")
            action.triggered.connect(lambda: self.toggle_seen(rel_path, item))
            menu.exec_(self.tree.viewport().mapToGlobal(position))

    def toggle_seen(self, rel_path, item):
        self.seen_status[rel_path] = not self.seen_status.get(rel_path, False)
        save_seen(self.seen_status)
        if self.seen_status[rel_path]:
            item.setIcon(0, QIcon(resource_path(ICON_VISTO)))
        else:
            item.setIcon(0, QIcon(resource_path(ICON_VIDEO)))
     
    def closeEvent(self, event):
        """Registra logout quando a janela principal é fechada."""
        AuditLogger().record_logout(self.usuario)
        super().closeEvent(event)        