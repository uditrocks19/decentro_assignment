from src.logger.log import get_logger
from src.utils.oracle_connector import OracleConnector
from src.utils.file_reader import FileReader


class ZeroRowsLoaded(Exception):
    pass

logger = get_logger()

def load_data_into_db(
    source_path: str = "src/silver/reconciled.parquet",
    table_name: str = "RECONCILLATION_PAYMENTS",
) -> int:
    """Read reconciled parquet and load it into Oracle."""
    file_reader = FileReader(source_path)
    df = file_reader.load()
    connector = OracleConnector()

    try:
        row_cnt = connector.write_dataframe(df, table_name)
        if row_cnt == 0:
            raise ZeroRowsLoaded("No rows loaded into Oracle")
        return row_cnt

    except Exception:
        logger.exception("Error loading data to Oracle")
        raise

    finally:
        connector.close()


