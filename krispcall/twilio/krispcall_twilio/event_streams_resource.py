from .twilio_requests import TwilioRequestResource
from twilio.base.exceptions import TwilioRestException
from krispcall.common.shortid import ShortId
from pydantic.types import SecretStr
from pydantic import AnyHttpUrl, parse_obj_as
from typing import Union
import json


class EventStreamsResource:
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
            AnyHttpUrl, "https://events.twilio.com/v1/Sinks/"
        )
        self.client: TwilioRequestResource = TwilioRequestResource(
            account_sid=account_sid, auth_token=auth_token
        )

    """"sink_configuration": {
    "destination": "http://example.org/webhook",
    "method": "<POST|GET>",
    "batch_events": <true|false>
}"""

    async def create_webhook_sync(self, workspace_sid: ShortId):
        payload = {
            "SinkType": "webhook",
            "Description": f"{workspace_sid}_Sink",
            "SinkConfiguration": json.dumps(
                {
                    "destination": f"{self.app_url}/twilio_callbacks/streams/{workspace_sid}",
                    "method": "POST",
                    "batch_events": False,
                }
            ),
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
