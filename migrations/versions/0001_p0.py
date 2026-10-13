"""Initial P0 storage metadata; no fabricated sessions or evidence."""

import sqlalchemy as sa
from alembic import op

revision = "0001_p0"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    table = op.create_table(
        "app_metadata",
        sa.Column("key", sa.String(), primary_key=True),
        sa.Column("value", sa.String(), nullable=False),
    )
    op.bulk_insert(table, [{"key": "schema_version", "value": "1.0"}])


def downgrade() -> None:
    op.drop_table("app_metadata")
