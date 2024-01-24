from __future__ import annotations
from distutils.command import upload
from enum import Enum, unique

from typing import Any, List, Optional, Union, Literal
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, root_validator

from krispcall.core.abstracts.shortid import ShortId
from krispcall.web.jsonapi.abstracts import (
    DataModel,
    ResourceModel,
    QueryModel,
    with_response,
)

from krispcall.web.constants import HTTP_SUCCESS_OK
from pydantic import validator


class CampaignContactListMastData(ResourceModel):
    id: ShortId
    name: str
    contact_count: int
    created_on: datetime


class CampaignContactListDetailData(ResourceModel):
    id: ShortId
    name: str
    number: str
    created_on: datetime


class AddCampaignContactDetail(DataModel):
    id: ShortId
    name: str
    number: str


class CampaignListData(ResourceModel):
    id: ShortId
    campaign_name: str
    assigne_name: str
    campaign_status: bool
    created_by: str
    created_on: datetime


class CampaignVoicemailListData(ResourceModel):
    id: ShortId
    name: str
    recording_type: str
    recording_url: str
    tts_source: str
    tts_voice: str
    tts_accent: str
    is_default: bool
    created_by: str
    created_on: datetime


class CampaignCallScriptsListData(ResourceModel):
    id: ShortId
    script_title: str
    description: str
    is_default: bool
    created_by: str
    created_on: datetime


class CampaignCallScriptsAtributeListData(ResourceModel):
    id: ShortId
    name: str
    descriptio: str


class DeleteCampaignContactDetail(DataModel):
    contacts: List[UUID]
    contact_list_id: ShortId


@with_response(CampaignContactListMastData)
def get_campaign_contact_list(response_factory, *, resource):
    data: List = []
    for record in resource:
        is_data_present = any(x["id"] == record["id"] for x in data)
        if not is_data_present:
            campaigns: List = []
            for eachRecord in resource:
                if record["id"] == eachRecord["id"]:
                    campaigns.append(eachRecord["campaign_name"])
            data.append(
                {
                    "id": record["id"],
                    "name": record["name"],
                    "created_on": record["created_on"],
                    "contact_count": record["contact_count"],
                    "created_by": record["created_by_name"],
                    "campaigns": [record["campaign_name"]]
                    if len(campaigns) == 0
                    else campaigns,
                }
            )
    contactList = [CampaignContactListMastData.construct(**c) for c in data]
    return {"status": HTTP_SUCCESS_OK, "error": None, "data": contactList}


@with_response(CampaignContactListDetailData)
def get_campaign_contact_dtl_list(response_factory, *, resource):
    data: List = []
    for record in resource:
        data.append(
            {
                "id": record["id"],
                "name": record["contact_name"],
                "number": record["contact_number"],
                "created_on": record["created_on"],
            }
        )
    contactList = [CampaignContactListDetailData.construct(**c) for c in data]
    return {"status": HTTP_SUCCESS_OK, "error": None, "data": contactList}


class UpdateCampaignContactList(DataModel):
    contact_list_id: ShortId
    action: str
    name: Optional[str]
    archive_contact_list: Optional[bool] = False


class UpdateCampaignVoicemail(DataModel):
    id: ShortId
    action: str
    rename_text: Optional[str]


class ArchiveCampaign(DataModel):
    id: ShortId
    is_archived: bool


@with_response(CampaignContactListMastData)
def campaign_contact_list_update(response_factory, *, resource):
    return response_factory(
        data=CampaignContactListMastData.construct(
            id=ShortId.with_uuid(resource.id_),
            name=resource.name,
        ),
        meta=None,
        status=HTTP_SUCCESS_OK,
    )


@with_response(AddCampaignContactDetail)
def campaign_add_contact_detail(response_factory, *, resource):
    return response_factory(
        data=AddCampaignContactDetail.construct(
            id=ShortId.with_uuid(resource.id_),
            name=resource.contact_name,
            number=resource.contact_number,
        ),
        meta=None,
        status=HTTP_SUCCESS_OK,
    )


class AddVoiceMailDrops(DataModel):
    recording_type: str
    created_by_name: str
    source: Optional[str]
    voice: Optional[str]
    accent: Optional[str]
    recording_url: str
    file: Any
    name: str

    @validator("source")
    def source_validation(cls, v):
        if len(v) > 350:
            raise ValueError("Source can be up to 350 characters")
        return v


@with_response(CampaignVoicemailListData)
def get_campaign_voicemails(response_factory, *, resource):
    data: List = []
    for record in resource:
        data.append(
            {
                "id": record["id"],
                "name": record["name"],
                "recording_type": record["recording_type"],
                "recording_url": record["recording_url"],
                "tts_source": record["tts_source"],
                "tts_voice": record["tts_gender"],
                "tts_accent": record["tts_accent"],
                "is_default": record["is_default"],
                "created_on": record["created_on"],
                "created_by": record["created_by_name"],
            }
        )
    voicemailList = [CampaignVoicemailListData.construct(**c) for c in data]
    return {"status": HTTP_SUCCESS_OK, "error": None, "data": voicemailList}


@with_response(CampaignListData)
def get_campaign(response_factory, *, resource):
    data: List = []
    for record in resource:
        data.append(
            {
                "id": record["id"],
                "workspace_id": record["workspace_id"],
                "assigne_id": record["assigne_id"],
                "dialing_number": record["dialing_number"],
                "dialing_number_id": record["dialing_number_id"],
                "calling_datacenter": record["calling_datacenter"],
                "call_recording_enabled": record["call_recording_enabled"],
                "voicemail_enabled": record["voicemail_enabled"],
                "voicemail_id": record["voicemail_id"],
                "cooloff_period_enabled": record["cooloff_period_enabled"],
                "cool_off_period": record["cool_off_period"],
                "call_attempts_enabled": record["call_attempts_enabled"],
                "call_attempts_count": record["call_attempts_count"],
                "call_attempts_gap": record["call_attempts_gap"],
                "is_contact_list_hidden": record[
                    "is_imported_contact_list_hidden"
                ],
                "call_script_enabled": record["call_script_enabled"],
                "is_archived": record["is_archived"],
                "call_script_id": record["call_script_id"],
                "contact_list_id": record["contact_list_id"],
                "next_number_to_dial": record["next_number_to_dial"],
                "assigne_name": record["assigne_name"],
                "campaign_name": record["campaign_name"],
                "campaign_status": record["campaign_status"],
                "created_on": record["created_on"],
                "contact_count": record["contact_count"],
                "created_by": record["created_by_name"],
                "contact_list_name": record["name"],
            }
        )
    campaignList = [CampaignListData.construct(**c) for c in data]
    return {"status": HTTP_SUCCESS_OK, "error": None, "data": campaignList}


class AddCallScripts(DataModel):
    created_by_name: str
    script_title: str
    description: str


class AddCampaignCallNote(DataModel):
    call_note: str
    campaign_id: ShortId
    campaign_conversation_id: ShortId


class UpdateCampaignCallNote(DataModel):
    call_note: str
    id: ShortId


class UpdateCampaignCallScripts(DataModel):
    id: ShortId
    action: str
    script_title: Optional[str]
    description: Optional[str]


@with_response(CampaignCallScriptsListData)
def get_campaign_callScripts(response_factory, *, resource):
    data: List = []
    for record in resource:
        data.append(
            {
                "id": record["id"],
                "script_title": record["script_title"],
                "description": record["description"],
                "is_default": record["is_default"],
                "created_on": record["created_on"],
                "created_by": record["created_by_name"],
            }
        )
    callScripts = [CampaignCallScriptsListData.construct(**c) for c in data]
    return {"status": HTTP_SUCCESS_OK, "error": None, "data": callScripts}


@with_response(CampaignCallScriptsListData)
def get_callScript_by_id(response_factory, *, record):
    callScripts = {
        "id": record.get("id"),
        "script_title": record.get("script_title"),
        "description": record.get("description"),
        "is_default": record.get("is_default"),
        "created_on": record.get("created_on"),
        "created_by": record.get("created_by_name"),
    }
    return {"status": HTTP_SUCCESS_OK, "error": None, "data": callScripts}


@with_response(CampaignCallScriptsAtributeListData)
def get_campaign_callScripts_attributes(response_factory, *, resource):
    data: List = []
    for record in resource:
        data.append(
            {
                "id": record["id"],
                "name": record["name"],
                "description": record["description"],
            }
        )
    callScripts = [
        CampaignCallScriptsAtributeListData.construct(**c) for c in data
    ]
    return {"status": HTTP_SUCCESS_OK, "error": None, "data": callScripts}


