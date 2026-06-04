from __future__ import annotations

import pandas as pd

from .schemas import PredictionRequest


def normalize_processed_ingestion(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    normalized["sku"] = normalized["sku"].astype(str).str.strip().str.upper()
    normalized["store_id"] = normalized["store_id"].astype(str).str.strip().str.upper()
    normalized["category"] = normalized["category"].astype(str).str.strip().str.upper()
    normalized["state_id"] = normalized["store_id"].str.split("_").str[0]
    normalized["dept_id"] = normalized.apply(
        lambda row: f"{row['category']}_{str(row['sku']).split('_')[1] if '_' in str(row['sku']) else '1'}",
        axis=1,
    )
    normalized["current_stock"] = normalized["current_stock"].round().astype(int)
    return normalized


def ingestion_row_to_prediction_request(row: dict, forecast_horizon: int = 7) -> PredictionRequest:
    return PredictionRequest(
        sku=str(row["sku"]).upper(),
        store_id=str(row["store_id"]).upper(),
        category=str(row["category"]).upper(),
        current_stock=int(float(row["current_stock"])),
        price=float(row["price"]),
        snap_day=int(row.get("snap_day", 0)),
        event_day=int(row.get("event_day", 0)),
        forecast_horizon=forecast_horizon,
    )
