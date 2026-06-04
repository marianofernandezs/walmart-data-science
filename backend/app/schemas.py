from typing import Any, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AppBaseModel(BaseModel):
    model_config = ConfigDict(protected_namespaces=())


class PredictionRequest(AppBaseModel):
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


class BatchPredictionRequest(AppBaseModel):
    items: Optional[List[PredictionRequest]] = Field(default=None)
    source_file: Optional[str] = None


class DailyForecastPoint(AppBaseModel):
    day: int
    demand: float


class PredictionResponse(AppBaseModel):
    sku: str
    forecast_horizon: int
    predicted_demand: float
    daily_forecast: List[DailyForecastPoint]
    recommended_stock: int
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    alert: str
    model_mode: Literal["trained_model", "mock_fallback", "mock_fallback_due_to_feature_mismatch"]
    features_used: Optional[dict[str, Any]] = None


class ProductRecord(AppBaseModel):
    sku: str
    store_id: str
    category: str
    dept_id: str
    state_id: str
    current_stock: int
    price: float
    date: Optional[str] = None
    snap_day: Optional[int] = None
    event_day: Optional[int] = None
    sales: Optional[float] = None


class IngestionRecord(AppBaseModel):
    sku: str = Field(..., min_length=1, examples=["FOODS_001"])
    store_id: str = Field(..., min_length=2, examples=["CA_1"])
    category: Literal["FOODS", "HOBBIES", "HOUSEHOLD"]
    date: str = Field(..., examples=["2026-06-03"])
    current_stock: float = Field(..., ge=0)
    price: float = Field(..., gt=0)
    snap_day: int = Field(..., ge=0, le=1)
    event_day: int = Field(..., ge=0, le=1)
    sales: float = Field(..., ge=0)
    extra_fields: Optional[dict[str, Any]] = None

    @field_validator("sku", "store_id", "category")
    @classmethod
    def normalize_ingestion_text(cls, value: str) -> str:
        return value.strip().upper()


class IngestionJSONRequest(AppBaseModel):
    items: List[IngestionRecord] = Field(..., min_length=1)


class IngestionSummaryResponse(AppBaseModel):
    filename: str
    status: Literal["success", "partial_success", "error"]
    rows_received: int
    rows_valid: int
    rows_rejected: int
    processed_file: Optional[str] = None
    rejected_file: Optional[str] = None
    validation_errors: List[str] = Field(default_factory=list)


class IngestionFileEntry(AppBaseModel):
    filename: str
    category: Literal["raw", "processed", "rejected"]
    created_at: str
    rows: Optional[int] = None


class IngestionPreviewResponse(AppBaseModel):
    filename: str
    rows: List[dict[str, Any]]


class IngestionSchemaResponse(AppBaseModel):
    required_columns: List[str]
    allowed_categories: List[str]
    validations: dict[str, Any]


class AlertRecord(AppBaseModel):
    sku: str
    store_id: str
    category: str
    current_stock: int
    predicted_demand: float
    recommended_stock: int
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    alert: str


class MetricsResponse(AppBaseModel):
    average_response_time_ms: float
    total_predictions: int
    api_status: str
    model_status: str
    example_model_metrics: dict[str, Any]


class ArchitectureResponse(AppBaseModel):
    frontend: str
    backend: str
    model: str
    storage: str
    flow: List[str]
