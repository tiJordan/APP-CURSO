# core/progress.py

import os
import json
from settings import STATUS_DIR

def get_user_status_file(usuario):
    os.makedirs(STATUS_DIR, exist_ok=True)
    return os.path.join(STATUS_DIR, f'status_{usuario}.json')

def load_status(usuario):
    fpath = get_user_status_file(usuario)
    if os.path.exists(fpath):
        with open(fpath, 'r') as f:
            return json.load(f)
    return {}

def save_status(usuario, status):
    fpath = get_user_status_file(usuario)
    with open(fpath, 'w') as f:
        json.dump(status, f, indent=2)
