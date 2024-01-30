"""
Services related to the client
"""
from __future__ import annotations
from krispcall.campaigns.service_layer.exceptions import (
    CampaignAlreadyActive,
    CampaignAlreadyEnded,
    CampaignAlreadyPaused,
)
from krispcall.providers.queue_service.job_queue import JobQueue
from krispcall.common.app_settings.app_settings import Settings
from krispcall.konference.domain.models import CampaignConversation
from loguru import logger
from starlette.requests import Request
from datetime import date, datetime
from typing import Dict, List, Union
from uuid import UUID, uuid4
from krispcall.common.utils.shortid import ShortId
from krispcall.common.database.connection import DbConnection
from krispcall.campaigns.domain import commands, models
from krispcall.campaigns.service_layer import (
    abstracts,
    handlers,
    unit_of_work,
    views,
    helpers,
)
from krispcall.konference import services as konference_services
from krispcall.konference.service_layer import views as konference_views
from krispcall.twilio.utils import TwilioClient
from krispcall.campaigns.service_layer import helpers
import copy


async def upload_campaign_contact_list(
    workspace_id: UUID,
    member: UUID,
    user: UUID,
    contact_data: Union[
        List[Dict], None
    ],  # [{"Contact Name": "test", "Phone Number": "1234567890"}]
    contact_list_name: str,
    contact_count: int,
    created_by_name: str,
    is_list_hidden: bool,
    skip_csv_upload: bool,
    db_conn: DbConnection,
    job_queue,
) -> models.Client: # type: ignore
    async with unit_of_work.CampaignContactSqlUnitOfWork(db_conn) as uow:
        contact_mast_data = handlers.add_contact_list_master(
            commands.CampaignContactMastData(
                name=contact_list_name,
                created_by_name=created_by_name,
                contact_count=contact_count,
                is_contact_list_hidden=False,
                workspace_id=workspace_id,
            )
        )

        await uow.repository.add_master_data(
            contact_mast_data,
            user,
        )

        if not skip_csv_upload:
            contact_list = []
            for each in contact_data: # type: ignore
                today = str(date.today())
                name = each.get("Contact Name", f"import_{today}")
                phone_number = each.get("Phone Number", "")
                id_ = uuid4()
                record = {
                    "id": id_,
                    "created_by": member,
                    "contact_name": name,
                    "contact_number": phone_number,
                    "created_on": datetime.now(),
                    "contact_list_id": contact_mast_data.id_,
                }
                contact_list.append(record)

            if contact_list:
                await uow.repository.upload_contact_in_bulk(contact_list)
        return contact_mast_data.id_


async def upload_contact_detail_csv(
    member: UUID,
    user: UUID,
    contact_list_id: UUID,
    total_records: int,
    contact_data: Dict,
    db_conn: DbConnection,
) -> models.Client: # type: ignore
    async with unit_of_work.CampaignContactSqlUnitOfWork(db_conn) as uow:
        contact_mast = await uow.repository.get(contact_list_id)
        contact_list = []
        for each in contact_data:
            today = str(date.today())
            name = each.get("Contact Name", f"import_{today}")
            phone_number = each.get("Phone Number", "")
            id_ = uuid4()
            record = {
                "id": id_,
                "created_by": member,
                "contact_name": name,
                "contact_number": phone_number,
                "created_on": datetime.now(),
                "contact_list_id": contact_list_id,
            }
            contact_list.append(record)

        if contact_list:
            await uow.repository.upload_contact_in_bulk(contact_list)
            contact_mast_data = handlers.update_contact_list_master(
                commands.CampaignContactMastUpdateCount(
                    contact_mast=contact_mast,
                    contact_count=int(total_records)
                    + int(contact_mast.contact_count),
                    modified_by=user,
                )
            )

            await uow.repository.update_contact_mast(
                contact_mast_data,
            )


