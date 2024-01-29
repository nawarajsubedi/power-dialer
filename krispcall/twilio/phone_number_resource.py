import asyncio
import logging
import typing

from .type import NumberAvailabilityParams, NumberAvailabilityPathParams
from .endpoints import (
    build_available_country_path,
    build_available_number_path,
)
from .twilio_requests import TwilioRequestResource
from functools import partial
from twilio.base.exceptions import TwilioRestException

PRICING_URL = "https://pricing.twilio.com/v1"
# LOOKUP_URL = "https://lookups.twilio.com/v2"

# LOOKUP_URL = f"https://lookups.{twilio_edge}.{twilio_region}.twilio.com/v2"

logger = logging.getLogger("twilio")


class PhoneNumberResource:
    def __init__(
        self,
        account_sid,
        auth_token,
        base_url,
        twilio_edge=None,
        twilio_region=None,
    ):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.base_url = base_url
        self.pricing_url = PRICING_URL
        self.lookup_url = (
            f"https://lookups.{twilio_edge}.{twilio_region}.twilio.com/v2"
            if twilio_edge and twilio_region
            else "https://lookups.twilio.com/v2"
        )
        self.get = TwilioRequestResource(
            account_sid=self.account_sid, auth_token=self.auth_token
        )

    async def get_country_properties(self, country: str):
        path = build_available_country_path(self.account_sid, country)
        response = await self.get.get(url=path)
        try:
            if country:
                return {
                    "country_code": response["country_code"],
                    "country": response["country"],
                    "types": response[
                        "subresource_uris"
                    ],  # [k for k in response["subresource_uris"]],
                }
            else:
                return [
                    {
                        "country_code": country["country_code"],
                        "country": country["country"],
                        "types": country[
                            "subresource_uris"
                        ],  # [k for k in country["subresource_uris"]],
                    }
                    for country in response["countries"]
                ]
        except KeyError:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=path,
            )

    async def search_number_availablity(
        self,
        path_params: NumberAvailabilityPathParams,
        params: NumberAvailabilityParams,
    ):
        response = None
        if path_params.type is not None:
            path = build_available_number_path(
                self.account_sid,
                path_params.country_iso,
                params,
                path_params.type,
            )
            response = await self.get.get(url=path)
            return self.construct_response(
                path_params, response["available_phone_numbers"]
            )
        else:
            path = build_available_number_path(
                self.account_sid,
                path_params.country_iso,
                params,
                path_params.types, # type: ignore
            )
            gen_coroutine = partial(self.get.get)
            funcs = list(map(gen_coroutine, path))
            response = await asyncio.gather(*funcs)
            available_phone_numbers = [
                r.get("available_phone_numbers", []) for r in response
            ]
            for i, resource in enumerate(available_phone_numbers):
                for r in resource:
                    r.update(
                        {
                            "type": path_params.types[i], # type: ignore
                        }
                    )

            aggrigated_resource = [
                r for sublist in available_phone_numbers for r in sublist
            ]

            return self.construct_response(
                path_params,
                aggrigated_resource,
            )

    @staticmethod
    def construct_response(path_params, response):
        try:
            return [
                {
                    "type": path_params.type or resource["type"],
                    "dialing_number": resource["phone_number"],
                    "capabilities": resource["capabilities"],
                    "address_requirements": resource["address_requirements"],
                    "region": resource["region"],
                    "locality": resource["locality"],
                    "rate_center": resource["rate_center"],
                    "country_iso": path_params.country_iso,
                }
                for resource in response
            ]
        except KeyError:
            logger.error(f"Response constructing failed in {__name__}")
            return []

    # Get price for specific number type and country
    async def get_country_price(self, country_iso):
        url = f"{self.pricing_url}/PhoneNumbers/Countries/{country_iso}"
        response = await self.get.get(url=url)
        try:
            response["prices"] = response.pop("phone_number_prices")
            response["unit"] = response.pop("price_unit")
            response["country_code"] = response.pop("iso_country")
            return response
        except KeyError:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )

    async def get_number_country(self, number):
        url = f"{self.lookup_url}/PhoneNumbers/{number}"
        response = await self.get.get(url=url)
        try:
            response["country_code"] = response.pop("country_code")
            return response
        except KeyError:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )

    # async def build_nums(self, resources, country_iso, num_type):
    #     "Add price to the numbers and for validation"
    #     price_request = await self.get_price(country_iso) 
    #     price = price_request[num_type]
    #     return [
    #         {
    #             "type": num_type,
    #             "dialing_number": resource["phone_number"],
    #             "capabilities": resource["capabilities"],
    #             "address_requirements": resource["address_requirements"]
    #             if num_type != "local"
    #             else "None",
    #             "region": resource["region"],
    #             "locality": resource["locality"],
    #             "rate_center": resource["rate_center"],
    #             "country_iso": country_iso,
    #             "price": price,
    #         }
    #         for resource in resources
    #     ]

    # Get voice price/min
    async def get_voice_price(self, dest_number, origin_number):
        url = f"{self.pricing_url}/Voice/Numbers/{dest_number}?"
        f"OriginationNumber={origin_number}"
        response = await self.get.get(url=url)
        try:
            return response
        except KeyError:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )

    # Get sms price
    async def get_sms_price(self, country):
        url = f"{self.pricing_url}/Messaging/Countries/{country}"
        response = await self.get.get(url=url)
        try:
            return response
        except KeyError:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )

    # Get voice price by country
    async def get_voice_price_by_country(self, country):
        url = f"{self.pricing_url}/Voice/Countries/{country}"
        response = await self.get.get(url=url)
        try:
            return response
        except KeyError:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )

    # Get recording price
    async def recording_price(self, sid):
        a_sid = self.account_sid
        url = f"{self.base_url}/Accounts/{a_sid}/Recordings/{sid}.json"
        response = await self.get.get(url=url)
        try:
            return response
        except KeyError:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )

    # Get transcription price
    async def transcription_price(self, sid):
        a_sid = self.account_sid
        url = f"{self.base_url}/Accounts/{a_sid}/Transcriptions/{sid}.json"
        response = await self.get.get(url=url)
        try:
            return response
        except KeyError:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )

    # Get country code by phone number
    async def get_code_by_phone(self, phone_no):
        url = f"{self.lookup_url}/PhoneNumbers/{phone_no}"
        response = await self.get.get(url=url)
        try:
            return response["country_code"]
        except KeyError:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )

    async def get_number_price(self, country_iso: str, type: str):
        country_prices = await self.get_country_price(country_iso)
        price = country_prices.get("prices", [])
        key = [each.get("number_type", "").replace(" ", "") for each in price]
        if type.lower() in key:
            type = type
        else:
            type = "National"
        value = [each.get("current_price", "") for each in price]
        prices = dict(zip(key, value))
        # return float(prices[type.lower()])
        data = {"price": float(prices[type.lower()]), "type": type}
        return data

    # async def get_number_base_price(
    #     self, country_iso: str, numbers: typing.List[str]
    # ):
    #     country_prices = await self.get_country_price(country_iso)
    #     price = country_prices.get("prices", [])
    #     key = [each.get("number_type", "").replace(" ", "") for each in price]
    #     for number in numbers:
    #         type = number["type"] # type: ignore
    #         if type.lower() in key:
    #             type = type
    #         else:
    #             type = "National"
    #         value = [
    #             self.number_price_after_commision(
    #                 float(each.get("current_price", ""))
    #             )
    #             for each in price
    #         ]
    #         prices = dict(zip(key, value))
    #         number["price"] = "{:.2f}".format(float(prices[type.lower()])) # type: ignore
    #     return numbers

    # def number_price_after_commision(self, amount: float) -> float:
    #     """
    #     -If the price is less than $3, the same price in Twilio is charged.
    #     -If the price is greater than $3 krispcall will charge 50% extra on the
    #     amount
    #     """
    #     from krispcall.billing.service_layer.helpers.business_rules import (
    #         purchase_number_gt_than_3,
    #         purchase_number_less_than_or_eq_3,
    #     )

    #     purchase_number_commission = 50
    #     actual_amount = ((purchase_number_commission / 100) * amount) + amount
    #     if amount > 3:
    #         round_off_actual_amount = purchase_number_gt_than_3(actual_amount)
    #     else:
    #         round_off_actual_amount = purchase_number_less_than_or_eq_3(
    #             actual_amount
    #         )
    #     return float(round_off_actual_amount)
