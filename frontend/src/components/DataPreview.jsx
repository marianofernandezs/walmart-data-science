export default function DataPreview({ preview }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <p className="eyebrow">Preview</p>
        <h2>Último archivo procesado</h2>
        <p className="section-copy">
          Vista rápida de las primeras 10 filas del archivo `processed` más reciente.
        </p>
      </div>

      {!preview?.rows?.length ? (
        <p className="muted">Sin datos procesados todavía.</p>
      ) : (
        <>
          <div className="preview-header">
            <span className="file-badge badge-processed">{preview.filename}</span>
            <span className="muted small-copy">{preview.rows.length} fila(s) visibles</span>
          </div>
        <div className="table-shell">
          <table>
            <thead>
              <tr>
                {Object.keys(preview.rows[0]).map((key) => (
                  <th key={key}>{key}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {preview.rows.map((row, index) => (
                <tr key={`${preview.filename}-${index}`}>
                  {Object.keys(preview.rows[0]).map((key) => (
                    <td key={key}>{String(row[key] ?? '')}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        </>
      )}
    </section>
  )
}
