""" Services Resources Adapter"""

from .twilio_requests import TwilioRequestResource
from .endpoints import convert_dict_to_pascal_case
from twilio.base.exceptions import TwilioRestException


class MessagingServiceResource:
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
        self.ressource_url = (
            f"https://messaging.{twilio_edge}.{twilio_region}.twilio.com/v1/Services"
            if twilio_edge and twilio_region
            else "https://messaging.twilio.com/v1/Services"
        )
        self.client = TwilioRequestResource(
            account_sid=account_sid, auth_token=auth_token
        )

    async def create(self, friendly_name: str, use_case: str) -> str:
        payload = {
            "FriendlyName": friendly_name,
            "UseInboundWebhookOnNumber": True,
            "Usecase": use_case,
        }
        url = self.ressource_url
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
        url = f"{self.ressource_url}/{sid}"
        try:
            return await self.client.get(url=url)
        except Exception as E:
            raise TwilioRestException(
                msg=str(E),
                code=400,
                status=400,
                uri=url,
            )

    async def attach_phone_number_to_service(
        self, service_sid: str, phone_number_sid: str
    ) -> str:
        url = f"{self.ressource_url}/{service_sid}/PhoneNumbers"
        payload = {"PhoneNumberSid": phone_number_sid}
        try:
            response = await self.client.post(url=url, payload=payload)
            return response["sid"]
        except KeyError:
            return "Invalid Phone Number"
            # raise TwilioRestException(
            #     msg=response["message"],
            #     code=response["code"],
            #     status=response["status"],
            #     uri=url,
            # )

    # async def delete_phone_number_from_service(
    #     self, service_sid: str, phone_number_sid: str
    # ) -> str:
    #     url = f"{self.ressource_url}/{service_sid}/PhoneNumbers/{phone_number_sid}"
    #     try:
    #         return await self.client.delete_req_twilio(url=url)
    #     except Exception as E:
    #         raise TwilioRestException(
    #             msg=str(E),
    #             code="400",
    #             status="400",
    #             uri=url,
    #         )

    # async def delete(self, sid: str):
    #     url = f"{self.ressource_url}/{sid}"
    #     try:
    #         return await self.client.delete_req_twilio(url=url)
    #     except Exception as E:
    #         raise TwilioRestException(
    #             msg=str(E),
    #             code="400",
    #             status="400",
    #             uri=url,
    #         )
