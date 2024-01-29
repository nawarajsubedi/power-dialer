from .twilio_requests import TwilioRequestResource
from twilio.base.exceptions import TwilioRestException
from krispcall.common.utils.shortid import ShortId
from pydantic.types import SecretStr
from pydantic import AnyHttpUrl
from typing import Union


class ApplicationResource:
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
        self.client: TwilioRequestResource = TwilioRequestResource(
            account_sid=account_sid, auth_token=auth_token
        )

    async def create(self, friendly_name: str, workspace_sid: ShortId) -> str:
        url = f"{self.base_url}/Accounts/{self.account_sid}/Applications.json"
        incoming_call_fallback_url: str = (
            f"{self.app_url}/twilio_callbacks/calls/fallback"
        )
        payload = {
            "VoiceMethod": "POST",
            "VoiceUrl": (
                f"{self.app_url}/twilio_callbacks/" f"call/outbound_conference"
            ),
            "FriendlyName": friendly_name,
            "VoiceFallbackUrl": incoming_call_fallback_url,
        }
        response = await self.client.post(url=url, payload=payload)
        try:
            return response["sid"]
        except KeyError as e:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            ) from e

    async def update(
        self, application_sid: str, workspace_sid: ShortId
    ) -> str:
        url = (
            f"{self.base_url}/Accounts/{self.account_sid}/"
            f"Applications/{application_sid}.json"
        )
        incoming_call_fallback_url: str = (
            f"{self.app_url}/twilio_callbacks/calls/fallback"
        )
        outgoing_conference_url: str = (
            f"{self.app_url}/twilio_callbacks/" f"call/outbound_conference"
        )
        payload = {
            "VoiceMethod": "POST",
            "VoiceUrl": outgoing_conference_url,
            "VoiceFallbackUrl": incoming_call_fallback_url,
        }
        response = await self.client.post(url=url, payload=payload)
        try:
            return response["sid"]
        except KeyError as e:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            ) from e

    async def delete(self, sid: str):
        url = (
            f"{self.base_url}/Accounts/{self.account_sid}"
            f"/Applications/{sid}.json"
        )
        response = await self.client.delete(url=url)
        return response
