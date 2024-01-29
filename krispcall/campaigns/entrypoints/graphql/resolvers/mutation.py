import json
import copy
import io
from typing import Any, Dict
from aiobotocore import session
from uuid import uuid4
from redis import Redis
from krispcall.auth.constant import AUTHENTICATED_ACCESS_USER

from krispcall.auth.requires_auth_power_dialer import (
    required_scope,
    requires_power_dialer_enabled,
)
from pydantic import ValidationError
from ariadne import convert_kwargs_to_snake_case
from graphql.type.definition import GraphQLResolveInfo
from pydantic import ValidationError
from krispcall.common.services.file_storage.csv_file_helper import process_contacts_csv
from krispcall.common.error_handler.exceptions import CSVProcessingError
from krispcall.common.responses.responses import create_error_response

from krispcall.common.utils.shortid import ShortId
from krispcall.common.error_handler.translator import get_translator
from krispcall.twilio.utils import TwilioClient
from krispcall.common.database.connection import DbConnection
from krispcall.common.app_settings.request_helpers import get_database


from krispcall.common.services import status as status
from krispcall.twilio.utils import sub_client
# from krispcall.common.service_layer.static_helpers import (
#     get_translator,
# )
# from krispcall.common.service_layer.helpers import (
#     clean_phone_number,
#     process_contacts_csv,
# )
# from krispcall.common.service_layer.exceptions import CSVProcessingError
# import pandas as pd

# from krispcall.common.service_layer.images import (
#     upload_file,
# )

from krispcall.auth.requires_auth_power_dialer import (
    requires_power_dialer_enabled,
)
from krispcall.konference.adapters.provider import get_workspace_credit
from krispcall.konference.billing.billing_service import BillingService
from krispcall.campaigns.service_layer import abstracts, views
from krispcall.campaigns import services


