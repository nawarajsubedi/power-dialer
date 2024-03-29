from uuid import UUID
from datetime import datetime, timedelta
from redis import Redis
from krispcall.common.database.connection import DbConnection
from krispcall.providers.queue_service.job_queue import JobQueue

from krispcall.twilio.enums import ActiveStatusEnum, NotActiveStatusEnum
from krispcall.twilio.twilio_client import TwilioClient
from krispcall.twilio.utils import get_conference_resource
from krispcall.konference.billing.enums import BillingTypeEnum
from krispcall.konference.domain import models
from krispcall.konference.billing.constant import CHARGE_CALL_BACK_TIME
from krispcall.konference.service_layer import commands
from krispcall.konference.service_layer import handlers
from krispcall.konference.service_layer import unit_of_work
from krispcall.konference.billing.models import (
    BillingResponse,
    CampaignOutboundCallRequest,
)
from krispcall.konference.billing.billing_service import BillingService


async def task_campaign_call_charge(
    ctx,
    campaign_call_params: CampaignOutboundCallRequest,
):
    try:
        settings = ctx["settings"]
        queue: JobQueue = ctx["queue"]
        db_conn: DbConnection = ctx["db"]
        twilio_client: TwilioClient = ctx["twilio"]

        cache = Redis.from_url(settings.redis_settings)

        billing_response = await process_billing_transaction(
            campaign_call_params, cache, queue, twilio_client
        )

        if billing_response.is_sufficient_credit:
            await update_campaign_conversation_status(
                status=models.ConferenceStatus.completed,
                conversation_id=campaign_call_params.conversation_id,
                db_conn=db_conn,
            )
    except Exception as e:
        print("Error", e)


async def process_billing_transaction(
    campaign_call_params: CampaignOutboundCallRequest,
    cache: Redis,
    queue: JobQueue,
    twilio_client: TwilioClient,
    charge_call_back_time: int = CHARGE_CALL_BACK_TIME,
    charge_for_first_minute: bool = False,
):
    is_call_inprogress = False

    conference_info = await get_conference_resource(
        twilio_client=twilio_client,
        cache=cache,
        conference_friendly_name=campaign_call_params.conference_friendly_name,
        campaign_id=campaign_call_params.campaign_id,
    )

    call_status = conference_info.conference_status.lower()
    active_statuses = {status.value for status in ActiveStatusEnum}
    print("Call charge task------------------------------------------------>", call_status)

    if call_status not in active_statuses and not charge_for_first_minute:
        # Do not charge to customer
        # So returning from the process_billing_transaction
        return BillingResponse(is_call_inprogress=False)

    if call_status in active_statuses or not campaign_call_params.call_sid:
        campaign_call_params.total_participants = 1

    billing_types = [
        BillingTypeEnum.SIP_CHARGE,
        BillingTypeEnum.CONFERENCE_CHARGE,
    ]

    if charge_for_first_minute or call_status in active_statuses:
        billing_types.append(BillingTypeEnum.CALL_CHARGE)

    campaign_call_params.billing_types = billing_types

    if call_status in active_statuses:
        is_call_inprogress = True
        await queue.enqueue_job(
            "task_campaign_call_charge",
            data=[campaign_call_params],
            queue_name="arq:pd_queue",
            defer_until=datetime.now() + timedelta(seconds=charge_call_back_time),
        )

    billing_response: BillingResponse = (
        await BillingService.execute_campaign_call_transaction(data=campaign_call_params)
    )
    billing_response.is_call_inprogress = is_call_inprogress

    return billing_response


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
