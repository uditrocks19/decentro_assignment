from pathlib import Path
from enum import Enum


class FileConfig(str, Enum):
    """Simple file and directory constants."""

    BANK_RETURNS_CSV = "bank_returns.csv"
    SOURCE_DIR = "source_dir"
    TARGET_DIR = "target_dir"
    APP_LOG = "app.log"

    @property
    def file_type(self) -> str:
        return Path(self.value).suffix.lstrip(".").lower()
