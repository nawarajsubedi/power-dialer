"""
"""
from __future__ import annotations

from pydantic import BaseModel


class ResourceModel(BaseModel):
    """base model for result resource"""

    class Config:
        use_enum_values = True


class DataModel(BaseModel):
    """base model for form data"""

    class Config:
        allow_mutation = False
        arbitrary_types_allowed = True
        extra = "ignore"
