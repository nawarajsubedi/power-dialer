from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from krispcall.common.domain.commands import Command
from krispcall.konference.domain import models


@dataclass
class AddCampaignConversationCommand(Command):
    id_: UUID
    twi_sid: UUID
    campaign_id: UUID
    status: str
    created_by: UUID
    contact_name: str
    contact_number: str
    initial_call: bool = True
    sequence_number: int = None
    recording_url: str = None
    recording_duration: int = None
    call_duration: int = None
    campaign_note_id: UUID = None
    reason_message: str = None
    reason_code: int = None


@dataclass
class UpdateCampaignConversationNoteCommand(Command):
    campaign_note_id: UUID


@dataclass
class UpdateCampaignConversationStatusCommand(Command):
    id: UUID
    status: models.ConferenceStatus
    reason_message: str = None
    reason_code: int = None


@dataclass
class UpdateCampaignParticipantCommand(Command):
    id: UUID
    status: models.ConferenceStatus


@dataclass
class AddCampaignParticipantCommand(Command):
    id_: UUID
    conversation_id: UUID
    twi_sid: models.TwilioCallSid
    status: models.TwilioCallStatus
    participant_type: models.ParticipantType
    created_by: models.AgentReference
    recording_url: models.RecordingUrl = None
    recording_duration: models.RecordingDuration = None
    call_duration: models.CallDuration = None
