const API_BASE_URL = 'http://localhost:8000'

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  })

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}))
    throw new Error(errorBody.detail || 'No se pudo completar la solicitud')
  }

  return response.json()
}

export const api = {
  getHealth: () => request('/health'),
  getProducts: () => request('/products'),
  getAlerts: () => request('/alerts'),
  getMetrics: () => request('/metrics'),
  getArchitecture: () => request('/architecture'),
  getIngestionSchema: () => request('/ingestion/schema'),
  getIngestionFiles: () => request('/ingestion/files'),
  getIngestionPreview: (filename) =>
    request(filename ? `/ingestion/preview?filename=${encodeURIComponent(filename)}` : '/ingestion/preview'),
  uploadCSV: async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await fetch(`${API_BASE_URL}/ingestion/upload-csv`, {
      method: 'POST',
      body: formData,
    })
    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}))
      throw new Error(errorBody.detail || 'No se pudo subir el CSV')
    }
    return response.json()
  },
  ingestJSON: (payload) =>
    request('/ingestion/json', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  deleteIngestionFile: (filename) =>
    request(`/ingestion/files/${encodeURIComponent(filename)}`, {
      method: 'DELETE',
    }),
  clearIngestionFiles: () =>
    request('/ingestion/clear', {
      method: 'DELETE',
    }),
  predict: (payload) =>
    request('/predict', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
}
