from __future__ import annotations

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .feature_service import ingestion_row_to_prediction_request
from .ingestion_service import ingestion_service
from .inventory_service import build_alert_record, list_products
from .metrics_service import metrics_service
from .model_service import model_service
from .schemas import (
    ArchitectureResponse,
    BatchPredictionRequest,
    IngestionJSONRequest,
    IngestionPreviewResponse,
    IngestionSchemaResponse,
    IngestionSummaryResponse,
    MetricsResponse,
    PredictionRequest,
    PredictionResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_service.load_model()
    ingestion_service.get_schema()
    yield


app = FastAPI(
    title="Optimización de Inventario API",
    description="API local para pronóstico de demanda y alertas de inventario.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def track_metrics(request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    metrics_service.record_response_time((time.perf_counter() - started) * 1000)
    return response


@app.get("/")
def root():
    return {
        "message": "API de pronóstico de demanda operativa",
        "docs": "/docs",
        "model_mode": model_service.mode,
    }


@app.get("/health")
def health():
    status = model_service.get_status()
    return {
        "status": "ok",
        "api": "online",
        "model_loaded": status["loaded"],
        "model_mode": status["mode"],
        "model_path": status["path"],
        "model_error": status["error"],
    }


@app.get("/products")
def products():
    return {"items": [product.model_dump() for product in list_products()]}


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest):
    try:
        prediction = model_service.predict(payload)
        metrics_service.record_prediction()
        return prediction
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc


@app.post("/batch-predict")
def batch_predict(payload: BatchPredictionRequest):
    try:
        items = payload.items or []
        if payload.source_file:
            source_rows = ingestion_service.get_processed_rows(payload.source_file)
            items.extend(
                ingestion_row_to_prediction_request(row, forecast_horizon=7)
                for row in source_rows
            )
        if not items:
            raise HTTPException(status_code=400, detail="Provide items or source_file")
        predictions = [model_service.predict(item) for item in items]
        metrics_service.record_prediction(len(predictions))
        return {"items": predictions, "count": len(predictions)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {exc}") from exc


@app.get("/alerts")
def alerts():
    alert_rows = []
    for product in list_products():
        request = PredictionRequest(
            sku=product.sku,
            store_id=product.store_id,
            category=product.category,
            current_stock=product.current_stock,
            price=product.price,
            snap_day=product.snap_day if product.snap_day is not None else (1 if product.state_id in {"CA", "TX"} else 0),
            event_day=product.event_day if product.event_day is not None else (1 if product.category == "FOODS" else 0),
            forecast_horizon=7,
        )
        prediction = model_service.predict(request)
        alert_rows.append(build_alert_record(product.model_dump(), prediction).model_dump())
    return {"items": alert_rows}


@app.get("/metrics", response_model=MetricsResponse)
def metrics():
    status = model_service.get_status()
    return metrics_service.snapshot(
        model_status=status["mode"],
        model_metrics=status["metrics"],
    )


@app.get("/architecture", response_model=ArchitectureResponse)
def architecture():
    return {
        "frontend": "React + Vite dashboard on localhost:5173",
        "backend": "FastAPI + Uvicorn on localhost:8000 with Swagger, CORS and ingestion endpoints",
        "model": "Joblib-loaded HistGradientBoosting bundle or mock fallback",
        "storage": "CSV sample products + local model artifact + ingested/raw/processed/rejected files",
        "flow": [
            "Frontend captura parámetros de inventario",
            "Frontend puede subir CSV o JSON para ingesta",
            "Ingestion service valida, transforma y guarda archivos locales",
            "API valida entrada con Pydantic",
            "Model service carga modelo real o usa fallback",
            "Inventory logic calcula stock recomendado y riesgo",
            "Dashboard renderiza predicción, alertas y métricas",
        ],
    }


@app.get("/ingestion/schema", response_model=IngestionSchemaResponse)
def ingestion_schema():
    return ingestion_service.get_schema()


@app.post("/ingestion/upload-csv", response_model=IngestionSummaryResponse)
async def ingestion_upload_csv(file: UploadFile = File(...)):
    content = await file.read()
    return ingestion_service.process_csv_upload(file.filename or "upload.csv", content)


@app.post("/ingestion/json", response_model=IngestionSummaryResponse)
def ingestion_json(payload: IngestionJSONRequest):
    return ingestion_service.process_json_records(payload.items)


@app.get("/ingestion/files")
def ingestion_files():
    return {"items": ingestion_service.list_files()}


@app.get("/ingestion/preview", response_model=IngestionPreviewResponse)
def ingestion_preview(filename: str | None = None):
    return ingestion_service.preview(filename)


@app.delete("/ingestion/files/{filename}")
def ingestion_delete_file(filename: str):
    deleted = ingestion_service.delete_file(filename)
    if not deleted:
        raise HTTPException(status_code=404, detail="File not found")
    return {"status": "deleted", "filename": filename}


@app.delete("/ingestion/clear")
def ingestion_clear():
    return ingestion_service.clear_all()
