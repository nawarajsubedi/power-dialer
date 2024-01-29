import copy
import json
import typing
from krispcall.common.utils.static_helpers import url_safe_encode
from krispcall.konference.billing.constant import CHARGE_START_CALL_TIME
from redis import Redis
from uuid import UUID, uuid4
from typing import List, Literal, Union
from starlette.requests import Request

from krispcall.konference.billing.models import CampaignOutboundCallRequest
from krispcall.konference.billing.billing_task_queue import (
    process_billing_transaction,
)

from krispcall.common.utils.shortid import ShortId

from krispcall.twilio.errorHelper import handle_call_failed
from krispcall.twilio.eventHandler import TwilioEventHandler
from krispcall.common.database.connection import DbConnection
from krispcall.providers.queue_service.job_queue import JobQueue
from krispcall.common.app_settings.app_settings import Settings
from krispcall.konference.service_layer.abstracts import (
    TwilioPSTNCallback,
    TwilioAgentCallback,
)

from krispcall.twilio.utils import sub_client
from krispcall.konference.adapters.provider import (
    get_plan_subscription,
    get_provider_details,
)
from krispcall.konference.service_layer import abstracts
from krispcall.konference.service_layer import unit_of_work
from krispcall.konference.domain import models
from krispcall.konference.service_layer import commands, views
from krispcall.konference.service_layer import handlers

from krispcall.campaigns.service_layer import views as campaign_views
from krispcall.campaigns import services as camp_services
from krispcall.konference.service_layer.event_handlers import call_handlers
from krispcall.campaigns.domain import models as campaign_models
from krispcall.twilio.twilio_client import TwilioClient
from krispcall.konference.billing.enums import (
    BillingTypeEnum,
    ConferencParticipantEnum,
)
from redis import Redis
from starlette.requests import Request
from uuid import UUID


async def add_campaign_conversation(
    validated_data: abstracts.AddCampaignConversation, db_conn: DbConnection
) -> models.CampaignConversation:
    cmd = commands.AddCampaignConversationCommand(**validated_data.dict())
    async with unit_of_work.CampaignConversationSqlUnitOfWork(db_conn) as uow:
        campaign_conversation = handlers.add_campaign_conversation(cmd)
        campaign_conversation = await uow.repository.add(campaign_conversation)
    return campaign_conversation


async def queue_conversations(
    validated_data: List[abstracts.AddCampaignConversation],
    db_conn: DbConnection,
) -> List[models.CampaignConversation]:
    conversations = [
        handlers.add_campaign_conversation(
            commands.AddCampaignConversationCommand(**data.dict())
        )
        for data in validated_data
    ]
    async with unit_of_work.CampaignConversationSqlUnitOfWork(db_conn) as uow:
        conversations = await uow.repository.bulk_add(conversations)
        return conversations


async def update_recording_info(
    conversation: UUID,
    recording_url: str,
    recording_duration: int,
    db_conn: DbConnection,
):
    async with unit_of_work.CampaignConversationSqlUnitOfWork(db_conn) as uow:
        await uow.repository.update_recording_info(  # type: ignore
            conversation, recording_url, recording_duration
        )


async def update_conversation_duration(
    conversation_id: UUID,
    duration: int,
    recording: bool,
    db_conn: DbConnection,
):
    async with unit_of_work.CampaignConversationSqlUnitOfWork(db_conn) as uow:
        campaign_conversation = await uow.repository.get(
            conversation_id=conversation_id
        )
        campaign_conversation = handlers.update_conversation_duration(
            duration=duration, model=campaign_conversation
        )
        return await uow.repository.update_call_duration(campaign_conversation)


async def update_campaign_conversation_status(
    status: models.ConferenceStatus,
    conversation_id: UUID,
    db_conn: DbConnection,
):
    cmd = commands.UpdateCampaignConversationStatusCommand(
        id=conversation_id, status=status
    )
    async with unit_of_work.CampaignConversationSqlUnitOfWork(db_conn) as uow:
        campaign_conversation = await uow.repository.get(
            conversation_id=conversation_id
        )
        campaign_conversation = handlers.update_campaign_status(
            cmd, campaign_conversation
        )
        await uow.repository.update_conversation_status(campaign_conversation)
        return campaign_conversation


