from typing import Union
from pydantic import SecretStr, AnyHttpUrl
from .twilio_requests import TwilioRequestResource
from twilio.base.exceptions import TwilioRestException


class TranscriptionResource:
    def __init__(
        self,
        account_sid: Union[SecretStr, SecretStr],
        auth_token: Union[SecretStr, SecretStr],
        app_url: AnyHttpUrl,
    ):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.base_url = "https://api.twilio.com/2010-04-01/Accounts/"
        self.app_url = app_url
        self.request_client: TwilioRequestResource = TwilioRequestResource(
            account_sid=account_sid, auth_token=auth_token
        )

    async def get_transcription(self, transcription_sid: str):
        url = (
            self.base_url
            + f"{self.account_sid}/Transcriptions/{transcription_sid}.json"
        )
        response = await self.request_client.get(url=url)
        try:
            return response
        except KeyError:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )
