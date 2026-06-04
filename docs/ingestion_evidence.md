# Evidencia de ingesta

## Qué verificar

- Swagger muestra los endpoints `ingestion/*`
- La subida de CSV retorna resumen con válidas y rechazadas
- El preview devuelve filas del último processed
- `products` incorpora SKUs nuevos sin duplicar `sku + store_id`
- `alerts` muestra también productos ingeridos

## Evidencias sugeridas

- Captura de `/ingestion/schema`
- Captura de respuesta de `/ingestion/upload-csv`
- Captura del dashboard con preview de datos nuevos
