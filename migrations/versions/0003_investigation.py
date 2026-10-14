"""Durable bounded jobs, immutable trial manifests and application progress events."""

import sqlalchemy as sa
from alembic import op

revision = "0003_investigation"
down_revision = "0002_capture"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "demo_starts",
        sa.Column("idempotency_key", sa.String(), primary_key=True),
        sa.Column("request_digest", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
    )
    op.create_table(
        "investigations",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("session_id", sa.String(), sa.ForeignKey("sessions.id"), nullable=False),
        sa.Column("idempotency_key", sa.String(), unique=True, nullable=False),
        sa.Column("request_digest", sa.String(), nullable=False),
        sa.Column("request", sa.Text(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("reason", sa.String()),
        sa.Column("created_at", sa.String(), nullable=False),
        sa.Column("started_at", sa.Float()),
        sa.Column("heartbeat_at", sa.String()),
        sa.Column("lease_until", sa.Float()),
        sa.Column("worker_id", sa.String()),
        sa.Column("cancel_requested", sa.Boolean(), nullable=False),
        sa.Column("plan", sa.Text()),
        sa.Column("plan_digest", sa.String()),
        sa.Column("graph", sa.Text(), nullable=False),
    )
    op.create_table(
        "investigation_trials",
        sa.Column("job_id", sa.String(), sa.ForeignKey("investigations.id"), primary_key=True),
        sa.Column("ordinal", sa.Integer(), primary_key=True),
        sa.Column("phase", sa.String(), nullable=False),
        sa.Column("arm", sa.String(), nullable=False),
        sa.Column("manifest", sa.Text(), nullable=False),
        sa.Column("result", sa.Text()),
    )
    op.create_table(
        "investigation_events",
        sa.Column("job_id", sa.String(), sa.ForeignKey("investigations.id"), primary_key=True),
        sa.Column("seq", sa.Integer(), primary_key=True),
        sa.Column("body", sa.Text(), nullable=False),
    )
    op.execute(
        "CREATE TRIGGER freeze_confirmation BEFORE UPDATE OF plan,plan_digest "
        "ON investigations WHEN OLD.plan IS NOT NULL "
        "BEGIN SELECT RAISE(ABORT, 'confirmation plan frozen'); END"
    )
    op.execute(
        "CREATE TRIGGER immutable_trial_manifest BEFORE UPDATE OF manifest,phase,arm "
        "ON investigation_trials BEGIN SELECT RAISE(ABORT, 'trial manifest frozen'); END"
    )
    op.execute(
        "CREATE TRIGGER immutable_trial_result BEFORE UPDATE OF result "
        "ON investigation_trials WHEN OLD.result IS NOT NULL "
        "BEGIN SELECT RAISE(ABORT, 'trial result frozen'); END"
    )
    for operation in ("UPDATE", "DELETE"):
        op.execute(
            f"CREATE TRIGGER progress_no_{operation.lower()} BEFORE {operation} "
            "ON investigation_events BEGIN SELECT RAISE(ABORT, 'durable event'); END"
        )


def downgrade():
    for trigger in (
        "freeze_confirmation",
        "immutable_trial_manifest",
        "immutable_trial_result",
        "progress_no_update",
        "progress_no_delete",
    ):
        op.execute(f"DROP TRIGGER {trigger}")
    for table in ("investigation_events", "investigation_trials", "investigations"):
        op.drop_table(table)
    op.drop_table("demo_starts")
