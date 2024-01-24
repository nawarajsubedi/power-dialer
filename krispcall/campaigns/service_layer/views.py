from __future__ import annotations

from uuid import UUID
from krispcall.campaigns.service_layer.abstracts import CampPaginationParams
from krispcall.common.service_layer.abstracts import PaginationParams
from krispcall.common.service_layer.pagination import CursorPagination
import sqlalchemy as sa
from krispcall.core.protocols.database import DbConnection
from krispcall.campaigns.adapters import orm


async def get_campaign_contact_list(
    workspace_id: UUID, fetch_archived: bool, db_conn: DbConnection
) -> bool:
    query_j = orm.campaign_contact_list_mast.join(
        orm.campaigns_campaigns,
        orm.campaigns_campaigns.c.contact_list_id
        == orm.campaign_contact_list_mast.c.id,
        isouter=True,
    )
    return await db_conn.fetch_all(
        sa.select(
            [
                orm.campaign_contact_list_mast.c.id,
                orm.campaign_contact_list_mast.c.name,
                orm.campaign_contact_list_mast.c.created_by_name,
                orm.campaign_contact_list_mast.c.contact_count,
                orm.campaign_contact_list_mast.c.is_archived,
                orm.campaigns_campaigns.c.campaign_name,
                orm.campaign_contact_list_mast.c.created_on,
            ]
        )
        .select_from(query_j)
        .where(
            sa.and_(
                orm.campaign_contact_list_mast.c.workspace_id == workspace_id,
                orm.campaign_contact_list_mast.c.is_archived == fetch_archived,
            )
        )
        .order_by(orm.campaign_contact_list_mast.c.created_on.desc())
    )


async def get_contact_detail_by_number(
    number: str, db_conn: DbConnection, mast_id: UUID
):
    return await db_conn.fetch_one(
        sa.select(
            [
                orm.campaign_contact_list_detail.c.id,
                orm.campaign_contact_list_detail.c.contact_name,
                orm.campaign_contact_list_detail.c.contact_number,
                orm.campaign_contact_list_detail.c.created_on,
            ]
        ).where(
            sa.and_(
                orm.campaign_contact_list_detail.c.contact_number == number,
                orm.campaign_contact_list_detail.c.contact_list_id == mast_id,
            )
        )
    )


async def get_campaign_contact_dtl_list(
    contact_master_id: UUID,
    db_conn: DbConnection,
):
    return await db_conn.fetch_all(
        sa.select(
            [
                orm.campaign_contact_list_detail.c.id,
                orm.campaign_contact_list_detail.c.contact_name,
                orm.campaign_contact_list_detail.c.contact_number,
                orm.campaign_contact_list_detail.c.created_on,
            ]
        )
        .where(
            orm.campaign_contact_list_detail.c.contact_list_id
            == contact_master_id,
        )
        .order_by(orm.campaign_contact_list_detail.c.created_on.desc())
    )


async def get_voicemail_by_id(
    voicemail_id: UUID,
    db_conn: DbConnection,
):
    return await db_conn.fetch_one(
        sa.select(
            [
                orm.campaign_voicemails.c.id,
                orm.campaign_voicemails.c.name,
                orm.campaign_voicemails.c.recording_type,
                orm.campaign_voicemails.c.recording_url,
            ]
        ).where(
            orm.campaign_voicemails.c.id == voicemail_id,
        )
    )


async def get_campaign_voicemail_list(
    workspace_id,
    db_conn: DbConnection,
):
    return await db_conn.fetch_all(
        sa.select(
            [
                orm.campaign_voicemails.c.id,
                orm.campaign_voicemails.c.name,
                orm.campaign_voicemails.c.recording_type,
                orm.campaign_voicemails.c.recording_url,
                orm.campaign_voicemails.c.tts_source,
                orm.campaign_voicemails.c.tts_gender,
                orm.campaign_voicemails.c.tts_accent,
                orm.campaign_voicemails.c.is_default,
                orm.campaign_voicemails.c.created_by_name,
                orm.campaign_voicemails.c.created_on,
            ]
        )
        .where(
            sa.and_(
                orm.campaign_voicemails.c.workspace_id == workspace_id,
            )
        )
        .order_by(orm.campaign_voicemails.c.created_on.desc())
    )


