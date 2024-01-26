""" DB table for konference in sales api"""


from __future__ import annotations
import sqlalchemy as sa
from krispcall.common.database.bootstrap import SQL_METADATA
from sqlalchemy.dialects import postgresql

from krispcall.konference.domain.models import (
    ConferenceStatus,
    ParticipantType,
    TwilioCallStatus,
)

CONFERENCE_STATUS_ENUM = [each.value for each in list(ConferenceStatus)]
PARTICIPANT_STATUS_ENUM = [each.value for each in list(TwilioCallStatus)]
TWILIO_CALL_STATUS_ENUM = [each.value for each in list(TwilioCallStatus)]
PARTICIPANT_TYPE_ENUM = [each for each in list(ParticipantType)]
campaign_conversation = sa.Table(
    "campaign_conversation",
    SQL_METADATA,
    sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
    sa.Column("twi_sid", postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column("campaign_id", postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column("initial_call", sa.Boolean(), nullable=False),
    sa.Column(
        "current_attempt", sa.Integer(), nullable=False
    ),  # Current attempt is to track the call attempt
    # And send data to frontend
    # 0 - Initial call
    # 1 - First call attempt
    # 2 - Second call attempt
    # 3 - Third call attempt
    sa.Column(
        "status",
        sa.Enum(*CONFERENCE_STATUS_ENUM),
        nullable=False,
        default=ConferenceStatus.pending.value,
    ),
    sa.Column("reason_message", sa.String(255), nullable=True),
    sa.Column("reason_code", sa.Integer, nullable=True),
    sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column("recording_url", sa.String(1000), nullable=True, default=""),
    sa.Column("recording_duration", sa.Integer, nullable=True, default=0),
    sa.Column("call_duration", sa.Integer, nullable=True, default=0),
    sa.Column(
        "campaign_note_id", postgresql.UUID(as_uuid=False), nullable=True
    ),
    sa.Column("sequence_number", sa.Integer(), nullable=False),
    sa.Column("contact_name", sa.String(255), nullable=False),
    sa.Column("contact_number", sa.String(255), nullable=False),
    sa.Column("skipped", sa.Boolean(), nullable=False, default=False),
    sa.Column("skip_cooldown", sa.Boolean(), nullable=False, default=False),
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


participant_calls = sa.Table(
    "participant_calls",
    SQL_METADATA,
    sa.Column("id", postgresql.UUID(as_uuid=False)),
    sa.Column("conversation_id", postgresql.UUID(as_uuid=False)),
    sa.Column("twi_sid", sa.String(255), nullable=False),
    sa.Column(
        "participant_type",
        sa.Enum(*PARTICIPANT_TYPE_ENUM),
        nullable=False,
        default=ParticipantType.agent.value,
    ),
    sa.Column("recording_url", sa.String(255), nullable=True, default=""),
    sa.Column(
        "status",
        sa.Enum(*TWILIO_CALL_STATUS_ENUM),
        nullable=False,
        default=TwilioCallStatus.queued.value,
    ),
    sa.Column("created_by", postgresql.UUID(as_uuid=False)),
    sa.Column("recording_duration", sa.Integer, nullable=True, default=0),
    sa.Column("call_duration", sa.Integer, nullable=True, default=0),
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
    sa.ForeignKeyConstraint(["conversation_id"], ["campaign_conversation.id"]),
)
