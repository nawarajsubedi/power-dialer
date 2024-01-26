import asyncio
import logging
from typing import Any, Dict, List
from pydantic import AnyHttpUrl, parse_obj_as

from krispcall_twilio.twilio_requests import TwilioRequestResource
from krispcall_twilio.type import (
    AddClientsToConference,
    Client,
    ExternalNumberPayload,
    OutboundParticipantPayload,
    AddAgentToCampaign,
    OutboundParticipantPayload,
    CampaignOutboundParticipantPayload,
)
from twilio.twiml.voice_response import VoiceResponse, Dial
from krispcall.common.shortid import ShortId
from krispcall_twilio.type import AddNumberToConference

logger = logging.getLogger("twilio")


class ConferenceResource:
    def __init__(
        self, account_sid, auth_token, base_url, app_url, ring_url, hold_url
    ):
        self.account_sid: str = account_sid
        self.auth_token: str = auth_token
        self.base_url: AnyHttpUrl = base_url
        self.app_url: AnyHttpUrl = app_url
        self.client: TwilioRequestResource = TwilioRequestResource(
            account_sid=self.account_sid, auth_token=self.auth_token
        )
        self._participant_callback: AnyHttpUrl = parse_obj_as(
            AnyHttpUrl, f"{app_url}/twilio_callbacks/events"
        )
        self._conference_url: AnyHttpUrl = parse_obj_as(
            AnyHttpUrl,
            f"{base_url}/Accounts/{account_sid}/Conferences",
        )
        self._transfer_callback: AnyHttpUrl = parse_obj_as(
            AnyHttpUrl, f"{app_url}/twilio_callbacks/transfer"
        )
        self._hold_url: AnyHttpUrl = parse_obj_as(
            AnyHttpUrl,
            hold_url,
        )
        self.ring_url: AnyHttpUrl = parse_obj_as(
            AnyHttpUrl,
            ring_url,
        )
        self.conf_callback: AnyHttpUrl = parse_obj_as(
            AnyHttpUrl, f"{self.app_url}/twilio_callbacks/conference"
        )
        self.campaign_callback: AnyHttpUrl = parse_obj_as(
            AnyHttpUrl, f"{self.app_url}/sales_callbacks/campaigns"
        )
        self.missed_callback: AnyHttpUrl = parse_obj_as(
            AnyHttpUrl, f"{self.app_url}/twilio_callbacks/missed"
        )
        self.campaign_number_callback: AnyHttpUrl = parse_obj_as(
            AnyHttpUrl, f"{self.app_url}/sales_callbacks/campaigns/client"
        )

    async def connect_to_conference(self, friendly_name: str):
        """Returns TWIML to connect to existing conference"""
        response = VoiceResponse()
        dial = Dial()
        dial.conference(
            name=friendly_name,
            start_conference_on_enter=True,
        )
        response.append(dial)
        return response

    async def new_conference(
        self,
        friendly_name: str,
        workspace: ShortId,
        channel: ShortId,
        direction: str,
        end_on_exit: bool = True,
        live: bool = False,
        auto_record: bool = False,
        wait_url: str = None, # type: ignore
    ):
        """
        Returns TWIML for new simple conference.
        """
        response = VoiceResponse()
        callback = (
            f"{self.missed_callback}/"
            f"{workspace}/"
            f"{channel}/"
            f"{friendly_name}"
        )
        dial = Dial(timeout=40)

        if direction == "incoming":
            dial = Dial(timeout=40, action=callback, method="POST")

        dial.conference(
            name=friendly_name,
            wait_url=wait_url or self.ring_url,
            wait_method="GET",
            start_conference_on_enter=True,
            record="record-from-start" if auto_record else None,
            trim="trim-silence" if auto_record else None,
            muted=live,
            end_conference_on_exit=end_on_exit,
            status_callback_event="start end join leave",
            status_callback=f"{self.conf_callback}/{direction}/{workspace}/{friendly_name}",
        )

        response.append(dial)
        return response

    async def campaign_conference(
        self, conference_id: ShortId, callback_data: str, auto_record: bool
    ):
        response = VoiceResponse()
        callback = f"{self.campaign_callback}/{callback_data}"
        dial = Dial(timeout=40)
        dial.conference(
            name=conference_id,
            wait_url=self.ring_url,
            wait_method="GET",
            start_conference_on_enter=True,
            record="record-from-start" if auto_record else None,
            recording_status_callback=f"{self.campaign_callback}/record/{callback_data}",
            # end_conference_on_exit=True,
            status_callback_event="start end join leave",
            status_callback=callback,
        )
        response.append(dial)
        return response

    async def add_agent(
        self,
        data: AddClientsToConference,
        client: ShortId,
        transfer: bool = False,
        transferer: str = None, # type: ignore
    ):
        callback = (
            f"{self._transfer_callback}/"
            f"{data.direction}/"
            f"{data.workspace}/"
            f"{data.channel}/"
            f"{transferer}/"
            f"{data.friendly_name}"
            if transfer
            else f"{self._participant_callback}/"
            f"{data.direction}/"
            f"{data.workspace}/"
            f"{data.channel}/"
            f"{data.friendly_name}"
        )

        # not adding caller id to workaround carrier mismatch
        # caller_id is optional field
        payload = OutboundParticipantPayload(
            To=Client(identity=client, params=data.params).dial_str,
            From=data.caller_id if data.caller_id else data.call_from,
            Label=client,
            StatusCallback=callback, # type: ignore
            EarlyMedia=False,
            EndConferenceOnExit=data.eoe,
        )
        url = f"{self._conference_url}/{data.friendly_name}/Participants.json"
        result = await self.client.post(url=url, payload=payload.as_multi_dict)
        if result.get("call_sid"):
            return {
                "success": True,
                "participant": client,
                "call_sid": result.get("call_sid"),
                "conference": result.get("conference_sid"),
                "status": result.get("status"),
            }
        else:
            return {
                "success": False,
                "code": result.get("code"),
                "message": result.get("message"),
            }

    async def add_campaign_agent(
        self, data: AddAgentToCampaign, client: ShortId
    ):
        callback = (
            f"{self.campaign_callback}/{data.friendly_name}/{data.campaign_id}"
        )
        payload = OutboundParticipantPayload(
            To=Client(identity=client, params=data.params).dial_str,
            From=data.caller_id if data.caller_id else data.call_from,
            Label=client,
            StatusCallback=callback, # type: ignore
            EarlyMedia=False,
            EndConferenceOnExit=True,
        )
        conference = await self.fetch_one(data.friendly_name)
        conference_sid = conference.get("sid") # type: ignore
        url = f"{self._conference_url}/{conference_sid}/Participants.json"
        result = await self.client.post(url=url, payload=payload.as_multi_dict)
        return {
            "participant": client,
            "call_sid": result.get("call_sid"),
            "conference": result.get("conference_sid"),
            "status": result.get("status"),
        }

    async def create_amd_call(
        self, number: str, from_: str, callback_data: str
    ):
        callback = (
            f"{self.app_url}/sales_callbacks/campaigns/client/{callback_data}"
        )
        payload = {
            "To": number,
            "From": from_,
            "AsyncAmdStatusCallback": callback,
            "AsyncAmdStatusCallbackMethod": "POST",
            "AsyncAmd": True,
            "MachineDetection": "Enable",
            "Url": callback,
        }
        call_url = f"{self.base_url}/Accounts/{self.account_sid}/Calls.json"
        response = await self.client.post(url=call_url, payload=payload)
        if not "sid" in response:
            print(response)
            raise Exception("Couldn't place the call")
        return {
            "call_sid": response.get("sid"),
            "status": response.get("status"),
        }

    async def add_campaign_external_number(
        self,
        conference_sid: str,
        number: str,
        from_: str,
        callback_data: str,
    ):
        callback = f"{self.campaign_number_callback}/{callback_data}"

        callback = (
            f"{self.app_url}/sales_callbacks/campaigns/client/{callback_data}"
        )
        payload = CampaignOutboundParticipantPayload(
            To=number,
            From=from_, # type: ignore
            StatusCallback=callback,
            EarlyMedia=False,
            EndConferenceOnExit=True,
            # AsyncAmd=True,
            # AyncAmdStatusCallback=callback,
            # AsyncAmdStatusCallbackMethod="POST",
        )
        url = f"{self._conference_url}/{conference_sid}/Participants.json"
        result = await self.client.post(url=url, payload=payload.as_multi_dict)
        return {
            "participant": number,
            "call_sid": result.get("call_sid"),
            "conference": result.get("conference_sid"),
            "status": result.get("status"),
            "reason_code": result.get("code"),
        }

    async def add_agents(self, data: AddClientsToConference) -> Dict:
        """
        Adds all active agents from data.call_to
        in the conference
        """
        tasks = [
            asyncio.create_task(self.add_agent(data=data, client=client))
            for client in data.call_to
        ]

        results = await asyncio.gather(
            *tasks,
        )
        return results # type: ignore

    async def add_external_number(
        self,
        data: AddNumberToConference,
        transfer: bool = False,
        forward: bool = False,
        transferer: str = None, # type: ignore
    ):
        callback = (
            f"{self._transfer_callback}/"
            f"{data.direction}/"
            f"{data.workspace}/"
            f"{data.channel}/"
            f"{transferer}/"
            f"{data.friendly_name}"
            if transfer
            else f"{self._participant_callback}/"
            f"{data.direction}/"
            f"{data.workspace}/"
            f"{data.channel}/"
            f"{data.friendly_name}"
        )
        # patch_caller_id = data.caller_id if data.caller_id else data.call_from
        # caller_id = (
        #     data.channel_number if forward or transfer else patch_caller_id
        # )
        # payload = OutboundParticipantPayload(
        #     To=data.call_to,
        #     From=caller_id,
        #     Label=data.participant_label,
        #     StatusCallback=callback,
        #     EndConferenceOnExit=data.eoe,
        # )
        # url = f"{self._conference_url}/{data.friendly_name}/Participants.json"
        # response = await self.client.post(
        #     url=url, payload=payload.as_multi_dict
        # )
        payload = ExternalNumberPayload(
            Url=callback,
            StatusCallback=callback, # type: ignore
            To=data.call_to,
            From=data.caller_id,
            CallToken=data.call_token,
        )

        url = f"{self.base_url}/Accounts/{self.account_sid}/Calls.json"
        response = await self.client.post(
            url=url, payload=payload.as_multi_dict
        )
        if response.get("sid"):
            return {
                "success": True,
                "participant": data.call_to,
                "call_sid": response.get("sid"),
                "status": response.get("status"),
                # "conference": response.get("conference_sid"),
            }
        else:
            msg = f"data: {dict(data)}, twi_resp: {response}"
            logger.error("Failed to call. %s", msg, exc_info=1) # type: ignore
            return {
                "success": False,
                "participant": data.call_to,
                # "call_sid": response.get("call_sid"),
                #   "status": response.get("status"),
                # "conference": response.get("conference_sid"),
                "code": response.get("code"),
                "message": response.get("message"),
            }

    async def add_number(
        self,
        data: AddNumberToConference,
        transfer: bool = False,
        forward: bool = False,
        transferer: str = None, # type: ignore
    ):
        callback = (
            f"{self._transfer_callback}/"
            f"{data.direction}/"
            f"{data.workspace}/"
            f"{data.channel}/"
            f"{transferer}/"
            f"{data.friendly_name}"
            if transfer
            else f"{self._participant_callback}/"
            f"{data.direction}/"
            f"{data.workspace}/"
            f"{data.channel}/"
            f"{data.friendly_name}"
        )
        patch_caller_id = data.caller_id if data.caller_id else data.call_from
        caller_id = (
            data.channel_number if forward or transfer else patch_caller_id
        )
        payload = OutboundParticipantPayload(
            To=data.call_to,
            From=caller_id,
            Label=data.participant_label,
            StatusCallback=callback, # type: ignore
            EndConferenceOnExit=data.eoe,
        )
        url = f"{self._conference_url}/{data.friendly_name}/Participants.json"
        response = await self.client.post(
            url=url, payload=payload.as_multi_dict
        )

        if response.get("call_sid"):
            return {
                "success": True,
                "participant": data.call_to,
                "call_sid": response.get("call_sid"),
                "status": response.get("status"),
                "conference": response.get("conference_sid"),
            }
        else:
            msg = f"data: {dict(data)}, twi_resp: {response}"
            logger.error("Failed to call. %s", msg, exc_info=1) # type: ignore
            return {
                "success": False,
                "participant": data.call_to,
                # "call_sid": response.get("call_sid"),
                # "status": response.get("status"),
                # "conference": response.get("conference_sid"),
                "code": response.get("code"),
                "message": response.get("message"),
            }

    async def delete(self, friendly_name):
        url = f"{self._conference_url}/{friendly_name}.json"
        response = await self.client.delete(url=url)
        return response

    async def fetch_one(self, friendly_name: str):
        url = f"{self._conference_url}.json?FriendlyName={friendly_name}"
        response = await self.client.get(url=url)
        if response.get("conferences"):
            return response.get("conferences")[0]
        else:
            return response

    async def fetch_conference(self, friendly_name: str):
        """Returns conference object response"""
        url = f"{self.base_url}/Accounts/{self.account_sid}/Conferences.json?FriendlyName={friendly_name}"
        response = await self.client.get(url=url)
        return response

    async def fetch_participants(self, conference_sid: str):
        """Returns conference participants"""
        url = f"{self.base_url}/Accounts/{self.account_sid}/Conferences/{conference_sid}/Participants.json"
        response = await self.client.get(url=url)
        return response

    async def fetch_all_active(self):
        url = f"{self._conference_url}.json?Status=in-progress"
        response = await self.client.get(url=url)
        return response

    async def complete(self, friendly_name: str):
        url = f"{self.base_url}/Accounts/{self.account_sid}/Conferences/{friendly_name}.json"
        payload = {"Status": "completed"}
        response = await self.client.post(url=url, payload=payload)
        return response

    async def hold_conference_by_friendly_name(
        self, friendly_name: str, hold: bool
    ):
        url = f"{self.base_url}/Accounts/{self.account_sid}/Conferences/{friendly_name}.json"

        payload = {"Hold": hold, "HoldUrl": self._hold_url}
        response = await self.client.post(url=url, payload=payload)
        return response

    async def hold_call_by_label(
        self, friendly_name: str, label: str, hold: bool = True
    ):
        payload = {"Hold": hold, "HoldUrl": self._hold_url}
        conference = await self.fetch_one(friendly_name=friendly_name)
        sid = conference.get("conferences")[0]["sid"]
        participant = await self.fetch_participant(sid=sid, label=label)
        url = f"{self._conference_url}/{sid}/Participants/{participant}.json"

        # TO : DO - Add a custom hold endpoint and allow custom hold music
        response = await self.client.post(url=url, payload=payload)
        return response

    async def hold_call_by_sid(self, friendly_name: str, sid: str):
        url = f"{self._conference_url}/{friendly_name}/Participants/{sid}.json"
        payload = {"Hold": True, "HoldUrl": self._hold_url}
        response = await self.client.post(url=url, payload=payload)
        return response

    async def wait_participant_by_sid(
        self, conference_friendly_name: str, call_sid: str, hold: bool = True
    ):
        conference = await self.fetch_one(
            friendly_name=conference_friendly_name
        )
        # assuming there is only conference when we fetch one
        sid = conference.get("sid")
        payload = {"Hold": hold, "HoldUrl": self._hold_url}
        url = f"{self._conference_url}/{sid}/Participants/{call_sid}.json"
        response = await self.client.post(url=url, payload=payload)
        return response

    async def fetch_participant(self, sid: str, label: str):
        url = f"{self._conference_url}/{sid}/Participants/{label}.json"
        response = await self.client.get(url=url)
        try:
            return response["call_sid"]
        except KeyError as e:
            raise KeyError(
                "Participant not found. Please check the participant label and conference sid"
            ) from e

    async def hold_participant_by_id(
        self,
        conference_sid: str,
        participant_sid: str,
        hold: bool = True,
        custom_url: str = None, # type: ignore
    ):
        payload = {"Hold": hold, "HoldUrl": custom_url or self._hold_url}
        url = f"{self._conference_url}/{conference_sid}/Participants/{participant_sid}.json"
        response = await self.client.post(url=url, payload=payload)
        return response

    async def update_eoe_by_sid(
        self, conference_sid: str, participant_sid: str, eoe: bool
    ):
        """Updates End conference on exit status of participant"""
        payload = {"EndConferenceOnExit": eoe}
        url = f"{self._conference_url}/{conference_sid}/Participants/{participant_sid}.json"
        response = await self.client.post(url=url, payload=payload)
        return response

    async def active_participants_by_id(self, conference_sid: str):
        """Get participants with active status"""
        url = f"{self._conference_url}/{conference_sid}/Participants.json?Status=in-progress"
        response = await self.client.get(url=url)
        try:
            return response.get("participants")
        except KeyError as e:
            raise KeyError(
                "Participant not found. Please check the participant label and conference sid"
            ) from e

    async def terminate_by_id(self, conference_sid: str):
        """Mark the conference status as complete"""
        url = f"{self._conference_url}/{conference_sid}.json"
        payload = {"Status": "completed"}
        response = await self.client.post(url=url, payload=payload)
        return response

    async def terminate_by_name(self, conference_name: str):
        """End conference with friendly name"""
        conference_ = await self.fetch_one(friendly_name=conference_name)
        sid = conference_.get("sid")
        response = await self.terminate_by_id(sid)
        return response

    async def active_participants_by_name(self, conference_name: str):
        """Get participants with active status"""
        url = f"{self._conference_url}/{conference_name}/Participants.json?Status=in-progress"
        response = await self.client.get(url=url)
        try:
            return response.get("participants")
        except KeyError as e:
            raise KeyError(
                "Participant not found. Please check the participant label and conference sid"
            ) from e

    async def fetch_recordings(self, sid: str):
        url = f"{self._conference_url}/{sid}/Recordings.json"
        response = await self.client.get(url=url)
        return response

    async def fetch_by_sid(self, sid: str):
        url = f"{self._conference_url}/{sid}.json"
        response = await self.client.get(url=url)
        return response
