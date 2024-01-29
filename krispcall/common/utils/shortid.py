"""
"""
from __future__ import annotations

import typing
from uuid import UUID

import shortuuid


SHORTUUID_LENGTH: int = 22


class ShortId(str):
    """ShortUUID based Id"""

    @classmethod
    def __get_validators__(cls):  # type: ignore
        yield cls.validate

    @classmethod
    def validate(cls, v: typing.Any) -> ShortId:
        """validate shortuuid string"""
        if isinstance(v, UUID):
            return cls(shortuuid.encode(v))
        if not isinstance(v, str):
            raise TypeError("string required")
        if len(v) != SHORTUUID_LENGTH:
            raise ValueError("Invalid id length")
        # now try to decode with shortuuid
        shortuuid.decode(v)
        return cls(v)

    def __init__(self, value: str):
        self._uuid: UUID = shortuuid.decode(value)

    @classmethod
    def with_uuid(cls, value: UUID) -> ShortId:
        return cls(shortuuid.encode(value))

    def uuid(self) -> UUID:
        return self._uuid
