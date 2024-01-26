""" Schema for common views"""
from __future__ import annotations
from ast import Tuple
import typing
from typing import Any, Union, List, Dict
from uuid import UUID
from datetime import datetime
from loguru import logger
from pydantic import ValidationError, validator
from pydantic import BaseModel, Field, root_validator
from pydantic.generics import GenericModel

from krispcall.common.services.abstracts import MetaLink
from krispcall.common.services.status import (
    HTTP_200_OK,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from krispcall.common.services.abstracts import (
    DataModel,
    ResourceModel,
    QueryModel,
    with_response,
)


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
    links: typing.Optional[MetaLink] # type: ignore
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


class ErrorResponseModel(GenericModel):
    status: int
    error: Error


class SuccessResponseModel(GenericModel):
    data: Union[List[typing.Any], Dict[str, typing.Any]] = None # type: ignore
    error: Error = None # type: ignore
    status: int


class MultipleErrorResponseModel(GenericModel):
    status: int
    error: MultipleError


class Edges(ResourceModel): # type: ignore
    cursor: str
    node: typing.Any


class PaginatedResource(ResourceModel): # type: ignore
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


class PaginationParams(QueryModel): # type: ignore
    first: int = None # type: ignore
    after: datetime = None # type: ignore
    after_with: typing.Optional[datetime]
    last: int = None # type: ignore
    before: datetime = None # type: ignore
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


class Country(DataModel): # type: ignore
    uid: UUID
    name: str
    short_name: str
    alpha_two_code: str
    dialing_code: str
    flag_url: str
    timezone: str


class AreaCode(DataModel): # type: ignore
    country: str
    alphaTwoCode: str
    dialCode: str
    code: int
    stateCenter: str
    dialingCode: str
    flagUrl: str


class TimeZone(DataModel): # type: ignore
    value: str
    abbr: str
    offset: float
    isdst: str
    text: str
    utc: typing.List[str]


class NumberResource(ResourceModel): # type: ignore
    type: str
    dialing_number: str
    capabilities: typing.Dict[str, bool]
    address_requirements: str
    region: str
    locality: str
    country_iso: str


@with_response(PaginatedResource) # type: ignore
def create_paginated_response(response_model, *, resource: PaginatedResource):
    return response_model(data=resource, meta=None, status=200)


def create_error_response(
    *, message: Union[str, Tuple[str, any]], error_status: ErrorKeyTuple, translator=None # type: ignore
) -> ErrorDict:
    if translator:
        message_str = ""
        message = translator(message)
    # Checks status code is 500 if yes return generic internal server error message
    # else return message pass by calling method
    if error_status[0] == HTTP_500_INTERNAL_SERVER_ERROR[0]:
        logger.error(message)
        message = HTTP_500_INTERNAL_SERVER_ERROR[2]
    
    if isinstance(message, str):
        message_str = message
    elif isinstance(message, object):
        message_str = extract_error_message(message)

    return ErrorResponseModel(
        status=error_status[0],
        error=Error(
            message=message_str, # type: ignore
            code=error_status[0],
            error_key=error_status[1],
        ),
    ).dict()

def extract_error_message(message: Union[str, Any]) -> str:
    if isinstance(message, str):
        return message
    
    try:
        message_errors = message.errors()
        if message_errors and isinstance(message_errors, list) and message_errors[0].get('msg') is not None:
            return message_errors[0]['msg']
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
            message=message, # type: ignore
            code=error_status[0],
            error_key=error_status[1],
        ),
    ).dict()


def construct_success_response(
    data=None,
    status=HTTP_200_OK[0],
    error=None,
):
    return SuccessResponseModel(data=data, error=error, status=status) # type: ignore


def construct_countries(country_list) -> typing.List[Country]:
    return [
        Country.construct(
            uid=country["uid"],
            name=country["name"],
            short_name=country["short_name"],
            alpha_two_code=country["alpha2_code"],
            dialing_code=country["dialing_code"],
            flag_url=country["flag_url"],
            timezone=country["timezone"],
        )
        for country in country_list
    ]


def construct_area_codes(area_code_list) -> typing.List[AreaCode]:
    return [
        AreaCode.construct(
            dial_code=area_code["dialCode"],
            alpha_two_code=area_code["alphaTwoCode"],
            country=area_code["country"],
            state=area_code["state"],
            code=area_code["code"],
            state_center=area_code["stateCenter"],
            dialing_code=area_code["dialingCode"],
            flag_url=area_code["flagUrl"],
        )
        for area_code in area_code_list
    ]


def construct_timezones(timezones) -> typing.List[TimeZone]:
    return [
        TimeZone.construct(
            value=timezone["value"],
            abbr=timezone["abbr"],
            offset=timezone["offset"],
            isdst=timezone["isdst"],
            text=timezone["text"],
            utc=timezone["utc"],
        )
        for timezone in timezones
    ]




class OffsetPageInfo(BaseModel):
    offset: int
    limit: int
    total: int


class TestEdges(ResourceModel): # type: ignore
    node: typing.Any


class OffsetPaginationParams(QueryModel): # type: ignore
    offset: int = None # type: ignore
    limit: int = None # type: ignore
    sort: typing.Optional[str]
    order: typing.Literal["asc", "desc"] = Field("asc")
    search: typing.Optional[SearchType]
    filter: typing.Optional[FilterType]
    filters: typing.Optional[typing.List[FilterType]]


class OffsetPaginatedResource(ResourceModel): # type: ignore
    page_info: OffsetPageInfo
    edges: typing.List[TestEdges]


@with_response(OffsetPaginatedResource) # type: ignore
def create_offsetpaginated_response(
    response_model, *, resource: OffsetPaginatedResource
):
    return response_model(data=resource, meta=None, status=200)
