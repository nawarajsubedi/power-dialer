import copy
import json
from uuid import UUID
from krispcall.common.utils.shortid import ShortId
from krispcall.common.error_handler.exceptions import CPaaSAuthenticationException
from krispcall.twilio.models import ConferenceResource, AccountCredential

from redis import Redis
# from krispcall.twilio.utils import sub_client
from krispcall.twilio.twilio_client import TwilioClient


async def get_call_details(
    twilio_client: TwilioClient,
    cache: Redis,
    campaign_id: UUID,
    call_sid: UUID,
):
    twilio_sub_client = build_twilio_subaccount_client(
        twilio_client, cache, campaign_id
    )
    call_info = await twilio_sub_client.call_resource.get_call_details(
        call_sid=ShortId.with_uuid(call_sid)
    )

    return call_info


async def get_conference_resource(
    twilio_client: TwilioClient,
    cache: Redis,
    conference_friendly_name: UUID,
    campaign_id: UUID,
) -> ConferenceResource:
    twilio_sub_client = build_twilio_subaccount_client(
        twilio_client, cache, campaign_id
    )

    try:
        result = await twilio_sub_client.conference_resource.fetch_conference(
            friendly_name=ShortId.with_uuid(conference_friendly_name)
        )
        conference_resource = ConferenceResource(
            conference_id=result["conferences"][0]["sid"],
            conference_status=result["conferences"][0]["status"],
        )

        return conference_resource
    except Exception as e:
        print(e)
        raise Exception(str(e))


def get_subaccount_credential_from_cache(cache: Redis, campaign_id: UUID):
    values = cache.get(ShortId.with_uuid(campaign_id)) or {}

    camp_obj = json.loads(values)
    credentials: AccountCredential = camp_obj.get("cpass_user")
    return credentials


def build_twilio_subaccount_client(
    twilio_client: TwilioClient, cache: Redis, campaign_id: UUID
) -> TwilioClient:
    credentials = get_subaccount_credential_from_cache(cache, campaign_id)
    client: TwilioClient = sub_client(
        obj=copy.copy(twilio_client),
        details=credentials,
    )
    return client


def sub_client(obj, details):
    if details["string_id"] is None or details["auth_token"] is None:
        raise CPaaSAuthenticationException("Invalid twilio authentication")
    setattr(obj, "account_sid", details["string_id"])
    setattr(obj, "auth_token", details["auth_token"])
    setattr(obj, "api_key", details["api_key"])
    setattr(obj, "api_secret", details["api_secret"])
    if "outgoing_application_sid" in details:
        setattr(
            obj,
            "outgoing_application_sid",
            details["outgoing_application_sid"],
        )
    if "android_push_key" in details:
        setattr(obj, "android_push_key", details["android_push_key"])

    if "ios_push_key" in details:
        setattr(obj, "ios_push_key", details["ios_push_key"])

    return obj
