# Actual P8 synthetic evidence examples

Byte-identical files from EXP-011, raw directory
artifacts/p8/EXP-011/20261014T201810043273Z/, 2026-10-15 Asia/Calcutta. Source
parent 709ff0d, dirty P8 implementation; complete source/artifact mapping is in
P8-ARTIFACTS.json. These are measured records, never live runtime fallback data.

- fixed_repeatability snapshot/trials: 32 actual returned simulator trials, 24
  valid and eight deliberate invalid argument controls across two isolated surfaces,
  two configurations and two deterministic repetitions. Historical maturity was
  implemented at measurement time, before the final verification promotion.
- time_limit snapshot: one started/incomplete, zero returned, 15 unstarted; no
  missing outcome counted harmless.
- failure-capture.json: actual encrypted-store export with the original signed
  source chain/seal and synthetic plaintext evidence for one failed owned trial.
- trusted-public.ed25519: public **demonstration key**. Selecting it is an explicit
  trust assumption, not independent external identity or automatic anchoring.

Verify the source with the existing capture verifier and this explicitly supplied
key; signed integrity is separate from trial validity, scope and truth. The
Preflight aggregate is not a signed Ledger record or safety/compliance certificate.
Screenshots show actual stored suite/failure states at the reviewed viewports.
No provider, secret, arbitrary-target attack or generated model variant is included.
