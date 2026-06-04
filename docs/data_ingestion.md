# Ingesta de datos

El sistema ahora permite incorporar nuevos registros mediante CSV o JSON sin reemplazar la arquitectura actual.

## Flujo

1. El usuario sube un CSV o envía JSON.
2. FastAPI valida columnas, tipos, fechas y rangos.
3. El archivo original queda en `backend/data/ingested/raw/` cuando aplica.
4. Las filas válidas se guardan en `backend/data/ingested/processed/`.
5. Las filas rechazadas se guardan en `backend/data/ingested/rejected/`.
6. Los registros válidos pasan a alimentar `products`, `alerts` y el dashboard.

## Esquema mínimo

- `sku`
- `store_id`
- `category`
- `date`
- `current_stock`
- `price`
- `snap_day`
- `event_day`
- `sales`
