import typing
from loguru import logger
from pydantic.generics import GenericModel
from pydantic import BaseModel, ValidationError

from krispcall.common.services.status import HTTP_500_INTERNAL_SERVER_ERROR

ErrorDict = typing.Dict[str, typing.Any]
ErrorKeyTuple = typing.Tuple[int, str]


class Error(BaseModel):
    code: int
    message: str
    error_key: str


class ErrorResponseModel(GenericModel):
    status: int
    error: Error