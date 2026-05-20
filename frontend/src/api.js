const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

async function postJson(path, payload, errorLabel) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw new Error(`${errorLabel} failed with status ${response.status}`)
  }

  return response.json()
}

export async function compareAuctions(payload) {
  return postJson('/auction/compare', payload, 'Auction comparison')
}

export async function runGspAuction(payload) {
  return postJson('/auction/gsp', payload, 'GSP auction')
}

export async function runVcgAuction(payload) {
  return postJson('/auction/vcg', payload, 'VCG auction')
}

export async function computePriceOfAnarchy(payload) {
  return postJson('/metrics/price-of-anarchy', payload, 'Price of anarchy')
}

export async function checkNashEquilibrium(payload) {
  return postJson('/nash/check', payload, 'Nash equilibrium check')
}

export async function computeBestResponse(payload) {
  return postJson('/best-response', payload, 'Best response')
}

export async function computeBestResponseCurve(payload) {
  return postJson('/best-response/curve', payload, 'Best-response curve')
}

export async function trackRlConvergence(payload) {
  return postJson('/rl/convergence', payload, 'RL convergence')
}

export async function runStatisticalSimulation(payload) {
  return postJson('/simulation/statistical', payload, 'Statistical simulation')
}

export async function trainMultiAgentRl(payload) {
  return postJson('/rl/multi-agent', payload, 'Multi-agent RL training')
}

export async function compareStrategies(payload) {
  return postJson('/simulation/strategy-comparison', payload, 'Strategy comparison')
}

export async function checkHealth() {
  const response = await fetch(`${API_BASE_URL}/health`)

  if (!response.ok) {
    throw new Error(`Health check failed with status ${response.status}`)
  }

  return response.json()
}
