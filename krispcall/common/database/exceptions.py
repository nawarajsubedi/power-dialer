"""
"""
from __future__ import annotations


class DomainException(Exception):
    """Base Domain Level Exception"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class DuplicateEntity(DomainException):
    pass


class NonExistingEntity(DomainException):
    pass


class EntityContractFailed(DomainException):
    pass
