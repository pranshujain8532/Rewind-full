import { useEffect, useRef, useState } from 'react';
import type { components } from './generated/api';
import { api, type Session } from './api';
import { useResource } from './state';
import { Badge, EmptyState, ErrorState, Icon, Loading, ModeBadge } from './ui/evidence';
import { Card, CardContent, CardHeader, CardTitle } from './ui/primitives';

type SentinelSession = components['schemas']['SentinelSession'];
type Action = components['schemas']['ActionView'];
type AuditEvent = { body: { seq: number; type: string; time: string; data: { action_id?: string; reason?: string } }; event_hash: string };

export function Sentinel({ id, go }: { id: string | null; go: (url: string) => void }) {
  const sessions = useResource<SentinelSession[]>('/api/sentinel/sessions');
  const sources = useResource<Session[]>('/api/sessions');
  const selected = useResource<SentinelSession>(id ? `/api/sentinel/sessions/${id}` : null);
  const events = useResource<AuditEvent[]>(id ? `/api/sentinel/sessions/${id}/events` : null);
  const [source, setSource] = useState('');
  const [seconds, setSeconds] = useState(60);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const actionDialog = useRef<HTMLDialogElement>(null);
  const [choice, setChoice] = useState<{ action: Action; decision: 'approve' | 'deny' | 'deny_and_investigate' | 'cancel' } | null>(null);
  const [reason, setReason] = useState('');
  const session = selected.data;
  useEffect(() => {
    if (!id) return;
    let stopped = false;
    let timer: number;
    const update = async () => {
      if (navigator.onLine && document.visibilityState === 'visible') {
        await selected.refresh(); await events.refresh();
      }
      if (!stopped) timer = window.setTimeout(update, 1500);
    };
    timer = window.setTimeout(update, 1500);
    const recover = () => { void selected.refresh(); void events.refresh(); };
    window.addEventListener('online', recover); document.addEventListener('visibilitychange', recover);
    return () => { stopped = true; window.clearTimeout(timer); window.removeEventListener('online', recover); document.removeEventListener('visibilitychange', recover); };
  }, [id]);
  async function start(scenario?: 'single' | 'authorised') {
    setBusy(true); setError('');
    try {
      let sourceId = source;
      if (scenario) {
        const capture = await api<{ session_id: string; status: string }>('/api/demo/runs', { scenario });
        if (capture.status !== 'completed') throw new Error('Source capture failed; no protected run started.');
        sourceId = capture.session_id;
      }
      const result = await api<SentinelSession>('/api/sentinel/sessions', { source_session_id: sourceId, hold_seconds: seconds });
      await sessions.refresh(); await sources.refresh();
      go(`/sentinel?id=${result.id}`);
    } catch (e) { setError(String(e)); } finally { setBusy(false); }
  }
  function prompt(action: Action, decision: NonNullable<typeof choice>['decision']) {
    setChoice({ action, decision }); setReason(''); actionDialog.current?.showModal();
  }
  async function decide() {
    if (!choice) return;
    setBusy(true); setError('');
    const a = choice.action;
    try {
      await api<SentinelSession>(`/api/approvals/${a.id}/decision`, {
        decision: choice.decision, reason, action_digest: a.action_digest, args_digest: a.args_digest,
        session_id: a.session_id, mandate_version: a.mandate_version,
      });
      actionDialog.current?.close();
      await selected.refresh(); await events.refresh(); await sessions.refresh();
    } catch (e) { setError(String(e)); await selected.refresh(); } finally { setBusy(false); }
  }
  const available = sources.data?.filter(s => s.sealed && s.metadata.mode === 'simulated') ?? [];
  return <>
    <div className="page-heading"><div><p className="eyebrow">SENTINEL / BEFORE DISPATCH</p><h1>Sentinel</h1><p className="intro">Check the mandate. Hold eligible actions. Preserve each decision.</p></div><Badge>Rules · owned simulator</Badge></div>
    {(error || selected.error) && <ErrorState message={error || selected.error!} stale={!!session} retry={() => { setError(''); void selected.refresh(); }} />}
    <Card className="sentinel-setup"><CardHeader><CardTitle>Protected execution</CardTitle><p>Fresh simulator decisions from a trusted captured world. Every effect stays in the local synthetic sink.</p></CardHeader><CardContent>
      <div className="sentinel-start"><label>Captured source<select value={source} onChange={e => setSource(e.target.value)}><option value="">Choose a sealed simulator session</option>{available.map(s => <option key={s.id} value={s.id}>{s.id.slice(0, 8)} · {s.metadata.task_ref}</option>)}</select></label><label>Tool-call deadline<select value={seconds} onChange={e => setSeconds(Number(e.target.value))}><option value={60}>60 seconds</option><option value={300}>5 minutes</option><option value={5}>5 seconds · timeout demo</option></select></label><button className="primary" disabled={busy || !source} onClick={() => void start()}>Start protected run</button></div>
      <div className="action-row"><button disabled={busy} onClick={() => void start('single')}>Demo A · forbidden export</button><button disabled={busy} onClick={() => void start('authorised')}>Demo B · approval hold</button>{busy && <span role="status">Saving real execution state…</span>}</div>
      <p className="muted">Demos first record an observation-only source in owned mocks, then start a separate protected run. Source dispatches are separate from Sentinel dispatches.</p>
    </CardContent></Card>
    <div className="sentinel-layout"><Card><CardHeader><CardTitle>Protected runs</CardTitle><p>Stored executions · refresh preserves state</p></CardHeader><CardContent>
      {sessions.error && <ErrorState message={sessions.error} retry={() => void sessions.refresh()} />}
      {sessions.loading ? <Loading /> : !sessions.data?.length ? <EmptyState title="No protected runs yet">Start a demo or choose a complete simulator capture.</EmptyState> : <div className="sentinel-runs">{sessions.data.map(s => <a key={s.id} aria-current={s.id === id ? 'page' : undefined} href={`/sentinel?id=${s.id}`}><strong className="mono">{s.id.slice(0, 8)}</strong><Badge tone={s.status === 'awaiting_approval' ? 'caution' : s.status === 'completed' ? 'success' : 'danger'}>{s.status.replaceAll('_', ' ')}</Badge><small>{s.dispatched} dispatched · {s.actions.length} proposed</small></a>)}</div>}
    </CardContent></Card><div className="sentinel-workspace">
      {!id ? <Card><EmptyState title="Inspect an action before it runs">A forbidden export has a denial and an investigation path. An authorised high-impact action has an eligible approval hold.</EmptyState></Card> : !session ? <Loading /> : <>
        <Card><CardHeader><div className="action-row"><CardTitle>Run {session.id.slice(0, 8)}</CardTitle><ModeBadge mode={session.mode} /><Badge>{session.status.replaceAll('_', ' ')}</Badge></div></CardHeader><CardContent>
          <div className="sentinel-metrics"><div><strong>{session.dispatched}</strong><span>Protected dispatches</span></div><div><strong>{session.exported_rows}</strong><span>Synthetic row instances</span></div><div><strong>{session.task_success === null ? 'Pending' : session.task_success ? 'Passed' : 'Failed'}</strong><span>Legitimate task</span></div></div>
          <p><a href={`/sessions/${session.source_session_id}`}>Inspect captured source <Icon name="arrow" size={14} /></a> · <a href={`/api/sentinel/sessions/${session.id}/download`} download>Download signed policy audit</a></p>
          <p className="muted">Evidence: {session.evidence_status}. Coverage: {session.coverage}. Locally signed audit; verify with a separately trusted public key.</p>
        </CardContent></Card>
        {session.actions.length === 0 && <Card><EmptyState title="No proposed writes">The simulator completed its summary without requesting a send.</EmptyState></Card>}
        {session.actions.map(a => <Card key={a.id} className={`sentinel-action state-${a.state}`} data-action-id={a.id}>
          <CardHeader><div className="action-row"><Badge tone={a.state === 'held' ? 'caution' : a.state === 'dispatched' ? 'success' : 'danger'}>{a.state}</Badge><CardTitle>{a.tool}</CardTitle></div><p className="sentinel-reason">{a.reason.replaceAll('_', ' ')}</p></CardHeader><CardContent>
            <dl className="sentinel-facts"><dt>Policy verdict</dt><dd>{a.policy_verdict.replaceAll('_', ' ')}</dd><dt>Enforcement</dt><dd>{a.enforcement_decision}</dd><dt>Deadline</dt><dd><time dateTime={a.deadline}>{new Date(a.deadline).toLocaleString()}</time> · server enforced</dd><dt>Agent continuation</dt><dd>{a.agent_can_resume ? 'Owned adapter can continue with the recorded result' : 'This tool call cannot resume; start a new run'}</dd></dl>
            <pre className="code-box">{JSON.stringify(a.arguments, null, 2)}</pre>
            <details><summary>Exact approval binding</summary><dl className="sentinel-facts"><dt>Action digest</dt><dd className="mono">{a.action_digest}</dd><dt>Arguments digest</dt><dd className="mono">{a.args_digest}</dd><dt>Session</dt><dd className="mono">{a.session_id}</dd><dt>Mandate version</dt><dd className="mono">{a.mandate_version}</dd><dt>Authenticated approver</dt><dd>{a.approval?.approver_id as string ?? 'Local operator required; no approval consumed'}</dd></dl></details>
            {a.approval && <p>Approved by {String(a.approval.approver_id)} · consumed once at {new Date(Number(a.approval.consumed_at) * 1000).toLocaleString()}.</p>}
            <div className="action-row">
              {a.state === 'held' && a.policy_verdict === 'in_scope' && a.enforcement_decision === 'hold' && <button className="primary" disabled={busy || !!selected.error} onClick={() => prompt(a, 'approve')}>Approve exact action</button>}
              {a.state === 'held' && <><button disabled={busy || !!selected.error} onClick={() => prompt(a, 'deny')}>Deny action</button><button disabled={busy || !!selected.error} onClick={() => prompt(a, 'cancel')}>Cancel tool call</button></>}
              {['held', 'denied'].includes(a.state) && !a.investigation_id && <button disabled={busy || !!selected.error} onClick={() => prompt(a, 'deny_and_investigate')}>{a.investigation_error ? 'Retry investigation' : 'Deny and investigate'}</button>}
              {a.investigation_id && <a className="button" href={`/investigations/${a.investigation_id}`}>Open source investigation <Icon name="arrow" size={14} /></a>}
            </div>
            {a.state === 'denied' && <p className="muted">Dispatch is denied. Changing scope requires a new authorised mandate.</p>}
            {a.investigation_error && <p role="status">{a.investigation_error}</p>}
          </CardContent></Card>)}
        <Card><CardHeader><CardTitle>Signed mandate</CardTitle><p>Issuer and agent binding · exact recipient/data scope · $0 provider spend</p></CardHeader><CardContent><dl className="sentinel-facts"><dt>Issuer</dt><dd>{session.mandate.mandate.issuer}</dd><dt>Agent</dt><dd>{session.agent_id} · owned adapter binding</dd><dt>Validity</dt><dd>{new Date(session.mandate.mandate.not_before).toLocaleString()} → {new Date(session.mandate.mandate.not_after).toLocaleString()}</dd><dt>Recipient scope</dt><dd>{session.mandate.mandate.recipients.join(', ') || 'None'}</dd><dt>Data scope</dt><dd>{session.mandate.mandate.data_ids.join(', ')} · {session.mandate.mandate.data_classes.join(', ')}</dd><dt>Budget</dt><dd>{session.mandate.mandate.max_dispatches} dispatches / {session.mandate.mandate.max_export_rows} exported row instances per run</dd></dl><details><summary>Full signed mandate</summary><pre className="code-box">{JSON.stringify(session.mandate, null, 2)}</pre></details></CardContent></Card>
        <Card><CardHeader><CardTitle>Policy event trail</CardTitle><p>{events.error ? 'Connection unavailable · last stored events' : 'Persisted snapshots · polled every 1.5 seconds while visible'}</p></CardHeader><CardContent>{events.error && <ErrorState message={events.error} stale retry={() => void events.refresh()} />}<div className="table-scroll" tabIndex={0} role="region" aria-label="Sentinel event trail"><table><caption>Ordered signed events for this protected run</caption><thead><tr><th>Sequence</th><th>Event</th><th>Recorded time</th></tr></thead><tbody>{events.data?.map(e => <tr key={e.event_hash}><td>{e.body.seq}</td><td>{e.body.type.replaceAll('_', ' ')}</td><td><time dateTime={e.body.time}>{new Date(e.body.time).toLocaleTimeString()}</time></td></tr>)}</tbody></table></div></CardContent></Card>
        <p className="muted">{session.limitations.join(' ')}</p>
      </>}
    </div></div>
    <dialog ref={actionDialog} className="sentinel-dialog" aria-label="Confirm policy decision"><form onSubmit={e => { e.preventDefault(); void decide(); }}><div className="dialog-actions"><h2>{choice?.decision === 'approve' ? 'Approve this exact action' : 'Record policy decision'}</h2><button type="button" className="icon-button" aria-label="Close decision" disabled={busy} onClick={() => actionDialog.current?.close()}><Icon name="close" /></button></div><p>{choice?.decision.replaceAll('_', ' ')} · authenticated local operator</p><pre className="code-box">{JSON.stringify(choice?.action.arguments, null, 2)}</pre><p className="mono">Arguments digest: {choice?.action.args_digest}</p><label>Decision reason<textarea value={reason} onChange={e => setReason(e.target.value)} required maxLength={500} /></label><p className="muted">The server rechecks mandate, exact arguments, deadline, budget and action state before any dispatch.</p>{error && <p role="alert">{error}</p>}<button className="primary" disabled={busy || !reason.trim()} type="submit">Confirm {choice?.decision === 'approve' ? 'approval' : choice?.decision === 'cancel' ? 'cancellation' : 'denial'}</button></form></dialog>
  </>;
}
