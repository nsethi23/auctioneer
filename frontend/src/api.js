const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

export async function compareAuctions(payload) {
  const response = await fetch(`${API_BASE_URL}/auction/compare`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw new Error(`Auction comparison failed with status ${response.status}`)
  }

  return response.json()
}
