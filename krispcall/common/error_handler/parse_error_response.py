import typing
from loguru import logger
from pydantic import ValidationError
from krispcall.common.models.error_response import Error, ErrorResponseModel

from krispcall.common.services.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTPError

ErrorDict = typing.Dict[str, typing.Any]
ErrorKeyTuple = HTTPError

def create_error_response(
    *,
    message: typing.Union[str, typing.Tuple[str, typing.Any], Exception],
    error_status: ErrorKeyTuple,
    translator=None
) -> ErrorDict:
    if translator:
        message_str = ""
        message = translator(message)
    # Checks status code is 500 if yes return generic internal server error message
    # else return message pass by calling method
    if error_status[0] == HTTP_500_INTERNAL_SERVER_ERROR.status_code:
        logger.error(message)
        message = HTTP_500_INTERNAL_SERVER_ERROR.status_message

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
        if hasattr(message, "errors") and callable(message.errors):
            message_errors = message.errors()
            if message_errors and isinstance(message_errors, list):
                return message_errors[0].get("msg", "")
        
        if isinstance(message.args, tuple) and message.args:
            return str(message.args[0])
        
        if isinstance(message.args, str):
            return message.args
    except ValidationError:
        pass  # Ignore validation error

    # If no suitable error message found, return a default message
    return "An unexpected error occurred."
