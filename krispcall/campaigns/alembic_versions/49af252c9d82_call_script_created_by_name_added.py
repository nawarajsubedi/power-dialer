"""call_script_Created_by_name_added

Revision ID: 49af252c9d82
Revises: e343c7fa2ca4
Create Date: 2022-11-07 14:00:43.425426

"""
# pylint: disable=invalid-name, no-member, missing-function-docstring

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "49af252c9d82"
down_revision = "e343c7fa2ca4"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "campaign_callscripts",
        sa.Column("created_by_name", sa.String(255), nullable=False),
    )


def downgrade():
    op.drop_column("campaign_callscripts", "created_by_name")
