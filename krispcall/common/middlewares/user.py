"""
"""

from __future__ import annotations

import logging
import typing
from uuid import UUID

from krispcall.common.domain.entities import BaseEntity
from krispcall.common.domain.jwt import JWTClaim
from krispcall.common.error_handler.exceptions import InvalidJWTUserClaim

# from krispcall.core.constants.common import NULL_UUID
# from krispcall.core.domain.entities import BaseEntity
# from krispcall.core.domain.jwt import JWTClaim
# from krispcall.core.exceptions import InvalidJWTUserClaim

T = typing.TypeVar("T")
LOGGER = logging.getLogger(__name__)


class PrincipalUser(BaseEntity):
    """principal entity"""

    id_: UUID
    authenticated_: bool
    claim: JWTClaim
    username: typing.Optional[str]

    @property
    def is_authenticated(self) -> bool:
        return self.authenticated_

    @property
    def identity(self) -> UUID:
        return self.id_

    @property
    def display_name(self) -> typing.Optional[str]:
        return self.username

    def get_claim(self, name: str, type_: typing.Type[T]) -> T:
        try:
            value = type_(self.claim.user_claims[name])  # type: ignore
        except (AttributeError, KeyError, ValueError) as e:
            LOGGER.exception(e)
            raise InvalidJWTUserClaim("Invalid Token")
        else:
            return value


def create_authenticated_principal_user(
    claims: typing.Dict[str, typing.Any]
) -> PrincipalUser:
    """principal entity factory"""
    claim = JWTClaim(**claims)
    return PrincipalUser(id_=claim.sub, authenticated_=True, claim=claim)


def create_unauthenticated_principal_user() -> PrincipalUser:
    """unauthenticated principal user"""
    return PrincipalUser(id_=NULL_UUID, authenticated_=False, claim=None)
