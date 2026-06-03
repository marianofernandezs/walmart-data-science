export default function ArchitecturePanel({ architecture }) {
  return (
    <section className="panel architecture-panel">
      <div className="panel-heading">
        <p className="eyebrow">Despliegue local</p>
        <h2>Arquitectura</h2>
      </div>

      <div className="architecture-flow">
        {(architecture?.flow || []).map((step, index) => (
          <div key={step} className="flow-step">
            <span>{index + 1}</span>
            <p>{step}</p>
          </div>
        ))}
      </div>

      <div className="architecture-summary">
        <p><strong>Frontend:</strong> {architecture?.frontend}</p>
        <p><strong>Backend:</strong> {architecture?.backend}</p>
        <p><strong>Modelo:</strong> {architecture?.model}</p>
        <p><strong>Storage:</strong> {architecture?.storage}</p>
      </div>
    </section>
  )
}
