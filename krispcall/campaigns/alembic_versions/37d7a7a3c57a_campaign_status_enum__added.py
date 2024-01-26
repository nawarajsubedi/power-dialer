"""campaign_status_enum _added

Revision ID: 37d7a7a3c57a
Revises: 589bfa044008
Create Date: 2022-11-21 09:23:14.228489

"""
# pylint: disable=invalid-name, no-member, missing-function-docstring

from alembic import op
from krispcall.campaigns.adapters.orm import CAMPAIGN_STATUS_ENUM
from krispcall.campaigns.domain.models import CampaignStatus
from sqlalchemy.dialects import postgresql
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "37d7a7a3c57a"
down_revision = "589bfa044008"
branch_labels = None
depends_on = None


def upgrade():
    sales_campaign_status_enum = postgresql.ENUM(
        "active",
        "archived",
        "completed",
        "ended",
        "paused",
        "inprogress",
        name="sales_campaign_status_enum",
    )
    sales_campaign_status_enum.create(op.get_bind())
    op.alter_column(
        "campaigns",
        "campaign_status",
        existing_type=sa.String,
        type_=sa.Enum(
            *CAMPAIGN_STATUS_ENUM, name="sales_campaign_status_enum"
        ),
        nullable=False,
        default=CampaignStatus.ACTIVE.value,
        postgresql_using="campaign_status::sales_campaign_status_enum",
    )


def downgrade():
    op.alter_column(
        "campaigns",
        "campaign_status",
        type_=sa.String(30),
        nullable=False,
    )
