# Evidencias de funcionamiento

## Backend

- Ejecutar `uvicorn app.main:app --reload --port 8000` dentro de `backend/`
- Verificar `http://localhost:8000/health`
- Verificar Swagger en `http://localhost:8000/docs`

## Frontend

- Ejecutar `npm install && npm run dev` dentro de `frontend/`
- Abrir `http://localhost:5173`

## Flujo funcional

- Completar el formulario y generar predicción
- Confirmar que se muestra demanda, stock recomendado y nivel de riesgo
- Confirmar que el panel de alertas carga productos simulados
- Confirmar que el panel de métricas refleja estado API y modo de modelo
- Confirmar que la ingesta CSV/JSON genera resumen y preview de datos procesados

## Evidencias sugeridas

- Captura de Swagger operativo
- Captura del dashboard con predicción generada
- Captura de respuesta `curl` a `/predict`
- Captura de respuesta de `/ingestion/upload-csv` o `/ingestion/json`
