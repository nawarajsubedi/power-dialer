""" Starts calls """
import json
import time
from typing import List
import typing
import uuid
import time
from krispcall.common.database.connection import DbConnection
from krispcall.common.utils.shortid import ShortId
from uuid import UUID, uuid4
from krispcall.common.utils.static_helpers import url_safe_encode

from krispcall.providers.queue_service.job_queue import JobQueue
from krispcall.common.app_settings.app_settings import Settings
from krispcall.konference.service_layer import abstracts, helpers, views
from krispcall.konference import services
from krispcall.konference.domain import models
from krispcall.campaigns.domain import models as campaign_models
from krispcall.campaigns.service_layer import views as campaign_views
from krispcall.campaigns import services as camp_services
from redis import Redis

from krispcall.twilio.twilio_client import TwilioClient


async def add_agent(
    conversation_data: abstracts.AddCampaignConversation,
    db_conn: DbConnection,
    settings: Settings,
    twilio_: TwilioClient,
    member: UUID,
    workspace: UUID,
    dialing_number: str,
    campaign_id: UUID,
    call_script_id: typing.Union[UUID, None],
    dialing_number_id: UUID,
    queue: JobQueue,
    cool_off_period_enabled: bool,
    cool_off_period: typing.Union[None, int],
    next_number_to_dial: typing.Union[str, None],
    next_conversation_id: typing.Union[None, UUID],
    is_reattempt: bool = False,
    recording_enabled: bool = False,
):
    cache = Redis.from_url(settings.redis_settings)

    (
        conversation_id,
        conference_sid,
        contact_name,
        contact_number,
        sequence_number,
    ) = (
        conversation_data.id_,
        conversation_data.twi_sid,
        conversation_data.contact_name,
        conversation_data.contact_number,
        conversation_data.sequence_number,
    )

    # encode and add data into callback string to be used in twilio callback
    # _data = f"{ShortId.with_uuid(workspace)}|{ShortId.with_uuid(campaign.id_)}|{conference_sid}id_"

    workspace_sid, camp_sid, conf_sid, conv_sid = (
        ShortId.with_uuid(workspace),
        ShortId.with_uuid(campaign_id),
        ShortId.with_uuid(conference_sid),
        ShortId.with_uuid(conversation_data.id_),
    )

    callback_data = url_safe_encode(
        string=f"{workspace_sid},{camp_sid},{conf_sid},{conv_sid},{0 if not is_reattempt else 1}"
    )

    campaign_conference = await twilio_.conference_resource.campaign_conference(
        conference_id=ShortId.with_uuid(conference_sid),
        callback_data=callback_data,
        auto_record=recording_enabled,
    )

    agent_callback_data = f"{workspace_sid}/{camp_sid}/{conf_sid}"

    agent_call = await twilio_.call_resource.campaign_add_participant(
        call_to=ShortId.with_uuid(member),
        call_from=dialing_number,
        callback_data=url_safe_encode(string=agent_callback_data),
        twiml=str(campaign_conference),
        params={
            "isCampaignCall": True,
            "campaignId": ShortId.with_uuid(campaign_id),
            "campaignConversationId": ShortId.with_uuid(conversation_id),
            "callScriptsId": None
            if not call_script_id
            else ShortId.with_uuid(call_script_id),
            "coolOffEnabled": cool_off_period_enabled,
            "coolOffPeriod": cool_off_period,
            "contact_number": contact_number,
            "contactName": contact_name,
            "channel_sid": ShortId.with_uuid(dialing_number_id),
            "nextQueue": next_number_to_dial,
            "sequenceNumber": sequence_number,
            "nextCampaignConversationId": None
            if not next_conversation_id
            else ShortId.with_uuid(next_conversation_id),
            "after_transfer": False,
            "isReattempt": is_reattempt,
            "recordingEnabled": recording_enabled,
        },
    )
    # queue all the conversations

    if "sid" not in agent_call:
        print("Failed response:: -> ")
        print(agent_call)
        raise Exception(
            "Agent couldn't be added to the call. Please contact support or check your campaign settings."
        )
    participant_call = abstracts.AddParticipantCallMsg(
        id_=ShortId.with_uuid(uuid4()),
        twi_sid=agent_call.get("sid"),
        status=models.TwilioCallStatus.queued.value,
        created_by=ShortId.with_uuid(member),
        participant_type=models.CallLegType.agent.value,
        recording_url=None,
        recording_duration=None,
        call_duration=None,
        conversation_id=ShortId.with_uuid(conversation_data.id_),
    )
    cache.set(participant_call.twi_sid, json.dumps(dict(participant_call)))
    await queue.enqueue_job(
        "add_participant_call",
        data=[participant_call],  # type: ignore
        queue_name="arq:pd_queue",
    )
    await queue.enqueue_job(
        "update_dialed_contacts",
        data=[campaign_id],  # type: ignore
        queue_name="arq:pd_queue",
    )


