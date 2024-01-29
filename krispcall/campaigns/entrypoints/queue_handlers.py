import json
import typing
from uuid import UUID
from krispcall.campaigns import services
from redis import Redis

from krispcall.common.utils.shortid import ShortId


async def update_next_number_to_dial(
    ctx, campaign_id: UUID, next_to_dial: str
):
    return await services.update_next_number_to_dial(
        campaign_id=campaign_id, next_number=next_to_dial, db_conn=ctx["db"]
    )


async def create_campaign_stats(ctx, campaign_id: UUID, contact_list_id: UUID):
    db_conn = ctx["db"]
    await services.create_campaign_stats(
        campaign_id=campaign_id,
        contact_list_id=contact_list_id,
        db_conn=db_conn,
    )


async def update_campaign_duration(ctx, campaign_id: UUID, add_seconds: int):
    db_conn = ctx["db"]
    await services.update_campaign_duration(
        campaign_id=campaign_id,
        db_conn=db_conn,
        add_seconds=add_seconds,
    )


async def update_dialed_contacts(ctx, campaign_id: UUID):
    db_conn = ctx["db"]
    await services.update_campaign_dialed_contacts(
        campaign_id=campaign_id,
        db_conn=db_conn,
    )


async def update_campaign_calls(ctx, campaign_id: UUID, answered: bool):
    db_conn = ctx["db"]
    await services.update_campaign_calls(
        campaign_id=campaign_id,
        db_conn=db_conn,
        answered=answered,
    )


async def update_voicemail_drops(ctx, campaign_id: UUID):
    db_conn = ctx["db"]
    await services.update_campaign_voicemail_drops(
        campaign_id=campaign_id,
        db_conn=db_conn,
    )


async def end_campaign(ctx, campaign_id: UUID):
    db_conn = ctx["db"]
    settings = ctx["settings"]
    cache = Redis.from_url(settings.redis_settings)
    campaign = cache.get(ShortId.with_uuid(campaign_id)) or {}
    # If we don't find the campaign in cache, it means its paused or
    # ended so we do nothing
    if not campaign:
        return
    camp_obj = json.loads(campaign)

    # Now, we'll check if the campaign is still in dialing_completed
    # state if it is we'll end the campaign
    print("$$" * 30)
    print("Campaign status is :: ->", camp_obj)
    print("$$" * 30)
    if camp_obj.get("status") == "dialing_completed":
        await services.end_campaign(
            campaign_id=campaign_id,
            db_conn=db_conn,
        )
