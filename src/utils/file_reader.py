from pathlib import Path
from typing import Any, Dict, Optional, Union

import pandas as pd

from src.logger.log import get_logger

logger = get_logger()


class FileReader:
    SUPPORTED_TYPES = {"csv", "json"}

    def __init__(self, file_path: Union[str, Path], file_type: Optional[str] = None, **read_kwargs: Any):
        self.file_path = Path(file_path)
        self.file_type = (file_type or self.file_path.suffix.lstrip('.')).lower()
        self._data: Optional[pd.DataFrame] = None
        self._read_kwargs: Dict[str, Any] = read_kwargs
        self._validate()

    def _validate(self) -> None:
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        if not self.file_path.is_file():
            raise ValueError(f"Expected a file path, got a directory: {self.file_path}")

        if self.file_type not in self.SUPPORTED_TYPES:
            raise ValueError(
                f"Unsupported file type '{self.file_type}' for {self.file_path}. "
                f"Supported types are: {sorted(self.SUPPORTED_TYPES)}"
            )

    def load(self, *, force: bool = False) -> pd.DataFrame:
        if self._data is not None and not force:
            return self._data

        try:
            if self.file_type == "csv":
                self._data = pd.read_csv(self.file_path, **self._read_kwargs)
            else:
                self._data = pd.read_json(self.file_path, **self._read_kwargs)

        except Exception as exc:
            logger.exception("Unable to read %s file: %s", self.file_type, self.file_path)
            raise RuntimeError(
                f"Could not load {self.file_type.upper()} file '{self.file_path}': {exc}"
            ) from exc

        return self._data

    @property
    def data(self) -> pd.DataFrame:
        return self.load()

    def reload(self) -> pd.DataFrame:
        return self.load(force=True)
               

     

     