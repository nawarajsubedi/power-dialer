# Handles the event for the conference
import json
from redis import Redis
from starlette.endpoints import HTTPEndpoint
from starlette.responses import Response
from starlette.requests import Request

from krispcall.common.error_handler.exceptions import InsufficientBalanceException
from krispcall.common.utils.shortid import ShortId
from krispcall.common.utils.helpers import url_safe_decode
from krispcall.common.services.helper import convert_dict_to_snake_case
from krispcall.common.services.status import HTTP_200_OK, HTTP_400_INVALID, HTTP_500_INTERNAL_SERVER_ERROR
from krispcall.konference.service_layer import abstracts
from krispcall.konference import services


class CampaignConferenceHandler(HTTPEndpoint):
    """Handles the conference event for the dialing campaign"""

    async def post(self, request: Request):
        try:
            data = await request.form()
            callback_data = request.path_params["callback_data"]
            decoded_data = url_safe_decode(callback_data).split(",")
            workspace = decoded_data[0]
            campaign_id = decoded_data[1]
            conference_friendly_name = decoded_data[2]
            conversation = decoded_data[3]
            is_reattempt = True if int(decoded_data[4]) else False
            validated_data = abstracts.ConferenceParticipantEvent(
                **(convert_dict_to_snake_case(dict(data)))
            )
            settings = request.app.state.settings
            cache = Redis.from_url(settings.redis_settings)
            values = cache.get(campaign_id) or "{}"
            camp_obj = json.loads(values)
            await services.handle_conference_event(
                validated_data=validated_data,
                request=request,
                workspace=ShortId(workspace).uuid(),
                campaign_id=ShortId(campaign_id).uuid(),
                conference_friendly_name=ShortId(conference_friendly_name).uuid(),
                conversation=ShortId(conversation).uuid(),
                is_reattempt=is_reattempt,
                camp_obj=camp_obj,
                cache=cache,
            )
            return Response(
                status_code=HTTP_200_OK.status_code, media_type="application/xml"
            )
        except InsufficientBalanceException as e:
            print("exception", str(e))
            return Response(
                status_code=HTTP_400_INVALID.status_code,
                media_type="application/xml",
            )

        except Exception as e:
            print("exception", str(e))
            return Response(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR.status_code,
                media_type="application/xml",
            )


class ConferenceRecordingHandler(HTTPEndpoint):
    """Handles the conference event for the dialing campaign"""

    async def post(self, request: Request):
        try:
            # parse data
            data = await request.form()
            callback_data = request.path_params["callback_data"]
            decoded_data = url_safe_decode(callback_data).split(",")
            workspace = decoded_data[0]
            campaign_id = decoded_data[1]
            conference_friendly_name = decoded_data[2]
            conversation = decoded_data[3]
            data = convert_dict_to_snake_case(dict(data))
            if (
                "recording_status" in data
                and data.get("recording_status") == "completed"
            ):
                recording_url = data.get("recording_url", "")
                recording_duration = data.get("recording_duration", 0)

                await services.update_recording_info(
                    conversation=ShortId(conversation).uuid(),
                    recording_url=recording_url,
                    recording_duration=recording_duration,
                    db_conn=request.app.state.db,
                )

            # settings = request.app.state.settings
            # cache = Redis.from_url(settings.redis_settings)
            # values = cache.get(campaign_id) or "{}"
            # camp_obj = json.loads(values)
            # print("*" * 100)
            # print(values)
            # print("*" * 100)
            # await services.handle_conference_event(
            #     validated_data=validated_data,
            #     request=request,
            #     workspace=ShortId(workspace).uuid(),
            #     campaign_id=ShortId(campaign_id).uuid(),
            #     conference_friendly_name=ShortId(conference_friendly_name).uuid(),
            #     conversation=ShortId(conversation).uuid(),
            #     is_reattempt=is_reattempt,
            #     camp_obj=camp_obj,
            #     cache=cache,
            # )
            return Response(
                status_code=HTTP_200_OK.status_code, media_type="application/xml"
            )
        except Exception as e:
            print("exception", str(e))
            return Response(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR.status_code,
                media_type="application/xml",
            )
