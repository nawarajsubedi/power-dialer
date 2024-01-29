"""
sql repositories
"""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.dialects import postgresql
from sqlalchemy import select
from krispcall.common.database.connection import DbConnection
from krispcall.campaigns.domain import models
from krispcall.campaigns.adapters.orm import (
    campaign_contact_list_detail,
    campaign_contact_list_mast,
    campaign_voicemails,
    campaign_callscripts,
    campaigns_campaigns,
    campaign_callnotes,
    campaign_stats,
)

from typing import List


class CampaignContactListRepository:
    def __init__(self, db: DbConnection):
        self.db = db

    async def get(self, ref: UUID) -> models.CampaignContactListMast:
        record = await self.db.fetch_one(
            query=campaign_contact_list_mast.select().where(
                campaign_contact_list_mast.c.id == ref
            )
        )
        return models.CampaignContactListMast.construct(
            id_=record["id"],
            name=record["name"],
            contact_count=record["contact_count"],
            creacted_by_name=record["created_by_name"],
            is_archived=record["is_archived"],
            is_contact_list_hidden=record["is_imported_contact_list_hidden"],
            workspace_id=record["workspace_id"],
        )

    async def add_master_data(
        self, model: models.CampaignContactListMast, principal: UUID
    ):
        values = {
            "id": model.id_,
            "name": model.name,
            "contact_count": str(model.contact_count),
            "is_archived": model.is_archived,
            "is_imported_contact_list_hidden": model.is_contact_list_hidden,
            "created_by_name": model.created_by_name,
            "workspace_id": model.workspace,
            "created_by": principal,
            "modified_by": principal,
        }
        await self.db.execute(
            query=campaign_contact_list_mast.insert(), values=values
        )

    async def add_contact_detail(
        self, model: models.CampaignContactListDetail, principal: UUID
    ):
        values = {
            "id": model.id_,
            "contact_name": model.contact_name,
            "contact_list_id": model.contact_list_id,
            "contact_number": model.contact_number,
            "created_by": principal,
        }
        await self.db.execute(
            query=campaign_contact_list_detail.insert(), values=values
        )

    async def update_contact_mast(self, model: models.CampaignContactListMast):
        values = {
            "name": model.name,
            "contact_count": str(model.contact_count),
            "is_archived": model.is_archived,
            "workspace_id": model.workspace_id,
            "is_imported_contact_list_hidden": model.is_contact_list_hidden,
            "modified_by": model.modified_by,
        }
        await self.db.execute(
            query=campaign_contact_list_mast.update().where(
                campaign_contact_list_mast.c.id == model.id_
            ),
            values=values,
        )

    async def upload_contact_in_bulk(self, records: List[dict]):
        """Bulk insert of contacts, doesn't need custom query because fields are same as table columns"""
        insert_stmt = postgresql.insert(campaign_contact_list_detail).values(
            records
        )  # noqa

        await self.db.execute(
            query=insert_stmt.on_conflict_do_nothing()
        )  # noqa

    async def delete_contacts(self, contacts):
        return await self.db.execute(
            query=campaign_contact_list_detail.delete().where(
                campaign_contact_list_detail.c.id.in_(contacts),
            )
        )


class CampaignVoicemailRepository:
    def __init__(self, db: DbConnection):
        self.db = db

    async def get(self, ref: UUID) -> models.CampaignVoicemail:
        record = await self.db.fetch_one(
            query=campaign_voicemails.select().where(
                campaign_voicemails.c.id == ref
            )
        )
        return models.CampaignVoicemail.construct(
            id_=record["id"],
            name=record["name"],
            source=record["tts_source"],
            recording_type=record["recording_type"],
            recording_url=record["recording_url"],
            created_by_name=record["created_by_name"],
            voice=record["tts_gender"],
            accent=record["tts_accent"],
            is_default=record["is_default"],
            workspace_id=record["workspace_id"],
        )

    async def add(self, model: models.CampaignVoicemail, principal: UUID):
        values = {
            "id": model.id_,
            "name": model.name,
            "recording_type": model.recording_type,
            "created_by_name": model.created_by_name,
            "recording_url": model.recording_url,
            "tts_source": model.source,
            "tts_gender": model.voice,
            "tts_accent": model.accent,
            "is_default": model.is_default,
            "workspace_id": model.workspace_id,
            "created_by": principal,
        }
        await self.db.execute(
            query=campaign_voicemails.insert(), values=values
        )

    async def update_voicemail(self, model: models.CampaignVoicemail):
        values = {
            "name": model.name,
            "is_default": model.is_default,
        }
        await self.db.execute(
            query=campaign_voicemails.update().where(
                campaign_voicemails.c.id == model.id_
            ),
            values=values,
        )

    async def drop_voicemail(self, model: models.CampaignVoicemail):
        await self.db.execute(
            query=campaign_voicemails.delete().where(
                campaign_voicemails.c.id == model.id_
            ),
        )


