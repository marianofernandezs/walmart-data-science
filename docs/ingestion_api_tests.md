# Pruebas de API de ingesta

## Esquema

```bash
curl http://localhost:8000/ingestion/schema
```

## CSV

```bash
curl -X POST http://localhost:8000/ingestion/upload-csv \
  -F "file=@sample_ingestion.csv"
```

## JSON

```bash
curl -X POST http://localhost:8000/ingestion/json \
  -H "Content-Type: application/json" \
  -d '{"items":[{"sku":"FOODS_9_001","store_id":"CA_1","category":"FOODS","date":"2026-06-03","current_stock":20,"price":3.5,"snap_day":1,"event_day":0,"sales":14}]}'
```

## Listado y preview

```bash
curl http://localhost:8000/ingestion/files
curl http://localhost:8000/ingestion/preview
```

## Borrado

```bash
curl -X DELETE http://localhost:8000/ingestion/files/<filename>
```
