import asyncio
from krispcall.twilio.request_validator import RequestValidator
from krispcall.twilio.type import OutboundSmsPayload
from .twilio_requests import TwilioRequestResource
from twilio.twiml.messaging_response import MessagingResponse
from twilio.base.exceptions import TwilioRestException
from typing import Dict, Union

from loguru import logger
from pydantic import SecretStr


class SmsResource:
    def __init__(
        self,
        account_sid: Union[SecretStr, SecretStr],
        auth_token: Union[SecretStr, SecretStr],
        base_url: str,
        app_url: str,
    ):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.base_url = base_url
        self.app_url = app_url
        self._post: TwilioRequestResource = TwilioRequestResource(
            account_sid=account_sid, auth_token=auth_token
        )
        self.sms_validators = RequestValidator()

    async def send_message(self, params: Dict) -> str:
        print(self.auth_token)
        print(self.account_sid)
        self.sms_validators.validate_sms(
            body=params["body"],
            message_to=params["message_to"],
            message_from=params["message_from"],
        )
        if "media_url" in params:
            payload = {
                "Body": params["body"],
                "From": params["message_from"],
                "To": params["message_to"],
                "StatusCallback": (
                    f"{self.app_url}/twilio_callbacks/sms_events/"
                    f"{params['workspace_sid']}"
                ),
                "MediaUrl": params["media_url"],
            }
        else:
            payload = {
                "Body": params["body"],
                "From": params["message_from"],
                "To": params["message_to"],
                "StatusCallback": (
                    f"{self.app_url}/twilio_callbacks/sms_events/"
                    f"{params['workspace_sid']}"
                ),
            }
        url: str = f"{self.base_url}/Accounts/{self.account_sid}/Messages.json"
        response = await self._post.post(url=url, payload=payload)
        if "sid" in response:
            return response["sid"]
        else:
            logger.info(
                f"SMS sending failed- From:{params['message_from']},To:{params['message_to']}, response_error_msg:{response['message']}, response_error_code:{response['code']}"
            )
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )

    async def receive_sms(self):
        return MessagingResponse()

    async def get_sms_resource(self, sms_id: str):
        a_sid = self.account_sid
        url: str = f"{self.base_url}/Accounts/{a_sid}/Messages/{sms_id}.json"
        response = await self._post.get(url=url)
        if "sid" in response:
            return response
        else:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )

    async def send_bulk_message(self, params: Dict) -> str:
        self.sms_validators.validate_bulksms(
            body=params["body"], message_to=params["message_to"]
        )

        # payload = {
        #     "Body": params["body"],
        #     "MessagingServiceSid": params["messaging_service_sid"],
        #     "To": params["message_to"],
        #     "From": params["message_from"],
        #     "StatusCallback": (
        #         f"{self.app_url}/twilio_callbacks/bulksms_events/"
        #         f"{params['workspace_sid']}/{params['campaign_sid']}/{params['contact_count']}"
        #     ),
        # }
        payload = OutboundSmsPayload(
            Body=params["body"],
            MessagingServiceSid=params["messaging_service_sid"],
            To=params["message_to"],
            From=params["message_from"],
            StatusCallback=(
                f"{self.app_url}/twilio_callbacks/bulksms_events/"
                f"{params['workspace_sid']}/{params['campaign_sid']}/{params['contact_count']}"
            ), # type: ignore
        )
        print(payload.as_multi_dict)
        url: str = f"{self.base_url}/Accounts/{self.account_sid}/Messages.json"
        try:
            response = await self._post.post(
                url=url, payload=payload.as_multi_dict
            )
            if "sid" in response:
                return response["sid"]
            return response
        except Exception:
            raise TwilioRestException(
                msg=response["message"], # type: ignore
                code=response["code"], # type: ignore
                status=response["status"], # type: ignore
                uri=url,
            )

    async def delete_sms(self, sms_id: str):
        a_sid = self.account_sid
        url: str = f"{self.base_url}/Accounts/{a_sid}/Messages/{sms_id}.json"
        response = await self._post.delete(url=url)
        if not response:
            return response
        else:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )
