

"""
"""
from __future__ import annotations

import logging
import typing
import http
from jose import jwt
from pydantic import BaseModel, ValidationError 
from pydantic.error_wrappers import ErrorList
from krispcall.common.auth_utils.jwt import JWTClaim

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

"""
"""

class BaseHTTPException(Exception):
    """base exception class from starlette code"""

    def __init__(self, status_code: int, detail: str = None) -> None:
        if detail is None:
            detail = http.HTTPStatus(status_code).phrase
        self.status_code = status_code
        self.detail = detail

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r}, detail={self.detail!r})"

class HTTPException(BaseHTTPException):
    def __init__(self, reason: str):
        super().__init__(status_code=self.status_code, detail=reason)



class RequestValidationError(ValidationError):
    """obtained from fastapi"""

    def __init__(
        self,
        errors: typing.Sequence[ErrorList],
        *,
        model_cls: typing.Type[BaseModel],
        body: typing.Any = None,
    ) -> None:
        self.body = body
        super().__init__(errors, model_cls)



class InvalidPhoneNumber(Exception):
    pass


class PermissionDenied(Exception):
    pass


class NotSupported(Exception):
    pass


class ObjectDoesNotExist(Exception):
    pass


class UnableToFormatJSON(Exception):
    pass


class InvalidFileObjectException(Exception):
    pass


class UploadSizeLimitExceed(Exception):
    pass


class UnsupportedImageType(Exception):
    pass


class ColumnNotFound(Exception):
    pass


class CSVProcessingError(Exception):
    pass

class InsufficientBalanceException(Exception):
    pass