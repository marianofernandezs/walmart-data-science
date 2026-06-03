# Backend

API local en FastAPI para consultar pronósticos, alertas y métricas del sistema.

## Ejecutar

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Modelo

- Ruta esperada: `backend/models/model.pkl`
- Formato soportado: bundle serializado con `joblib` que incluya `model`, `feature_cols`, `categorical_cols`, `boolean_cols`, `float_cols` y `category_mappings`
- Fallback: si el archivo no existe o falla la carga, la API sigue operativa con un predictor mock realista

## Endpoints

- `GET /`
- `GET /health`
- `GET /products`
- `POST /predict`
- `POST /batch-predict`
- `GET /alerts`
- `GET /metrics`
- `GET /architecture`
