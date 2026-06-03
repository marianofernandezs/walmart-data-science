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

## Validaciones

- `current_stock` no acepta valores negativos
- `price` no acepta valores negativos
- `forecast_horizon` solo acepta valores entre 1 y 28
- FastAPI/Pydantic devuelve errores claros cuando faltan campos o tipos correctos

## Tiempos de respuesta esperados

- `/health` y `/products`: ~10-50 ms en local
- `/predict`: ~20-120 ms con el modelo local
- `/alerts`: depende del número de SKUs de ejemplo

## Estabilidad local

- El backend mantiene operatividad aunque falle la carga del modelo real
- Las métricas se almacenan en memoria para la sesión activa

## Limitaciones

- El predictor real usa features sintéticas derivadas para servir inferencia local
- No existe persistencia de métricas ni autenticación
- El frontend requiere instalar dependencias antes de ejecutar Vite

## Mejoras futuras

- Persistir métricas en base de datos
- Incorporar forecast jerárquico por tienda/departamento
- Versionar modelos y metadata de features
- Agregar pruebas automatizadas de API y frontend