async def update_campaign_conversation_status_with_reason(
    status: models.ConferenceStatus,
    conversation_id: UUID,
    db_conn: DbConnection,
    reason_code: int = None, # type: ignore
    reason_message: str = None, # type: ignore
):
    cmd = commands.UpdateCampaignConversationStatusCommand(
        id=conversation_id,
        status=status,
        reason_code=reason_code,
        reason_message=reason_message,
    )
    async with unit_of_work.CampaignConversationSqlUnitOfWork(db_conn) as uow:
        campaign_conversation = await uow.repository.get(
            conversation_id=conversation_id
        )
        campaign_conversation = (
            handlers.update_conversation_status_with_reason(
                cmd, campaign_conversation
            )
        )
        await uow.repository.update_conversation_status_with_reason(
            campaign_conversation
        )

    cmd = commands.UpdateCampaignParticipantCommand(
        id=conversation_id, status=status
    )

    async with unit_of_work.ParticipantCallSqlUnitOfWork(db_conn) as uow:
        campaign_participant = await uow.repository.get(
            conversation_id=conversation_id
        )
        campaign_participant = handlers.update_campaign_participant_status(
            cmd, campaign_participant
        )
        await uow.repository.update_call_status(
            campaign_participant, conversation_id
        )
        return campaign_participant


async def complete_campaign_conversations(
    campaign_id: UUID, st: List[str], db_conn: DbConnection
):
    async with unit_of_work.CampaignConversationSqlUnitOfWork(db_conn) as uow:
        await uow.repository.bulk_complete(campaign_id, st)
    return NotImplemented


async def complete_campaign_conversation(
    conversations: List[UUID], db_conn: DbConnection
):
    for conversation in conversations:
        try:
            await update_campaign_conversation_status(
                status=models.ConferenceStatus.completed.value,  # type: ignore
                conversation_id=conversation,
                db_conn=db_conn,
            )
        except Exception as e:
            print(e)


async def update_campaign_conversation_notes(
    campaign_call_note_id: UUID, id: UUID, db_conn: DbConnection
):
    cmd = commands.UpdateCampaignConversationNoteCommand(campaign_call_note_id)
    async with unit_of_work.CampaignConversationSqlUnitOfWork(db_conn) as uow:
        model: models.CampaignConversation = await uow.repository.get(conversation_id=id)  # type: ignore
        campaign_conversation = handlers.update_campaign_note(cmd, model)
        campaign_conversation = await uow.repository.update_call_note(  # type: ignore
            campaign_conversation
        )


async def add_participant_call(
    validated_data: abstracts.AddParticipantCall, db_conn: DbConnection
) -> models.ParticipantCall:
    cmd = commands.AddCampaignParticipantCommand(**validated_data.dict())
    async with unit_of_work.ParticipantCallSqlUnitOfWork(db_conn) as uow:
        participant_call = handlers.add_participant_call(cmd)
        participant_call = await uow.repository.add(participant_call)
    return participant_call


