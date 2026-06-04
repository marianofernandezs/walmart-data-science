import { useState } from 'react'

const SAMPLE_JSON = `[
  {
    "sku": "FOODS_9_001",
    "store_id": "CA_1",
    "category": "FOODS",
    "date": "2026-06-03",
    "current_stock": 20,
    "price": 3.5,
    "snap_day": 1,
    "event_day": 0,
    "sales": 14
  }
]`

export default function DataUpload({ onUploadCSV, onUploadJSON, loading, lastUploadName }) {
  const [jsonText, setJsonText] = useState(SAMPLE_JSON)

  const handleJSONSubmit = () => {
    onUploadJSON(jsonText)
  }

  return (
    <section className="panel">
      <div className="panel-heading">
        <p className="eyebrow">Ingesta de datos</p>
        <h2>Subir nuevos registros</h2>
        <p className="section-copy">
          Sube un CSV o pega JSON para alimentar productos, alertas y predicciones sin interrumpir la demo.
        </p>
      </div>

      <div className="upload-grid">
        <label className="upload-card">
          <span className="upload-title">CSV desde archivo</span>
          <small>Arrastra o selecciona un archivo con el esquema esperado.</small>
          <input
            className="file-input"
            type="file"
            accept=".csv"
            onChange={(event) => {
              const file = event.target.files?.[0]
              if (file) onUploadCSV(file)
            }}
            disabled={loading}
          />
        </label>

        <label>
          JSON de ejemplo
          <textarea
            rows="10"
            value={jsonText}
            onChange={(event) => setJsonText(event.target.value)}
          />
        </label>
      </div>

      <div className="ingestion-toolbar">
        <div className="upload-meta">
          <span className="meta-label">Última subida</span>
          <strong>{lastUploadName || 'Sin archivos nuevos aún'}</strong>
        </div>
      </div>

      <button className="primary-button" onClick={handleJSONSubmit} disabled={loading}>
        {loading ? 'Procesando ingesta...' : 'Enviar JSON'}
      </button>
    </section>
  )
}
