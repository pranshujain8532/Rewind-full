import { useEffect, useState } from 'react';
import { api, type EvidenceRecord, type Run } from './api';
import { isTerminal, refreshResource, useProgress, useResource } from './state';
import { Badge, CopyIdentifier, EmptyState, ErrorState, human, Icon, Loading, ModeBadge } from './ui/evidence';
import { Card, CardHeader, CardTitle, CardContent } from './ui/primitives';

type Arm = { configuration: string; status: string; harmful_attempts: number | null; harmful_dispatches: number | null; task_success: boolean | null; safety_requirement_met: boolean | null; valid: number; invalid: number; incomplete: number };
export function Regressions({ go }: { go: (url: string) => void }) {
  const params = new URLSearchParams(location.search);
  const [recordId, setRecordId] = useState(params.get('record') ?? '');
  const [runId, setRunId] = useState(params.get('run') ?? '');
  const [kind, setKind] = useState('behavioural');
  const [version, setVersion] = useState('behavioural-v1');
  const [left, setLeft] = useState('');
  const [comparison, setComparison] = useState<{ left: Run; right: Run } | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const records = useResource<EvidenceRecord[]>('/api/records');
  const recordQuery = useResource<EvidenceRecord>(recordId ? `/api/records/${recordId}` : null);
  const runs = useResource<Run[]>('/api/regression-runs');
  const runQuery = useResource<Run>(runId ? `/api/regression-runs/${runId}` : null);
  const record = recordQuery.data;
  const run = runQuery.data;
  const progress = useProgress('regression-runs', run?.id, run?.status, run?.last_event_seq ?? 0, () => { void runQuery.refresh(); void runs.refresh(); });
  useEffect(() => { if (!recordId && records.data?.[0]) setRecordId(records.data[0].id); }, [records.data, recordId]);
  useEffect(() => {
    if (!run) return;
    if (run.record_id) setRecordId(run.record_id);
    if (run.kind) setKind(run.kind);
    const schedule = run.plan.schedule as { configuration: string }[] | undefined;
    if (schedule?.[1]) setVersion(schedule[1].configuration);
  }, [run?.id]);
  const originalImpact = record?.observed_synthetic_impact.original_trace as { attempted_attachment_row_instances?: number } | undefined;
  const reason = !record ? 'Choose a stored evidence record.' : record.mode !== 'simulated' ? 'Original-attack regressions currently support simulator evidence only.' : record.replay_coverage.complete !== true ? 'Incomplete or invalid source evidence cannot produce a passing regression.' : !originalImpact?.attempted_attachment_row_instances ? 'The source does not contain an observed original harmful attack.' : '';
  async function start() {
    if (!record) return;
    const previousRunId = runId; setRunId('');
    setBusy(true); setError(''); setComparison(null);
    try {
      const regression = await api<{ id: string }>(`/api/regressions/from-record/${record.id}`, { kind });
      const current = await api<Run>('/api/regression-runs', { case_id: regression.id, fixed_configuration: version, mode: 'simulated' });
      setRunId(current.id); localStorage.setItem('rewind-regression-run', current.id);
      go(`/regressions?record=${record.id}&run=${current.id}`);
      void refreshResource('/api/regression-runs');
    } catch (e) { setRunId(previousRunId); setError(String(e)); } finally { setBusy(false); }
  }
  async function cancel() { try { await api(`/api/regression-runs/${runId}/cancel`, {}); await runQuery.refresh(); } catch (e) { setError(String(e)); } }
  async function compare() { try { setComparison(await api(`/api/regression-comparison?left=${left}&right=${runId}`)); } catch (e) { setError(String(e)); } }
  const arms = run?.manifest?.arms as { vulnerable: Arm; fixed: Arm } | undefined;
  return <>
    <div className="page-heading"><div><p className="eyebrow">REGRESSION / ORIGINAL ATTACK</p><h1>Does the defence still hold?</h1><p className="intro">The same original attack. A declared safety outcome. Useful work preserved.</p></div><ModeBadge mode="simulated" /></div>
    <Card><CardHeader><CardTitle>Contract & defence configuration</CardTitle><Badge>$0 provider spend</Badge></CardHeader><CardContent><div className="form-grid"><label>Source evidence record<select value={recordId} onChange={e => { setRecordId(e.target.value); setRunId(''); setComparison(null); go(`/regressions?record=${e.target.value}`); }}><option value="">Choose a record</option>{records.data?.map(r => <option key={r.id} value={r.id}>{r.id.slice(0, 8)} · {human(r.evidence_status)}</option>)}</select></label><label>Regression contract<select value={kind} onChange={e => { setKind(e.target.value); setVersion(e.target.value === 'behavioural' ? 'behavioural-v1' : 'containment-v1'); }}><option value="behavioural">Behavioural: no harmful attempts</option><option value="containment">Containment: no harmful dispatch</option></select></label><label>Defence configuration<select value={version} onChange={e => setVersion(e.target.value)}>{['behavioural-v1', 'containment-v1', 'vulnerable-v1', 'deny-all-v1'].map(v => <option key={v}>{v}</option>)}</select></label></div><p>One fresh deterministic simulator trial per arm, unchanged attack input. Budget: two trials, 60 seconds, $0. Safety and legitimate task must both pass; residual attempts remain visible. No confidence interval.</p><details><summary>Documented configuration behaviour</summary><ul><li>behavioural-v1: retain the input; ignore external executable directives.</li><li>containment-v1: retain attempts; enforce the captured owned recipient allowlist.</li><li>vulnerable-v1: interpret external directives; no enforcement.</li><li>deny-all-v1: deny all mock sends; task failure remains a failure.</li></ul></details><div className="form-actions"><button className="primary" onClick={() => void start()} disabled={busy || !!reason || (!!run && !isTerminal(run.status))} aria-describedby="regression-eligibility"><Icon name="play" size={16} />{busy ? 'Starting original attack…' : 'Run original-attack regression'}</button>{record && <a href={`/ledger/${record.id}`}>Inspect source record <Icon name="arrow" size={14} /></a>}</div><p id="regression-eligibility" className={reason ? 'capability-note' : 'muted'}>{run && !isTerminal(run.status) ? run.cancel_requested ? 'Cancellation requested; the actual in-flight result may still arrive.' : 'Current regression is active. Wait or cancel before starting another.' : reason || 'Source is complete and includes an observed original attack. The backend independently rechecks integrity and admission.'}</p></CardContent></Card>
    {[error, records.error, recordQuery.error, runQuery.error, runs.error].filter(Boolean).map((message, i) => <ErrorState key={i} message={message!} />)}
    {runId && !run && !runQuery.error && <Loading />}
    {run && <Card data-regression-id={run.id}><CardHeader><div><h2>Regression: {run.status} · {run.verdict}</h2><p className="muted">{run.completed_trials} stored outcomes / {run.started_trials} started · {progress.connection}</p></div><CopyIdentifier value={run.id} label="Copy regression identifier" /></CardHeader><CardContent><p>Execution duration: {run.elapsed_seconds === null || run.elapsed_seconds === undefined ? 'not started / unavailable' : `${run.elapsed_seconds.toFixed(1)} s`} ; server clock; terminal duration uses its persisted event.</p><p>{run.reason ?? run.manifest?.reason as string ?? 'Waiting for fresh stored outcomes.'}</p>{run.manifest && <p>Stored contract: {String(run.manifest.kind)}. Immutable original input: <code>{String(run.manifest.original_input_digest).slice(0, 16)}</code>.</p>}{!isTerminal(run.status) && <button disabled={run.cancel_requested} onClick={() => void cancel()}>{run.cancel_requested ? 'Cancellation requested' : 'Cancel regression'}</button>}{arms && <div className="table-scroll" tabIndex={0} role="region" aria-label="Original-attack results"><table><caption>Original-attack safety and useful task</caption><thead><tr><th>Configuration</th><th>Requirement</th><th>Residual attempts</th><th>Harmful dispatches</th><th>Safety</th><th>Useful task</th><th>Validity</th></tr></thead><tbody>{(['vulnerable', 'fixed'] as const).map(arm => <tr key={arm}><td><strong>{arm}</strong><br />{arms[arm].configuration}</td><td><Badge tone={arms[arm].status === 'pass' ? 'success' : 'caution'}>{arms[arm].status}</Badge></td><td>{arms[arm].harmful_attempts ?? 'unknown'}</td><td>{arms[arm].harmful_dispatches ?? 'unknown'}</td><td>{arms[arm].safety_requirement_met === null ? 'unknown' : arms[arm].safety_requirement_met ? 'pass' : 'fail'}</td><td>{arms[arm].task_success === null ? 'unknown' : arms[arm].task_success ? 'pass' : 'fail'}</td><td>{arms[arm].valid} valid · {arms[arm].invalid} invalid · {arms[arm].incomplete} incomplete</td></tr>)}</tbody></table></div>}{run.manifest && <><a className="button" href={`/api/regression-runs/${run.id}/download`} download><Icon name="download" size={16} />Download immutable regression manifest</a><ul>{(run.manifest.limitations as string[]).map(limit => <li key={limit}>{limit}</li>)}</ul></>}<details><summary>Frozen regression plan</summary><pre>{run.plan_json ?? 'Exact frozen plan unavailable'}</pre></details></CardContent></Card>}
    <Card><CardHeader><CardTitle>Stored run history & version comparison</CardTitle><Badge>Latest {runs.data?.length ?? 0}</Badge></CardHeader><CardContent>{runs.data?.length ? <><div className="table-scroll" tabIndex={0} role="region" aria-label="Regression run history"><table><caption>Immutable regression runs</caption><thead><tr><th>Run</th><th>Execution</th><th>Verdict</th><th>Stored counts</th><th>Open</th></tr></thead><tbody>{runs.data.map(r => <tr key={r.id}><td className="mono">{r.id.slice(0, 8)}</td><td>{r.status}</td><td>{r.verdict}</td><td>{r.completed_trials}/{r.started_trials}</td><td><button onClick={() => { setRunId(r.id); setComparison(null); go(`/regressions?record=${r.record_id ?? recordId}&run=${r.id}`); }}>Open run {r.id.slice(0, 8)}</button></td></tr>)}</tbody></table></div><div className="form-actions"><label>Compare with an earlier run<select value={left} onChange={e => { setLeft(e.target.value); setComparison(null); }}><option value="">Select same-case run</option>{runs.data.filter(r => r.id !== runId).map(r => <option key={r.id} value={r.id} disabled={!run || r.case_id !== run.case_id}>{r.id.slice(0, 8)} · {r.verdict}{!run || r.case_id !== run.case_id ? ' · different case' : ''}</option>)}</select></label><button disabled={!run || !left || !runs.data.some(r => r.id === left && r.case_id === run.case_id)} onClick={() => void compare()}>Compare stored runs</button></div><p className="muted">Comparisons require the same original case. No pooling of counts across versions.</p>{comparison && <div className="comparison-result" role="status">Stored version comparison: {comparison.left.verdict} → {comparison.right.verdict}. Each version retains its own safety, task and residual attempt counts.</div>}</> : <EmptyState title="No regressions yet">Create a regression from a complete signed record with an observed original attack.</EmptyState>}</CardContent></Card>
  </>;
}
