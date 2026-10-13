# Optional P11 — Evaluate the dossier's advanced methods

Use only after P10 or after an explicit schedule change. This preserves the accepted long-term technology vision without putting experimental methods on the critical path.

~~~text
Extend REWIND one method at a time. Read the research table in the roadmap.
Do not replace the working baseline or silently change the product.

For each proposed method:
1. State the exact decision it improves.
2. Choose a simple baseline.
3. Define a held-out benchmark and a promotion criterion before training.
4. Record data source, licence, split, leakage checks and compute budget.
5. Implement behind a feature flag.
6. Measure quality, uncertainty, latency and resource cost.
7. Promote only with evidence; retain fallback and model card.
8. Update experiments, decisions, risks and interview notes.

Suggested order:
A. n-gram/Markov vs small trajectory transformer. Compare detection and
false holds on separately held-out scenario families. Separate training,
run-level calibration and final testing.
B. Embedding-based drift. Measure whether it adds benefit over policy and
sequence features; do not assume statistical independence.
C. Injection classifier and graph prior. Compare candidate recall@k and
trials-to-supported-finding. Keep ranking separate from verdict.
D. Pair/group enumeration vs sampled Shapley. Define the coalition game,
baseline, marginal outcome and Monte Carlo uncertainty. Demonstrate
redundancy and interaction cases before scaling candidates.
E. Fixed-N vs a reviewed sequential test/confidence sequence. State the
hypotheses and stopping/error guarantees. Validate them in simulation
before enabling early stopping.
F. Trajectory retrieval encoder and changepoint methods only if they improve
a measured user task.
G. True Merkle inclusion proofs and externally anchored session seals if
needed; preserve explicit trust assumptions.
H. Broader MCP/OTel adapters with capture-completeness tests.

Do not train all models at once. Do not claim synthetic validation proves
enterprise performance. If a method fails to improve the baseline, record
the negative result and keep the simpler implementation.

Atlas, multi-organisation responsibility, insurer scores and certification
remain larger roadmap products. Implementing those is a new scope decision,
not an incidental extension of this task.
~~~

