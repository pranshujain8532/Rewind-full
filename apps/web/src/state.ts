import { useEffect, useRef, useState, useSyncExternalStore } from 'react';
import { api } from './api';

type Snapshot = { data?: unknown; error?: string; loading: boolean };
type Entry = { snapshot: Snapshot; listeners: Set<() => void>; loading?: Promise<void>; again: boolean };
const cache = new Map<string, Entry>();
function entry(key: string) {
  if (!cache.has(key) && cache.size >= 64) {
    for (const [oldKey, old] of cache) {
      if (!old.listeners.size && !old.loading) { cache.delete(oldKey); break; }
    }
  }
  if (!cache.has(key)) cache.set(key, { snapshot: { loading: true }, listeners: new Set(), again: false });
  return cache.get(key)!;
}
function emit(current: Entry, next: Snapshot) { current.snapshot = next; current.listeners.forEach(listener => listener()); }

export async function refreshResource(key: string, loader: () => Promise<unknown> = () => api(key)) {
  const current = entry(key);
  if (current.loading) { current.again = true; return current.loading; }
  current.loading = (async () => {
    do {
      current.again = false;
      try { emit(current, { data: await loader(), loading: false }); }
      catch (error) { emit(current, { data: current.snapshot.data, error: String(error), loading: false }); }
    } while (current.again);
  })().finally(() => { current.loading = undefined; });
  return current.loading;
}

export function useResource<T>(key: string | null, loader?: () => Promise<T>) {
  const loaderRef = useRef(loader); loaderRef.current = loader;
  const current = entry(key ?? 'disabled');
  const snapshot = useSyncExternalStore(listener => { current.listeners.add(listener); return () => { current.listeners.delete(listener); }; }, () => current.snapshot);
  useEffect(() => { if (key) void refreshResource(key, loaderRef.current); }, [key]);
  return { ...snapshot, data: snapshot.data as T | undefined, refresh: () => key ? refreshResource(key, loaderRef.current) : Promise.resolve() };
}

export type Progress = { id: string; job_id: string; job_seq: number; type: string; time: string };
export function acceptProgress(event: Progress, id: string, cursor: number): boolean {
  return event.job_id === id && Number.isSafeInteger(event.job_seq) && event.job_seq > cursor && event.id === `${id}:${event.job_seq}`;
}
export const isTerminal = (status?: string) => !!status && ['completed', 'failed', 'cancelled', 'interrupted'].includes(status);

export function useProgress(kind: 'investigations' | 'regression-runs', id: string | undefined, status: string | undefined, seq: number, onProgress: () => void) {
  const callback = useRef(onProgress); callback.current = onProgress;
  const [connection, setConnection] = useState('Connecting');
  const [latest, setLatest] = useState<Progress | null>(null);
  const done = isTerminal(status);
  useEffect(() => {
    if (!id || !status || done) { setConnection(navigator.onLine ? 'Stored snapshot' : 'Offline · stored snapshot'); return; }
    let active = true;
    let cursor = seq;
    const stream = new EventSource(`/api/${kind}/${id}/events?after=${cursor}`);
    stream.onopen = () => { if (active) setConnection('Live · persisted events'); };
    stream.onerror = () => { if (active) setConnection(navigator.onLine ? 'Reconnecting · snapshot recovery' : 'Offline · last stored snapshot'); };
    stream.onmessage = message => {
      try {
        const event = JSON.parse(message.data) as Progress;
        if (!acceptProgress(event, id, cursor)) return;
        cursor = event.job_seq;
        if (active) { setLatest(event); callback.current(); }
      } catch { if (active) { setConnection('Invalid event · refreshing snapshot'); callback.current(); } }
    };
    const recover = () => { if (active) { callback.current(); setConnection(navigator.onLine ? 'Reconnecting · snapshot recovery' : 'Offline · last stored snapshot'); } };
    window.addEventListener('online', recover); window.addEventListener('offline', recover);
    // Recovery reads persisted facts. This timer never increments an experimental counter.
    const timer = window.setInterval(() => { if (active) callback.current(); }, 4000);
    return () => { active = false; stream.close(); window.clearInterval(timer); window.removeEventListener('online', recover); window.removeEventListener('offline', recover); };
    // seq is the initial REST cursor for this subscription; messages own its subsequent value.
  }, [kind, id, done, !!status]);
  return { connection, latest };
}

export function useRoute() {
  const [route, setRoute] = useState(location.pathname + location.search);
  useEffect(() => {
    const update = () => setRoute(location.pathname + location.search);
    const navigate = (event: MouseEvent) => {
      const anchor = (event.target as Element).closest('a');
      if (!anchor || event.defaultPrevented || event.button || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || anchor.download || anchor.hasAttribute('download') || anchor.target || anchor.origin !== location.origin || anchor.pathname.startsWith('/api/') || anchor.hash) return;
      event.preventDefault(); history.pushState({}, '', anchor.href); update();
    };
    window.addEventListener('popstate', update); document.addEventListener('click', navigate);
    return () => { window.removeEventListener('popstate', update); document.removeEventListener('click', navigate); };
  }, []);
  const go = (url: string) => { history.pushState({}, '', url); setRoute(url); };
  return { route, go };
}