async def handle_conference_event(
    validated_data: abstracts.ConferenceParticipantEvent,
    request: Request,
    workspace: UUID,
    campaign_id: UUID,
    conference_friendly_name: UUID,
    conversation: UUID,
    is_reattempt: bool,
    camp_obj: typing.Dict,
    cache: Redis,
):
    # check if the event is participant join
    if (
        validated_data.status_callback_event
        == abstracts.ConferenceEvent.participant_join
    ):
        # Start charging to customer after participant join and sequence number 1
        if int(validated_data.sequence_number) == 1:
            db_conn: DbConnection = request.app.state.db
            queue: JobQueue = (
                request.app.state.queue
            )  # JobQueue(redis_settings=request.app.state.settings.redis_settings)
            twilio_client: TwilioClient = request.app.state.twilio

            campaign_call_params = CampaignOutboundCallRequest(
                workspace_id=workspace,# type: ignore
                call_sid=validated_data.call_sid,
                child_call_sid=validated_data.call_sid,
                parent_call_sid=validated_data.call_sid,
                conference_sid=validated_data.conference_sid,
                from_=camp_obj.get("dialing_number"),# type: ignore
                to=camp_obj.get("conversation_data")[0]["contact_number"],# type: ignore
                campaign_id=campaign_id,# type: ignore
                conversation_id=camp_obj.get("conversation_data")[0]["id_"],# type: ignore
                conference_friendly_name=conference_friendly_name,# type: ignore
                remarks="",
                total_participants=ConferencParticipantEnum.DEFAULT_TOTAL_PARTICIPANTS,
                # Each call should be charged sip and conference charge amount
                billing_types=[
                    BillingTypeEnum.SIP_CHARGE,
                    BillingTypeEnum.CONFERENCE_CHARGE,
                ],
            )

            billing_response = await process_billing_transaction(
                campaign_call_params,
                cache,
                queue,
                twilio_client,
                charge_call_back_time=CHARGE_START_CALL_TIME,  # For the first time charge job schedule should run after CHARGE_START_CALL_TIME
                # And then it should run after every CHARGE_CALL_BACK_TIME
            )

            if (
                billing_response.is_sufficient_credit
                or not billing_response.is_call_inprogress
            ):
                print(
                    "Ending call due to insufficient credit/call is not inprogress"
                )
                await update_campaign_conversation_status(
                    status=models.ConferenceStatus.completed,
                    conversation_id=conversation,
                    db_conn=db_conn,
                )

        await handle_participant_join(
            validated_data=validated_data,
            request=request,
            workspace=workspace,
            campaign_id=campaign_id,
            conversation_sid=conference_friendly_name,
            conversation_id=conversation,
            is_reattempt=is_reattempt,
            camp_obj=camp_obj,
            cache=cache,
        )
    elif (
        validated_data.status_callback_event
        == abstracts.ConferenceEvent.participant_leave
    ):
        await handle_participant_leave(
            validated_data=validated_data,
            request=request,
            workspace=workspace,
            campaign_id=campaign_id,
            conversation_sid=conference_friendly_name,
            is_reattempt=is_reattempt,
            cache=cache,
            camp_obj=camp_obj,
        )
    elif (
        validated_data.status_callback_event
        == abstracts.ConferenceEvent.conference_end
    ):
        await request.app.state.queue.enqueue_job(
            "handle_campaign_conversation_end",
            [
                conversation,
                workspace,
                conference_friendly_name,
                campaign_id,
                is_reattempt,
            ],
            queue_name="arq:pd_queue",
            defer_by_seconds=1,
        )


