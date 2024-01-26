import json
import typing
from krispcall.campaigns.domain import models as campaign_models
from krispcall.providers.queue_service.job_queue import JobQueue
from krispcall.twilio.utils import sub_client
from krispcall.konference import services
from krispcall.konference.adapters.provider import get_provider_details
from uuid import UUID
import dateutil
from krispcall.common.shortid import ShortId
from krispcall.konference.domain.models import (
    AgentReference,
    ConferenceStatus,
    ParticipantType,
)
from krispcall.twilio.krispcall_twilio import TwilioClient
from krispcall.konference.service_layer import views, abstracts
from krispcall.konference.service_layer.event_handlers import call_handlers
from krispcall.campaigns.service_layer import views as campaign_views
from krispcall.campaigns import services as camp_services
from redis import Redis


def get_conversation_status(participants):
    if not participants:
        return ConferenceStatus.failed

    for participant in participants:
        if participant.get("participant_type") == ParticipantType.agent:

            status = participant.get("status")
            return {
                "failed": ConferenceStatus.failed,
                "busy": ConferenceStatus.busy,
                "completed": ConferenceStatus.completed,
                "no_answer": ConferenceStatus.no_answer,
                "canceled": ConferenceStatus.cancelled,
            }.get(status, ConferenceStatus.failed)

    return ConferenceStatus.cancelled


async def handle_campaign_conversation_end(
    ctx,
    conversation: UUID,
    workspace: UUID,
    conference_friendly_name: UUID,
    campaign_id: UUID,
    is_reattempt: bool,
):
    db_conn = ctx["db"]
    twilio_client_ = ctx["twilio"]
    queue: JobQueue = ctx["queue"]
    settings = ctx["settings"]
    cache = Redis.from_url(settings.redis_settings)

    participants = await views.get_conversation_participants(
        conversation=conversation, db_conn=db_conn
    )

    campaign_conversation = await views.get_camaign_conversation(
        conversation_id=conversation, db_conn=db_conn
    )

    participants_stat = get_conversation_status(participants)

    """In case of geopermission not allowed we update failed status in campaign_conversation
       an if the campaign_conversation has status failed, busy, no_answer, and cancelled we don't update campaign_conversation status
    """
    if campaign_conversation.get("status") not in [
        ConferenceStatus.failed.value,
        ConferenceStatus.busy.value,
        ConferenceStatus.no_answer.value,
        ConferenceStatus.cancelled.value,
    ]:
        await services.update_campaign_conversation_status(
            status=participants_stat,
            conversation_id=conversation,
            db_conn=db_conn,
        )

    if participants_stat in [
        ConferenceStatus.failed,
        ConferenceStatus.busy,
        ConferenceStatus.no_answer,
        ConferenceStatus.cancelled,
    ]:
        await queue.enqueue_job(
            "update_campaign_calls",
            data=[campaign_id, False],  # type: ignore , False here to indicate call wasn't
            # answered
            queue_name="arq:pd_queue",
            defer_by_seconds=1,
        )
        return

    # TODO : These details can be fetched from cache
    details = await get_provider_details(
        workspace_id=ShortId.with_uuid(workspace),
    )

    sub_client_: TwilioClient = sub_client(
        obj=twilio_client_,
        details={
            "string_id": details.auth_id,
            "auth_token": details.auth_token,
            "api_key": details.api_key,
            "api_secret": details.api_secret,
        },
    )
    conference_resource = (
        await sub_client_.conference_resource.fetch_conference(
            friendly_name=ShortId.with_uuid(conference_friendly_name)
        )
    )
    if not "conferences" in conference_resource:
        raise Exception("Conferences not found for the given twi sid.")

    if not conference_resource.get("conferences"):
        raise Exception("Conference resource not found for the given id.")

    conference_duration = dateutil.parser.parse(  # type: ignore
        conference_resource.get("conferences")[0].get("date_updated")
    ) - dateutil.parser.parse(  # type: ignore
        conference_resource.get("conferences")[0].get("date_created")
    )

    failed_statuses = [ConferenceStatus.failed.value]
    campaign_status = campaign_conversation.get("status")
    is_not_failed_status = campaign_status not in failed_statuses

    conference_duration_in_seconds = (
        conference_duration.seconds
        if conference_duration and conference_duration.seconds is not None
        else 0
    )
    is_answered = is_not_failed_status

    await services.update_conversation_duration(
        conversation_id=conversation,
        duration=conference_duration.seconds,
        recording=False,
        db_conn=db_conn,
    )
    await queue.enqueue_job(
        "update_campaign_calls",
        data=[campaign_id, is_answered],  # type: ignore , True here to indicate call was answered
        queue_name="arq:pd_queue",
        defer_by_seconds=1,
    )

    await queue.enqueue_job(
        "update_campaign_duration",
        data=[campaign_id, conference_duration_in_seconds],  # type: ignore
        queue_name="arq:pd_queue",
        defer_by_seconds=1,
    )
    # clear the conversation data from cache
    cache.delete(ShortId.with_uuid(conversation))