class CampaignCallScriptsRepository:
    def __init__(self, db: DbConnection):
        self.db = db

    async def get(self, ref: UUID) -> models.CampaignCallScripts:
        record = await self.db.fetch_one(
            query=campaign_callscripts.select().where(
                campaign_callscripts.c.id == ref
            )
        )
        return models.CampaignCallScripts.construct(
            id_=record["id"],
            created_by_name=record["created_by_name"],
            script_title=record["script_title"],
            description=record["description"],
            is_default=record["is_default"],
            workspace_id=record["workspace_id"],
        )

    async def add(self, model: models.CampaignCallScripts, principal: UUID):
        values = {
            "id": model.id_,
            "created_by_name": model.created_by_name,
            "script_title": model.script_title,
            "description": model.description,
            "is_default": model.is_default,
            "workspace_id": model.workspace_id,
            "created_by": principal,
        }
        await self.db.execute(
            query=campaign_callscripts.insert(), values=values
        )

    async def update_callscripts(self, model: models.CampaignCallScripts):
        values = {
            "script_title": model.script_title,
            "description": model.description,
            "is_default": model.is_default,
        }
        await self.db.execute(
            query=campaign_callscripts.update().where(
                campaign_callscripts.c.id == model.id_
            ),
            values=values,
        )

    async def drop_callscripts(self, model: models.CampaignCallScripts):
        await self.db.execute(
            query=campaign_callscripts.delete().where(
                campaign_callscripts.c.id == model.id_
            ),
        )


class CampaignCallNotesRepository:
    def __init__(self, db: DbConnection):
        self.db = db

    async def get(self, ref: UUID) -> models.CampaignCallNotes:
        record = await self.db.fetch_one(
            query=campaign_callnotes.select().where(
                campaign_callnotes.c.id == ref
            )
        )
        return models.CampaignCallNotes.construct(
            id_=record["id"],
            campaign_conversation_id=record["campaign_conversation_id"],
            campaign_id=record["campaign_id"],
            call_note=record["call_note"],
        )

    async def add(self, model: models.CampaignCallNotes, principal: UUID):
        values = {
            "id": model.id_,
            "campaign_conversation_id": model.campaign_conversation_id,
            "campaign_id": model.campaign_id,
            "call_note": model.call_note,
            "created_by": principal,
        }
        await self.db.execute(query=campaign_callnotes.insert(), values=values)

    async def update(self, model: models.CampaignCallNotes):
        values = {
            "id": model.id_,
            "call_note": model.call_note,
        }
        await self.db.execute(
            query=campaign_callnotes.update().where(
                campaign_callnotes.c.id == model.id_
            ),
            values=values,
        )


