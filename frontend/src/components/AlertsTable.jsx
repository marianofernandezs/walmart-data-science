export default function AlertsTable({ alerts }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <p className="eyebrow">Monitoreo</p>
        <h2>Alertas de inventario</h2>
      </div>

      <div className="table-shell">
        <table>
          <thead>
            <tr>
              <th>SKU</th>
              <th>Tienda</th>
              <th>Stock</th>
              <th>Demanda</th>
              <th>Riesgo</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map((item) => (
              <tr key={`${item.sku}-${item.store_id}`}>
                <td>{item.sku}</td>
                <td>{item.store_id}</td>
                <td>{item.current_stock}</td>
                <td>{item.predicted_demand}</td>
                <td className={`risk-${item.risk_level.toLowerCase()}`}>{item.risk_level}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
