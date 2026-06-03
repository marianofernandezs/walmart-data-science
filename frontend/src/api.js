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
  predict: (payload) =>
    request('/predict', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
}
