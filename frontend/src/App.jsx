import { useEffect, useMemo, useState } from 'react'
import { api } from './api'
import PredictionForm from './components/PredictionForm'
import PredictionResult from './components/PredictionResult'
import AlertsTable from './components/AlertsTable'
import MetricsPanel from './components/MetricsPanel'
import ArchitecturePanel from './components/ArchitecturePanel'
import DataUpload from './components/DataUpload'
import IngestionSummary from './components/IngestionSummary'
import DataPreview from './components/DataPreview'

const INITIAL_FORM = {
  sku: 'FOODS_1_001',
  store_id: 'CA_1',
  category: 'FOODS',
  current_stock: 120,
  price: 3.99,
  snap_day: 1,
  event_day: 0,
  forecast_horizon: 28,
}

export default function App() {
  const [form, setForm] = useState(INITIAL_FORM)
  const [health, setHealth] = useState(null)
  const [products, setProducts] = useState([])
  const [alerts, setAlerts] = useState([])
  const [metrics, setMetrics] = useState(null)
  const [architecture, setArchitecture] = useState(null)
  const [prediction, setPrediction] = useState(null)
  const [loadingPrediction, setLoadingPrediction] = useState(false)
  const [loadingIngestion, setLoadingIngestion] = useState(false)
  const [ingestionSummary, setIngestionSummary] = useState(null)
  const [ingestionFiles, setIngestionFiles] = useState([])
  const [preview, setPreview] = useState(null)
  const [successMessage, setSuccessMessage] = useState('')
  const [error, setError] = useState('')

  const connectionLabel = useMemo(() => {
    if (!health) return 'Conectando...'
    return health.status === 'ok' ? `API activa · ${health.model_mode}` : 'Sin conexión'
  }, [health])

  const loadDashboard = async () => {
    try {
      const [healthData, productsData, alertsData, metricsData, architectureData, filesData, previewData] = await Promise.all([
        api.getHealth(),
        api.getProducts(),
        api.getAlerts(),
        api.getMetrics(),
        api.getArchitecture(),
        api.getIngestionFiles(),
        api.getIngestionPreview(),
      ])

      setHealth(healthData)
      setProducts(productsData.items || [])
      setAlerts(alertsData.items || [])
      setMetrics(metricsData)
      setArchitecture(architectureData)
      setIngestionFiles(filesData.items || [])
      setPreview(previewData)
    } catch (requestError) {
      setError(requestError.message)
    }
  }

  useEffect(() => {
    loadDashboard()
  }, [])

  const handlePredict = async () => {
    setLoadingPrediction(true)
    setError('')
    try {
      const result = await api.predict(form)
      setPrediction(result)
      setSuccessMessage('Predicción generada correctamente.')
      const [alertsData, metricsData, healthData] = await Promise.all([
        api.getAlerts(),
        api.getMetrics(),
        api.getHealth(),
      ])
      setAlerts(alertsData.items || [])
      setMetrics(metricsData)
      setHealth(healthData)
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoadingPrediction(false)
    }
  }

  const refreshIngestionViews = async () => {
    const [filesData, previewData, productsData, alertsData] = await Promise.all([
      api.getIngestionFiles(),
      api.getIngestionPreview(),
      api.getProducts(),
      api.getAlerts(),
    ])
    setIngestionFiles(filesData.items || [])
    setPreview(previewData)
    setProducts(productsData.items || [])
    setAlerts(alertsData.items || [])
  }

  const handleUploadCSV = async (file) => {
    setLoadingIngestion(true)
    setError('')
    setSuccessMessage('')
    try {
      const summary = await api.uploadCSV(file)
      setIngestionSummary(summary)
      setSuccessMessage(`Archivo procesado: ${summary.filename}`)
      await refreshIngestionViews()
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoadingIngestion(false)
    }
  }

  const handleUploadJSON = async (jsonText) => {
    setLoadingIngestion(true)
    setError('')
    setSuccessMessage('')
    try {
      const parsed = JSON.parse(jsonText)
      const summary = await api.ingestJSON({ items: parsed })
      setIngestionSummary(summary)
      setSuccessMessage('JSON ingerido correctamente.')
      await refreshIngestionViews()
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoadingIngestion(false)
    }
  }

  const handleDeleteFile = async (filename) => {
    setLoadingIngestion(true)
    setError('')
    setSuccessMessage('')
    try {
      await api.deleteIngestionFile(filename)
      setSuccessMessage(`Archivo eliminado: ${filename}`)
      await refreshIngestionViews()
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoadingIngestion(false)
    }
  }

  const handleClearAll = async () => {
    setLoadingIngestion(true)
    setError('')
    setSuccessMessage('')
    try {
      const result = await api.clearIngestionFiles()
      setIngestionSummary(null)
      setSuccessMessage(
        `Ingesta limpiada. Raw: ${result.deleted.raw}, processed: ${result.deleted.processed}, rejected: ${result.deleted.rejected}.`
      )
      await refreshIngestionViews()
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoadingIngestion(false)
    }
  }

  return (
    <main className="app-shell">
      <header className="hero">
        <p className="eyebrow">Proyecto de Ciencia de Datos</p>
        <h1>Optimización de Inventario mediante Pronóstico de Demanda Jerárquico</h1>
        <p className="hero-copy">
          Dashboard local para validar predicciones, riesgos de quiebre y métricas técnicas de deployment.
        </p>
        <div className="hero-meta">
          <div className="status-pill">{connectionLabel}</div>
          <div className="hero-kpis">
            <div className="hero-kpi">
              <span>Productos</span>
              <strong>{products.length}</strong>
            </div>
            <div className="hero-kpi">
              <span>Archivos ingesta</span>
              <strong>{ingestionFiles.length}</strong>
            </div>
          </div>
        </div>
        {successMessage && <div className="success-banner">{successMessage}</div>}
        {error && <div className="error-banner">{error}</div>}
      </header>

      <section className="top-grid">
        <PredictionForm
          products={products}
          value={form}
          onChange={setForm}
          onSubmit={handlePredict}
          loading={loadingPrediction}
        />
        <PredictionResult prediction={prediction} />
      </section>

      <section className="bottom-grid">
        <AlertsTable alerts={alerts} />
        <MetricsPanel metrics={metrics} health={health} />
      </section>

      <section className="bottom-grid">
        <DataUpload
          onUploadCSV={handleUploadCSV}
          onUploadJSON={handleUploadJSON}
          loading={loadingIngestion}
          lastUploadName={ingestionSummary?.processed_file || ingestionSummary?.filename}
        />
        <IngestionSummary
          summary={ingestionSummary}
          files={ingestionFiles}
          onDeleteFile={handleDeleteFile}
          onClearAll={handleClearAll}
          loading={loadingIngestion}
        />
      </section>

      <DataPreview preview={preview} />

      <ArchitecturePanel architecture={architecture} />
    </main>
  )
}
