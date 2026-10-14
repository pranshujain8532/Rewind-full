import { useState } from 'react';
import type { components } from './generated/api';
import { api } from './api';
import { useProgress, useResource } from './state';
import { Badge, EmptyState, ErrorState, Icon, Loading, ModeBadge } from './ui/evidence';
import { Card, CardContent, CardHeader, CardTitle } from './ui/primitives';

type Snapshot = components['schemas']['PreflightSnapshot'];
type Configuration = 'vulnerable-v1' | 'containment-v1' | 'behavioural-v1' | 'deny-all-v1';
type Trial = { ordinal: number; session_id: string; investigation_id: string | null; spec: { fixture_id: string; configuration: string; surface: string; seed: number; fixture_digest: string; configuration_digest: string }; result: null | { validity: string; reason?: string; harmful_action_attempted?: boolean | null; harmful_policy_block?: boolean | null; harmful_action_executed?: boolean | null; legitimate_task_success?: boolean | null; model: string; usage: { host_elapsed_ms: number; provider_cost_usd: number; compute_cost_usd: number | null }; attempts?: unknown[]; dispatches?: unknown[] } };
const human = (value: string) => value.replaceAll('_', ' ');
const outcome = (value?: boolean | null) => value == null ? 'Unknown' : value ? 'Yes' : 'No';

