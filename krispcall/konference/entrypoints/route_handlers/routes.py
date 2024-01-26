from starlette.routing import Route
from krispcall.konference.entrypoints.route_handlers import (
    conference_handler,
)
from krispcall.konference.entrypoints.route_handlers import (
    event_handler,
)

routes = [
    Route(
        "/sales_callbacks/campaigns/{callback_data:str}",
        conference_handler.CampaignConferenceHandler,
        methods=["POST"],
    ),
    Route(
        "/sales_callbacks/campaigns/record/{callback_data:str}",
        conference_handler.ConferenceRecordingHandler,
        methods=["POST"],
    ),
    Route(
        "/sales_callbacks/campaigns/agent/{callback_data:str}",
        event_handler.CampaignAgentHandler,
        methods=["POST"],
    ),
    Route(
        "/sales_callbacks/campaigns/client/{callback_data:str}",
        event_handler.CampaignClientHandler,
        methods=["POST"],
    ),
    Route(
        "/test",
        event_handler.CampaignAgentHandler,
        methods=["POST"],
    ),
]
