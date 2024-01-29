"""
"""
# pylint: disable=too-few-public-methods
from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Dict, Generic, Optional, Type, TypeVar
from toolz import curry

from pydantic import BaseModel, validator
from pydantic.generics import GenericModel

from krispcall.common.responses.response_model import ResponseModel

# from krispcall.common.services.abstracts import ResponseModel

# from krispcall.common.services.abstracts import ResponseModel

# from krispcall.common.services.query import (  # noqa: F401
#     KeysetQueryParam as KeysetQueryParam,
# )
# from krispcall.common.services.query import (
#     QueryModel as QueryModel,
# )  # noqa: F401
# from krispcall.common.services.query import (
#     QueryParamModel as QueryParamModel,
# )  # noqa: F401

# from krispcall.common.services.model import ResponseModel

__all__ = ["DataModel", "ResourceModel", "with_response"]


ParamT = TypeVar("ParamT")
DataDict = Dict[str, Any]


class DataModel(BaseModel):
    """base model for form data"""

    class Config:
        allow_mutation = False
        arbitrary_types_allowed = True
        extra = "ignore"


class ResourceModel(BaseModel):
    """base model for result resource"""

    class Config:
        use_enum_values = True


# class ConditionalQueryParam(GenericModel, Generic[ParamT]):
#     """conditional query param"""

#     gt: Optional[ParamT]
#     lt: Optional[ParamT]
#     ge: Optional[ParamT]
#     le: Optional[ParamT]
#     eq: Optional[ParamT]

#     @validator("gt")
#     def should_not_come_with_ge(
#         cls, val: Any, values: DataDict, **kwargs: DataDict
#     ) -> Any:
#         _other_exists = "ge" in values and values["ge"] and not None
#         if val is not None and _other_exists:
#             raise ValueError("both gt and ge cannot be used at same time")
#         return val

#     @validator("ge")
#     def should_not_come_with_gt(
#         cls, val: Any, values: DataDict, **kwargs: DataDict
#     ) -> Any:
#         _other_exists = "gt" in values and values["gt"] and not None
#         if val is not None and _other_exists:
#             raise ValueError("both gt and ge cannot be used at same time")
#         return val

#     @validator("lt")
#     def should_not_come_with_lte(
#         cls, val: Any, values: DataDict, **kwargs: DataDict
#     ) -> Any:
#         _other_exists = "le" in values and values["le"] and not None
#         if val is not None and _other_exists:
#             raise ValueError("both lt and le cannot be used at same time")
#         return val

#     @validator("le")
#     def should_not_come_with_lt(
#         cls, val: Any, values: DataDict, **kwargs: DataDict
#     ) -> Any:
#         _other_exists = "lt" in values and values["lt"] and not None
#         if val is not None and _other_exists:
#             raise ValueError("both lt and le cannot be used at same time")
#         return val

#     @validator("eq")
#     def should_only_be_eq(
#         cls, val: Any, values: DataDict, **kwargs: DataDict
#     ) -> Any:
#         _other_exists = any(
#             [
#                 (v is not None)
#                 for k, v in values.items()
#                 if k in ("gt", "ge", "lt", "le")
#             ]
#         )
#         if val is not None and _other_exists:
#             raise ValueError("eq cannot be used with other conditionals")
#         return val


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
            status: int = 200,
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