async def start_campaign_loop(
    campaign: campaign_models.Campaigns,
    sub_client: TwilioClient,
    db_conn: DbConnection,
    member: UUID,
    workspace: UUID,
    settings: Settings,
    cpass_user: typing.Dict,
    queue: JobQueue,
):
    """
    @params
    sub_client: Always assumes that sub_client instance is provided
    Will raise TwilioRestClientError with 403 if not
    only start campaign from the start because it is stateful
    """

    # get campaign contact list
    contact_list = await campaign_views.get_campaign_contact_dtl_list(
        contact_master_id=campaign.contact_list_id, db_conn=db_conn
    )

    # conversation data with all the campaign conversation is created here
    # because, this data needs to be sent to the frontend
    # for the campaign conference analytics page
    # we can reference the whole data with campagin id later on
    conversation_data: List[
        abstracts.AddCampaignConversationMsg
    ] = helpers.create_conversation_data(
        contact_list=contact_list,
        member=member,
        campaign_id=campaign.id_,
    )
    cache = Redis.from_url(settings.redis_settings)

    await queue.enqueue_job(
        "queue_conversation",
        data=[conversation_data],  # type: ignore
        queue_name="arq:pd_queue",
    )

    next_conversation_id = (
        None if len(conversation_data) < 2 else ShortId(conversation_data[1].id_).uuid()
    )
    next_number_to_dial = (
        None if len(conversation_data) < 2 else conversation_data[1].contact_number
    )

    # move the camp to the next step by adding agent
    d = conversation_data[0]
    camp_obj = {
        "status": "in_progress",
        "cpass_user": cpass_user,
        "next_number_to_dial": next_number_to_dial,
        "current_call_seq": conversation_data[0].sequence_number,
        "conversation_data": [dict(data) for data in conversation_data],
        "assignee_id": ShortId.with_uuid(member),
        "dialing_number": campaign.dialing_number,
        "dialing_number_id": ShortId.with_uuid(campaign.dialing_number_id),
        "cool_off_period": campaign.cool_off_period,
        "cooloff_period_enabled": campaign.cooloff_period_enabled,
        "call_script_id": None
        if not campaign.call_script_id
        else ShortId.with_uuid(campaign.call_script_id),
        "recording_enabled": campaign.call_recording_enabled,
    }
    cache.set(ShortId.with_uuid(campaign.id_), json.dumps(camp_obj))

    await add_agent(
        conversation_data=abstracts.AddCampaignConversation(
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
        ),
        member=member,
        db_conn=db_conn,
        workspace=workspace,
        twilio_=sub_client,
        campaign_id=campaign.id_,
        next_number_to_dial=next_number_to_dial,
        next_conversation_id=next_conversation_id,
        dialing_number=campaign.dialing_number,
        call_script_id=campaign.call_script_id,
        dialing_number_id=campaign.dialing_number_id,
        cool_off_period_enabled=campaign.cooloff_period_enabled,
        cool_off_period=campaign.cool_off_period,
        settings=settings,
        queue=queue,
        recording_enabled=campaign.call_recording_enabled,
    )

    # Now, we can start the first campaign conference


async def pause_campaign_loop(
    campaign: campaign_models.Campaigns,
    sub_client: TwilioClient,
    db_conn: DbConnection,
    member: UUID,
    workspace: UUID,
    settings: Settings,
    cpass_user: typing.Dict,
    queue: JobQueue,
):
    # pausing campaign loop is same as ending campaign loop but instead of
    # ending all the active conversations inqcluding ones in the queue
    # we only end ongoing and on_hold conversations
    await end_campaign_loop(
        campaign=campaign,
        sub_client=sub_client,
        db_conn=db_conn,
        member=member,
        workspace=workspace,
        st=["in_progress", "on_hold"],
        settings=settings,
        cpass_user=cpass_user,
        queue=queue,
    )


