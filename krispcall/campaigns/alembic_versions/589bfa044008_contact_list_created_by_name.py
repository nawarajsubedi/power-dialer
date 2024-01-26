"""contact_list_created_by_name

Revision ID: 589bfa044008
Revises: 5443bbe4d419
Create Date: 2022-11-08 09:24:11.539222

"""
# pylint: disable=invalid-name, no-member, missing-function-docstring

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "589bfa044008"
down_revision = "5443bbe4d419"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "campaign_contact_list_mast",
        sa.Column("created_by_name", sa.String(255), nullable=False),
    )


def downgrade():
    op.drop_column("campaign_contact_list_mast", "created_by_name")
