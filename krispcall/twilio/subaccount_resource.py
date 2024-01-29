from .twilio_requests import TwilioRequestResource
from typing import Dict, Union
from pydantic.types import SecretStr
from twilio.base.exceptions import TwilioRestException


class SubAccountResource:
    def __init__(
        self,
        account_sid: Union[SecretStr, SecretStr],
        auth_token: Union[SecretStr, SecretStr],
        base_url,
    ):
        self._account_sid = account_sid
        self._auth_token = auth_token
        self.base_url = base_url
        self._post = TwilioRequestResource(
            account_sid=self._account_sid, auth_token=self._auth_token
        )

    async def create(self, name: str) -> Dict:
        """
        Creates subaccount with master client.
        @requires: name -> str
        """
        if not name or name == "":
            raise ValueError("Invalid friendly name")
        payload = {
            "FriendlyName": name,
        }
        url = f"{self.base_url}/Accounts.json"
        response = await self._post.post(url=url, payload=payload)
        try:
            return {
                "sid": response["sid"],
                "auth_token": response["auth_token"],
            }
        except KeyError as e:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            ) from e

    async def create_client_access_keys(self, sub_account_sid: str) -> Dict:
        """
        Creates client access tokens for the sub account.
        @requires: sub account_sid
        @returns : cPaas SDK authentication object
        """
        url = f"{self.base_url}/Accounts/{sub_account_sid}/Keys.json"

        response = await self._post.post(url=url)
        try:
            key_sid = response["sid"]
            key_secret = response["secret"]
            return {"key_sid": key_sid, "key_secret": key_secret}
        except KeyError as e:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            ) from e

    async def delete(self, sub_account_sid: str) -> str:
        """
        Deletes sub account with sid
        @requires: sub_account_sid

        """
        payload = {"Status": "closed"}
        url = f"{self.base_url}/Accounts/{sub_account_sid}.json"
        response = await self._post.post(url=url, payload=payload)
        if "status" in response:
            return response
        else:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )

    async def move_phone_number_to_subaccount(
        self, sub_account_sid: str, phone_number_sid: str
    ):
        """
        Move numbers from one/main account to sub account.
        Needs a master client

        """
        payload = {"AccountSid": sub_account_sid}
        url = (
            f"{self.base_url}/Accounts/{self._account_sid}"
            f"/IncomingPhoneNumbers/{phone_number_sid}.json"
        )
        response = await self._post.post(url=url, payload=payload)

        if "sid" in response:
            return response
        else:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )

    async def get(self, subaccount_sid: str):
        url = f"{self.base_url}/Accounts/{subaccount_sid}.json"
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

    async def suspend(self, subaccount_sid: str):
        payload = {"Status": "suspended"}
        url = f"{self.base_url}/Accounts/{subaccount_sid}.json"
        response = await self._post.post(url=url, payload=payload)
        if "sid" in response:
            return response
        else:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )

    async def re_activate_subaccount(self, subaccount_sid: str):
        payload = {"Status": "active"}
        url = f"{self.base_url}/Accounts/{subaccount_sid}.json"
        response = await self._post.post(url=url, payload=payload)

        print("********** response from reactivate subaccount *****", response)
        if "sid" in response:
            return response
        else:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )

    async def rename(self, title: str, sid: str):
        payload = {"FriendlyName": title}
        url = f"{self.base_url}/Accounts/{sid}.json"
        response = await self._post.post(url=url, payload=payload)
        return response
