from pathlib import Path

import duckdb


def test_reconciled_parquet_can_be_queried():
    repo_root = Path(__file__).resolve().parents[1]
    parquet_path = repo_root / "src" / "silver" / "reconciled.parquet"

    assert parquet_path.exists(), f"Expected reconciled Parquet file at {parquet_path}"

    query = f"SELECT txn_id, internal_amount, settled_amount, difference, status FROM read_parquet('{parquet_path.as_posix()}')"
    con = duckdb.connect(database=":memory:")
    result_df = con.execute(query).df()

    assert not result_df.empty, "DuckDB query returned no rows from reconciled Parquet"
    expected_columns = {"txn_id", "internal_amount", "settled_amount", "difference", "status"}
    assert expected_columns.issubset(result_df.columns), f"Missing expected columns: {expected_columns - set(result_df.columns)}"
    assert result_df["status"].isin(["matched", "mismatch", "missing_in_settlement"]).all(), "Unexpected status values found"
