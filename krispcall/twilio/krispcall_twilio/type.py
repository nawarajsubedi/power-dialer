"""
abstract types
"""
from enum import Enum
from typing import Optional, Literal, List, Dict, Union
import typing
from uuid import UUID
from multidict import MultiDict
from pydantic import BaseModel, BaseSettings, AnyHttpUrl
import pydantic
from pydantic.class_validators import validator
from pydantic.networks import HttpUrl
from typing import Union
from krispcall.common.shortid import ShortId

from pydantic.types import SecretStr


PhoneNumber = typing.NewType("PhoneNumber", str)
CountryReference = typing.NewType("CountryReference", UUID)
WorkspaceReference = typing.NewType("WorkspaceReference", UUID)
MemberReference = typing.NewType("MemberReference", UUID)
AgentReference = typing.NewType("AgentReference", UUID)
ContactReference = typing.NewType("ContactReference", UUID)
ChannelReference = typing.NewType("ChannelReference", UUID)
ConversationReference = typing.NewType("ConversationReference", UUID)
SID = typing.NewType("SID", str)



class Settings(BaseSettings):
    twilio_account_sid: SecretStr
    twilio_auth_token: SecretStr
    app_uri: AnyHttpUrl
    twilio_api_key: SecretStr
    twilio_api_secret: SecretStr
    twilio_outgoing_application_sid: SecretStr
    fcm_api_key: SecretStr
    ios_cert: SecretStr
    ios_cert_key: SecretStr
    ios_app_env: str
    test_twilio_account_sid: str
    test_twilio_auth_token: str
    twilio_edge: str
    twilio_region: str
    ring_url: AnyHttpUrl
    hold_url: AnyHttpUrl


class NumberAvailabilityPathParams(BaseModel):
    country_iso: str
    type: Optional[Literal["Local", "Mobile", "TollFree", "National"]]
    types: Optional[Union[str, List[str]]] = [
        "Local",
        "Mobile",
        "TollFree",
        "National",
    ]


class NumberAvailabilityParams(BaseModel):
    page_size: int = 50
    area_code: Optional[int]
    contains: Optional[str]
    sms_enabled: Optional[bool]
    mms_enabled: Optional[bool]
    voice_enabled: Optional[bool]
    exclude_all_address_required: Optional[bool]
    exclude_local_address_required: Optional[bool]
    exclude_foreign_address_required: Optional[bool]
    beta: Optional[bool]
    near_number: Optional[str]
    near_lat_long: Optional[str]
    distance: Optional[int]
    in_postal_code: Optional[str]
    in_region: Optional[str]
    in_rate_center: Optional[str]
    in_lata: Optional[str]
    in_locality: Optional[str]
    fax_enabled: Optional[int]

    @validator("page_size")
    def page_size_must_between_3_100(cls, v):
        if 3 <= v <= 100:
            return v
        raise ValueError("page size must be between 3 and 100")


class Sms(BaseModel):
    body: str
    message_to: str
    message_from: str

    @validator("body")
    def body_length(cls, v):
        if len(v) >= 160:
            raise ValueError(
                "Sms body should be less than or equal to 160 characters"
            )
        return v


class BuyPhoneNumber(BaseModel):
    country_code: str
    area_code: str
    phone_number: str
    phone_number_type: str


class PhoneNumberRouteSetup(BaseModel):
    workspace_id: str
    phone_number_sid: str
    channel_sid: str


class NumberAddress(BaseModel):
    customer_name: str
    street: str
    city: str
    region: str
    postal_code: str
    iso_country: str
    friendly_name: Optional[str]
    emergency_enabled: Optional[str]
    auto_correct_address: Optional[str]


class IncomingPhoneNumber(BaseModel):
    phone_number: str
    area_code: Optional[str]
    friendly_name: Optional[str]
    identity_sid: Optional[str]
    address_sid: Optional[str]
    bundle_sid: Optional[str]

    sms_application_sid: Optional[str]
    sms_fallback_method: Optional[Literal["POST", "GET"]]
    sms_fallback_url: Optional[HttpUrl]
    sms_method: Optional[Literal["POST", "GET"]]
    sms_url: Optional[HttpUrl]
    status_callback: Optional[HttpUrl]
    status_callback_method: Optional[Literal["POST", "GET"]]
    voice_application_sid: Optional[str]
    voice_caller_id_lookup: Optional[bool]
    voice_fallback_method: Optional[Literal["POST", "GET"]]
    voice_fallback_url: Optional[HttpUrl]
    voice_method: Optional[Literal["POST", "GET"]]
    voice_url: Optional[HttpUrl]


