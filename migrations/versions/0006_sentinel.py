"""Add signed policy audit, exact approvals and atomic owned mock dispatches."""

from alembic import op

revision = "0006_sentinel"
down_revision = "0005_workspace"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""CREATE TABLE sentinel_sessions (
        id TEXT PRIMARY KEY, source_session_id TEXT NOT NULL REFERENCES sessions(id),
        agent_id TEXT NOT NULL, mandate_version TEXT NOT NULL,
        world BLOB NOT NULL, world_digest TEXT NOT NULL, summary TEXT NOT NULL,
        idempotency_key TEXT NOT NULL UNIQUE, request_digest TEXT NOT NULL
    )""")
    op.execute("""CREATE TABLE sentinel_mandates (
        version TEXT PRIMARY KEY, body TEXT NOT NULL
    )""")
    op.execute("""CREATE TABLE sentinel_actions (
        id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sentinel_sessions(id),
        mandate_version TEXT NOT NULL, action BLOB NOT NULL,
        action_digest TEXT NOT NULL, args_digest TEXT NOT NULL,
        verdict TEXT NOT NULL, enforcement TEXT NOT NULL, state TEXT NOT NULL,
        reason TEXT NOT NULL, deadline REAL NOT NULL, agent_can_resume INTEGER NOT NULL,
        investigation_requested INTEGER NOT NULL DEFAULT 0,
        investigation_id TEXT, investigation_error TEXT,
        UNIQUE(session_id, action_digest)
    )""")
    op.execute("""CREATE TABLE sentinel_approvals (
        action_id TEXT PRIMARY KEY REFERENCES sentinel_actions(id),
        body TEXT NOT NULL, consumed_at REAL NOT NULL
    )""")
    op.execute("""CREATE TABLE sentinel_dispatches (
        action_id TEXT PRIMARY KEY REFERENCES sentinel_actions(id),
        session_id TEXT NOT NULL REFERENCES sentinel_sessions(id),
        export_rows INTEGER NOT NULL, result BLOB NOT NULL
    )""")
    op.execute("""CREATE TABLE sentinel_receipts (
        key TEXT PRIMARY KEY, request_digest TEXT NOT NULL, action_id TEXT NOT NULL
    )""")
    op.execute("""CREATE TABLE sentinel_events (
        session_id TEXT NOT NULL REFERENCES sentinel_sessions(id), seq INTEGER NOT NULL,
        body TEXT NOT NULL, event_hash TEXT NOT NULL, signature TEXT NOT NULL,
        PRIMARY KEY(session_id, seq)
    )""")
    for table in (
        "sentinel_mandates",
        "sentinel_approvals",
        "sentinel_dispatches",
        "sentinel_events",
    ):
        for operation in ("UPDATE", "DELETE"):
            op.execute(f"""CREATE TRIGGER {table}_no_{operation.lower()}
                BEFORE {operation} ON {table}
                BEGIN SELECT RAISE(ABORT,'immutable Sentinel evidence'); END""")


def downgrade():
    for table in (
        "sentinel_events",
        "sentinel_receipts",
        "sentinel_dispatches",
        "sentinel_approvals",
        "sentinel_actions",
        "sentinel_mandates",
        "sentinel_sessions",
    ):
        op.drop_table(table)