async def update_campaign_contact_list(
    user_id: UUID,
    validated_data: abstracts.UpdateCampaignContactList,
    db_conn: DbConnection,
) -> models.CampaignContactListMast:
    async with unit_of_work.CampaignContactSqlUnitOfWork(db_conn) as uow:
        contactMast = await uow.repository.get(
            validated_data.contact_list_id.uuid()
        )
        if validated_data.action == "Rename":
            contactMast = handlers.update_contact_list_master(
                commands.RenameCampaignContactMaster(
                    contact_mast=contactMast,
                    name=validated_data.name,
                    contact_list_id=validated_data.contact_list_id,
                    modified_by=user_id,
                )
            )
        else:
            contactMast = handlers.update_contact_list_master(
                commands.ArchiveCampaignContactMaster(
                    contact_mast=contactMast,
                    is_archived=validated_data.archive_contact_list,
                    contact_list_id=validated_data.contact_list_id,
                    modified_by=user_id,
                )
            )
        await uow.repository.update_contact_mast(
            contactMast,
        )

    return contactMast


async def update_campaign_voicemail(
    validated_data: abstracts.UpdateCampaignVoicemail,
    db_conn: DbConnection,
    workspace_id: UUID,
    request: Request,
) -> models.CampaignVoicemail:
    async with unit_of_work.CampaignVoicemailSqlUnitOfWork(db_conn) as uow:
        voicemail = await uow.repository.get(validated_data.id.uuid())
        if validated_data.action == "Rename":
            voicemail = handlers.update_campaign_voicemail(
                commands.RenameCampaignVoiceMailCommand(
                    voicemail=voicemail,
                    name=validated_data.rename_text,
                )
            )
            await uow.repository.update_voicemail(voicemail)
        elif validated_data.action == "Delete":
            recording_url = voicemail.recording_url
            upload_name = recording_url.split("/storage/")[1]
            logger.info(f"recording_url {upload_name}")
            await request.app.state.queue.run_task(
                "delete_s3_objects", upload_name
            )
            await uow.repository.drop_voicemail(voicemail)
        else:
            voicemail_ = await views.get_default_campaign_voicemail_list(
                workspace_id, db_conn, is_default=True
            )
            if voicemail_:
                voicemail_ = models.CampaignVoicemail(**voicemail_)
                voicemail_ = handlers.update_campaign_voicemail(
                    commands.UpdateDefaultVoiceMailCommand(
                        voicemail=voicemail_, is_default=False
                    )
                )
                await uow.repository.update_voicemail(voicemail_)
            voicemail = handlers.update_campaign_voicemail(
                commands.UpdateDefaultVoiceMailCommand(
                    voicemail=voicemail, is_default=True
                )
            )
            await uow.repository.update_voicemail(voicemail)
    return voicemail


async def add_campaign_contact_detail(
    validated_data: abstracts.AddCampaignContactDetail,
    db_conn: DbConnection,
    member: UUID,
    user: UUID,
):
    async with unit_of_work.CampaignContactSqlUnitOfWork(db_conn) as uow:
        contact_mast = await uow.repository.get(validated_data.id.uuid())
        contactDetail = handlers.add_contact_detail_master(
            commands.AddCampaignContactDetail(
                name=validated_data.name,
                number=validated_data.number,
                contact_list_id=validated_data.id.uuid(),
            )
        )
        await uow.repository.add_contact_detail(
            contactDetail,
            member,
        )
        contact_mast_data = handlers.update_contact_list_master(
            commands.CampaignContactMastUpdateCount(
                contact_mast=contact_mast,
                contact_count=int(contact_mast.contact_count) + 1,
                modified_by=user,
            )
        )

        await uow.repository.update_contact_mast(
            contact_mast_data,
        )
    return contactDetail


