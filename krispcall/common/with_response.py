"""
"""
# pylint: disable=too-few-public-methods
from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Dict, Optional, Type, TypeVar
from toolz import curry

from krispcall.common.models.resource_models import ResourceModel, DataModel

from krispcall.common.models.response_model import ResponseModel
from krispcall.common.services.status import HTTP_200_OK

__all__ = ["DataModel", "ResourceModel", "with_response"]



ParamT = TypeVar("ParamT")
DataDict = Dict[str, Any]

RMT = Type[ResourceModel]
RR = Callable[[DataDict, Optional[DataDict], int], ResponseModel[RMT]]
RF = Callable[..., RR]


def with_response(klass: RMT) -> Callable[[RF], RF]:
    """convert resource to response"""

    def response_factory(**kwargs: DataDict) -> RR:
        if "data" not in kwargs and "meta" not in kwargs:
            raise TypeError("Invalid Arguments")
        concrete_model = ResponseModel[klass]  # type: ignore

        def _inner(
            *,
            data: DataDict,
            meta: Optional[DataDict] = None,
            status: int = HTTP_200_OK.status_code,
        ) -> ResponseModel[RMT]:
            nonlocal concrete_model
            model = concrete_model(data=data, meta=meta, status=status) # type: ignore
            return model # type: ignore

        return curry(_inner)(**kwargs) # type: ignore

    def wrapper(func: RF) -> RF:
        @wraps(func)
        def inner(**kwargs: DataDict) -> RR:
            nonlocal response_factory
            return func(response_factory, **kwargs)

        return inner

    return wrapper
