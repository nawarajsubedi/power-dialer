"""
api format similar to but not exactly json:api
"""
from __future__ import annotations

import logging
import typing

from pydantic import BaseModel, validator
from pydantic.generics import GenericModel

LOGGER = logging.getLogger(__name__)


DataT = typing.TypeVar("DataT")
MetaT = typing.TypeVar("MetaT")
DataDict = typing.Dict[str, typing.Any]
ErrorsList = typing.List[DataDict]


class Error(BaseModel):
    code: int
    message: str
    errors: typing.Optional[ErrorsList]


class MetaLink(BaseModel):
    self: typing.Optional[str]
    prev: typing.Optional[str]
    next: typing.Optional[str]
    first: typing.Optional[str]
    last: typing.Optional[str]


class MetaModel(BaseModel):
    access: typing.Optional[DataDict]
    links: typing.Optional[MetaLink]
    count: typing.Optional[int]
    selected: typing.Optional[int]


class RequestDataModel(GenericModel, typing.Generic[DataT]):
    """post request generic data model"""

    data: DataT


class ResponseModel(GenericModel, typing.Generic[DataT]):
    """generic object response model"""

    status: int
    meta: typing.Optional[MetaModel]
    data: typing.Optional[DataT]
    error: typing.Optional[Error]

    @validator("error", always=True)
    def check_consistency(cls, val, values):  # type: ignore
        """validate if data and error key are not present"""
        if val is not None and (
            values["data"] is not None or values["meta"] is not None
        ):
            raise ValueError("Cannot accept both data/meta and error")
        if val is None and values.get("data") is None:
            raise ValueError("Either data or error should be given")
        return val


def create_error_response(
    *, message: str, status: int, errors: typing.Optional[ErrorsList] = None
) -> ResponseModel[Error]:
    """create error dict response"""
    return ResponseModel[Error](
        error=Error(message=message, code=status, errors=errors), status=status
    ) # type: ignore
