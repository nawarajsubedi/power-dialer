"""
Twilio docs: https://www.twilio.com/docs/phone-numbers/regulatory/api/end-users
"""

from krispcall.twilio.twilio_requests import TwilioRequestResource

NUMBERS_URL = "https://numbers.twilio.com/v2"


class EndUserResource:
    def __init__(self, account_sid, auth_token):
        self.base_url = f"{NUMBERS_URL}/RegulatoryCompliance/EndUsers"
        self.auth_token = auth_token
        self.account_sid = account_sid
        self.request = TwilioRequestResource(account_sid, auth_token)

    async def create(self, end_user):
        """create a new End-User of a phone number
        Args:
            FriendlyName (Required)
            Type (Required): individual or business
            Attributes
        Returns:
            sid
            account_sid
            friendly_name
            type
        """
        url = self.base_url
        response = await self.request.post(url, payload=end_user)
        return response

    async def fetch_one(self, sid: str):
        url = f"{self.base_url}/{sid}"
        response = await self.request.get(url)
        return response

    async def delete(self, sid: str):
        url = f"{self.base_url}/{sid}"
        response = await self.request.delete(url)
        return response

    async def types(self):
        url = f"{self.base_url}/EndUserTypes"
        response = await self.request.get(url)
        return response
