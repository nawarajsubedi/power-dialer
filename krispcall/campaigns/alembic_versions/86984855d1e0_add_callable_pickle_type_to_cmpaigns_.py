"""add callable pickle type to cmpaigns table

Revision ID: 86984855d1e0
Revises: 37d7a7a3c57a
Create Date: 2022-12-01 10:49:53.314442

"""
# pylint: disable=invalid-name, no-member, missing-function-docstring

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "86984855d1e0"
down_revision = "37d7a7a3c57a"
branch_labels = None
depends_on = None


def upgrade():
    # add pickle type to campaigns table
    op.add_column(
        "campaigns",
        sa.Column(
            "callable_data",
            sa.PickleType(),
            nullable=False,
        ),
    )


def downgrade():
    op.drop_column("campaigns", "callable_data")
