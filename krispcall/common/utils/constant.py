"""
core constants
"""
from __future__ import annotations

from uuid import UUID

NULL_UUID: UUID = UUID("00000000-0000-0000-0000-000000000000")


# emails
EMAIL_CHARSET: str = "utf-8"
COMMASPACE: str = ", "

# filesizes
ONE_MB_IN_BYTES: int = 10_00_000

# logging
LOG_FILE_MAX_SIZE: int = ONE_MB_IN_BYTES * 100
LOG_BACKUP_FILES_COUNT: int = 3

# shortuuid
SHORTUUID_LENGTH: int = 22

MIMETYPE_JSON: str = "application/json"
