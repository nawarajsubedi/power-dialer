from typing import Union

from pydantic import AnyHttpUrl
from pydantic.types import SecretStr

from .twilio_requests import TwilioRequestResource
from .type import BuyPhoneNumber, PhoneNumberRouteSetup
from twilio.base.exceptions import TwilioRestException
from .endpoints import convert_dict_to_pascal_case
from loguru import logger


class IncomingNumberResource:
    def __init__(
        self,
        app_url: AnyHttpUrl,
        account_sid: Union[SecretStr, SecretStr],
        auth_token: Union[SecretStr, SecretStr],
    ):
        self.app_url = app_url
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.base_url = "https://api.twilio.com/2010-04-01/Accounts/"
        self.client = TwilioRequestResource(
            account_sid=self.account_sid,
            auth_token=self.auth_token,
        )

    async def create_incoming_phone_number(
        self,
        phone_number,
        # address_sid=None,
        # bundle_sid=None,
    ):
        payload = convert_dict_to_pascal_case(phone_number)
        # if address_sid and payload["Type"].lower() in ["local", "tollfree", "national"]:
        #     payload.update(AddressSid=address_sid)
        # if bundle_sid and payload["Type"].lower() == "mobile":
        #     payload.update(AddressSid=address_sid, BundleSid=bundle_sid)
        url = f"{self.base_url}{self.account_sid}/IncomingPhoneNumbers.json"
        return await self.client.post(url=url, payload=payload)

    async def buy_a_number(self, phone_number_details: BuyPhoneNumber):
        payload = {"PhoneNumber": phone_number_details.phone_number}
        url = (
            self.base_url + f"{self.account_sid}/AvailablePhoneNumbers/"
            f"{phone_number_details.country_code}"
            f"/{phone_number_details.phone_number_type}.json?"
            f"AreaCode="
            f"{phone_number_details.area_code}"
        )
        response = await self.client.post(url=url, payload=payload)
        if "sid" in response:
            return response["sid"]
        else:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )

    async def list_all_phone_numbers(self):
        url = self.base_url + f"{self.account_sid}/IncomingPhoneNumbers.json"
        response = await self.client.get(url=url)

        if "incoming_phone_numbers" in response:
            return response
        else:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )

    async def list_all_mobile_numbers(self):
        url = (
            self.base_url
            + f"{self.account_sid}/IncomingPhoneNumbers.json/Mobile"
        )
        response = await self.client.get(url=url)
        return response

    async def list_all_local_numbers(self):
        url = (
            self.base_url
            + f"{self.account_sid}/IncomingPhoneNumbers.json/Local"
        )
        response = await self.client.get(url=url)
        return response

    async def list_all_toll_free_numbers(self):
        url = (
            self.base_url
            + f"{self.account_sid}/IncomingPhoneNumbers.json/TollFree"
        )
        response = await self.client.get(url=url)
        return response

    async def get_phone_number_detail(self, phone_number_sid):
        url = (
            self.base_url + f"{self.account_sid}/IncomingPhoneNumbers/"
            f"{phone_number_sid}.json"
        )
        response = await self.client.get(url=url)
        if "sid" in response:
            return response["sid"]
        else:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )

    async def get_incoming_number(self, phone_number_sid):
        url = (
            self.base_url + f"{self.account_sid}/IncomingPhoneNumbers/"
            f"{phone_number_sid}.json"
        )
        response = await self.client.get(url=url)
        if "sid" in response:
            return response
        else:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )

    async def get_number_sid(self, phone_number_friendly):
        url = (
            self.base_url + f"{self.account_sid}/IncomingPhoneNumbers.json?"
            f"PhoneNumber={phone_number_friendly}"
        )
        try:
            response = await self.client.get(url=url)
            return response["incoming_phone_numbers"][0]["sid"]
        except KeyError as e:
            raise TwilioRestException(
                msg=f"Phone number {phone_number_friendly} is already"
                f" associated with another workspace!",
                code=21473,
                status=404,
                uri=url,
            ) from e

    async def setup_ivr_routes(self, route_details: PhoneNumberRouteSetup):
        incoming_call_url: str = (
            f"{self.app_url}/twilio_callbacks/ivr/{route_details.workspace_id}"
            f"/{route_details.channel_sid}"
        )
        incoming_call_fallback_url: str = (
            f"{self.app_url}/twilio_callbacks/calls/fallback"
        )
        payload = {
            "VoiceUrl": incoming_call_url,
            "VoiceFallbackUrl": incoming_call_fallback_url,
        }
        url = (
            self.base_url + f"{self.account_sid}/IncomingPhoneNumbers/"
            f"{route_details.phone_number_sid}.json"
        )
        response = await self.client.post(url=url, payload=payload)
        if "sid" in response:
            return response["sid"]
        else:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )

    async def setup_routes(self, route_details: PhoneNumberRouteSetup):
        incoming_call_url: str = (
            f"{self.app_url}/twilio_callbacks/call/incoming/{route_details.workspace_id}"
            f"/{route_details.channel_sid}"
        )
        incoming_message_url: str = (
            f"{self.app_url}/twilio_callbacks/sms/incoming/{route_details.workspace_id}"
            f"/{route_details.channel_sid}"
        )
        incoming_call_fallback_url: str = (
            f"{self.app_url}/twilio_callbacks/calls/fallback"
        )

        incoming_message_fallback_url: str = (
            f"{self.app_url}/twilio_callbacks/sms/fallback/incoming"
            f"/{route_details.workspace_id}/{route_details.channel_sid}"
        )
        # get the abilities of the provided number
        number_details = await self.get_incoming_number(
            route_details.phone_number_sid
        )
        voice, sms = (
            number_details.get("capabilities").get("voice"),
            number_details.get("capabilities").get("sms"),
        )
        if voice and sms:
            payload = {
                "VoiceUrl": incoming_call_url,
                "SmsUrl": incoming_message_url,
                "VoiceFallbackUrl": incoming_call_fallback_url,
                "SmsFallbackUrl": incoming_message_fallback_url,
            }
        elif not voice and sms:
            payload = {
                "SmsUrl": incoming_message_url,
                "SmsFallbackUrl": incoming_message_fallback_url,
            }
        else:
            payload = {
                "VoiceUrl": incoming_call_url,
                "VoiceFallbackUrl": incoming_call_fallback_url,
            }

        url = (
            self.base_url + f"{self.account_sid}/IncomingPhoneNumbers/"
            f"{route_details.phone_number_sid}.json"
        )
        response = await self.client.post(url=url, payload=payload)
        logger.info(
            f"Number Configuration {str(response)}: msg={response}, payload={payload}"
        )

        if "sid" in response:
            logger.info(
                f"Number Configuration success for number {route_details.phone_number_sid}: msg={response}"
            )
            return response["sid"]
        else:
            logger.error(
                f"Number Configuration error for number {route_details.phone_number_sid}: msg={response['message']}, code={response['code']}, staus={response['status']}"
            )
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )

    async def unconfigure_routes(self, sid):
        payload = {
            "VoiceUrl": f"{self.app_url}/twilio_callbacks/cancelation_handlers",
            "SmsUrl": f"{self.app_url}/twilio_callbacks/cancelation_handlers",
            "VoiceFallbackUrl": "",
            "SmsFallbackUrl": "",
        }
        url = (
            self.base_url + f"{self.account_sid}/IncomingPhoneNumbers/"
            f"{sid}.json"
        )
        response = await self.client.post(url=url, payload=payload)
        if "sid" in response:
            return response["sid"]
        else:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )

    async def rename_number(self, sid, friendly_name):
        payload = {
            "FriendlyName": friendly_name,
        }
        url = (
            self.base_url + f"{self.account_sid}/IncomingPhoneNumbers/"
            f"{sid}.json"
        )
        response = await self.client.post(url=url, payload=payload)
        if "sid" in response:
            return response["sid"]
        else:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )

    async def delete(self, sid):
        url = f"{self.base_url}{self.account_sid}\
            /IncomingPhoneNumbers/{sid}.json"
        response = await self.client.delete(url)
        return response
