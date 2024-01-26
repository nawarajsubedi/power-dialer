"""Created_by_name_added

Revision ID: e343c7fa2ca4
Revises: 637155bdfda0
Create Date: 2022-11-07 10:03:05.473553

"""
# pylint: disable=invalid-name, no-member, missing-function-docstring

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "e343c7fa2ca4"
down_revision = "637155bdfda0"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "campaigns",
        sa.Column("created_by_name", sa.String(255), nullable=False),
    )
    op.add_column(
        "campaigns",
        sa.Column(
            "dialing_number_id", postgresql.UUID(as_uuid=False), nullable=False
        ),
    )


def downgrade():
    op.drop_column("campaigns", "created_by_name")
    op.drop_column("campaigns", "dialing_number_id")
