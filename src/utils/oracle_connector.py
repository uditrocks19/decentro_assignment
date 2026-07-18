import os
from typing import Optional

import oracledb
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class OracleConnector:
    """Simple Oracle helper to connect to Oracle and write a DataFrame."""

    def __init__(
        self,
        user: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        service_name: Optional[str] = None,
        dsn: Optional[str] = None,
    ):
        self.user = user or os.getenv("ORACLE_USERNAME")
        self.password = password or os.getenv("ORACLE_PASSWORD")
        self.host = host or os.getenv("ORACLE_HOST")
        self.port = port or self._get_port_from_env()
        self.service_name = service_name or os.getenv("ORACLE_SERVICE_NAME")
        self.dsn = dsn or os.getenv("ORACLE_DSN")
        self._connection: Optional[oracledb.Connection] = None

        if not self.user:
            raise ValueError("Oracle username is required.")
        if not self.dsn and not (self.host and self.port and self.service_name):
            raise ValueError(
                "Oracle connection settings are incomplete. "
                "Set ORACLE_HOST, ORACLE_PORT, ORACLE_SERVICE_NAME or ORACLE_DSN."
            )

    def _get_port_from_env(self) -> Optional[int]:
        port_value = os.getenv("ORACLE_PORT")
        if not port_value:
            return None
        return int(port_value)

    def _make_dsn(self) -> str:
        if self.dsn:
            return self.dsn
        assert self.host and self.port and self.service_name
        return oracledb.makedsn(self.host, self.port, service_name=self.service_name)

    def connect(self) -> oracledb.Connection:
        if self._connection is not None:
            return self._connection

        self._connection = oracledb.connect(
            user=self.user,
            password=self.password,
            dsn=self._make_dsn(),
        )
        return self._connection

    def close(self) -> None:
        if self._connection is None:
            return

        try:
            self._connection.close()
        except oracledb.InterfaceError:
            # Connection may already be closed or not connected.
            pass
        finally:
            self._connection = None

    def write_dataframe(
        self,
        df: pd.DataFrame,
        table_name: str,
        if_exists: str = "append",
        batch_size: int = 1000,
    ) -> int:
        """Write a DataFrame into an Oracle table."""
        if df.empty:
            return 0

        if if_exists not in {"append", "replace", "fail"}:
            raise ValueError("if_exists must be 'append', 'replace', or 'fail'.")

        table_name = table_name.strip().upper()
        conn = self.connect()
        cursor = conn.cursor()

        if if_exists == "replace":
            cursor.execute(f"DROP TABLE {table_name}")
            conn.commit()

        columns = [col.strip().upper().replace(" ", "_") for col in df.columns]
        column_list = ", ".join(columns)
        placeholders = ", ".join(f":{idx}" for idx in range(1, len(columns) + 1))
        insert_sql = f"INSERT INTO {table_name} ({column_list}) VALUES ({placeholders})"

        rows = [tuple(None if pd.isna(value) else value for value in row)
                for row in df.itertuples(index=False, name=None)]

        cursor.executemany(insert_sql, rows, batcherrors=True)
        batch_errors = cursor.getbatcherrors()
        if batch_errors:
            error_messages = "; ".join(
                f"row {err.offset}: {err.message}" for err in batch_errors
            )
            cursor.close()
            raise RuntimeError(f"Batch insert errors: {error_messages}")

        conn.commit()
        inserted = cursor.rowcount
        if inserted <= 0:
            inserted = len(rows)
        cursor.close()
        return inserted

