from typing import Union
from pydantic import SecretStr, AnyHttpUrl
from .twilio_requests import TwilioRequestResource
from twilio.base.exceptions import TwilioRestException


class RecordingsResource:
    def __init__(
        self,
        account_sid: Union[SecretStr, SecretStr],
        auth_token: Union[SecretStr, SecretStr],
        base_url: AnyHttpUrl,
        app_url: AnyHttpUrl,
    ):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.base_url = base_url
        self.app_url = app_url
        self.request_client: TwilioRequestResource = TwilioRequestResource(
            account_sid=account_sid, auth_token=auth_token
        )

    async def start_recording(self, conference_sid):
        """Start conference recording. Not supported by twilio yet in stable
        @params : conference_sid
        """
        url: str = (
            f"{self.base_url}/Accounts/{self.account_sid}"
            f"/Conferences/{conference_sid}/Recordings.json"
        )
        # payload = {
        #     "RecordingStatusCallback": f"{self.app_url}/twilio_callbacks"
        #     f"/recording-status-callback/{workspace_sid}",
        #     "trasncribe": True,
        # }

        response = await self.request_client.post(url=url)
        if response["status"] == "in-progress":
            return response
        else:
            raise TwilioRestException(
                msg=response["message"],
                status=response["status"],
                uri=response["more_info"],
            )

    async def resume_recording(self, conference_sid):
        """Resume the stopped conference recording
        @params : conference_sid
        """
        url: str = (
            f"{self.base_url}/Accounts/{self.account_sid}"
            f"/Conferences/{conference_sid}/Recordings/Twilio.CURRENT.json"
        )

        # payload is required to specify call recording
        # channels and status call back for events
        payload = {
            "Status": "in-progress",
        }

        response = await self.request_client.post(url=url, payload=payload)
        if response["status"] == "in-progress":
            return response
        # manually checking for recording resource
        # message for recording resource not
        # eligible for recording
        # when the recording hasn't started yet
        # TODO: handle the error more gracefully
        elif response["code"] == 21220:
            return response
        else:
            raise TwilioRestException(
                msg=response["message"],
                status=response["status"],
                uri=response["more_info"],
            )

    async def pause_recording(self, conference_sid):
        """Pause the conference recording.
        @params :: Conference sid
        """

        url: str = (
            f"{self.base_url}/Accounts/{self.account_sid}"
            f"/Conferences/{conference_sid}/Recordings/Twilio.CURRENT.json"
        )
        payload = {
            "Status": "paused",
        }
        response = await self.request_client.post(url=url, payload=payload)
        if response["status"] == "paused":
            return response
        elif response["code"] == 21220:
            return response
        else:
            raise TwilioRestException(
                msg=response["message"],
                status=response["status"],
                uri=response["more_info"],
            )

    async def stop_recording(self, conference_sid):
        url: str = (
            f"{self.base_url}/Accounts/{self.account_sid}"
            f"/Conferences/{conference_sid}/Recordings/Twilio.CURRENT.json"
        )
        payload = {
            "Status": "stopped",
        }
        response = await self.request_client.post(url=url, payload=payload)
        if response["status"] == "stopped":
            return response
        elif response["code"] == 21220:
            return response
        else:
            raise TwilioRestException(
                msg=response["message"],
                status=response["status"],
                uri=response["more_info"],
            )

    async def delete_recording(self, url):
        response = await self.request_client.delete(url=url)
        print(
            response,
        )
        if not response:
            return response
        else:
            raise TwilioRestException(
                msg=response["message"],
                status=response["status"],
                uri=response["more_info"],
            )
