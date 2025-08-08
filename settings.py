import os
import sys
import getpass
import tempfile

NOME_USUARIO = getpass.getuser()
REDE_ANOTACOES_DIR = r"\\srv-aux\deploy_app$\anotacoes_usuarios"
USER_NOTE_DIR = os.path.join(REDE_ANOTACOES_DIR, NOME_USUARIO)

if not os.path.exists(USER_NOTE_DIR):
    try:
        os.makedirs(USER_NOTE_DIR)
    except Exception as e:
        pass  # Pode dar erro se rodar fora da rede, trate no app se quiser

def note_filename(rel_path):
    nome = rel_path.replace("\\", "_").replace("/", "_") + ".txt"
    return os.path.join(USER_NOTE_DIR, nome)    

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_base_dir():
    # Se rodando como .exe
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    # Se rodando como script
    else:
        return os.path.abspath(os.path.dirname(__file__))

BASE_DIR = get_base_dir()
NOTES_DIR = os.path.join(BASE_DIR, "anotacoes")
SEEN_FILE = os.path.join(tempfile.gettempdir(), "status_videos.json")

if not os.path.exists(NOTES_DIR):
    os.makedirs(NOTES_DIR)
    
ICO_PATH = resource_path("assets/icone_app.ico")
LOGO_PATH = resource_path("assets/imagem_protec.png")
EYE_OPEN = resource_path("assets/eye_open.svg")
EYE_CLOSED = resource_path("assets/eye_closed.svg")
ICON_VISTO  = resource_path("assets/visto.svg")
ICON_VIDEO  = resource_path("assets/video.svg")
ICON_PDF    = resource_path("assets/pdf.svg")
ICON_PLAYER = resource_path("assets/player.svg")
ICON_APP    = resource_path("assets/icone_app.ico")


CURSO_PATH = r'\\192.168.0.140\curso ia'  # Ou caminho local de teste
USE_LDAP = True
AD_SERVER = '192.168.0.51'
AD_DOMAIN = 'protec2.local'
AD_BASEDN = 'DC=protec2,DC=local'
STATUS_DIR = 'status'
REDE_EXE = r"\\Srv-aux\deploy_app$\IA PROTEC.exe"
LOCAL_EXE = os.path.join(os.path.dirname(sys.executable), "IA PROTEC.exe")

APP_VERSION = "1.0.0"
BUILD_DATE = "07-08-2025"
# Caminho UNC para o recurso de atualização
UPDATE_MANIFEST = r"\\Srv-aux\deploy_app$\version.json"



