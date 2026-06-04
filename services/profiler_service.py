"""Data profiling — auto-generates statistics, outliers, top values."""

import polars as pl
import pandas as pd
import numpy as np
from typing import Any


class ProfilerService:
    def profile(self, df: pl.DataFrame, table_name: str) -> dict:
        rows, cols = df.shape
        numeric_cols  = [c for c in df.columns if df[c].dtype in (pl.Float64, pl.Float32, pl.Int64, pl.Int32, pl.Int16, pl.Int8, pl.UInt64, pl.UInt32)]
        cat_cols      = [c for c in df.columns if df[c].dtype == pl.Utf8 or df[c].dtype == pl.Categorical]
        date_cols     = [c for c in df.columns if df[c].dtype in (pl.Date, pl.Datetime)]

        missing_total = sum(df[c].null_count() for c in df.columns)
        dup_count     = rows - df.unique().shape[0]

        col_profiles = []
        for col in df.columns:
            series   = df[col]
            dtype    = str(series.dtype)
            nulls    = series.null_count()
            null_pct = round(nulls / max(rows, 1) * 100, 1)
            unique   = series.n_unique()

            profile: dict[str, Any] = {
                "name":     col,
                "dtype":    dtype,
                "nulls":    nulls,
                "null_pct": null_pct,
                "unique":   unique,
            }

            if col in numeric_cols:
                clean = series.drop_nulls()
                if len(clean) > 0:
                    desc = clean.describe()
                    profile.update({
                        "mean":     round(float(clean.mean()), 4),
                        "median":   round(float(clean.median()), 4),
                        "std":      round(float(clean.std()), 4),
                        "min":      float(clean.min()),
                        "max":      float(clean.max()),
                        "outliers": self._count_outliers(clean),
                    })

            elif col in cat_cols:
                top = series.drop_nulls().value_counts().sort("count", descending=True).head(5)
                profile["top_values"] = [
                    {"value": str(r[col]), "count": int(r["count"])}
                    for r in top.iter_rows(named=True)
                ]

            col_profiles.append(profile)

        return {
            "table":          table_name,
            "rows":           rows,
            "cols":           cols,
            "numeric_cols":   numeric_cols,
            "cat_cols":       cat_cols,
            "date_cols":      date_cols,
            "missing_total":  missing_total,
            "missing_pct":    round(missing_total / max(rows * cols, 1) * 100, 1),
            "duplicates":     dup_count,
            "completeness":   round((1 - missing_total / max(rows * cols, 1)) * 100, 1),
            "col_profiles":   col_profiles,
        }

    def _count_outliers(self, series: pl.Series) -> int:
        try:
            q1  = series.quantile(0.25)
            q3  = series.quantile(0.75)
            iqr = q3 - q1
            return int(((series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)).sum())
        except Exception:
            return 0

    def profile_to_text(self, profile: dict) -> str:
        lines = [
            f"Table: {profile['table']}",
            f"Rows: {profile['rows']:,} | Columns: {profile['cols']}",
            f"Completeness: {profile['completeness']}% | Duplicates: {profile['duplicates']:,}",
            "",
            "Column Summary:",
        ]
        for cp in profile["col_profiles"]:
            line = f"  {cp['name']} ({cp['dtype']}) — {cp['null_pct']}% null, {cp['unique']} unique"
            if "mean" in cp:
                line += f", mean={cp['mean']}, min={cp['min']}, max={cp['max']}, outliers={cp['outliers']}"
            if "top_values" in cp:
                tops = ", ".join([f"{v['value']}({v['count']})" for v in cp["top_values"][:3]])
                line += f", top: [{tops}]"
            lines.append(line)
        return "\n".join(lines)
