import typing
from uuid import UUID
from krispcall.common.responses.response_model import PaginationParams
from krispcall.common.services.pagination.pagination import CursorPagination
from krispcall.konference.domain import models
from krispcall.konference.adapters import orm
from krispcall.konference.service_layer import unit_of_work
from krispcall.common.database.connection import DbConnection
import sqlalchemy as sa


# async def get_campaign_conference_by_twi_sid(
#     twi_sid: str, db_conn: DbConnection
# ) -> models.CampaignConversation:
#     async with unit_of_work.CampaignConversationSqlUnitOfWork(db_conn) as uow:
#         return await uow.repository.get_by_twi_sid(twi_sid)


async def get_participant_call(
    twi_sid: str, db_conn: DbConnection
) -> models.ParticipantCall:
    async with unit_of_work.ParticipantCallSqlUnitOfWork(db_conn) as uow:
        return await uow.repository.get_by_twi_sid(twi_sid)


async def get_conversation_participants(conversation: UUID, db_conn):
    return await db_conn.fetch_all(
        sa.select(
            [
                orm.participant_calls.c.id,
                orm.participant_calls.c.twi_sid,
                orm.participant_calls.c.conversation_id,
                orm.participant_calls.c.status,
                orm.participant_calls.c.participant_type,
                orm.participant_calls.c.created_by,
            ]
        ).where(
            sa.and_(
                orm.participant_calls.c.conversation_id == conversation,
            )
        )
    )


async def get_participant_call_by_twi_sid(twi_sid: str, db_conn: DbConnection):
    return await db_conn.fetch_one(
        sa.select(
            [
                orm.participant_calls.c.id,
                orm.participant_calls.c.twi_sid,
                orm.participant_calls.c.conversation_id,
                orm.participant_calls.c.status,
                orm.participant_calls.c.participant_type,
                orm.participant_calls.c.created_by,
            ]
        ).where(
            sa.and_(
                orm.participant_calls.c.twi_sid == twi_sid,
            )
        )
    )


async def get_active_campaign_conferences(
    campaign_id: UUID, db_conn: DbConnection, st: typing.List[str]
):
    return await db_conn.fetch_all(
        sa.select(
            [
                orm.campaign_conversation.c.id,
                orm.campaign_conversation.c.twi_sid,
                orm.campaign_conversation.c.initial_call,
                orm.campaign_conversation.c.current_attempt,
                orm.campaign_conversation.c.status,
                orm.campaign_conversation.c.created_by,
                orm.campaign_conversation.c.sequence_number,
                orm.campaign_conversation.c.contact_name,
                orm.campaign_conversation.c.skipped,
                orm.campaign_conversation.c.skip_cooldown,
                orm.campaign_conversation.c.contact_name,
                orm.campaign_conversation.c.contact_number,
                orm.campaign_conversation.c.campaign_id,
            ]
        ).where(
            sa.and_(
                orm.campaign_conversation.c.status.in_(st),
                orm.campaign_conversation.c.campaign_id == campaign_id,
            )
        )
    )


async def get_camaign_conversation(
    conversation_id: UUID, db_conn: DbConnection
):
    return await db_conn.fetch_one(
        sa.select(
            [
                orm.campaign_conversation.c.id,
                orm.campaign_conversation.c.status,
            ]
        ).where(
            sa.and_(
                orm.campaign_conversation.c.id == conversation_id,
            )
        )
    )


async def get_reattempt_list(campaign_id: UUID, db_conn: DbConnection):
    return await db_conn.fetch_all(
        sa.select(
            [
                orm.campaign_conversation.c.id,
                orm.campaign_conversation.c.contact_number,
                orm.campaign_conversation.c.contact_name,
                orm.campaign_conversation.c.skip_cooldown,
            ]
        ).where(
            sa.and_(
                orm.campaign_conversation.c.campaign_id == campaign_id,
                orm.campaign_conversation.c.status.in_(
                    ["failed", "cancelled", "busy", "no_answer"]
                ),
            )
        )
    )


