

"""
"""
from __future__ import annotations

import logging
import typing

from jose import jwt 

from krispcall.common.jwt import JWTClaim

LOGGER = logging.getLogger(__name__)


class CPaaSAuthenticationException(Exception):
    pass


class TwilioException(Exception):
    pass
class CoreException(Exception):
    """Base Exception"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class FailedPermissionException(CoreException):
    """failed permission check"""

    message = "Permission Denied."


class FailedIdentityException(CoreException):
    """identity of applicant is not known"""

    message = "Identity Verification Failed."


class InvalidJWTUserClaim(FailedIdentityException):
    """Invalid User Claim"""

    message = "Invalid JWT User Claim"


class TokenException(Exception):
    pass


class TokenSignatureExpiredException(FailedIdentityException):
    """Token Signature Expired"""

    message = "Token Signature Expired"


class InvalidTokenException(FailedIdentityException):
    """Invalid Token"""

    message = "Invalid Token"


class InvalidTicketException(FailedIdentityException):
    """Invalid web ticket"""

    message = "Invalid Ticket"


# def decode_token(
#     token: str, secret: str, algorithms: typing.List[str], audience: str
# ) -> typing.Optional[typing.Dict]:
#     """decode jwt token with secret"""
#     payload = None
#     try:
#         payload = jwt.decode(
#             token=token, key=secret, algorithms=algorithms, audience=audience
#         )
#     except jwt.ExpiredSignatureError as e:
#         LOGGER.warning(e)
#         raise TokenSignatureExpiredException("Token Signature Expired.")

#     except jwt.JWTError as e:
#         LOGGER.warning(e)
#         raise InvalidTokenException()
#     return payload
