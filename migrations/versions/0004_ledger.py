"""Immutable encrypted evidence, original-attack cases and bounded regression jobs."""

import sqlalchemy as sa
from alembic import op

revision = "0004_ledger"
down_revision = "0003_investigation"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "evidence_records",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "investigation_id", sa.String(), sa.ForeignKey("investigations.id"), nullable=False
        ),
        sa.Column("idempotency_key", sa.String(), unique=True, nullable=False),
        sa.Column("request_digest", sa.String(), nullable=False),
        sa.Column("created_at", sa.String(), nullable=False),
        sa.Column("bundle", sa.LargeBinary(), nullable=False),
        sa.Column("bundle_digest", sa.String(), nullable=False),
    )
    op.create_table(
        "regression_cases",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("record_id", sa.String(), sa.ForeignKey("evidence_records.id"), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
    )
    op.create_table(
        "regression_runs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("case_id", sa.String(), sa.ForeignKey("regression_cases.id"), nullable=False),
        sa.Column("idempotency_key", sa.String(), unique=True, nullable=False),
        sa.Column("request_digest", sa.String(), nullable=False),
        sa.Column("request", sa.Text(), nullable=False),
        sa.Column("plan", sa.Text(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("reason", sa.String()),
        sa.Column("created_at", sa.String(), nullable=False),
        sa.Column("started_at", sa.Float()),
        sa.Column("lease_until", sa.Float()),
        sa.Column("heartbeat_at", sa.String()),
        sa.Column("worker_id", sa.String()),
        sa.Column("cancel_requested", sa.Boolean(), nullable=False),
        sa.Column("manifest", sa.LargeBinary()),
    )
    op.create_table(
        "ledger_case_starts",
        sa.Column("idempotency_key", sa.String(), primary_key=True),
        sa.Column("case_id", sa.String(), sa.ForeignKey("regression_cases.id"), nullable=False),
        sa.Column("request_digest", sa.String(), nullable=False),
    )
    op.create_table(
        "regression_trials",
        sa.Column("run_id", sa.String(), sa.ForeignKey("regression_runs.id"), primary_key=True),
        sa.Column("ordinal", sa.Integer(), primary_key=True),
        sa.Column("spec", sa.Text(), nullable=False),
        sa.Column("result", sa.Text()),
    )
    for table in ("evidence_records", "regression_cases", "ledger_case_starts"):
        for operation in ("UPDATE", "DELETE"):
            op.execute(
                f"CREATE TRIGGER {table}_no_{operation.lower()} BEFORE {operation} ON {table} "
                "BEGIN SELECT RAISE(ABORT, 'immutable ledger artifact'); END"
            )
    op.execute(
        "CREATE TRIGGER regression_spec_frozen BEFORE UPDATE OF spec ON regression_trials "
        "BEGIN SELECT RAISE(ABORT, 'regression specification frozen'); END"
    )
    op.execute(
        "CREATE TRIGGER regression_result_frozen BEFORE UPDATE OF result ON regression_trials "
        "WHEN OLD.result IS NOT NULL BEGIN SELECT RAISE(ABORT, 'regression result frozen'); END"
    )
    op.execute(
        "CREATE TRIGGER regression_trial_no_delete BEFORE DELETE ON regression_trials "
        "BEGIN SELECT RAISE(ABORT, 'regression trial retained'); END"
    )
    op.execute(
        "CREATE TRIGGER regression_plan_frozen BEFORE UPDATE OF request,plan,case_id "
        "ON regression_runs BEGIN SELECT RAISE(ABORT, 'regression plan frozen'); END"
    )
    op.execute(
        "CREATE TRIGGER regression_run_frozen BEFORE UPDATE ON regression_runs "
        "WHEN OLD.manifest IS NOT NULL BEGIN SELECT RAISE(ABORT, 'regression manifest frozen'); END"
    )
    op.execute(
        "CREATE TRIGGER regression_run_no_delete BEFORE DELETE ON regression_runs "
        "BEGIN SELECT RAISE(ABORT, 'regression run retained'); END"
    )


def downgrade():
    for table in (
        "regression_trials",
        "regression_runs",
        "ledger_case_starts",
        "regression_cases",
        "evidence_records",
    ):
        op.drop_table(table)
