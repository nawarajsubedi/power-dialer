
from graphql import GraphQLError
from ariadne import format_error
from loguru import logger

from krispcall.common.error_handler.parse_error_response import create_error_response
from krispcall.common.services.status import HTTP_400_INVALID_INPUT


def default_graphql_badrequest_handler(
    error: GraphQLError, debug: bool = False
) -> dict:
    """
    generic server errors in non debug mode
    """
    if debug:
        return format_error(error, debug)
    logger.warning(
        f"Sending {HTTP_400_INVALID_INPUT} due to bad graphql schema"
    )

    return create_error_response(
        message="Bad Request",
        error_status=HTTP_400_INVALID_INPUT,
    )