async def delete_contacts(
    validated_data: abstracts.DeleteCampaignContactDetail,
    db_conn: DbConnection,
    user: UUID,
):
    async with unit_of_work.CampaignContactSqlUnitOfWork(db_conn) as uow:
        contact_mast = await uow.repository.get(
            validated_data.contact_list_id.uuid()
        )
        await uow.repository.delete_contacts(
            contacts=validated_data.contacts,
        )
        deleted_count = len(validated_data.contacts)
        contact_mast_data = handlers.update_contact_list_master(
            commands.CampaignContactMastUpdateCount(
                contact_mast=contact_mast,
                contact_count=int(contact_mast.contact_count) - deleted_count,
                modified_by=user,
            )
        )

        await uow.repository.update_contact_mast(
            contact_mast_data,
        )


async def add_campaign_voicemail(
    workspace_id: UUID,
    validated_data: abstracts.AddVoiceMailDrops,
    member: UUID,
    db_conn: DbConnection,
):
    r_type = validated_data.recording_type
    cmd = commands.AddCampaignVoicemail(
        workspace_id=workspace_id,
        created_by_name=validated_data.created_by_name,
        source=validated_data.source if r_type == "TTS" else None,
        recording_url=validated_data.recording_url,
        recording_type=validated_data.recording_type,
        voice=validated_data.voice if r_type == "TTS" else None,
        accent=validated_data.accent if r_type == "TTS" else None,
        name=validated_data.name,
        is_default=False,
    )

    async with unit_of_work.CampaignVoicemailSqlUnitOfWork(db_conn) as uow:
        voicemail = handlers.campaigns_voicemail(cmd)
        await uow.repository.add(voicemail, member)
    return voicemail


async def add_campaign_callScripts(
    workspace_id: UUID,
    validated_data: abstracts.AddCallScripts,
    member: UUID,
    db_conn: DbConnection,
):
    cmd = commands.AddCampaignCallScripts(
        workspace_id=workspace_id,
        script_title=validated_data.script_title,
        description=validated_data.description,
        is_default=False,
        created_by_name=validated_data.created_by_name,
    )
    async with unit_of_work.CampaignCallScriptsSqlUnitOfWork(db_conn) as uow:
        callScripts = handlers.add_campaigns_callscripts(cmd)
        await uow.repository.add(callScripts, member)
    return callScripts


async def add_campaign_call_notes(
    validated_data: abstracts.AddCampaignCallNote,
    member: UUID,
    db_conn: DbConnection,
) -> models.CampaignCallNotes:
    cmd = commands.AddCampaignCallNotes(
        call_note=validated_data.call_note,
        campaign_id=validated_data.campaign_id.uuid(),
        campaign_conversation_id=validated_data.campaign_conversation_id.uuid(),
    )
    async with unit_of_work.CampaignCallNotesSqlUnitOfWork(db_conn) as uow:
        callNotes = handlers.add_campaigns_callnotes(cmd)
        await uow.repository.add(callNotes, member)  # type: ignore
        await konference_services.update_campaign_conversation_notes(
            callNotes.id_,
            callNotes.campaign_conversation_id,
            db_conn,
        )
    return callNotes


async def update_campaign_call_notes(
    validated_data: abstracts.UpdateCampaignCallNote,
    db_conn: DbConnection,
) -> models.CampaignCallNotes:
    async with unit_of_work.CampaignCallNotesSqlUnitOfWork(db_conn) as uow:
        callNote = await uow.repository.get(validated_data.id.uuid())
        cmd = commands.UpdateCampaignCallNotes(
            callNote=callNote,
            call_note=validated_data.call_note,
            id=validated_data.id.uuid(),
        )
        callNotes = handlers.update_campaigns_callnotes(cmd)
        await uow.repository.update(callNotes)
    return callNotes


