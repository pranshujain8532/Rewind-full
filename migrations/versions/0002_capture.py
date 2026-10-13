"""Encrypted payloads, immutable ordered events, session seals and occurrences."""

import sqlalchemy as sa
from alembic import op

revision = "0002_capture"
down_revision = "0001_p0"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "sessions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("metadata", sa.Text(), nullable=False),
        sa.Column("sealed", sa.Boolean(), nullable=False),
        sa.Column("seal", sa.Text()),
    )
    op.create_table(
        "capture_blobs",
        sa.Column("digest", sa.String(), primary_key=True),
        sa.Column("ciphertext", sa.LargeBinary(), nullable=False),
    )
    op.create_table(
        "capture_events",
        sa.Column("session_id", sa.String(), sa.ForeignKey("sessions.id"), primary_key=True),
        sa.Column("seq", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.String(), unique=True, nullable=False),
        sa.Column("event_hash", sa.String(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("signature", sa.String(), nullable=False),
        sa.Column("display", sa.Text(), nullable=False),
    )
    op.create_table(
        "chunk_occurrences",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("session_id", sa.String(), sa.ForeignKey("sessions.id"), nullable=False),
        sa.Column("fixture_occurrence", sa.String(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("blob_digest", sa.String(), nullable=False),
        sa.Column("source_uri", sa.String(), nullable=False),
        sa.Column("origin", sa.String(), nullable=False),
        sa.Column("model_call_id", sa.String(), nullable=False),
    )
    for operation in ("UPDATE", "DELETE"):
        op.execute(
            f"CREATE TRIGGER capture_no_{operation.lower()} BEFORE {operation} "
            "ON capture_events BEGIN SELECT RAISE(ABORT, 'immutable capture event'); END"
        )


def downgrade():
    for operation in ("update", "delete"):
        op.execute(f"DROP TRIGGER capture_no_{operation}")
    for table in ("chunk_occurrences", "capture_events", "capture_blobs", "sessions"):
        op.drop_table(table)
