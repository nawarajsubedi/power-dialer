"""init campaigns tables

Revision ID: 637155bdfda0
Revises:
Create Date: 2022-09-22 07:10:16.499785

"""
# pylint: disable=invalid-name, no-member, missing-function-docstring

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "637155bdfda0"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # campaign contact list table
    op.create_table(
        "campaign_contact_list_mast",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("name", sa.String(63), nullable=False),
        sa.Column("contact_count", sa.String(10), nullable=False),
        sa.Column("is_archived", sa.Boolean(), nullable=False),
        sa.Column(
            "is_imported_contact_list_hidden", sa.Boolean(), nullable=False
        ),
        sa.Column(
            "workspace_id", postgresql.UUID(as_uuid=False), nullable=False
        ),
        sa.Column(
            "created_by", postgresql.UUID(as_uuid=False), nullable=False
        ),
        sa.Column(
            "modified_by", postgresql.UUID(as_uuid=False), nullable=False
        ),
        sa.Column(
            "modified_on",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.Column(
            "created_on",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            default=sa.func.now(),
        ),
    )

    # create contact list detail table
    op.create_table(
        "campaign_contact_list_detail",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column(
            "contact_list_id", postgresql.UUID(as_uuid=False), nullable=False
        ),
        sa.Column("contact_name", sa.String(63), nullable=False),
        sa.Column("contact_number", sa.String(63), nullable=False),
        sa.Column(
            "created_on",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            default=sa.func.now(),
        ),
        sa.Column(
            "created_by", postgresql.UUID(as_uuid=False), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["contact_list_id"], ["campaign_contact_list_mast.id"]
        ),
    )

    # voicemails table
    op.create_table(
        "campaign_voicemails",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("name", sa.String(63), nullable=False),
        sa.Column("recording_type", sa.String(30), nullable=False),
        sa.Column("recording_url", sa.String(255), nullable=False),
        sa.Column("tts_source", sa.String(255), nullable=True),
        sa.Column("tts_gender", sa.String(15), nullable=True),
        sa.Column("tts_accent", sa.String(31), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column(
            "workspace_id", postgresql.UUID(as_uuid=False), nullable=False
        ),
        sa.Column(
            "created_by", postgresql.UUID(as_uuid=False), nullable=False
        ),
        sa.Column(
            "created_on",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            default=sa.func.now(),
        ),
    )

    # callscripts table
    op.create_table(
        "campaign_callscripts",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("script_title", sa.String(255), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column(
            "workspace_id", postgresql.UUID(as_uuid=False), nullable=False
        ),
        sa.Column(
            "created_by", postgresql.UUID(as_uuid=False), nullable=False
        ),
        sa.Column(
            "created_on",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            default=sa.func.now(),
        ),
    )

    op.create_table(
        "campaign_callscripts_attributes",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column(
            "created_on",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            default=sa.func.now(),
        ),
        sa.Column(
            "created_by", postgresql.UUID(as_uuid=False), nullable=False
        ),
    )

    # campaign table
    op.create_table(
        "campaigns",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column(
            "workspace_id", postgresql.UUID(as_uuid=False), nullable=False
        ),
        sa.Column("campaign_name", sa.String(255), nullable=False),
        sa.Column("assigne_name", sa.String(255), nullable=False),
        sa.Column(
            "assigne_id", postgresql.UUID(as_uuid=False), nullable=False
        ),
        sa.Column("dialing_number", sa.String(255), nullable=False),
        sa.Column("calling_datacenter", sa.String(255), nullable=False),
        sa.Column("campaign_status", sa.String(30), nullable=False),
        sa.Column("call_recording_enabled", sa.Boolean(), nullable=False),
        sa.Column("voicemail_enabled", sa.Boolean(), nullable=False),
        sa.Column(
            "voicemail_id", postgresql.UUID(as_uuid=False), nullable=True
        ),
        sa.Column("cooloff_period_enabled", sa.Boolean(), nullable=False),
        sa.Column("cool_off_period", sa.Integer(), nullable=True),
        sa.Column("call_attempts_enabled", sa.Boolean(), nullable=False),
        sa.Column("call_attempts_count", sa.Integer(), nullable=True),
        sa.Column("call_attempts_gap", sa.Integer(), nullable=True),
        sa.Column("call_script_enabled", sa.Boolean(), nullable=False),
        sa.Column(
            "call_script_id", postgresql.UUID(as_uuid=False), nullable=True
        ),
        sa.Column(
            "contact_list_id",
            postgresql.UUID(as_uuid=False),
            nullable=False,
        ),
        sa.Column(
            "is_archived",
            sa.Boolean,
            nullable=False,
            default=False,
        ),
        sa.Column("next_number_to_dial", sa.String(255), nullable=True),
        sa.Column(
            "created_by", postgresql.UUID(as_uuid=False), nullable=False
        ),
        sa.Column(
            "modified_by", postgresql.UUID(as_uuid=False), nullable=False
        ),
        sa.Column(
            "created_on",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "modified_on",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["contact_list_id"], ["campaign_contact_list_mast.id"]
        ),
    )


def downgrade():
    op.drop_table("campaign_contact_list_mast")
    op.drop_table("campaign_contact_list_detail")
    op.drop_table("campaign_voicemails")
    op.drop_table("campaign_callscripts")
    op.drop_table("campaign_callscripts_attributes")
    op.drop_table("campaigns")
