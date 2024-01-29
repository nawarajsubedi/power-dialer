"""
Twilio docs: https://www.twilio.com/docs/phone-numbers/regulatory/api/bundles
"""

from krispcall.twilio.twilio_requests import TwilioRequestResource
from krispcall.twilio.endpoints import convert_dict_to_pascal_case
from urllib.parse import urlencode

NUMBERS_URL = "https://numbers.twilio.com/v2"


class BundlesResource:
    def __init__(self, account_sid, auth_token):
        self.base_url = f"{NUMBERS_URL}/RegulatoryCompliance/Bundles"
        self.auth_token = auth_token
        self.account_sid = account_sid
        self.request = TwilioRequestResource(account_sid, auth_token)

    async def create(self, bundle):
        """create a new Bundle that will contain all the information required
        to follow local telco Regulations

        Args:
            FriendlyName (Required)
            Email (Required)
            StatusCallback
            RegulationSid
            IsoCountry
            EndUserType: individual/business
            NumberType

        Returns:
            sid
            account_sid
            friendly_name
            regulation_sid
            status: draft/pending-review/in-review/
                twilio-rejected/twilio-approved
            email
            status_callback
            valid_until
            links
        """
        url = self.base_url
        payload = convert_dict_to_pascal_case(bundle)
        return await self.request.post(url, payload)

    async def update(self, sid: str):
        """
        Args:
            sid (str): Bundle resource id after it was created
        """
        url = f"{self.base_url}/{sid}"
        response = await self.request.post(url)
        return response

    async def delete(self, sid: str):
        url = f"{self.base_url}/{sid}"
        response = await self.request.delete(url)
        return response

    async def all(self):
        url = self.base_url
        response = await self.request.get(url)
        return response

    async def get_bundle_from_country(self, iso_country: str):
        url = self.base_url
        response = await self.request.get(f"{url}?IsoCountry={iso_country}")
        return response

    async def regulations(self, params):
        params = convert_dict_to_pascal_case(params)
        url = f"{NUMBERS_URL}/RegulatoryCompliance/Regulations"
        query = urlencode(params)
        if query:
            url = f"{url}?{query}"
        response = await self.request.get(url)
        return response.get("results", "")

    async def regulation_detail(self, sid):
        url = f"{NUMBERS_URL}/RegulatoryCompliance/Regulations/{sid}"
        return await self.request.get(url)
