from pathlib import Path
from typing import Union

from src.logger.log import get_logger
from src.utils.file_reader import FileReader

logger = get_logger()


class FileWriter:
    """Writes data from a FileReader into Parquet format."""

    def __init__(
        self,
        reader: FileReader,
        target_path: Union[str, Path],
        make_dirs: bool = True,
        **write_kwargs,
    ):
        if not isinstance(reader, FileReader):
            raise TypeError("FileWriter requires a FileReader instance")

        self.reader = reader
        self.target_path = Path(target_path)
        self._write_kwargs = write_kwargs
        self._make_dirs = make_dirs

        self._prepare_target()

    def _prepare_target(self) -> None:
        if self.target_path.exists() and self.target_path.is_dir():
            raise ValueError(
                f"Target path must be a file path, not a directory: {self.target_path}"
            )

        if self.target_path.suffix.lower() != ".parquet":
            self.target_path = self.target_path.with_suffix(".parquet")

        parent = self.target_path.parent
        if parent and not parent.exists():
            if self._make_dirs:
                parent.mkdir(parents=True, exist_ok=True)
                logger.debug("Created target directory %s", parent)
            else:
                raise FileNotFoundError(f"Target directory does not exist: {parent}")

    def write(self, *, force: bool = False) -> Path:
        df = self.reader.reload() if force else self.reader.data

        try:
            df.to_parquet(self.target_path, index=False, **self._write_kwargs)
        except Exception as exc:
            logger.exception("Failed to write Parquet file to %s", self.target_path)
            raise RuntimeError(
                f"Could not write Parquet file '{self.target_path}': {exc}"
            ) from exc

        logger.info("Wrote Parquet file to %s", self.target_path)
        return self.target_path


def write_reader_data(
    reader: FileReader,
    target_path: Union[str, Path],
    **write_kwargs,
) -> Path:
    writer = FileWriter(reader, target_path, **write_kwargs)
    return writer.write()
