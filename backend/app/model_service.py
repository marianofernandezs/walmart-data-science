from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from .schemas import PredictionRequest
from .utils import (
    category_baseline,
    clamp_non_negative,
    dept_from_sku_category,
    seasonality_multiplier,
    seeded_noise,
    state_from_store,
)


MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "model.pkl"


@dataclass
class LoadedModel:
    bundle: dict[str, Any]

    @property
    def estimator(self):
        return self.bundle["model"]

    @property
    def metrics(self) -> dict[str, Any]:
        metrics = self.bundle.get("metrics", {})
        return {
            "model": metrics.get("model", self.bundle.get("model_name", "trained_model")),
            "MAE": metrics.get("MAE"),
            "RMSE": metrics.get("RMSE"),
            "RMSSE_global": metrics.get("RMSSE_global"),
            "R2": metrics.get("R2"),
            "data_source_label": metrics.get("data_source_label"),
        }


class ModelService:
    def __init__(self) -> None:
        self.loaded_model: LoadedModel | None = None
        self.model_error: str | None = None
        self.mode = "mock_fallback"
        self.load_model()

    def load_model(self) -> None:
        if not MODEL_PATH.exists():
            self.loaded_model = None
            self.mode = "mock_fallback"
            self.model_error = "model.pkl not found"
            return
        try:
            loaded = joblib.load(MODEL_PATH)
            if not isinstance(loaded, dict) or "model" not in loaded:
                raise ValueError("Unsupported model bundle format")
            self.loaded_model = LoadedModel(bundle=loaded)
            self.mode = "trained_model"
            self.model_error = None
        except Exception as exc:
            self.loaded_model = None
            self.mode = "mock_fallback"
            self.model_error = str(exc)

    def get_status(self) -> dict[str, Any]:
        metrics = self.loaded_model.metrics if self.loaded_model else self.mock_metrics()
        return {
            "mode": self.mode,
            "loaded": self.loaded_model is not None,
            "path": str(MODEL_PATH),
            "error": self.model_error,
            "metrics": metrics,
            "expected_features": self.expected_feature_structure(),
        }

    def expected_feature_structure(self) -> dict[str, Any]:
        if self.loaded_model:
            bundle = self.loaded_model.bundle
            return {
                "feature_cols": bundle.get("feature_cols", []),
                "categorical_cols": bundle.get("categorical_cols", []),
                "boolean_cols": bundle.get("boolean_cols", []),
                "float_cols": bundle.get("float_cols", []),
            }
        return {
            "feature_cols": [
                "sell_price", "snap_active", "has_event", "month", "year", "dayofweek",
                "weekofyear", "is_weekend", "lag_7", "lag_14", "lag_28",
                "rolling_mean_7", "rolling_mean_28", "item_id", "dept_id", "cat_id",
                "store_id", "state_id",
            ],
            "categorical_cols": ["item_id", "dept_id", "cat_id", "store_id", "state_id"],
            "boolean_cols": ["snap_active", "has_event", "is_weekend"],
            "float_cols": ["sell_price", "lag_7", "lag_14", "lag_28", "rolling_mean_7", "rolling_mean_28"],
        }

    def mock_metrics(self) -> dict[str, Any]:
        return {
            "model": "Mock fallback",
            "MAE": 3.42,
            "RMSE": 5.18,
            "RMSSE_global": 0.91,
            "WRMSSE": 0.87,
            "R2": 0.74,
        }

    def predict(self, payload: PredictionRequest) -> dict[str, Any]:
        if self.loaded_model:
            try:
                return self._predict_with_model(payload)
            except Exception as exc:
                self.model_error = str(exc)
                self.mode = "mock_fallback"
        return self._predict_with_mock(payload)

    def _predict_with_model(self, payload: PredictionRequest) -> dict[str, Any]:
        bundle = self.loaded_model.bundle
        feature_rows = self._build_feature_rows(payload, use_model=True)
        frame = pd.DataFrame(feature_rows)
        forecast = bundle["model"].predict(frame[bundle["feature_cols"]])
        return self._format_prediction(payload, forecast, "trained_model", feature_rows[0])

    def _predict_with_mock(self, payload: PredictionRequest) -> dict[str, Any]:
        feature_rows = self._build_feature_rows(payload, use_model=False)
        forecast = [row["rolling_mean_7"] * row["seasonal_factor"] for row in feature_rows]
        return self._format_prediction(payload, forecast, "mock_fallback", feature_rows[0])

    def _format_prediction(
        self,
        payload: PredictionRequest,
        forecast_values: Any,
        mode: str,
        first_row_features: dict[str, Any],
    ) -> dict[str, Any]:
        cleaned = [round(clamp_non_negative(value), 2) for value in forecast_values][: payload.forecast_horizon]
        predicted_demand = round(sum(cleaned), 2)
        recommended_stock = int(round(predicted_demand * 1.15))
        risk_level = self._risk_level(payload.current_stock, predicted_demand)
        alert = self._alert_message(risk_level, payload.current_stock, predicted_demand, recommended_stock)
        return {
            "sku": payload.sku,
            "forecast_horizon": payload.forecast_horizon,
            "predicted_demand": predicted_demand,
            "daily_forecast": [{"day": index + 1, "demand": value} for index, value in enumerate(cleaned)],
            "recommended_stock": recommended_stock,
            "risk_level": risk_level,
            "alert": alert,
            "model_mode": mode,
            "features_used": {
                key: value
                for key, value in first_row_features.items()
                if key in self.expected_feature_structure()["feature_cols"]
            },
        }

    def _build_feature_rows(self, payload: PredictionRequest, use_model: bool) -> list[dict[str, Any]]:
        today = date.today()
        category = payload.category.upper()
        dept_id = dept_from_sku_category(payload.sku, category)
        state_id = state_from_store(payload.store_id)
        base = category_baseline(category)
        lag_values = [base * 0.92, base, base * 1.05, base * 0.97]
        rows: list[dict[str, Any]] = []

        for offset in range(payload.forecast_horizon):
            target_date = today + timedelta(days=offset + 1)
            seasonal_factor = seasonality_multiplier(target_date)
            event_boost = 1.18 if payload.event_day else 1.0
            snap_boost = 1.10 if payload.snap_day else 1.0
            price_penalty = max(0.72, 1.18 - (payload.price / 20.0))
            noise = seeded_noise(payload.sku + payload.store_id, offset)
            recent_mean = sum(lag_values[-3:]) / 3
            rolling_7 = clamp_non_negative(recent_mean * seasonal_factor * event_boost * snap_boost * price_penalty + noise)
            rolling_28 = clamp_non_negative(((sum(lag_values) / len(lag_values)) + recent_mean) / 2)

            row = {
                "sell_price": float(payload.price),
                "snap_active": int(payload.snap_day),
                "has_event": int(payload.event_day),
                "month": target_date.month,
                "year": target_date.year,
                "dayofweek": target_date.weekday(),
                "weekofyear": int(target_date.strftime("%U")),
                "is_weekend": int(target_date.weekday() >= 5),
                "lag_7": float(lag_values[-1]),
                "lag_14": float(lag_values[-2]),
                "lag_28": float(lag_values[-3]),
                "rolling_mean_7": float(rolling_7),
                "rolling_mean_28": float(rolling_28),
                "item_id": payload.sku,
                "dept_id": dept_id,
                "cat_id": category,
                "store_id": payload.store_id,
                "state_id": state_id,
                "seasonal_factor": seasonal_factor,
            }
            if use_model and self.loaded_model:
                row = self._encode_row(row, self.loaded_model.bundle)

            rows.append(row)
            lag_values.append(rolling_7)
            lag_values = lag_values[-4:]
        return rows

    def _encode_row(self, row: dict[str, Any], bundle: dict[str, Any]) -> dict[str, Any]:
        encoded = dict(row)
        mappings = bundle.get("category_mappings", {})
        for col in bundle.get("categorical_cols", []):
            values = mappings.get(col, [])
            try:
                encoded[col] = values.index(str(row[col]))
            except ValueError:
                encoded[col] = 0
        for col in bundle.get("boolean_cols", []):
            encoded[col] = int(bool(row[col]))
        return encoded

    def _risk_level(self, current_stock: int, predicted_demand: float) -> str:
        if current_stock < predicted_demand * 0.8:
            return "HIGH"
        if current_stock <= predicted_demand * 1.1:
            return "MEDIUM"
        return "LOW"

    def _alert_message(
        self,
        risk_level: str,
        current_stock: int,
        predicted_demand: float,
        recommended_stock: int,
    ) -> str:
        if risk_level == "HIGH":
            return (
                f"Riesgo alto de quiebre: stock actual {current_stock} por debajo de la demanda "
                f"esperada {predicted_demand}. Recomendado: {recommended_stock}."
            )
        if risk_level == "MEDIUM":
            return (
                f"Stock ajustado: {current_stock} cercano a la demanda proyectada {predicted_demand}. "
                f"Conviene monitorear reposición."
            )
        return (
            f"Stock holgado: {current_stock} supera la demanda proyectada {predicted_demand}. "
            f"Revisa riesgo de sobrestock si la tendencia baja."
        )


model_service = ModelService()
