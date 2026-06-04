from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
INGESTED_DIR = DATA_DIR / "ingested"
RAW_DIR = INGESTED_DIR / "raw"
PROCESSED_DIR = INGESTED_DIR / "processed"
REJECTED_DIR = INGESTED_DIR / "rejected"
SCHEMA_DIR = DATA_DIR / "schema"
EXPECTED_SCHEMA_PATH = SCHEMA_DIR / "expected_columns.json"


def ensure_storage_layout() -> None:
    for directory in (RAW_DIR, PROCESSED_DIR, REJECTED_DIR, SCHEMA_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def timestamp_slug() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def build_storage_name(prefix: str, original_name: str, suffix: str = ".csv") -> str:
    safe_name = Path(original_name).stem.replace(" ", "_").replace("/", "_")
    return f"{timestamp_slug()}_{prefix}_{safe_name}{suffix}"


def save_dataframe(df: pd.DataFrame, directory: Path, filename: str) -> Path:
    ensure_storage_layout()
    path = directory / filename
    df.to_csv(path, index=False)
    return path


def save_uploaded_bytes(content: bytes, filename: str) -> Path:
    ensure_storage_layout()
    path = RAW_DIR / filename
    path.write_bytes(content)
    return path


def list_ingested_files() -> list[dict[str, Any]]:
    ensure_storage_layout()
    results: list[dict[str, Any]] = []
    for category, directory in (("raw", RAW_DIR), ("processed", PROCESSED_DIR), ("rejected", REJECTED_DIR)):
        for path in sorted(directory.glob("*.csv"), reverse=True):
            rows = None
            try:
                rows = len(pd.read_csv(path))
            except Exception:
                rows = None
            results.append(
                {
                    "filename": path.name,
                    "category": category,
                    "created_at": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
                    "rows": rows,
                }
            )
    return results


def get_processed_file(filename: str | None = None) -> Path | None:
    ensure_storage_layout()
    if filename:
        candidate = (PROCESSED_DIR / filename).resolve()
        if PROCESSED_DIR.resolve() not in candidate.parents and candidate != PROCESSED_DIR.resolve():
            return None
        return candidate if candidate.exists() else None
    files = sorted(PROCESSED_DIR.glob("*.csv"), key=lambda path: path.stat().st_mtime, reverse=True)
    return files[0] if files else None


def read_processed_dataframe(filename: str | None = None) -> pd.DataFrame:
    path = get_processed_file(filename)
    if not path:
        return pd.DataFrame()
    return pd.read_csv(path)


def delete_ingested_file(filename: str) -> bool:
    ensure_storage_layout()
    for directory in (RAW_DIR, PROCESSED_DIR, REJECTED_DIR):
        candidate = (directory / filename).resolve()
        if directory.resolve() not in candidate.parents:
            continue
        if candidate.exists():
            candidate.unlink()
            return True
    return False


def clear_ingested_files() -> dict[str, int]:
    ensure_storage_layout()
    deleted_counts = {"raw": 0, "processed": 0, "rejected": 0}
    for category, directory in (("raw", RAW_DIR), ("processed", PROCESSED_DIR), ("rejected", REJECTED_DIR)):
        for path in directory.glob("*.csv"):
            path.unlink(missing_ok=True)
            deleted_counts[category] += 1
    return deleted_counts
