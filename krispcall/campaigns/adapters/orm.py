"""
db tables for campaigns
"""
from __future__ import annotations
from krispcall.campaigns.domain.models import CampaignStatus

import sqlalchemy as sa  # type: ignore
from krispcall.common.database.bootstrap import SQL_METADATA
from sqlalchemy.dialects import postgresql  # type: ignore

CAMPAIGN_STATUS_ENUM = [each.value for each in list(CampaignStatus)]
campaign_contact_list_mast = sa.Table(
    "campaign_contact_list_mast",
    SQL_METADATA,
    sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
    sa.Column("name", sa.String(63), nullable=False),
    sa.Column("created_by_name", sa.String(255), nullable=False),
    sa.Column("contact_count", sa.String(10), nullable=False),
    sa.Column("is_archived", sa.Boolean(), nullable=False),
    sa.Column("is_imported_contact_list_hidden", sa.Boolean(), nullable=False),
    sa.Column("workspace_id", postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column("modified_by", postgresql.UUID(as_uuid=False), nullable=False),
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

campaign_contact_list_detail = sa.Table(
    "campaign_contact_list_detail",
    SQL_METADATA,
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
    sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=False),
    sa.ForeignKeyConstraint(
        ["contact_list_id"], ["campaign_contact_list_mast.id"]
    ),
)

# campaign_callable_list = ""
# /**
# **/

# campaign_reattempt_list = ""
# /**
# -- ((phonenumber, 5), (phonenumber2, 5) ...(phonenumber16, 5))
# -- ((phonenumber, 4), (phonenumber2, 5) ...(phonenumber16, 5))
# -- ((phonenumber, 3), (phonenumber2, 5) ...(phonenumber16, 5))
# -- ((phonenumber, 2), (phonenumber2, 5) ...(phonenumber16, 5))
# -- ((phonenumber, 1), (phonenumber2, 5) ...(phonenumber16, 5))
# --
# --
# -- ((phonenumber, 0), (phonenumber2, 4) ...(phonenumber16, 5))
# -- ((phonenumber, 0), (phonenumber2, 3) ...(phonenumber16, 5))
# -- ((phonenumber, 0), (phonenumber2, 2) ...(phonenumber16, 5))
# --((phonenumber, 0), (phonenumber2, 1) ...(phonenumber16, 5))

# **/


campaign_voicemails = sa.Table(
    "campaign_voicemails",
    SQL_METADATA,
    sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
    sa.Column("name", sa.String(63), nullable=False),
    # TO DO: Remove nullable fields
    sa.Column("recording_type", sa.String(30), nullable=False),  # NULL , ""
    sa.Column("recording_url", sa.String(255), nullable=False),
    sa.Column("tts_source", sa.String(255), nullable=True),
    sa.Column("tts_gender", sa.String(15), nullable=True),
    sa.Column("tts_accent", sa.String(31), nullable=True),
    sa.Column("is_default", sa.Boolean(), nullable=False),
    sa.Column("created_by_name", sa.String(255), nullable=False),
    sa.Column("workspace_id", postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column(
        "created_on",
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        default=sa.func.now(),
    ),
)


campaign_callscripts = sa.Table(
    "campaign_callscripts",
    SQL_METADATA,
    sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
    sa.Column("script_title", sa.String(255), nullable=False),
    sa.Column("description", sa.String(), nullable=False),
    sa.Column("created_by_name", sa.String(255), nullable=False),
    sa.Column("is_default", sa.Boolean(), nullable=False),
    sa.Column("workspace_id", postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column(
        "created_on",
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        default=sa.func.now(),
    ),
)


campaign_callscripts_attributes = sa.Table(
    "campaign_callscripts_attributes",
    SQL_METADATA,
    sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
    sa.Column("name", sa.String(255), nullable=False),
    sa.Column("description", sa.String(), nullable=False),
    sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column(
        "created_on",
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        default=sa.func.now(),
    ),
)

campaigns_campaigns = sa.Table(
    "campaigns",
    SQL_METADATA,
    sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
    sa.Column("workspace_id", postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column("campaign_name", sa.String(255), nullable=False),
    sa.Column("assigne_name", sa.String(255), nullable=False),
    sa.Column("assigne_id", postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column(
        "dialing_number_id", postgresql.UUID(as_uuid=False), nullable=False
    ),
    sa.Column("created_by_name", sa.String(255), nullable=False),
    sa.Column("dialing_number", sa.String(255), nullable=False),
    sa.Column("calling_datacenter", sa.String(255), nullable=False),
    sa.Column("callable_data", sa.PickleType(), nullable=False),
    sa.Column(
        "campaign_status",
        sa.Enum(*CAMPAIGN_STATUS_ENUM),
        nullable=False,
        default=CampaignStatus.ACTIVE.value,
    ),
    sa.Column("call_recording_enabled", sa.Boolean(), nullable=False),
    sa.Column("voicemail_enabled", sa.Boolean(), nullable=False),
    sa.Column("voicemail_id", postgresql.UUID(as_uuid=False), nullable=True),
    sa.Column("cooloff_period_enabled", sa.Boolean(), nullable=False),
    sa.Column("cool_off_period", sa.Integer(), nullable=True),
    sa.Column("call_attempts_enabled", sa.Boolean(), nullable=False),
    sa.Column("call_attempts_count", sa.Integer(), nullable=True),
    sa.Column("call_attempts_gap", sa.Integer(), nullable=True),
    sa.Column("call_script_enabled", sa.Boolean(), nullable=False),
    sa.Column("is_archived", sa.Boolean(), nullable=False, default=False),
    sa.Column("call_script_id", postgresql.UUID(as_uuid=False), nullable=True),
    sa.Column(
        "contact_list_id", postgresql.UUID(as_uuid=False), nullable=False
    ),
    sa.Column("next_number_to_dial", sa.String(255), nullable=True),
    sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column("modified_by", postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column(
        "created_on",
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        default=sa.func.now(),
    ),
    sa.Column(
        "modified_on",
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        default=sa.func.now(),
        onupdate=sa.func.now(),
    ),
    sa.ForeignKeyConstraint(
        ["contact_list_id"], ["campaign_contact_list_mast.id"]
    ),
)


campaign_callnotes = sa.Table(
    "campaigns_call_notes",
    SQL_METADATA,
    sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
    sa.Column(
        "campaign_conversation_id",
        postgresql.UUID(as_uuid=False),
        nullable=False,
    ),
    sa.Column("campaign_id", postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column("call_note", sa.String(255), nullable=True),
    sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column(
        "created_at",
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        default=sa.func.now(),
    ),
    sa.Column(
        "modified_at",
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        default=sa.func.now(),
    ),
)

campaign_stats = sa.Table(
    "campaign_stats",
    SQL_METADATA,
    sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
    sa.Column("campaign_id", postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column("total_contacts", sa.Integer(), nullable=True, default=0),
    sa.Column("dialed_contacts", sa.Integer(), nullable=True, default=0),
    sa.Column("voicemail_drops", sa.Integer(), nullable=True, default=0),
    sa.Column("answered_calls", sa.Integer(), nullable=True, default=0),
    sa.Column("unanswered_calls", sa.Integer(), nullable=True, default=0),
    sa.Column("active_call_duration", sa.Integer(), nullable=True, default=0),
    sa.Column("campaign_duration", sa.Integer(), nullable=True, default=0),
)
