import { useEffect, useState } from 'react';
import { allTrials, api, type EvidenceRecord, type Graph, type Job, type SessionDetail, type Trial } from './api';
import { isTerminal, refreshResource, useProgress, useResource } from './state';
import { SessionWorkspace } from './SessionWorkspace';
import { ActionDiff, Badge, EffectEstimate, EmptyState, ErrorState, EvidenceStatus, human, Icon, Loading, ModeBadge } from './ui/evidence';
import { Card, CardHeader, CardTitle, CardContent } from './ui/primitives';

export function StartInvestigation({ session, go, available }: { session: SessionDetail; go: (url: string) => void; available: boolean }) {
  const [stochastic, setStochastic] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const reason = !available ? 'Verified replay isolation is unavailable.' : session.replay.eligible !== true ? String(session.replay.reason) : '';
  async function start() {
    setBusy(true); setError('');
    try {
      const job = await api<Job>('/api/investigations', { session_id: session.id, mode: 'simulated', stochastic, n: 40, max_finalists: 3, discovery_budget: 24, budget: { max_trials: 256, max_model_turns: 256, max_seconds: 600, max_tokens: 0, authorised_cost_usd: 0 } });
      localStorage.setItem('rewind-investigation-id', job.id);
      go(`/investigations/${job.id}`);
    } catch (e) { setError(String(e)); } finally { setBusy(false); }
  }
  return <Card className="start-investigation"><CardHeader><div><CardTitle>Test an input intervention</CardTitle><p className="muted">Separate discovery from fresh, fixed-plan confirmation.</p></div><button className="primary" disabled={busy || !!reason} aria-describedby="investigation-eligibility" onClick={() => void start()}><Icon name="play" size={16} />{busy ? 'Starting…' : 'Start investigation'}</button></CardHeader><CardContent><label className="checkbox-label"><input type="checkbox" checked={stochastic} onChange={e => setStochastic(e.target.checked)} disabled={!!reason || busy} />Stochastic simulator confirmation</label><p>{stochastic ? '40 fresh runs per condition; at most three finalists. Independent simulator streams, alpha 0.05/m and a 20 pp meaningful threshold.' : 'One fresh run per condition. Deterministic fixture effects, no confidence interval.'} Budget: 256 trials, 600 seconds, $0 provider spend.</p><p id="investigation-eligibility" className={reason ? 'capability-note' : 'muted'}>{reason || 'Eligible: complete owned simulator capture. Hosted and local models are unsupported here.'}</p>{error && <ErrorState message={error} />}</CardContent></Card>;
}

