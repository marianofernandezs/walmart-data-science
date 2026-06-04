export default function MetricsPanel({ metrics, health }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <p className="eyebrow">Observabilidad</p>
        <h2>Métricas técnicas</h2>
      </div>

      <div className="metrics-list">
        <div>
          <span>Estado API</span>
          <strong>{metrics?.api_status || 'loading'}</strong>
        </div>
        <div>
          <span>Estado modelo</span>
          <strong>{health?.model_mode || metrics?.model_status || 'loading'}</strong>
        </div>
        <div>
          <span>Tiempo promedio</span>
          <strong>{metrics?.average_response_time_ms ?? 0} ms</strong>
        </div>
        <div>
          <span>Total predicciones</span>
          <strong>{metrics?.total_predictions ?? 0}</strong>
        </div>
      </div>

      <pre className="json-card">{JSON.stringify(metrics?.example_model_metrics || {}, null, 2)}</pre>
    </section>
  )
}
