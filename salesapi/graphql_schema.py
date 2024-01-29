"""Load graphql schema from the components"""

from ariadne import make_executable_schema, snake_case_fallback_resolvers
from ariadne.asgi import GraphQL
from ariadne.load_schema import read_graphql_file

from krispcall.campaigns.entrypoints.graphql import types as camp_types
from krispcall.common.app_settings.app_settings import resolve_component_module_locations
from krispcall.common.error_handler.graphql_error import default_graphql_badrequest_handler
from krispcall.common.graphql import (
    cursor_scalar,
    datetime_scalar,
    filter_scalar,
    uid_scalar,
)
# from krispcall.bulksms.entrypoints.graphql import types as bulk_types

GRAPHQL_FILES = [
    "types.graphql",
    "queries.graphql",
    "mutations.graphql",
    "schema.graphql",
]


def load_schema() -> str:
    dirs = resolve_component_module_locations(
        [
            "krispcall.campaigns",
            # "krispcall.bulksms",
            "salesapi",
        ],
        "schemas",
    )

    schema_list = []

    for path in dirs:
        for graphql_file in GRAPHQL_FILES:
            try:
                f = path.joinpath((graphql_file))
                schema_list.append(read_graphql_file(f))
            except:
                pass
    return "\n".join(schema_list)


TYPE_DEFS = load_schema()

# create schema and export
schema = make_executable_schema(
    TYPE_DEFS,
    [
        # subscription,
        camp_types.query,
        camp_types.mutation,
        # bulk_types.query,
        # bulk_types.mutation,
        datetime_scalar,
        uid_scalar,
        cursor_scalar,
        filter_scalar,
    ],
    snake_case_fallback_resolvers,
)
graphql = GraphQL(
    schema, error_formatter=default_graphql_badrequest_handler, debug=True
)
