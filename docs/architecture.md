# Arquitectura localhost

La solución se despliega localmente con un frontend React que consume una API FastAPI. El backend valida entradas, consulta el servicio de predicción, procesa ingestas CSV/JSON, calcula reglas de inventario y devuelve respuestas JSON al dashboard.

```mermaid
graph TD
  A[Usuario] --> B[Frontend React]
  B --> C[API FastAPI localhost:8000]
  B --> H[Subida CSV o JSON]
  C --> D[Servicio de Predicción]
  D --> E[Modelo HistGradientBoosting o Mock Fallback]
  C --> I[Servicio de Ingesta]
  I --> J[Validación y Transformación]
  J --> K[raw / processed / rejected]
  C --> F[Datos CSV]
  C --> G[Respuesta JSON]
  G --> B
```

## Componentes

- Frontend: formulario, panel de resultados, alertas, métricas y arquitectura.
- Backend: endpoints REST, validación Pydantic, CORS, métricas en memoria e ingesta local.
- Modelo: carga `backend/models/model.pkl` si existe; en caso contrario, usa fallback.
- Datos: `backend/data/sample_products.csv` como fuente local de SKUs demo y `backend/data/ingested/` para nuevos datos.
