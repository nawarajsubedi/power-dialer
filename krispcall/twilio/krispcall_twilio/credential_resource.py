from .twilio_requests import TwilioRequestResource
from twilio.base.exceptions import TwilioRestException


class CredentialsResource:
    def __init__(
        self,
        account_sid,
        auth_token,
        fcm_api_key,
        ios_cert,
        ios_key,
        ios_app_env,
        twilio_edge=None,
        twilio_region=None,
    ):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.base_url = (
            f"https://conversations.{twilio_edge}.{twilio_region}.twilio.com/v1/Credentials"
            if twilio_edge and twilio_region
            else "https://conversations.twilio.com/v1/Credentials"
        )
        self.client = TwilioRequestResource(
            account_sid=account_sid, auth_token=auth_token
        )
        self.fcm_key = fcm_api_key
        self.ios_cert = ios_cert
        self.ios_key = ios_key
        self.sandbox = True if ios_app_env == "sandbox" else False

    async def list_all_credentials(self):

        response = await self.client.get(url=self.base_url)
        try:
            return response
        except KeyError as e:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=self.base_url,
            ) from e

    async def create_android(self, friendly_name: str):
        payload = {
            "FriendlyName": friendly_name,
            "Type": "fcm",
            "Secret": self.fcm_key,
        }
        response = await self.client.post(url=self.base_url, payload=payload)
        try:
            return response["sid"]
        except KeyError as e:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=self.base_url,
            ) from e

    # Delete Android
    async def delete_credential(self, sid: str):
        url = f"{self.base_url}/{sid}"
        try:
            await self.client.delete(url=url)
        except Exception:
            pass

    async def create_ios(self, friendly_name: str):
        payload = {
            "FriendlyName": friendly_name,
            "Type": "apn",
            "Certificate": self.ios_cert,
            "PrivateKey": self.ios_key,
        }
        if self.sandbox:
            payload["Sandbox"] = True
        response = await self.client.post(url=self.base_url, payload=payload)
        try:
            return response["sid"]
        except KeyError as e:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=self.base_url,
            ) from e
