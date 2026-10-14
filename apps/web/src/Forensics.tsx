import { useCallback, useEffect, useRef, useState } from 'react';
import type { components } from './generated/api';
import { Ledger } from './Ledger';

type Job = components['schemas']['JobSnapshot'];
type Graph = components['schemas']['GraphResponse'];
type Session = { id: string; sealed: boolean; metadata: { mode: string; task_ref: string } };
const terminal = new Set(['completed', 'cancelled', 'failed', 'interrupted']);

async function api<T>(path: string, body?: unknown, key?: string): Promise<T> {
  const response = await fetch(path, {
    method: body === undefined ? 'GET' : 'POST',
    headers: body === undefined ? {} : {
      'Content-Type': 'application/json', 'X-REWIND-Local': '1',
      ...(key ? { 'Idempotency-Key': key } : {}),
    },
    body: body === undefined ? undefined : JSON.stringify(body),
    signal: AbortSignal.timeout(45000),
  });
  if (response.status === 401 && path !== '/api/auth/local') {
    await api('/api/auth/local', {});
    return api<T>(path, body, key);
  }
  if (!response.ok) throw new Error(`HTTP ${response.status}: ${(await response.text()).slice(0, 300)}`);
  return response.status === 204 ? undefined as T : response.json() as Promise<T>;
}

