import typing
from pydantic.generics import GenericModel
from pydantic import BaseModel

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
    *, message: str, error_status: ErrorKeyTuple, translator=None
) -> ErrorDict:
    if translator:
        message = translator(message)
    return ErrorResponseModel(
        status=error_status[0],
        error=Error(
            message=message,
            code=error_status[0],
            error_key=error_status[1],
        ),
    ).dict()
