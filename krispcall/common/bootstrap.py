"""
"""
from __future__ import annotations

import typing
# import rollbar
# from rollbar.logger import RollbarHandler
from databases import Database
from datetime import timedelta, datetime
from arq import create_pool
from arq.connections import RedisSettings, ArqRedis
from krispcall.common.app_settings.app_settings import Settings
from krispcall.common.database.connection import DbConnection
from krispcall.providers.queue_service.job_queue import JobQueue
from krispcall.twilio.twilio_client import TwilioClient

def init_queue(settings: Settings) -> JobQueue:
    """initialize Job Queue"""
    return JobQueue(settings.redis_settings, skip_rpc=settings.is_testing)


def init_twillo(settings: Settings) -> TwilioClient:
    """initialize twillo client"""
    return TwilioClient(settings)


# def init_slack(settings: Settings) -> WebClient:
#     """initialize slack client"""
#     return WebClient(
#         token=settings.slack_token,
#     )


# def init_rollbar(settings: Settings):
#     """Initliases the rollbar middleware"""
#     rollbar.init(
#         settings.rollbar_api_secret,
#         envrionment=settings.app_env,
#     )
#     rollbar_handler = RollbarHandler()
#     return rollbar_handler


# def init_broadcaster(settings: Settings) -> KrispBroadcast:
#     """initialize kafka client"""
#     return KrispBroadcast(settings.broadcaster_dsn)


# def init_payment_service(settings: Settings) -> StripeClient:
#     """initialize payment client"""
#     return StripeClient(settings)


# def init_chargebee(settings: Settings) -> ChargebeeClient:
#     """initialize chargebee client"""
#     return ChargebeeClient(settings)


# def init_partnerstack(settings: Settings) -> PartnerStackClient:
#     """initialize partnerstack client"""
#     return PartnerStackClient(settings)


# def init_casbin(settings: Settings, db_conn: DbConnection) -> AppEnforcer:
#     """initialize casbin permission"""
#     return AppEnforcer(settings, db_conn)


# def init_fcm_service(settings: Settings) -> FCMNotification:
#     """initialize fcm service"""
#     return FCMNotification(api_key=settings.fcm_api_key)


def init_worker_database(settings: Settings) -> Database:
    """load/unload postgres engine"""
    if settings.is_testing:
        return Database(
            settings.pg_dsn, ssl=settings.pg_use_ssl, force_rollback=True
        )
    return Database(
        settings.pg_dsn,
        ssl=settings.pg_use_ssl,
        min_size=settings.worker_pg_min_size,
        max_size=settings.worker_pg_max_size,
    )
