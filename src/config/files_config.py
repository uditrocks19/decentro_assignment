from pathlib import Path
from enum import Enum

class Transactions(str, Enum):
    """Simple file and directory constants."""
    SRC_PATH = "src/src_files/transactions.csv"
    TGT_PATH = "src/bronze/"
    FILE_TYPE = "csv"

class Settlements(str, Enum):
    """Simple file and directory constants."""
    SRC_PATH = "src/src_files/settlements.csv"
    TGT_PATH = "src/bronze/"
    FILE_TYPE = "csv"

class UPIResponses(str, Enum):
    """Simple file and directory constants."""
    SRC_PATH = "src/src_files/upi_responses.json"
    TGT_PATH = "src/bronze/"
    FILE_TYPE = "json"