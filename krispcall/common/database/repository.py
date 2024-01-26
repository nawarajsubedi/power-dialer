"""
"""
from __future__ import annotations

import typing
from uuid import UUID

from pydantic import BaseModel


class Repository(typing.Protocol):
    """
    base repository protocol,
    should not be instantiated

    subclasses should also be protocols
    """

    def add(self, model: BaseModel) -> None:
        raise NotImplementedError()

    def get(self, ref: UUID) -> BaseModel:
        raise NotImplementedError()
