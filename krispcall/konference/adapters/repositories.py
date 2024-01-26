from __future__ import annotations
import datetime
import asyncio
import typing
from uuid import UUID
from sqlalchemy.dialects import postgresql
from krispcall.konference.domain import models
from krispcall.konference.adapters import orm
from krispcall.common.database.connection import DbConnection


class CampaignConversationRepository:
    def __init__(self, db: DbConnection):
        self.db = db

    async def bulk_add(self, data: typing.List[models.CampaignConversation]):
        records = [
            {
                "id": model.id_,
                "twi_sid": model.twi_sid,
                "campaign_id": model.campaign_id,
                "status": model.status.value,
                "created_by": model.created_by,
                "sequence_number": model.sequence_number,
                "contact_name": model.contact_name,
                "contact_number": model.contact_number,
                "recording_url": model.recording_url,
                "current_attempt": model.current_attempt,
                "initial_call": model.initial_call,
                "recording_duration": model.recording_duration,
                "call_duration": model.call_duration,
                "skipped": model.skipped,
                "skip_cooldown": model.skip_cooldown,
                "reason_message": model.reason_message,
                "reason_code": model.reason_code,
                "created_at": datetime.datetime.now(),
                "modified_at": datetime.datetime.now(),
            }
            for model in data
        ]
        query = postgresql.insert(orm.campaign_conversation).values(records)
        await self.db.execute(query=query)

    async def bulk_complete(self, campaign_id: UUID, st: typing.List[str]):
        query = f"""
            UPDATE campaign_conversation
            SET status = 'completed'
            WHERE campaign_id = '{campaign_id}'
            AND status in {tuple(st)};
            """
        await self.db.execute(f"{query}")

    async def add(self, model: models.CampaignConversation):
        """Adds campaign conversation with default values"""
        values = {
            "id": model.id_,
            "twi_sid": model.twi_sid,
            "campaign_id": model.campaign_id,
            "status": model.status,
            "created_by": model.created_by,
            "sequence_number": model.sequence_number,
            "contact_name": model.contact_name,
            "contact_number": model.contact_number,
            "recording_url": model.recording_url,
            "current_attempt": model.current_attempt,
            "initial_call": model.initial_call,
            "recording_duration": model.recording_duration,
            "call_duration": model.call_duration,
            "skipped": model.skipped,
            "skip_cooldown": model.skip_cooldown,
            "reason_message": model.reason_message,
            "reason_code": model.reason_code,
        }
        await self.db.execute(
            query=orm.campaign_conversation.insert(),
            values=values,
        )
        return model

    async def add_multiple(self, models: typing.List[models.CampaignConversation]):
        tasks = asyncio.gather(*[self.add(model) for model in models])
        asyncio.run(tasks)

    async def skip_conversation(self, id: UUID):
        await self.db.execute(
            query=orm.campaign_conversation.update().where(
                orm.campaign_conversation.c.id == id
            ),
            values={"skipped": True},
        )

    async def skip_cooldown(self, id: UUID):
        """Skips the cool down period for a conversation i.e.
        specific client being called, and immediately calls
        them in the conference handler webhook
        """
        await self.db.execute(
            query=orm.campaign_conversation.update().where(
                orm.campaign_conversation.c.id == id
            ),
            values={"skip_cooldown": True},
        )

    async def get(self, conversation_id: UUID) -> models.CampaignConversation:
        """Fetches single campaign conversation by campaign id: UUID"""
        record = await self.db.fetch_one(
            query=orm.campaign_conversation.select().where(
                orm.campaign_conversation.c.id == conversation_id
            )
        )
        return models.CampaignConversation(
            id_=record["id"],
            twi_sid=record["twi_sid"],
            campaign_id=record["campaign_id"],
            status=record["status"],
            created_by=record["created_by"],
            modified_at=record["modified_at"],
            sequence_number=record["sequence_number"],
            contact_name=record["contact_name"],
            contact_number=record["contact_number"],
            recording_url=record["recording_url"],
            recording_duration=record["recording_duration"],
            initial_call=record["initial_call"],
            current_attempt=record["current_attempt"],
            skip_cooldown=record["skip_cooldown"],
            campaign_note_id=record["campaign_note_id"],
            call_duration=record["call_duration"],
            reason_message=record["reason_message"],
            reason_code=record["reason_code"],
        )  # type: ignore

    async def get_by_twi_sid(self, twi_sid: str) -> models.CampaignConversation:
        """Fetches single campaign conversation by twilio conference sid: str"""
        record = await self.db.fetch_one(
            query=orm.campaign_conversation.select().where(
                orm.campaign_conversation.c.twi_sid == twi_sid
            )
        )
        return models.CampaignConversation(
            id_=record["id"],
            twi_sid=record["twi_sid"],
            campaign_id=record["campaign_id"],
            status=record["status"],
            created_by=record["created_by"],
            recording_url=record["recording_url"],
            recording_duration=record["recording_duration"],
            call_duration=record["call_duration"],
            reason_message=record["reason_message"],
            reason_code=record["reason_code"],
        )  # type: ignore

    async def update_conversation_status(self, model: models.CampaignConversation):
        """Updates the conversation status according to twilio conference status"""
        await self.db.execute(
            query=orm.campaign_conversation.update().where(
                orm.campaign_conversation.c.id == model.id_
            ),
            values={"status": model.status},
        )

    async def update_conversation_status_with_reason(
        self, model: models.CampaignConversation
    ):
        """Updates the conversation status and status reason according to twilio conference status"""
        await self.db.execute(
            query=orm.campaign_conversation.update().where(
                orm.campaign_conversation.c.id == model.id_
            ),
            values={
                "status": model.status,
                "reason_message": model.reason_message,
                "reason_code": model.reason_code,
            },
        )

    async def update_recording_info(
        self, ref: UUID, recording_url: str, recording_duration: int
    ):
        """Updates recording duration as conference recording duration"""
        await self.db.execute(
            query=orm.campaign_conversation.update().where(
                orm.campaign_conversation.c.id == ref
            ),
            values={
                "recording_duration": int(recording_duration),
                "recording_url": recording_url,
            },
        )

    async def update_call_duration(self, model: models.CampaignConversation):
        """Updates call duration as conference call duration"""
        await self.db.execute(
            query=orm.campaign_conversation.update().where(
                orm.campaign_conversation.c.id == model.id_
            ),
            values={"call_duration": model.call_duration},
        )

    async def update_call_note(self, model: models.CampaignConversation):
        """Updates call note id"""
        await self.db.execute(
            query=orm.campaign_conversation.update().where(
                orm.campaign_conversation.c.id == model.id_
            ),
            values={"campaign_note_id": model.campaign_note_id},
        )