async def hold_conversation_by_id(
    ctx, twi_sid: ShortId, workspace: UUID, hold: bool, client_call_sid: str
):
    twilio_client_: TwilioClient = ctx["twilio"]

    details = await get_provider_details(
        workspace_id=ShortId.with_uuid(workspace),
    )
    sub_client_: TwilioClient = sub_client(
        obj=twilio_client_,
        details={
            "string_id": details.auth_id,
            "auth_token": details.auth_token,
            "api_key": details.api_key,
            "api_secret": details.api_secret,
        },
    )

    response = await sub_client_.conference_resource.wait_participant_by_sid(
        conference_friendly_name=twi_sid,
        hold=hold,
        call_sid=client_call_sid,
    )
    print(response)


async def add_agent_to_conversation(
    ctx,
    conversation_data: abstracts.AddCampaignConversation,
    queue_data: abstracts.QueueData,
):
    db_conn = ctx["db"]
    settings = ctx["settings"]
    queue = ctx["queue"]
    cache = Redis.from_url(settings.redis_settings)
    twilio_client_: TwilioClient = ctx["twilio"]
    campaign = await campaign_views.get_campaign_by_id(
        campaign_id=queue_data.get("campaign_id"),
        db_conn=db_conn,
    )

    if campaign.get("campaign_status") in ["paused", "ended"]:
        print("Paused campaign didn't add agent")
        return

    workspace: UUID = queue_data.get("workspace")

    details = await get_provider_details(
        workspace_id=ShortId.with_uuid(workspace),
    )

    sub_client_: TwilioClient = sub_client(
        obj=twilio_client_,
        details={
            "string_id": details.auth_id,
            "auth_token": details.auth_token,
            "api_key": details.api_key,
            "api_secret": details.api_secret,
        },
    )
    camp_obj = (
        cache.get(ShortId.with_uuid(queue_data.get("campaign_id"))) or "{}"
    )
    camp_obj = json.loads(camp_obj)
    is_reattempt = (
        True if camp_obj.get("is_reattempt", "False") == str(True) else False
    )
    await call_handlers.add_agent(
        conversation_data=conversation_data,
        db_conn=db_conn,
        twilio_=sub_client_,
        workspace=workspace,
        dialing_number=queue_data.get("dialing_number"),
        dialing_number_id=queue_data.get("dialing_number_id"),
        cool_off_period_enabled=queue_data.get(
            "cool_off_period_enabled", False
        ),
        cool_off_period=queue_data.get("cool_off_period"),
        next_number_to_dial=queue_data.get("next_number_to_dial"),
        next_conversation_id=queue_data.get("next_conversation_id"),
        member=queue_data.get("member"),
        call_script_id=queue_data.get("call_script_id"),
        campaign_id=queue_data.get("campaign_id"),
        settings=settings,
        queue=queue,
        recording_enabled=queue_data.get("recording_enabled"),
        is_reattempt=is_reattempt,
    )

    # await camp_services.update_campaign_dialed_contacts(
    #     campaign_id=queue_data.get("campaign_id"),
    #     db_conn=db_conn,
    # )


async def queue_conversation(
    ctx, validated_data: typing.List[abstracts.AddCampaignConversationMsg]
):
    db_conn = ctx["db"]
    data: typing.List[abstracts.AddCampaignConversation] = [
        abstracts.AddCampaignConversation(
            id_=ShortId(d.id_).uuid(),
            twi_sid=ShortId(d.twi_sid).uuid(),
            status=d.status,
            created_by=ShortId(d.created_by).uuid(),
            sequence_number=d.sequence_number,
            contact_name=d.contact_name,
            contact_number=d.contact_number,
            recording_url=d.recording_url,
            initial_call=d.initial_call,
            recording_duration=d.recording_duration,
            campaign_id=ShortId(d.campaign_id).uuid(),
            reason_message=d.reason_message,
            reason_code=d.reason_code,
        )
        for d in validated_data
    ]
    await services.queue_conversations(validated_data=data, db_conn=db_conn)


async def add_participant_call(
    ctx, validated_data: abstracts.AddParticipantCallMsg
):
    db_conn = ctx["db"]
    data: abstracts.AddParticipantCall = abstracts.AddParticipantCall(
        id_=ShortId(validated_data.id_).uuid(),
        twi_sid=validated_data.twi_sid,
        status=validated_data.status,
        created_by=AgentReference(ShortId(validated_data.created_by).uuid()),
        participant_type=validated_data.participant_type,
        recording_url=validated_data.recording_url,
        recording_duration=validated_data.recording_duration,
        conversation_id=ShortId(validated_data.conversation_id).uuid(),
    )
    await services.add_participant_call(validated_data=data, db_conn=db_conn)


async def expire_cache(ctx, key: str):
    settings = ctx["settings"]
    cache = Redis.from_url(settings.redis_settings)
    cache.delete(key)
