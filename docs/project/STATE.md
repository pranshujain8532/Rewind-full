# Current project state

Updated 2026-10-13 (Asia/Calcutta). P2 VERIFIED; P3 next in authorised P1–P10 run.

## Working

- P0 API/web/locked setup and P1 six synthetic scenarios/owned stdio mocks.
- Byte-preserving, bounded stdio recorder for MCP 2.3.0 / 2026-07-28, verified
  request/reply correlation, concurrency, tool errors and cancellation.
- Simulator adapter captures actual request/response, initial world, stateless
  memory, framework tool definitions and model/config digests; no response cache.
- SQLite migration 0002_capture; transaction-allocated ordered immutable events,
  AES-256-GCM content-addressed payloads, redacted display data, Ed25519 chain/seal.
- Trusted-key CLI verifier detects mutation/provenance changes and missing payloads.
- Duplicate text deduplicates bytes but retains distinct signed occurrence origins.
- Captured CLI demo exports result and bundle; API reports actual stored-session count.

## Modes and limits

Simulator: verified owned host mocks; deterministic fixture evidence only.
Playback: explicit recording read, no fresh inference or statistical use.
Local/remote models unavailable; no configured model/provider/budget or fallback.
P3 isolation still unimplemented/unverified; Docker engine available, base image not yet cached.
Resources/prompts/HTTP MCP, unproxied calls and arbitrary agent frameworks unsupported.
Signatures prove trusted-key bytes relative to seal, not truth/legal fault or external anchoring.
Payload encryption applies to the evidence store; development fixtures/artifacts are synthetic.
No production/private-data deployment or key-custody guarantee is claimed.

## Commands

```powershell
python scripts/rewind.py setup
python scripts/rewind.py check
python scripts/rewind.py demo
.venv/Scripts/python.exe -m rewind_capture.cli export --session SESSION_UUID --bundle bundle.json
.venv/Scripts/python.exe -m rewind_capture.cli verify --bundle bundle.json --trusted-key data/keys/trusted-public.ed25519
python scripts/rewind.py dev
```

Demo runs actual agent→proxy→mock tools and saves a signed synthetic capture;
all attempted sends terminate in a local outbox. Trusted public key comes from
the separately pinned local key, never an untrusted bundle's embedded key.

## Verification / next

Full gate check: 32/32; P2 integrity/correlation suite 13/13 plus frame/lifetime
bound test; envelope/partial-capture follow-up 2/2; trusted CLI verification valid.
Browser 4/4, target renders inspected; evidence/P2.md and artifacts/p2/*.
Checkpoint parent 40a1399; local phase commits, no push. Continue prompts/03-REPLAY.md.
P3 real-model path may remain blocked; continue independent simulator/playback work.