async def update_campaign_callScripts(
    validated_data: abstracts.UpdateCampaignCallScripts,
    db_conn: DbConnection,
    workspace_id: UUID,
) -> models.CampaignCallScripts:
    async with unit_of_work.CampaignCallScriptsSqlUnitOfWork(db_conn) as uow:
        callScript = await uow.repository.get(validated_data.id.uuid())
        if validated_data.action == "Update":
            callScript = handlers.update_campaign_callscripts(
                commands.UpdateCampaignCallScriptCommand(
                    callScript=callScript,
                    script_title=validated_data.script_title,
                    description=validated_data.description,
                )
            )
            await uow.repository.update_callscripts(callScript)
        elif validated_data.action == "Delete":
            await uow.repository.drop_callscripts(callScript)
        else:
            callScript_ = await views.get_default_campaign_callScripts(
                workspace_id, db_conn, is_default=True
            )
            if callScript_:
                callScript_ = models.CampaignCallScripts(**callScript_)
                callScript_ = handlers.update_campaign_callscripts(
                    commands.UpdateDefaultCallScriptCommand(
                        callScript=callScript_, is_default=False
                    )
                )
                await uow.repository.update_callscripts(callScript_)
            callScript = handlers.update_campaign_callscripts(
                commands.UpdateDefaultCallScriptCommand(
                    callScript=callScript, is_default=True
                )
            )
            await uow.repository.update_callscripts(callScript)
    return callScript


async def create_campaign(
    workspace_id: UUID,
    member: UUID,
    db_conn: DbConnection,
    contact_list_id: ShortId,
    next_number_to_dial: str,
    validated_data: abstracts.CreateCampaign,
    callable_data: Union[List[Dict], None],
) -> models.Client: # type: ignore
    cmd = commands.AddCampaigns(
        workspace_id=workspace_id,
        campaign_name=validated_data.campaign_name,
        assigne_name=validated_data.assignee_name,
        assigne_id=ShortId(validated_data.assignee_id).uuid(),
        dialing_number_id=ShortId(validated_data.dialing_number_id).uuid(),
        created_by_name=validated_data.created_by_name,
        dialing_number=validated_data.dialing_number,
        calling_datacenter=validated_data.data_center,
        campaign_status=models.CampaignStatus.ACTIVE.value,
        is_archived=False,
        call_recording_enabled=validated_data.is_call_recording_enabled,
        voicemail_enabled=validated_data.is_voicemail_enabled,
        voicemail_id=None
        if not validated_data.is_voicemail_enabled
        else ShortId(validated_data.voice_mail_id).uuid(), # type: ignore
        cooloff_period_enabled=validated_data.is_cool_off_period_enabled,
        cool_off_period=validated_data.cool_off_period,
        call_attempts_enabled=validated_data.is_attempts_per_call_enabled,
        call_attempts_count=validated_data.call_attempt_count,
        call_attempts_gap=validated_data.call_attempt_gap,
        call_script_enabled=validated_data.is_call_script_enabled,
        call_script_id=None
        if not validated_data.is_call_script_enabled
        else ShortId(validated_data.call_script_id).uuid(), # type: ignore
        contact_list_id=contact_list_id,
        next_number_to_dial=next_number_to_dial,
        callable_data=helpers.build_callable_list(callable_data),
    )
    async with unit_of_work.CampaignSqlUnitOfWork(db_conn) as uow:
        campaign = handlers.add_campaigns(cmd)
        await uow.repository.add(campaign, member)
    return campaign


async def archive_campaign(
    member: UUID,
    db_conn: DbConnection,
    validated_data: abstracts.ArchiveCampaign,
):
    async with unit_of_work.CampaignSqlUnitOfWork(db_conn) as uow:
        campaign = await uow.repository.get(validated_data.id.uuid())
        created_by = campaign.created_by
        campaign = handlers.archive_campaign(
            commands.ArchiveCampaignCommand(
                campaign=campaign,
                is_archived=validated_data.is_archived,
                modified_by=member,
            )
        )
        await uow.repository.update_campaigns(campaign, member, created_by)  # type: ignore
    return campaign