class CreateCampaign(DataModel):
    campaign_name: str
    skip_csv_upload: bool
    is_contact_list_hidden: Optional[bool]
    contact_list_id: Optional[ShortId]
    file: Optional[Any]
    assignee_id: ShortId
    assignee_name: str
    created_by_name: str
    dialing_number_id: ShortId
    dialing_number: str
    data_center: str
    is_call_recording_enabled: bool
    is_voicemail_enabled: Optional[bool]
    voice_mail_id: Optional[ShortId]
    is_cool_off_period_enabled: bool
    cool_off_period: Optional[int]
    is_attempts_per_call_enabled: bool
    call_attempt_count: Optional[int]
    call_attempt_gap: Optional[int]
    is_call_script_enabled: bool
    call_script_id: Optional[ShortId]


class UpdateCampaign(DataModel):
    id: ShortId
    campaign_name: str
    skip_csv_upload: bool
    is_contact_list_hidden: bool
    contact_list_id: Optional[ShortId]
    file: Optional[Any]
    assignee_id: ShortId
    dialing_number_id: ShortId
    assignee_name: str
    dialing_number: str
    data_center: str
    is_call_recording_enabled: bool
    is_voicemail_enabled: bool
    voice_mail_id: Optional[ShortId]
    is_cool_off_period_enabled: bool
    cool_off_period: Optional[int]
    is_attempts_per_call_enabled: bool
    call_attempt_count: Optional[int]
    call_attempt_gap: Optional[int]
    is_call_script_enabled: bool
    call_script_id: Optional[ShortId]
    contact_list_id: Optional[ShortId]
    created_by_name: str


@unique
class CampaignAction(Enum):
    START = "START"
    PAUSE = "PAUSE"
    END = "END"
    REATTEMPT = "REATTEMPT"
    RESUME = "RESUME"


# start -> campaign loop is started, can
# only be triggered from active. --> inprogress after start is called
# pause -> can be done to inprogress campaign
# end -> can be done to inprgoress , paused campaign


class SkipCampaignConversation(DataModel):
    conversation_sid: UUID
    campaign_id: UUID


class CampaignDetailsInput(DataModel):
    id: UUID


class CampaignVoicemailInput(DataModel):
    voicemail_id: UUID


class CampaignCallScriptInput(DataModel):
    callscript_id: UUID


class VoicemailDropInput(DataModel):
    conversation_id: UUID
    campaign_id: UUID


class HoldCampaignConversation(DataModel):
    conversation_sid: UUID
    hold: bool


class RecordAction(Enum):
    RESUME = "RESUME"
    STOP = "STOP"
    PAUSE = "PAUSE"


class RecordCampaignConversation(DataModel):
    conversation_sid: UUID
    action: RecordAction


class ControlCampaign(DataModel):
    """Form data for control campaign
    mutation"""

    id: ShortId
    action: CampaignAction


class ConversationType(Enum):
    INTIAL = "INITIAL"
    REATTEMPT = "REATTEMPT"


class SearchParams(QueryModel):
    columns: List[str]
    value: str


class CampPaginationParams(QueryModel):
    first: int = None
    after: datetime = None
    after_with: Optional[datetime]
    last: int = None
    before: datetime = None
    before_with: Optional[datetime]
    search: Optional[SearchParams]
    order: Literal["asc", "desc"] = Field("asc")

    @root_validator
    def check_valid_pagination(cls, values):
        first, after, after_with = (
            values.get("first"),
            values.get("after"),
            values.get("after_with"),
        )
        last, before, before_with = (
            values.get("last"),
            values.get("before"),
            values.get("before_with"),
        )

        forward = first or after or after_with
        backward = last or before or before_with

        if forward and backward:
            raise ValueError("Paging can't be forward and backward")
        elif forward or backward:
            return values
        else:
            raise ValueError("Invalid Paging Params")


class Edges(ResourceModel):
    cursor: Optional[datetime]
    node: Optional[Any]


class PageInfo(BaseModel):
    start_cursor: Optional[datetime]
    end_cursor: Optional[datetime]
    has_next_page: Optional[bool]
    has_previous_page: Optional[bool]
    total_count: Optional[int]


class PaginatedResource(ResourceModel):
    page_info: Optional[PageInfo]
    edges: Optional[List[Edges]]


