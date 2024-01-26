"""Expand conference conversation status

Revision ID: d94f896050b0
Revises: f8809335d55a
Create Date: 2023-08-30 14:18:21.749975

"""
# pylint: disable=invalid-name, no-member, missing-function-docstring

from alembic import op
from krispcall.konference.adapters.orm import CONFERENCE_STATUS_ENUM
from krispcall.konference.domain.models import ConferenceStatus
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "d94f896050b0"
down_revision = "f8809335d55a"
branch_labels = None
depends_on = None


def upgrade():
    with op.get_context().autocommit_block():
        op.execute(
            "ALTER TYPE conference_status_enum ADD VALUE IF NOT EXISTS 'no_answer'"
        )
        op.execute(
            "ALTER TYPE conference_status_enum ADD VALUE IF NOT EXISTS 'busy'"
        )
        op.execute(
            "ALTER TYPE conference_status_enum ADD VALUE IF NOT EXISTS 'cancelled'"
        )


def downgrade():
    pass
