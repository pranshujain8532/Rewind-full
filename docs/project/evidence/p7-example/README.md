# Actual P7 synthetic audit examples

Byte-identical exports from EXP-010, 2026-10-15 Asia/Calcutta, raw directory
`artifacts/p7/EXP-010/20261014T192818971254Z/`. Parent 373a0e8, dirty P7 source;
exact source digests and full retained evidence are indexed in P7-ARTIFACTS.json.
No provider call, cached model response or invented presentation result is included.

`approve_with_forbidden_export_denied.json`: nine signed events, one protected
approved owner send, two synthetic row instances, forbidden export denied and
source investigation linked. `deadline.json`: held owner send expires with explicit
policy_tool_timeout and agent_can_resume=false; forbidden export remains denied.
The full observation-only source capture is retained in the raw directory; these
policy sidecars do not bundle its Forensics trials or certify source truth.

`trusted-public.ed25519` is a **demonstration public key**, not automatic trust.
Select it explicitly only if accepting that demonstration assumption:

```powershell
.venv/Scripts/python.exe -m rewind_core.sentinel.verify docs/project/evidence/p7-example/approve_with_forbidden_export_denied.json --trusted-public-key docs/project/evidence/p7-example/trusted-public.ed25519
```

Authenticity does not establish real identity, legal fault, compliance, LLM safety
or arbitrary production tool delivery. Screenshots show actual stored simulator
states; they are review artifacts and never runtime fallback measurements.
