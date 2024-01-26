"""campaign_stats table

Revision ID: 31414297f9ca
Revises: 86984855d1e0
Create Date: 2023-06-29 09:08:32.926466

"""
# pylint: disable=invalid-name, no-member, missing-function-docstring

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "31414297f9ca"
down_revision = "86984855d1e0"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "campaign_stats",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column(
            "campaign_id", postgresql.UUID(as_uuid=False), nullable=False
        ),
        sa.Column("total_contacts", sa.Integer(), nullable=True, default=0),
        sa.Column("dialed_contacts", sa.Integer(), nullable=True, default=0),
        sa.Column("voicemail_drops", sa.Integer(), nullable=True, default=0),
        sa.Column("answered_calls", sa.Integer(), nullable=True, default=0),
        sa.Column("unanswered_calls", sa.Integer(), nullable=True, default=0),
        sa.Column(
            "active_call_duration", sa.Integer(), nullable=True, default=0
        ),
        sa.Column("campaign_duration", sa.Integer(), nullable=True, default=0),
    )


def downgrade():
    op.drop_table("campaign_stats")
