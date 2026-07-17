from pathlib import Path
from typing import Optional, Union

from src.logger.log import get_logger
from src.utils.file_reader import FileReader

logger = get_logger()


class FileWriter:
    SUPPORTED_TYPES = {"csv", "json"}

    def __init__(
        self,
        reader: FileReader,
        target_path: Union[str, Path],
        file_type: Optional[str] = None,
        make_dirs: bool = True,
        **write_kwargs,
    ):
        if not isinstance(reader, FileReader):
            raise TypeError("FileWriter requires a FileReader instance")

        self.reader = reader
        self.target_path = Path(target_path)
        self.file_type = (file_type or self.target_path.suffix.lstrip('.')).lower()
        self._write_kwargs = write_kwargs
        self._make_dirs = make_dirs

        self._validate_target()

    def _validate_target(self) -> None:
        if self.file_type not in self.SUPPORTED_TYPES:
            raise ValueError(
                f"Unsupported target file type '{self.file_type}'. "
                f"Supported types are: {sorted(self.SUPPORTED_TYPES)}"
            )

        if self.target_path.exists() and self.target_path.is_dir():
            raise ValueError(
                f"Target path must be a file path, not a directory: {self.target_path}"
            )

        parent = self.target_path.parent
        if parent and not parent.exists():
            if self._make_dirs:
                parent.mkdir(parents=True, exist_ok=True)
                logger.debug("Created target directory %s", parent)
            else:
                raise FileNotFoundError(
                    f"Target directory does not exist: {parent}"
                )

    def write(self, *, force: bool = False) -> Path:
        df = self.reader.reload() if force else self.reader.data

        try:
            if self.file_type == "csv":
                df.to_csv(self.target_path, index=False, **self._write_kwargs)
            else:
                df.to_json(self.target_path, orient="records", lines=True, **self._write_kwargs)

        except Exception as exc:
            logger.exception("Failed to write %s file to %s", self.file_type, self.target_path)
            raise RuntimeError(
                f"Could not write {self.file_type.upper()} file '{self.target_path}': {exc}"
            ) from exc

        logger.info("Wrote %s file to %s", self.file_type, self.target_path)
        return self.target_path


def write_reader_data(
    reader: FileReader,
    target_path: Union[str, Path],
    file_type: Optional[str] = None,
    **write_kwargs,
) -> Path:
    writer = FileWriter(reader, target_path, file_type=file_type, **write_kwargs)
    return writer.write()
