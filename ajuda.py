
import os
import sys
import json
import tempfile
import hashlib
import ctypes
import ctypes.wintypes
import subprocess

from PyQt5.QtWidgets import QMessageBox
from packaging.version import parse as parse_version
from jsonschema import Draft7Validator

from settings import UPDATE_MANIFEST, APP_VERSION, BUILD_DATE

# ------------------------- Utilidades -------------------------

def resource_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS  # type: ignore[attr-defined]
    return os.path.dirname(__file__)
    
def mostrar_mensagem_temporaria(parent, titulo, mensagem, timeout=3000):
    from PyQt5.QtCore import QTimer
    msg = QMessageBox(parent)
    msg.setWindowTitle(titulo)
    msg.setText(mensagem)
    msg.setIcon(QMessageBox.Information)
    msg.setStandardButtons(QMessageBox.NoButton)
    msg.show()
    QTimer.singleShot(timeout, msg.close)

def mostrar_versao(parent):
    import platform
    from PyQt5.QtCore import qVersion
    # mesma função usada no fluxo de update
    from ajuda import get_installed_version  
    # se preferir evitar import circular, mova get_installed_version() para este arquivo

    versao = get_installed_version()
    texto = (
        f"Versão: {versao}\n"
        f"Build: {BUILD_DATE}\n"
        f"Sistema: {platform.system()} {platform.release()}\n"
        f"Python: {platform.python_version()}\n"
        f"Qt: {qVersion()}"
    )
    QMessageBox.information(parent, "Versão", texto)

def mostrar_ajuda(parent):
    QMessageBox.information(parent, "Ajuda",
                            "Para suporte, contate o TI.\nConsulte também o manual no menu 'Ajuda'.")

def mostrar_sobre(parent):
    QMessageBox.about(parent, "Sobre",
                      "IA PROTEC\nCurso sobre IA no Escritório\n© 2025 PROTEC\nTodos os direitos reservados.")

def resource_base_path():
    """Base de recursos: _MEIPASS (EXE) ou pasta do arquivo (dev)."""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(__file__)    
    

def validar_manifesto(path, schema_path):
    with open(schema_path, encoding='utf-8') as f:
        schema = json.load(f)
    with open(path, encoding='utf-8') as f:
        manifest = json.load(f)

    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(manifest), key=lambda e: e.path)
    if errors:
        msgs = ["{}/{}: {}".format('/'.join(map(str, e.path)), '', e.message) for e in errors]
        raise ValueError("Manifesto inválido:\n" + "\n".join(msgs))
    return manifest

def get_installed_version():
    """Tenta ler a versão instalada deixada pelo MSI no Registro."""
    try:
        import winreg
        keys = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Protec Assessoria Contabil\\PROTEC IA"),
            (winreg.HKEY_CURRENT_USER,  r"SOFTWARE\\Protec Assessoria Contabil\\PROTEC IA"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\WOW6432Node\\Protec Assessoria Contabil\\PROTEC IA"),
        ]
        for root, subkey in keys:
            try:
                with winreg.OpenKey(root, subkey) as k:
                    v, _ = winreg.QueryValueEx(k, "Version")
                    if isinstance(v, str) and v.strip():
                        return v.strip()
            except FileNotFoundError:
                continue
    except Exception:
        pass
    return APP_VERSION

# ---------------------- Fluxo de Atualização ------------------

