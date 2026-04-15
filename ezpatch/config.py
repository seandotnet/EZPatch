import os
from pathlib import Path

# core settings
APP_NAME = "EZPatch"
APP_VERSION = "1.0"

# fortnite replay offsets
OFFSET_VERSION = 0x28
BYTES_LENGTH = 4

# magic number for unreal engine replays this never changes 
MAGIC_NUMBER = bytes([0x7F, 0xE2, 0xA2, 0x1C])

# min file size (10kb)
MIN_FILE_SIZE = 10 * 1024

# default paths
DEFAULT_REPLAY_DIR = Path(os.environ.get('LOCALAPPDATA', '')) / 'FortniteGame' / 'Saved' / 'Demos'
LOG_DIR = Path("logs")
