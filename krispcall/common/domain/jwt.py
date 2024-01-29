"""
"""
from __future__ import annotations

import typing
from uuid import UUID

from krispcall.common.domain.entities import BaseEntity


class JWTClaim(BaseEntity):
    """jwt claim entity"""

    jti: str
    sub: str
    iss: str
    aud: typing.List[str]
    exp: int
    iat: int
    nbf: int
    version: str
    scope: typing.List[str]
    kind: typing.Literal["auth", "refresh", "access"]
    fresh: bool
    user_claims: typing.Dict[str, typing.Any]


def create_jwt_claim(
    *,
    jwt_id: typing.Union[UUID, str],
    subject: typing.Union[UUID, str],
    issuer: str,
    audience: typing.List[str],
    expire_after: Duration,
    version: typing.Optional[str] = None,
    scope: typing.Optional[typing.List[str]] = None,
    user_claims: typing.Optional[typing.Dict[str, typing.Any]] = None,
    kind: str = "access",
    fresh: bool = False,
) -> JWTClaim:
    """create new jwt claim"""
    issued_at = utc_now()
    return JWTClaim(
        jti=str(jwt_id),
        sub=str(subject),
        iss=issuer,
        aud=audience,
        exp=int((issued_at + expire_after).timestamp()),
        iat=int(issued_at.timestamp()),  # type: ignore
        nbf=int(issued_at.timestamp()),  # type: ignore
        version=version if version is not None else "1.0",
        scope=scope if scope else [],
        kind=kind,
        fresh=fresh,
        user_claims=user_claims if user_claims else {},
    )
