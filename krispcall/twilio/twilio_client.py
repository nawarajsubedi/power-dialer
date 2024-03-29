"""
Wrapper around the Twilio Client for the methods we need.
"""

from typing import Union
from krispcall.twilio.caller_id_resource import CallerIdResource
from krispcall.twilio.notify_resource import NotifyResource
from krispcall.twilio.usage_triggers import UseLimitsResource
from pydantic import AnyHttpUrl
from pydantic.tools import parse_obj_as
from pydantic.types import SecretStr
from krispcall.twilio.conference_resource import ConferenceResource
from .type import (
    TwilioSettings,
)
from .transcription_resource import TranscriptionResource
from .credential_resource import CredentialsResource
from .call_resource import CallResource
from .application_resource import ApplicationResource
from .recording_resource import RecordingsResource
from .event_streams_resource import EventStreamsResource

from .regulatory_compliance import (
    BundlesResource,
    DocumentResource,
    EndUserResource,
)


class TwilioClient:
    def __init__(self, settings: TwilioSettings):
        self.account_sid = settings.twilio_account_sid
        self.auth_token = settings.twilio_auth_token
        self.app_uri: AnyHttpUrl = settings.app_uri
        self.api_key = settings.twilio_api_key
        self.api_secret = settings.twilio_api_secret
        self.outgoing_application_sid = (
            settings.twilio_outgoing_application_sid
        )
        self.base_url: AnyHttpUrl = parse_obj_as(
            AnyHttpUrl, "https://api.twilio.com/2010-04-01"
        )
        self.fcm_api_key = settings.fcm_api_key
        self.ios_cert = settings.ios_cert
        self.ios_key = settings.ios_cert_key
        self.ios_push_key: Union[SecretStr, None] = None
        self.android_push_key: Union[SecretStr, None] = None
        self.ios_app_env = settings.ios_app_env
        self.test_twilio_account_sid = settings.test_twilio_account_sid
        self.test_twilio_auth_token = settings.test_twilio_auth_token
        self.twilio_edge = settings.twilio_edge
        self.twilio_region = settings.twilio_region
        self.ring_url = settings.ring_url
        self.hold_url = settings.hold_url



    @property
    def call_resource(self) -> CallResource:
        return CallResource(
            account_sid=self.account_sid,
            auth_token=self.auth_token,
            api_key=self.api_key,
            api_secret=self.api_secret,
            outgoing_application_sid=self.outgoing_application_sid,
            app_url=self.app_uri,
            base_url=self.base_url,
            ios_push_key=self.ios_push_key,
            android_push_key=self.android_push_key,
            ring_url=self.ring_url,
            hold_url=self.hold_url,
        )

    @property
    def application_resource(self) -> ApplicationResource:
        return ApplicationResource(
            account_sid=self.account_sid,
            auth_token=self.auth_token,
            base_url=self.base_url,
            app_url=self.app_uri,
        )


    @property
    def recordings_resource(self) -> RecordingsResource:
        return RecordingsResource(
            account_sid=self.account_sid,
            auth_token=self.auth_token,
            base_url=self.base_url,
            app_url=self.app_uri,
        )

    @property
    def credential_resource(self) -> CredentialsResource:
        return CredentialsResource(
            account_sid=self.account_sid,
            auth_token=self.auth_token,
            fcm_api_key=self.fcm_api_key,
            ios_cert=self.ios_cert,
            ios_key=self.ios_key,
            ios_app_env=self.ios_app_env,
        )

    @property
    def bundles_resource(self) -> BundlesResource:
        return BundlesResource(
            account_sid=self.account_sid,
            auth_token=self.auth_token,
        )

    @property
    def end_user_resource(self) -> EndUserResource:
        return EndUserResource(
            account_sid=self.account_sid,
            auth_token=self.auth_token,
        )

    @property
    def document_resource(self) -> DocumentResource:
        return DocumentResource(
            account_sid=self.account_sid,
            auth_token=self.auth_token,
        )

    @property
    def caller_id_resource(self) -> CallerIdResource:
        return CallerIdResource(
            account_sid=self.account_sid,
            auth_token=self.auth_token,
            base_url=self.base_url,
            app_url=self.app_uri,
        )


    @property
    def notify_resource(self) -> NotifyResource:
        return NotifyResource(
            account_sid=self.account_sid,
            auth_token=self.auth_token,
            app_url=self.app_uri,
            twilio_edge=self.twilio_edge,
            twilio_region=self.twilio_region,
        )

    @property
    def use_limits_resource(self) -> UseLimitsResource:
        return UseLimitsResource(
            account_sid=self.account_sid,
            auth_token=self.auth_token,
            base_url=self.base_url,
            app_url=self.app_uri,
        )

    @property
    def conference_resource(self):
        return ConferenceResource(
            account_sid=self.account_sid,
            auth_token=self.auth_token,
            app_url=self.app_uri,
            base_url=self.base_url,
            ring_url=self.ring_url,
            hold_url=self.hold_url,
        )

    @property
    def transcription_resource(self):
        return TranscriptionResource(
            account_sid=self.account_sid,
            auth_token=self.auth_token,
            app_url=self.app_uri,
        )

    @property
    def event_streams_resource(self):
        return EventStreamsResource(
            account_sid=self.account_sid,
            auth_token=self.auth_token,
            base_url=self.base_url,
            app_url=self.app_uri,
        )
