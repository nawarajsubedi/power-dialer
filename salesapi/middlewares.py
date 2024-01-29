from __future__ import annotations
import typing
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware

from krispcall.common.app_settings.app_settings import WebSettings
from krispcall.common.error_handler.error_handlers import on_authentication_error
from krispcall.common.middlewares.middleware import JWTAuthenticationBackend, ResponseMiddleware


def load_middlewares(settings: WebSettings) -> typing.List[Middleware]:
    return [
        Middleware(ResponseMiddleware),
        Middleware(
            CORSMiddleware,
            allow_origins=settings.cors_allow_origins,
            allow_methods=settings.cors_allow_methods,
            allow_headers=settings.cors_allow_headers,
            allow_credentials=settings.cors_allow_credentials,
            expose_headers=settings.cors_expose_headers,
            max_age=settings.cors_max_age,
        ),
        # Load session middleware
        Middleware(
            SessionMiddleware,
            secret_key=settings.secret_key.get_secret_value(),
            max_age=settings.session_lifetime,
        ),
        Middleware(
            AuthenticationMiddleware,
            backend=JWTAuthenticationBackend(
                secret=settings.jwt_secret_public_pem.get_secret_value(),
                audience=settings.app_id,
            ),
            on_error=on_authentication_error,
        ),
    ]
