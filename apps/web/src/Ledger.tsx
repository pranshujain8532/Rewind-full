import { useEffect, useState } from 'react';
import type { components } from './generated/api';

type Record = components['schemas']['EvidenceRecord'];
type Run = components['schemas']['RegressionSnapshot'];
type Arm = { configuration: string; status: string; harmful_attempts: number | null; harmful_dispatches: number | null; task_success: boolean | null };

async function ledgerApi<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(path, {
    method: body === undefined ? 'GET' : 'POST',
    headers: body === undefined ? {} : { 'Content-Type': 'application/json', 'X-REWIND-Local': '1', 'Idempotency-Key': crypto.randomUUID() },
    body: body === undefined ? undefined : JSON.stringify(body), signal: AbortSignal.timeout(45000),
  });
  if (!response.ok) throw new Error(`Ledger request failed (${response.status}): ${(await response.text()).slice(0, 250)}`);
  return response.json() as Promise<T>;
}

export function Ledger({ investigationId, status }: { investigationId: string; status: string }) {
  const [record, setRecord] = useState<Record | null>(null);
  const [run, setRun] = useState<Run | null>(null);
  const [previous, setPrevious] = useState<Run | null>(null);
  const [kind, setKind] = useState<'behavioural' | 'containment'>('behavioural');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [comparison, setComparison] = useState('');
  useEffect(() => {
    let active = true;
    setRecord(null); setRun(null); setPrevious(null); setError(''); setComparison('');
    void ledgerApi<Record[]>('/api/records').then(records => {
      const saved = records.find(r => r.investigation_id === investigationId);
      if (!active || !saved) return;
      setRecord(saved);
      const id = localStorage.getItem('rewind-regression-run');
      if (id) void ledgerApi<Run>(`/api/regression-runs/${id}`).then(current => {
        if (active && Object.values(saved.regression_ids).includes(current.case_id)) {
          setRun(current);
          if (current.case_id === saved.regression_ids.containment) setKind('containment');
        }
      }).catch(() => { /* The evidence record remains available without this older run. */ });
    }).catch(e => { if (active) setError(String(e)); });
    return () => { active = false; };
  }, [investigationId]);
  useEffect(() => {
    if (!run || !['queued', 'running'].includes(run.status)) return;
    let active = true;
    const timer = window.setInterval(() => {
      void ledgerApi<Run>(`/api/regression-runs/${run.id}`).then(current => { if (active) { setRun(current); setError(''); } })
        .catch(e => { if (active) setError(String(e)); });
    }, 1500);
    return () => { active = false; window.clearInterval(timer); };
  }, [run?.id, run?.status]);
  async function save() {
    setBusy(true); setError('');
    try { setRecord(await ledgerApi<Record>('/api/records', { investigation_id: investigationId })); }
    catch (e) { setError(String(e)); } finally { setBusy(false); }
  }
  async function start() {
    if (!record) return;
    const priorRun = run;
    setPrevious(priorRun); setRun(null);
    setBusy(true); setError(''); setComparison('');
    try {
      const regression = await ledgerApi<{ id: string }>(`/api/regressions/from-record/${record.id}`, { kind });
      const current = await ledgerApi<Run>('/api/regression-runs', {
        case_id: regression.id, fixed_configuration: kind === 'behavioural' ? 'behavioural-v1' : 'containment-v1', mode: 'simulated',
      });
      setRun(current); localStorage.setItem('rewind-regression-run', current.id);
    } catch (e) { setRun(priorRun); setError(String(e)); } finally { setBusy(false); }
  }
  async function compare() {
    if (!run || !previous) return;
    try {
      const result = await ledgerApi<{ left: Run; right: Run }>(`/api/regression-comparison?left=${previous.id}&right=${run.id}`);
      setComparison(`Stored version comparison: ${result.left.verdict} → ${result.right.verdict}. Each run retains its own counts.`);
    } catch (e) { setError(String(e)); }
  }
  const arms = run?.manifest?.arms as { vulnerable: Arm; fixed: Arm } | undefined;
  return <section className="ledger-panel" aria-labelledby="ledger-title">
    <h3 id="ledger-title">Ledger evidence and regression</h3>
    <p>The signed record binds the stored trace and trials. A separately trusted public key establishes integrity; it does not prove truth or blame.</p>
    <button disabled={busy || !['completed', 'cancelled', 'failed', 'interrupted'].includes(status)} onClick={() => void save()}>Create signed record</button>
    {error && <p role="alert">{error}</p>}
    {record && <>
      <p>Record {record.id.slice(0, 8)} · {record.evidence_status}. Governance mapping pending.</p>
      <a href={`/api/records/${record.id}/download`} download>Download signed evidence bundle</a>
      <label>Regression contract<select value={kind} onChange={e => setKind(e.target.value as typeof kind)}>
        <option value="behavioural">Behavioural: prevent harmful attempts</option>
        <option value="containment">Containment: block dispatch; report attempts</option>
      </select></label>
      <p>Fresh simulator decisions on the unchanged original attack, using vulnerable and fixed configurations. Budget: two trials, 60 seconds, no paid inference. No confidence interval.</p>
      <button disabled={busy || (run !== null && ['queued', 'running'].includes(run.status))} onClick={() => void start()}>Run original-attack regression</button>
    </>}
    {run && <div data-regression-id={run.id}>
      <h4>Regression: {run.status} · {run.verdict}</h4>
      {run.manifest && <p>Stored contract: {String(run.manifest.kind)}.</p>}
      <p>{run.completed_trials} stored outcomes / {run.started_trials} started. {run.reason}</p>
      {arms && <div className="table-scroll" tabIndex={0} role="region" aria-label="Original-attack results, scroll horizontally"><table><caption>Original-attack safety and useful task</caption><thead><tr><th>Configuration</th><th>Requirement</th><th>Residual attempts</th><th>Harmful dispatches</th><th>Task</th></tr></thead>
        <tbody>{(['vulnerable', 'fixed'] as const).map(arm => <tr key={arm}><td>{arm} · {arms[arm].configuration}</td><td>{arms[arm].status}</td><td>{arms[arm].harmful_attempts ?? 'unknown'}</td><td>{arms[arm].harmful_dispatches ?? 'unknown'}</td><td>{arms[arm].task_success === null ? 'unknown' : arms[arm].task_success ? 'pass' : 'fail'}</td></tr>)}</tbody></table></div>}
      {run.manifest && <a href={`/api/regression-runs/${run.id}/download`} download>Download immutable regression manifest</a>}
      {previous && previous.case_id === run.case_id && <button onClick={() => void compare()}>Compare stored runs</button>}
      {comparison && <p>{comparison}</p>}
    </div>}
  </section>;
}