class CampaignsRepository:
    def __init__(self, db: DbConnection):
        self.db = db

    async def get(self, ref: UUID) -> models.Campaigns:
        record = await self.db.fetch_one(
            query=campaigns_campaigns.select().where(
                campaigns_campaigns.c.id == ref
            )
        )
        return models.Campaigns.construct(
            id_=record["id"],
            workspace_id=record["workspace_id"],
            campaign_name=record["campaign_name"],
            assigne_name=record["assigne_name"],
            assigne_id=record["assigne_id"],
            created_by_name=record["created_by_name"],
            dialing_number_id=record["dialing_number_id"],
            dialing_number=record["dialing_number"],
            calling_datacenter=record["calling_datacenter"],
            campaign_status=record["campaign_status"],
            call_recording_enabled=record["call_recording_enabled"],
            voicemail_enabled=record["voicemail_enabled"],
            voicemail_id=record["voicemail_id"],
            cooloff_period_enabled=record["cooloff_period_enabled"],
            cool_off_period=record["cool_off_period"],
            call_attempts_enabled=record["call_attempts_enabled"],
            call_attempts_count=record["call_attempts_count"],
            call_attempts_gap=record["call_attempts_gap"],
            call_script_enabled=record["call_script_enabled"],
            call_script_id=record["call_script_id"],
            contact_list_id=record["contact_list_id"],
            next_number_to_dial=record["next_number_to_dial"],
            is_archived=record["is_archived"],
            created_by=record["created_by"],
            modified_by=record["modified_by"],
            callable_data=record["callable_data"],
        )

    async def add(self, model: models.Campaigns, principal: UUID):
        values = {
            "id": model.id_,
            "workspace_id": model.workspace_id,
            "campaign_name": model.campaign_name,
            "assigne_name": model.assigne_name,
            "assigne_id": model.assigne_id,
            "created_by_name": model.created_by_name,
            "dialing_number_id": model.dialing_number_id,
            "dialing_number": model.dialing_number,
            "calling_datacenter": model.calling_datacenter,
            "campaign_status": model.campaign_status,
            "call_recording_enabled": model.call_recording_enabled,
            "voicemail_enabled": model.voicemail_enabled,
            "voicemail_id": model.voicemail_id,
            "cooloff_period_enabled": model.cooloff_period_enabled,
            "cool_off_period": model.cool_off_period,
            "call_attempts_enabled": model.call_attempts_enabled,
            "call_attempts_count": model.call_attempts_count,
            "call_attempts_gap": model.call_attempts_gap,
            "call_script_enabled": model.call_script_enabled,
            "call_script_id": model.call_script_id,
            "contact_list_id": model.contact_list_id,
            "next_number_to_dial": model.next_number_to_dial,
            "is_archived": model.is_archived,
            "created_by": principal,
            "modified_by": principal,
            "callable_data": model.callable_data,
        }
        await self.db.execute(
            query=campaigns_campaigns.insert(), values=values
        )

    async def update_campaigns(
        self, model: models.Campaigns, principal: UUID, created_by: UUID
    ):
        values = {
            "workspace_id": model.workspace_id,
            "campaign_name": model.campaign_name,
            "assigne_name": model.assigne_name,
            "assigne_id": model.assigne_id,
            "created_by_name": model.created_by_name,
            "dialing_number_id": model.dialing_number_id,
            "dialing_number": model.dialing_number,
            "calling_datacenter": model.calling_datacenter,
            "campaign_status": model.campaign_status,
            "call_recording_enabled": model.call_recording_enabled,
            "voicemail_enabled": model.voicemail_enabled,
            "voicemail_id": model.voicemail_id,
            "cooloff_period_enabled": model.cooloff_period_enabled,
            "cool_off_period": model.cool_off_period,
            "call_attempts_enabled": model.call_attempts_enabled,
            "call_attempts_count": model.call_attempts_count,
            "call_attempts_gap": model.call_attempts_gap,
            "call_script_enabled": model.call_script_enabled,
            "call_script_id": model.call_script_id,
            "contact_list_id": model.contact_list_id,
            "next_number_to_dial": model.next_number_to_dial,
            "is_archived": model.is_archived,
            "created_by": created_by,
            "modified_by": principal,
        }
        await self.db.execute(
            query=campaigns_campaigns.update().where(
                campaigns_campaigns.c.id == model.id_
            ),
            values=values,
        )


class CampaignStatRepository:
    def __init__(self, db: DbConnection):
        self.db = db

    async def get(self, ref: UUID) -> models.CampaignStats:
        query = campaign_stats.select().where(
            campaign_stats.c.campaign_id == ref
        )
        record = await self.db.fetch_one(query=query)
        return models.CampaignStats(
            id_=record["id"],
            campaign_id=record["campaign_id"],
            total_contacts=record["total_contacts"],
            dialed_contacts=record["dialed_contacts"],
            answered_calls=record["answered_calls"],
            unanswered_calls=record["unanswered_calls"],
            campaign_duration=record["campaign_duration"],
            active_call_duration=record["active_call_duration"],
            voicemail_drops=record["voicemail_drops"],
        )

    async def update(
        self, model: models.CampaignStats, field: str, value: int
    ) -> models.CampaignStats:
        async with self.db.connection() as connection:
            async with connection.transaction():
                connection = self.db

                await connection.execute(
                    select([campaign_stats.c.id])
                    .where(campaign_stats.c.id == model.id_)
                    .with_for_update()
                )
                record = await self.db.fetch_one(
                    query=campaign_stats.select().where(
                        campaign_stats.c.id == model.id_
                    )
                )
                # model = model.update({field: record[field] + value})
                query = (
                    campaign_stats.update()
                    .values(**{field: record[field] + value})
                    .where(campaign_stats.c.id == model.id_)
                )
                await self.db.execute(query=query)
        return model

    async def add(self, model: models.CampaignStats) -> models.CampaignStats:
        query = campaign_stats.insert().values(
            id=model.id_,
            campaign_id=model.campaign_id,
            total_contacts=model.total_contacts,
            dialed_contacts=model.dialed_contacts,
            answered_calls=model.answered_calls,
            unanswered_calls=model.unanswered_calls,
            campaign_duration=model.campaign_duration,
            active_call_duration=model.active_call_duration,
            voicemail_drops=model.voicemail_drops,
        )
        await self.db.execute(query=query)
        return model
