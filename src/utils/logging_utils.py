import os
import json
import datetime
from ..config.settings import DATA_DIR, OUT_DIR, GEN_BG_DIR

def log_transaction(data):
    """
    Log transaction data to history.json.
    """
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
    log_file = os.path.join(DATA_DIR, "history.json")
    try:
        with open(log_file, "r", encoding="utf-8") as f: history = json.load(f)
    except: history = [] 
    data["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history.append(data)
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

def ensure_directories_exist():
    """
    Ensure all necessary directories exist.
    """
    if not os.path.exists(OUT_DIR): os.makedirs(OUT_DIR)
    if not os.path.exists(GEN_BG_DIR): os.makedirs(GEN_BG_DIR)
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
    if not os.path.exists("assets/screenshots"): os.makedirs("assets/screenshots")
    if not os.path.exists("assets/mockups"): os.makedirs("assets/mockups")
