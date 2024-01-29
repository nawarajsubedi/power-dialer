from typing import List
from uuid import UUID, uuid4
from krispcall.konference.service_layer import abstracts
from krispcall.konference.domain import models
from krispcall.common.utils.shortid import ShortId


def create_conversation_data(
    contact_list,
    member: UUID,
    campaign_id: UUID,
    reattempt: bool = False,
    current_sequence_number: int = 0,
) -> List[abstracts.AddCampaignConversationMsg]:
    """Creates conversation data to add to the db"""
    conversation_data = []
    sequence_number = current_sequence_number
    for contact in contact_list:
        sequence_number += 1
        conversation_data.append(
            abstracts.AddCampaignConversationMsg(
                id_=ShortId.with_uuid(uuid4()),
                twi_sid=ShortId.with_uuid(uuid4()),
                campaign_id=ShortId.with_uuid(campaign_id),
                status=models.ConferenceStatus.in_queue,
                created_by=ShortId.with_uuid(member),
                sequence_number=sequence_number,
                contact_name=contact.get("contact_name"),
                contact_number=contact.get("contact_number"),
                initial_call=not reattempt,
            )
        )
    return conversation_data
