"""
"""
from __future__ import annotations

from typing import Any, Dict

from pydantic import validator

from krispcall.common.domain.entities import BaseEntity

DataDict = Dict[str, Any]


class BaseEvent(BaseEntity):
    """base event entity"""

    id_: str

    @validator("id_")
    def name_should_follow_dotted_notation(
        cls, val: Any, values: DataDict, **kwargs: DataDict
    ) -> Any:
        _val = val.strip()
        if _val.startswith(".") or _val.endswith("."):
            raise ValueError("should not start or end with dot")
        if "." not in _val:
            raise ValueError("must be namespaced.")
        return _val