def replace_uuid_with_shortid(map_: typing.Dict):
    for k, v in map_:
        if isinstance(UUID, v):
            map_[k] = ShortId.with_uuid(v)
    return map_


async def resume_campaign_loop(
    campaign: campaign_models.Campaigns,
    sub_client: TwilioClient,
    db_conn: DbConnection,
    member: UUID,
    workspace: UUID,
    settings: Settings,
    cpass_user: typing.Dict,
    queue: JobQueue,
):
    # resuming campaign we don't need to do anything
    # special than starting campaign loop
    # except we need to get the next number to call for the campaign from the campaign object
    # and build the conversation data from the next number to call
    # TODO : Break this and into a queable task
    # along withh the participant leave
    # make more sensible and remove bad comments and duplication
    if not campaign.next_number_to_dial:
        raise Exception("No contact remaining to call")
    cache = Redis.from_url(settings.redis_settings)
    callable_data = await views.get_callable_data(
        campaign_id=campaign.id_,
        db_conn=db_conn,
        contact_number=campaign.next_number_to_dial,
        initial_call=True,
    )
    dialing_contact = callable_data[0]
    next_contact = None if len(callable_data) < 2 else callable_data[1]
    next_conversation_id = None if not next_contact else next_contact.get("id_")
    next_number_to_dial = (
        None if not next_contact else next_contact.get("contact_number")
    )

    conversation_data = abstracts.AddCampaignConversation(
        id_=dialing_contact.get("id_"),
        twi_sid=dialing_contact.get("twi_sid"),
        campaign_id=campaign.id_,
        contact_number=dialing_contact.get("contact_number"),
        sequence_number=dialing_contact.get("sequence_number"),
        status=models.ConferenceStatus.pending.value,
        contact_name=dialing_contact.get("contact_name"),
        recording_url=dialing_contact.get("recording_url"),
        recording_duration=dialing_contact.get("recording_duration"),
        created_by=campaign.assigne_id,
    )
    camp_obj = {
        "status": "in_progress",
        "cpass_user": cpass_user,
        "next_number_to_dial": next_number_to_dial,
        "current_call_seq": conversation_data.sequence_number,
        "conversation_data": [
            dict(abstracts.AddCampaignConversationMsg(**dict(data)))
            for data in callable_data
        ],
        "assignee_id": ShortId.with_uuid(member),
        "dialing_number": campaign.dialing_number,
        "dialing_number_id": ShortId.with_uuid(campaign.dialing_number_id),
        "cool_off_period": campaign.cool_off_period,
        "cooloff_period_enabled": campaign.cooloff_period_enabled,
        "call_script_id": None
        if not campaign.call_script_id
        else ShortId.with_uuid(campaign.call_script_id),
        "recording_enabled": campaign.call_recording_enabled,
    }

    cache.set(ShortId.with_uuid(campaign.id_), json.dumps(camp_obj))

    await add_agent(
        conversation_data=conversation_data,
        db_conn=db_conn,
        twilio_=sub_client,
        workspace=workspace,
        member=member,
        dialing_number=campaign.dialing_number,
        dialing_number_id=campaign.dialing_number_id,
        cool_off_period=campaign.cool_off_period,
        cool_off_period_enabled=campaign.cooloff_period_enabled,
        call_script_id=campaign.call_script_id,
        next_conversation_id=next_conversation_id,
        next_number_to_dial=next_number_to_dial,
        campaign_id=campaign.id_,
        settings=settings,
        queue=queue,
        recording_enabled=campaign.call_recording_enabled,
    )


