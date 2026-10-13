# P3 — Make interventions actually change decisions

Prerequisite: P2 gate. This is the critical technical gate.

~~~text
Implement P3. Read the complete replay contract and its negative tests.
Build this carefully before adding a causal verdict or elaborate animation.

Implement PLAYBACK separately from SIMULATED and fresh LOCAL_MODEL /
REMOTE_MODEL re-execution. Never use a cached model response after its
input changed. Capture the actual transformed request and fresh response.

For the supported sandbox agent, clone initial tool state and memory per
trial, apply occurrence-specific interventions at the input insertion point,
and rerun the downstream decision process. Start from the full task snapshot
before trying prefix optimisation.

Implement strict recorded response matching with tool/schema, arguments,
occurrence and environment state. Unknown branches become unsupported.
Also support versioned pure mock tools for sandbox re-execution; label that
environment correctly. External writes always go to isolated local sinks.

Implement a non-root, resource-limited, no-network worker with only declared
mounts. A normal subprocess is not network isolation. For hosted inference,
use the architecture's narrow IPC broker: only the model provider is
reachable by the broker; the worker cannot call arbitrary network tools.
Explicitly label this network exception.

Add a compatible real-model adapter using an available local model or
configured provider. Do not buy services or conceal unavailable access.
If real inference is blocked, complete and verify the simulator and
playback paths, mark the real-model gate blocked, and preserve an actionable
setup note. Do not declare real-model re-execution complete.

GATE:
- removal and neutral replacement visibly reach fresh decision inputs;
- repeated same-argument calls use the correct state/occurrence;
- unknown strict-replay paths fail honestly;
- trial state does not leak between runs;
- DNS/TCP, host-secret and path-traversal negative tests establish the boundary;
- safety outcome and useful-task outcome are separate;
- actual model requests are evidenced for every claimed real-model trial.

Record measured variability; do not call provider output deterministic by
assumption. Update all context files and explain why playback cannot prove
the effect of an intervention.
~~~

