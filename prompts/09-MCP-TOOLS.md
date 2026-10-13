# P9 — Expose REWIND through MCP

Prerequisites: typed API services and tested evidence operations.

~~~text
Implement P9 with the pinned official MCP SDK and supported revision.
Expose REWIND's existing domain services, not duplicate business logic.

Start with read tools:
rewind_list_incidents, rewind_explain_step, rewind_get_record,
rewind_regression_suite and rewind_attack_surface.
Add rewind_investigate only with authentication, authorisation, budget
validation and an asynchronous job handle. Names must comply with the
selected SDK/protocol's actual constraints.

Expose evidence resources where the pinned implementation supports them.
Sanitise sensitive fields by role. A read caller cannot approve an action,
read keys or launch an unrestricted replay.

Test with a real SDK client and record the protocol version and supported
transport. Start with stdio. Implement Streamable HTTP only if time allows
and version-specific lifecycle/security tests pass. Do not assume older
initialisation or SSE semantics apply to a newer revision.

If demonstrating self-recording, prevent recursive invocation loops using
a clear service boundary and correlation marker. Do not claim that
self-recording makes REWIND independently trusted.

GATE:
- external local client can query a real stored incident and record;
- authorised investigation returns a job handle and final evidence;
- unauthorised actions and excessive budgets are rejected;
- protocol errors and unsupported capabilities are explicit;
- no secrets leak through tool results or stdout diagnostics.

Update integration coverage and give a small working client example.
~~~