class AddNumberToConference(BaseModel):
    friendly_name: str
    call_to: PhoneNumber
    call_from: PhoneNumber
    participant_label: str
    channel: ShortId
    workspace: ShortId
    channel_number: PhoneNumber
    caller_id: PhoneNumber = None # type: ignore
    direction: str = "outgoing"
    eoe: bool = True
    call_token: str = None  # type: ignore # only in the case of external transfer


class AddClientsToConference(BaseModel):
    friendly_name: str
    call_to: List[ShortId]
    call_from: PhoneNumber
    participant_label: Union[ShortId, str]
    channel: ShortId
    workspace: ShortId
    params: Dict
    caller_id: PhoneNumber = None # type: ignore
    direction: str = "incoming"
    eoe: bool = True


class AddAgentToCampaign(BaseModel):
    friendly_name: str
    call_from: PhoneNumber
    campaign_id: ShortId
    participant_label: Union[ShortId, str]
    params: Dict
    caller_id: PhoneNumber = None # type: ignore


class CampaignOutboundParticipantPayload(BaseModel):
    To: Union[PhoneNumber, str]
    From: PhoneNumber
    CallerId: PhoneNumber = None # type: ignore
    EndConferenceOnExit: bool = True
    Label: Optional[str] = None
    Timeout: int = 30
    StatusCallback: Union[HttpUrl, str] = None # type: ignore
    EarlyMedia: bool = False
    # AsyncAmd: str = "true"
    # MachineDetection: str = "DetectMessageEnd"
    # MachineDetectionTimeout: int = 59
    # AsyncAmdStatusCallback: Union[HttpUrl, str] = None
    # AsyncAmdStatusCallbackMethod: Literal["POST", "GET"] = "POST"
    Record: Optional[bool] = False

    @property
    def as_multi_dict(self) -> MultiDict:
        payload = MultiDict(
            [
                ("StatusCallbackEvent", "initiated"),
                ("StatusCallbackEvent", "ringing"),
                ("StatusCallbackEvent", "answered"),
                ("StatusCallbackEvent", "completed"),
            ]
        )
        payload.update(self.dict(exclude_none=True))
        return payload


class ExternalNumberPayload(BaseModel):
    To: Union[PhoneNumber, str]
    From: PhoneNumber
    CallerId: PhoneNumber = None # type: ignore
    Url: str = None # type: ignore
    StatusCallback: HttpUrl = None # type: ignore
    CallToken: str = None # type: ignore

    @property
    def as_multi_dict(self) -> MultiDict:
        payload = MultiDict(
            [
                ("StatusCallbackEvent", "initiated"),
                ("StatusCallbackEvent", "ringing"),
                ("StatusCallbackEvent", "answered"),
                ("StatusCallbackEvent", "completed"),
            ]
        )
        payload.update(self.dict(exclude_none=True))
        return payload


class OutboundParticipantPayload(BaseModel):
    To: Union[PhoneNumber, str]
    From: PhoneNumber
    CallerId: PhoneNumber = None # type: ignore
    EndConferenceOnExit: bool = True
    Label: str = None # type: ignore
    Timeout: int = 30
    StatusCallback: HttpUrl = None # type: ignore
    EarlyMedia: bool = False

    @property
    def as_multi_dict(self) -> MultiDict:
        payload = MultiDict(
            [
                ("StatusCallbackEvent", "initiated"),
                ("StatusCallbackEvent", "ringing"),
                ("StatusCallbackEvent", "answered"),
                ("StatusCallbackEvent", "completed"),
            ]
        )
        payload.update(self.dict(exclude_none=True))
        return payload


class Client(BaseModel):
    identity: str
    name: str = "client"
    params: Dict = {}

    @property
    def dial_str(self) -> str:
        """
        Returns a dial string for twiml
        client:alice?mycustomparam1=foo&mycustomparam2=bar
        """
        str_ = f"{self.name}:{self.identity}?"
        parms_str = "&".join(
            [f"{key}={self.params[key]}" for key in self.params]
        )
        return str_ + parms_str


class MessagingEvents(Enum):
    failed = "com.twilio.messaging.message.failed"
    undelivered = "com.twilio.messaging.message.undelivered"


class TwilioEventTypes(Enum):
    errors = "com.twilio.error-logs.error.logged"
    messaging = MessagingEvents


class OutboundSmsPayload(BaseModel):
    To: Union[PhoneNumber, str]
    From: PhoneNumber
    StatusCallback: HttpUrl = None # type: ignore
    MessagingServiceSid: str
    Body: str

    @property
    def as_multi_dict(self) -> MultiDict:
        payload = MultiDict(
            [
                ("StatusCallbackEvent", "sent"),
                ("StatusCallbackEvent", "delivered"),
                ("StatusCallbackEvent", "undelivered"),
            ]
        )
        payload.update(self.dict(exclude_none=True))
        return payload