async def update_campaign(
    member: UUID,
    workspace_id: UUID,
    db_conn: DbConnection,
    validated_data: abstracts.UpdateCampaign,
    contact_list_id: UUID,
):
    async with unit_of_work.CampaignSqlUnitOfWork(db_conn) as uow:
        campaign = await uow.repository.get(validated_data.id.uuid())
        created_by = campaign.created_by
        campaign = handlers.update_campaign(
            commands.UpdateCampaignCommand(
                campaign=campaign,
                workspace_id=workspace_id,
                id=ShortId(validated_data.id).uuid(),
                campaign_name=validated_data.campaign_name,
                assigne_name=validated_data.assignee_name,
                assigne_id=ShortId(validated_data.assignee_id).uuid(),
                dialing_number_id=ShortId(
                    validated_data.dialing_number_id
                ).uuid(),
                created_by_name=campaign.created_by_name,
                dialing_number=validated_data.dialing_number,
                calling_datacenter=validated_data.data_center,
                campaign_status=campaign.campaign_status,
                call_recording_enabled=validated_data.is_call_recording_enabled,
                voicemail_enabled=validated_data.is_voicemail_enabled,
                voicemail_id=None
                if not validated_data.voice_mail_id
                else ShortId(validated_data.voice_mail_id).uuid(),
                cooloff_period_enabled=validated_data.is_cool_off_period_enabled,
                cool_off_period=validated_data.cool_off_period,
                call_attempts_enabled=validated_data.is_attempts_per_call_enabled,
                call_attempts_count=validated_data.call_attempt_count,
                call_attempts_gap=validated_data.call_attempt_gap,
                call_script_enabled=validated_data.is_call_script_enabled,
                call_script_id=None
                if not validated_data.call_script_id
                else ShortId(validated_data.call_script_id).uuid(),
                contact_list_id=contact_list_id,
                next_number_to_dial=campaign.next_number_to_dial,
                is_archived=campaign.is_archived,
                modified_by=member,
            )
        )
        await uow.repository.update_campaigns(campaign, member, created_by)  # type: ignore
    return campaign


async def update_next_number_to_dial(
    campaign_id: UUID, next_number: str, db_conn: DbConnection
):
    async with unit_of_work.CampaignSqlUnitOfWork(db_conn) as uow:
        campaign = await uow.repository.get(campaign_id)
        created_by = campaign.created_by
        campaign_ = handlers.update_next_number_to_dial(
            commands.UpdateCampaignNextToDial(
                campaign=campaign,
                id=campaign_id,
                next_number_to_dial=next_number,
            )
        )
        await uow.repository.update_campaigns(
            campaign_, created_by, created_by
        )


async def hold_campaign_conversation(
    conversation_sid: UUID, hold: bool, db_conn: DbConnection
):
    return await konference_services.hold_conversation(
        conversation_sid=conversation_sid, hold=hold, db_conn=db_conn
    )


async def record_campaign_conversation(
    conversation_sid: UUID,
    action: abstracts.RecordAction,
    db_conn: DbConnection,
    twilio_client_: TwilioClient,
    workspace: UUID,
):
    return await konference_services.record_campaign_conversation(
        conversation_sid=conversation_sid,
        action=action.value.lower(), # type: ignore
        db_conn=db_conn,
        twilio_client_=twilio_client_,
        workspace=workspace,
    )


async def skip_campaign_conversation(
    conversation_sid: UUID, campaign_id: UUID, db_conn: DbConnection
):
    conversation: CampaignConversation = (
        await konference_services.skip_conversation(
            conversation_sid=conversation_sid, db_conn=db_conn
        )
    )
    next_in_sequence = (
        await konference_views.get_campaign_conference_by_sequence_number(
            campaign_id=campaign_id,
            sequence_number=conversation.sequence_number + 1,
            db_conn=db_conn,
            initial_call=conversation.initial_call,
        )
    )

    await konference_services.complete_campaign_conversation(
        conversations=[conversation_sid],
        db_conn=db_conn,
    )
    if not next_in_sequence:
        await update_next_number_to_dial(
            campaign_id=campaign_id, next_number="", db_conn=db_conn
        )
        return
    next_number = next_in_sequence.get("contact_number")
    await update_next_number_to_dial(
        campaign_id=campaign_id, next_number=next_number, db_conn=db_conn # type: ignore
    )
    return next_in_sequence


