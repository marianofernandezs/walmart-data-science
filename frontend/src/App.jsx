import { useEffect, useMemo, useState } from 'react'
import { api } from './api'
import PredictionForm from './components/PredictionForm'
import PredictionResult from './components/PredictionResult'
import AlertsTable from './components/AlertsTable'
import MetricsPanel from './components/MetricsPanel'
import ArchitecturePanel from './components/ArchitecturePanel'

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
  const [error, setError] = useState('')

  const connectionLabel = useMemo(() => {
    if (!health) return 'Conectando...'
    return health.status === 'ok' ? `API activa · ${health.model_mode}` : 'Sin conexión'
  }, [health])

  const loadDashboard = async () => {
    try {
      const [healthData, productsData, alertsData, metricsData, architectureData] = await Promise.all([
        api.getHealth(),
        api.getProducts(),
        api.getAlerts(),
        api.getMetrics(),
        api.getArchitecture(),
      ])

      setHealth(healthData)
      setProducts(productsData.items || [])
      setAlerts(alertsData.items || [])
      setMetrics(metricsData)
      setArchitecture(architectureData)
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

  return (
    <main className="app-shell">
      <header className="hero">
        <p className="eyebrow">Proyecto de Ciencia de Datos</p>
        <h1>Optimización de Inventario mediante Pronóstico de Demanda Jerárquico</h1>
        <p className="hero-copy">
          Dashboard local para validar predicciones, riesgos de quiebre y métricas técnicas de deployment.
        </p>
        <div className="status-pill">{connectionLabel}</div>
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

      <ArchitecturePanel architecture={architecture} />
    </main>
  )
}
