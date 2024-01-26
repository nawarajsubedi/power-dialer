from starlette.requests import Request

from krispcall.common.app_settings import WebSettings
from krispcall.common.database.connection import DbConnection


def get_app_settings(request: Request) -> WebSettings:
    return request.app.state.settings


def get_database(request: Request) -> DbConnection:
    return request.app.state.db
