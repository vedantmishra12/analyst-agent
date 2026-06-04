"""DuckDB database layer — table registration, query execution, schema inspection."""

import duckdb
import polars as pl
import pandas as pd
import io
from pathlib import Path
from typing import Optional
from config.settings import BLOCKED_SQL_KEYWORDS


class DatabaseService:
    def __init__(self):
        self.conn = duckdb.connect(database=":memory:")
        self.tables: dict[str, dict] = {}   # table_name → {file, columns, rows}

    # ── Registration ────────────────────────────────────────────────────────
    def register_file(self, file_bytes: bytes, filename: str) -> str:
        """Load file into DuckDB and return table name."""
        ext  = Path(filename).suffix.lower()
        name = Path(filename).stem.lower().replace(" ", "_").replace("-", "_")

        if ext == ".csv":
            df = pl.read_csv(io.BytesIO(file_bytes), infer_schema_length=10_000, ignore_errors=True)
        elif ext in (".xlsx", ".xls"):
            df = pl.read_excel(io.BytesIO(file_bytes))
        elif ext == ".parquet":
            df = pl.read_parquet(io.BytesIO(file_bytes))
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        self.conn.register(name, df.to_pandas())
        schema = self._build_schema(name, df, filename)
        self.tables[name] = schema
        return name

    def _build_schema(self, name: str, df: pl.DataFrame, filename: str) -> dict:
        cols = []
        for col in df.columns:
            series = df[col]
            cols.append({
                "name":     col,
                "dtype":    str(series.dtype),
                "nulls":    series.null_count(),
                "null_pct": round(series.null_count() / max(len(df), 1) * 100, 1),
                "unique":   series.n_unique(),
            })
        return {
            "file":    filename,
            "table":   name,
            "rows":    len(df),
            "columns": len(df.columns),
            "cols":    cols,
            "df":      df,
        }

    # ── Query Execution ─────────────────────────────────────────────────────
    def validate_sql(self, sql: str) -> tuple[bool, str]:
        upper = sql.upper()
        for kw in BLOCKED_SQL_KEYWORDS:
            if kw in upper:
                return False, f"Blocked keyword: {kw}. Only SELECT queries are allowed."
        if not upper.strip().startswith("SELECT"):
            return False, "Only SELECT queries are allowed."
        return True, ""

    def execute(self, sql: str) -> tuple[Optional[pd.DataFrame], Optional[str]]:
        valid, msg = self.validate_sql(sql)
        if not valid:
            return None, msg
        try:
            result = self.conn.execute(sql).fetchdf()
            return result, None
        except Exception as e:
            return None, str(e)

    # ── Schema ──────────────────────────────────────────────────────────────
    def get_schema_prompt(self) -> str:
        if not self.tables:
            return "No tables loaded."
        lines = []
        for name, meta in self.tables.items():
            lines.append(f"TABLE: {name} ({meta['rows']:,} rows, {meta['columns']} columns)")
            for col in meta["cols"]:
                lines.append(f"  - {col['name']} ({col['dtype']}, {col['null_pct']}% null, {col['unique']} unique)")
        return "\n".join(lines)

    def get_table_names(self) -> list[str]:
        return list(self.tables.keys())

    def clear(self):
        for name in list(self.tables.keys()):
            try:
                self.conn.execute(f"DROP VIEW IF EXISTS {name}")
            except Exception:
                pass
        self.tables = {}
