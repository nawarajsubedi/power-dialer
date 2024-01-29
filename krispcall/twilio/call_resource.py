from loguru import logger
import json
from pydantic import parse_obj_as, AnyHttpUrl
from krispcall.common.utils.shortid import ShortId
from twilio.jwt.access_token import AccessToken
from twilio.twiml.voice_response import VoiceResponse, Dial
from twilio.jwt.access_token.grants import VoiceGrant
from typing import Dict, List
from .twilio_requests import TwilioRequestResource
from twilio.base.exceptions import TwilioRestException
from .conference_resource import ConferenceResource
from uuid import UUID
import asyncio

from .type import Client


class CallResource:
    def __init__(
        self,
        account_sid,
        auth_token,
        api_key,
        api_secret,
        outgoing_application_sid,
        base_url,
        app_url,
        ios_push_key,
        android_push_key,
        ring_url,
        hold_url,
    ):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.api_key = api_key
        self.api_secret = api_secret
        self.outgoing_application_sid = outgoing_application_sid
        self.base_url = base_url
        self.app_url = app_url
        self.ios_push_key = ios_push_key
        self.android_push_key = android_push_key
        self.client = TwilioRequestResource(
            account_sid=self.account_sid,
            auth_token=self.auth_token,
        )
        self.conference = ConferenceResource(
            account_sid=self.account_sid,
            auth_token=self.auth_token,
            base_url=self.base_url,
            app_url=self.app_url,
            ring_url=ring_url,
            hold_url=hold_url,
        )
        self.campaign_agent_callback: AnyHttpUrl = parse_obj_as(
            AnyHttpUrl, f"{self.app_url}/sales_callbacks/campaigns/agent"
        )

    async def generate_access_tokens(
        self, identity: str, platform: str, ttl: int
    ):
        # platform = "iphone"
        # if platform.lower() == "iphone":
        #     identity = "test_4_device" + "_ios"
        token = AccessToken(
            self.account_sid,
            self.api_key,
            self.api_secret,
            identity=identity,
            ttl=ttl,
        )
        if platform is None or platform == "web" or platform == "hubspot":
            voice_grant = VoiceGrant(
                outgoing_application_sid=self.outgoing_application_sid,
                incoming_allow=True,
            )
        if platform == "android":
            voice_grant = VoiceGrant(
                outgoing_application_sid=self.outgoing_application_sid,
                incoming_allow=True,
                push_credential_sid=self.android_push_key,
            )

        elif platform == "iphone":
            voice_grant = VoiceGrant(
                outgoing_application_sid=self.outgoing_application_sid,
                incoming_allow=True,
                push_credential_sid=self.ios_push_key,
            )
        token.add_grant(voice_grant) # type: ignore
        return token.to_jwt()

    async def outgoing_call_handler(
        self,
        call_to: str,
        call_from: str,
        workspace_sid: str,
        channel_sid: str,
        auto_record: bool,
        caller_id: str,
        platform: str = None, # type: ignore
    ):
        response = VoiceResponse()
        BRIDGE = platform != "mobile"
        if auto_record:
            dial = Dial(
                callerId=caller_id or call_from,
                timeout=30,
                answerOnBridge=BRIDGE,
                record="record-from-answer-dual",
                transcribe=True,
                transcribe_callback=(
                    f"{self.app_url}/twilio_callbacks/transcriptions-handler"
                ),
                recording_status_callback=f"{self.app_url}/twilio_callbacks"
                f"/recording-status-callback/{workspace_sid}",
                trim="trim-silence",
                action=(
                    f"{self.app_url}/twilio_callbacks/terminations/"
                    f"outgoing/{workspace_sid}/{channel_sid}"
                ),
            )

        else:
            dial = Dial(
                callerId=caller_id or call_from,
                timeout=30,
                answerOnBridge=BRIDGE,
                action=(
                    f"{self.app_url}/twilio_callbacks/terminations/"
                    f"outgoing/{workspace_sid}/{channel_sid}"
                ),
            )

        dial.number(
            phone_number=call_to,
            status_callback=(
                f"{self.app_url}/twilio_callbacks/call_events/{workspace_sid}"
            ),
            status_callback_event=("initiated ringing answered completed"),
            status_callback_method="POST",
        )

        response = response.append(dial)
        return response

    async def incoming_call_handler(
        self,
        call_to: List,
        call_from: str,
        workspace_sid: str,
        channel_sid: str,
        auto_record: bool,
        params: Dict = None,  # type: ignore
        external_forward: bool = False,
        simultaneous_dial: bool = False,
        external_number: str = None, # type: ignore
        welcome_recording_url: str = None, # type: ignore
    ):
        response = VoiceResponse()
        # Play :
        # Create a response.play attribute
        # to execute before the dial
        # provide welcome msg
        if welcome_recording_url and welcome_recording_url != "recording_url":
            response.play(url=welcome_recording_url)
        if auto_record:
            dial = Dial(
                callerId=call_from,
                timeout=30,
                transcribe=True,
                transcribe_callback=(
                    f"{self.app_url}/twilio_callbacks/transcriptions-handler"
                ),
                method="POST",
                action=(
                    f"{self.app_url}/twilio_callbacks/terminations/incoming/"
                    f"{workspace_sid}/{channel_sid}"
                ),
                record="record-from-answer-dual",
                recording_status_callback=f"{self.app_url}/twilio_callbacks"
                f"/recording-status-callback/{workspace_sid}",
                trim="trim-silence",
            )
        else:
            dial = Dial(
                callerId=call_from,
                method="POST",
                timeout=30,
                action=(
                    f"{self.app_url}/twilio_callbacks/terminations/incoming/"
                    f"{workspace_sid}/{channel_sid}"
                ),
            )
        # if forwarding is enabled
        if external_forward and not simultaneous_dial:
            number = dial.number(
                external_number,
                status_callback_event=("initiated ringing answered completed"),
                status_callback=f"{self.app_url}/twilio_callbacks/call_events/"
                f"{workspace_sid}",
            )
            # dial = dial.append(number)
        elif external_forward and simultaneous_dial:
            number = dial.number(
                external_number,
                status_callback_event=("initiated ringing answered completed"),
                status_callback=f"{self.app_url}/twilio_callbacks/call_events/"
                f"{workspace_sid}",
            )
            for agent_id in call_to:
                client = dial.client(
                    identity=agent_id,
                    status_callback=(
                        f"{self.app_url}/twilio_callbacks"
                        f"/call_events/"
                        f"{workspace_sid}"
                    ),
                    status_callback_event=(
                        "initiated ringing answered completed"
                    ),
                    status_callback_method="POST",
                )
                if params is not {}:
                    [
                        client.parameter(name=k, value=v or "None") # type: ignore
                        for (k, v) in params.items()
                    ]
            # dial = dial.append(client)
        else:
            for agent_id in call_to:
                client = dial.client(
                    identity=agent_id,
                    status_callback=(
                        f"{self.app_url}/twilio_callbacks"
                        f"/call_events/"
                        f"{workspace_sid}"
                    ),
                    status_callback_event=(
                        "initiated ringing answered completed"
                    ),
                    status_callback_method="POST",
                )
                if params is not {}:
                    [
                        client.parameter(name=k, value=v or "None") # type: ignore
                        for (k, v) in params.items()
                    ]
        response = response.append(dial)
        return response

    # To do : Do all the fallback methods and URLs as optional params

    async def campaign_add_participant(
        self,
        call_to: str,
        call_from: str,
        callback_data: str,  # url safe encoded data
        twiml: str,
        params: Dict,
    ):
        """Adds web or mobile agent with the given twiml.
        Calls the browser/mobile agent with conference twiml
        here
        """
        callback = f"{self.campaign_agent_callback}/{callback_data}"
        payload = dict(
            Twiml=twiml,
            From=call_from,
            To=Client(identity=call_to, params=params).dial_str,
            StatusCallback=callback,
            StatusCallBackEvents="intiated ringing answered completed",
        )
        url = f"{self.base_url}/Accounts/{self.account_sid}/Calls.json"
        response = await self.client.post(url, payload)
        if "sid" in response:
            return response
        else:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )

    async def place_outbound_call(
        self, call_to: str, call_from: str, handler_url: str
    ):
        payload = {
            "Url": f"{self.app_url}/twilio_callbacks/call/outgoing",
            "To": call_to,
            "From": call_from,
        }
        url = f"{self.base_url}/Accounts/{self.account_sid}/Calls.json"
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

    # async def send_event_to_call(self, call_sid: str, msg: Dict):
    #     url = (
    #         f"https://api.twilio.com/2010-04-01/Accounts/"
    #         f"{self.account_sid}/Calls/{call_sid}/UserDefinedMessages.json"
    #     )
    #     data = {
    #         "Content": json.dumps(msg),
    #     }
    #     response = await self.client.post(url=url, payload=data)
    #     if "sid" in response:
    #         return response
    #     else:
    #         raise TwilioRestException(
    #             msg=response["message"],
    #             code=response["code"],
    #             status=response["status"],
    #             uri=url,
    #         )

    async def get_call_details(self, call_sid: str):
        url = (
            f"https://api.twilio.com/2010-04-01/Accounts/"
            f"{self.account_sid}/Calls/{call_sid}.json"
        )
        call_info = await self.client.get(url=url)
        if "sid" in call_info:
            return call_info
        else:
            raise TwilioRestException(
                msg=call_info["message"],
                code=call_info["code"],
                status=call_info["status"],
                uri=url,
            )

    async def send_event_to_call(self, call_sid: str, msg: Dict):
        url = (
            f"https://api.twilio.com/2010-04-01/Accounts/"
            f"{self.account_sid}/Calls/{call_sid}/UserDefinedMessages.json"
        )
        data = {
            "Content": json.dumps(msg),
        }
        response = await self.client.post(url=url, payload=data)
        if "sid" in response:
            return response
        else:
            raise TwilioRestException(
                msg=response["message"],
                code=response["code"],
                status=response["status"],
                uri=url,
            )

    async def get_call_status(self, call_sid: str) -> str:
        call_info = await self.get_call_details(call_sid=call_sid)
        return call_info["status"]

    async def get_call_details_from_parent_call_sid(
        self, parent_call_sid: str
    ):
        url = (
            f"https://api.twilio.com/2010-04-01/Accounts/"
            f"{self.account_sid}"
            f"/Calls.json?ParentCallSid={parent_call_sid}"
        )
        call_info_list = await self.client.get(url=url)
        if "calls" in call_info_list:
            return call_info_list["calls"]
        else:
            raise TwilioRestException(
                msg=call_info_list["message"],
                code=call_info_list["code"],
                status=call_info_list["status"],
                uri=url,
            )

    # Play :
    # Replace : response.say with response.play
    async def record_voice_mail(
        self,
        workspace_sid: ShortId,
        channel_sid: ShortId,
        conference_name: str,
        recording_url: str = None, # type: ignore
        transcribe: bool = False,
    ):
        response = VoiceResponse()
        msg = (
            "I'm unable to answer your call right now."
            " Thank you."
            " Leave your message after the beep,"
            " and I'll return your call as soon as I'm free."
        )
        if recording_url and recording_url != "recording_url":
            response.play(recording_url)
        else:
            response.say(msg)
        response.pause(length=1)
        record_url = (
            f"{self.app_url}/twilio_callbacks/voicemail/status_callback/"
            f"{workspace_sid}/{channel_sid}/{conference_name}"
        )
        if transcribe:
            logger.info("gone here")
            response.record(
                max_length=60 * 6,  # 6 minutes
                recording_status_callback=record_url,
                transcribe=True,
                transcribe_callback=(
                    f"{self.app_url}/twilio_callbacks/transcriptions-handler/"
                    f"{conference_name}"
                ),
                recording_status_callback_event="completed",
            )
        else:
            response.record(
                max_length=60 * 6,  # 6 minutes
                recording_status_callback=record_url,
                recording_status_callback_event="completed",
            )
        response.hangup()
        return response

    async def redirect_call_to_voicemail(
        self,
        call_sid: str,
        workspace_sid: ShortId,
        channel_sid: ShortId,
        recording_url: str,
        conference_name: str,
        transcribe: bool,
    ):
        url = (
            f"https://api.twilio.com/2010-04-01/Accounts/"
            f"{self.account_sid}/Calls/{call_sid}.json"
        )
        payload = {
            "Twiml": await self.record_voice_mail(
                workspace_sid=ShortId.with_uuid(workspace_sid), # type: ignore
                channel_sid=ShortId.with_uuid(channel_sid), # type: ignore
                recording_url=recording_url,
                conference_name=conference_name,
                transcribe=transcribe,
            )
        }
        logger.info(f"payload {payload}")
        redirect = await self.client.post(url=url, payload=payload)
        return redirect

    # async def cold_transfer(
    #     self,
    #     call_sid: str,
    #     destination,
    #     caller_id,
    #     direction,
    #     workspace_sid,
    #     channel_sid,
    #     params,
    # ):
    #     url = (
    #         f"https://api.twilio.com/2010-04-01/Accounts/"
    #         f"{self.account_sid}/Calls/{call_sid}.json"
    #     )
    #     payload = {
    #         "Twiml": await self.conference.dial_transfer(
    #             destination=destination,
    #             caller_id=caller_id,
    #             direction=direction,
    #             workspace_sid=workspace_sid,
    #             channel_sid=channel_sid,
    #             params=params,
    #         )
    #     }
    #     transfer = await self.client.post(url=url, payload=payload)
    #     return transfer

    # # async def put_call_on_hold(
    #     self,
    #     call_sid,
    #     workspace_sid,
    #     identity,
    #     direction,
    #     conversation_sid,
    # ):
    #     response = VoiceResponse()
    #     child_call = await self.get_call_details_from_parent_call_sid(
    #         parent_call_sid=call_sid
    #     )
    #     url = (
    #         f"{self.app_url}/twilio_callbacks/hold-url/outgoing/"
    #         f"{workspace_sid}/{conversation_sid}"
    #     )
    #     if direction == "incoming":
    #         url = (
    #             f"{self.app_url}/twilio_callbacks/hold-url/incoming/"
    #             f"{workspace_sid}/{conversation_sid}"
    #         )

    #     response.enqueue(wait_url=url, name=identity)

    #     url = (
    #         f"https://api.twilio.com/2010-04-01/Accounts/"
    #         f"{self.account_sid}/Calls/{child_call[0].get('sid')}.json"
    #     )
    #     payload = {"Twiml": str(response)}

    #     # Execute this twiml for the suspended agent

    #     # now, place the callee on hold
    #     callee_hold = await self.client.post(url=url, payload=payload)
    #     return callee_hold

    async def remove_call_from_hold(
        self,
        call_sid,
        workspace_sid,
        channel_sid,
        identity,
        direction,
        params,
    ):
        child_call = await self.get_call_details_from_parent_call_sid(
            parent_call_sid=call_sid
        )

        # hangup the agents ongoing music
        agent_sid = call_sid
        callee_sid = child_call[0].get("sid")
        if direction.lower() == "inbound":
            agent_sid = child_call[0].get("sid")
            callee_sid = call_sid

        hangup = await self.hangup_call(call_sid=agent_sid)
        url = (
            f"https://api.twilio.com/2010-04-01/Accounts/"
            f"{self.account_sid}/Calls/{callee_sid}.json"
        )

        response = VoiceResponse()
        dial = Dial(
            method="POST",
            action=(
                f"{self.app_url}/twilio_callbacks/terminations/incoming/"
                f"{workspace_sid}/{channel_sid}"
            ),
            ring_tone="none",
        )
        client = dial.client(
            identity=identity,
        )
        if params is not {}:
            [
                client.parameter(name=k, value=v or "None") # type: ignore
                for (k, v) in params.items()
            ]
        response = response.append(dial)
        payload = {"Twiml": str(response)}

        call_hold_off = await self.client.post(url=url, payload=payload)
        return [call_hold_off, hangup]

    async def hangup_call(self, call_sid):
        url = (
            f"https://api.twilio.com/2010-04-01/Accounts/"
            f"{self.account_sid}/Calls/{call_sid}.json"
        )
        payload = {"Status": "completed"}
        return await self.client.post(url=url, payload=payload)

    async def hangup_multiple_calls(self, call_sids: List[str]):
        tasks = [
            asyncio.gather(self.hangup_call(call_sid))
            for call_sid in call_sids
        ]

    async def hangup_active_child_call(self, call_sid):
        child_calls = await self.get_call_details_from_parent_call_sid(
            parent_call_sid=call_sid
        )
        child_call_sids = [calls.get("sid") for calls in child_calls]
        payload = {"Status": "completed"}
        url = (
            f"https://api.twilio.com/2010-04-01/Accounts/"
            f"{self.account_sid}/Calls/{child_call_sids[0]}.json"
        )
        return await self.client.post(url=url, payload=payload)

    async def end_queue(self, call_sid):
        # Hangup the main call
        await self.hangup_call(call_sid=call_sid)

        # Hangup active child calls
        await self.hangup_active_child_call(call_sid=call_sid)

    async def drop_voicemail(self, call_sid: str, voicemail_url: str):
        url = (
            f"https://api.twilio.com/2010-04-01/Accounts/"
            f"{self.account_sid}/Calls/{call_sid}.json"
        )
        response = VoiceResponse()
        response.play(url=voicemail_url)
        payload = {"Twiml": str(response)}
        return await self.client.post(url=url, payload=payload)

    async def play_music(self, call_sid):
        url = (
            f"https://api.twilio.com/2010-04-01/Accounts/"
            f"{self.account_sid}/Calls/{call_sid}.json"
        )
        response = VoiceResponse()
        response.play(
            url=(
                "http://com.twilio.sounds.music.s3.amazonaws.com"
                "/MARKOVICHAMP-Borghestral.mp3"
            ),
            loop=0,
        )
        payload = {"Twiml": str(response)}
        return await self.client.post(url=url, payload=payload)
