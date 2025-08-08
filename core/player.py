# core/player.py

import os
import platform

def open_pdf(filepath):
    # Abre o PDF no visualizador padrão do sistema operacional
    if platform.system() == "Windows":
        os.startfile(filepath)
    elif platform.system() == "Darwin":
        os.system(f"open '{filepath}'")
    else:
        os.system(f"xdg-open '{filepath}'")
