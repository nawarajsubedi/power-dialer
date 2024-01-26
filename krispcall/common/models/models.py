"""
"""
from __future__ import annotations

from pydantic import BaseModel


class BaseEntity(BaseModel):
    class Config:
        allow_mutation = False
        extra = "forbid"
