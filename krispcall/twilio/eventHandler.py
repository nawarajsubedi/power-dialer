import copy
import json
from typing import Any
from uuid import UUID
from krispcall.common.utils.shortid import ShortId

from krispcall.twilio.utils import sub_client
from krispcall.twilio.twilio_client import TwilioClient


class TwilioEventHandler:
    async def send_event_to_client(
        self,
        call_sid: str,
        conversation_id: UUID,
        twilio_client: TwilioClient,
        participants: Any,
        subaccount_credentials: Any,
        message: str,
    ):
        _client: TwilioClient = sub_client(
            obj=copy.copy(twilio_client),
            details=subaccount_credentials,
        )
        agent_call = [
            p for p in participants if p.get("participant_type") == "agent"
        ]
        if agent_call:
            agent_call = agent_call[0].get("twi_sid")
        else:
            agent_call = call_sid

        # send event to front-end client
        await _client.call_resource.send_event_to_call(
            call_sid=agent_call,
            msg={
                "conversationSid": ShortId.with_uuid(conversation_id),
                "status": "callDisconnected",
                "message": message,
            },
        )