async def has_reattempt_calls(campaign_id: UUID, db_conn: DbConnection):
    return await db_conn.fetch_val(
        query=sa.select(
            [
                sa.exists().where(
                    sa.and_(
                        orm.campaign_conversation.c.campaign_id == campaign_id,
                        orm.campaign_conversation.c.status.in_(
                            ["busy", "no_answer"]
                        ),
                    )
                )
            ]
        )
    )


async def get_final_sequnce_number(campaign_id: UUID, db_conn: DbConnection):
    """Finds the total length of initial conversation"""
    query = (
        sa.select([sa.func.count(orm.campaign_conversation.c.id)])
        .select_from(orm.campaign_conversation)
        .where(
            sa.and_(
                orm.campaign_conversation.c.campaign_id == campaign_id,
                orm.campaign_conversation.c.initial_call == True,
            )
        )
    )
    return await db_conn.fetch_val(query)


async def get_campaign_conversations(
    pagination_params: PaginationParams,
    initial_call: bool,
    campaign_id: UUID,
    db_conn: DbConnection,
    status_filter: str = "",
):
    if status_filter:
        filter = sa.and_(
            orm.campaign_conversation.c.campaign_id == campaign_id,
            orm.campaign_conversation.c.initial_call == initial_call,
            orm.campaign_conversation.c.status == status_filter,
        )
    else:
        filter = sa.and_(
            orm.campaign_conversation.c.campaign_id == campaign_id,
            orm.campaign_conversation.c.initial_call == initial_call,
        )

    query = sa.select(
        [
            orm.campaign_conversation.c.id,
            orm.campaign_conversation.c.twi_sid,
            orm.campaign_conversation.c.initial_call,
            orm.campaign_conversation.c.current_attempt,
            orm.campaign_conversation.c.status,
            orm.campaign_conversation.c.created_by,
            orm.campaign_conversation.c.created_at,
            orm.campaign_conversation.c.created_at.label("call_start_time"),
            orm.campaign_conversation.c.sequence_number,
            orm.campaign_conversation.c.contact_name,
            orm.campaign_conversation.c.skipped,
            orm.campaign_conversation.c.skip_cooldown,
            orm.campaign_conversation.c.contact_number,
            orm.campaign_conversation.c.campaign_id,
            orm.campaign_conversation.c.recording_url,
            orm.campaign_conversation.c.recording_duration,
            orm.campaign_conversation.c.call_duration,
            orm.campaign_conversation.c.reason_message,
            orm.campaign_conversation.c.campaign_note_id.label(
                "conversation_note"
            ),
        ]
    ).where(sa.and_(filter))
    pagination = CursorPagination(
        query=query, db_conn=db_conn, cursor_column="created_at"
    )
    return await pagination.page(pagination_params)


async def get_campaign_conference_by_twi_sid(
    twi_sid: UUID, db_conn: DbConnection
):
    return await db_conn.fetch_one(
        sa.select(
            [
                orm.campaign_conversation.c.id,
                orm.campaign_conversation.c.twi_sid,
                orm.campaign_conversation.c.initial_call,
                orm.campaign_conversation.c.current_attempt,
                orm.campaign_conversation.c.status,
                orm.campaign_conversation.c.created_by,
                orm.campaign_conversation.c.sequence_number,
                orm.campaign_conversation.c.contact_name,
                orm.campaign_conversation.c.skipped,
                orm.campaign_conversation.c.skip_cooldown,
                orm.campaign_conversation.c.contact_name,
                orm.campaign_conversation.c.contact_number,
                orm.campaign_conversation.c.campaign_id,
            ]
        ).where(
            sa.and_(
                orm.campaign_conversation.c.twi_sid == twi_sid,
            )
        )
    )


async def get_campaign_conference_by_id(ref: UUID, db_conn: DbConnection):
    return await db_conn.fetch_one(
        sa.select(
            [
                orm.campaign_conversation.c.id,
                orm.campaign_conversation.c.twi_sid,
                orm.campaign_conversation.c.initial_call,
                orm.campaign_conversation.c.current_attempt,
                orm.campaign_conversation.c.status,
                orm.campaign_conversation.c.created_by,
                orm.campaign_conversation.c.sequence_number,
                orm.campaign_conversation.c.contact_name,
                orm.campaign_conversation.c.skipped,
                orm.campaign_conversation.c.skip_cooldown,
                orm.campaign_conversation.c.contact_name,
                orm.campaign_conversation.c.contact_number,
                orm.campaign_conversation.c.campaign_id,
            ]
        ).where(
            sa.and_(
                orm.campaign_conversation.c.id == ref,
            )
        )
    )


