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
from krispcall.twilio.twilio_client import TwilioClient

class JobQueue:
    def __init__(
        self,
        redis_settings,
        skip_rpc: bool = False,
        default_queue_name: str = "arq:general_queue",
        rpc_queue_name: str = "arq:rpc_queue",
        sales_queue_name: str = "arq:sales_queue",
    ):
        self._redis: ArqRedis
        self._settings = redis_settings
        self._skip_rpc = skip_rpc
        self._default_queue_name = default_queue_name
        self._rpc_queue_name = rpc_queue_name
        self._sales_queue_name = sales_queue_name

    async def connect(self):
        self._redis = await create_pool(
            RedisSettings.from_dsn(self._settings),
            default_queue_name=self._default_queue_name,
        )

    async def enqueue_job(
        self,
        func: str,
        data: typing.Tuple[typing.Any, ...],
        *,
        job_id: typing.Optional[str] = None,
        defer_by_seconds: typing.Optional[float] = None,
        expires_in_seconds: typing.Optional[float] = None,
        defer_until: typing.Optional[datetime] = None,
        queue_name: typing.Optional[str] = None,
    ):
        return await self._redis.enqueue_job(  # type: ignore
            func,
            *data,
            _job_id=job_id,
            _queue_name=queue_name,
            _defer_by=None
            if defer_by_seconds is None
            else timedelta(seconds=defer_by_seconds),
            _expires=None
            if expires_in_seconds is None
            else timedelta(seconds=expires_in_seconds),
            _defer_until=defer_until,
        )

    async def run_task(
        self,
        func: str,
        *args: typing.Any,
        _job_id: typing.Optional[str] = None,
        _queue_name: typing.Optional[str] = None,
    ):
        """enqueue job in default queue"""
        await self._redis.enqueue_job(
            func, *args, _job_id=_job_id, _queue_name=_queue_name
        )

    async def call(
        self,
        func: str,
        *args: typing.Any,
        _job_id: typing.Optional[str] = None,
    ):
        # if self._skip_rpc:
        #     return None
        # """enqueue job and wait for result"""
        # job = await self._redis.enqueue_job(
        #     func, *args, _job_id=_job_id, _queue_name=self._rpc_queue_name
        # )
        # return await job.result()  # type: ignore
        """enqueue job and do not wait for result"""
        await self._redis.enqueue_job(
            func, *args, _job_id=_job_id, _queue_name=self._rpc_queue_name
        )

    async def sales_call(
        self,
        func: str,
        *args: typing.Any,
        defer_by_seconds: typing.Optional[float] = None,
        defer_until: typing.Optional[datetime] = None,
        _job_id: typing.Optional[str] = None,
    ):
        # if self._skip_rpc:
        #     return None
        # """enqueue job and wait for result"""
        # job = await self._redis.enqueue_job(
        #     func, *args, _job_id=_job_id, _queue_name=self._rpc_queue_name
        # )
        # return await job.result()  # type: ignore
        """enqueue job and do not wait for result"""
        await self._redis.enqueue_job(
            func,
            *args,
            _job_id=_job_id,
            _queue_name=self._sales_queue_name,
            _defer_by=None
            if defer_by_seconds is None
            else timedelta(seconds=defer_by_seconds),
            _defer_until=defer_until,
        )


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
