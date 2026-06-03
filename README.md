# Optimización de Inventario mediante Pronóstico de Demanda Jerárquico

Aplicación full-stack local para la fase de deployment de CRISP-DM. El sistema combina un dashboard React con una API FastAPI para consultar predicciones de demanda, alertas de stock y métricas técnicas.

## Qué encontré en el repositorio

- Notebooks previos: `notebooks/01-eda_and_cleaning.ipynb` y `notebooks/02-modeling_and_evaluation_final_rubrica.ipynb`
- Modelos serializados detectados en `models/`
- Modelo exportable integrado: se toma como base `models/best_forecasting_model_part_2_histgradientboosting.pkl`

## Dónde debe ir el modelo real

- Ruta obligatoria del backend: `backend/models/model.pkl`
- Formato esperado: bundle `joblib` con estas claves:
  - `model`
  - `feature_cols`
  - `categorical_cols`
  - `boolean_cols`
  - `float_cols`
  - `category_mappings`
  - `metrics` (opcional, pero recomendado)

Si `backend/models/model.pkl` no existe o falla al cargar, el backend activa automáticamente `mock_fallback`.

## Estructura de features esperada por `model_service.py`

`backend/app/model_service.py` construye una fila de inferencia con esta estructura:

- `sell_price`
- `snap_active`
- `has_event`
- `month`
- `year`
- `dayofweek`
- `weekofyear`
- `is_weekend`
- `lag_7`
- `lag_14`
- `lag_28`
- `rolling_mean_7`
- `rolling_mean_28`
- `item_id`
- `dept_id`
- `cat_id`
- `store_id`
- `state_id`

Las categóricas se codifican con `category_mappings` cuando se usa el modelo real. Si llega un valor desconocido, se usa un índice seguro por defecto.

## Arquitectura

- Frontend: React + Vite en `http://localhost:5173`
- Backend: FastAPI + Uvicorn en `http://localhost:8000`
- Modelo: `joblib` si existe `backend/models/model.pkl`; si no, fallback mock con reglas de negocio realistas
- Datos demo: `backend/data/sample_products.csv`

## Instalación backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Swagger:

- [http://localhost:8000/docs](http://localhost:8000/docs)

## Instalación frontend

```bash
cd frontend
npm install
npm run dev
```

## Endpoints principales

- `GET /`
- `GET /health`
- `GET /products`
- `POST /predict`
- `POST /batch-predict`
- `GET /alerts`
- `GET /metrics`
- `GET /architecture`

## Documentación adicional

- `docs/architecture.md`
- `docs/api_tests.md`
- `docs/deployment_evidence.md`
- `docs/technical_evaluation.md`
