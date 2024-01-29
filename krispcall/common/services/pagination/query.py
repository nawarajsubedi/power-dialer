"""
"""
from __future__ import annotations

import typing
from datetime import datetime
from urllib.parse import quote
from uuid import UUID

from pydantic import BaseModel, Field

from krispcall.common.utils.shortid import ShortId


class QueryModel(BaseModel):
    """base model for query params"""

    class Config:
        allow_mutation = False
        extra = "ignore"

    class Meta:
        fields = None


class KeysetQueryParam(BaseModel):
    first: str
    second: str


class QueryParamModel(QueryModel):
    q: typing.Optional[str]
    sort: typing.Optional[str]
    columns: typing.Optional[str]
    order: typing.Literal["asc", "desc"] = Field("asc")
    keyset: typing.ClassVar[KeysetQueryParam] = KeysetQueryParam(
        first="", second=""
    )
    next: typing.Optional[str]
    prev: typing.Optional[str]
    num: int = Field(10, ge=5, le=25)


def transform_keyset(
    value: typing.Union[UUID, datetime, str, typing.Any]
) -> typing.Union[ShortId, str, typing.Any]:
    if isinstance(value, UUID):
        return ShortId.with_uuid(value)
    elif isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, str):
        return quote(value)
    return value
