from __future__ import annotations
from starlette.routing import Mount
from starlette.applications import Starlette

from krispcall.common import bootstrap
from krispcall.common.database.bootstrap import init_database, load_exception_handlers
from krispcall.common.locales import init_translation
from krispcall.common.configs.log_config import configure_logging


from salesapi import settings
from salesapi.graphql_schema import graphql
from salesapi.middlewares import load_middlewares
from krispcall.konference.entrypoints.route_handlers.routes import (
    routes as konference_routes,
)

ROUTES = [
    Mount(
        "/api/" + settings.API_BASE_VERSION,
        routes=[Mount("/graphql", graphql)],
    ),
    Mount(
        "/",
        routes=konference_routes,
    ),
]


def new_app(settings_) -> Starlette:
    loggers, handlers = settings.get_loggers_config(settings_)
    configure_logging(settings_, handlers=handlers, loggers=loggers)
    db = init_database(settings_)
    _middlewares = load_middlewares(settings_)
    translator = init_translation()
    twilio = bootstrap.init_twillo(settings_)
    queue = bootstrap.init_queue(settings_)
    app = Starlette(
        debug=settings_.debug,
        routes=ROUTES,
        middleware=_middlewares,
        exception_handlers=load_exception_handlers(),
        on_startup=[
            db.connect,
            queue.connect,
        ],
        on_shutdown=[
            db.disconnect,
        ],
    )

    app.state.settings = settings_
    app.state.db = db
    app.state.twilio = twilio
    app.state.translator = translator
    app.state.queue = queue
    return app


app = new_app(settings.get_application_settings())
