import typing
from uuid import UUID, uuid4
from enum import Enum, unique

from krispcall.common.models.models import BaseEntity

WorkspaceReference = typing.NewType("WorkspaceReference", UUID)
PhoneNumber = typing.NewType("PhoneNumber", str)
CampaignContactMastReference = typing.NewType(
    "CampaignContactMastReference", UUID
)


@unique
class CampaignStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    COMPLETED = "completed"
    ENDED = "ended"
    PAUSED = "paused"
    INPROGRESS = "inprogress"


class Campaigns(BaseEntity):
    id_: UUID
    workspace_id: UUID
    campaign_name: str
    created_by_name: str
    dialing_number_id: UUID
    assigne_name: str
    assigne_id: UUID
    dialing_number: str
    calling_datacenter: str
    campaign_status: str
    call_recording_enabled: bool
    voicemail_enabled: bool
    voicemail_id: typing.Optional[UUID]
    cooloff_period_enabled: bool
    cool_off_period: typing.Optional[int]
    call_attempts_enabled: bool
    call_attempts_count: typing.Optional[int]
    call_attempts_gap: typing.Optional[int]
    call_script_enabled: bool
    call_script_id: typing.Optional[UUID]
    contact_list_id: UUID
    next_number_to_dial: typing.Optional[str]
    is_archived: bool
    callable_data: typing.Dict = None # type: ignore

    def update(self, mapping: typing.Dict[str, typing.Any]):
        return self.copy(update=mapping)


class CampaignVoicemail(BaseEntity):
    id_: UUID
    source: typing.Optional[str]
    created_by_name: str
    recording_type: str
    recording_url: str
    voice: typing.Optional[str]
    accent: typing.Optional[str]
    workspace_id: WorkspaceReference
    name: str
    is_default: bool

    def update(self, mapping: typing.Dict[str, typing.Any]):
        return self.copy(update=mapping)


class CampaignCallScripts(BaseEntity):
    id_: UUID
    workspace_id: WorkspaceReference
    created_by_name: str
    script_title: str
    description: str
    is_default: bool

    def update(self, mapping: typing.Dict[str, typing.Any]):
        return self.copy(update=mapping)


class CampaignCallNotes(BaseEntity):
    id_: UUID
    campaign_conversation_id: UUID
    campaign_id: UUID
    call_note: str

    def update(self, mapping: typing.Dict[str, typing.Any]):
        return self.copy(update=mapping)


class CampaignCallScriptsAttributes(BaseEntity):
    id_: UUID
    name: str
    description: str

    def update(self, mapping: typing.Dict[str, typing.Any]):
        return self.copy(update=mapping)


class CampaignContactListMast(BaseEntity):
    id_: UUID
    name: str
    contact_count: int
    created_by_name: str
    is_archived: bool
    workspace: WorkspaceReference
    is_contact_list_hidden: bool

    def update(self, mapping: typing.Dict[str, typing.Any]):
        return self.copy(update=mapping)


class CampaignContactListDetail(BaseEntity):
    id_: UUID
    contact_list_id: CampaignContactMastReference
    contact_name: str
    contact_number: PhoneNumber


class CampaignStats(BaseEntity):
    id_: UUID
    campaign_id: UUID
    total_contacts: int
    dialed_contacts: int
    voicemail_drops: int
    answered_calls: int
    unanswered_calls: int
    active_call_duration: int
    campaign_duration: int

    def update(self, mapping: typing.Dict[str, typing.Any]):
        return self.copy(update=mapping)


def campaign_contact_list_mast_factory(
    workspace: WorkspaceReference,
    *,
    name: str,
    contact_count: int,
    is_archived: bool,
    created_by_name: str,
    is_hidden: bool,
) -> CampaignContactListMast:
    return CampaignContactListMast(
        id_=uuid4(),
        name=name,
        created_by_name=created_by_name,
        contact_count=contact_count,
        is_archived=is_archived,
        workspace=workspace,
        is_contact_list_hidden=is_hidden,
    )


def campaign_contact_list_detail_factory(
    contact_list_id: CampaignContactListMast,
    *,
    contact_name: str,
    contact_number: PhoneNumber,
) -> CampaignContactListDetail:
    return CampaignContactListDetail(
        id_=uuid4(),
        contact_list_id=contact_list_id, # type: ignore
        contact_name=contact_name,
        contact_number=contact_number,
    )