def buscar_atualizacao(self):
    # 0) Validar schema do manifesto
    schema_file = os.path.join(resource_base_path(), 'installer', 'manifest-schema.json')
    try:
        manifest = validar_manifesto(UPDATE_MANIFEST, schema_file)
    except ValueError as e:
        QMessageBox.critical(self, "Erro de Manifesto", str(e))
        return
    except Exception as e:
        QMessageBox.critical(self, "Erro inesperado", str(e))
        return

    # 1) Checar versões
    current_ver = get_installed_version()
    net_ver = manifest.get("version")
    installer_name = manifest.get("installer")
    checksum = manifest.get("sha256", "")

    if not net_ver or not installer_name:
        QMessageBox.warning(self, "Atualização", "Manifesto inválido.")
        return

    if parse_version(net_ver) <= parse_version(current_ver):
        QMessageBox.information(self, "Atualização", "Você já está na versão mais recente ({}).".format(current_ver))
        return

    # 2) Confirma atualização
    resp = QMessageBox.question(
        self,
        "Atualização disponível",
        "Nova versão {} disponível. Deseja atualizar agora?".format(net_ver),
        QMessageBox.Yes | QMessageBox.No
    )
    if resp != QMessageBox.Yes:
        return

    # 3) Copiar MSI para %TEMP%
    share_dir = os.path.dirname(UPDATE_MANIFEST)
    src = os.path.join(share_dir, installer_name)
    dst = os.path.join(tempfile.gettempdir(), installer_name)

    try:
        with open(src, 'rb') as f_src, open(dst, 'wb') as f_dst:
            while True:
                buf = f_src.read(8192)
                if not buf:
                    break
                f_dst.write(buf)
    except Exception as e:
        QMessageBox.critical(self, "Erro de Cópia", "Não foi possível copiar o instalador:\n{}".format(e))
        return

    if not os.path.exists(dst):
        QMessageBox.critical(self, "Erro", "Arquivo MSI não foi copiado corretamente.")
        return

    # 4) Verificar checksum (se fornecido)
    if checksum:
        h = hashlib.sha256()
        with open(dst, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        got = h.hexdigest().lower()
        if got != checksum.lower():
            QMessageBox.critical(self, "Erro", "Checksum do instalador inválido.")
            return

    # 5) Disparar MSI elevado via ShellExecuteEx e preparar relançamento
    log_path = os.path.join(tempfile.gettempdir(), "IA_PROTEC_Update.log")
    params   = '/i "{}" /quiet /norestart /l*v "{}"'.format(dst, log_path)

    windir  = os.environ.get("WINDIR", r"C:\\Windows")
    msi_exe = os.path.join(windir, "System32", "msiexec.exe")
    msi_alt = os.path.join(windir, "Sysnative", "msiexec.exe")
    if not os.path.exists(msi_exe) and os.path.exists(msi_alt):
        msi_exe = msi_alt

    SEE_MASK_NOCLOSEPROCESS = 0x00000040
    class SHELLEXECUTEINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize",      ctypes.wintypes.DWORD),
            ("fMask",       ctypes.wintypes.ULONG),
            ("hwnd",        ctypes.wintypes.HWND),
            ("lpVerb",      ctypes.wintypes.LPCWSTR),
            ("lpFile",      ctypes.wintypes.LPCWSTR),
            ("lpParameters",ctypes.wintypes.LPCWSTR),
            ("lpDirectory", ctypes.wintypes.LPCWSTR),
            ("nShow",       ctypes.c_int),
            ("hInstApp",    ctypes.wintypes.HINSTANCE),
            ("lpIDList",    ctypes.c_void_p),
            ("lpClass",     ctypes.wintypes.LPCWSTR),
            ("hkeyClass",   ctypes.c_void_p),
            ("dwHotKey",    ctypes.wintypes.DWORD),
            ("hIcon",       ctypes.wintypes.HANDLE),
            ("hProcess",    ctypes.wintypes.HANDLE),
        ]

    sei = SHELLEXECUTEINFO()
    sei.cbSize      = ctypes.sizeof(SHELLEXECUTEINFO)
    sei.fMask       = SEE_MASK_NOCLOSEPROCESS
    sei.hwnd        = None
    sei.lpVerb      = "runas"
    sei.lpFile      = msi_exe
    sei.lpParameters= params
    sei.lpDirectory = None
    sei.nShow       = 1
    sei.hInstApp    = None

    ok = ctypes.windll.shell32.ShellExecuteExW(ctypes.byref(sei))

    pid = None
    if not ok or not sei.hProcess:
        # Fallback via PowerShell
        try:
            msi_ps  = msi_exe.replace("'", "''")
            args_ps = params.replace("'", "''")
            ps_cmd = "Start-Process -FilePath '{}' -ArgumentList '{}' -Verb RunAs".format(msi_ps, args_ps)
            subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd],
                check=True
            )
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Erro na Atualização", "Falha ao executar instalador:\n{}".format(e))
            return
    else:
        try:
            GetProcessId = ctypes.windll.kernel32.GetProcessId
            GetProcessId.argtypes = [ctypes.wintypes.HANDLE]
            GetProcessId.restype  = ctypes.wintypes.DWORD
            pid = int(GetProcessId(sei.hProcess))
        except Exception:
            pid = None

    # 6) Relançar o app após concluir a instalação
    exe_to_launch = sys.executable
    exe_ps = exe_to_launch.replace("'", "''")
    if pid:
        ps_cmd2 = (
            "$pid={}; ".format(pid) +
            "try { Wait-Process -Id $pid -ErrorAction SilentlyContinue } catch {}; " +
            "Start-Sleep -Seconds 2; " +
            "Start-Process -FilePath '{}'".format(exe_ps)
        )
    else:
        ps_cmd2 = "Start-Sleep -Seconds 20; Start-Process -FilePath '{}'".format(exe_ps)

    DETACHED_PROCESS = 0x00000008
    CREATE_NO_WINDOW = 0x08000000
    try:
        subprocess.Popen(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd2],
            creationflags=DETACHED_PROCESS | CREATE_NO_WINDOW
        )
    except Exception:
        pass

    # 7) Encerrar imediatamente
    os._exit(0)
