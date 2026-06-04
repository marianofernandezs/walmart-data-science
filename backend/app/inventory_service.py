from __future__ import annotations

from pathlib import Path

import pandas as pd

from .feature_service import normalize_processed_ingestion
from .schemas import AlertRecord, ProductRecord
from .storage_service import PROCESSED_DIR, ensure_storage_layout


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
PRODUCTS_CSV = DATA_DIR / "sample_products.csv"


SAMPLE_PRODUCTS = [
    {"sku": "FOODS_1_001", "store_id": "CA_1", "category": "FOODS", "dept_id": "FOODS_1", "state_id": "CA", "current_stock": 120, "price": 3.99},
    {"sku": "FOODS_1_045", "store_id": "TX_1", "category": "FOODS", "dept_id": "FOODS_1", "state_id": "TX", "current_stock": 60, "price": 5.49},
    {"sku": "HOUSEHOLD_1_210", "store_id": "WI_1", "category": "HOUSEHOLD", "dept_id": "HOUSEHOLD_1", "state_id": "WI", "current_stock": 85, "price": 8.99},
    {"sku": "HOBBIES_1_088", "store_id": "CA_2", "category": "HOBBIES", "dept_id": "HOBBIES_1", "state_id": "CA", "current_stock": 40, "price": 12.50},
    {"sku": "FOODS_2_014", "store_id": "TX_2", "category": "FOODS", "dept_id": "FOODS_2", "state_id": "TX", "current_stock": 140, "price": 2.99},
]


def ensure_sample_products() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not PRODUCTS_CSV.exists():
        pd.DataFrame(SAMPLE_PRODUCTS).to_csv(PRODUCTS_CSV, index=False)
    return PRODUCTS_CSV


def get_products_df() -> pd.DataFrame:
    csv_path = ensure_sample_products()
    base_df = pd.read_csv(csv_path)
    ensure_storage_layout()
    processed_frames = []
    for path in sorted(PROCESSED_DIR.glob("*.csv")):
        try:
            processed_frames.append(pd.read_csv(path))
        except Exception:
            continue
    if processed_frames:
        ingested_df = normalize_processed_ingestion(pd.concat(processed_frames, ignore_index=True))
        merged = pd.concat([base_df, ingested_df], ignore_index=True, sort=False)
        merged = merged.drop_duplicates(subset=["sku", "store_id"], keep="last")
        return merged
    return base_df


def list_products() -> list[ProductRecord]:
    df = get_products_df()
    normalized_rows = []
    for row in df.to_dict(orient="records"):
        normalized_rows.append(
            {
                key: (None if pd.isna(value) else value)
                for key, value in row.items()
            }
        )
    return [ProductRecord(**row) for row in normalized_rows]


def build_alert_record(row: dict, prediction: dict) -> AlertRecord:
    return AlertRecord(
        sku=row["sku"],
        store_id=row["store_id"],
        category=row["category"],
        current_stock=int(row["current_stock"]),
        predicted_demand=prediction["predicted_demand"],
        recommended_stock=prediction["recommended_stock"],
        risk_level=prediction["risk_level"],
        alert=prediction["alert"],
    )
