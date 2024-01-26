"""
"""
from __future__ import annotations

from enum import Enum, unique


@unique
class RecordStatus(str, Enum):
    active = "Active"
    inactive = "Inactive"
    archived = "Archived"
    removed = "Removed"


@unique
class ResourceStatus(str, Enum):
    active = "Active"
    inactive = "Inactive"
    archived = "Archived"
    deleted = "Deleted"
    expired = "Expired"


@unique
class AuthStatus(str, Enum):
    active = "Active"
    inactive = "Inactive"
    archived = "Archived"
    removed = "Removed"
    Unverified = "Unverified"


@unique
class Gender(str, Enum):
    male = "Male"
    female = "Female"
    unspecified = "Unspecified"


@unique
class ActionStatus(str, Enum):
    pending = "Pending"
    processing = "Processing"
    completed = "Completed"


@unique
class Priority(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"
