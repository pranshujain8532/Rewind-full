# Actual synthetic P5 review example

These files are byte-identical copies of actual EXP-004 outputs, not runtime demo
fixtures or invented presentation values. Source:
artifacts/p5/EXP-004/20261014T101549809036Z/. The original malicious comment is
unchanged; an owner-requested send was added before capture to test useful work.

- evidence.json: original signed trace, stored investigation trials and signed report.
- behavioural-behavioural-v1.json: fresh original-attack behavioural pass.
- containment-containment-v1.json: containment pass with one harmful attempt retained.
- containment-deny-all-v1.json: useful-task failure despite blocked dispatch.
- trusted-public.ed25519: public demonstration trust anchor; no private key included.

Choose this key explicitly only to verify this synthetic demonstration. Providing
a key alongside a bundle does not independently establish identity or make it trusted.
The CLI never accepts a bundled key automatically. No external anchoring, compliance,
real-model estimate, legal fault or exposed-person count is claimed.

```powershell
.venv/Scripts/python.exe -m rewind_ledger.cli verify --bundle docs/project/evidence/p5-example/evidence.json --trusted-public-key docs/project/evidence/p5-example/trusted-public.ed25519
.venv/Scripts/python.exe -m rewind_ledger.cli verify --bundle docs/project/evidence/p5-example/containment-containment-v1.json --trusted-public-key docs/project/evidence/p5-example/trusted-public.ed25519
```

The first command checks integrity/completeness and source regression eligibility.
The second checks the immutable fresh regression result and reports eligible=true
for that declared containment contract. The same containment configuration fails
a behavioural contract because its attempted behaviour remains.
