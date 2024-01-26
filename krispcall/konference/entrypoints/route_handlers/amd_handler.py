from krispcall.common.shortid import ShortId
from krispcall.common.static_helpers import url_safe_decode
from krispcall.konference import services
from starlette.endpoints import HTTPEndpoint
from starlette.responses import Response
from starlette.requests import Request


class AsyncAmdHandler(HTTPEndpoint):
    """Handles the event for in case call in answered by answering machine.
    Drops voicemail if configured.
    And drops the call.
    """

    async def post(self, request: Request):
        # parse data

        data = await request.form()

        # https://www.twilio.com/docs/voice/answering-machine-detection

        callback_data = request.path_params["callback_data"]
        decoded_data = url_safe_decode(callback_data).split(",")
        workspace = decoded_data[0]
        campaign_id = decoded_data[1]

        # conference_friendly_name = decoded_data[2]

        conversation = decoded_data[3]
        answered_by = data.get("AnsweredBy")
        call_sid = str(data.get("CallSid"))

        if answered_by == "machine_start":
            # drop voicemail
            # drop call
            await services.drop_voicemail(
                campaign_id=ShortId(campaign_id).uuid(),
                workspace=ShortId(workspace).uuid(),
                conversation=ShortId(conversation).uuid(),
                call_sid=call_sid,
                provider_client=request.app.state.twilio,
                db_conn=request.app.state.db,
            )
        return Response(status_code=200)
