# Owned synthetic sandbox (P1)

The demo code is now packaged in `packages/rewind_sandbox` for coherent imports.
Its ticket/files/mail servers are owned stdio mocks; mail writes only a synthetic
local outbox. CLI: `.venv/Scripts/python.exe -m rewind_sandbox.cli run --scenario single`.
Host-local mocks do not establish replay network isolation.
