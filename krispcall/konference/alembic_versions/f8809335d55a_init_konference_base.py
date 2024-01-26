"""Init konference base

Revision ID: f8809335d55a
Revises:
Create Date: 2022-11-29 10:50:22.837093

"""
# pylint: disable=invalid-name, no-member, missing-function-docstring

from alembic import op
from krispcall.konference.adapters.orm import (
    CONFERENCE_STATUS_ENUM,
    PARTICIPANT_TYPE_ENUM,
    TWILIO_CALL_STATUS_ENUM,
)
from krispcall.konference.domain.models import (
    ConferenceStatus,
    ParticipantType,
    TwilioCallStatus,
)
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "f8809335d55a"
down_revision = None
branch_labels = ("konference",)
depends_on = None


def upgrade():
    # add new campaign conversation table
    conference_status_enum = postgresql.ENUM(
        "failed",
        "completed",
        "in_progress",
        "on_hold",
        "in_queue",
        "pending",
        name="conference_status_enum",
    )
    twilio_call_status_enum = postgresql.ENUM(
        "queued",
        "ringing",
        "in_progress",
        "canceled",
        "completed",
        "busy",
        "no_answer",
        "failed",
        name="twilio_call_status_enum",
    )
    participant_type_enum = postgresql.ENUM(
        "agent",
        "client",
        name="participant_type_enum",
    )
    op.create_table(
        "campaign_conversation",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("twi_sid", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column(
            "campaign_id", postgresql.UUID(as_uuid=False), nullable=False
        ),
        sa.Column("initial_call", sa.Boolean(), nullable=False),
        sa.Column("current_attempt", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            type_=conference_status_enum,
            nullable=False,
            default=ConferenceStatus.pending.value,
        ),
        sa.Column(
            "created_by", postgresql.UUID(as_uuid=False), nullable=False
        ),
        sa.Column("recording_url", sa.String(1000), nullable=True, default=""),
        sa.Column("recording_duration", sa.Integer, nullable=True, default=0),
        sa.Column("call_duration", sa.Integer, nullable=True, default=0),
        sa.Column(
            "campaign_note_id",
            postgresql.UUID(as_uuid=False),
            nullable=True,
        ),
        sa.Column("sequence_number", sa.Integer(), nullable=False),
        sa.Column("contact_name", sa.String(255), nullable=False),
        sa.Column("contact_number", sa.String(255), nullable=False),
        sa.Column("skipped", sa.Boolean(), nullable=False, default=False),
        sa.Column(
            "skip_cooldown", sa.Boolean(), nullable=False, default=False
        ),
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

    # add participant calls table
    op.create_table(
        "participant_calls",
        sa.Column("id", postgresql.UUID(as_uuid=False)),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=False)),
        sa.Column("twi_sid", sa.String(255), nullable=False),
        sa.Column(
            "participant_type",
            type_=participant_type_enum,
            nullable=False,
            default=ParticipantType.agent.value,
        ),
        sa.Column("recording_url", sa.String(255), nullable=True, default=""),
        sa.Column(
            "status",
            type_=twilio_call_status_enum,
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
        sa.ForeignKeyConstraint(
            ["conversation_id"], ["campaign_conversation.id"]
        ),
    )


def downgrade():
    op.drop_table("campaign_conversation")
    op.drop_table("participant_calls")
