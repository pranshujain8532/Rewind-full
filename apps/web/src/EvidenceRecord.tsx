import { useState } from 'react';
import type { components } from './generated/api';
import type { EvidenceRecord as Record, SessionDetail } from './api';
import { useResource } from './state';
import { Badge, CopyIdentifier, CoverageBadge, EffectEstimate, ErrorState, EvidenceStatus, Icon, IntegrityStatus, Loading, ModeBadge } from './ui/evidence';
import { Card, CardHeader, CardTitle, CardContent } from './ui/primitives';

type Verification = components['schemas']['VerificationResult'];
export function EvidenceRecord({ id }: { id: string }) {
  const query = useResource<Record>(`/api/records/${id}`);
  const record = query.data;
  const captureVerification = record?.capture_coverage.verification as { capture_complete?: boolean } | undefined;
  const session = useResource<SessionDetail>(record ? `/api/sessions/${record.session_id}` : null);
  const [publicKey, setPublicKey] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [verification, setVerification] = useState<Verification | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  async function verify() {
    setBusy(true); setError(''); setVerification(null);
    try {
      let bytes: ArrayBuffer;
      if (file) { if (file.size > 8_000_000) throw new Error('Bundle exceeds the 8 MB input limit.'); bytes = await file.arrayBuffer(); }
      else {
        const response = await fetch(`/api/records/${id}/download`);
        if (!response.ok) throw new Error(`Download unavailable (${response.status}).`);
        bytes = await response.arrayBuffer();
        if (bytes.byteLength > 8_000_000) throw new Error('Bundle exceeds the 8 MB input limit.');
      }
      // Preserve original UTF-8 bytes: parse/stringify would round 64-bit seeds.
      const response = await fetch('/api/records/verify', { method: 'POST', body: bytes, headers: { 'Content-Type': 'application/json', 'X-REWIND-Local': '1', 'X-REWIND-Trusted-Public-Key': publicKey.trim() }, signal: AbortSignal.timeout(45000) });
      if (!response.ok) throw new Error(`Verification refused (${response.status}): ${(await response.text()).slice(0, 250)}`);
      setVerification(await response.json() as Verification);
    } catch (e) { setError(String(e)); } finally { setBusy(false); }
  }
  if (!record) return query.error ? <ErrorState message={query.error} retry={() => void query.refresh()} /> : <Loading />;
  return <div className="ledger-panel">
    <div className="page-heading"><div><p className="eyebrow">LEDGER / PORTABLE EVIDENCE</p><h1>Evidence record</h1><p className="intro">Stored facts. A verifiable seal. Explicit limits.</p></div><div className="heading-actions"><a className="button primary" href={`/api/records/${id}/download`} download><Icon name="download" size={16} />Download signed evidence bundle</a><a className="button" href={`/regressions?record=${id}`}><Icon name="regression" size={16} />Create regression</a></div></div>
    <div className="evidence-badges"><ModeBadge mode={record.mode} /><EvidenceStatus status={record.evidence_status} /><CoverageBadge complete={captureVerification?.capture_complete === true} /><Badge>Replay: {record.replay_coverage.complete === true ? 'complete' : 'incomplete / unsupported'}</Badge><Badge>Trace: {session.data ? String(session.data.integrity.status).replaceAll('_', ' ') : 'not checked'}</Badge><IntegrityStatus status={verification && !file ? verification.integrity_valid ? 'record verified under supplied key' : 'record verification failed' : 'record not independently checked'} /></div>
    {query.error && <ErrorState message={query.error} stale retry={() => void query.refresh()} />}
    <div className="ledger-grid"><Card><CardHeader><CardTitle>Record & source bindings</CardTitle><CopyIdentifier value={id} label="Copy record identifier" /></CardHeader><CardContent><dl><dt>Captured session</dt><dd><a href={`/sessions/${record.session_id}`}>{record.session_id}</a></dd><dt>Investigation</dt><dd><a href={`/investigations/${record.investigation_id}`}>{record.investigation_id}</a></dd><dt>Created</dt><dd>{new Date(record.created_at).toLocaleString()}</dd>{Object.entries(record.provenance).map(([key, value]) => <div key={key}><dt>{key.replaceAll('_', ' ')}</dt><dd className={key.includes('digest') ? 'mono' : ''}>{value === null ? 'Unknown / not captured' : String(value)}</dd></div>)}</dl><details><summary>Session seal</summary><pre>{JSON.stringify(record.session_seal, null, 2)}</pre></details></CardContent></Card>
    <Card><CardHeader><div><CardTitle>Verify against a trusted key</CardTitle><p className="muted">Choose a key independently; a bundled key is not a trust anchor.</p></div><Icon name="shield" /></CardHeader><CardContent><label>Trusted public key (64 hexadecimal characters)<input value={publicKey} onChange={e => { setPublicKey(e.target.value); setVerification(null); }} maxLength={64} spellCheck={false} autoComplete="off" className="mono" placeholder="Paste your independently trusted public key" /></label><label>Bundle to verify (optional)<input type="file" accept=".json,application/json" onChange={e => { setFile(e.target.files?.[0] ?? null); setVerification(null); }} /></label><p className="muted">{file ? `Selected ${file.name}. Verification applies to this file, which may differ from the displayed record.` : 'Verifies the original bytes of this downloaded record.'} Maximum 8 MB.</p><button className="primary" onClick={() => void verify()} disabled={busy || !/^[a-fA-F0-9]{64}$/.test(publicKey.trim())} aria-describedby="key-reason"><Icon name="shield" size={16} />{busy ? 'Checking integrity…' : 'Verify bundle'}</button><p id="key-reason" className="muted">Supply a 32-byte Ed25519 public key to enable verification.</p>{error && <ErrorState message={error} />}{verification && <div className={`verification-result ${verification.integrity_valid ? 'success' : 'caution'}`} role="status"><strong>{verification.integrity_valid ? 'Integrity verified under supplied key' : 'Integrity verification failed'}</strong><p>{verification.reason}. Trusted signer: {String(verification.trusted)}. Evidence complete: {String(verification.evidence_complete)}. Regression eligible: {String(verification.regression_eligible)}.</p></div>}<p className="trust-note">Signing proves that these bytes match a signer under your trust assumption. It does not prove the capture is true, complete, compliant or attributable to an individual.</p></CardContent></Card></div>
    {record.findings.map(finding => <EffectEstimate key={finding.arm} finding={finding} />)}
    <Card><CardHeader><CardTitle>Actual stored counts</CardTitle><Badge>Backend projections</Badge></CardHeader><CardContent><div className="table-scroll" role="region" tabIndex={0} aria-label="Record counts"><table><caption>Stored trial counts by condition</caption><thead><tr><th>Condition</th><th>Started</th><th>Valid</th><th>Invalid</th><th>Incomplete</th><th>Harmful attempts</th><th>Harmful dispatch</th><th>Useful task</th></tr></thead><tbody>{Object.entries(record.counts).map(([arm, counts]) => <tr key={arm}><td>{arm}</td>{(['started', 'valid', 'invalid', 'incomplete', 'harmful', 'dispatched', 'task_success'] as const).map(field => <td key={field}>{counts[field]}</td>)}</tr>)}</tbody></table></div></CardContent></Card>
    <Card><CardHeader><CardTitle>Coverage, impact & limitations</CardTitle></CardHeader><CardContent><div className="coverage-grid"><section><h3>Capture coverage</h3><pre>{JSON.stringify(record.capture_coverage, null, 2)}</pre></section><section><h3>Replay coverage</h3><pre>{JSON.stringify(record.replay_coverage, null, 2)}</pre></section></div><details><summary>Observed synthetic impact and policy trail</summary><pre>{JSON.stringify({ impact: record.observed_synthetic_impact, policy_approval_trail: record.policy_approval_trail }, null, 2)}</pre></details><p>Governance mapping pending. No exact external control was read and recorded; no certificate or compliance percentage is claimed.</p><ul>{record.limitations.map(limit => <li key={limit}>{limit}</li>)}</ul></CardContent></Card>
  </div>;
}
