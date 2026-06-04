from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

import pandas as pd

from .data_validation_service import (
    build_validation_summary,
    get_expected_schema,
    validate_data_types,
    validate_dates,
    validate_required_columns,
    validate_value_ranges,
    split_valid_invalid_rows,
)
from .feature_service import normalize_processed_ingestion
from .schemas import IngestionRecord
from .storage_service import (
    PROCESSED_DIR,
    RAW_DIR,
    REJECTED_DIR,
    build_storage_name,
    clear_ingested_files,
    delete_ingested_file,
    get_processed_file,
    read_processed_dataframe,
    list_ingested_files,
    save_dataframe,
    save_uploaded_bytes,
)


class IngestionService:
    def get_schema(self) -> dict[str, Any]:
        return get_expected_schema()

    def process_csv_upload(self, filename: str, content: bytes) -> dict[str, Any]:
        if not filename.lower().endswith(".csv"):
            return {
                "filename": filename,
                "status": "error",
                "rows_received": 0,
                "rows_valid": 0,
                "rows_rejected": 0,
                "processed_file": None,
                "rejected_file": None,
                "validation_errors": ["Only .csv files are allowed"],
            }

        raw_filename = build_storage_name("raw", filename)
        save_uploaded_bytes(content, raw_filename)
        df = pd.read_csv(BytesIO(content))
        return self._process_dataframe(df, filename)

    def process_json_records(self, records: list[IngestionRecord]) -> dict[str, Any]:
        rows = []
        for record in records:
            base = record.model_dump(exclude={"extra_fields"})
            merged = {**(record.extra_fields or {}), **base}
            rows.append(merged)
        df = pd.DataFrame(rows)
        return self._process_dataframe(df, "json_ingestion.csv")

    def _process_dataframe(self, df: pd.DataFrame, original_name: str) -> dict[str, Any]:
        errors = validate_required_columns(df)
        if errors:
            return {
                "filename": original_name,
                "status": "error",
                "rows_received": int(len(df)),
                "rows_valid": 0,
                "rows_rejected": int(len(df)),
                "processed_file": None,
                "rejected_file": None,
                "validation_errors": errors,
            }

        typed_df, type_errors = validate_data_types(df)
        dated_df, date_errors = validate_dates(typed_df)
        range_errors = validate_value_ranges(dated_df)
        valid_df, invalid_df = split_valid_invalid_rows(dated_df)

        if not valid_df.empty:
            valid_df = normalize_processed_ingestion(valid_df)

        summary = build_validation_summary(valid_df, invalid_df, [*type_errors, *date_errors, *range_errors])
        processed_file = None
        rejected_file = None

        if not valid_df.empty:
            processed_filename = build_storage_name("processed", original_name)
            processed_file = save_dataframe(valid_df, PROCESSED_DIR, processed_filename).name

        if not invalid_df.empty:
            rejected_filename = build_storage_name("rejected", original_name)
            rejected_file = save_dataframe(invalid_df, REJECTED_DIR, rejected_filename).name

        return {
            "filename": original_name,
            "status": summary["status"],
            "rows_received": summary["rows_received"],
            "rows_valid": summary["rows_valid"],
            "rows_rejected": summary["rows_rejected"],
            "processed_file": processed_file,
            "rejected_file": rejected_file,
            "validation_errors": summary["validation_errors"],
        }

    def list_files(self) -> list[dict[str, Any]]:
        return list_ingested_files()

    def preview(self, filename: str | None = None) -> dict[str, Any]:
        path = get_processed_file(filename)
        if not path:
            return {"filename": "", "rows": []}
        df = pd.read_csv(path).head(10)
        return {"filename": path.name, "rows": df.to_dict(orient="records")}

    def delete_file(self, filename: str) -> bool:
        return delete_ingested_file(filename)

    def get_processed_rows(self, filename: str | None = None) -> list[dict[str, Any]]:
        df = read_processed_dataframe(filename)
        if df.empty:
            return []
        return df.to_dict(orient="records")

    def clear_all(self) -> dict[str, Any]:
        deleted = clear_ingested_files()
        return {
            "status": "cleared",
            "deleted": deleted,
        }


ingestion_service = IngestionService()
