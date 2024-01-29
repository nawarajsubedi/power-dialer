from datetime import datetime
import typing
from uuid import UUID, uuid4
from enum import Enum, unique

from krispcall.common.domain.entities import BaseEntity

WorkspaceReference = typing.NewType("WorkspaceReference", UUID)
PhoneNumber = typing.NewType("PhoneNumber", str)
RecordingUrl = typing.NewType("RecordingUrl", str)
AgentReference = typing.NewType("AgentReference", UUID)
TwilioConferenceFriendlyName = typing.NewType(
    "TwilioConferenceFriendlyName", UUID
)
TwilioConferenceSid = typing.NewType("TwilioConferenceSid", str)
CampaignConversationReference = typing.NewType(
    "CampaignConversationReference", UUID
)
TwilioCallSid = typing.NewType("TwilioCallSid", str)
TwilioAccountSid = typing.NewType("TwilioAccountSid", str)
CallDuration = typing.NewType("CallDuration", float)
RecordingDuration = typing.NewType("RecordingDuration", float)


@unique
class ConferenceStatus(str, Enum):
    failed = "failed"
    completed = "completed"
    in_progress = "in_progress"
    on_hold = "on_hold"
    in_queue = "in_queue"
    pending = "pending"
    busy = "busy"
    no_answer = "no_answer"
    cancelled = "cancelled"


@unique
class TwilioCallStatus(str, Enum):
    queued = "queued"
    ringing = "ringing"
    in_progress = "in_progress"
    canceled = "canceled"
    completed = "completed"
    busy = "busy"
    no_answer = "no_answer"
    failed = "failed"


@unique
class ParticipantType(str, Enum):
    agent = "agent"
    customer = "client"


@unique
class CallLegType(str, Enum):
    agent = "agent"
    customer = "client"


class CampaignConversation(BaseEntity):
    id_: UUID
    twi_sid: TwilioConferenceFriendlyName
    campaign_id: UUID
    status: ConferenceStatus
    created_by: AgentReference
    sequence_number: int
    contact_name: str
    contact_number: str
    created_at: typing.Optional[datetime]
    modified_at: typing.Optional[datetime]
    skipped: bool = False
    recording_url: RecordingUrl = None
    recording_duration: RecordingDuration = None
    initial_call: bool = True
    current_attempt: int = 0
    call_duration: CallDuration = None
    campaign_note_id: UUID = None
    skip_cooldown: bool = False
    reason_message: typing.Union[str, None] = (None,)
    reason_code: typing.Union[int, None] = (None,)

    def update(self, mapping: typing.Dict[str, typing.Any]):
        return self.copy(update=mapping)


def campaign_conversation_factory(
    id_: UUID,
    twi_sid: TwilioConferenceFriendlyName,
    campaign_id: UUID,
    status: ConferenceStatus,
    created_by: AgentReference,
    sequence_number: int,
    contact_name: str,
    contact_number: str,
    skipped: bool = False,
    recording_url: RecordingUrl = None,
    initial_call: bool = True,
    recording_duration: RecordingDuration = None,
    current_attempt: int = 0,
    call_duration: CallDuration = None,
    campaign_note_id: typing.Union[UUID, None] = None,
    skip_cooldown: bool = False,
    reason_message: typing.Union[str, None] = None,
    reason_code: typing.Union[int, None] = None,
) -> CampaignConversation:
    return CampaignConversation(
        id_=id_,
        twi_sid=twi_sid,
        campaign_id=campaign_id,
        status=status,
        created_by=created_by,
        sequence_number=sequence_number,
        contact_name=contact_name,
        contact_number=contact_number,
        initial_call=initial_call,
        current_attempt=current_attempt,
        recording_url=recording_url,
        recording_duration=recording_duration,
        call_duration=call_duration,
        campaign_note_id=campaign_note_id,
        skipped=skipped,
        skip_cooldown=skip_cooldown,
        reason_message=reason_message,
        reason_code=reason_code,
    )


class ParticipantCall(BaseEntity):
    id_: UUID
    conversation_id: CampaignConversationReference
    twi_sid: TwilioCallSid
    status: TwilioCallStatus
    participant_type: ParticipantType
    created_at: typing.Optional[datetime]
    modified_at: typing.Optional[datetime]
    recording_url: RecordingUrl = None
    duration: RecordingDuration = None
    created_by: AgentReference = None
    recording_duration: RecordingDuration = None
    call_duration: CallDuration = None

    def update(self, mapping: typing.Dict[str, typing.Any]):
        return self.copy(update=mapping)


def participant_call_factory(
    id_: UUID,
    conversation_id: CampaignConversationReference,
    twi_sid: TwilioCallSid,
    status: TwilioCallStatus,
    participant_type: ParticipantType,
    created_by: AgentReference,
    recording_url: RecordingUrl = None,
    call_duration: RecordingDuration = 0,
    recording_duration: RecordingDuration = 0,
) -> ParticipantCall:
    return ParticipantCall(
        id_=id_,
        conversation_id=conversation_id,
        twi_sid=twi_sid,
        status=status,
        participant_type=participant_type,
        recording_url=recording_url,
        created_by=created_by,
        recording_duration=recording_duration,
        call_duration=call_duration,
    )
