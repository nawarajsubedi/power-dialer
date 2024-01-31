""" Schema for common views"""
from __future__ import annotations
import typing
from typing import Any, Union, List, Dict
from datetime import datetime
from pydantic import ValidationError, validator
from pydantic import BaseModel, Field, root_validator
from pydantic.generics import GenericModel
from krispcall.common.models.resource_models import ResourceModel
from krispcall.common.services.pagination.query import QueryModel

from krispcall.common.services.status import (
    HTTP_200_OK,
)

DataT = typing.TypeVar("DataT")
MetaT = typing.TypeVar("MetaT")
DataDict = typing.Dict[str, typing.Any]
ErrorsList = typing.List[DataDict]


class RequestDataModel(GenericModel, typing.Generic[DataT]):
    """post request generic data model"""

    data: DataT


ErrorDict = typing.Dict[str, typing.Any]
ErrorKeyTuple = typing.Tuple[int, str]
FilterType = typing.List[typing.Dict[str, typing.Any]]

DataT = typing.TypeVar("DataT")
MetaT = typing.TypeVar("MetaT")
DataDict = typing.Dict[str, typing.Any]
ErrorsList = typing.List[DataDict]

class Error(BaseModel):
    code: int
    message: str
    error_key: str

class MetaLink(BaseModel):
    self: typing.Optional[str]
    prev: typing.Optional[str]
    next: typing.Optional[str]
    first: typing.Optional[str]
    last: typing.Optional[str]


class MultipleError(BaseModel):
    code: int
    message: str
    error_key: str


class PageInfo(BaseModel):
    start_cursor: datetime
    end_cursor: datetime
    has_next_page: bool
    has_previous_page: bool
    total_count: int


class MetaModel(BaseModel):
    access: typing.Optional[DataDict]
    links: typing.Optional[MetaLink]
    count: typing.Optional[int]
    selected: typing.Optional[int]


class ResponseModel(GenericModel, typing.Generic[DataT]):
    """generic object response model"""

    status: int
    meta: typing.Optional[MetaModel]
    data: typing.Optional[DataT]
    error: typing.Optional[Error]

    @validator("error", always=True)
    def check_consistency(cls, val, values):
        """validate if data and error key are not present"""
        if val is not None and (
            values["data"] is not None or values["meta"] is not None
        ):
            raise ValueError("Cannot accept both data/meta and error")
        if val is None and values.get("data") is None:
            raise ValueError("Either data or error should be given")
        return val


class SuccessResponseModel(GenericModel):
    data: Union[List[typing.Any], Dict[str, typing.Any]] = None
    error: Error = None
    status: int


class MultipleErrorResponseModel(GenericModel):
    status: int
    error: MultipleError


class Edges(ResourceModel):
    cursor: str
    node: typing.Any


class PaginatedResource(ResourceModel):
    page_info: PageInfo
    edges: typing.List[Edges]


class KeySet(BaseModel):
    first: str
    second: str


class SearchType(BaseModel):
    # value: typing.Union[int, str]
    value: typing.Any
    columns: typing.List[str]


"""
search / filter example
{
    search: {value: "sadfsdaf", columns: ["name", "number"]},
    filter: {
        "name.eq": "value",
    },
    sort: "name",
    order: "desc"
}
"""


class PaginationParams(QueryModel):
    first: int = None  # type: ignore
    after: datetime = None  # type: ignore
    after_with: typing.Optional[datetime]
    last: int = None  # type: ignore
    before: datetime = None  # type: ignore
    before_with: typing.Optional[datetime]
    q: typing.Optional[str]
    s: typing.Optional[str]
    sort: typing.Optional[str]
    order: typing.Literal["asc", "desc"] = Field("asc")

    search: typing.Optional[SearchType]
    filter: typing.Optional[FilterType]
    filters: typing.Optional[typing.List[FilterType]]

    @root_validator
    def check_valid_pagination(cls, values):
        first, after, after_with = (
            values.get("first"),
            values.get("after"),
            values.get("after_with"),
        )
        last, before, before_with = (
            values.get("last"),
            values.get("before"),
            values.get("before_with"),
        )
        forward = first or after or after_with
        backward = last or before or before_with

        if forward and backward:
            raise ValueError("Paging can't be forward and backward")
        elif forward or backward:
            return values
        else:
            raise ValueError("Invalid paging params")


def extract_error_message(message: Union[str, Any]) -> str:
    if isinstance(message, str):
        return message

    try:
        message_errors = message.errors()
        if (
            message_errors
            and isinstance(message_errors, list)
            and message_errors[0].get("msg") is not None
        ):
            return message_errors[0]["msg"]
    except ValidationError:
        pass  # Ignore validation error

    return "An unexpected error occurred."


def create_multiple_error_response(
    *, message: dict, error_status: ErrorKeyTuple, translator=None
) -> ErrorDict:
    if translator:
        message = translator(message)
    return MultipleErrorResponseModel(
        status=error_status[0],
        error=MultipleError(
            message=message,  # type: ignore
            code=error_status[0],
            error_key=error_status[1],
        ),
    ).dict()


def create_success_response(
    data=None,
    status=HTTP_200_OK[0],
    error=None,
):
    return SuccessResponseModel(data=data, error=error, status=status)


class OffsetPageInfo(BaseModel):
    offset: int
    limit: int
    total: int


class TestEdges(ResourceModel):
    node: typing.Any


class OffsetPaginationParams(QueryModel):
    offset: int = None  # type: ignore
    limit: int = None  # type: ignore
    sort: typing.Optional[str]
    order: typing.Literal["asc", "desc"] = Field("asc")
    search: typing.Optional[SearchType]
    filter: typing.Optional[FilterType]
    filters: typing.Optional[typing.List[FilterType]]


class OffsetPaginatedResource(ResourceModel):
    page_info: OffsetPageInfo
    edges: typing.List[TestEdges]
