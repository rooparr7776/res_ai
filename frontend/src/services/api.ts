import type {
  EvaluationResult,
  Scenario,
  SimulationRequest,
  SimulationResult,
} from '../types'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_BASE}${path}`, init)
  } catch (error) {
    const reason = error instanceof Error ? error.message : 'Network request failed'
    throw new Error(`Cannot reach the DriveGuard backend at ${API_BASE}: ${reason}`)
  }

  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`
    try {
      const body: { detail?: string } = await response.json()
      detail = body.detail ?? detail
    } catch {
      // Keep the HTTP status as the actionable fallback when the error body is not JSON.
    }
    throw new Error(`Backend request failed: ${detail}`)
  }
  return response.json() as Promise<T>
}

export function getHealth(): Promise<{ status: string; service: string }> {
  return request('/api/health')
}

export function getScenarios(): Promise<Scenario[]> {
  return request('/api/scenarios')
}

export function runSimulation(body: SimulationRequest): Promise<SimulationResult> {
  return request('/api/simulate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}

export function runEvaluation(seed = 42, episodesPerScenario = 20): Promise<EvaluationResult> {
  return request('/api/evaluate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ seed, episodes_per_scenario: episodesPerScenario }),
  })
}

export async function downloadEvaluation(): Promise<void> {
  let response: Response
  try {
    response = await fetch(`${API_BASE}/api/results/export`)
  } catch (error) {
    const reason = error instanceof Error ? error.message : 'Network request failed'
    throw new Error(`Cannot reach the DriveGuard backend at ${API_BASE}: ${reason}`)
  }
  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`
    try {
      const body: { detail?: string } = await response.json()
      detail = body.detail ?? detail
    } catch {
      // Preserve the status detail for a non-JSON response.
    }
    throw new Error(`CSV export failed: ${detail}`)
  }
  const blob = await response.blob()
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'driveguard-evaluation.csv'
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.setTimeout(() => URL.revokeObjectURL(url), 1000)
}
