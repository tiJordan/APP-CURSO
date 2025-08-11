
import os
import sys
import getpass
import tempfile

# =============================================================
# Helpers de caminho (PyInstaller EXE e modo script)
# =============================================================
def resource_base_path() -> str:
    """Base de recursos:
    - No EXE (PyInstaller): sys._MEIPASS
    - Em dev: pasta deste arquivo
    """
    if getattr(sys, "frozen", False):
        return sys._MEIPASS  # type: ignore[attr-defined]
    return os.path.abspath(os.path.dirname(__file__))

def resource_path(relative_path: str) -> str:
    """Monta caminho absoluto para arquivos de recursos."""
    return os.path.join(resource_base_path(), relative_path)

def get_base_dir() -> str:
    """Pasta onde o executável/script está rodando."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.dirname(__file__))

BASE_DIR = get_base_dir()

# =============================================================
# Auditoria/estado (protegidos)
# =============================================================
PROGRAMDATA = os.environ.get("PROGRAMDATA") or os.environ.get("ALLUSERSPROFILE") or r"C:\\ProgramData"
LOCALAPPDATA = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or BASE_DIR

# Apenas retorna o caminho; criação pode ser feita on-demand
def get_status_folder(create: bool = False) -> str:
    primary = os.path.join(PROGRAMDATA, "IA_PROTEC", "status")
    fallback = os.path.join(LOCALAPPDATA, "IA_PROTEC", "status")
    if create:
        try:
            os.makedirs(primary, exist_ok=True)
            return primary
        except OSError:
            os.makedirs(fallback, exist_ok=True)
            return fallback
    return primary

def get_audit_db_path(create_dir: bool = False) -> str:
    folder = get_status_folder(create=create_dir)
    return os.path.join(folder, "audit.db")

AUDIT_DB = get_audit_db_path(create_dir=False)

# =============================================================
# Diretórios de anotações (compatibilidade com código existente)
# =============================================================
NOME_USUARIO = getpass.getuser()
# Caminho de rede (se utilizado em outras rotinas) — mantido apenas como string
REDE_ANOTACOES_DIR = "\\\\SRV-AD02\\DEPLOY\\anotacoes_usuarios"

# Fallback local seguro (evita permissões em Program Files)
NOTES_DIR = os.path.join(LOCALAPPDATA, "IA_PROTEC", "anotacoes")
try:
    os.makedirs(NOTES_DIR, exist_ok=True)
except OSError:
    pass

def get_user_note_dir(create: bool = False) -> str:
    """Prefere rede se a pasta existir; caso contrário, usa NOTES_DIR local."""
    target = NOTES_DIR
    if os.path.isdir(REDE_ANOTACOES_DIR):
        target = os.path.join(REDE_ANOTACOES_DIR, NOME_USUARIO)
    if create:
        try:
            os.makedirs(target, exist_ok=True)
        except OSError:
            target = NOTES_DIR
            os.makedirs(target, exist_ok=True)
    return target

def note_filename(rel_path: str, create_dirs: bool = False) -> str:
    """Nome de arquivo de anotação a partir de um caminho relativo."""
    nome = rel_path.replace("\\", "_").replace("/", "_") + ".txt"
    base = get_user_note_dir(create=create_dirs)
    return os.path.join(base, nome)

# Arquivo temporário de status de vídeos (por-usuário)
SEEN_FILE = os.path.join(tempfile.gettempdir(), "status_videos.json")

# =============================================================
# Recursos visuais (ícones, imagens)
# =============================================================
ICO_PATH    = resource_path("assets/icone_app.ico")
LOGO_PATH   = resource_path("assets/imagem_protec.png")
EYE_OPEN    = resource_path("assets/eye_open.svg")
EYE_CLOSED  = resource_path("assets/eye_closed.svg")
ICON_VISTO  = resource_path("assets/visto.svg")
ICON_VIDEO  = resource_path("assets/video.svg")
ICON_PDF    = resource_path("assets/pdf.svg")
ICON_PLAYER = resource_path("assets/player.svg")
ICON_APP    = resource_path("assets/icone_app.ico")

# =============================================================
# Configurações diversas
# =============================================================
CURSO_PATH = "\\\\192.168.0.140\\curso ia"  # mantenha se necessário
USE_LDAP   = True
AD_SERVER  = "192.168.0.51"
AD_DOMAIN  = "protec2.local"
AD_BASEDN  = "DC=protec2,DC=local"

# =============================================================
# Atualização automática
# =============================================================
UPDATE_MANIFEST = "\\\\SRV-AD02\\DEPLOY\\version.json"
NREDE_EXE = "\\\\SRV-AD02\\DEPLOY\\IA PROTEC.exe"
LOCAL_EXE = os.path.join(BASE_DIR, "IA PROTEC.exe")

APP_VERSION = "1.0.0"
BUILD_DATE  = "2025-08-09"
