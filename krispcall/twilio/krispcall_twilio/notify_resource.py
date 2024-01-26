""" Notify Services Adapter"""

from typing import List
from .twilio_requests import TwilioRequestResource
from .endpoints import convert_dict_to_pascal_case
from twilio.base.exceptions import TwilioRestException
import json


class NotifyResource:
    def __init__(
        self,
        account_sid,
        auth_token,
        app_url,
        twilio_edge=None,
        twilio_region=None,
    ):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.app_url = app_url
        self.resource_url = (
            f"https://notify.{twilio_edge}.{twilio_region}.twilio.com/v1/Services"
            if twilio_edge and twilio_region
            else "https://notify.twilio.com/v1/Services"
        )
        self.client = TwilioRequestResource(
            account_sid=account_sid, auth_token=auth_token
        )

    async def create(self, friendly_name: str):
        url = self.resource_url
        payload = {
            "FriendlyName": friendly_name,
        }
        response = await self.client.post(url=url, payload=payload)
        try:
            return response["sid"]
        except KeyError:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )

    async def get(self, sid: str):
        url = f"{self.resource_url}/{sid}"
        try:
            return await self.client.get(url=url)
        except Exception as E:
            raise TwilioRestException(
                msg=str(E),
                code=400,
                status=400,
                uri=url,
            )

    # async def delete(self, sid: str):
        # url = f"{self.resource_url}/{sid}"
        # try:
        #     return await self.client.delete_req_twilio(url=url)
        # except Exception as E:
        #     raise TwilioRestException(
        #         msg=str(E),
        #         code="400",
        #         status="400",
        #         uri=url,
        #     )

    async def update(self, sid: str, friendly_name: str):
        url = f"{self.resource_url}/{sid}"
        payload = {
            "FriendlyName": friendly_name,
        }
        response = await self.client.post(url=url, payload=payload)
        try:
            return response["sid"]
        except KeyError:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )

    async def attach_sms_service_to_notify_service(
        self, sms_service_sid: str, notify_service_sid: str
    ) -> str:
        url = f"{self.resource_url}/{notify_service_sid}"
        payload = {"MessagingServiceSid": sms_service_sid}
        response = await self.client.post(url=url, payload=payload)
        try:
            return response["sid"]
        except KeyError:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )

    async def send_broadcast_message(
        self, contacts: List[str], body: str, notify_service: str
    ) -> str:
        url = f"{self.resource_url}/{notify_service}/Notifications"
        to_binding = [
            json.dumps({"binding_type": "sms", "address": contact})
            for contact in contacts
        ]
        payload = {
            "ToBinding": to_binding,
            "Body": body,
        }
        try:

            response = await self.client.post(url=url, payload=payload)
            return response.get("sid")
        except Exception as E:
            raise TwilioRestException(
                msg=str(E),
                code=400,
                status=400,
                uri=url,
            )