async def handle_participant_leave(
    validated_data: abstracts.ConferenceParticipantEvent,
    request: Request,
    workspace: UUID,
    campaign_id: UUID,
    conversation_sid: UUID,
    is_reattempt: bool,
    camp_obj: typing.Dict,
    cache: Redis,
):
    # import pdb

    # pdb.set_trace()

    queue = request.app.state.queue
    participant_call_resource = cache.get(validated_data.call_sid)
    if not participant_call_resource:
        raise Exception("Participant call not found in cache!")
    participant_call_resource = json.loads(participant_call_resource) # type: ignore
    # participant_call_resource = await views.get_participant_call_by_twi_sid(
    #     validated_data.call_sid,
    #     request.app.state.db,
    # )
    participant_call_type = participant_call_resource.get("participant_type")
    details = camp_obj.get("cpass_user")
    # details = await get_provider_details(
    #     workspace_id=ShortId.with_uuid(workspace),
    # )
    sub_client_: TwilioClient = sub_client(
        obj=copy.copy(request.app.state.twilio),
        details=details,
    )
    if participant_call_type != "agent":
        print("Client call left - ending conference")
        try:
            await sub_client_.conference_resource.terminate_by_name(
                ShortId.with_uuid(conversation_sid),
            )
        except Exception as e:
            print(e)
            raise e
        return
    conversations = camp_obj.get("conversation_data")

    if not conversations:
        raise Exception("Conversations not found in cache!")

    campaign_conversation = (
        item
        for item in conversations
        if item["twi_sid"] == ShortId.with_uuid(conversation_sid)
    )
    campaign_conversation = next(campaign_conversation, None)
    if not campaign_conversation:
        raise Exception("Conversation not found!")

    # campaign_conversation = await views.get_campaign_conference_by_twi_sid(
    #     conversation_sid, request.app.state.db
    # )

    # fetch campaigin details
    # campaign = await campaign_views.get_campaign_by_id(
    #     campaign_id=campaign_id,
    #     db_conn=request.app.state.db,
    # )
    if camp_obj.get("status") in ["paused", "ended"]:
        # This means campaign has ended.
        return
    # if not campaign and campaign.get("campaign_status") not in [
    #     "paused",
    #     "ended",
    # ]:
    #     return

    next_number_to_dial = camp_obj.get("next_number_to_dial")
    print("The next number to dial is", next_number_to_dial)

    if (
        campaign_conversation.get("contact_number") == next_number_to_dial
        or not next_number_to_dial
    ):
        # If there is no next number to dial end the conference
        try:
            await sub_client_.conference_resource.terminate_by_name(
                ShortId.with_uuid(conversation_sid),
            )
        except Exception as e:
            print(e)
        # update campaign status in the cache to dialing_completed
        # print("Campaign Reached the end of dialing:: ->")
        camp_obj.update({"status": "dialing_completed"})
        cache.set(ShortId.with_uuid(campaign_id), json.dumps(camp_obj))
        await queue.enqueue_job(
            "end_campaign",
            data=[campaign_id],
            queue_name="arq:pd_queue",
            defer_by_seconds=60,
        )

        return

    # use the next number to dial to get the next_contact
    dialing_contact = next(
        (
            item
            for item in conversations
            if item.get("contact_number") == next_number_to_dial
        )
    )
    if not dialing_contact:
        raise Exception("Current number to dial not found!")
    next_contact = next(
        (
            item
            for item in conversations
            if item.get("sequence_number")
            == dialing_contact.get("sequence_number") + 1
        ),
        None,
    )
    # get the provider details from the grpc adapter
    # mark the current conference as complete
    try:
        await sub_client_.conference_resource.terminate_by_name(
            ShortId.with_uuid(conversation_sid),
        )
        # TODO : Send complete conversation to the queue
        # await complete_campaign_conversation(
        #     conversations=[conversation_sid], db_conn=request.app.state.db
        # )
    except Exception as e:
        print(e)

    # Start the process for the next contact

    conversation_data = abstracts.AddCampaignConversation(
        id_=ShortId(dialing_contact.get("id_")).uuid(),
        twi_sid=ShortId(dialing_contact.get("twi_sid")).uuid(),
        campaign_id=campaign_id,
        contact_number=dialing_contact.get("contact_number"),
        sequence_number=dialing_contact.get("sequence_number"),
        status=models.ConferenceStatus.pending.value,
        contact_name=dialing_contact.get("contact_name"),
        recording_url=dialing_contact.get("recording_url"),
        recording_duration=dialing_contact.get("recording_duration"),
        created_by=ShortId(camp_obj.get("assignee_id")).uuid(), # type: ignore
    )

    queue_data: abstracts.QueueData = dict(
        workspace=workspace,
        dialing_number=camp_obj.get("dialing_number"),
        dialing_number_id=ShortId(camp_obj.get("dialing_number_id")).uuid(),# type: ignore
        cool_off_period_enabled=camp_obj.get("cooloff_period_enabled"),
        cool_off_period=camp_obj.get("cool_off_period"),
        next_number_to_dial=None
        if not next_contact
        else next_contact.get("contact_number"),
        next_conversation_id=None
        if not next_contact
        else ShortId(next_contact.get("id_")).uuid(),
        member=ShortId(camp_obj.get("assignee_id")).uuid(),# type: ignore
        call_script_id=None
        if not camp_obj.get("call_script_id")
        else ShortId(camp_obj.get("call_script_id")).uuid(), # type: ignore
        campaign_id=campaign_id,
        is_reattempt=is_reattempt,
        recording_enabled=camp_obj.get("recording_enabled", False),
    )  # type: ignore
    await queue.enqueue_job(
        "add_agent_to_conversation",
        [conversation_data, queue_data],
        defer_by_seconds=8,
        queue_name="arq:pd_queue",
    )


async def handle_participant_join(
    validated_data: abstracts.ConferenceParticipantEvent,
    request: Request,
    workspace: UUID,
    campaign_id: UUID,
    conversation_sid: UUID,
    conversation_id: UUID,
    is_reattempt: bool,
    camp_obj: typing.Dict,
    cache: Redis,
):
    # fetch the campaign details
    # campaign = await campaign_views.get_campaign_by_id(
    #     campaign_id=campaign_id,
    #     db_conn=request.app.state.db,
    # )
    db_conn = request.app.state.db
    queue = JobQueue(redis_settings=request.app.state.settings.redis_settings)
    await queue.connect()
    if camp_obj.get("status") in ["paused", "ended"]:
        print("CAMPAIGN IS EITHER ENDED OR PAUSED")
        return

    conversations = camp_obj.get("conversation_data")
    if not conversations:
        raise Exception("Campaign doesn't have any data in memory!")

    next_to_dial = camp_obj.get("next_to_dial")
    campaign_conversation = (
        item
        for item in conversations
        if item["twi_sid"] == ShortId.with_uuid(conversation_sid)
    )

    campaign_conversation = next(campaign_conversation, None)
    if not campaign_conversation:
        raise Exception("Invalid campaign_conversation ID!")

    # campaign_conversation = await views.get_campaign_conference_by_twi_sid(
    #     conversation_sid, request.app.state.db
    # )
    campaign_sequence_number = camp_obj.get("current_call_seq", 0)

    current_contact = campaign_conversation.get("contact_number")

    # Create Twilio Sub client for the workspace
    details = camp_obj.get("cpass_user")
    sub_client_: TwilioClient = sub_client(
        obj=copy.copy(request.app.state.twilio),
        details=details,
    )

    if not current_contact:
        # End campaign if reattempt
        # is true and there is no next contact -> Conference shouldn't reach here unless
        # there is some error
        await sub_client_.conference_resource.terminate_by_name(
            ShortId.with_uuid(conversation_sid),
        )
        raise Exception("Current contact not found. Doing nothing!")

    next_to_dial = (
        item
        for item in conversations
        if item["sequence_number"]
        == campaign_conversation.get("sequence_number") + 1
    )
    next_to_dial = next(next_to_dial, None)
    if next_to_dial:
        camp_obj.update(
            {
                "next_number_to_dial": next_to_dial.get("contact_number"),
                "current_call_seq": campaign_sequence_number + 1,
            }
        )
        cache.set(ShortId.with_uuid(campaign_id), json.dumps(camp_obj))

        await queue.enqueue_job(
            "update_next_number_to_dial",
            data=[
                campaign_id,
                next_to_dial.get("contact_number"),
            ],  # type: ignore
            queue_name="arq:pd_queue",
        )

    participant_call_resource = cache.get(validated_data.call_sid)

    if not participant_call_resource:
        await sub_client_.conference_resource.terminate_by_name(
            ShortId.with_uuid(conversation_sid),
        )
        raise Exception("Participant call not found saved in cache!")

    participant_call_resource = json.loads(participant_call_resource) # type: ignore

    if (
        participant_call_resource.get("participant_type")
        == models.ParticipantType.agent.value
        and int(validated_data.sequence_number) == 1
    ):
        # Add next dialing number of the campaign as the
        # participant to the conference
        # if sequence number is 1, then the agent is the first participant
        # we add the first customer to the conference
        # this call will send callback events to
        # event_handlers_client handler endpoint
        # which will handle the events
        # client_callback_data = f"{}"
        client_callback_data = f"{ShortId.with_uuid(workspace)},{ShortId.with_uuid(campaign_id)},{ShortId.with_uuid(conversation_sid)},{participant_call_resource.get('conversation_id')}"

        customer_call = (
            await sub_client_.conference_resource.add_campaign_external_number(
                conference_sid=validated_data.conference_sid,
                number=current_contact,
                from_=camp_obj.get("dialing_number"),  # type: ignore
                callback_data=url_safe_encode(client_callback_data),
            )
        )

        if not "call_sid" in customer_call or not customer_call.get(
            "call_sid"
        ):
            reason_code = customer_call.get("reason_code")
            reason_message = handle_call_failed(int(reason_code)) # type: ignore

            await send_event_to_client(
                call_sid=validated_data.call_sid,
                campaign_id=campaign_id,  # type: ignore
                conversation_id=conversation_id, # type: ignore
                cache=cache,
                db_conn=db_conn,
                twilio_client=request.app.state.twilio,
                message=reason_message, # type: ignore
            )

            await update_campaign_conversation_status_with_reason(
                status=models.TwilioCallStatus.failed, # type: ignore
                conversation_id=conversation_id,
                db_conn=db_conn,
                reason_code=reason_code, # type: ignore
                reason_message=reason_message, # type: ignore
            )
            await sub_client_.conference_resource.terminate_by_name(
                ShortId.with_uuid(conversation_sid),
            )
            return

        if "call_sid" in customer_call:
            conversation_obj = {
                "client": customer_call.get("call_sid"),
                "client_status": "initiated",
            }
            cache.set(
                campaign_conversation.get("id_"), json.dumps(conversation_obj)
            )
            data = abstracts.AddParticipantCallMsg(
                id_=ShortId.with_uuid(uuid4()),
                twi_sid=customer_call.get("call_sid"),
                status=models.TwilioCallStatus.queued.value,
                created_by=camp_obj.get("assignee_id"),
                participant_type=models.CallLegType.customer.value,
                recording_url=None,
                recording_duration=None,
                call_duration=None,
                conversation_id=campaign_conversation.get("id_"),
            )
            # TODO : Fire a queue to save this to database
            cache.set(data.twi_sid, json.dumps(dict(data)))
            await queue.enqueue_job(
                "add_participant_call",
                data=[data],  # type: ignore
                queue_name="arq:pd_queue",
            )
    return


async def send_event_to_client(
    call_sid: str,
    campaign_id: str,
    conversation_id: str,
    message: str,
    twilio_client: TwilioClient,
    cache,
    db_conn,
):
    values = cache.get(ShortId.with_uuid(campaign_id)) or {} # type: ignore
    camp_obj = json.loads(values) # type: ignore
    subaccount_credentials = camp_obj.get("cpass_user")

    participants = await views.get_conversation_participants(
        conversation=conversation_id, db_conn=db_conn # type: ignore
    )

    twilio_event_handler = TwilioEventHandler()
    await twilio_event_handler.send_event_to_client(
        call_sid=call_sid,
        conversation_id=conversation_id, # type: ignore
        twilio_client=twilio_client,
        participants=participants,
        subaccount_credentials=subaccount_credentials,
        message=message,
    )


async def fetch_provider_workspace_client(
    workspace: UUID, provider_client: TwilioClient
) -> TwilioClient:
    details = await get_provider_details(
        workspace_id=ShortId.with_uuid(workspace)
    )

    # build a krispcall_twilio sub client
    #  # we build sub client because using client directly
    # with provider details would give us 403
    # and we've separated our different twilio accounts into
    # sub accounts for each workspace
    # TODO: Move Sub client mechanism into the krispcall_twilio

    return sub_client(
        obj=copy.copy(provider_client),
        details={
            "string_id": details.auth_id,
            "auth_token": details.auth_token,
            "api_key": details.api_key,
            "api_secret": details.api_secret,
        },
    )


async def skip_conversation(
    conversation_sid: UUID,
    db_conn: DbConnection,
):
    async with unit_of_work.CampaignConversationSqlUnitOfWork(db_conn) as uow:
        conversation = await uow.repository.get(conversation_sid)
        await uow.repository.skip_conversation(id=conversation_sid)
        return conversation


async def hold_conversation(
    conversation_sid: UUID, hold: bool, db_conn: DbConnection
):
    if hold:
        return await update_campaign_conversation_status(
            status=models.ConferenceStatus.on_hold,
            conversation_id=conversation_sid,
            db_conn=db_conn,
        )
    return await update_campaign_conversation_status(
        status=models.ConferenceStatus.in_progress,
        conversation_id=conversation_sid,
        db_conn=db_conn,
    )


