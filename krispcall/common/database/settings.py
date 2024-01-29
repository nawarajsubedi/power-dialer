"""
"""
from __future__ import annotations

from typing import Protocol

from pydantic import PostgresDsn

from krispcall.common.app_settings.app_settings import CoreSettings

# class DatabaseSettings(Protocol):
#     """database settings protocol"""

#     @property
#     def pg_dsn(self) -> PostgresDsn:
#         raise NotImplementedError()

#     @property
#     def pg_use_ssl(self) -> bool:
#         raise NotImplementedError()

#     @property
#     def pg_min_size(self) -> int:
#         raise NotImplementedError()

#     @property
#     def pg_max_size(self) -> int:
#         raise NotImplementedError()


class DatabaseSettings(CoreSettings):
    """database related settings"""

    database_log_file: str = "database.log"

    # postgres settings
    pg_dsn: PostgresDsn
    pg_schema: str = "public"
    pg_min_size: int = 5
    pg_max_size: int = 10
    pg_use_ssl: bool = True