def campaignVoicemail_factory(
    workspace_id: WorkspaceReference,
    recording_url: str,
    recording_type: str,
    created_by_name: str,
    source: typing.Optional[str],
    voice: typing.Optional[str],
    accent: typing.Optional[str],
    name: str,
    is_default: bool,
) -> CampaignVoicemail:
    return CampaignVoicemail(
        id_=uuid4(),
        source=source,
        recording_type=recording_type,
        recording_url=recording_url,
        workspace_id=workspace_id,
        created_by_name=created_by_name,
        voice=voice,
        accent=accent,
        name=name,
        is_default=is_default,
    )


def campaignCallScripts_factory(
    workspace_id: WorkspaceReference,
    script_title: str,
    description: str,
    created_by_name: str,
    is_default: bool,
) -> CampaignCallScripts:
    return CampaignCallScripts(
        id_=uuid4(),
        workspace_id=workspace_id,
        script_title=script_title,
        description=description,
        created_by_name=created_by_name,
        is_default=is_default,
    )


def campaignCallScriptsAttibutes_factory(
    name: str,
    description: str,
) -> CampaignCallScriptsAttributes:
    return CampaignCallScriptsAttributes(
        id_=uuid4(),
        name=name,
        description=description,
    )


def campaignCallNotes_factory(
    call_note: str, campaign_id: UUID, campaign_conversation_id: UUID
) -> CampaignCallNotes:
    return CampaignCallNotes(
        id_=uuid4(),
        campaign_id=campaign_id,
        campaign_conversation_id=campaign_conversation_id,
        call_note=call_note,
    )


def campaigns_factory(
    workspace_id: WorkspaceReference,
    campaign_name: str,
    created_by_name: str,
    assigne_name: str,
    assigne_id: UUID,
    dialing_number: str,
    calling_datacenter: str,
    campaign_status: str,
    call_recording_enabled: bool,
    voicemail_enabled: bool,
    voicemail_id: typing.Optional[UUID],
    cooloff_period_enabled: bool,
    cool_off_period: typing.Optional[int],
    call_attempts_enabled: bool,
    call_attempts_count: typing.Optional[int],
    call_attempts_gap: typing.Optional[int],
    call_script_enabled: bool,
    call_script_id: typing.Optional[UUID],
    contact_list_id: UUID,
    next_number_to_dial: str,
    is_archived: bool,
    dialing_number_id: UUID,
    callable_data: typing.Dict = None, # type: ignore
) -> Campaigns:
    return Campaigns(
        id_=uuid4(),
        workspace_id=workspace_id,
        campaign_name=campaign_name,
        assigne_name=assigne_name,
        assigne_id=assigne_id,
        dialing_number=dialing_number,
        calling_datacenter=calling_datacenter,
        campaign_status=campaign_status,
        call_recording_enabled=call_recording_enabled,
        voicemail_enabled=voicemail_enabled,
        voicemail_id=voicemail_id,
        cooloff_period_enabled=cooloff_period_enabled,
        cool_off_period=cool_off_period,
        call_attempts_enabled=call_attempts_enabled,
        call_attempts_count=call_attempts_count,
        call_attempts_gap=call_attempts_gap,
        call_script_enabled=call_script_enabled,
        call_script_id=call_script_id,
        contact_list_id=contact_list_id,
        next_number_to_dial=next_number_to_dial,
        is_archived=is_archived,
        created_by_name=created_by_name,
        dialing_number_id=dialing_number_id,
        callable_data=callable_data,
    )


def campaign_stats_factory(
    campaign_id: UUID,
    total_contacts: int,
    dialed_contacts: int,
    voicemail_drops: int,
    answered_calls: int,
    unanswered_calls: int,
    active_call_duration: int,
    campaign_duration: int,
) -> CampaignStats:
    return CampaignStats(
        id_=uuid4(),
        campaign_id=campaign_id,
        total_contacts=total_contacts,
        dialed_contacts=dialed_contacts,
        voicemail_drops=voicemail_drops,
        answered_calls=answered_calls,
        unanswered_calls=unanswered_calls,
        active_call_duration=active_call_duration,
        campaign_duration=campaign_duration,
    )