class ParticipantCallRepository:
    def __init__(self, db: DbConnection):
        self.db = db

    async def add(self, model: models.ParticipantCall):
        """Adds participant call with default values"""
        values = {
            "id": model.id_,
            "conversation_id": model.conversation_id,
            "twi_sid": model.twi_sid,
            "status": model.status,
            "participant_type": model.participant_type,
            "created_by": model.created_by,
            "recording_url": model.recording_url,
            "recording_duration": model.recording_duration,
            "call_duration": model.call_duration,
        }
        await self.db.execute(
            query=orm.participant_calls.insert(),
            values=values,
        )
        return model

    async def get(self, conversation_id: UUID) -> models.ParticipantCall:
        """Fetches single participant conversation by conversation id: UUID"""
        record = await self.db.fetch_one(
            query=orm.participant_calls.select().where(
                orm.participant_calls.c.conversation_id == conversation_id
            )
        )
        return models.ParticipantCall(
            id_=record["id"],
            conversation_id=record["conversation_id"],
            twi_sid=record["twi_sid"],
            status=record["status"],
            participant_type=record["participant_type"],
            created_by=record["created_by"],
            recording_url=record["recording_url"],
            call_duration=record["call_duration"],
            recording_duration=record["recording_duration"],
        )  # type: ignore

    async def get_by_twi_sid(self, twi_sid: str) -> models.ParticipantCall:
        """Fetches single participant call by twilio call sid: str"""
        record = await self.db.fetch_one(
            query=orm.participant_calls.select().where(
                orm.participant_calls.c.twi_sid == twi_sid
            )
        )
        return models.ParticipantCall(
            id_=record["id"],
            conversation_id=record["conversation_id"],
            twi_sid=record["twi_sid"],
            status=record["status"],
            participant_type=record["participant_type"],
            created_by=record["created_by"],
            recording_url=record["recording_url"],
            recording_duration=record["recording_duration"],
            call_duration=record["call_duration"],
        )  # type: ignore

    async def update_call_status(
        self, model: models.ParticipantCall, conversation_id: UUID
    ):
        """Updates the call status according to twilio call status"""
        await self.db.execute(
            query=orm.participant_calls.update().where(
                orm.participant_calls.c.conversation_id == conversation_id
            ),
            values={"status": model.status},
        )

    async def update_call_status_by_twi_sid(self, ref: str, status: str):
        """Updates the call status according to twilio call status"""
        await self.db.execute(
            query=orm.participant_calls.update().where(
                orm.participant_calls.c.twi_sid == ref
            ),
            values={"status": status},
        )

    async def update_recording_url(self, model: models.ParticipantCall):
        """Updates recording url as call recording url"""
        await self.db.execute(
            query=orm.participant_calls.update().where(
                orm.participant_calls.c.id == model.id_
            ),
            values={"recording_url": model.recording_url},
        )

    async def update_recording_duration(self, model: models.ParticipantCall):
        """Updates recording duration as call recording duration"""
        await self.db.execute(
            query=orm.participant_calls.update().where(
                orm.participant_calls.c.id == model.id_
            ),
            values={"recording_duration": model.recording_duration},
        )
