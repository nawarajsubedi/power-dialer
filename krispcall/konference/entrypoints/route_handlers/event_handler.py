import copy
import json
from krispcall.common.utils.static_helpers import url_safe_decode
from krispcall.konference.domain.models import ConferenceStatus
from krispcall.common.app_settings.request_helpers import get_database
from redis import Redis
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import Response
from krispcall.konference.service_layer import (
    abstracts,
    views,
)
from krispcall.common.services.helper import change_camel_case_to_snake
from krispcall.konference import services
from krispcall.common.utils.shortid import ShortId
from krispcall.providers.queue_service.job_queue import JobQueue
from krispcall.twilio.utils import TwilioClient, sub_client


def replace_from(string: str):
    return string.replace("From", "ChannelNumber")


class CampaignClientHandler(HTTPEndpoint):
    """Handles the conference event for the dialing campaign
    Will use this as final callback to update the campaign participant event for agent
    """

    async def post(self, request):
        # parse data
        data = await request.form()
        call_status = data.get("CallStatus")
        if call_status == "initiated":
            return Response(status_code=200, media_type="application/xml")
        db_conn = get_database(request)
        data = {
            change_camel_case_to_snake(replace_from(key)): value
            for key, value in data.items()
        }
        validated_data = abstracts.TwilioPSTNCallback.construct(**data)
        callback_data = request.path_params["callback_data"]
        (
            workspace,
            campaign_id,
            conference_friendly_name,
            conversation,
        ) = url_safe_decode(callback_data).split(",")
        if call_status.lower() in [
            "in_progress",
            "in-progress",
        ]:
            cache = Redis.from_url(request.app.state.settings.redis_settings)
            values = cache.get(campaign_id) or {}
            camp_obj = json.loads(values)
            details = camp_obj.get("cpass_user")
            _client: TwilioClient = sub_client(
                obj=copy.copy(request.app.state.twilio),
                details=details,
            )
            participants = await views.get_conversation_participants(
                conversation=ShortId(conversation).uuid(), db_conn=db_conn
            )
            agent_call = [
                p for p in participants if p.get("participant_type") == "agent"
            ]
            if agent_call:
                agent_call = agent_call[0].get("twi_sid")
            else:
                agent_call = validated_data.call_sid

            # send event to front end
            await _client.call_resource.send_event_to_call(
                call_sid=agent_call,
                msg={
                    "conversationSid": conversation,
                    "status": "callConnected",
                },
            )

        if call_status.lower() in [
            "completed",
            "busy",
            "canceled",
            "failed",
            "no-answer",
            "noanswer",
        ]:
            await request.app.state.queue.enqueue_job(
                "expire_cache",
                data=[validated_data.call_sid],
                queue_name="arq:pd_queue",
                defer_by_seconds=500,
            )
        # get the conversation id from the callback data to update
        # the campaign conversation status
        conversation_status = {
            "completed": ConferenceStatus.completed,
            "busy": ConferenceStatus.busy,
            "canceled": ConferenceStatus.cancelled,
            "failed": ConferenceStatus.failed,
            "no-answer": ConferenceStatus.no_answer,
            "noanswer": ConferenceStatus.no_answer,
            "in_progress": ConferenceStatus.in_progress,
        }.get(call_status, ConferenceStatus.in_progress)
        await services.update_campaign_conversation_status(
            status=conversation_status,
            conversation_id=ShortId(conversation).uuid(),
            db_conn=db_conn,
        )
        await services.handle_participant_event(
            validated_data=validated_data,
            db_conn=db_conn,
        )
        return Response(status_code=200, media_type="application/xml")


class CampaignAgentHandler(HTTPEndpoint):
    """Handles the conference event for numbers added to campaign
    Will this as final callback to update the campaign participant event
    """

    async def post(self, request: Request):
        """Request object"""
        data = await request.form()
        call_status = data.get("CallStatus")
        if call_status == "initiated":
            return Response(status_code=200, media_type="application/xml")
        db_conn = get_database(request)
        job_queue: JobQueue = request.app.state.queue
        data = {
            change_camel_case_to_snake(replace_from(key)): value
            for key, value in data.items()
        }
        validated_data = abstracts.TwilioAgentCallback.construct(**data)
        callback_data = request.path_params["callback_data"]

        if call_status.lower() in [
            "completed",
            "busy",
            "canceled",
            "failed",
            "no-answer",
            "noanswer",
        ]:
            await job_queue.enqueue_job(
                "expire_cache",
                data=[validated_data.call_sid],
                queue_name="arq:pd_queue",
                defer_by_seconds=500,
            )

        await services.handle_participant_event(
            validated_data=validated_data,
            db_conn=db_conn,
        )
        return Response(status_code=200, media_type="application/xml")
