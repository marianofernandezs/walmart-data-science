from __future__ import annotations

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .inventory_service import build_alert_record, list_products
from .metrics_service import metrics_service
from .model_service import model_service
from .schemas import (
    ArchitectureResponse,
    BatchPredictionRequest,
    MetricsResponse,
    PredictionRequest,
    PredictionResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_service.load_model()
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
        predictions = [model_service.predict(item) for item in payload.items]
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
            snap_day=1 if product.state_id in {"CA", "TX"} else 0,
            event_day=1 if product.category == "FOODS" else 0,
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
        "backend": "FastAPI + Uvicorn on localhost:8000 with Swagger and CORS",
        "model": "Joblib-loaded HistGradientBoosting bundle or mock fallback",
        "storage": "CSV sample products + local model artifact under backend/models",
        "flow": [
            "Frontend captura parámetros de inventario",
            "API valida entrada con Pydantic",
            "Model service carga modelo real o usa fallback",
            "Inventory logic calcula stock recomendado y riesgo",
            "Dashboard renderiza predicción, alertas y métricas",
        ],
    }
