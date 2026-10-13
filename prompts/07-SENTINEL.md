# P7 — Live policy gate and approvals

Prerequisites: recorder, UI and policy entities.

~~~text
Implement P7. Keep the Sentinel product mode, starting with rules that
we can test. Read the mandate/approval contract and negative tests.

Verify signed mandate, agent identity binding, validity period, tool/data/
recipient scope and budget before dispatch. Separate policy verdict from
enforcement decision. Explicit denial must never be overridden by a
normal approval click.

Implement held-action state, expiration, deny and deny-and-investigate.
Eligible approval binds to the exact arguments digest, session, mandate
version and authenticated approver, with expiry and one-time consumption.
Revalidate before dispatch and protect against races and duplicate requests.

The demo must show:
A. A forbidden export denied; investigation can follow.
B. An otherwise allowed high-impact action held for approval.
Do not invent an “Approve” path for a hard-denied action.

Connect the live Sentinel screen to real events and the relevant evidence.
Handle tool-call timeout honestly; record whether the agent can resume.

If time allows, add a small n-gram/Markov anomaly baseline. Do not block
core delivery on training. Label heuristic/synthetic-trained status.
Only add a transformer after a held-out comparison demonstrates benefit.
No universal FPR guarantee or assumed signal independence.

GATE:
- disallowed tool invocation never dispatches;
- expired/forged mandate fails closed;
- changed arguments, stale approvals and double submissions fail safely;
- eligible action dispatches at most once;
- timeout/cancel and deny-and-investigate are consistent;
- false holds are measured on benign cases if anomaly detection is claimed.

Update decisions, experiments and interview notes with actual trade-offs.
~~~

