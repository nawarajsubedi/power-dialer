import asyncio
from functools import wraps
from krispcall.auth.constant import TOKEN_EXPIRED
from krispcall.common.utils.shortid import ShortId
from krispcall.common.services import status as HTTP_STATUS_CODE

from starlette.authentication import has_required_scope
from typing import Any, Callable, List
from krispcall.auth.enums import AuthFeatureEnum
from krispcall.common.responses.responses import create_error_response
from krispcall.common.error_handler.translator import get_translator
from krispcall.providers.foundation_provider import get_workspace_feature


# from krispcall.bulksms.service_layer import views
# from krispcall.common.service_layer import status
# from krispcall.common.service_layer.abstracts import create_error_response
# from krispcall.common.service_layer.static_helpers import get_translator


def requires_power_dialer_enabled(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        _, info = args
        request = info.context["request"]
        workspace_id = request.user.get_claim("workspace_id", ShortId)

        power_dialer_feature = await get_workspace_feature(
            workspace_id=workspace_id,
            feature_name=AuthFeatureEnum.POWER_DIALER.value,
        )
        if power_dialer_feature and power_dialer_feature.get("is_enabled", False):
            return await func(*args, **kwargs)

        return create_error_response(
            translator=get_translator(request),
            message="Sales dailer feature disabled!",
            error_status=HTTP_STATUS_CODE.HTTP_403_FORBIDDEN,
        )

    return wrapper


def required_scope(scope: List[str]) -> Callable:
    """checks permission and return forbidden response if required"""

    def actual_wrapper(func: Callable):
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                _, info = args
                if has_required_scope(info.context["request"], TOKEN_EXPIRED):
                    # raise AuthenticationError(
                    #     "Token Expired"
                    # )
                    return create_error_response(
                        message="Token Expired",
                        error_status=HTTP_STATUS_CODE.HTTP_401_TOKEN_EXPIRED,
                    )
                if not has_required_scope(info.context["request"], scope):
                    return create_error_response(
                        message="Invalid auth credentials",
                        error_status=HTTP_STATUS_CODE.HTTP_401_UNAUTHORIZED,
                    )
                return await func(*args, **kwargs)

            return async_wrapper

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            _, info = args
            if has_required_scope(info.context["request"], TOKEN_EXPIRED):
                return create_error_response(
                    message="Token Expired",
                    error_status=HTTP_STATUS_CODE.HTTP_401_TOKEN_EXPIRED,
                )
            if not has_required_scope(info.context["request"], scope):
                return create_error_response(
                    message="Invalid auth credentials",
                    error_status=HTTP_STATUS_CODE.HTTP_401_UNAUTHORIZED,
                )
            return func(*args, **kwargs)

    return actual_wrapper

