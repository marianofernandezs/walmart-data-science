const DEFAULT_FORM = {
  sku: 'FOODS_1_001',
  store_id: 'CA_1',
  category: 'FOODS',
  current_stock: 120,
  price: 3.99,
  snap_day: 1,
  event_day: 0,
  forecast_horizon: 28,
}

export default function PredictionForm({ products, value, onChange, onSubmit, loading }) {
  const handleChange = (event) => {
    const { name, value: fieldValue, type } = event.target
    onChange({
      ...value,
      [name]: type === 'number' ? Number(fieldValue) : fieldValue,
    })
  }

  const applyProduct = (sku) => {
    const selected = products.find((item) => item.sku === sku)
    if (!selected) return
    onChange({
      ...value,
      sku: selected.sku,
      store_id: selected.store_id,
      category: selected.category,
      current_stock: selected.current_stock,
      price: selected.price,
      snap_day: selected.snap_day ?? value.snap_day,
      event_day: selected.event_day ?? value.event_day,
    })
  }

  return (
    <section className="panel panel-form">
      <div className="panel-heading">
        <p className="eyebrow">Simulación local</p>
        <h2>Generar predicción</h2>
      </div>

      <div className="form-grid">
        <label>
          SKU
          <select
            name="sku"
            value={value.sku}
            onChange={(event) => {
              handleChange(event)
              applyProduct(event.target.value)
            }}
          >
            {(products.length ? products : [DEFAULT_FORM]).map((item) => (
              <option key={`${item.sku}-${item.store_id}`} value={item.sku}>
                {item.sku}
              </option>
            ))}
          </select>
        </label>

        <label>
          Tienda
          <input name="store_id" value={value.store_id} onChange={handleChange} />
        </label>

        <label>
          Categoría
          <input name="category" value={value.category} onChange={handleChange} />
        </label>

        <label>
          Stock actual
          <input name="current_stock" type="number" min="0" value={value.current_stock} onChange={handleChange} />
        </label>

        <label>
          Precio
          <input name="price" type="number" step="0.01" min="0" value={value.price} onChange={handleChange} />
        </label>

        <label>
          Horizonte
          <input name="forecast_horizon" type="number" min="1" max="28" value={value.forecast_horizon} onChange={handleChange} />
        </label>

        <label>
          SNAP activo
          <select name="snap_day" value={value.snap_day} onChange={handleChange}>
            <option value={1}>Sí</option>
            <option value={0}>No</option>
          </select>
        </label>

        <label>
          Evento especial
          <select name="event_day" value={value.event_day} onChange={handleChange}>
            <option value={0}>No</option>
            <option value={1}>Sí</option>
          </select>
        </label>
      </div>

      <button className="primary-button" onClick={onSubmit} disabled={loading}>
        {loading ? 'Calculando...' : 'Generar predicción'}
      </button>
    </section>
  )
}
