"""Frozen owned suites, immutable reservations/results and durable progress."""

from alembic import op

revision = "0007_preflight"
down_revision = "0006_sentinel"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""CREATE TABLE preflight_runs (
        id TEXT PRIMARY KEY, idempotency_key TEXT NOT NULL UNIQUE,
        request_digest TEXT NOT NULL, plan TEXT NOT NULL, plan_digest TEXT NOT NULL,
        status TEXT NOT NULL, reason TEXT, created_at TEXT NOT NULL,
        started_at REAL, ended_at REAL, worker_id TEXT, lease_until REAL,
        cancel_requested INTEGER NOT NULL DEFAULT 0
    )""")
    op.execute("""CREATE TABLE preflight_trials (
        run_id TEXT NOT NULL REFERENCES preflight_runs(id), ordinal INTEGER NOT NULL,
        spec TEXT NOT NULL, session_id TEXT NOT NULL, result TEXT,
        investigation_id TEXT, PRIMARY KEY(run_id,ordinal), UNIQUE(session_id)
    )""")
    op.execute("""CREATE TABLE preflight_events (
        run_id TEXT NOT NULL REFERENCES preflight_runs(id), seq INTEGER NOT NULL,
        body TEXT NOT NULL, PRIMARY KEY(run_id,seq)
    )""")
    for operation in ("UPDATE", "DELETE"):
        op.execute(f"""CREATE TRIGGER preflight_events_no_{operation.lower()}
            BEFORE {operation} ON preflight_events
            BEGIN SELECT RAISE(ABORT,'immutable Preflight event'); END""")
    op.execute("""CREATE TRIGGER preflight_plan_frozen
        BEFORE UPDATE OF plan,plan_digest ON preflight_runs
        BEGIN SELECT RAISE(ABORT,'frozen Preflight plan'); END""")
    op.execute("""CREATE TRIGGER preflight_spec_frozen
        BEFORE UPDATE OF spec,session_id ON preflight_trials
        BEGIN SELECT RAISE(ABORT,'frozen Preflight reservation'); END""")
    op.execute("""CREATE TRIGGER preflight_result_frozen BEFORE UPDATE OF result ON preflight_trials
        WHEN OLD.result IS NOT NULL BEGIN SELECT RAISE(ABORT,'immutable Preflight result'); END""")
    op.execute("""CREATE TRIGGER preflight_trial_retained BEFORE DELETE ON preflight_trials
        BEGIN SELECT RAISE(ABORT,'retained Preflight trial'); END""")


def downgrade():
    for table in ("preflight_events", "preflight_trials", "preflight_runs"):
        op.drop_table(table)