@with_response(PaginatedResource)
def create_paginated_response(response_model, *, resource: PaginatedResource):
    return response_model(data=resource, meta=None, status=200)


class CampaignAnalyticsInput(DataModel):
    campaign_id: UUID
    conversation_type: Optional[ConversationType] = ConversationType.INTIAL


class CampaignAnalyticsData(ResourceModel):
    conversation_id: UUID
    status: str
    contact_name: str
    contact_number: str


@with_response(CampaignAnalyticsData)
def get_campaign_analytics(response_factory, *, resource):
    return {
        "status": HTTP_SUCCESS_OK,
        "error": None,
        "data": [
            {
                "conversationId": record.get("id"),
                "status": record.get("status"),
                "contactName": record.get("contact_name"),
                "contactNumber": record.get("contact_number"),
                "recordingDuration": record.get("recording_duration"),
                "callDuration": record.get("call_duration"),
                "recordingUrl": record.get("recording_url"),
                "callStartTime": record.get("created_at"),
            }
            for record in resource
        ],
    }


class CampaignStatsData(ResourceModel):
    campaign_id: UUID
    total_contacts: int
    dialed_contacts: int
    voicemail_drops: int
    answered_calls: int
    unanswered_calls: int
    active_call_duration: int
    campaign_duration: int


@with_response(CampaignStatsData)
def get_campaign_stats(response_factory, *, resource):
    # Todo revisit
    data = (
        {}
        if not resource
        else {
            "campaign_id": resource.get("campaign_id"),
            "total_contacts": resource.get("total_contacts"),
            "dialed_contacts": resource.get("dialed_contacts")
            if resource.get("total_contacts") > resource.get("total_contacts")
            else resource.get("total_contacts"),
            "voicemail_drops": 2,
            "answered_calls": resource.get("answered_calls"),
            "unanswered_calls": resource.get("unanswered_calls"),
            "active_call_duration": resource.get("active_call_duration"),
            "campaign_duration": resource.get("active_call_duration")
            + (
                15
                * (
                    resource.get("answered_calls")
                    + resource.get("unanswered_calls")
                )
            ),
        }
    )

    return {"status": HTTP_SUCCESS_OK, "error": None, "data": data}


class CampaignNote(ResourceModel):
    id: UUID
    call_note: str
    created_at: datetime


@with_response(CampaignNote)
def get_campaign_note(response_factory, *, resource):
    return {
        "status": HTTP_SUCCESS_OK,
        "error": None,
        "data": {
            "call_note": resource.get("call_note"),
            "id": resource.get("id"),
            "created_at": resource.get("created_at"),
        },
    }


def get_campaign_callscript(resource):
    return {
        "status": HTTP_SUCCESS_OK,
        "error": None,
        "data": {
            "id": resource.get("id"),
            "script_title": resource.get("script_title"),
            "description": resource.get("description"),
        },
    }


def get_campaign_voicemail(resource):
    return {
        "status": HTTP_SUCCESS_OK,
        "error": None,
        "data": {
            "id": resource.get("id"),
            "name": resource.get("name"),
            "recording_type": resource.get("recording_type"),
            "recording_url": resource.get("recording_url"),
        },
    }


class CampaignDetails(ResourceModel):
    id: UUID
    workspace_id: UUID
    created_by_name: str
    campaign_name: str
    assignee_name: str
    assignee_id: UUID
    dialing_number: str
    dialing_number_id: UUID
    campaign_status: str
    call_recording_enabled: bool
    call_script_enabled: bool
    call_script_id: UUID
    voicemail_id: UUID
    cooloff_period_enabled: bool
    voicemail_enabled: bool
    calling_datacenter: str
    is_archived: bool
    created_on: datetime
    contact_count: int


@with_response(CampaignDetails)
def get_campaign_details(response_factory, *, resource):
    return {
        "status": HTTP_SUCCESS_OK,
        "error": None,
        "data": resource,
    }


class VoicemailDropResource(ResourceModel):
    conversation_id: UUID
    status: str


@with_response(VoicemailDropResource)
def get_voicemail_drop(response_factory, *, resource):
    return {
        "status": HTTP_SUCCESS_OK,
        "error": None,
        "data": {
            "conversation_id": resource.get("conversation_id"),
            "status": resource.get("status"),
        },
    }
