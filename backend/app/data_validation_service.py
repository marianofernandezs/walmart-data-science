from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from .storage_service import EXPECTED_SCHEMA_PATH, ensure_storage_layout


REQUIRED_COLUMNS = [
    "sku",
    "store_id",
    "category",
    "date",
    "current_stock",
    "price",
    "snap_day",
    "event_day",
    "sales",
]
ALLOWED_CATEGORIES = ["FOODS", "HOBBIES", "HOUSEHOLD"]


def ensure_expected_schema() -> Path:
    ensure_storage_layout()
    if not EXPECTED_SCHEMA_PATH.exists():
        schema = {
            "required_columns": REQUIRED_COLUMNS,
            "allowed_categories": ALLOWED_CATEGORIES,
            "validations": {
                "date": "YYYY-MM-DD",
                "current_stock": ">= 0",
                "price": "> 0",
                "snap_day": "0 or 1",
                "event_day": "0 or 1",
                "sales": ">= 0",
            },
        }
        EXPECTED_SCHEMA_PATH.write_text(json.dumps(schema, indent=2), encoding="utf-8")
    return EXPECTED_SCHEMA_PATH


def get_expected_schema() -> dict[str, Any]:
    path = ensure_expected_schema()
    return json.loads(path.read_text(encoding="utf-8"))


def validate_required_columns(df: pd.DataFrame) -> list[str]:
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    return [f"Missing required columns: {missing}"] if missing else []


def validate_data_types(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    converted = df.copy()
    errors: list[str] = []
    for column in ["current_stock", "price", "snap_day", "event_day", "sales"]:
        converted[column] = pd.to_numeric(converted[column], errors="coerce")
    for column in ["sku", "store_id", "category", "date"]:
        converted[column] = converted[column].astype(str).str.strip()
    if converted[["current_stock", "price", "snap_day", "event_day", "sales"]].isna().any().any():
        errors.append("Some numeric fields could not be parsed")
    return converted, errors


def validate_value_ranges(df: pd.DataFrame) -> list[str]:
    errors = []
    if not df["category"].isin(ALLOWED_CATEGORIES).all():
        errors.append(f"Category must be one of {ALLOWED_CATEGORIES}")
    if not (df["current_stock"] >= 0).fillna(False).all():
        errors.append("current_stock must be >= 0")
    if not (df["price"] > 0).fillna(False).all():
        errors.append("price must be > 0")
    if not df["snap_day"].isin([0, 1]).all():
        errors.append("snap_day must be 0 or 1")
    if not df["event_day"].isin([0, 1]).all():
        errors.append("event_day must be 0 or 1")
    if not (df["sales"] >= 0).fillna(False).all():
        errors.append("sales must be >= 0")
    return errors


def validate_dates(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    converted = df.copy()
    parsed = pd.to_datetime(converted["date"], format="%Y-%m-%d", errors="coerce")
    converted["date"] = parsed.dt.strftime("%Y-%m-%d")
    if parsed.isna().any():
        return converted, ["date must use format YYYY-MM-DD"]
    return converted, []


def split_valid_invalid_rows(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    checks = pd.Series(True, index=df.index)
    checks &= df["sku"].astype(str).str.len() > 0
    checks &= df["store_id"].astype(str).str.len() > 0
    checks &= df["category"].isin(ALLOWED_CATEGORIES)
    checks &= df["current_stock"].ge(0)
    checks &= df["price"].gt(0)
    checks &= df["snap_day"].isin([0, 1])
    checks &= df["event_day"].isin([0, 1])
    checks &= df["sales"].ge(0)
    checks &= pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce").notna()
    valid_df = df[checks].copy()
    invalid_df = df[~checks].copy()
    return valid_df, invalid_df


def build_validation_summary(df_valid: pd.DataFrame, df_invalid: pd.DataFrame, errors: list[str]) -> dict[str, Any]:
    status = "success"
    if len(df_valid) == 0:
        status = "error"
    elif len(df_invalid) > 0 or errors:
        status = "partial_success"
    return {
        "status": status,
        "rows_received": int(len(df_valid) + len(df_invalid)),
        "rows_valid": int(len(df_valid)),
        "rows_rejected": int(len(df_invalid)),
        "validation_errors": errors,
        "validated_at": datetime.now().isoformat(),
    }
