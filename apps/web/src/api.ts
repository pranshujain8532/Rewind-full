import type { components } from './generated/api';

export type Health = components['schemas']['HealthResponse'];
export type Capabilities = components['schemas']['CapabilitiesResponse'];

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
