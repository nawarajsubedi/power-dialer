"""
"""
from __future__ import annotations

from databases import Database
from krispcall.common.configs.app_settings import Settings
from krispcall.providers.queue_service.job_queue import JobQueue
from krispcall.twilio.twilio_client import TwilioClient

def init_queue(settings: Settings) -> JobQueue:
    """initialize Job Queue"""
    return JobQueue(settings.redis_settings, skip_rpc=settings.is_testing)


def init_twillo(settings: Settings) -> TwilioClient:
    """initialize twillo client"""
    return TwilioClient(settings)

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
