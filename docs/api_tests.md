# Pruebas de API

## Health

```bash
curl http://localhost:8000/health
```

Respuesta esperada:

```json
{
  "status": "ok",
  "api": "online",
  "model_loaded": true,
  "model_mode": "trained_model",
  "model_path": ".../backend/models/model.pkl",
  "model_error": null
}
```

## Products

```bash
curl http://localhost:8000/products
```

## Predict

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "FOODS_1_001",
    "store_id": "CA_1",
    "category": "FOODS",
    "current_stock": 120,
    "price": 3.99,
    "snap_day": 1,
    "event_day": 0,
    "forecast_horizon": 28
  }'
```

Respuesta esperada:

```json
{
  "sku": "FOODS_1_001",
  "forecast_horizon": 28,
  "predicted_demand": 0,
  "daily_forecast": [{"day": 1, "demand": 0}],
  "recommended_stock": 0,
  "risk_level": "LOW",
  "alert": "mensaje",
  "model_mode": "trained_model",
  "features_used": {}
}
```

## Batch predict

```bash
curl -X POST http://localhost:8000/batch-predict \
  -H "Content-Type: application/json" \
  -d '{"items":[{"sku":"FOODS_1_001","store_id":"CA_1","category":"FOODS","current_stock":120,"price":3.99,"snap_day":1,"event_day":0,"forecast_horizon":7}]}'
```

## Alerts

```bash
curl http://localhost:8000/alerts
```

## Metrics

```bash
curl http://localhost:8000/metrics
```

## Architecture

```bash
curl http://localhost:8000/architecture
```
