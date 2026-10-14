import type { components } from './generated/api';

export type Health = components['schemas']['HealthResponse'];
export type Capabilities = components['schemas']['CapabilitiesResponse'];
export type SessionDetail = components['schemas']['SessionDetail'];
export type Job = components['schemas']['JobSnapshot'];
export type Graph = components['schemas']['GraphResponse'];
export type Finding = components['schemas']['Finding'];
export type EvidenceRecord = components['schemas']['EvidenceRecord'];
export type Run = components['schemas']['RegressionSnapshot'];
export type Session = { id: string; sealed: boolean; metadata: { mode: string; task_ref?: string; model?: string } };
export type Action = { tool: string; arguments: { [key: string]: unknown } };
export type Trial = { ordinal: number; phase: string; arm: string; manifest: { intervention: { kind: string; targets: string[] } }; result: null | { validity: string; reason?: string; harmful_action_attempted?: boolean; task_success?: boolean; attempts?: Action[]; dispatches?: Action[]; model_response?: { actions: Action[] }; elapsed_ms?: number } };

let authenticating: Promise<void> | null = null;
let authenticatedOnce = false;
export async function authenticate(): Promise<void> {
  if (!authenticating) authenticating = fetch('/api/auth/local', { method: 'POST', headers: { 'X-REWIND-Local': '1' } })
    .then(response => { if (!response.ok) throw new Error(`Local access unavailable (${response.status}).`); authenticatedOnce = true; })
    .finally(() => { authenticating = null; });
  return authenticating;
}

export async function api<T>(path: string, body?: unknown, key = crypto.randomUUID()): Promise<T> {
  if (!authenticatedOnce) await authenticate();
  async function request() {
    return fetch(path, {
      method: body === undefined ? 'GET' : 'POST',
      headers: body === undefined ? {} : { 'Content-Type': 'application/json', 'X-REWIND-Local': '1', 'Idempotency-Key': key },
      body: body === undefined ? undefined : JSON.stringify(body), signal: AbortSignal.timeout(45000),
    });
  }
  let response = await request();
  if (response.status === 401) { authenticatedOnce = false; await authenticate(); response = await request(); }
  if (!response.ok) {
    const detail = (await response.text()).slice(0, 350);
    throw new Error(`Request unavailable (${response.status}): ${detail}`);
  }
  return response.status === 204 ? undefined as T : response.json() as Promise<T>;
}

export async function allTrials(id: string): Promise<Trial[]> {
  const rows: Trial[] = [];
  // The backend budget is bounded at 512; never silently drop later confirmation rows.
  for (let offset = 0; offset < 512; offset += 100) {
    const page = await api<Trial[]>(`/api/investigations/${id}/trials?offset=${offset}&limit=100`);
    rows.push(...page);
    if (page.length < 100) break;
  }
  return rows;
}

async function read<T>(path: string): Promise<T> {
  const response = await fetch(path, { signal: AbortSignal.timeout(8000) });
  // A 503 health response is a structured readiness result, not a transport error.
  if (!response.ok && !(path === '/api/health' && response.status === 503)) {
    throw new Error(`The API returned HTTP ${response.status}.`);
  }
  if (!response.headers.get('content-type')?.includes('application/json')) {
    throw new Error('The API did not return JSON. Check that the backend is running.');
  }
  return response.json() as Promise<T>;
}

export async function readSystem(): Promise<{ health: Health; capabilities: Capabilities }> {
  const [health, capabilities] = await Promise.all([
    read<Health>('/api/health'), read<Capabilities>('/api/capabilities'),
  ]);
  return { health, capabilities };
}
