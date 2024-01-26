"""Force primary key in update table

Revision ID: 7a1684c805b4
Revises: d94f896050b0
Create Date: 2023-10-02 08:48:21.769410

"""
# pylint: disable=invalid-name, no-member, missing-function-docstring

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7a1684c805b4"
down_revision = "d94f896050b0"
branch_labels = None
depends_on = None


def upgrade():
    with op.get_context().autocommit_block():
        # create id as primary key on participant_calls table
        op.execute(
            "ALTER TABLE participant_calls ADD CONSTRAINT participant_calls_pkey PRIMARY KEY (id)"
        )


def downgrade():
    with op.get_context().autocommit_block():
        op.execute(
            "ALTER TABLE participant_calls DROP CONSTRAINT participant_calls_pkey"
        )
