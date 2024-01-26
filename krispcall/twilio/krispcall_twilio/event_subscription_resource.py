from .twilio_requests import TwilioRequestResource
from twilio.base.exceptions import TwilioRestException
from krispcall_twilio.type import TwilioEventTypes
from pydantic.types import SecretStr
from pydantic import AnyHttpUrl, parse_obj_as
from typing import Union
import json


class EventSubscriptionResource:
    def __init__(
        self,
        account_sid: Union[SecretStr, SecretStr],
        auth_token: Union[SecretStr, SecretStr],
        base_url: AnyHttpUrl,
        app_url: AnyHttpUrl,
    ):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.base_url = base_url
        self.app_url = app_url
        self.sink_url: AnyHttpUrl = parse_obj_as(
            AnyHttpUrl, "https://events.twilio.com/v1/Subscriptions"
        )
        self.client: TwilioRequestResource = TwilioRequestResource(
            account_sid=account_sid, auth_token=auth_token
        )

    async def create_new_subscription(
        self, sink_sid: str, description: str, type_: TwilioEventTypes
    ):
        payload = {
            "Description": description,
            "Types": json.dumps(
                {
                    "type": type_,
                }
            ),
            "SinkSid": sink_sid,
        }
        response = await self.client.post(url=self.sink_url, payload=payload)
        try:
            return response["sid"]
        except KeyError as e:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=self.sink_url,
            ) from e
