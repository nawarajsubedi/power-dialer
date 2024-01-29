import typing
from jose import jwt  # type: ignore
import logging
import typing

from jose import jwt

from krispcall.common.middlewares.user import create_authenticated_principal_user  # type: ignore

LOGGER = logging.getLogger(__name__)

from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    UnauthenticatedUser,
)
from starlette.requests import HTTPConnection
from starlette.responses import PlainTextResponse, Response
from starlette.types import ASGIApp, Receive, Scope, Send

from krispcall.common.app_settings.request_helpers import get_app_settings
from krispcall.common.error_handler.exceptions import FailedIdentityException, TokenException, TokenSignatureExpiredException
from krispcall.common.utils.datetime import utc_now
from starlette.middleware.base import BaseHTTPMiddleware


class InvalidTokenException(FailedIdentityException):
    """Invalid Token"""

    message = "Invalid Token"


def decode_token(
    token: str, secret: str, algorithms: typing.List[str], audience: str
) -> typing.Optional[typing.Dict]:
    """decode jwt token with secret"""
    payload = None
    try:
        payload = jwt.decode(
            token=token, key=secret, algorithms=algorithms, audience=audience
        )
    except jwt.ExpiredSignatureError as e: # type: ignore
        LOGGER.warning(e)
        raise TokenSignatureExpiredException("Token Signature Expired.")

    except jwt.JWTError as e: # type: ignore
        LOGGER.warning(e)
        raise InvalidTokenException() # type: ignore
    return payload


class AuthenticationMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        backend: AuthenticationBackend,
        on_error: typing.Optional[
            typing.Callable[[HTTPConnection, AuthenticationError], Response]
        ] = None,
    ) -> None:
        self.app = app
        self.backend = backend
        self.on_error: typing.Callable[
            [HTTPConnection, AuthenticationError], Response
        ] = (on_error if on_error is not None else self.default_on_error)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ["http", "websocket"]:
            await self.app(scope, receive, send)
            return

        conn = HTTPConnection(scope)
        try:
            auth_result = await self.backend.authenticate(conn)
        except AuthenticationError as exc:
            response = self.on_error(conn, exc)
            if scope["type"] == "websocket":
                await send({"type": "websocket.close", "code": 1000})
            else:
                await response(scope, receive, send)
            return

        if auth_result is None:
            auth_result = AuthCredentials(), UnauthenticatedUser()
        scope["auth"], scope["user"] = auth_result
        await self.app(scope, receive, send)

    @staticmethod
    def default_on_error(conn: HTTPConnection, exc: Exception) -> Response:
        return PlainTextResponse(str(exc), status_code=400)


def on_authentication_error(_, exc):
    raise exc

def get_authorization_token(authorization: str, prefix: str) -> str:

    scheme, token = authorization.strip().split(" ")
    if scheme.strip().casefold() != prefix:

        raise ValueError("Invalid authorization scheme.")

    if not token:

        raise ValueError("Missing token.")

    return token

class JWTAuthenticationBackend(AuthenticationBackend):
    def __init__(self, secret: str, prefix: str = "JWT", audience: str = ""):
        self.secret = secret
        self.prefix = prefix.strip().casefold()
        self.audience = audience

    async def authenticate(self, request):
        if "Authorization" not in request.headers:
            return None

        try:
            token = get_authorization_token(
                request.headers["Authorization"], prefix=self.prefix
            )
        except ValueError as e:
            raise AuthenticationError(str(e))

        settings = get_app_settings(request)
        try:
            payload = decode_token(
                token,
                secret=self.secret,
                audience=self.audience,
                algorithms=settings.jwt_algorithms,
            )

        except TokenSignatureExpiredException:
            return (
                AuthCredentials(["unauthenticated", "token.kind:expired"]),
                UnauthenticatedUser(),
            )
        except TokenException as e:
            raise AuthenticationError(str(e))

        if "kind" not in payload:
            raise AuthenticationError("Invalid Token Kind")
        kind = payload["kind"]
        scopes = ["authenticated", f"token.kind:{kind}"]

        if "scope" in payload and payload["scope"]:
            scopes.extend(payload["scope"])

        if "fresh" in payload and payload["fresh"]:
            scopes.append("token.age:fresh")

        return (
            AuthCredentials(scopes),
            create_authenticated_principal_user(payload),
        )


class ResponseMiddleware(BaseHTTPMiddleware):
    """attach date to response header"""

    async def dispatch(self, request, call_next):
        """ """
        response = await call_next(request)
        response.headers["Response-Time"] = utc_now().isoformat()
        return response