async def control_campaign(
    validated_data: abstracts.ControlCampaign,
    member: UUID,
    workspace: UUID,
    db_conn: DbConnection,
    provider_client: TwilioClient,
    settings: Settings,
    queue: JobQueue,
) -> models.Campaigns:
    status_to_command_map = {
        "start": "inprogress",
        "pause": "paused",
        "end": "ended",
        "reattempt": "inprogress",
        "resume": "inprogress",
    }

    if validated_data.action == abstracts.CampaignAction.REATTEMPT:
        data = await konference_views.has_reattempt_calls(
            campaign_id=validated_data.id.uuid(),
            db_conn=db_conn,
        )
        print(data)
        if not data:
            raise CampaignAlreadyEnded(
                "The campaign has concluded, and retrying is not possible."
            )

    async with unit_of_work.CampaignSqlUnitOfWork(db_conn) as uow:
        campaign: models.Campaigns = await uow.repository.get(
            validated_data.id.uuid()
        )

        # becasue starting a already started campaign is a long process
        # we will not user start campaign that is already started and throw an error
        if (
            validated_data.action.value.lower() == "start"
            and campaign.campaign_status == "ended"
        ):
            raise CampaignAlreadyEnded("Cannot re-start completed campaign.")
        if (
            validated_data.action.value.lower() == "pause"
            and campaign.campaign_status == "ended"
        ):
            raise CampaignAlreadyEnded("Cannot pause completed campaign.")

        if (
            validated_data.action.value.lower() == "pause"
            and campaign.campaign_status == "paused"
        ):
            raise CampaignAlreadyPaused(
                "Cannot pause already paused campaign."
            )

        if (
            validated_data.action.value.lower() == "start"
            and campaign.campaign_status == "inprogress"
        ):
            raise CampaignAlreadyActive("Campaign is already active.")
        campaign_ = handlers.control_campaign(
            commands.ControlCampaignCommand(
                campaign=campaign,
                campaign_status=status_to_command_map.get(
                    validated_data.action.value.lower()
                ),
                modified_by=member,
            )
        )

        await uow.repository.update_campaigns(campaign_, member, campaign.created_by)

    # Pass the command over to the konference (Twilio Powerdialer) component
    # right now we are calling the component directly
    # also it takes over 9 seconds to complete for campaigns with more than
    # 10 contacts
    # and providing the entire state
    # in future, we will need to call this over
    # AMQP or GRPC for performance

    await konference_services.control_campaign_loop(
        command=validated_data.action.value.lower(),
        campaign=campaign,
        workspace=workspace,
        provider_client=provider_client,
        db_conn=db_conn,
        member=member,
        settings=settings,
        queue=queue,
    )
    return campaign


async def end_campaign(campaign_id: UUID, db_conn: DbConnection):
    async with unit_of_work.CampaignSqlUnitOfWork(db_conn) as uow:
        campaign = await uow.repository.get(campaign_id)
        created_by = campaign.created_by
        campaign_ = handlers.control_campaign(
            commands.ControlCampaignCommand(
                campaign=campaign,
                campaign_status="ended",
                modified_by=created_by,
            ),
        )
        await uow.repository.update_campaigns(
            campaign_, created_by, created_by
        )


