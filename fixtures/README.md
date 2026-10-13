# Versioned fixtures (P1)

Scenario inputs and recorded outputs belong here. Evaluator ground truth must
stay separate from subject-agent inputs and future ranking data.
P1 has six generated `scenarios/*.json`, a version/digest manifest and separate
`evaluation/expectations.json`. Agent loading never reads evaluator metadata.
Regenerate with `.venv/Scripts/python.exe -m rewind_sandbox.cli generate`.
Playback explicitly reads an actual saved run result; it adds no trial evidence.
