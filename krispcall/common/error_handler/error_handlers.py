"""
"""
from __future__ import annotations

from http import HTTPStatus

import typing
# from krispcall.common.service_layer.abstracts import create_error_response

from starlette.responses import JSONResponse as StarletteJSONResponse
from starlette.responses import Response as Response  # noqa: F401

from loguru import logger
import sys
import traceback
import json
from krispcall.common.responses.response_model import ResponseModel
from krispcall.common.responses.responses import create_error_response

from krispcall.common.utils.constant import MIMETYPE_JSON


class JSONResponse(StarletteJSONResponse):
    media_type = MIMETYPE_JSON

    def render(
        self,
        content: typing.Union[ResponseModel, dict[str, typing.Any]],
    ) -> bytes:
        if isinstance(content, ResponseModel):
            self.status_code = content.status
            content = content.dict(exclude_none=False)
        return super().render(content)


async def http_exception(request, exc):
    return JSONResponse(
        create_error_response(message=exc.detail, status=exc.status_code) # type: ignore
    )


async def request_validation_error(request, exc):
    return JSONResponse(
        create_error_response(
            message="Request Validation Failed",
            errors=exc.errors(), # type: ignore
            status=HTTPStatus.UNPROCESSABLE_ENTITY, # type: ignore
        )
    )


async def system_exception(request, exc):
    return JSONResponse(
        create_error_response(
            message="Unexpected Error Occurred",
            error_status=HTTPStatus.INTERNAL_SERVER_ERROR, # type: ignore
        )
    )


async def resource_not_found(request, exc):
    return JSONResponse(
        create_error_response(message=exc.message, status=HTTPStatus.NOT_FOUND) # type: ignore
    )


async def cannot_process_request(request, exc):
    return JSONResponse(
        create_error_response(
            message=exc.message, status=HTTPStatus.BAD_REQUEST # type: ignore
        ) # type: ignore
    )


async def unauthorized_request(request, exc):
    return JSONResponse(
        create_error_response(
            message=exc.message, status=HTTPStatus.UNAUTHORIZED # type: ignore
        )
    )


async def forbidden_request(request, exc):
    return JSONResponse(
        create_error_response(message=exc.message, status=HTTPStatus.FORBIDDEN) # type: ignore
    )


def on_authentication_error(request, exc):
    return JSONResponse(
        create_error_response(message=str(exc), status=HTTPStatus.UNAUTHORIZED) # type: ignore
    )


def error_serialize(record):
    subset = {
        # "date": record["time"].timestamp(),
        "asctime": int(record["time"].timestamp()),
        # "date": int(record["time"].timestamp()),
        # "message": record["message"],
        # "loglevel": record["level"].name,
        "levelname": record["level"].name,
        "name": record["name"],
        "message": f"{record['time'].strftime('%Y-%m-%d %H:%M:%S')} | ERROR | {record['extra'].get('line')} - {record['message']}",
        "exc_info": record["extra"].get("exception"),
    }
    return json.dumps(subset)


def error_formatter(record):
    # Note this function returns the string to be formatted, not the actual message to be logged
    record["extra"]["serialized"] = error_serialize(record)
    return "{extra[serialized]}\n"


def error_logger(module, event, message):
    message = f"module:{module}, event:{event}, message:Token Signature Expired {message}"
    logger.remove()
    logger.add(sys.stderr, format=error_formatter)
    e_type, e_object, e_traceback = sys.exc_info()
    if e_traceback:
        e_filename = e_traceback.tb_frame.f_code.co_filename
        e_line_number = e_traceback.tb_lineno
        logger.error(
            message,
            exception=traceback.format_exc(),
            line=f"{e_filename}:{e_line_number}",
        )
    else:
        logger.error(message, exception=traceback.format_exc())
