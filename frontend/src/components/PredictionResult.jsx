export default function PredictionResult({ prediction }) {
  if (!prediction) {
    return (
      <section className="panel">
        <div className="panel-heading">
          <p className="eyebrow">Resultado</p>
          <h2>Esperando simulación</h2>
        </div>
        <p className="muted">Completa el formulario para ver demanda, stock recomendado y forecast diario.</p>
      </section>
    )
  }

  return (
    <section className="panel">
      <div className="panel-heading">
        <p className="eyebrow">Respuesta del modelo</p>
        <h2>{prediction.sku}</h2>
      </div>

      <div className="stats-grid">
        <article>
          <span>Demanda pronosticada</span>
          <strong>{prediction.predicted_demand}</strong>
        </article>
        <article>
          <span>Stock recomendado</span>
          <strong>{prediction.recommended_stock}</strong>
        </article>
        <article>
          <span>Riesgo</span>
          <strong className={`risk-${prediction.risk_level.toLowerCase()}`}>{prediction.risk_level}</strong>
        </article>
        <article>
          <span>Modo</span>
          <strong>{prediction.model_mode}</strong>
        </article>
      </div>

      <p className="alert-copy">{prediction.alert}</p>

      <div className="table-shell">
        <table>
          <thead>
            <tr>
              <th>Día</th>
              <th>Demanda</th>
            </tr>
          </thead>
          <tbody>
            {prediction.daily_forecast.map((point) => (
              <tr key={point.day}>
                <td>{point.day}</td>
                <td>{point.demand}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
