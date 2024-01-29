from .twilio_requests import TwilioRequestResource
from twilio.base.exceptions import TwilioRestException
from krispcall.common.utils.shortid import ShortId
from typing import Dict, Any


class CallerIdResource:
    def __init__(self, account_sid, auth_token, base_url, app_url):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.base_url = base_url
        self.app_url = app_url
        self.client = TwilioRequestResource(
            account_sid=account_sid, auth_token=auth_token
        )

    async def create(
        self,
        friendly_name: str,
        phone_number: str,
        workspace_sid: ShortId,
        channel_sid: ShortId,
    ) -> Dict[str, Any]:
        url: str = (
            f"{self.base_url}/Accounts/{self.account_sid}"
            f"/OutgoingCallerIds.json"
        )
        status_callback: str = (
            f"{self.app_url}/twilio_callbacks/"
            f"callerid_verification/{workspace_sid}/{channel_sid}"
        )
        payload = {
            "PhoneNumber": phone_number,
            "FriendlyName": friendly_name,
            "StatusCallback": status_callback,
        }
        response = await self.client.post(url=url, payload=payload)
        pending = f"Code sent to {phone_number}"
        try:
            return {
                "code": response["validation_code"]
                if response.get("validation_code")
                else 0,
                "message": "Phone number is already used!"
                if response.get("message")
                else pending,
            }

        except KeyError as e:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            ) from e

    async def delete(self, callerid_sid: str):
        url: str = (
            f"{self.base_url}/Accounts/{self.account_sid}"
            f"/OutgoingCallerIds/{callerid_sid}.json"
        )
        response = await self.client.delete(url=url)
        try:
            return response
        except KeyError as e:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            ) from e