@required_scope(AUTHENTICATED_ACCESS_USER)
@requires_power_dialer_enabled
@convert_kwargs_to_snake_case
async def resolve_create_contact_list_with_csv(
    _: any, info: GraphQLResolveInfo, data: Dict[str, Any]
):
    request = info.context["request"]
    db_conn = get_database(request)
    workspace_id = request.user.get_claim("workspace_id", ShortId).uuid()
    member_id = request.user.get_claim("member_id", ShortId).uuid()
    user = request.user
    skip_csv_upload = data.get("skip_csv_upload")
    try:
        if not skip_csv_upload:
            # TODO harris
            csv_file = data.get("file")
            all_contacts = await process_contacts_csv(
                csv_file=csv_file,
                contact_name_column="Contact Name",
                usecols=["Contact Name", "Phone Number"],
            )
            total_records = len(all_contacts)

            await services.upload_campaign_contact_list(
                workspace_id=workspace_id,
                contact_list_name=data.get("contact_list_name"),
                created_by_name=data.get("created_by_name"),
                is_list_hidden=data.get("is_contact_list_hidden"),
                skip_csv_upload=skip_csv_upload,
                user=user.id_,
                member=member_id,
                contact_data=all_contacts,
                contact_count=total_records,
                db_conn=db_conn,
                job_queue=request.app.state.queue,
            )
        else:
            await services.upload_campaign_contact_list(
                workspace_id=workspace_id,
                contact_list_name=data.get("contact_list_name"),
                created_by_name=data.get("created_by_name"),
                is_list_hidden=data.get("is_contact_list_hidden"),
                skip_csv_upload=skip_csv_upload,
                user=user.id_,
                member=member_id,
                contact_data=[],
                contact_count=0,
                db_conn=db_conn,
                job_queue=request.app.state.queue,
            )

        return {
            "status": 200,
            "data": {
                "total_contact_count": 0 if skip_csv_upload else total_records
            },
            "error": None,
        }

    except ValidationError:
        return create_error_response(
            translator=get_translator(request),
            message="Invalid input",
            error_status=status.HTTP_400_INVALID_INPUT,
        )

    except CSVProcessingError:
        return create_error_response(
            translator=get_translator(request),
            message="Encountered invalid data format during CSV processing!",
            error_status=status.HTTP_400_INVALID_INPUT,
        )

    except Exception as e:
        return create_error_response(
            translator=get_translator(request),
            message=str(e),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@requires_power_dialer_enabled
@convert_kwargs_to_snake_case
async def resolve_update_campaign_contact_list(
    _: any, info: GraphQLResolveInfo, data: Dict[str, Any]
):
    request = info.context["request"]

    try:
        validated_data = abstracts.UpdateCampaignContactList(**data)
        resource = await services.update_campaign_contact_list(
            validated_data=validated_data,
            db_conn=get_database(request),
            user_id=request.user.id_,
        )
        return abstracts.campaign_contact_list_update(resource=resource).dict()

    except ValidationError:
        return create_error_response(
            translator=get_translator(request),
            message="Invalid input",
            error_status=status.HTTP_400_INVALID_INPUT,
        )

    except Exception as e:
        return create_error_response(
            translator=get_translator(request),
            message=str(e),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@requires_power_dialer_enabled
@convert_kwargs_to_snake_case
async def resolve_add_campaign_contact_detail(
    obj: any, info: GraphQLResolveInfo, data: Dict[str, Any]
):
    request = info.context["request"]
    member_id = request.user.get_claim("member_id", ShortId).uuid()
    try:
        validated_data = abstracts.AddCampaignContactDetail(**data)
        resource = await services.add_campaign_contact_detail(
            validated_data=validated_data,
            db_conn=get_database(request),
            member=member_id,
            user=request.user.id_,
        )
        return abstracts.campaign_add_contact_detail(resource=resource).dict()

    except ValidationError:
        return create_error_response(
            translator=get_translator(request),
            message="Invalid input",
            error_status=status.HTTP_400_INVALID_INPUT,
        )
    except Exception as e:
        return create_error_response(
            translator=get_translator(request),
            message=str(e),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@requires_power_dialer_enabled
@convert_kwargs_to_snake_case
async def resolve_delete_campaign_contact_detail(
    obj: any, info: GraphQLResolveInfo, data: Dict[str, Any]
):
    request = info.context["request"]
    try:
        validated_data = abstracts.DeleteCampaignContactDetail(**data)
        await services.delete_contacts(
            validated_data=validated_data,
            db_conn=get_database(request),
            user=request.user.id_,
        )
        return {"status": 200, "data": dict(success=True), "error": None}

    except ValidationError:
        return create_error_response(
            translator=get_translator(request),
            message="Invalid input",
            error_status=status.HTTP_400_INVALID_INPUT,
        )
    except Exception as e:
        return create_error_response(
            translator=get_translator(request),
            message=str(e),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@requires_power_dialer_enabled
@convert_kwargs_to_snake_case
async def resolve_upload_contact_detail_csv(
    _: any, info: GraphQLResolveInfo, data: Dict[str, Any]
):
    request = info.context["request"]
    db_conn = get_database(request)
    member_id = request.user.get_claim("member_id", ShortId).uuid()
    user = request.user.id_
    contact_list_id = ShortId(data.get("contact_list_id")).uuid()
    try:
        csv_file = data.get("file")
        all_contacts = await process_contacts_csv(
            csv_file=csv_file,
            contact_name_column="Contact Name",
            usecols=["Contact Name", "Phone Number"],
        )
        total_records = len(all_contacts)
        await services.upload_contact_detail_csv(
            member=member_id,
            user=user,
            contact_data=all_contacts,
            total_records=total_records,
            contact_list_id=contact_list_id,
            db_conn=db_conn,
        )
        return {
            "status": 200,
            "data": {"total_contact_count": total_records},
            "error": None,
        }

    except ValidationError:
        return create_error_response(
            translator=get_translator(request),
            message="Invalid input",
            error_status=status.HTTP_400_INVALID_INPUT,
        )

    except CSVProcessingError:
        return create_error_response(
            translator=get_translator(request),
            message="Encountered invalid data format during CSV processing!",
            error_status=status.HTTP_400_INVALID_INPUT,
        )

    except Exception as e:
        return create_error_response(
            translator=get_translator(request),
            message=str(e),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@requires_power_dialer_enabled
@convert_kwargs_to_snake_case
async def resolve_add_campaign_voicemail(
    _: Any,
    info: GraphQLResolveInfo,
    data: dict,
):
    request = info.context["request"]
    workspace_id = request.user.get_claim("workspace_id", ShortId).uuid()
    user_id = request.user.id_
    r_type = data.get("recording_type", "")
    source_file = data.get("file", None)
    ext = source_file.filename.split(".")[-1] if source_file else ".mp3"
    upload_name = f"audio/{uuid4()}.{ext}"
    base_url = request.app.state.settings.gateway_uri
    data.update({"recording_url": f"{base_url}/storage/{upload_name}"})
    validated_data = abstracts.AddVoiceMailDrops(**data)
    if r_type == "Custom":
        boto_session = session.get_session()
        settings = request.app.state.settings
        try:
            await upload_file_to_s3(
                boto_session, settings, validated_data.file, upload_name
            )
        except Exception as e:
            return create_error_response(
                translator=get_translator(request),
                message=str(e),
                error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    elif r_type == "TTS":
        # TODO harris
        await request.app.state.queue.run_task(
            "convert_and_save_text", validated_data, upload_name
        )
    try:
        await services.add_campaign_voicemail(
            workspace_id=workspace_id,
            member=user_id,
            validated_data=validated_data,
            db_conn=get_database(request),
        )
        return {
            "status": 200,
            "data": {"success": True},
            "error": None,
        }
    except (ValidationError, ValueError):
        return create_error_response(
            translator=get_translator(request),
            message="Invalid Input",
            error_status=status.HTTP_400_INVALID_INPUT,
        )

    except Exception as e:
        return create_error_response(
            translator=get_translator(request),
            message=str(e),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@requires_power_dialer_enabled
@convert_kwargs_to_snake_case
async def resolve_update_campaign_voicemail(
    _: Any,
    info: GraphQLResolveInfo,
    data: Dict[str, Any],
):
    request = info.context["request"]
    workspace_id = request.user.get_claim("workspace_id", ShortId).uuid()
    try:
        validated_data = abstracts.UpdateCampaignVoicemail(**data)
        resource = await services.update_campaign_voicemail(
            validated_data=validated_data,
            db_conn=get_database(request),
            workspace_id=workspace_id,
            request=request,
        )
        return {
            "status": 200,
            "data": {"success": True},
            "error": None,
        }
    except (ValidationError, ValueError):
        return create_error_response(
            translator=get_translator(request),
            message="Invalid Input",
            error_status=status.HTTP_400_INVALID_INPUT,
        )
    except Exception as e:
        return create_error_response(
            translator=get_translator(request),
            message=str(e),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@requires_power_dialer_enabled
@convert_kwargs_to_snake_case
async def resolve_add_campaign_callscripts(
    _: Any,
    info: GraphQLResolveInfo,
    data: dict,
):
    request = info.context["request"]
    workspace_id = request.user.get_claim("workspace_id", ShortId).uuid()
    user_id = request.user.id_
    validated_data = abstracts.AddCallScripts(**data)
    try:
        await services.add_campaign_callScripts(
            workspace_id=workspace_id,
            member=user_id,
            validated_data=validated_data,
            db_conn=get_database(request),
        )
        return {
            "status": 200,
            "data": {"success": True},
            "error": None,
        }
    except (ValidationError, ValueError):
        return create_error_response(
            translator=get_translator(request),
            message="Invalid Input",
            error_status=status.HTTP_400_INVALID_INPUT,
        )

    except Exception as e:
        return create_error_response(
            translator=get_translator(request),
            message=str(e),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@requires_power_dialer_enabled
@convert_kwargs_to_snake_case
async def resolve_update_campaign_callscripts(
    _: Any,
    info: GraphQLResolveInfo,
    data: Dict[str, Any],
):
    request = info.context["request"]
    workspace_id = request.user.get_claim("workspace_id", ShortId).uuid()
    try:
        validated_data = abstracts.UpdateCampaignCallScripts(**data)
        await services.update_campaign_callScripts(
            validated_data=validated_data,
            db_conn=get_database(request),
            workspace_id=workspace_id,
        )
        return {
            "status": 200,
            "data": {"success": True},
            "error": None,
        }
    except (ValidationError, ValueError):
        return create_error_response(
            translator=get_translator(request),
            message="Invalid Input",
            error_status=status.HTTP_400_INVALID_INPUT,
        )
    except Exception as e:
        return create_error_response(
            translator=get_translator(request),
            message=str(e),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@requires_power_dialer_enabled
@convert_kwargs_to_snake_case
async def resolve_create_campaigns(
    _: any, info: GraphQLResolveInfo, data: Dict[str, Any]
):
    request = info.context["request"]
    db_conn = get_database(request)
    workspace_id = request.user.get_claim("workspace_id", ShortId).uuid()
    member_id = request.user.get_claim("member_id", ShortId).uuid()
    user = request.user
    skip_csv_upload = data.get("skip_csv_upload")
    validated_data = abstracts.CreateCampaign(**data)
    try:
        if not skip_csv_upload:
            csv_file = data.get("file")
            all_contacts = await process_contacts_csv(
                csv_file=csv_file,
                contact_name_column="Contact Name",
                usecols=["Contact Name", "Phone Number"],
            )
            total_records = len(all_contacts)
            contact_mast_id = await services.upload_campaign_contact_list(
                workspace_id=workspace_id,
                contact_list_name=csv_file.filename,
                created_by_name=validated_data.created_by_name,
                is_list_hidden=data.get("is_contact_list_hidden"),
                skip_csv_upload=skip_csv_upload,
                user=user.id_,
                member=member_id,
                contact_data=all_contacts,
                contact_count=total_records,
                db_conn=db_conn,
                job_queue=request.app.state.queue,
            )
            await services.create_campaign(
                workspace_id=workspace_id,
                member=user.id_,
                db_conn=db_conn,
                contact_list_id=contact_mast_id,
                callable_data=all_contacts,
                validated_data=validated_data,
                next_number_to_dial=all_contacts[0].get("Phone Number"),
            )
        else:
            contact_data = await views.get_campaign_contact_dtl_list(
                contact_master_id=ShortId(
                    validated_data.contact_list_id
                ).uuid(),
                db_conn=db_conn,
            )
            callable_data = [
                {
                    "Phone Number": contact.get("contact_number"),
                    "Contact Name": contact.get("contact_name"),
                }
                for contact in contact_data
            ]
            await services.create_campaign(
                workspace_id=workspace_id,
                member=user.id_,
                db_conn=db_conn,
                contact_list_id=ShortId(validated_data.contact_list_id).uuid(),
                validated_data=validated_data,
                next_number_to_dial=callable_data[0].get("Phone Number")
                if callable_data
                else None,
                callable_data=callable_data,
                # Todo: First number in contact list need to be populated while creating campaign
            )

        return {
            "status": 200,
            "data": {"success": True},
            "error": None,
        }

    except ValidationError:
        return create_error_response(
            translator=get_translator(request),
            message="Invalid input",
            error_status=status.HTTP_400_INVALID_INPUT,
        )

    except CSVProcessingError:
        return create_error_response(
            translator=get_translator(request),
            message="Encountered invalid data format during CSV processing!",
            error_status=status.HTTP_400_INVALID_INPUT,
        )

    except Exception as e:
        return create_error_response(
            translator=get_translator(request),
            message=str(e),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@convert_kwargs_to_snake_case
@requires_power_dialer_enabled
async def resolve_archive_campaign(
    _: Any,
    info: GraphQLResolveInfo,
    data: Dict[str, Any],
):
    request = info.context["request"]
    user = request.user
    try:
        validated_data = abstracts.ArchiveCampaign(**data)
        await services.archive_campaign(
            validated_data=validated_data,
            db_conn=get_database(request),
            member=user.id_,
        )
        return {
            "status": 200,
            "data": {"success": True},
            "error": None,
        }
    except (ValidationError, ValueError):
        return create_error_response(
            translator=get_translator(request),
            message="Invalid Input",
            error_status=status.HTTP_400_INVALID_INPUT,
        )
    except Exception as e:
        return create_error_response(
            translator=get_translator(request),
            message=str(e),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@convert_kwargs_to_snake_case
@requires_power_dialer_enabled
async def resolve_update_campaign(
    _: any, info: GraphQLResolveInfo, data: Dict[str, Any]
):
    request = info.context["request"]
    db_conn = get_database(request)
    workspace_id = request.user.get_claim("workspace_id", ShortId).uuid()
    member_id = request.user.get_claim("member_id", ShortId).uuid()
    user = request.user
    skip_csv_upload = data.get("skip_csv_upload")
    validated_data = abstracts.UpdateCampaign(**data)
    try:
        if not skip_csv_upload:
            csv_file = data.get("file")
            all_contacts = await process_contacts_csv(
                csv_file=csv_file,
                contact_name_column="Contact Name",
                usecols=["Contact Name", "Phone Number"],
            )
            total_records = len(all_contacts)
            contact_mast_id = await services.upload_campaign_contact_list(
                workspace_id=workspace_id,
                contact_list_name=csv_file.file_name,
                created_by_name=validated_data.created_by_name,
                is_list_hidden=data.get("is_contact_list_hidden"),
                skip_csv_upload=skip_csv_upload,
                user=user.id_,
                member=member_id,
                contact_data=all_contacts,
                contact_count=total_records,
                db_conn=db_conn,
                job_queue=request.app.state.queue,
            )
            await services.update_campaign(
                validated_data=validated_data,
                workspace_id=workspace_id,
                db_conn=get_database(request),
                member=user.id_,
                contact_list_id=contact_mast_id,
            )
        else:
            await services.update_campaign(
                validated_data=validated_data,
                workspace_id=workspace_id,
                db_conn=get_database(request),
                member=user.id_,
                contact_list_id=ShortId(validated_data.contact_list_id).uuid(),
            )

        return {
            "status": 200,
            "data": {"success": True},
            "error": None,
        }

    except ValidationError:
        return create_error_response(
            translator=get_translator(request),
            message="Invalid input",
            error_status=status.HTTP_400_INVALID_INPUT,
        )

    except CSVProcessingError:
        return create_error_response(
            translator=get_translator(request),
            message="Encountered invalid data format during CSV processing!",
            error_status=status.HTTP_400_INVALID_INPUT,
        )

    except Exception as e:
        return create_error_response(
            translator=get_translator(request),
            message=str(e),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@convert_kwargs_to_snake_case
@requires_power_dialer_enabled
async def resolve_hold_campaign_conversation(
    _: Any, info: GraphQLResolveInfo, data: abstracts.HoldCampaignConversation
):
    request = info.context["request"]
    workspace = request.user.get_claim("workspace_id", ShortId).uuid()
    settings = request.app.state.settings
    cache = Redis.from_url(settings.redis_settings)
    try:
        validated_data = abstracts.HoldCampaignConversation(**data)

        # get active conversation from cache
        conversation = cache.get(
            ShortId.with_uuid(validated_data.conversation_sid)
        )
        if not conversation:
            raise Exception("Conversation not active. Can not hold call.")

        conversation = json.loads(conversation)

        client_call_sid = conversation.get("client")
        conversation = await services.hold_campaign_conversation(
            conversation_sid=validated_data.conversation_sid,
            hold=validated_data.hold,
            db_conn=get_database(request),
        )
        await request.app.state.queue.enqueue_job(
            "hold_conversation_by_id",
            [
                ShortId.with_uuid(conversation.twi_sid),
                workspace,
                validated_data.hold,
                client_call_sid,
            ],
            queue_name="arq:pd_queue",
        )
        return {
            "status": 200,
            "data": {
                "conversation_sid": validated_data.conversation_sid,
                "on_hold": validated_data.hold,
            },
            "error": None,
        }
    except Exception as e:
        return create_error_response(
            translator=get_translator(request),
            message=str(e),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@convert_kwargs_to_snake_case
@requires_power_dialer_enabled
async def resolve_record_campaign_conversation(
    _: Any,
    info: GraphQLResolveInfo,
    input: abstracts.RecordCampaignConversation,
):
    request = info.context["request"]
    user = request.user
    workspace = user.get_claim("workspace_id", ShortId).uuid()
    db_conn: DbConnection = request.app.state.db
    twilio_client: TwilioClient = request.app.state.twilio

    try:
        validated_data = abstracts.RecordCampaignConversation(**input)

        await services.record_campaign_conversation(
            conversation_sid=validated_data.conversation_sid,
            action=validated_data.action,
            db_conn=db_conn,
            twilio_client_=twilio_client,
            workspace=workspace,
        )
        action_map = {
            "RESUME": "INPROGRESS",
            "PAUSE": "PAUSED",
            "STOP": "STOPPED",
        }

        return {
            "status": 200,
            "error": None,
            "data": {
                "conversation_sid": validated_data.conversation_sid,
                "status": action_map.get(validated_data.action.value),
            },
        }
    except Exception as e:
        return create_error_response(
            translator=get_translator(request),
            message=str(e),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@convert_kwargs_to_snake_case
@requires_power_dialer_enabled
async def resolve_skip_campaign_conversation(
    _: Any, info: GraphQLResolveInfo, data: abstracts.SkipCampaignConversation
):
    request = info.context["request"]
    user = request.user
    db_conn: DbConnection = request.app.state.db
    cache = Redis.from_url(request.app.state.settings.redis_settings)
    try:
        # do stuff
        validated_data = abstracts.SkipCampaignConversation(**data)
        next_in_seq = await services.skip_campaign_conversation(
            conversation_sid=validated_data.conversation_sid,
            campaign_id=validated_data.campaign_id,
            db_conn=db_conn,
        )
        resp = {}
        values = cache.get(ShortId.with_uuid(validated_data.campaign_id)) or {}
        camp_obj = json.loads(values)
        if next_in_seq:
            # if skipping is successful we'll change
            # the cache value of next number to dial
            # to the next in sequence contact number
            # TODO: Abstract and move this to helper services
            camp_obj.update(
                {
                    "next_number_to_dial": next_in_seq.get("contact_number"),
                    "current_call_seq": next_in_seq.get("sequence_number"),
                }
            )
            cache.set(
                ShortId.with_uuid(validated_data.campaign_id),
                json.dumps(camp_obj),
            )

            resp = {
                "next_id": next_in_seq.get("id"),
                "contact_number": next_in_seq.get("contact_number"),
            }
        if not next_in_seq:
            camp_obj.update(
                {"next_number_to_dial": None, "current_call_seq": None}
            )
            cache.set(
                ShortId.with_uuid(validated_data.campaign_id),
                json.dumps(camp_obj),
            )
        return {
            "status": 200,
            "data": resp,
            "error": None,
        }

    except Exception as e:
        return create_error_response(
            translator=get_translator(request),
            message=str(e),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@requires_power_dialer_enabled
async def resolve_control_campaign(
    _: Any, info: GraphQLResolveInfo, data: abstracts.ControlCampaign
):
    request = info.context["request"]
    user = request.user
    queue: JobQueue = request.app.state.queue
    # get member id as UUID
    member_id = user.get_claim("member_id", ShortId).uuid()
    workspace_id = user.get_claim("workspace_id", ShortId).uuid()
    try:
        workspace_credit = await get_workspace_credit(
            ShortId.with_uuid(workspace_id)
        )

        if not BillingService.is_sufficient_credit(workspace_credit):
            return create_error_response(
                translator=get_translator(request),
                message="Insufficient credit",
                error_status=status.HTTP_400_INVALID_INPUT,
            )

        validated_data = abstracts.ControlCampaign(**data)  # type: ignore

        campaign = await services.control_campaign(
            validated_data=validated_data,
            db_conn=get_database(request),
            member=member_id,
            workspace=workspace_id,
            provider_client=request.app.state.twilio,
            settings=request.app.state.settings,
            queue=queue,
        )

        if validated_data.action == abstracts.CampaignAction.START:
            # TODO check create_campaign_stats should be called before update contact function called.
            # so need to test more on this part

            # await queue.run_task(
            #     "create_campaign_stats",
            #     campaign.id_,
            #     campaign.contact_list_id,
            #     _queue_name="arq:pd_queue",
            # )

            db_conn = get_database(request)
            await services.create_campaign_stats(
                campaign_id=campaign.id_,
                contact_list_id=campaign.contact_list_id,
                db_conn=db_conn,
            )

        if validated_data.action.value in [
            abstracts.CampaignAction.END.value,
            abstracts.CampaignAction.PAUSE.value,
        ]:
            cache = Redis.from_url(request.app.state.settings.redis_settings)
            cache.delete(validated_data.id)

        status_to_command_map = {
            "start": "inprogress",
            "pause": "paused",
            "end": "ended",
            "reattempt": "inprogress",
            "resume": "inprogress",
        }
        status_ = status_to_command_map.get(
            validated_data.action.value.lower()
        )
        return {
            "status": 200,
            "data": {
                "id": campaign.id_,
                "status": None if not status_ else status_.upper(),
            },
            "error": None,
        }
    except (ValidationError, ValueError):
        return create_error_response(
            translator=get_translator(request),
            message="Invalid Input",
            error_status=status.HTTP_400_INVALID_INPUT,
        )
    except Exception as error:
        return create_error_response(
            translator=get_translator(request),
            message=str(error),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@convert_kwargs_to_snake_case
@requires_power_dialer_enabled
async def resolve_add_campaign_call_note(
    _: Any,
    info: GraphQLResolveInfo,
    data: dict,
):
    request = info.context["request"]
    user_id = request.user.id_
    validated_data = abstracts.AddCampaignCallNote(**data)
    try:
        call_notes = await services.add_campaign_call_notes(
            member=user_id,
            validated_data=validated_data,
            db_conn=get_database(request),
        )
        return {
            "status": 200,
            "data": {
                "id": call_notes.id_,
                "note": call_notes.call_note,
            },
            "error": None,
        }
    except (ValidationError, ValueError):
        return create_error_response(
            translator=get_translator(request),
            message="Invalid Input",
            error_status=status.HTTP_400_INVALID_INPUT,
        )

    except Exception as e:
        return create_error_response(
            translator=get_translator(request),
            message=str(e),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@convert_kwargs_to_snake_case
@requires_power_dialer_enabled
async def resolve_update_campaign_call_note(
    _: Any,
    info: GraphQLResolveInfo,
    data: dict,
):
    request = info.context["request"]
    validated_data = abstracts.UpdateCampaignCallNote(**data)
    try:
        call_notes = await services.update_campaign_call_notes(
            validated_data=validated_data,
            db_conn=get_database(request),
        )
        return {
            "status": 200,
            "data": {
                "id": call_notes.id_,
                "note": call_notes.call_note,
            },
            "error": None,
        }
    except (ValidationError, ValueError):
        return create_error_response(
            translator=get_translator(request),
            message="Invalid Input",
            error_status=status.HTTP_400_INVALID_INPUT,
        )

    except Exception as e:
        return create_error_response(
            translator=get_translator(request),
            message=str(e),
            error_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@required_scope(AUTHENTICATED_ACCESS_USER)
@convert_kwargs_to_snake_case
@requires_power_dialer_enabled
async def resolve_campaign_voicemail_drop(
    _: Any, info: GraphQLResolveInfo, input: abstracts.VoicemailDropInput
):
    request = info.context["request"]
    cache = Redis.from_url(request.app.state.settings.redis_settings)
    db_conn = get_database(request)
    _twilio = request.app.state.twilio
    try:
        input = abstracts.VoicemailDropInput(**input)
        campaign_data = cache.get(ShortId.with_uuid(input.campaign_id)) or "{}"
        camp_obj = json.loads(campaign_data)
        if not camp_obj:
            raise Exception("Campaign is not active.")
        cpass_details = camp_obj.get("cpass_user")
        _sub_client: TwilioClient = sub_client(
            obj=copy.copy(_twilio),
            details=cpass_details,
        )
        await services.drop_campaign_voicemail(
            campaign_id=input.campaign_id,
            conversation_id=input.conversation_id,
            sub_client=_sub_client,
            db_conn=db_conn,
        )
        return abstracts.get_voicemail_drop(
            resource={
                "conversation_id": input.conversation_id,
                "status": "voicemailDropped",
            }
        )

    except Exception as e:
        return create_error_response(
            message=str(e), error_status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
