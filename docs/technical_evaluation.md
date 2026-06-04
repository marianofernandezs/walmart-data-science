# Evaluación técnica

## Endpoints probados

- `GET /`
- `GET /health`
- `GET /products`
- `POST /predict`
- `POST /batch-predict`
- `GET /alerts`
- `GET /metrics`
- `GET /architecture`
- `GET /ingestion/schema`
- `POST /ingestion/upload-csv`
- `POST /ingestion/json`
- `GET /ingestion/files`
- `GET /ingestion/preview`
- `DELETE /ingestion/files/{filename}`

## Validaciones

- `current_stock` no acepta valores negativos
- `price` no acepta valores negativos
- `forecast_horizon` solo acepta valores entre 1 y 28
- FastAPI/Pydantic devuelve errores claros cuando faltan campos o tipos correctos
- La ingesta separa filas válidas y rechazadas sin detener la demo completa

## Tiempos de respuesta esperados

- `/health` y `/products`: ~10-50 ms en local
- `/predict`: ~20-120 ms con el modelo local
- `/alerts`: depende del número de SKUs de ejemplo

## Estabilidad local

- El backend mantiene operatividad aunque falle la carga del modelo real
- Las métricas se almacenan en memoria para la sesión activa
- La ingesta conserva raw, genera processed y opcionalmente rejected para auditoría local

## Limitaciones

- El predictor real usa features sintéticas derivadas para servir inferencia local
- No existe persistencia de métricas ni autenticación
- El frontend requiere instalar dependencias antes de ejecutar Vite
- La validación de ingesta es local y no reemplaza un pipeline productivo con base de datos

## Mejoras futuras

- Persistir métricas en base de datos
- Incorporar forecast jerárquico por tienda/departamento
- Versionar modelos y metadata de features
- Agregar pruebas automatizadas de API y frontend
- Enlazar la ingesta con un feature store o pipeline batch incremental
