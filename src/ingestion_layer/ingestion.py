from pathlib import Path
from typing import List, Type

from src.config.files_config import Settlements, Transactions, UPIResponses
from src.logger.log import get_logger
from src.utils.file_reader import FileReader
from src.utils.file_writer import FileWriter

logger = get_logger(__name__)

CONFIG_ENTRIES: List[Type] = [Transactions, Settlements, UPIResponses]


def ingest_all_files(force: bool = False) -> List[Path]:
    """Load all configured files and write them into their configured target directories."""
    loaded_paths: List[Path] = []

    for entry in CONFIG_ENTRIES:
        loaded_path = ingest_file(entry, force=force)
        loaded_paths.append(loaded_path)

    return loaded_paths


def ingest_file(entry: Type, force: bool = False) -> Path:
    """Read a configured source file and write it into the configured target directory."""
    source_path = Path(entry.SRC_PATH.value)
    target_dir = Path(entry.TGT_PATH.value)
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / source_path.with_suffix(".parquet").name
    logger.info("Ingesting %s into %s", source_path, target_path)

    reader = FileReader(source_path, file_type=entry.FILE_TYPE.value)
    writer = FileWriter(reader, target_path)
    return writer.write(force=force)