async def get_default_campaign_voicemail_list(
    workspace_id,
    db_conn: DbConnection,
    is_default: bool,
):
    return await db_conn.fetch_one(
        sa.select(
            [
                orm.campaign_voicemails.c.id.label("id_"),
                orm.campaign_voicemails.c.name,
                orm.campaign_voicemails.c.recording_type,
                orm.campaign_voicemails.c.recording_url,
                orm.campaign_voicemails.c.is_default,
                orm.campaign_voicemails.c.created_by_name,
                orm.campaign_voicemails.c.workspace_id,
            ]
        ).where(
            sa.and_(
                orm.campaign_voicemails.c.workspace_id == workspace_id,
                orm.campaign_voicemails.c.is_default == is_default,
            )
        )
    )


async def get_default_campaign_callScripts(
    workspace_id,
    db_conn: DbConnection,
    is_default: bool,
):
    return await db_conn.fetch_one(
        sa.select(
            [
                orm.campaign_callscripts.c.id.label("id_"),
                orm.campaign_callscripts.c.script_title,
                orm.campaign_callscripts.c.description,
                orm.campaign_callscripts.c.is_default,
                orm.campaign_callscripts.c.workspace_id,
                orm.campaign_callscripts.c.created_by_name,
            ]
        ).where(
            sa.and_(
                orm.campaign_callscripts.c.workspace_id == workspace_id,
                orm.campaign_callscripts.c.is_default == is_default,
            )
        )
    )


async def get_campaign_callScript_list(
    workspace_id,
    db_conn: DbConnection,
):
    return await db_conn.fetch_all(
        sa.select(
            [
                orm.campaign_callscripts.c.id.label("id"),
                orm.campaign_callscripts.c.script_title,
                orm.campaign_callscripts.c.description,
                orm.campaign_callscripts.c.is_default,
                orm.campaign_callscripts.c.workspace_id,
                orm.campaign_callscripts.c.created_by_name,
                orm.campaign_callscripts.c.created_on,
            ]
        )
        .where(
            sa.and_(
                orm.campaign_callscripts.c.workspace_id == workspace_id,
            )
        )
        .order_by(orm.campaign_callscripts.c.created_on.desc())
    )


async def get_callScript_by_id(
    workspace_id,
    db_conn: DbConnection,
    call_script_id: UUID,
):
    return await db_conn.fetch_one(
        sa.select(
            [
                orm.campaign_callscripts.c.id.label("id"),
                orm.campaign_callscripts.c.script_title,
                orm.campaign_callscripts.c.description,
                orm.campaign_callscripts.c.is_default,
                orm.campaign_callscripts.c.workspace_id,
                orm.campaign_callscripts.c.created_by_name,
                orm.campaign_callscripts.c.created_on,
            ]
        ).where(
            sa.and_(
                orm.campaign_callscripts.c.workspace_id == workspace_id,
                orm.campaign_callscripts.c.id == call_script_id,
            )
        )
    )


async def get_campaign_callScriptAttribute_list(
    db_conn: DbConnection,
):
    return await db_conn.fetch_all(
        sa.select(
            [
                orm.campaign_callscripts_attributes.c.id.label("id"),
                orm.campaign_callscripts_attributes.c.name,
                orm.campaign_callscripts_attributes.c.description,
            ]
        )
    )


async def get_campaigns_states(workspace: UUID, db_conn: DbConnection):
    query = sa.select(
        [
            orm.campaigns_campaigns.c.id,
            orm.campaigns_campaigns.c.is_archived,
        ]
    ).where(
        sa.and_(
            orm.campaigns_campaigns.c.workspace_id == workspace,
        )
    )
    return await db_conn.fetch_all(query)


