# P2 — Record and verify evidence

Prerequisite: P1 gate.

~~~text
Implement REWIND P2 under AGENTS.md. Read architecture sections 5–7 and
the recorder/integrity tests in 06-VERIFICATION.md.

Build the stdio MCP recorder for our pinned revision. Preserve protocol
IDs, notifications, errors, cancellation and call correlation. Launch
subprocesses with argv, write diagnostics to stderr, and enforce size/time
limits. Support only the primitives we actually test and disclose others.

Add the model/agent adapter to capture supported model input envelopes,
tool schemas, task/memory state and configuration. Record context occurrence
IDs, not just deduplicated content hashes. Show tool-only recording as
partial capture rather than pretending full replay coverage.

Implement migrations, immutable events, per-session ordering, content
storage, encrypted payloads, redacted display views, standard Ed25519
signatures and a signed linked hash chain with a session seal.
Use the documented canonical form. This is not a Merkle tree.

Build a trusted-key CLI verifier. A public key inside an untrusted bundle
alone is not a trusted identity. Handle missing payloads explicitly.

GATE:
- agent -> proxy -> mock server produces a complete supported trace;
- identical content in different locations preserves distinct origins;
- full adapter capture passes readiness fields; tool-only capture is partial;
- edits, reordered/deleted events, altered blobs and wrong signers are caught;
- no protocol contamination on stdout and no secrets in ordinary logs.

Persist evidence from actual runs and mutation tests. Update STATE, TASKS,
DECISIONS, SESSION-LOG, HANDOFF and relevant interview notes.
Explain content hash versus occurrence ID and what a signature proves.
~~~

