export default function IngestionSummary({ summary, files, onDeleteFile, onClearAll, loading }) {
  const processedFiles = files.filter((file) => file.category === 'processed')

  return (
    <section className="panel">
      <div className="panel-heading">
        <p className="eyebrow">Resultado de ingesta</p>
        <h2>Resumen y archivos</h2>
        <p className="section-copy">
          Gestiona aquí la información nueva subida. Puedes borrar archivos individuales o limpiar toda la ingesta.
        </p>
      </div>

      {summary ? (
        <div className="stats-grid stats-grid-ingestion">
          <article className={`status-card status-${summary.status}`}>
            <span>Estado</span>
            <strong>{summary.status}</strong>
          </article>
          <article>
            <span>Recibidas</span>
            <strong>{summary.rows_received}</strong>
          </article>
          <article>
            <span>Válidas</span>
            <strong>{summary.rows_valid}</strong>
          </article>
          <article>
            <span>Rechazadas</span>
            <strong>{summary.rows_rejected}</strong>
          </article>
        </div>
      ) : (
        <p className="muted">Todavía no hay una ingesta ejecutada en esta sesión.</p>
      )}

      <div className="ingestion-actions">
        <button
          className="secondary-button"
          onClick={onClearAll}
          disabled={loading || files.length === 0}
        >
          {loading ? 'Limpiando...' : 'Borrar toda la información subida'}
        </button>
        <span className="muted small-copy">
          {processedFiles.length} archivo(s) processed disponibles para predicción.
        </span>
      </div>

      <div className="table-shell">
        <table>
          <thead>
            <tr>
              <th>Archivo</th>
              <th>Tipo</th>
              <th>Filas</th>
              <th>Acción</th>
            </tr>
          </thead>
          <tbody>
            {files.length ? (
              files.map((file) => (
                <tr key={`${file.category}-${file.filename}`}>
                  <td>{file.filename}</td>
                  <td><span className={`file-badge badge-${file.category}`}>{file.category}</span></td>
                  <td>{file.rows ?? '-'}</td>
                  <td>
                    <button
                      className="ghost-button danger-button"
                      onClick={() => onDeleteFile(file.filename)}
                      disabled={loading}
                    >
                      Borrar
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="4" className="empty-row">No hay archivos de ingesta guardados.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  )
}
