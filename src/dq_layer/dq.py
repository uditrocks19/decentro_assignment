from pathlib import Path
from typing import Dict, List, Tuple, Union

import pandas as pd

from src.logger.log import get_logger

logger = get_logger(__name__)


def _find_negative_amounts(df: pd.DataFrame, column: str) -> pd.DataFrame:
    if column not in df.columns:
        return pd.DataFrame(columns=df.columns)
    values = pd.to_numeric(df[column], errors="coerce")
    return df[values < 0].copy()


def _find_missing_required_columns(df: pd.DataFrame, required_columns: List[str]) -> pd.DataFrame:
    missing = [col for col in required_columns if col not in df.columns]
    if not missing:
        return pd.DataFrame(columns=df.columns)

    logger.warning("Missing required columns: %s", missing)
    return pd.DataFrame()


def find_bad_data(
    transactions: pd.DataFrame,
    settlements: pd.DataFrame,
    upi: pd.DataFrame,
) -> Dict[str, pd.DataFrame]:
    """Detect bad records in the bronze datasets."""
    bad_data: Dict[str, pd.DataFrame] = {}

    bad_transactions = _find_negative_amounts(transactions, "amount")
    if not bad_transactions.empty:
        bad_data["transactions"] = bad_transactions

    bad_settlements = _find_negative_amounts(settlements, "settled_amount")
    if not bad_settlements.empty:
        bad_data["settlements"] = bad_settlements

    return bad_data


def write_bad_data(
    bad_data: Dict[str, pd.DataFrame],
    target_dir: Union[str, Path] = "src/bad_data",
) -> Path:
    """Write bad data records into Parquet files under target_dir."""
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    for name, df in bad_data.items():
        if df.empty:
            continue
        target_path = target_dir / f"bad_{name}.parquet"
        df.to_parquet(target_path, index=False)
        logger.info("Written bad data for %s to %s", name, target_path)

    return target_dir
