# P8 — Pre-deployment defensive evaluation

Prerequisites: isolated runtime, predicates, evaluation engine and UI.

~~~text
Implement P8, preserving Preflight as the accepted fourth product mode.

Build a bounded test suite against only our owned synthetic sandbox.
Start with fixed, reviewed scenarios across ticket comments and one
additional supported surface such as tool descriptions or mock file text.
Use explicit target identifiers and deny arbitrary external target URLs.

Each trial records fixture version, insertion surface, model/configuration,
attempted harmful action, policy block, executed mock action, task success,
validity and resource cost. The attack-surface table must show real
numerators and denominators, not a decorative risk percentage.

Separate unsafe intent/attempt from actual sandbox dispatch and from
guardrail detection. If no guardrail classifier exists, say “not measured”
instead of reporting an evasion rate.

Optional after fixed-suite validation: add small budgeted LLM variations
to the owned synthetic scenarios, with constraints and logged lineage.
Label these exploratory tests. Do not add arbitrary-target attack tooling,
credential discovery or outbound action capability.

GATE:
- two supported surfaces run inside the isolated environment;
- trials are repeatable by fixture/configuration version;
- cost and iteration limits stop jobs cleanly;
- invalid trials remain visible in denominators/coverage;
- clicking a failure opens its recorded session and investigation;
- offline fixed-suite mode works without a provider.

Update the feature maturity table. Evolutionary generation is complete
only if implemented, bounded and tested; otherwise retain it as a
documented extension.
~~~

