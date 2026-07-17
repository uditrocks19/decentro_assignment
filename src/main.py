from pathlib import Path

from src.logger.log import get_logger
from src.ingestion_layer.ingestion import ingest_all_files
from src.silver_layer.processing import load_bronze_parquet_data, process_reconciliation

logger = get_logger(__name__)


def main() -> None:
    """Run the ingestion and processing pipeline."""
    logger.info("Pipeline start")

    try:
        ingest_all_files()
        transactions, settlements, upi = load_bronze_parquet_data()
        reconciled_path = process_reconciliation(transactions, settlements, upi)
        logger.info("Pipeline complete. Reconciled file written to %s", reconciled_path)
    except Exception as exc:
        logger.exception("Pipeline failed: %s", exc)
        raise


if __name__ == "__main__":
    main()
