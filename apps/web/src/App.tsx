import { useEffect, useRef, useState } from 'react';
import { readSystem } from './api';
import { useResource, useRoute } from './state';
import { Investigation } from './Investigation';
import { EvidenceRecord } from './EvidenceRecord';
import { Regressions } from './Regressions';
import { Sentinel } from './Sentinel';
import { Overview, SessionList, SessionPage, InvestigationList, RecordList, Settings, UnavailableScreen } from './pages';
import { Badge, EmptyState, ErrorState, Icon, Loading, PermissionState } from './ui/evidence';
import { Card } from './ui/primitives';

const navigation = [
  { path: '/overview', label: 'Overview', icon: 'overview' },
  { path: '/sessions', label: 'Sessions', icon: 'sessions' },
  { path: '/investigations', label: 'Investigations', icon: 'graph' },
  { path: '/ledger', label: 'Ledger', icon: 'ledger' },
  { path: '/regressions', label: 'Regressions', icon: 'regression' },
  { path: '/sentinel', label: 'Sentinel', icon: 'shield' },
  { path: '/preflight', label: 'Preflight', icon: 'play' },
];

export function App() {
  const { route, go } = useRoute();
  const path = route.split('?')[0];
  const system = useResource('/api/system', readSystem);
  const main = useRef<HTMLElement>(null);
  const jump = useRef<HTMLDialogElement>(null);
  const [online, setOnline] = useState(navigator.onLine);
  const [search, setSearch] = useState('');
  useEffect(() => {
    const update = () => setOnline(navigator.onLine);
    const key = (e: KeyboardEvent) => { if ((e.metaKey || e.ctrlKey) && e.key === 'k') { e.preventDefault(); jump.current?.showModal(); } };
    window.addEventListener('online', update); window.addEventListener('offline', update); window.addEventListener('keydown', key);
    return () => { window.removeEventListener('online', update); window.removeEventListener('offline', update); window.removeEventListener('keydown', key); };
  }, []);
  const previousPath = useRef(path);
  useEffect(() => { if (previousPath.current !== path) { main.current?.focus(); window.scrollTo({ top: 0, behavior: 'instant' }); previousPath.current = path; } }, [path]);
  const current = path === '/' ? navigation[0] : navigation.find(item => path.startsWith(item.path));
  const title = current?.label ?? (path === '/settings' ? 'Settings' : 'Workspace');
  const capabilities = system.data?.capabilities;
  const screen = !system.data ? system.error ? <Card><EmptyState title="Backend unavailable" action={<button onClick={() => void system.refresh()}>Refresh status</button>}>Start the local API to read stored facts. {system.error}</EmptyState></Card> : <Loading />
    : !system.data.health.ready ? <PermissionState title="Storage needs attention" reason={`Readiness: ${system.data.health.database.reason}. Run the additive migrations before using evidence.`} />
    : path === '/' || path === '/overview' ? <Overview go={go} system={system.data} />
    : path === '/sessions' ? <SessionList />
    : path.startsWith('/sessions/') ? <SessionPage id={path.split('/')[2]} go={go} capabilities={capabilities!} />
    : path === '/investigations' ? <InvestigationList />
    : path.startsWith('/investigations/') ? <Investigation key={path} id={path.split('/')[2]} go={go} />
    : path === '/ledger' ? <RecordList />
    : path.startsWith('/ledger/') ? <EvidenceRecord key={path} id={path.split('/')[2]} />
    : path === '/regressions' ? <Regressions key={route} go={go} />
    : path === '/settings' ? <Settings system={system.data} />
    : path === '/sentinel' ? <Sentinel key={route} id={new URLSearchParams(route.split('?')[1]).get('id')} go={go} />
    : path === '/preflight' ? <UnavailableScreen id="preflight" capabilities={capabilities!} />
    : <EmptyState title="This route is unavailable" action={<a className="button" href="/overview">Return to overview</a>}>No evidence was loaded for this address.</EmptyState>;
  return <div className="app-frame">
    <a href="#main" className="skip-link">Skip to evidence workspace</a>
    <aside className="sidebar" aria-label="Workspace">
      <a className="brand" href="/overview" aria-label="REWIND overview"><span className="brand-mark"><Icon name="rewind" size={25} /></span><span>REWIND<small>Evidence before conclusions</small></span></a>
      <button className="jump-button" onClick={() => jump.current?.showModal()}><Icon name="sessions" size={16} />Jump to a workspace<span className="keycap">⌘ K</span></button>
      <button className="mobile-menu-toggle" aria-label="Open navigation" onClick={() => { setSearch(''); jump.current?.showModal(); }}><Icon name="overview" size={18} />Menu</button><p className="sidebar-caption">INVESTIGATION WORKSPACE</p>
      <nav aria-label="Main navigation">{navigation.map(item => <a key={item.path} href={item.path} className={current?.path === item.path ? 'nav-active' : ''} aria-current={current?.path === item.path ? 'page' : undefined}><Icon name={item.icon} size={19} /><span>{item.label}</span>{item.path === '/preflight' && <small>Planned</small>}</a>)}</nav>
      <div className="sidebar-note"><Icon name="shield" size={18} /><p>A signed record preserves bytes.<br />A test supports a scoped finding.</p></div>
      <div className="sidebar-footer"><a href="/settings" aria-current={path === '/settings' ? 'page' : undefined}><span className="avatar">PJ</span><span>Pranshu Jain<small>Local workspace · settings</small></span><Icon name="settings" size={17} /></a></div>
    </aside>
    <div className="workspace"><header className="topbar"><span className="breadcrumb">Workspace <span>/</span> <strong>{title}</strong></span><div><span className={`connection-dot ${online ? '' : 'offline'}`} /><span>{online ? system.error ? 'Connection unavailable' : 'Local workspace' : 'Offline · data may be stale'}</span><button className="icon-button" aria-label="Refresh status" onClick={() => void system.refresh()}><Icon name="refresh" size={17} /></button></div></header>
    <main id="main" tabIndex={-1} ref={main}>{system.data && system.error && <ErrorState message={system.error} stale retry={() => void system.refresh()} />}{screen}<footer className="main-footer"><span>Evidence before conclusions.</span><span>REWIND · owned sandbox · no external tool dispatch</span></footer></main></div>
    <dialog ref={jump} className="jump-dialog" aria-label="Jump to workspace"><div className="dialog-actions"><label>Find a workspace<input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search sessions, investigations, Ledger…" autoFocus /></label><button className="icon-button" aria-label="Close navigation" onClick={() => jump.current?.close()}><Icon name="close" /></button></div><nav aria-label="Workspace shortcuts">{[...navigation, { path: '/settings', label: 'Settings', icon: 'settings' }].filter(item => item.label.toLowerCase().includes(search.toLowerCase())).map(item => <a key={item.path} href={item.path} onClick={() => jump.current?.close()}><Icon name={item.icon} />{item.label}<Icon name="arrow" size={16} /></a>)}</nav></dialog>
  </div>;
}
