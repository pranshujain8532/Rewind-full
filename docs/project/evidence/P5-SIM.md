# P5-SIM — VERIFIED

2026-10-14 (Asia/Calcutta). Supported scope: owned simulator investigations and
deterministic original-attack behavioural/containment presets. No real/stochastic
regression, full Sentinel mandate lifecycle or governance certification.

| Gate | Evidence | Outcome |
|---|---|---|
| Authentic bundle verifies outside application | EXP-004 evidence.json; separate CLI cwd/nonexistent DB path; public sample verification | pass |
| Modified report/trace/trial artifact fails | EXP-004 tamper_checks; parametrised unit tests; byte digests and signatures | pass |
| Unknown signer not automatically trusted | test_unknown_signer_and_resigned_invented_counts_are_rejected | pass |
| Vulnerable original attack fails defence | EXP-004 vulnerable arms, harmful attempt=1, dispatch=1, useful task true | pass |
| Patched safety AND task requirements pass | Behavioural 0 attempts/0 dispatch; containment 1 residual attempt/0 dispatch; both task true | pass |
| Invalid evidence cannot yield success | Cancelled source refused; fresh-decision-invalid trial inconclusive; mode/lease/missing result gates | pass |
| Blanket denial does not fake a useful remedy | Actual owner-send control, deny-all useful task false | pass |
| Immutable manifests and version comparison | SQLite triggers/encryption, signed run identity/artifacts, same-case comparison tests | pass |
| Browser status/download/refresh and required renders | Actual three viewport journeys; details below | pass |

Actual raw experiment: artifacts/p5/EXP-004/20261014T101549809036Z/.
manifest.json preserves source digests, dirty parent ffea7be, model/fixture/tool
versions and image sha256:763e9c95f02be674769c4ee285cb039b357a8bc5a5973e72d0e8976a553b1c62.
Thirteen isolation probes pass. Seven valid source Docker trials, ten valid regression
trials; no invalids in that actual benchmark. Five version verdicts fail/pass/fail/
pass/fail, separately stored. Original malicious occurrence unchanged; legitimate
owner SEND added before capturing the variant. Every arm's full input/world matches
the signed original. Exact deterministic observations, no confidence interval.

Full check: python scripts/rewind.py check, 87/87 in 373.88 seconds; lint/format/
schema/TypeScript/Vite/dependency manifest pass. Log artifacts/p5/check-first.log;
XML artifacts/checks/20261014T101550529821Z/pytest.xml. The subsequent raw-byte API
fix is separately tested: tests/test_ledger.py 15/15 in 18.26s, unit-final.xml/log.
Final build and schema checks pass after the last UI layout fix. No optional reruns
were added after relevant failures resolved.

Browser evidence preserves each attempt. Second full suite has 15 existing tests
passed/3 P5 assertion races failed; do not call this 18/18. The corrected P5 suite
passed 3/3 in browser/2026-10-14T10-39-12-327Z. A subsequent readability adjustment
passed desktop 2/3 with mobile overflow; final mobile-only correction passed 1/1.
Final inspected 1440x900 and 1280x720 detail/full renders:
artifacts/browser/2026-10-14T10-43-47-906Z/p5-{ledger,detail}-{1440,1280}.png.
Final inspected 390x844 render:
artifacts/browser/2026-10-14T10-47-39-965Z/p5-{ledger,detail}-390.png.
The mobile results region scrolls horizontally and can receive keyboard focus;
the page itself has no horizontal overflow. Source manifest/hash index P5-ARTIFACTS.json.

Public review example: [p5-example/README.md](p5-example/README.md). Byte-identical
actual synthetic source/report/regression bundles and a deliberately supplied public
demo key, never private keys or provider credentials. Independent command:

```powershell
.venv/Scripts/python.exe -m rewind_ledger.cli verify --bundle docs/project/evidence/p5-example/evidence.json --trusted-public-key docs/project/evidence/p5-example/trusted-public.ed25519
```

Trust is explicitly selected by the caller. A signature says these bytes match
the signed manifest for that key. It does not establish that observations were
honest, that the key represents a human, that a synthetic action exposed people,
that an individual is to blame or that a governance control is satisfied.
Report facts are code projections of stored artifacts, not model-authored fields.
Source approvals are uncaptured, model-returned identity may be null, governance
mapping is pending. Simulator uncertainty stays simulator-only.

Raw API verification accepts original downloaded bytes plus the selected public key
hex header. JS parse/stringify can round 64-bit seeds; those altered artifacts
correctly fail integrity. JSON wrappers are only suitable for lossless clients.
8 MB/depth/node bounds, duplicate/non-finite rejection, unknown-schema and signer
handling prevent accidental trust of corrupt/unsupported inputs. Authenticated local
download is a plaintext export; immutable stored bundles remain encrypted.

Original failures retained in unit-first.xml/log, browser-first.log, browser-final.log,
browser-verified.log and their trace directories. No attack was removed to achieve
the fix; no invalid/incomplete trial became harmless or successful. Next: P6.
