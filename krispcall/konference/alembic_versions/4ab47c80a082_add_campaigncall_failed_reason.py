"""add-campaigncall-failed-reason

Revision ID: 4ab47c80a082
Revises: daa35e7911e1
Create Date: 2024-01-02 13:46:09.869559

"""
# pylint: disable=invalid-name, no-member, missing-function-docstring

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4ab47c80a082"
down_revision = "7a1684c805b4"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "campaign_conversation",
        sa.Column("reason_message", sa.String(255), nullable=True),
    )
    op.add_column(
        "campaign_conversation",
        sa.Column("reason_code", sa.Integer, nullable=True),
    )


def downgrade():
    pass
