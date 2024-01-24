from functools import wraps
from krispcall.common.shortid import ShortId
from krispcall.common import http_status_code

from typing import Any, Callable
from krispcall.auth.enums import AuthFeatureEnum
from krispcall.common.responses import create_error_response
from krispcall.common.translator import get_translator
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
            error_status=http_status_code.HTTP_403_FORBIDDEN,
        )

    return wrapper
