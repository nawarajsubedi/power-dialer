"""voicemail_created_by_name_added

Revision ID: 5443bbe4d419
Revises: 49af252c9d82
Create Date: 2022-11-07 14:33:38.746205

"""
# pylint: disable=invalid-name, no-member, missing-function-docstring

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5443bbe4d419"
down_revision = "49af252c9d82"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "campaign_voicemails",
        sa.Column("created_by_name", sa.String(255), nullable=False),
    )


def downgrade():
    op.drop_column("campaign_voicemails", "created_by_name")
