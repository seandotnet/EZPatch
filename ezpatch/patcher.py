import os
import shutil
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Tuple, List

from .config import (
    MAGIC_NUMBER, OFFSET_VERSION, 
    BYTES_LENGTH, MIN_FILE_SIZE
)

@dataclass
class VersionInfo:
    version_bytes: bytes

@dataclass
class PatchResult:
    success: bool
    message: str
    file_path: Path

class ReplayPatcher:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        
    def validate_replay(self, file_path: Path) -> bool:
        # checks if a file is a valid fortnite replay 
        try:
            if not file_path.exists() or file_path.stat().st_size < MIN_FILE_SIZE:
                return False
                
            with open(file_path, 'rb') as f:
                header = f.read(len(MAGIC_NUMBER))
                
            return header == MAGIC_NUMBER
        except Exception as e:
            self.logger.error(f"failed to validate {file_path.name}: {e}")
            return False

    def extract_version(self, file_path: Path) -> VersionInfo | None:
        # grabs the version bytes from a working replay
        try:
            with open(file_path, 'rb') as f:
                f.seek(OFFSET_VERSION)
                version_bytes = f.read(BYTES_LENGTH)
                
            return VersionInfo(version_bytes)
        except Exception as e:
            self.logger.error(f"failed to extract version from {file_path.name}: {e}")
            return None

    def process_file(
        self, 
        broken_path: Path, 
        version_info: VersionInfo, 
        keep_originals: bool = True,
        move_to_backups: bool = True,
        overwrite_patched: bool = False,
        skip_old_seasons: bool = False
    ) -> PatchResult:
        # the main logic to patch a single replay file
        try:
            filename = broken_path.name
            
            if not self.validate_replay(broken_path):
                return PatchResult(False, "invalid replay format", broken_path)
                
            # read the broken file
            with open(broken_path, 'rb') as f:
                file_bytes = bytearray(f.read())
                
            # check current bytes
            current_version = file_bytes[OFFSET_VERSION:OFFSET_VERSION + BYTES_LENGTH]
            
            needs_version_update = current_version != version_info.version_bytes
            
            # skip if already current
            if not needs_version_update:
                return PatchResult(False, "already up to date", broken_path)
                
            # skip old seasons if user wants to
            if skip_old_seasons and needs_version_update:
                return PatchResult(False, "skipped old season", broken_path)
                
            # update the bytes 
            if needs_version_update:
                file_bytes[OFFSET_VERSION:OFFSET_VERSION + BYTES_LENGTH] = version_info.version_bytes
                
            # handle output path
            if filename.startswith("PatchedEZ_") and not overwrite_patched:
                return PatchResult(False, "skipped previously patched file", broken_path)
                
            output_name = filename if filename.startswith("PatchedEZ_") else f"PatchedEZ_{filename}"
            output_path = broken_path.parent / output_name
            
            # write the patched file
            with open(output_path, 'wb') as f:
                f.write(file_bytes)
                
            # handle the original file if we made a new one
            if broken_path != output_path:
                if not keep_originals:
                    broken_path.unlink()
                    self.logger.debug(f"deleted original: {filename}")
                elif move_to_backups:
                    backup_dir = broken_path.parent / "Backups"
                    backup_dir.mkdir(exist_ok=True)
                    backup_path = backup_dir / filename
                    
                    if backup_path.exists():
                        broken_path.unlink()
                        self.logger.debug(f"backup exists, deleted original: {filename}")
                    else:
                        shutil.move(str(broken_path), str(backup_path))
                        self.logger.debug(f"moved to backup: {filename}")
                        
            return PatchResult(True, "successfully patched", broken_path)
            
        except Exception as e:
            self.logger.error(f"error processing {broken_path.name}: {e}")
            return PatchResult(False, f"error: {str(e)}", broken_path)
