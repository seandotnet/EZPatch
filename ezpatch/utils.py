import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from .config import LOG_DIR

def get_resource_path(relative_path: str) -> Path:
    # get absolute path to resource works for dev and for pyinstaller fr
    try:
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path(os.path.abspath("."))
    
    return base_path / relative_path

def setup_logging(log_level_str: str) -> logging.Logger:
    # setup the logger for the app fr
    LOG_DIR.mkdir(exist_ok=True)
    
    # map string to logging level
    level = logging.DEBUG if log_level_str.lower() == "debug" else logging.INFO
    
    # create logger
    logger = logging.getLogger("EZPatch")
    logger.setLevel(level)
    
    # clear existing handlers so we dont get duplicates lol
    if logger.hasHandlers():
        logger.handlers.clear()
        
    log_filename = LOG_DIR / f"ezpatch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # file handler
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(level)
    
    # console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_latest_replay(folder_path: Path) -> Path | None:
    # finds the newest replay file in a folder
    if not folder_path.exists() or not folder_path.is_dir():
        return None
        
    replays = list(folder_path.glob("*.replay"))
    if not replays:
        return None
        
    # sort by modified time
    return max(replays, key=lambda p: p.stat().st_mtime)