async def update_campaign_duration(
    campaign_id: UUID, db_conn: DbConnection, add_seconds: int
):
    """Adds seconds to the campaign stats for the provided campaign"""
    async with unit_of_work.CampaignStatsSqlUnitOfWork(db_conn) as uow:
        stats: models.CampaignStats = await uow.repository.get(ref=campaign_id)

        updated_stats = handlers.update_campaign_stats(
            cmd=commands.UpdateCampaignCallDuration(
                stats=stats,
                active_call_duration=stats.active_call_duration + add_seconds,
            )  # type: ignore
        )
        return await uow.repository.update(updated_stats, "active_call_duration", add_seconds)  # type: ignore


async def update_campaign_dialed_contacts(
    campaign_id: UUID, db_conn: DbConnection
):
    """Adds +1 to the dialed_contacts table for the campaign"""
    async with unit_of_work.CampaignStatsSqlUnitOfWork(db_conn) as uow:
        stats: models.CampaignStats = await uow.repository.get(ref=campaign_id)
        updated_stats = handlers.update_campaign_stats(
            cmd=commands.UpdateCampaignDialedContacts(
                stats=stats, dialed_contacts=stats.dialed_contacts + 1
            )  # type: ignore
        )
        return await uow.repository.update(updated_stats, "dialed_contacts", 1)  # type: ignore


async def update_campaign_calls(
    campaign_id: UUID,
    db_conn: DbConnection,
    answered: bool,
):
    """Adds +1 to the answered or unanswered calls table for the campaign"""
    async with unit_of_work.CampaignStatsSqlUnitOfWork(db_conn) as uow:
        stats: models.CampaignStats = await uow.repository.get(ref=campaign_id)
        updated_stats = handlers.update_campaign_stats(
            cmd=commands.UpdateCampaignAnsweredCalls(stats, answered_calls=stats.answered_calls + 1) if answered else commands.UpdateCampaignUnansweredCalls(stats, unanswered_calls=stats.unanswered_calls + 1)  # type: ignore
        )
        return await uow.repository.update(updated_stats, "answered_calls" if answered else "unanswered_calls", 1)  # type: ignore


async def update_campaign_voicemail_drops(
    campaign_id: UUID, db_conn: DbConnection
):
    """Adds +1 to the voicemail drops  table for the campaign"""
    async with unit_of_work.CampaignStatsSqlUnitOfWork(db_conn) as uow:
        stats: models.CampaignStats = await uow.repository.get(ref=campaign_id)
        updated_stats = handlers.update_campaign_stats(
            cmd=commands.UpdateCampaignVoicemailDrops(
                stats=stats,
                voicemail_drops=stats.voicemail_drops + 1,
            )  # type: ignore
        )
        return await uow.repository.update(updated_stats, "voicemail_drops", 1)  # type: ignore


async def create_campaign_stats(
    campaign_id: UUID, db_conn: DbConnection, contact_list_id: UUID
):
    total_contacts = await views.contact_list_length(contact_list_id, db_conn)
    campaign_stat = handlers.add_campaign_stats(
        commands.AddCampaignStat(
            campaign_id=campaign_id,
            total_contacts=total_contacts,
            dialed_contacts=1,
            answered_calls=0,
            unanswered_calls=0,
            campaign_duration=0,
            active_call_duration=0,
            voicemail_drops=0,
        )
    )
    async with unit_of_work.CampaignStatsSqlUnitOfWork(db_conn) as uow:
        stat = await uow.repository.add(campaign_stat)
        return stat


async def drop_campaign_voicemail(
    campaign_id: UUID,
    conversation_id: UUID,
    sub_client: TwilioClient,
    db_conn: DbConnection,
):
    # get the campaign voicemail url
    voicemail = await views.get_campaign_voicemail(campaign_id, db_conn)
    # print(dict(voicemail))

    await konference_services.drop_campaign_voicemail(
        provider_client=sub_client,
        conversation=conversation_id,
        voicemail_url=voicemail.get("recording_url"),
        db_conn=db_conn,
    )
