"""
"""
from __future__ import annotations

import typing

import sqlalchemy as sa
from databases import Database

from krispcall.common.error_handler import error_handlers

SQL_METADATA = sa.MetaData()


def get_metadata(schema: typing.Optional[str] = None) -> sa.MetaData:
    if schema is not None:
        return sa.MetaData(schema=schema)
    return SQL_METADATA


from krispcall.common.database.exceptions import (
    DuplicateEntity,
    EntityContractFailed,
    NonExistingEntity,
)
from krispcall.common.error_handler.exceptions import (
    FailedIdentityException,
    FailedPermissionException,
    HTTPException,
    RequestValidationError
)
from krispcall.common.database.settings import DatabaseSettings


def load_exception_handlers() -> dict[typing.Any, typing.Any]:
    return {
        NonExistingEntity: error_handlers.resource_not_found,
        DuplicateEntity: error_handlers.cannot_process_request,
        EntityContractFailed: error_handlers.cannot_process_request,
        FailedIdentityException: error_handlers.unauthorized_request,
        FailedPermissionException: error_handlers.forbidden_request,
        HTTPException: error_handlers.http_exception,
        RequestValidationError: error_handlers.request_validation_error,
        Exception: error_handlers.system_exception,
    }


def init_database(settings: DatabaseSettings) -> Database:
    # """load/unload postgres engine"""
    # if settings.is_testing:
    #     return Database(
    #         settings.pg_dsn, ssl=settings.pg_use_ssl, force_rollback=True
        # )
    return Database(
        settings.pg_dsn,
        ssl=settings.pg_use_ssl,
        min_size=settings.pg_min_size,
        max_size=settings.pg_max_size,
    )