async def reattempt_campaign_loop(
    campaign: campaign_models.Campaigns,
    sub_client: TwilioClient,
    db_conn: DbConnection,
    settings: Settings,
    member: UUID,
    workspace: UUID,
    cpass_user: typing.Dict,
    queue: JobQueue,
    st: typing.Union[typing.List[str], None] = None,
):
    # reattempt campaign loop is a special case of resume campaign loop
    # in reattempt we need to get all of the conversations which failed
    # or canceled
    # and get them into a new list
    # create new callable data
    # and do same thing as start campaign loop
    # afterwards.
    # but we set the initial_call to false
    # and current attempt to 1 instead of 0
    cache = Redis.from_url(settings.redis_settings)
    contact_list = await views.get_reattempt_list(
        campaign_id=campaign.id_, db_conn=db_conn
    )
    contact_list_len = await views.get_final_sequnce_number(
        campaign_id=campaign.id_, db_conn=db_conn
    )
    conversation_data: List[
        abstracts.AddCampaignConversationMsg
    ] = helpers.create_conversation_data(
        contact_list=contact_list,
        member=member,
        campaign_id=campaign.id_,
        reattempt=True,
        current_sequence_number=contact_list_len,
    )
    camp_obj = {
        "status": "in_progress",
        "is_reattempt": "True",
        "cpass_user": cpass_user,
        "next_number_to_dial": campaign.next_number_to_dial,
        "current_call_seq": conversation_data[0].sequence_number,
        "conversation_data": [dict(data) for data in conversation_data],
        "assignee_id": ShortId.with_uuid(member),
        "dialing_number": campaign.dialing_number,
        "dialing_number_id": ShortId.with_uuid(campaign.dialing_number_id),
        "cool_off_period": campaign.cool_off_period,
        "cooloff_period_enabled": campaign.cooloff_period_enabled,
        "call_script_id": None
        if not campaign.call_script_id
        else ShortId.with_uuid(campaign.call_script_id),
        "recording_enabled": campaign.call_recording_enabled,
    }
    cache.set(ShortId.with_uuid(campaign.id_), json.dumps(camp_obj))

    await queue.enqueue_job(
        "queue_conversation",
        data=[conversation_data],  # type: ignore
        queue_name="arq:pd_queue",
    )
    # conversations = await services.queue_conversations(
    #     validated_data=conversation_data,
    #     db_conn=db_conn,
    # )
    next_conversation_id = (
        None if len(conversation_data) < 2 else conversation_data[1].id_
    )

    next_number_to_dial = (
        None if len(conversation_data) < 2 else conversation_data[1].contact_number
    )
    d = conversation_data[0]
    await add_agent(
        conversation_data=abstracts.AddCampaignConversation(
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
        ),
        member=member,
        db_conn=db_conn,
        workspace=workspace,
        twilio_=sub_client,
        campaign_id=campaign.id_,
        next_number_to_dial=next_number_to_dial,
        next_conversation_id=None
        if not next_conversation_id
        else ShortId(next_conversation_id).uuid(),
        dialing_number=campaign.dialing_number,
        call_script_id=campaign.call_script_id,
        dialing_number_id=campaign.dialing_number_id,
        cool_off_period=campaign.cool_off_period,
        cool_off_period_enabled=campaign.cooloff_period_enabled,
        is_reattempt=True,
        settings=settings,
        queue=queue,
        recording_enabled=campaign.call_recording_enabled,
    )
    return campaign.id_


async def end_campaign_loop(
    campaign: campaign_models.Campaigns,
    sub_client: TwilioClient,
    db_conn: DbConnection,
    member: UUID,
    workspace: UUID,
    settings: Settings,
    cpass_user: typing.Dict,
    queue: JobQueue,
    st: typing.Union[None, typing.List[str]] = None,
):
    # get the active campagin conversations
    active_conversations = await views.get_active_campaign_conferences(
        st=st if st else ["in_progress"],
        campaign_id=campaign.id_,
        db_conn=db_conn,
    )
    # # if not active_conversations or active_conversations == []:
    # #     return
    # # we are only completing the campaign conversations from
    # # all of the callbacks for the ongoing calls which ended will
    # # be handled by callback handlers
    # # end all of the conference calls
    for conversation in active_conversations:
        try:
            await sub_client.conference_resource.terminate_by_name(
                ShortId.with_uuid(conversation.get("twi_sid"))
            )
        except Exception as e:
            print(e)

    # mark them complete in db
    return await services.complete_campaign_conversations(
        campaign_id=campaign.id_,
        st=st if st else ["in_progress", "in_queue", "pending", "on_hold"],
        db_conn=db_conn,
    )
