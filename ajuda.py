import os
import sys
import subprocess
from PyQt5.QtWidgets import QMessageBox,QMessageBox, QApplication
from PyQt5.QtCore import QTimer
from settings import UPDATE_MANIFEST, APP_VERSION
import json
import shutil
import tempfile
import subprocess
import hashlib

from packaging.version import parse as parse_version

def get_local_exe_path():
    # Se rodando como .exe do PyInstaller
    if getattr(sys, 'frozen', False):
        return sys.executable
    else:
        # Para testes via script, simula na área de trabalho
        return os.path.join(os.path.expanduser('~'), 'Desktop', 'IA PROTEC.exe')

LOCAL_EXE = get_local_exe_path()

def mostrar_mensagem_temporaria(parent, titulo, mensagem, timeout=3000):
    msg = QMessageBox(parent)
    msg.setWindowTitle(titulo)
    msg.setText(mensagem)
    msg.setIcon(QMessageBox.Information)
    msg.setStandardButtons(QMessageBox.NoButton)  # Sem botão
    msg.show()
    QTimer.singleShot(timeout, msg.close)

def mostrar_versao(parent):
     """
     Exibe o número da versão (e data de build, se disponível),
     puxando de settings, em vez de um texto fixo.  
     """
     from settings import APP_VERSION, BUILD_DATE
     # Exemplo de informação adicional (ambiente):
     import platform
     from PyQt5.QtCore import qVersion as qt_version
 
     info = (
         f"Versão: {APP_VERSION}\n"
         f"Build: {BUILD_DATE}\n\n"
         f"Sistema: {platform.system()} {platform.release()}\n"
         f"Python: {platform.python_version()}\n"
         f"Qt: {qt_version()}"
     )
     QMessageBox.information(parent, "Versão", info)
    
def mostrar_ajuda(parent):
    # Pode abrir PDF, link, ou mostrar instruções
    QMessageBox.information(parent, "Ajuda", "Para suporte, entre em contato com o setor de TI.\nOu consulte o manual no menu 'Ajuda'.")

def mostrar_sobre(parent):
    QMessageBox.about(parent, "Sobre", "IA PROTEC\nCurso sobre IA no Escritório\n© 2025 PROTEC\nTodos os direitos reservados.")

def buscar_atualizacao(self):
    # 1) Carrega manifesto
    if not os.path.exists(UPDATE_MANIFEST):
        QMessageBox.warning(self, "Atualização", "Manifesto não encontrado.")
        return

    with open(UPDATE_MANIFEST, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    net_ver = manifest.get("version")
    installer_name = manifest.get("installer")
    checksum = manifest.get("sha256", "")

    if not net_ver or not installer_name:
        QMessageBox.warning(self, "Atualização", "Manifesto inválido.")
        return

    # 2) Compara versões
    if parse_version(net_ver) <= parse_version(APP_VERSION):
        QMessageBox.information(self, "Atualização", "Você já está na versão mais recente.")
        return

    # 3) Confirma com o usuário
    resp = QMessageBox.question(
        self, "Atualização disponível",
        f"Nova versão {net_ver} disponível. Deseja atualizar agora?",
        QMessageBox.Yes | QMessageBox.No
    )
    if resp != QMessageBox.Yes:
        return

    # 4) Copia MSI para pasta temporária
    share_dir = os.path.dirname(UPDATE_MANIFEST)
    src = os.path.join(share_dir, installer_name)
    dst = os.path.join(tempfile.gettempdir(), installer_name)
    try:
        shutil.copy2(src, dst)
    except Exception as e:
        QMessageBox.critical(self, "Erro", f"Falha ao copiar instalador: {e}")
        return

    # 5) Verifica checksum
    if checksum:
        h = hashlib.sha256()
        with open(dst, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        if h.hexdigest().lower() != checksum.lower():
            QMessageBox.critical(self, "Erro", "Checksum inválido.")
            return

    # 6) Executa MSI silenciosamente com privilégios elevados
    try:
        subprocess.run(
            ["msiexec", "/i", dst, "/quiet", "/norestart"],
            check=True
        )
        QApplication.quit()  # Fecha app para liberar arquivos
    except subprocess.CalledProcessError as e:
        QMessageBox.critical(self, "Erro", f"Falha ao executar instalador: {e}")