# contains the map of recording action


async def record_campaign_conversation(
    conversation_sid: UUID,
    action: Literal["stop", "pause", "resume"],
    db_conn: DbConnection,
    twilio_client_: TwilioClient,
    workspace: UUID,
):
    # get the sub client using the workspace
    sub_client = await fetch_provider_workspace_client(
        workspace,
        twilio_client_,
    )
    record_action_map = {
        "stop": sub_client.recordings_resource.stop_recording,
        "pause": sub_client.recordings_resource.pause_recording,
        "resume": sub_client.recordings_resource.resume_recording,
    }

    # get the camapgin conversation
    campaign_conversation = await views.get_campaign_conference_by_id(
        ref=conversation_sid,
        db_conn=db_conn,
    )
    if not campaign_conversation:
        return
    # get the conference sid
    conference_sid = ShortId.with_uuid(campaign_conversation.get("twi_sid"))

    # get the correct action
    action_func = record_action_map.get(action.lower, None) # type: ignore

    if action_func:
        await action_func(conference_sid=conference_sid)


# contains the map of the command and the function to control
# the campaign from the call_handlers
controller_map = {
    "start": call_handlers.start_campaign_loop,
    "resume": call_handlers.resume_campaign_loop,
    "pause": call_handlers.pause_campaign_loop,
    "end": call_handlers.end_campaign_loop,
    "reattempt": call_handlers.reattempt_campaign_loop,
}


async def control_campaign_loop(
    command: str,
    campaign: campaign_models.Campaigns,
    provider_client: TwilioClient,
    member: UUID,
    db_conn: DbConnection,
    workspace: UUID,
    settings: Settings,
    queue: JobQueue,
):
    details = await get_provider_details(
        workspace_id=ShortId.with_uuid(workspace)
    )

    # build a krispcall_twilio sub client
    #  # we build sub client because using client directly
    # with provider details would give us 403
    # and we've separated our different twilio accounts into
    # sub accounts for each workspace
    # TODO: Move Sub client mechanism into the krispcall_twilio

    cpass_user = {
        "string_id": details.auth_id,
        "auth_token": details.auth_token,
        "api_key": details.api_key,
        "api_secret": details.api_secret,
    }
    sub_client_ = sub_client(
        obj=copy.copy(provider_client),
        details=cpass_user,
    )
    # end campaign if no command is found
    controller = controller_map.get(command, call_handlers.end_campaign_loop)

    await controller(
        campaign=campaign,
        sub_client=sub_client_,
        db_conn=db_conn,
        member=member,
        workspace=workspace,
        settings=settings,
        cpass_user=cpass_user,
        queue=queue,
    )


status_map = {
    "queued": "queued",
    "ringing": "ringing",
    "in-progress": "in_progress",
    "canceled": "canceled",
    "completed": "completed",
    "no-answer": "no_answer",
    "busy": "busy",
    "failed": "failed",
}


async def handle_participant_event(
    validated_data: Union[TwilioAgentCallback, TwilioPSTNCallback],
    db_conn: DbConnection,
):
    async with unit_of_work.ParticipantCallSqlUnitOfWork(db_conn) as uow:
        await uow.repository.update_call_status_by_twi_sid(
            ref=validated_data.call_sid,
            status=status_map.get(validated_data.call_status),
        )


async def drop_campaign_voicemail(
    provider_client: TwilioClient,  # needs to be sub client
    conversation: UUID,
    voicemail_url: str,
    db_conn: DbConnection,
):
    # get conversation participants
    participants = await views.get_conversation_participants(
        conversation=conversation,
        db_conn=db_conn,
    )
    client_call = [
        record
        for record in participants
        if record.get("participant_type") == "client"
    ]
    if not client_call:
        return
    client_call = client_call[0]
    call_sid = client_call.get("twi_sid")
    await provider_client.call_resource.drop_voicemail(
        call_sid=call_sid,
        voicemail_url=voicemail_url,
    )
    # print(response)
    return