export function Investigation({ id, go }: { id: string; go: (url: string) => void }) {
  const key = `/api/investigations/${id}`;
  const query = useResource<Job>(key);
  const job = query.data;
  const sessionQuery = useResource<SessionDetail>(job ? `/api/sessions/${job.session_id}` : null);
  const graphQuery = useResource<Graph>(sessionQuery.data?.replay.eligible ? `/api/sessions/${job?.session_id}/graph` : null);
  const trialsKey = `/api/investigations/${id}/trials/all`;
  const trialsQuery = useResource<Trial[]>(trialsKey, () => allTrials(id));
  const [selected, setSelected] = useState('');
  const [selectedNode, setSelectedNode] = useState(new URLSearchParams(location.search).get('node') ?? '');
  const [trialOrdinal, setTrialOrdinal] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const progress = useProgress('investigations', job?.id, job?.status, job?.last_event_seq ?? 0, () => { void query.refresh(); void refreshResource(trialsKey, () => allTrials(id)); });
  useEffect(() => { void refreshResource(trialsKey, () => allTrials(id)); }, [job?.completed_trials, job?.status]);
  useEffect(() => { if (job?.coverage.length && !selected) setSelected((job.coverage.find(c => c.id === selectedNode) ?? job.coverage[0]).target); }, [job?.coverage, selected, selectedNode]);
  if (!job) return query.error ? <ErrorState message={query.error} retry={() => void query.refresh()} /> : <Loading />;
  const findings = job.findings.filter(f => f.targets.includes(selected));
  const finding = selected ? findings[0] : job.findings[0];
  const rows = trialsQuery.data ?? [];
  const relevant = rows.filter(t => t.manifest.intervention.targets.includes(selected) || (finding && t.arm === finding.arm));
  const intervention = (trialOrdinal === null ? undefined : rows.find(t => t.ordinal === trialOrdinal)) ?? relevant.find(t => t.phase === 'confirmation' && t.result?.validity === 'valid') ?? relevant.find(t => t.result?.validity === 'valid');
  const baseline = rows.find(t => t.arm === 'baseline' && t.phase === intervention?.phase && t.result?.validity === 'valid') ?? rows.find(t => t.arm === 'baseline' && t.result?.validity === 'valid');
  async function cancel() { try { await api(`${key}/cancel`, {}); await query.refresh(); } catch (e) { setError(String(e)); } }
  async function save() {
    setBusy(true); setError('');
    try { const record = await api<EvidenceRecord>('/api/records', { investigation_id: id }); go(`/ledger/${record.id}`); }
    catch (e) { setError(String(e)); } finally { setBusy(false); }
  }
  return <>
    <div className="page-heading"><div><p className="eyebrow">FORENSICS / CONTROLLED INTERVENTION</p><h1>Investigation</h1><p className="intro">Change the input. Observe the behaviour. Keep the uncertainty.</p></div><div className="heading-actions"><a className="button" href={`/sessions/${job.session_id}`}>Open captured session</a><button className="primary" disabled={busy || !isTerminal(job.status)} aria-describedby="record-reason" onClick={() => void save()}><Icon name="ledger" size={16} />Create signed record</button></div></div>
    <div className="job-result" data-job-id={id}><Card className="progress-panel"><CardHeader><div><h2>Investigation status: {job.status}</h2><p className="muted" id="record-reason">{isTerminal(job.status) ? 'Stored outcomes are available for an immutable record.' : 'A signed record becomes available when execution reaches a terminal state.'}</p></div><ModeBadge mode={job.mode} /></CardHeader><CardContent><div className="progress-stats" aria-live="polite" aria-atomic="true"><div><strong>{job.completed_trials}</strong><span>stored outcomes</span></div><div><strong>{job.started_trials}</strong><span>started trials</span></div><div><strong>{job.budget.max_trials}</strong><span>authorised trial cap</span></div><div><EvidenceStatus status={job.evidence_status} /><span className="connection-state">{progress.connection}</span></div></div><progress value={job.completed_trials} max={job.started_trials || undefined} aria-label="Stored outcomes relative to actually started trials" hidden={!job.started_trials} /><p className="muted">Counts are stored outcomes / started trials. An unused budget is not uncompleted work. Duration: {job.elapsed_seconds === null || job.elapsed_seconds === undefined ? 'not started / unavailable' : `${job.elapsed_seconds.toFixed(1)} s`}; {isTerminal(job.status) ? 'stored start to terminal event' : 'server clock since stored start'}.</p><div className="progress-bottom"><span>{job.reason ?? (job.plan ? 'Confirmation plan frozen before fresh trials.' : 'Adaptive discovery precedes fixed confirmation.')}</span>{!isTerminal(job.status) && <button onClick={() => void cancel()} disabled={job.cancel_requested}>{job.cancel_requested ? 'Cancellation requested' : 'Cancel investigation'}</button>}</div>{job.plan && <details><summary>Confirmation plan frozen · {String(job.plan.n)} runs per condition · {String(job.plan.m)} predeclared findings</summary><pre>{job.plan_json ?? 'Exact frozen plan unavailable'}</pre><p>Plan digest: <code>{job.plan_digest}</code>. No optional stopping on fixed-sample intervals.</p></details>}</CardContent></Card></div>
    {(error || query.error) && <ErrorState message={error || query.error!} stale={!!query.error} retry={() => void query.refresh()} />}
    {trialsQuery.error && <ErrorState message={trialsQuery.error} stale={!!trialsQuery.data} retry={() => void trialsQuery.refresh()} />}
    <div className="investigation-hero"><div className="hero-source">
    {sessionQuery.error && <ErrorState message={sessionQuery.error} retry={() => void sessionQuery.refresh()} />}
    {sessionQuery.data && <SessionWorkspace session={sessionQuery.data} graph={graphQuery.data} compact selectedNode={selectedNode} onSelect={node => { setSelectedNode(node); const candidate = job.coverage.find(c => c.id === node); if (candidate) { setSelected(candidate.target); setTrialOrdinal(null); } }} />}
    <Card className="candidate-panel"><CardHeader><CardTitle>Interventions & search coverage</CardTitle><Badge>{job.coverage.length} retained candidates</Badge></CardHeader><CardContent><div className="candidate-grid">{job.coverage.map(candidate => {
      const f = job.findings.find(f => f.targets.includes(candidate.target));
      const running = rows.some(t => !t.result && t.manifest.intervention.targets.includes(candidate.target)) && !isTerminal(job.status);
      const status = f ? human(f.evidence_status) : running ? 'Testing' : candidate.coverage === 'untested' ? 'Not tested' : human(candidate.coverage);
      return <button key={candidate.id} className={`candidate-tile ${selected === candidate.target ? 'selected' : ''}`} aria-pressed={selected === candidate.target} onClick={() => { setSelected(candidate.target); setTrialOrdinal(null); setSelectedNode(candidate.id); const url = new URL(location.href); url.searchParams.set('node', candidate.id); history.replaceState({}, '', url); }}><span className="eyebrow">RANK {candidate.rank} · {candidate.origin}</span><strong>{candidate.target}</strong><span>{status}</span><small>{candidate.tested_subsets?.length ?? 0} stored discovery subsets · score {candidate.score.toFixed(2)}</small></button>;
    })}</div><p className="muted">Low-ranked and untested candidates remain unknown. Selected single, pair and group tests do not establish global minimality or monotonicity.</p></CardContent></Card>
    </div><div className="hero-comparison">
    <Card><CardHeader><div><CardTitle>Before / after actions</CardTitle><p className="muted">One selected stored trial per condition; aggregate counts are shown separately below.</p></div></CardHeader><CardContent><label>Selected intervention trial<select value={intervention?.ordinal ?? ''} onChange={e => setTrialOrdinal(Number(e.target.value))}><option value="">No stored intervention</option>{relevant.map(t => <option key={t.ordinal} value={t.ordinal}>#{t.ordinal} · {t.phase} · {t.arm} · {t.result?.validity ?? 'incomplete'}</option>)}</select></label><p className="muted">Changed occurrences: {intervention?.manifest.intervention.targets.join(' + ') || 'none'} · transformation: {intervention?.manifest.intervention.kind ?? 'unknown'}. Actual worker time: {intervention?.result?.elapsed_ms === undefined ? 'unavailable' : `${intervention.result.elapsed_ms} ms`}. Original #{baseline?.ordinal ?? 'unavailable'}, intervention #{intervention?.ordinal ?? 'unavailable'}.</p><ActionDiff before={baseline?.result?.attempts ?? []} after={intervention?.result?.attempts ?? []} beforeKnown={baseline?.result?.validity === 'valid'} afterKnown={intervention?.result?.validity === 'valid'} beforeOutcome={baseline?.result ?? undefined} afterOutcome={intervention?.result ?? undefined} /></CardContent></Card>
    {finding ? <EffectEstimate finding={finding} /> : <Card><EmptyState title={isTerminal(job.status) ? 'No finding for this candidate' : 'Confirmation is pending'}>{job.reason ?? 'This candidate has only exploratory or untested coverage. The overall investigation status is not a candidate finding.'}</EmptyState></Card>}
    </div></div>
    <details className="evidence-console"><summary>Evidence console · stored trials, scope & limitations</summary><div className="table-scroll" tabIndex={0} role="region" aria-label="Stored trial log"><table><caption>Every stored subset and outcome</caption><thead><tr><th>Trial</th><th>Phase</th><th>Arm / occurrences</th><th>Transformation</th><th>Validity</th><th>Attempt</th><th>Useful task</th></tr></thead><tbody>{rows.map(t => <tr key={t.ordinal}><td>{t.ordinal}</td><td>{t.phase}</td><td>{t.arm}<br />{t.manifest.intervention.targets.join(' + ')}</td><td>{t.manifest.intervention.kind}</td><td>{t.result?.validity ?? 'incomplete'}</td><td>{t.result?.validity === 'valid' ? String(t.result.harmful_action_attempted) : 'unknown'}</td><td>{t.result?.validity === 'valid' ? String(t.result.task_success) : 'unknown'}</td></tr>)}</tbody></table></div><ul>{job.limitations.map(limit => <li key={limit}>{limit}</li>)}</ul></details>
  </>;
}
