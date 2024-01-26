from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from krispcall.common.domain.commands import Command
from krispcall.campaigns.domain import models
import typing


@dataclass
class CampaignContactMastData(Command):
    name: str
    contact_count: int
    created_by_name: str
    is_contact_list_hidden: bool
    workspace_id: UUID
    is_archived: bool = False


@dataclass
class CampaignContactMastCommand(Command):
    contact_mast: models.CampaignContactListMast


@dataclass
class CampaignVoicemailCommand(Command):
    voicemail: models.CampaignVoicemail


@dataclass
class CampaignContactMastUpdateCount(CampaignContactMastCommand):
    contact_count: int
    modified_by: UUID


@dataclass
class RenameCampaignContactMaster(CampaignContactMastCommand):
    contact_list_id: UUID
    name: str
    modified_by: UUID


@dataclass
class AddCampaignContactDetail(Command):
    name: str
    number: str
    contact_list_id: UUID


@dataclass
class AddCampaignStat(Command):
    campaign_id: UUID
    total_contacts: int
    dialed_contacts: int
    voicemail_drops: int
    answered_calls: int
    unanswered_calls: int
    active_call_duration: int
    campaign_duration: int


@dataclass
class CampaignStatCommand(Command):
    stats: models.CampaignStats


@dataclass
class UpdateCampaignDuration(CampaignStatCommand):
    campaign_duration: int


@dataclass
class UpdateCampaignCallDuration(CampaignStatCommand):
    active_call_duration: int


@dataclass
class UpdateCampaignAnsweredCalls(CampaignStatCommand):
    answered_calls: int


@dataclass
class UpdateCampaignUnansweredCalls(CampaignStatCommand):
    unanswered_calls: int


@dataclass
class UpdateCampaignVoicemailDrops(CampaignStatCommand):
    voicemail_drops: int


@dataclass
class UpdateCampaignDialedContacts(CampaignStatCommand):
    dialed_contacts: int


@dataclass
class RenameCampaignVoiceMailCommand(CampaignVoicemailCommand):
    name: str


@dataclass
class DeleteCampaignVoiceMailCommand(CampaignVoicemailCommand):
    id: UUID


@dataclass
class UpdateDefaultVoiceMailCommand(CampaignVoicemailCommand):
    is_default: bool


@dataclass
class ArchiveCampaignContactMaster(CampaignContactMastCommand):
    contact_list_id: UUID
    is_archived: bool
    modified_by: UUID


@dataclass
class AddCampaignVoicemail(Command):
    workspace_id: UUID
    created_by_name: str
    recording_url: str
    recording_type: str
    source: typing.Optional[str]
    voice: typing.Optional[str]
    accent: typing.Optional[str]
    is_default: bool
    name: str


@dataclass
class CampaignCallScriptCommand(Command):
    callScript: models.CampaignCallScripts


@dataclass
class CampaignCallNoteCommand(Command):
    callNote: models.CampaignCallNotes


@dataclass
class AddCampaignCallScripts(Command):
    workspace_id: UUID
    is_default: bool
    created_by_name: str
    script_title: str
    description: str


@dataclass
class AddCampaignCallNotes(Command):
    call_note: str
    campaign_id: UUID
    campaign_conversation_id: UUID


@dataclass
class UpdateCampaignCallNotes(CampaignCallNoteCommand):
    call_note: str
    id: UUID


@dataclass
class UpdateCampaignNextToDial(Command):
    campaign: UUID
    id: UUID
    next_number_to_dial: str


@dataclass
class UpdateCampaignCallScriptCommand(CampaignCallScriptCommand):
    script_title: str
    description: str


@dataclass
class DeleteCampaignCallScriptCommand(CampaignCallScriptCommand):
    id: UUID


@dataclass
class UpdateDefaultCallScriptCommand(CampaignCallScriptCommand):
    is_default: bool


@dataclass
class AddCampaigns(Command):
    workspace_id: UUID
    campaign_name: str
    assigne_name: str
    assigne_id: UUID
    created_by_name: str
    dialing_number_id: UUID
    dialing_number: str
    calling_datacenter: str
    campaign_status: str
    voicemail_id: typing.Optional[UUID]
    cool_off_period: typing.Optional[int]
    call_attempts_enabled: bool
    call_attempts_count: typing.Optional[int]
    call_attempts_gap: typing.Optional[int]
    call_script_id: typing.Optional[UUID]
    contact_list_id: UUID
    next_number_to_dial: str
    is_archived: bool
    callable_data: typing.Dict = None
    call_recording_enabled: bool = False
    cooloff_period_enabled: bool = False
    voicemail_enabled: bool = False
    call_script_enabled: bool = False


@dataclass
class CampaignsCommand(Command):
    campaign: models.Campaigns


@dataclass
class ArchiveCampaignCommand(CampaignsCommand):
    is_archived: bool
    modified_by: UUID


@dataclass
class UpdateCampaignCommand(CampaignsCommand):
    id: UUID
    workspace_id: UUID
    campaign_name: str
    assigne_name: str
    assigne_id: UUID
    dialing_number: str
    created_by_name: str
    dialing_number_id: UUID
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
    is_archived: bool
    next_number_to_dial: str
    modified_by: UUID


@dataclass
class ControlCampaignCommand(CampaignsCommand):
    campaign: UUID
    campaign_status: str
    modified_by: UUID