async def get_campaigns_list(
    params: PaginationParams,
    workspace_id: UUID,
    fetch_archived: bool,
    db_conn: DbConnection,
):
    query_j = orm.campaigns_campaigns.join(
        orm.campaign_contact_list_mast,
        orm.campaigns_campaigns.c.contact_list_id
        == orm.campaign_contact_list_mast.c.id,
    )
    filter = sa.and_(
        orm.campaigns_campaigns.c.workspace_id == workspace_id,
        orm.campaigns_campaigns.c.is_archived == fetch_archived,
    )
    if params.search:
        value = params.search.value
        filter = sa.and_(
            orm.campaigns_campaigns.c.workspace_id == workspace_id,
            orm.campaigns_campaigns.c.is_archived == fetch_archived,
            orm.campaigns_campaigns.c.campaign_name.ilike(f"%{str(value)}%"),
        )

    query = (
        sa.select(
            [
                orm.campaigns_campaigns.c.id,
                orm.campaigns_campaigns.c.workspace_id,
                orm.campaigns_campaigns.c.created_by_name,
                orm.campaigns_campaigns.c.campaign_name,
                orm.campaigns_campaigns.c.assigne_name,
                orm.campaigns_campaigns.c.assigne_id,
                orm.campaigns_campaigns.c.dialing_number,
                orm.campaigns_campaigns.c.dialing_number_id,
                orm.campaigns_campaigns.c.calling_datacenter,
                orm.campaigns_campaigns.c.campaign_status,
                orm.campaigns_campaigns.c.call_recording_enabled,
                orm.campaigns_campaigns.c.voicemail_enabled,
                orm.campaigns_campaigns.c.voicemail_id,
                orm.campaigns_campaigns.c.cooloff_period_enabled,
                orm.campaigns_campaigns.c.cool_off_period,
                orm.campaigns_campaigns.c.call_attempts_enabled,
                orm.campaigns_campaigns.c.call_attempts_count,
                orm.campaigns_campaigns.c.call_attempts_gap,
                orm.campaigns_campaigns.c.call_script_enabled,
                orm.campaigns_campaigns.c.is_archived,
                orm.campaigns_campaigns.c.call_script_id,
                orm.campaigns_campaigns.c.contact_list_id,
                orm.campaigns_campaigns.c.next_number_to_dial,
                orm.campaigns_campaigns.c.created_on,
                orm.campaigns_campaigns.c.assigne_name.label("created_by"),
                orm.campaign_contact_list_mast.c.contact_count,
                orm.campaign_contact_list_mast.c.name.label(
                    "contact_list_name"
                ),
                orm.campaign_contact_list_mast.c.is_imported_contact_list_hidden,
            ]
        )
        .select_from(query_j)
        .where(filter)
        .order_by(orm.campaigns_campaigns.c.created_on.desc())
    )
    pagination = CursorPagination(
        query=query, db_conn=db_conn, cursor_column="created_on"
    )
    return await pagination.page(params)


async def get_campaign_by_id(
    campaign_id: UUID,
    db_conn: DbConnection,
):
    query_j = orm.campaigns_campaigns.join(
        orm.campaign_contact_list_mast,
        orm.campaigns_campaigns.c.contact_list_id
        == orm.campaign_contact_list_mast.c.id,
    )
    data = await db_conn.fetch_one(
        sa.select(
            [
                orm.campaigns_campaigns.c.id,
                orm.campaigns_campaigns.c.workspace_id,
                orm.campaigns_campaigns.c.created_by_name,
                orm.campaigns_campaigns.c.campaign_name,
                orm.campaigns_campaigns.c.assigne_name.label("assignee_name"),
                orm.campaigns_campaigns.c.assigne_id.label("assignee_id"),
                orm.campaigns_campaigns.c.dialing_number,
                orm.campaigns_campaigns.c.dialing_number_id,
                orm.campaigns_campaigns.c.calling_datacenter,
                orm.campaigns_campaigns.c.campaign_status,
                orm.campaigns_campaigns.c.call_recording_enabled,
                orm.campaigns_campaigns.c.voicemail_enabled,
                orm.campaigns_campaigns.c.voicemail_id,
                orm.campaigns_campaigns.c.cooloff_period_enabled,
                orm.campaigns_campaigns.c.cool_off_period,
                orm.campaigns_campaigns.c.call_attempts_enabled,
                orm.campaigns_campaigns.c.call_attempts_count,
                orm.campaigns_campaigns.c.call_attempts_gap,
                orm.campaigns_campaigns.c.call_script_enabled,
                orm.campaigns_campaigns.c.is_archived,
                orm.campaigns_campaigns.c.call_script_id,
                orm.campaigns_campaigns.c.contact_list_id,
                orm.campaigns_campaigns.c.next_number_to_dial,
                orm.campaigns_campaigns.c.created_on,
                orm.campaign_contact_list_mast.c.contact_count,
                orm.campaign_contact_list_mast.c.name,
                orm.campaign_contact_list_mast.c.is_imported_contact_list_hidden,
            ]
        )
        .select_from(query_j)
        .where(
            sa.and_(
                orm.campaigns_campaigns.c.id == campaign_id,
            )
        )
    )
    return data


