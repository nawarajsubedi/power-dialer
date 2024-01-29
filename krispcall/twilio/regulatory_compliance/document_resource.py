"""
Supporting Documents resource of Twilio's Regulatory Compliance APIs allows
you to create new Supporting Documents with metadata to fulfill Regulations

Twilio docs:
    https://www.twilio.com/docs/phone-numbers/regulatory/api/supporting-documents
"""

from krispcall.twilio.twilio_requests import TwilioRequestResource

NUMBERS_URL = "https://numbers.twilio.com/v2"


class DocumentResource:
    def __init__(self, account_sid, auth_token):
        self.base_url = (
            f"{NUMBERS_URL}/RegulatoryCompliance/SupportingDocuments"
        )
        self.auth_token = auth_token
        self.account_sid = account_sid
        self.request = TwilioRequestResource(account_sid, auth_token)

    async def create(self, document):
        """
        Args:
            FriendlyName (Required)
            Type (Required)
            Attributes
            File
        Returns:
            sid
            account_sid
            friendly_name
            mime_type
            status: draft/pending-review/rejected/approved/expired
            type
            attributes
        """
        url = self.base_url
        response = self.request.post(url=url, payload=document)
        return response

    async def update(self, sid: str, document):
        url = f"{self.base_url}/{sid}"
        response = self.request.post(url=url, payload=document)
        return response

    async def delete(self, sid: str):
        url = f"{self.base_url}/{sid}"
        response = self.request.delete(url=url)
        return response

    async def types(self):
        url = f"{self.base_url}/SupportingDocumentTypes"
        response = self.request.get(url=url)
        return response
