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


def create_error_response(
    *,
    message: typing.Union[str, typing.Tuple[str, typing.Any]],
    error_status: ErrorKeyTuple,
    translator=None
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
            message=message_str,
            code=error_status[0],
            error_key=error_status[1],
        ),
    ).dict()


def extract_error_message(message: typing.Union[str, typing.Any]) -> str:
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