async def get_campaign_stats(campaign_id: UUID, db_conn: DbConnection):
    return await db_conn.fetch_one(
        sa.select(
            [
                orm.campaign_stats.c.id,
                orm.campaign_stats.c.campaign_id,
                orm.campaign_stats.c.total_contacts,
                orm.campaign_stats.c.dialed_contacts,
                orm.campaign_stats.c.answered_calls,
                orm.campaign_stats.c.voicemail_drops,
                orm.campaign_stats.c.unanswered_calls,
                orm.campaign_stats.c.campaign_duration,
                orm.campaign_stats.c.active_call_duration,
            ]
        ).where(orm.campaign_stats.c.campaign_id == campaign_id)
    )


async def contact_list_length(contact_list_id: UUID, db_conn: DbConnection):
    query = (
        sa.select([orm.campaign_contact_list_detail.c.id])
        .select_from(orm.campaign_contact_list_detail)
        .where(
            orm.campaign_contact_list_detail.c.contact_list_id
            == contact_list_id
        )
        .alias("subquery")
    )
    return await db_conn.fetch_val(
        sa.select([sa.func.count()]).select_from(query)
    )


async def get_campaign_note(note_id: UUID, db_conn: DbConnection):
    query = sa.select(
        [
            orm.campaign_callnotes.c.id,
            orm.campaign_callnotes.c.call_note,
            orm.campaign_callnotes.c.created_at,
            orm.campaign_callnotes.c.created_by,
        ]
    ).where(orm.campaign_callnotes.c.id == note_id)
    return await db_conn.fetch_one(query=query)


async def get_campaign_voicemail_by_id(
    voicemail_id: UUID, db_conn: DbConnection
):
    query = sa.select(
        [
            orm.campaign_voicemails.c.id,
            orm.campaign_voicemails.c.name,
            orm.campaign_voicemails.c.recording_type,
            orm.campaign_voicemails.c.recording_url,
        ]
    ).where(orm.campaign_voicemails.c.id == voicemail_id)
    return await db_conn.fetch_one(query=query)


async def get_campaign_callscript(callscript_id: UUID, db_conn: DbConnection):
    query = sa.select(
        [
            orm.campaign_callscripts.c.id,
            orm.campaign_callscripts.c.script_title,
            orm.campaign_callscripts.c.description,
            orm.campaign_callscripts.c.created_by_name,
        ]
    ).where(orm.campaign_callscripts.c.id == callscript_id)
    return await db_conn.fetch_one(query=query)


async def get_campaign_voicemail(campaign_id: UUID, db_conn: DbConnection):
    subquery = (
        sa.select([orm.campaigns_campaigns.c.voicemail_id])
        .where(orm.campaigns_campaigns.c.id == campaign_id)
        .alias("subquery")
    )
    query = sa.select(
        [
            orm.campaign_voicemails.c.id,
            orm.campaign_voicemails.c.name,
            orm.campaign_voicemails.c.recording_type,
            orm.campaign_voicemails.c.recording_url,
        ]
    ).where(orm.campaign_voicemails.c.id == subquery.c.voicemail_id)
    return await db_conn.fetch_one(query=query)
