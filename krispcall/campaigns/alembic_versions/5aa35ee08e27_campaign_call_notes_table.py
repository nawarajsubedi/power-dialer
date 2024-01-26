"""campaign call notes table

Revision ID: 5aa35ee08e27
Revises: 31414297f9ca
Create Date: 2023-08-15 04:33:51.756673

"""
# pylint: disable=invalid-name, no-member, missing-function-docstring

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "5aa35ee08e27"
down_revision = "31414297f9ca"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "campaigns_call_notes",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column(
            "campaign_conversation_id",
            postgresql.UUID(as_uuid=False),
            nullable=False,
        ),
        sa.Column(
            "campaign_id", postgresql.UUID(as_uuid=False), nullable=False
        ),
        sa.Column("call_note", sa.String(255), nullable=True),
        sa.Column(
            "created_by", postgresql.UUID(as_uuid=False), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            default=sa.func.now(),
        ),
        sa.Column(
            "modified_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            default=sa.func.now(),
        ),
    )


def downgrade():
    op.drop_table(
        "campaigns_call_notes",
    )