export function Preflight({ id, go }: { id: string | null; go: (url: string) => void }) {
  const runs = useResource<Snapshot[]>('/api/preflight-runs');
  const selected = useResource<Snapshot>(id ? `/api/preflight-runs/${id}` : null);
  const trials = useResource<Trial[]>(id ? `/api/preflight-runs/${id}/trials` : null);
  const [configurations, setConfigurations] = useState<Configuration[]>(['vulnerable-v1', 'containment-v1']);
  const [maxTrials, setMaxTrials] = useState(32), [maxSeconds, setMaxSeconds] = useState(180), [repeats, setRepeats] = useState(1);
  const [busy, setBusy] = useState(false), [error, setError] = useState('');
  const run = selected.data;
  const refresh = () => { void selected.refresh(); void trials.refresh(); void runs.refresh(); };
  const progress = useProgress('preflight-runs', id ?? undefined, run?.status, run?.last_event_seq ?? 0, refresh);
  async function start() {
    setBusy(true); setError('');
    try {
      const created = await api<Snapshot>('/api/preflight-runs', {
        target_id: 'owned-support-agent-v1', suite_version: 'preflight-fixed-v1', configurations, repeats,
        budget: { max_trials: maxTrials, max_model_turns: maxTrials, max_seconds: maxSeconds, max_provider_cost_usd: 0 },
      });
      await runs.refresh(); go(`/preflight?id=${created.id}`);
    } catch (e) { setError(String(e)); } finally { setBusy(false); }
  }
  async function investigate(trial: Trial) {
    if (!id) return;
    setBusy(true); setError('');
    try {
      const link = await api<{ investigation_id: string }>(`/api/preflight-runs/${id}/trials/${trial.ordinal}/investigate`, {});
      go(`/investigations/${link.investigation_id}`);
    } catch (e) { setError(String(e)); } finally { setBusy(false); }
  }
  async function cancel() {
    setBusy(true); setError('');
    try { await api(`/api/preflight-runs/${id}/cancel`, {}); refresh(); }
    catch (e) { setError(String(e)); } finally { setBusy(false); }
  }
  return <>
    <div className="page-heading"><div><p className="eyebrow">PREFLIGHT / OWNED SANDBOX EVALUATION</p><h1>Preflight</h1><p className="intro">Rehearse a fixed suite. Inspect attempts, containment and useful work.</p></div><Badge>Fixed suite · no provider</Badge></div>
    {(error || selected.error) && <ErrorState message={error || selected.error!} stale={!!run} retry={() => { setError(''); refresh(); }} />}
    <Card className="preflight-setup"><CardHeader><CardTitle>Run the reviewed suite</CardTitle><p>Eight versioned fixtures across ticket comments and mock file text. Unknown-attachment cases deliberately exercise invalid-trial reporting.</p></CardHeader><CardContent>
      <div className="preflight-form"><label>Owned target<select value="owned-support-agent-v1" disabled><option value="owned-support-agent-v1">Owned support agent v1</option></select></label><label>Iteration limit<input type="number" value={maxTrials} min={1} max={96} onChange={e => setMaxTrials(Number(e.target.value))} /></label><label>Time limit (seconds)<input type="number" value={maxSeconds} min={1} max={600} onChange={e => setMaxSeconds(Number(e.target.value))} /></label><label>Deterministic repeats<input type="number" value={repeats} min={1} max={3} onChange={e => setRepeats(Number(e.target.value))} /></label></div>
      <fieldset className="preflight-presets"><legend>Versioned configurations</legend>{(['vulnerable-v1', 'containment-v1', 'behavioural-v1', 'deny-all-v1'] as Configuration[]).map(c => <label className="checkbox-label" key={c}><input type="checkbox" checked={configurations.includes(c)} onChange={e => setConfigurations(e.target.checked ? [...configurations, c] : configurations.filter(v => v !== c))} />{c}</label>)}</fieldset>
      <p className="muted">preflight-fixed-v1 · Only this target identifier is accepted. Policy presets are small owned rules. Guardrail classifier detection is not measured.</p>
      <div className="action-row"><button className="primary" disabled={busy || !configurations.length || maxTrials < 1 || maxTrials > 96 || maxSeconds < 1 || maxSeconds > 600 || repeats < 1 || repeats > 3} onClick={() => void start()}>Run fixed suite <Icon name="play" size={15} /></button>{busy && <span role="status">Saving actual job state…</span>}</div>
    </CardContent></Card>
    {!id && <Card><CardHeader><CardTitle>Stored suite runs</CardTitle></CardHeader><CardContent>{runs.error && <ErrorState message={runs.error} retry={() => void runs.refresh()} />}{runs.loading ? <Loading /> : !runs.data?.length ? <EmptyState title="No Preflight runs yet">Run the fixed suite inside the verified isolated runtime.</EmptyState> : <div className="recent-list">{runs.data.map(r => <a key={r.id} href={`/preflight?id=${r.id}`}><Icon name="play" /><span><strong>Suite {r.id.slice(0, 8)}</strong><small>{r.returned_trials}/{r.plan.schedule instanceof Array ? r.plan.schedule.length : '?'} returned</small></span><Badge>{r.status}</Badge></a>)}</div>}</CardContent></Card>}
    {id && !run && !selected.error && <Loading />}
    {run && <>
      <Card className="preflight-status" data-run-id={run.id}><CardHeader><div><CardTitle>Suite status: {run.status}</CardTitle><p>{progress.connection} · {run.id}</p></div><div className="action-row"><ModeBadge mode={run.mode} /><Badge>{human(run.evidence_status)}</Badge>{['queued', 'running'].includes(run.status) && <button disabled={busy || run.cancel_requested} onClick={() => void cancel()}>{run.cancel_requested ? 'Cancellation requested' : 'Cancel suite'}</button>}</div></CardHeader><CardContent>
        <div className="preflight-stats"><div><strong>{run.returned_trials}/{Array.isArray(run.plan.schedule) ? run.plan.schedule.length : '?'}</strong><span>Returned / planned</span></div><div><strong>{run.surface_counts.reduce((n,c) => n+c.valid,0)}/{run.started_trials}</strong><span>Valid / started</span></div><div><strong>{run.surface_counts.reduce((n,c) => n+c.invalid,0)}</strong><span>Invalid · retained</span></div><div><strong>${run.provider_cost_usd}</strong><span>Provider cost · compute not measured</span></div></div>
        {run.reason && <p role="status">{run.reason}</p>}<p className="muted">Deterministic repeats check reproducibility; they do not add independent statistical evidence. A completed job can contain invalid or failed trials.</p>
      </CardContent></Card>
      <Card><CardHeader><CardTitle>Attack-surface coverage</CardTitle><p>Actual stored counts, separated by surface and configuration. Invalid and incomplete outcomes remain unknown.</p></CardHeader><CardContent><div className="table-scroll" tabIndex={0} role="region" aria-label="Attack-surface coverage"><table><caption>Attempt and dispatch counts use valid-trial denominators. Policy blocks use harmful-attempt denominators.</caption><thead><tr><th>Surface / configuration</th><th>Valid / started / planned</th><th>Invalid / incomplete / not started</th><th>Harmful attempts / valid</th><th>Policy blocks / attempts</th><th>Harmful dispatches / valid</th><th>Task successes / valid</th><th>Guardrail classifier</th></tr></thead><tbody>{run.surface_counts.map(c => <tr key={`${c.surface}-${c.configuration}`}><th scope="row">{human(c.surface)}<small className="block">{c.configuration}</small></th><td>{c.valid}/{c.started}/{c.planned}</td><td>{c.invalid}/{c.incomplete}/{c.not_started}</td><td>{c.harmful_attempts}/{c.valid}</td><td>{c.harmful_policy_blocks}/{c.harmful_attempts}</td><td>{c.harmful_dispatches}/{c.valid}</td><td>{c.task_successes}/{c.valid}</td><td>Not measured</td></tr>)}</tbody></table></div><p className="muted">No evasion rate or risk percentage is inferred from these fixtures. 0/0 means no measured denominator.</p></CardContent></Card>
      <Card><CardHeader><CardTitle>Recorded trials</CardTitle><p>Each result retains fixture/configuration digests, model request, attempts, private mock effects, policy events and resource use.</p></CardHeader><CardContent>
        {trials.error && <ErrorState message={trials.error} stale={!!trials.data} retry={() => void trials.refresh()} />}
        {!trials.data?.length ? <EmptyState title="No trial reserved yet">Queued work has no fabricated outcomes.</EmptyState> : <div className="preflight-trials">{trials.data.map(t => {
          const r = t.result;
    const failure = !r || r.validity !== 'valid' || r.harmful_action_attempted || !r.legitimate_task_success;
          return <details key={t.ordinal} data-trial-ordinal={t.ordinal} className="preflight-trial"><summary>Trial {t.ordinal} · {human(t.spec.fixture_id)} · {t.spec.configuration} <Badge tone={!r || r.validity !== 'valid' ? 'caution' : r.harmful_action_executed ? 'danger' : ''}>{!r ? 'Incomplete' : r.validity !== 'valid' ? 'Invalid · outcome unknown' : r.harmful_action_attempted ? r.harmful_policy_block ? 'Unsafe attempt · contained' : 'Unsafe mock dispatch' : 'No harmful attempt'}</Badge></summary><dl><dt>Model</dt><dd>{r?.model ?? 'Not returned'}</dd><dt>Harmful attempt</dt><dd>{r?.validity === 'valid' ? outcome(r.harmful_action_attempted) : 'Unknown · invalid/incomplete trial'}</dd><dt>Harmful policy block</dt><dd>{outcome(r?.harmful_policy_block)}</dd><dt>Harmful mock dispatch</dt><dd>{r?.validity === 'valid' ? outcome(r.harmful_action_executed) : 'Unknown; inspect retained partial dispatches'}</dd><dt>Task success</dt><dd>{outcome(r?.legitimate_task_success)}</dd><dt>Guardrail detection</dt><dd>Not measured</dd><dt>Resource use</dt><dd>{r ? `${r.usage.host_elapsed_ms} ms host elapsed; $${r.usage.provider_cost_usd} provider cost; compute cost/tokens not measured` : 'One model turn reserved; result unavailable'}</dd><dt>Validity reason</dt><dd>{r?.reason ?? (r ? 'Code checked' : 'No returned result')}</dd><dt>Fixture digest</dt><dd className="mono">{t.spec.fixture_digest}</dd><dt>Configuration digest</dt><dd className="mono">{t.spec.configuration_digest}</dd><dt>Seed</dt><dd>{t.spec.seed}</dd></dl><div className="action-row"><a className="button" href={`/sessions/${t.session_id}`}>Open recorded session {t.ordinal} <Icon name="arrow" size={15} /></a>{t.investigation_id ? <a className="button" href={`/investigations/${t.investigation_id}`}>Open investigation {t.ordinal}</a> : failure && <button disabled={busy} onClick={() => void investigate(t)}>Investigate trial {t.ordinal}</button>}</div>{r && <details><summary>Actual attempted and executed mock actions</summary><pre>{JSON.stringify({ attempts: r.attempts, dispatches: r.dispatches }, null, 2)}</pre></details>}</details>;
        })}</div>}
      </CardContent></Card>
      <Card><CardHeader><CardTitle>Feature maturity</CardTitle></CardHeader><CardContent><table><caption>Preflight capabilities in this build</caption><thead><tr><th>Capability</th><th>Status</th></tr></thead><tbody><tr><td>Fixed reviewed two-surface suite</td><td>{run.maturity}</td></tr><tr><td>Evolutionary generation</td><td>Not implemented · documented extension</td></tr><tr><td>Budgeted LLM variations</td><td>Not implemented</td></tr><tr><td>Guardrail classifier</td><td>Not measured · absent</td></tr></tbody></table><p className="muted">{run.limitations.join(' ')}</p></CardContent></Card><a href="/preflight">All stored suite runs</a>
    </>}
  </>;
}
