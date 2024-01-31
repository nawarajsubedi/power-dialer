from typing import Any, Dict
from krispcall.auth.constant import AUTHENTICATED_ACCESS_USER

from krispcall.auth.requires_auth_power_dialer import (
    required_scope,
    requires_power_dialer_enabled,
)
from ariadne import convert_kwargs_to_snake_case
from graphql.type.definition import GraphQLResolveInfo
from krispcall.common.models.response_model import PaginationParams
from krispcall.common.error_handler.parse_error_response import create_error_response

from krispcall.common.utils.shortid import ShortId
from krispcall.common.configs.request_helpers import get_database


from krispcall.common.services import status as status
from krispcall.auth.requires_auth_power_dialer import (
    requires_power_dialer_enabled,
)
from krispcall.campaigns.service_layer import abstracts, views
from krispcall.konference.service_layer import views as konference_views


@required_scope(AUTHENTICATED_ACCESS_USER)
@requires_power_dialer_enabled
@convert_kwargs_to_snake_case
async def resolve_campaign_contact_list(
    obj: any,
    info: GraphQLResolveInfo,
    fetch_archived: bool,
):
    request = info.context["request"]
    workspace = request.user.get_claim("workspace_id", ShortId)
    workspace_id = ShortId(workspace).uuid()
    db_conn = get_database(request)
    try:
        contactLists = await views.get_campaign_contact_list(
            workspace_id, fetch_archived, db_conn
        )
        return abstracts.get_campaign_contact_list(resource=contactLists)
    except Exception as e:
        return create_error_response(
            message=str(e),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@requires_power_dialer_enabled
@convert_kwargs_to_snake_case
async def resolve_campaign_contact_detail_lst(
    obj: any,
    info: GraphQLResolveInfo,
    id: str,
):
    request = info.context["request"]
    db_conn = get_database(request)
    try:
        contactDtlList = await views.get_campaign_contact_dtl_list(
            id,
            db_conn,
        )
        return abstracts.get_campaign_contact_dtl_list(resource=contactDtlList)
    except Exception as e:
        return create_error_response(
            message=str(e),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@requires_power_dialer_enabled
@convert_kwargs_to_snake_case
async def resolve_campaign_voicemail_list(
    obj: any,
    info: GraphQLResolveInfo,
):
    request = info.context["request"]
    workspace = request.user.get_claim("workspace_id", ShortId)
    workspace_id = ShortId(workspace).uuid()
    db_conn = get_database(request)
    try:
        voiceMailList = await views.get_campaign_voicemail_list(
            workspace_id,
            db_conn,
        )
        return abstracts.get_campaign_voicemails(resource=voiceMailList)
    except Exception as e:
        return create_error_response(
            message=str(e), error_status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@requires_power_dialer_enabled
@convert_kwargs_to_snake_case
async def resolve_campaign_callScripts_list(
    obj: any,
    info: GraphQLResolveInfo,
):
    request = info.context["request"]
    workspace = request.user.get_claim("workspace_id", ShortId)
    workspace_id = ShortId(workspace).uuid()
    db_conn = get_database(request)
    try:
        callScripts = await views.get_campaign_callScript_list(
            workspace_id,
            db_conn,
        )
        return abstracts.get_campaign_callScripts(resource=callScripts)
    except Exception as e:
        return create_error_response(
            message=str(e), error_status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@requires_power_dialer_enabled
@convert_kwargs_to_snake_case
async def resolve_callScript_by_campaign_id(
    obj: any,
    info: GraphQLResolveInfo,
    call_script_id: ShortId,
):
    request = info.context["request"]
    workspace = request.user.get_claim("workspace_id", ShortId)
    workspace_id = ShortId(workspace).uuid()
    db_conn = get_database(request)
    try:
        callScript = await views.get_callScript_by_id(
            workspace_id,
            db_conn,
            ShortId(call_script_id).uuid(),
        )
        return abstracts.get_callScript_by_id(record=callScript)
    except Exception as e:
        return create_error_response(
            message=e, error_status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@requires_power_dialer_enabled
@convert_kwargs_to_snake_case
async def resolve_campaign_callScripts_attribute_list(
    obj: any,
    info: GraphQLResolveInfo,
):
    request = info.context["request"]
    db_conn = get_database(request)
    try:
        callScriptsAttribute = (
            await views.get_campaign_callScriptAttribute_list(
                db_conn,
            )
        )
        return abstracts.get_campaign_callScripts_attributes(
            resource=callScriptsAttribute
        )
    except Exception as e:
        return create_error_response(
            message=str(e), error_status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@requires_power_dialer_enabled
@convert_kwargs_to_snake_case
async def resolve_campaign_list(
    obj: Any,
    info: GraphQLResolveInfo,
    fetch_archived: bool,
    params: Dict,
):
    request = info.context["request"]
    workspace = request.user.get_claim("workspace_id", ShortId)
    workspace_id = ShortId(workspace).uuid()
    db_conn = get_database(request)

    if params:
        params = abstracts.CampPaginationParams(**params)
    else:
        params = abstracts.CampPaginationParams(first=20)
    try:
        campaignList = await views.get_campaigns_list(
            PaginationParams(**params.dict()),
            workspace_id,
            fetch_archived,
            db_conn,
        )

        return abstracts.create_paginated_response(resource=campaignList)
    except Exception as e:
        return create_error_response(
            message=str(e),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@requires_power_dialer_enabled
@convert_kwargs_to_snake_case
async def resolve_campaign_analytics(
    _: Any,
    info: GraphQLResolveInfo,
    input: abstracts.CampaignAnalyticsInput,
    params: Dict,
):
    request = info.context["request"]
    db_conn = get_database(request)

    if params.get("filter"):
        status_filter: str = params["filter"][0].get("value")
    else:
        status_filter = ""
    try:
        data = abstracts.CampaignAnalyticsInput(**input)  # type: ignore
        initial_call = (
            True
            if data.conversation_type == abstracts.ConversationType.INTIAL
            else False
        )
        if params:
            params = abstracts.CampPaginationParams(**params)  # type: ignore
        else:
            params = abstracts.CampPaginationParams(first=10)  # type: ignore
        conversations = await konference_views.get_campaign_conversations(
            pagination_params=PaginationParams(**params.dict()),
            initial_call=initial_call,
            campaign_id=data.campaign_id,
            db_conn=db_conn,
            status_filter=status_filter,
        )
        if not conversations.edges:
            return create_error_response(
                message="No conversations found",
                error_status=status.HTTP_404_DOES_NOT_EXISTS,
            )

        response = abstracts.create_paginated_response(resource=conversations)  # type: ignore
        return response

    except Exception as e:
        return create_error_response(
            message=str(e),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@requires_power_dialer_enabled
@convert_kwargs_to_snake_case
async def resolve_campaign_stats(
    _: Any, info: GraphQLResolveInfo, input: Dict
):
    request = info.context["request"]
    db_conn = get_database(request)
    try:
        campaign_id = input["campaign_id"]
        stats = await views.get_campaign_stats(
            campaign_id,
            db_conn,
        )
        # Todo revist
        # if not stats:
        #     raise Exception("No stats found for campaign.")
        return abstracts.get_campaign_stats(resource=stats)  # type: ignore

    except Exception as e:
        return create_error_response(
            message=str(e),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@requires_power_dialer_enabled
@convert_kwargs_to_snake_case
async def resolve_campaign_note(_: Any, info: GraphQLResolveInfo, input: Dict):
    request = info.context["request"]
    db_conn = get_database(request)
    try:
        note_id = input["note_id"]
        note = await views.get_campaign_note(
            note_id,
            db_conn,
        )
        if not note:
            raise Exception("No note found for given id.")
        return abstracts.get_campaign_note(resource=note)  # type: ignore

    except Exception as e:
        return create_error_response(
            message=str(e),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@requires_power_dialer_enabled
@convert_kwargs_to_snake_case
async def resolve_campaign_callscript(
    _: Any, info: GraphQLResolveInfo, input: abstracts.CampaignCallScriptInput
):
    request = info.context["request"]
    db_conn = get_database(request)
    try:
        input = abstracts.CampaignCallScriptInput(**input)
        call_script = await views.get_campaign_callscript(
            input.callscript_id, db_conn
        )
        if not call_script:
            raise Exception("No callscript found for the given id.")
        return abstracts.get_campaign_callscript(resource=call_script)
    except Exception as e:
        return create_error_response(
            message=str(e),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@requires_power_dialer_enabled
@convert_kwargs_to_snake_case
async def resolve_campaign_voicemail(
    _: Any, info: GraphQLResolveInfo, input: abstracts.CampaignVoicemailInput
):
    request = info.context["request"]
    db_conn = get_database(request)
    try:
        input = abstracts.CampaignVoicemailInput(**input)
        campaign_voicemail = await views.get_campaign_voicemail_by_id(
            input.voicemail_id, db_conn
        )
        if not campaign_voicemail:
            raise Exception("No voicemail found for given id.")
        return abstracts.get_campaign_voicemail(resource=campaign_voicemail)
    except Exception as e:
        return create_error_response(
            message=str(e),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@requires_power_dialer_enabled
@convert_kwargs_to_snake_case
async def resolve_campaign_details(
    _: Any, info: GraphQLResolveInfo, input: abstracts.CampaignDetailsInput
):
    request = info.context["request"]
    db_conn = get_database(request)
    try:
        input = abstracts.CampaignDetailsInput(**input)
        campaign = await views.get_campaign_by_id(
            campaign_id=input.id, db_conn=db_conn
        )
        if not campaign:
            raise Exception("No campaign found for the given id")
        return abstracts.get_campaign_details(resource=dict(campaign))
    except Exception as e:
        return create_error_response(
            message=str(e),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@requires_power_dialer_enabled
@convert_kwargs_to_snake_case
async def resolve_campaign_count(_: Any, info: GraphQLResolveInfo):
    request = info.context["request"]
    workspace = request.user.get_claim("workspace_id", ShortId).uuid()
    db_conn = get_database(request)

    try:

        def filter_count(data) -> Dict:
            if not data:
                return
            archived = 0
            active = 0
            for d in data:
                if d.get("is_archived"):
                    archived = archived + 1
                else:
                    active = active + 1
            return {"archived": archived, "active": active}

        count_data = await views.get_campaigns_states(workspace, db_conn)
        count_data = filter_count(count_data)
        if not count_data:
            return {
                "status": 200,
                "data": {
                    "archived": 0,
                    "active": 0,
                },
            }
        return {
            "status": 200,
            "data": {
                "archived": count_data.get("archived"),
                "active": count_data.get("active"),
            },
        }
    except Exception as e:
        return create_error_response(
            message=str(e),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
