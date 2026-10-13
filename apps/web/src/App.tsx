import { useCallback, useEffect, useRef, useState } from 'react';
import { readSystem } from './api';

type System = Awaited<ReturnType<typeof readSystem>>;
type State = { kind: 'loading' } | { kind: 'error'; message: string } | { kind: 'loaded'; data: System };

export function App() {
  const [state, setState] = useState<State>({ kind: 'loading' });
  const generation = useRef(0);
  const refresh = useCallback(async () => {
    const request = ++generation.current;
    setState({ kind: 'loading' });
    try {
      const data = await readSystem();
      if (request === generation.current) setState({ kind: 'loaded', data });
    } catch (error) {
      if (request === generation.current) setState({
        kind: 'error', message: error instanceof Error ? error.message : 'The API is unreachable.',
      });
    }
  }, []);
  useEffect(() => { void refresh(); return () => { generation.current++; }; }, [refresh]);

  return (
    <div className="app-frame">
      <aside className="sidebar" aria-label="Workspace">
        <a className="brand" href="/" aria-label="REWIND overview"><span aria-hidden="true">↶</span> REWIND</a>
        <p className="sidebar-caption">AGENT ACCOUNTABILITY</p>
        <nav aria-label="Main navigation"><a className="nav-active" href="/" aria-current="page"><span aria-hidden="true">◫</span> Overview</a></nav>
        <div className="sidebar-roadmap">
          <p className="eyebrow">THE WORKSPACE AHEAD</p>
          {['Forensics', 'Ledger', 'Sentinel', 'Preflight'].map(name => <div className="roadmap-item" key={name}><span>{name}</span><span className="tiny-label">Planned</span></div>)}
        </div>
        <div className="sidebar-footer"><span className="local-dot" aria-hidden="true" /><span>Local development<br /><small>Pranshu Jain · REWIND</small></span></div>
      </aside>
      <div className="workspace">
        <header className="topbar"><span>Workspace <span className="slash">/</span> <strong>System overview</strong></span><span className="badge">P0 · Foundation</span></header>
        <main id="main">
          <div className="page-heading"><div><p className="eyebrow">KNOW WHAT YOU CAN TRUST</p><h1>System overview</h1><p className="intro">One recorder. Four ways to understand and govern agent behaviour.</p></div><button aria-label="Refresh status" onClick={() => void refresh()} disabled={state.kind === 'loading'}>↻ <span>Refresh status</span></button></div>
          <div aria-live="polite" aria-atomic="true" className="status-announcement">{state.kind === 'loading' ? 'Checking backend readiness…' : state.kind === 'error' ? 'Backend unavailable' : state.data.health.ready ? 'API ready. Agent run modes are unavailable.' : 'API requires attention.'}</div>
          {state.kind === 'loading' && <section className="panel loading-panel"><span className="pulse-dot" aria-hidden="true" /><p>Reading system capabilities…</p></section>}
          {state.kind === 'error' && <section className="panel error-panel" role="alert"><h2>Backend unavailable</h2><p>{state.message}</p><p className="muted">Start the local API, then refresh to read its current capabilities.</p><code>python scripts/rewind.py dev</code></section>}
          {state.kind === 'loaded' && <SystemView data={state.data} />}
          <footer className="main-footer"><span>Evidence before conclusions.</span><span>Local, single-user development · No model calls in P0</span></footer>
        </main>
      </div>
    </div>
  );
}

function SystemView({ data }: { data: System }) {
  const { health, capabilities } = data;
  const recorder = capabilities.features.find(feature => feature.id === 'recorder');
  return <>
    <section className="readiness panel" aria-labelledby="readiness-title">
      <div><span className={`signal ${health.ready ? 'ready' : 'attention'}`} aria-hidden="true" /><div><h2 id="readiness-title">{health.ready ? 'Foundation is online' : 'Foundation needs attention'}</h2><p>{health.ready ? 'API and migrated storage are ready. Agent execution is not yet implemented.' : `Storage readiness: ${health.database.reason}. Run the migration command.`}</p></div></div>
      <span className={`badge ${health.ready ? 'success' : 'caution'}`}>{health.ready ? 'API ready' : 'Not ready'}</span>
    </section>
    <div className="content-grid">
      <div>
        <section className="panel evidence-panel" aria-labelledby="evidence-title">
          <div className="section-top"><p className="eyebrow">EVIDENCE WORKSPACE</p><span className="badge">Empty</span></div>
          <div className="empty-glyph" aria-hidden="true">↶</div><h2 id="evidence-title">Your first run starts here.</h2>
          <p>No agent runs have been recorded.<br />The next phase adds a synthetic support scenario and local tool sinks.</p>
          <div className="empty-action"><button disabled>Run demo scenario</button><span>Available after P1 · Sandbox</span></div>
        </section>
        <section className="feature-section" aria-labelledby="features-title"><div className="section-title"><h2 id="features-title">One evidence layer, four perspectives</h2><span>Planned capabilities</span></div><div className="feature-grid">{capabilities.features.filter(feature => feature.id !== 'recorder').map(feature => <article className="panel feature-card" key={feature.id}><div><h3>{feature.label}</h3><span className="tiny-label">{feature.maturity}</span></div><p>{feature.description}</p><p className="feature-reason">{feature.reason}</p></article>)}</div></section>
      </div>
      <aside className="details" aria-label="Backend capabilities">
        <section className="panel modes-panel"><p className="eyebrow">EXECUTION</p><h2>Run modes</h2><p className="muted">Availability reported by the API.</p>{capabilities.modes.map(mode => <div className="mode-row" key={mode.mode}><div className="mode-top"><h3>{mode.label}</h3><span className={mode.available ? 'available' : 'unavailable'}>{mode.available ? 'Available' : 'Unavailable'}</span></div><p>{mode.reason}</p><div className="mode-tags"><span>{mode.maturity}</span><span>Evidence: {mode.evidence_status}</span></div></div>)}</section>
        <section className="panel contract-panel"><p className="eyebrow">SYSTEM CONTRACT</p><dl><dt>API version</dt><dd>{health.version}</dd><dt>Schema</dt><dd>{health.schema_version}</dd><dt>Database</dt><dd>{health.database.journal_mode?.toUpperCase() ?? 'Unavailable'}</dd><dt>MCP SDK</dt><dd>{capabilities.mcp_sdk}</dd><dt>Protocol</dt><dd>{capabilities.mcp_protocol_revision}</dd><dt>Replay isolation</dt><dd>{capabilities.replay_isolation}</dd></dl><p>{recorder?.reason}</p></section>
      </aside>
    </div>
  </>;
}