async def get_campaign_conference_by_sequence_number(
    campaign_id: UUID,
    db_conn: DbConnection,
    sequence_number: int,
    initial_call: bool,
):
    return await db_conn.fetch_one(
        sa.select(
            [
                orm.campaign_conversation.c.id,
                orm.campaign_conversation.c.twi_sid,
                orm.campaign_conversation.c.initial_call,
                orm.campaign_conversation.c.current_attempt,
                orm.campaign_conversation.c.status,
                orm.campaign_conversation.c.created_by,
                orm.campaign_conversation.c.sequence_number,
                orm.campaign_conversation.c.contact_name,
                orm.campaign_conversation.c.skipped,
                orm.campaign_conversation.c.skip_cooldown,
                orm.campaign_conversation.c.contact_name,
                orm.campaign_conversation.c.contact_number,
                orm.campaign_conversation.c.campaign_id,
            ]
        ).where(
            sa.and_(
                orm.campaign_conversation.c.campaign_id == campaign_id,
                orm.campaign_conversation.c.sequence_number == sequence_number,
                orm.campaign_conversation.c.initial_call == initial_call,
            )
        )
    )


async def get_callable_data(
    contact_number: str,
    campaign_id: UUID,
    initial_call: bool,
    db_conn: DbConnection,
):
    subquery = (
        sa.select(
            [
                orm.campaign_conversation.c.sequence_number,
            ]
        )
        .where(
            sa.and_(
                orm.campaign_conversation.c.contact_number == contact_number,
                orm.campaign_conversation.c.campaign_id == campaign_id,
                orm.campaign_conversation.c.initial_call == initial_call,
            )
        )
        .alias("subquery")
    )

    query = (
        sa.select(
            [
                orm.campaign_conversation.c.id.label("id_"),
                orm.campaign_conversation.c.twi_sid,
                orm.campaign_conversation.c.initial_call,
                orm.campaign_conversation.c.current_attempt,
                orm.campaign_conversation.c.status,
                orm.campaign_conversation.c.created_by,
                orm.campaign_conversation.c.sequence_number,
                orm.campaign_conversation.c.contact_name,
                orm.campaign_conversation.c.skipped,
                orm.campaign_conversation.c.skip_cooldown,
                orm.campaign_conversation.c.contact_name,
                orm.campaign_conversation.c.contact_number,
                orm.campaign_conversation.c.campaign_id,
            ]
        )
        .where(
            sa.and_(
                orm.campaign_conversation.c.sequence_number
                >= subquery.c.sequence_number,
                orm.campaign_conversation.c.campaign_id == campaign_id,
            )
        )
        .order_by(orm.campaign_conversation.c.sequence_number)
    )

    return await db_conn.fetch_all(query=query)


async def get_campaign_conference_by_contact_number(
    contact_number: str, campaign_id: UUID, db_conn: DbConnection
):
    return await db_conn.fetch_one(
        sa.select(
            [
                orm.campaign_conversation.c.id,
                orm.campaign_conversation.c.twi_sid,
                orm.campaign_conversation.c.initial_call,
                orm.campaign_conversation.c.current_attempt,
                orm.campaign_conversation.c.status,
                orm.campaign_conversation.c.created_by,
                orm.campaign_conversation.c.sequence_number,
                orm.campaign_conversation.c.contact_name,
                orm.campaign_conversation.c.skipped,
                orm.campaign_conversation.c.skip_cooldown,
                orm.campaign_conversation.c.contact_name,
                orm.campaign_conversation.c.contact_number,
                orm.campaign_conversation.c.campaign_id,
            ]
        ).where(
            sa.and_(
                orm.campaign_conversation.c.campaign_id == campaign_id,
                orm.campaign_conversation.c.contact_number == contact_number,
            )
        )
    )
