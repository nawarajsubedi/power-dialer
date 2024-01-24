"""
"""
from __future__ import annotations
import typing

from krispcall.campaigns.domain import commands, models


def add_campaign_stats(cmd: commands.AddCampaignStat) -> models.CampaignStats:
    return models.campaign_stats_factory(
        campaign_id=cmd.campaign_id,
        total_contacts=cmd.total_contacts,
        dialed_contacts=cmd.dialed_contacts,
        voicemail_drops=cmd.voicemail_drops,
        answered_calls=cmd.answered_calls,
        unanswered_calls=cmd.unanswered_calls,
        active_call_duration=cmd.active_call_duration,
        campaign_duration=cmd.campaign_duration,
    )


def update_campaign_stats(
    cmd: commands.UpdateCampaignCommand,
) -> models.CampaignStats:
    cmd_map = {
        commands.UpdateCampaignCallDuration: lambda cmd: typing.cast(
            commands.UpdateCampaignCallDuration, cmd
        ).stats.update({"active_call_duration": cmd.active_call_duration}),
        commands.UpdateCampaignDialedContacts: lambda cmd: typing.cast(
            commands.UpdateCampaignDialedContacts, cmd
        ).stats.update({"dialed_contacts": cmd.dialed_contacts}),
        commands.UpdateCampaignAnsweredCalls: lambda cmd: typing.cast(
            commands.UpdateCampaignAnsweredCalls, cmd
        ).stats.update({"answered_calls": cmd.answered_calls}),
        commands.UpdateCampaignUnansweredCalls: lambda cmd: typing.cast(
            commands.UpdateCampaignUnansweredCalls, cmd
        ).stats.update({"unanswered_calls": cmd.unanswered_calls}),
    }
    return cmd_map.get(type(cmd), lambda _: Exception("Unknown command"))(cmd)  # type: ignore


def add_contact_list_master(
    cmd: commands.CampaignContactMastData,
) -> models.CampaignContactListMast:
    return models.campaign_contact_list_mast_factory(
        name=cmd.name,
        created_by_name=cmd.created_by_name,
        contact_count=cmd.contact_count,
        is_archived=cmd.is_archived,
        workspace=cmd.workspace_id,
        is_hidden=cmd.is_contact_list_hidden,
    )


def update_contact_list_master(
    cmd: commands.CampaignContactMastCommand,
) -> models.CampaignContactListMast:
    if isinstance(cmd, commands.CampaignContactMastUpdateCount):
        cmd = typing.cast(commands.CampaignContactMastUpdateCount, cmd)
        return cmd.contact_mast.update(
            {
                "contact_count": cmd.contact_count,
                "modified_by": cmd.modified_by,
            }
        )
    if isinstance(cmd, commands.RenameCampaignContactMaster):
        cmd = typing.cast(commands.RenameCampaignContactMaster, cmd)
        return cmd.contact_mast.update(
            {"name": cmd.name, "modified_by": cmd.modified_by}
        )
    if isinstance(cmd, commands.ArchiveCampaignContactMaster):
        cmd = typing.cast(commands.ArchiveCampaignContactMaster, cmd)
        return cmd.contact_mast.update(
            {"is_archived": cmd.is_archived, "modified_by": cmd.modified_by}
        )


def archive_campaign(
    cmd: commands.CampaignsCommand,
) -> models.Campaigns:
    if isinstance(cmd, commands.ArchiveCampaignCommand):
        cmd = typing.cast(commands.ArchiveCampaignCommand, cmd)
        return cmd.campaign.update(
            {
                "is_archived": cmd.is_archived,
                "modified_by": cmd.modified_by,
            }
        )


def add_contact_detail_master(
    cmd: commands.AddCampaignContactDetail,
) -> models.CampaignContactListDetail:
    return models.campaign_contact_list_detail_factory(
        contact_name=cmd.name,
        contact_number=cmd.number,
        contact_list_id=cmd.contact_list_id,
    )


def campaigns_voicemail(
    cmd: commands.AddCampaignVoicemail,
) -> models.CampaignVoicemail:
    return models.campaignVoicemail_factory(
        workspace_id=cmd.workspace_id,
        created_by_name=cmd.created_by_name,
        source=cmd.source,
        recording_url=cmd.recording_url,
        recording_type=cmd.recording_type,
        voice=cmd.voice,
        accent=cmd.accent,
        name=cmd.name,
        is_default=cmd.is_default,
    )


def update_campaign_voicemail(
    cmd: commands.CampaignVoicemailCommand,
) -> models.CampaignVoicemail:
    if isinstance(cmd, commands.RenameCampaignVoiceMailCommand):
        cmd = typing.cast(commands.RenameCampaignVoiceMailCommand, cmd)
        return cmd.voicemail.update(
            {
                "name": cmd.name,
            }
        )
    if isinstance(cmd, commands.UpdateDefaultVoiceMailCommand):
        cmd = typing.cast(commands.UpdateDefaultVoiceMailCommand, cmd)
        return cmd.voicemail.update(
            {
                "is_default": cmd.is_default,
            }
        )


