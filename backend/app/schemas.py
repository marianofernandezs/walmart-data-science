from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class PredictionRequest(BaseModel):
    sku: str = Field(..., min_length=3, examples=["FOODS_1_001"])
    store_id: str = Field(..., min_length=2, examples=["CA_1"])
    category: str = Field(..., min_length=2, examples=["FOODS"])
    current_stock: int = Field(..., ge=0, examples=[120])
    price: float = Field(..., ge=0, examples=[3.99])
    snap_day: int = Field(..., ge=0, le=1, examples=[1])
    event_day: int = Field(..., ge=0, le=1, examples=[0])
    forecast_horizon: int = Field(..., ge=1, le=28, examples=[28])

    @field_validator("sku", "store_id", "category")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return value.strip().upper()


class BatchPredictionRequest(BaseModel):
    items: List[PredictionRequest] = Field(..., min_length=1)


class DailyForecastPoint(BaseModel):
    day: int
    demand: float


class PredictionResponse(BaseModel):
    sku: str
    forecast_horizon: int
    predicted_demand: float
    daily_forecast: List[DailyForecastPoint]
    recommended_stock: int
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    alert: str
    model_mode: Literal["trained_model", "mock_fallback"]
    features_used: Optional[dict[str, Any]] = None


class ProductRecord(BaseModel):
    sku: str
    store_id: str
    category: str
    dept_id: str
    state_id: str
    current_stock: int
    price: float


class AlertRecord(BaseModel):
    sku: str
    store_id: str
    category: str
    current_stock: int
    predicted_demand: float
    recommended_stock: int
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    alert: str


class MetricsResponse(BaseModel):
    average_response_time_ms: float
    total_predictions: int
    api_status: str
    model_status: str
    example_model_metrics: dict[str, Any]


class ArchitectureResponse(BaseModel):
    frontend: str
    backend: str
    model: str
    storage: str
    flow: List[str]
