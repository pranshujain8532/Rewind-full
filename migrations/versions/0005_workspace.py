"""Persist regression progress without changing signed evidence or trials."""

from alembic import op

revision = "0005_workspace"
down_revision = "0004_ledger"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE TABLE regression_events (
            run_id TEXT NOT NULL REFERENCES regression_runs(id),
            seq INTEGER NOT NULL,
            body TEXT NOT NULL,
            PRIMARY KEY(run_id,seq)
        )
    """)
    for operation in ("UPDATE", "DELETE"):
        op.execute(f"""
            CREATE TRIGGER regression_events_no_{operation.lower()}
            BEFORE {operation} ON regression_events
            BEGIN SELECT RAISE(ABORT,'immutable progress event'); END
        """)


def downgrade():
    op.drop_table("regression_events")