export function Forensics({ onCaptured }: { onCaptured: () => void }) {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [session, setSession] = useState('');
  const [scenario, setScenario] = useState('single');
  const [stochastic, setStochastic] = useState(false);
  const [job, setJob] = useState<Job | null>(null);
  const [graph, setGraph] = useState<Graph | null>(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [ready, setReady] = useState(false);
  const lastSeq = useRef(0);

  const restore = useCallback(async () => {
    await api('/api/auth/local', {});
    const [captured, jobs] = await Promise.all([
      api<Session[]>('/api/sessions'), api<Job[]>('/api/investigations'),
    ]);
    setSessions(captured);
    setSession(current => current || captured.find(s => s.sealed && s.metadata.mode === 'simulated')?.id || '');
    const saved = localStorage.getItem('rewind-investigation-id');
    let current = saved ? jobs.find(j => j.id === saved) : jobs[0];
    if (saved && !current) {
      try { current = await api<Job>(`/api/investigations/${saved}`); }
      catch (e) { setError(`The saved investigation is unavailable: ${String(e)}`); }
    }
    if (current) { setJob(current); lastSeq.current = current.last_event_seq; }
    setReady(true);
  }, []);

  useEffect(() => { void restore().catch(e => setError(String(e))); }, [restore]);
  useEffect(() => {
    if (!session || !ready) return;
    let active = true;
    setGraph(null);
    void api<Graph>(`/api/sessions/${session}/graph`).then(g => { if (active) setGraph(g); })
      .catch(e => { if (active) setError(String(e)); });
    return () => { active = false; };
  }, [session, ready]);

  useEffect(() => {
    if (!job || terminal.has(job.status)) return;
    const id = job.id;
    let active = true;
    let fetching = false;
    const refresh = async () => {
      if (fetching) return;
      fetching = true;
      try {
        const current = await api<Job>(`/api/investigations/${id}`);
        if (active) { setJob(current); setError(''); }
      } catch (e) { if (active) setError(String(e)); }
      finally { fetching = false; }
    };
    const events = new EventSource(`/api/investigations/${id}/events?after=${lastSeq.current}`);
    events.onmessage = event => {
      const data = JSON.parse(event.data) as { job_seq: number };
      if (data.job_seq <= lastSeq.current) return;
      lastSeq.current = data.job_seq;
      void refresh();
    };
    // Snapshots also recover an expired worker lease or a disconnected event stream.
    const timer = window.setInterval(() => void refresh(), 1500);
    return () => { active = false; events.close(); window.clearInterval(timer); };
  }, [job?.id, job?.status]);

  async function createDemo() {
    setBusy(true); setError('');
    try {
      const result = await api<{ session_id: string; status: string }>('/api/demo/runs',
        { scenario }, crypto.randomUUID());
      if (result.status !== 'completed') throw new Error(`Demo capture ${result.status}; inspect the session before investigating.`);
      setSessions(await api<Session[]>('/api/sessions'));
      setSession(result.session_id);
      onCaptured();
    } catch (e) { setError(String(e)); } finally { setBusy(false); }
  }
  async function start() {
    setBusy(true); setError('');
    try {
      const current = await api<Job>('/api/investigations', {
        session_id: session, mode: 'simulated', stochastic,
        n: 40, max_finalists: 3, discovery_budget: 24,
        budget: { max_trials: 256, max_model_turns: 256, max_seconds: 600, max_tokens: 0, authorised_cost_usd: 0 },
      }, crypto.randomUUID());
      localStorage.setItem('rewind-investigation-id', current.id);
      lastSeq.current = 0;
      setJob(current);
    } catch (e) { setError(String(e)); } finally { setBusy(false); }
  }
  async function cancel() {
    if (!job) return;
    try { setJob(await api<Job>(`/api/investigations/${job.id}/cancel`, {})); }
    catch (e) { setError(String(e)); }
  }
  return <section className="panel forensics-panel" aria-labelledby="forensics-title">
    <div className="section-top"><h2 id="forensics-title">Forensics investigation</h2><span className="badge">Simulator only</span></div>
    <p>Fresh decisions in the isolated sandbox. Playback and real models are ineligible.</p>
    <div className="forensics-controls">
      <label>Owned scenario<select value={scenario} onChange={e => setScenario(e.target.value)}>
        {['single', 'interaction', 'redundant', 'harmless', 'clean', 'authorised'].map(s => <option key={s}>{s}</option>)}
      </select></label>
      <button onClick={() => void createDemo()} disabled={!ready || busy}>Capture demo scenario</button>
      <label>Captured session<select value={session} onChange={e => setSession(e.target.value)}>
        <option value="">Select a recorded session</option>
        {sessions.map(s => <option key={s.id} value={s.id} disabled={!s.sealed || s.metadata.mode !== 'simulated'}>{s.id.slice(0, 8)} · {s.metadata.mode} · {s.sealed ? 'sealed' : 'partial'}{s.metadata.mode !== 'simulated' ? ' · Forensics unsupported' : ''}</option>)}
      </select></label>
      <label className="checkbox-label"><input type="checkbox" checked={stochastic} onChange={e => setStochastic(e.target.checked)} />Stochastic simulator confirmation</label>
      <p className="muted">{stochastic ? '40 fresh runs per condition; at most 3 finalists. Independent Bernoulli gating (p=0.8), simulator uncertainty only.' : 'One fresh run per condition; exact deterministic fixture outcomes, no confidence interval.'} Budget: 256 trials, 600 seconds, no paid inference.</p>
      <button onClick={() => void start()} disabled={!ready || busy || !session}>Start investigation</button>
    </div>
    {error && <p role="alert" className="investigation-error">{error}</p>}
    {graph && <details><summary>Observable provenance · {graph.nodes.length} nodes, {graph.edges.length} relationships</summary>
      <p className="muted">{graph.ranking_formula}. Origin identity is unverified. These relationships describe observed input and action links.</p>
      <div className="table-scroll"><table><caption>Candidate ranking and input provenance</caption><thead><tr><th>Rank</th><th>Occurrence</th><th>Origin</th><th>Score</th><th>Distance</th></tr></thead>
        <tbody>{graph.candidates.map(c => <tr key={c.id}><td>{c.rank}</td><td>{c.target}</td><td>{c.origin}</td><td>{c.score.toFixed(2)}</td><td>{c.features.graph_distance ?? 'unknown'}</td></tr>)}</tbody></table></div>
      <ul>{graph.edges.map((e, i) => <li key={i}><code>{e.source.slice(0, 8)}</code> → <code>{e.target.slice(0, 8)}</code>: {e.relationship}</li>)}</ul>
    </details>}
    {job && <div className="job-result" data-job-id={job.id}>
      <h3>Investigation status: <span>{job.status}</span></h3>
      <p role="status">{job.completed_trials} stored outcomes / {job.started_trials} started trials · {job.evidence_status}</p>
      <p className="muted">Job {job.id}. Refresh restores this job from the database.</p>
      {job.reason && <p>{job.reason}</p>}
      {!terminal.has(job.status) && <button onClick={() => void cancel()} disabled={job.cancel_requested}>{job.cancel_requested ? 'Cancellation requested' : 'Cancel investigation'}</button>}
      {job.plan && <p>Confirmation plan frozen · {String(job.plan.n)} runs per condition · {String(job.plan.m)} findings · Plan digest <code>{job.plan_digest?.slice(0, 12)}</code></p>}
      {job.findings.map(f => <article className="finding" key={f.arm}>
        <h4>{f.targets.join(' + ')} · {f.evidence_status}</h4>
        <p>Harmful attempts: baseline {f.baseline.harmful}/{f.baseline.valid}; intervention {f.intervention.harmful}/{f.intervention.valid}. Useful tasks: {f.intervention.task_success}/{f.intervention.valid}.</p>
        <p>{f.effect === null ? 'Estimate unavailable.' : `Estimated reduction: ${(100 * f.effect).toFixed(1)} percentage points. Base flip-rate: ${(100 * (f.base_flip_rate ?? 0)).toFixed(1)}%.`}</p>
        <p>{f.interval ? `${(100 * f.interval_level).toFixed(2)}% Newcombe interval: ${(100 * f.interval[0]).toFixed(1)} to ${(100 * f.interval[1]).toFixed(1)} percentage points. This range expresses uncertainty in the simulator's harmful-action rates.` : 'No inferential interval for deterministic or incomplete samples.'}</p>
        <p>{f.reason} {f.scope}.</p>
      </article>)}
      <details><summary>Search coverage · {job.coverage.length} retained candidates</summary>
        <ul>{job.coverage.map(c => <li key={c.id}>{c.target}: {c.coverage}; tested subsets {(c.tested_subsets ?? []).join(', ') || 'none'}</li>)}</ul>
        <p>Untested candidates remain unknown. Discovery does not establish global minimality.</p>
      </details>
      <Ledger investigationId={job.id} status={job.status} />
    </div>}
  </section>;
}
