import { useEffect, useRef, useState } from 'react';
import type { Graph, SessionDetail } from './api';
import { Badge, CoverageBadge, CopyIdentifier, human, Icon, IntegrityStatus, ModeBadge } from './ui/evidence';
import { Card, CardHeader, CardTitle, CardContent } from './ui/primitives';

type Node = Graph['nodes'][number];
export function ProvenanceNode({ node, label, selected, select, style }: { node: Node; label: string; selected: boolean; select: () => void; style: React.CSSProperties }) {
  return <button className={`provenance-node ${selected ? 'selected' : ''}`} style={style} aria-pressed={selected} data-node-id={String(node.id)} onClick={select}><span className="node-kind"><Icon name={node.kind === 'input_occurrence' ? 'sessions' : node.kind === 'tool_requested' ? 'arrow' : 'graph'} size={15} />{human(String(node.kind))}</span><strong>{label}</strong><small>{node.origin ? `${node.origin} · identity unverified` : `Event ${node.seq}`}</small></button>;
}

export function SessionWorkspace({ session, graph, selectedNode, onSelect, compact = false }: { session: SessionDetail; graph?: Graph; selectedNode?: string; onSelect?: (id: string) => void; compact?: boolean }) {
  const initial = new URLSearchParams(location.search).get('node');
  const [localSelected, setSelected] = useState(initial ?? session.inputs[0]?.id ?? session.events[0]?.id ?? '');
  const selected = selectedNode || localSelected;
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => { setSelected(new URLSearchParams(location.search).get('node') ?? session.inputs[0]?.id ?? session.events[0]?.id ?? ''); }, [session.id]);
  const input = session.inputs.find(i => i.id === selected);
  const eventId = input?.model_event_id ?? selected;
  const event = session.events.find(e => e.id === eventId);
  const candidate = graph?.candidates.find(c => c.id === selected);
  const select = (id: string) => {
    setSelected(id);
    onSelect?.(id);
    const url = new URL(location.href); url.searchParams.set('node', id); history.replaceState({}, '', url);
  };
  const label = (node: Node) => session.inputs.find(i => i.id === node.id)?.target ?? `Event ${node.seq ?? String(node.id).slice(0, 8)}`;
  const groups = graph ? [graph.nodes.filter(n => n.kind === 'input_occurrence'), graph.nodes.filter(n => n.kind === 'model_request' || n.kind === 'model_response'), graph.nodes.filter(n => n.kind !== 'input_occurrence' && n.kind !== 'model_request' && n.kind !== 'model_response')] : [];
  const positions = new Map<string, { x: number; y: number }>();
  groups.forEach((group, col) => group.forEach((node, row) => positions.set(String(node.id), { x: 20 + col * 244, y: 45 + row * 108 })));
  const graphHeight = Math.max(260, ...groups.map(group => group.length * 108 + 62));
  const details = <>
    <div className="inspector-title"><span className="eyebrow">SELECTED EVIDENCE</span><Icon name="sessions" size={18} /></div>
    <h3>{input?.target ?? human(event?.kind ?? 'No selected event')}</h3>
    <CopyIdentifier value={selected} label="Copy selected evidence identifier" />
    {input && <><dl><dt>Source</dt><dd>{input.source_uri}</dd><dt>Origin</dt><dd>{input.origin} · unverified identity</dd><dt>Included in</dt><dd>Event {event?.seq ?? 'unknown'} · model input</dd><dt>Display</dt><dd>Redacted{input.display_truncated ? ' · text truncated' : ''}</dd></dl><h4>Captured input</h4><pre className="hostile-input" data-testid="input-text">{input.text || 'Payload unavailable'}</pre></>}
    {!input && event && <><dl><dt>Sequence</dt><dd>{event.seq}</dd><dt>Time</dt><dd>{new Date(event.time).toLocaleTimeString()}</dd><dt>Capture source</dt><dd>{event.source}</dd></dl><h4>Stored payload · redacted</h4><pre className="hostile-input">{event.payload_text}</pre></>}
    {candidate && <details><summary>Why this candidate was ranked</summary><p>Rank {candidate.rank} · score {candidate.score.toFixed(2)}</p><dl>{Object.entries(candidate.features).map(([key, value]) => <div key={key}><dt>{human(key)}</dt><dd>{value ?? 'unknown'}</dd></div>)}</dl><p>Ranking prioritises search. It does not establish cause.</p></details>}
    <div className="inspector-note"><Icon name="info" size={16} /><p>Edges describe captured relationships. An ancestor is not a proven cause.</p></div>
  </>;
  const timeline = <Card className="timeline-panel"><CardHeader><CardTitle>Captured timeline</CardTitle><Badge>{session.events.length} stored events</Badge></CardHeader><CardContent><div className="timeline-scrubber" aria-label="Event sequence">{session.events.map(e => <button key={e.id} aria-label={`Go to event ${e.seq}`} aria-pressed={e.id === eventId} onClick={() => select(e.id)} title={human(e.kind)}>{e.seq}</button>)}</div><div className="event-list table-scroll" role="region" tabIndex={0} aria-label="Captured event timeline"><table><caption>Captured events · selecting an event updates graph and details</caption><thead><tr><th>Seq.</th><th>Event</th><th>Time</th><th>Source</th></tr></thead><tbody>{session.events.map(e => <tr key={e.id} data-selected={e.id === eventId}><td className="mono">{String(e.seq).padStart(2, '0')}</td><td><button aria-pressed={e.id === eventId} onClick={() => select(e.id)} aria-label={`Inspect event ${e.seq} ${human(e.kind)}`}>{human(e.kind)}</button></td><td className="mono">{new Date(e.time).toLocaleTimeString()}</td><td>{e.source}</td></tr>)}</tbody></table></div></CardContent></Card>;
  return <>
    <div className="evidence-badges"><ModeBadge mode={String(session.metadata.mode ?? 'unknown')} /><Badge>Evidence: recorded trace</Badge><CoverageBadge complete={session.capture_coverage.complete === true} /><IntegrityStatus status={String(session.integrity.status)} /></div>
    <div className={`explorer-grid ${compact ? 'compact-explorer' : ''}`} data-selected-node={selected} data-selected-event={eventId}>
      <div className="explorer-main">
        <Card className="provenance-panel"><CardHeader><div><span className="eyebrow">FOLLOW THE INPUT</span><CardTitle>Observable provenance</CardTitle></div><button className="inspector-toggle" onClick={() => dialog.current?.showModal()}><Icon name="sessions" size={16} />Inspect selection</button></CardHeader><CardContent>
          <div className="graph-legend"><span><i className="legend-input" />Input occurrence</span><span><i className="legend-model" />Model boundary</span><span><i className="legend-action" />Action</span><span className="muted">Observed links · stable layout</span></div>
          {graph ? <>
            <div className="graph-scroll" role="region" tabIndex={0} aria-label="Observable provenance graph, scroll horizontally">
              <div className="provenance-canvas" style={{ height: graphHeight, width: 736 }}>
                <div className="graph-column-labels"><span>CAPTURED INPUTS</span><span>AGENT DECISION</span><span>ATTEMPT / DISPATCH</span></div>
                <svg width="736" height={graphHeight} className="graph-edges" aria-hidden="true"><defs><marker id={`edge-${session.id}`} viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" /></marker></defs>{graph.edges.map((edge, i) => {
                  const a = positions.get(edge.source), b = positions.get(edge.target); if (!a || !b) return null;
                  const same = a.x === b.x;
                  const d = same ? `M${a.x + 196} ${a.y + 80} C${a.x + 230} ${a.y + 95} ${b.x + 230} ${b.y - 15} ${b.x + 196} ${b.y}` : `M${a.x + 208} ${a.y + 42} C${a.x + 230} ${a.y + 42} ${b.x - 24} ${b.y + 42} ${b.x} ${b.y + 42}`;
                  return <path key={i} d={d} className={edge.source === selected || edge.target === selected ? 'edge-active' : ''} markerEnd={`url(#edge-${session.id})`}><title>{edge.relationship}</title></path>;
                })}</svg>
                {graph.nodes.map(node => { const p = positions.get(String(node.id))!; return <ProvenanceNode key={String(node.id)} node={node} label={label(node)} selected={selected === node.id} select={() => select(String(node.id))} style={{ left: p.x, top: p.y, width: 208 }} />; })}
              </div>
            </div>
            <details className="graph-table" open={window.matchMedia('(max-width: 700px)').matches || undefined}><summary>Accessible provenance table · {graph.nodes.length} nodes</summary><div className="table-scroll" role="region" tabIndex={0} aria-label="Provenance node table"><table><caption>Observable provenance nodes</caption><thead><tr><th>Node</th><th>Kind</th><th>Origin</th></tr></thead><tbody>{graph.nodes.map(node => <tr key={String(node.id)} data-selected={selected === node.id}><td><button aria-label={`Select ${label(node)}`} aria-pressed={selected === node.id} onClick={() => select(String(node.id))}>{label(node)}</button></td><td>{human(String(node.kind))}</td><td>{String(node.origin ?? 'captured boundary')}</td></tr>)}</tbody></table></div><details><summary>Observed relationships</summary><ul>{graph.edges.map((edge, i) => <li key={i}><code>{edge.source.slice(0, 8)}</code> → <code>{edge.target.slice(0, 8)}</code>: {human(edge.relationship)}</li>)}</ul></details></details>
          </> : <p className="capability-note">{session.replay.eligible ? 'Provenance snapshot not available yet; use the retry control if reading fails.' : `Graph unavailable: ${String(session.replay.reason)}.`} Recorded events remain inspectable; no causal relationship is inferred.</p>}
        </CardContent></Card>
        {compact ? <details className="timeline-console"><summary>Captured timeline / {session.events.length} stored events</summary>{timeline}</details> : timeline}
      </div>
      <aside className="evidence-inspector" aria-label="Selected evidence details">{details}</aside>
      <dialog ref={dialog} className="details-dialog" aria-label="Selected evidence details"><div className="dialog-actions"><button onClick={() => dialog.current?.close()} autoFocus><Icon name="close" size={16} />Close details</button></div>{details}</dialog>
    </div>
  </>;
}
