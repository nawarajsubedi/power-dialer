from krispcall.konference.service_layer import commands
from krispcall.konference.domain import models


def add_campaign_conversation(cmd) -> models.CampaignConversation:
    return models.campaign_conversation_factory(
        id_=cmd.id_,
        twi_sid=cmd.twi_sid,
        campaign_id=cmd.campaign_id,
        status=cmd.status,
        created_by=cmd.created_by,
        sequence_number=cmd.sequence_number,
        contact_name=cmd.contact_name,
        contact_number=cmd.contact_number,
        recording_url=cmd.recording_url,
        recording_duration=cmd.recording_duration,
        call_duration=cmd.call_duration,
        campaign_note_id=cmd.campaign_note_id,
        initial_call=cmd.initial_call,
        reason_code=cmd.reason_code,
        reason_message=cmd.reason_message,
    )


def update_campaign_note(
    cmd: commands.UpdateCampaignConversationNoteCommand,
    model: models.CampaignConversation,
) -> models.CampaignConversation:
    return model.update({"campaign_note_id": cmd.campaign_note_id})


def add_participant_call(
    cmd: commands.AddCampaignParticipantCommand,
) -> models.ParticipantCall:
    return models.participant_call_factory(
        id_=cmd.id_,
        conversation_id=cmd.conversation_id,
        twi_sid=cmd.twi_sid,
        status=cmd.status,
        participant_type=cmd.participant_type,
        created_by=cmd.created_by,
        recording_url=cmd.recording_url,
        recording_duration=cmd.recording_duration,
        call_duration=cmd.call_duration,
    )


def update_campaign_status(cmd, model) -> models.CampaignConversation:
    return models.campaign_conversation_factory(
        status=cmd.status,
        id_=cmd.id,
        twi_sid=model.twi_sid,
        campaign_id=model.campaign_id,
        created_by=model.created_by,
        sequence_number=model.sequence_number,
        contact_name=model.contact_name,
        contact_number=model.contact_number,
        recording_url=model.recording_url,
        recording_duration=model.recording_duration,
        call_duration=model.call_duration,
        campaign_note_id=model.campaign_note_id,
        reason_message=model.reason_message,
        reason_code=model.reason_code,
    )


def update_conversation_status_with_reason(
    cmd, model
) -> models.CampaignConversation:
    return models.campaign_conversation_factory(
        status=cmd.status,
        reason_message=cmd.reason_message,
        reason_code=cmd.reason_code,
        id_=cmd.id,
        twi_sid=model.twi_sid,
        campaign_id=model.campaign_id,
        created_by=model.created_by,
        sequence_number=model.sequence_number,
        contact_name=model.contact_name,
        contact_number=model.contact_number,
        recording_url=model.recording_url,
        recording_duration=model.recording_duration,
        call_duration=model.call_duration,
        campaign_note_id=model.campaign_note_id,
    )


def update_campaign_participant_status(cmd, model) -> models.ParticipantCall:
    return models.participant_call_factory(
        status=cmd.status,
        id_=cmd.id,
        conversation_id=model.conversation_id,
        twi_sid=model.twi_sid,
        participant_type=model.participant_type,
        created_by=model.created_by,
        recording_url=model.recording_url,
        recording_duration=model.recording_duration,
        call_duration=model.call_duration,
    )


def update_conversation_duration(
    duration, model: models.CampaignConversation
) -> models.CampaignConversation:
    return models.campaign_conversation_factory(
        status=model.status,
        id_=model.id_,
        twi_sid=model.twi_sid,
        campaign_id=model.campaign_id,
        created_by=model.created_by,
        sequence_number=model.sequence_number,
        contact_name=model.contact_name,
        contact_number=model.contact_number,
        recording_url=model.recording_url,
        recording_duration=model.recording_duration,
        call_duration=duration,
        campaign_note_id=model.campaign_note_id,
        reason_message=model.reason_message,
        reason_code=model.reason_code,
    )
