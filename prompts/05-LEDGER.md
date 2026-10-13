# P5 — Evidence record and permanent regression

Prerequisite: P4 gate.

~~~text
Implement P5 under AGENTS.md. Read architecture sections 6, 11 and 12.

Create a versioned evidence record from stored trace and trial facts:
session seal, model/configuration/fixture digests, capture and replay
coverage, mode, candidate scope, actual counts, interval method/level,
policy/approval trail, observed synthetic impact and explicit limitations.
Do not use a generative model to invent any field.

Sign the record and provide a downloadable bundle and independent CLI
verification against a trusted public key. Bound input sizes and handle
corrupt, incomplete, unknown-schema and untrusted-signer bundles.

Create a regression from the ORIGINAL unmodified attack. Run it against
the vulnerable configuration and a documented fixed agent/mandate
configuration. Declare a behavioural or containment regression contract.
A behavioural fix reduces attempted harmful actions; a containment fix
blocks dispatch even if attempts remain. Assert the chosen safety outcome
and legitimate task completion, and show residual attempts. Do not “fix” the regression by removing the attack.

Provide a CLI and API for regression runs, immutable result manifests,
version comparison and honest pass/fail/inconclusive status.
For governance, use a small evidence mapping only where the exact source
control was read and recorded. Otherwise mark mapping pending; do not
invent clause IDs, compliance percentages or certificates.

GATE:
- authentic bundle verifies outside the main application;
- modified report, trace or trial artifact fails integrity checks;
- unknown signer is not trusted automatically;
- vulnerable original-attack test fails the defence requirement;
- patched original-attack test passes its declared safety AND task requirements;
- invalid evidence cannot yield a successful regression status.

Update context and explain why signing proves integrity under a trust
assumption rather than proving truth or individual blame.
~~~

