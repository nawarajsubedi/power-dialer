from datetime import datetime
from enum import Enum, unique
import typing
from uuid import UUID
from typing import TypedDict, Union
from krispcall.common.with_response import DataModel
from dataclasses import dataclass
from krispcall.konference.domain.models import (
    ConferenceStatus,
    ParticipantType,
    TwilioAccountSid,
    TwilioCallSid,
    TwilioCallStatus,
    TwilioConferenceFriendlyName,
    TwilioConferenceSid,
    AgentReference,
    RecordingUrl,
    RecordingDuration,
    CallDuration,
)
from krispcall.common.utils.shortid import ShortId


# Data models
class AddCampaignConversation(DataModel):
    id_: UUID
    twi_sid: UUID
    campaign_id: UUID
    status: ConferenceStatus
    created_by: UUID
    sequence_number: int
    contact_name: str
    contact_number: str
    recording_url: RecordingUrl = None
    initial_call: bool = True
    recording_duration: RecordingDuration = None
    call_duration: CallDuration = None
    reason_message: str = None
    reason_code: int = None


class AddCampaignConversationMsg(DataModel):
    id_: ShortId
    twi_sid: ShortId
    campaign_id: ShortId
    status: ConferenceStatus
    created_by: ShortId
    sequence_number: int
    contact_name: str
    contact_number: str
    recording_url: RecordingUrl = None
    initial_call: bool = True
    recording_duration: RecordingDuration = None
    call_duration: CallDuration = None
    reason_message: str = None
    reason_code: int = None


class QueueData(TypedDict):
    workspace: UUID
    campaign_id: UUID
    dialing_number: str
    dialing_number_id: UUID
    cool_Off_period_enabled: bool
    recording_enabled: bool
    cool_off_period: Union[None, int]
    next_number_to_dial: Union[None, str]
    next_conversation_id: Union[None, UUID]
    member: UUID
    call_script_id: Union[None, UUID]


class UpdateCampaignConversationNotes(DataModel):
    id: UUID
    campaignCallNoteId: UUID


class AddParticipantCall(DataModel):
    id_: UUID
    conversation_id: UUID
    twi_sid: TwilioCallSid
    status: TwilioCallStatus
    participant_type: ParticipantType
    created_by: AgentReference
    recording_url: typing.Optional[RecordingUrl] = None
    recording_duration: typing.Optional[RecordingDuration] = None
    call_duration: typing.Optional[CallDuration] = None


class AddParticipantCallMsg(DataModel):
    id_: ShortId
    conversation_id: ShortId
    twi_sid: TwilioCallSid
    status: TwilioCallStatus
    participant_type: ParticipantType
    created_by: ShortId
    recording_url: typing.Optional[RecordingUrl] = None
    recording_duration: typing.Optional[RecordingDuration] = None
    call_duration: typing.Optional[CallDuration] = None


@unique
class ConferenceEvent(str, Enum):
    participant_join = "participant-join"
    conference_end = "conference-end"
    participant_leave = "participant-leave"


@dataclass
class ConferenceParticipantEvent:
    """Model representing a conference participant event"""

    friendly_name: TwilioConferenceFriendlyName
    conference_sid: TwilioConferenceSid
    status_callback_event: ConferenceEvent
    timestamp: datetime
    account_sid: TwilioAccountSid
    sequence_number: str
    coaching: bool = False
    end_conference_on_exit: bool = True
    start_conference_on_enter: bool = True
    hold: bool = False
    muted: bool = False
    call_sid: TwilioCallSid = None
    call_sid_ending_conference: TwilioCallSid = None
    reason_conference_ended: str = None
    participant_call_status: str = None
    reason_participant_left: str = None
    reason: str = None


class TwilioAgentCallback(DataModel):
    call_sid: str
    call_status: str


class TwilioPSTNCallback(DataModel):
    call_sid: str
    call_status: str