def add_campaigns_callscripts(
    cmd: commands.AddCampaignCallScripts,
) -> models.CampaignCallScripts:
    return models.campaignCallScripts_factory(
        workspace_id=cmd.workspace_id,
        description=cmd.description,
        created_by_name=cmd.created_by_name,
        script_title=cmd.script_title,
        is_default=cmd.is_default,
    )


def add_campaigns_callnotes(
    cmd: commands.AddCampaignCallNotes,
) -> models.CampaignCallNotes:
    return models.campaignCallNotes_factory(
        call_note=cmd.call_note,
        campaign_id=cmd.campaign_id,
        campaign_conversation_id=cmd.campaign_conversation_id,
    )


def update_campaigns_callnotes(
    cmd: commands.UpdateCampaignCallNotes,
) -> models.CampaignCallNotes:
    cmd = typing.cast(commands.UpdateCampaignCallNotes, cmd)
    return cmd.callNote.update(
        {
            "id_": cmd.id,
            "call_note": cmd.call_note,
        }
    )


def update_campaign_callscripts(
    cmd: commands.CampaignCallScriptCommand,
) -> models.CampaignCallScripts:
    if isinstance(cmd, commands.UpdateCampaignCallScriptCommand):
        cmd = typing.cast(commands.UpdateCampaignCallScriptCommand, cmd)
        return cmd.callScript.update(
            {
                "script_title": cmd.script_title,
                "description": cmd.description,
            }
        )
    if isinstance(cmd, commands.CampaignCallScriptCommand):
        cmd = typing.cast(commands.UpdateDefaultCallScriptCommand, cmd)
        return cmd.callScript.update(
            {
                "is_default": cmd.is_default,
            }
        )


def add_campaigns(
    cmd: commands.AddCampaigns,
) -> models.Campaigns:
    return models.campaigns_factory(
        workspace_id=cmd.workspace_id,
        campaign_name=cmd.campaign_name,
        assigne_name=cmd.assigne_name,
        assigne_id=cmd.assigne_id,
        created_by_name=cmd.created_by_name,
        dialing_number_id=cmd.dialing_number_id,
        dialing_number=cmd.dialing_number,
        calling_datacenter=cmd.calling_datacenter,
        campaign_status=cmd.campaign_status,
        call_recording_enabled=cmd.call_recording_enabled,
        voicemail_enabled=cmd.voicemail_enabled,
        voicemail_id=cmd.voicemail_id,
        cooloff_period_enabled=cmd.cooloff_period_enabled,
        cool_off_period=cmd.cool_off_period,
        call_attempts_enabled=cmd.call_attempts_enabled,
        call_attempts_count=cmd.call_attempts_count,
        call_attempts_gap=cmd.call_attempts_gap,
        call_script_enabled=cmd.call_script_enabled,
        call_script_id=cmd.call_script_id,
        contact_list_id=cmd.contact_list_id,
        next_number_to_dial=cmd.next_number_to_dial,
        is_archived=cmd.is_archived,
        callable_data=cmd.callable_data,
    )


def update_campaign(
    cmd: commands.CampaignsCommand,
) -> models.Campaigns:
    if isinstance(cmd, commands.UpdateCampaignCommand):
        cmd = typing.cast(commands.UpdateCampaignCommand, cmd)
        return cmd.campaign.update(
            {
                "workspace_id": cmd.workspace_id,
                "campaign_name": cmd.campaign_name,
                "assigne_name": cmd.assigne_name,
                "assigne_id": cmd.assigne_id,
                "next_number_to_dial": cmd.next_number_to_dial,
                "created_by_name": cmd.created_by_name,
                "dialing_number_id": cmd.dialing_number_id,
                "dialing_number": cmd.dialing_number,
                "calling_datacenter": cmd.calling_datacenter,
                "campaign_status": cmd.campaign_status,
                "call_recording_enabled": cmd.call_recording_enabled,
                "voicemail_enabled": cmd.voicemail_enabled,
                "voicemail_id": cmd.voicemail_id,
                "cooloff_period_enabled": cmd.cooloff_period_enabled,
                "cool_off_period": cmd.cool_off_period,
                "call_attempts_enabled": cmd.call_attempts_enabled,
                "call_attempts_count": cmd.call_attempts_count,
                "call_attempts_gap": cmd.call_attempts_gap,
                "call_script_enabled": cmd.call_script_enabled,
                "call_script_id": cmd.call_script_id,
                "contact_list_id": cmd.contact_list_id,
                "is_archived": cmd.is_archived,
            }
        )


def control_campaign(
    cmd: commands.CampaignsCommand,
) -> models.Campaigns:
    if isinstance(cmd, commands.ControlCampaignCommand):
        cmd = typing.cast(commands.ControlCampaignCommand, cmd)
        return cmd.campaign.update(
            {
                "campaign_status": cmd.campaign_status,
            }
        )


def update_next_number_to_dial(
    cmd: commands.CampaignCommand,
) -> models.Campaigns:
    if isinstance(cmd, commands.UpdateCampaignNextToDial):
        cmd = typing.cast(commands.UpdateCampaignNextToDial, cmd)
        return cmd.campaign.update(
            {
                "next_number_to_dial": cmd.next_number_to_dial,
            }
        )
