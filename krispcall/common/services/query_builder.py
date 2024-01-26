"""
advanced query builder for filters and sorting
"""

from datetime import datetime
from typing import Any, Callable, Dict, List, Union, Literal
from krispcall.common.services.abstracts import (
    PaginationParams,
    SearchType,
    OffsetPaginationParams,
)
from krispcall.common.services.helper import change_camel_case_to_snake
import sqlalchemy as sa
from sqlalchemy.sql.selectable import Selectable
from datetime import timedelta
from sqlalchemy.dialects import postgresql

UNARY_OPERATORS = ["is_null", "is_not_null", "is_true", "is_false"]


def is_null(arg1: Any, arg2: Any = None):
    return arg1 == None  # noqa


def is_not_null(arg1: Any, arg2: Any = None):
    return arg1 != None  # noqa


def is_true(arg1: bool, arg2: Any = None):
    return arg1 is True


def is_false(arg1: bool, arg2: Any = None):
    return arg1 is False


def equals(arg1: Union[int, str, datetime], arg2: Union[int, str, datetime]):
    return arg1 == arg2


def not_equals(
    arg1: Union[int, str, datetime], arg2: Union[int, str, datetime]
):
    return arg1 != arg2


def ignore_case_equals(arg1: str, arg2: str):
    return sa.func.lower(arg1) == arg2.lower()


def greater_than(arg1: Union[int, datetime], arg2: Union[int, datetime]):
    return arg1 > arg2 # type: ignore


def greater_than_equals(
    arg1: Union[int, datetime], arg2: Union[int, datetime]
):
    return arg1 >= arg2 # type: ignore


def less_than(arg1: Union[int, datetime], arg2: Union[int, datetime]):
    return arg1 < arg2 # type: ignore


def less_than_equals(arg1: Union[int, datetime], arg2: Union[int, datetime]):
    return arg1 <= arg2 # type: ignore


def like(arg1: str, arg2: str):
    return arg1.like(arg2) # type: ignore


def not_like(arg1: str, arg2: str):
    return ~arg1.like(arg2) # type: ignore


def ilike(arg1: str, arg2: str):
    return arg1.ilike(arg2) # type: ignore


def not_ilike(arg1: str, arg2: str):
    return ~arg1.ilike(arg2) # type: ignore


def in_(arg1: Union[int, str], arg2: List[Union[int, str]]):
    return arg1.in_(arg2) # type: ignore


def inarray_(arg1: List[str], arg2: Any):
    arr = postgresql.array(arg2)
    return arg1.op("?|")(arr) # type: ignore


def notin_(arg1: Union[int, str], arg2: List[Union[int, str]]):
    return arg1.notin_(arg2) # type: ignore


def contains(arg1: str, arg2: str):
    return arg1.contains(arg2) # type: ignore


def date_greater_than(arg1: Union[int, datetime], arg2: str):
    arg2 = datetime.fromisoformat(arg2) # type: ignore
    return arg1 > arg2 # type: ignore


def date_less_than(arg1: Union[int, datetime], arg2: str):
    arg2 = datetime.fromisoformat(arg2) # type: ignore
    return arg1 < arg2 # type: ignore


def date_greater_than_equal(arg1: Union[int, datetime], arg2: str):
    arg2 = datetime.fromisoformat(arg2) # type: ignore
    return arg1 >= arg2 # type: ignore


def date_less_than_equal(arg1: Union[int, datetime], arg2: str):
    arg2 = datetime.fromisoformat(arg2) # type: ignore
    return arg1 <= arg2 # type: ignore


def date_equals(arg1: Union[int, datetime], arg2: str):
    arg2 = datetime.fromisoformat(arg2) # type: ignore
    arg3 = arg2 + timedelta(days=1) # type: ignore
    return sa.and_(arg1 >= arg2, arg1 < arg3) # type: ignore


OPERATORS: Dict[str, Callable] = {
    # Unary operators.
    "is_null": is_null,
    "is_not_null": is_not_null,
    "is_true": is_true,
    "is_false": is_false,
    # Binary operators.
    "eq": equals,
    "ne": not_equals,
    "ieq": ignore_case_equals,
    "gt": greater_than,
    "lt": less_than,
    "gte": greater_than_equals,
    "lte": less_than_equals,
    "like": like,
    "not_like": not_like,
    "ilike": ilike,
    "not_ilike": not_ilike,
    "in_": in_,
    "notin_": notin_,
    "contains": contains,
    "date_gt": date_greater_than,
    "date_lt": date_less_than,
    "date_gte": date_greater_than_equal,
    "date_lte": date_less_than_equal,
    "date_eq": date_equals,
    "inarray_": inarray_,
}


def get_column(query, name):
    try:
        snake = change_camel_case_to_snake(name)
        return query.c[snake]
    except KeyError:
        raise KeyError("column {} not found".format(name))


def search_builder(query, search: SearchType):
    if search is None:
        return []
    restrictions = []
    for c in search.columns:
        col = get_column(query, c)
        if type(col.type) == sa.types.Integer:
            # If column type is integer,
            # use == instead of like for comparison
            if isinstance(search.value, int) and len(str(search.value)) <= 10:
                # Check if it is valid integer
                # with valid range to be checked
                restrictions.append(col == search.value)
        else:
            if c.lower() in ["firstname", "lastname"]:
                # if len(search.value.split(' ')) > 1:
                search_value = [
                    item + "%"
                    for item in search.value.split(" ") # type: ignore
                    if not item == ""
                ]
                restrictions.append(col.ilike(sa.any_(search_value)))
            else:
                restrictions.append(col.ilike(f"%{str(search.value)}%"))
    return restrictions


def filter_builder(query, filter: List[Dict]):
    if filter is None:
        return []
    restrictions = []
    for f in filter:
        col = get_column(query, f["name"])
        if f["operation"] in UNARY_OPERATORS:
            restrictions.append(OPERATORS[f["operation"]](col))
        else:
            restrictions.append(OPERATORS[f["operation"]](col, f["value"]))
    return restrictions


def query_builder_before_paginated(
    query: Selectable, params: PaginationParams
) -> Selectable:
    filter: List[Dict] = params.filter # type: ignore
    search: SearchType = params.search # type: ignore
    sort: str = params.sort # type: ignore
    order: Literal["asc", "desc"] = params.order
    first, after, after_with = (
        params.first,
        params.after,
        params.after_with,
    )
    before, before_with = params.before, params.before_with
    filters: List[List[Dict[str, Any]]] = params.filters # type: ignore

    # restrictions = []
    # search_restrictions = []
    alias = query.alias("query")
    # Search clauses
    search_restrictions = search_builder(alias, search)
    restrictions = filter_builder(alias, filter)
    if filters:
        for filter in filters:
            f = filter_builder(alias, filter)
            search_restrictions.append(sa.and_(*f))

    if search_restrictions:
        restrictions.append(sa.or_(*search_restrictions))

    if restrictions:
        selectable = sa.select([alias], whereclause=sa.and_(*restrictions))
    else:
        selectable = sa.select([alias])

    # Ordering
    if sort:
        order_col = get_column(selectable, sort)
        if not order == "asc":
            order_col = order_col.desc()
        selectable = selectable.order_by(order_col)
    return selectable


def query_builder(
    query: Selectable, params: PaginationParams, cursor: str = "created_on"
) -> Selectable:
    first, after, after_with = params.first, params.after, params.after_with
    before, before_with = params.before, params.before_with
    # Pagination
    alias = query.alias("query")
    selectable = sa.select([alias])

    cursor_column = get_column(alias, cursor)
    if first or after:
        selectable = selectable.order_by(cursor_column.desc())
        if after:
            selectable = selectable.where(cursor_column < after)
        elif after_with:
            selectable = selectable.where(cursor_column <= after_with)
    else:
        selectable = selectable.order_by(cursor_column)
        if before:
            selectable = selectable.where(cursor_column > before)
        elif before_with:
            selectable = selectable.where(cursor_column >= before_with)
    return selectable


def offset_query(
    query: Selectable, params: OffsetPaginationParams
) -> Selectable:
    filter: List[Dict] = params.filter # type: ignore
    sort: str = params.sort # type: ignore
    search: SearchType = params.search # type: ignore
    order: Literal["asc", "desc"] = params.order
    filters: List[List[Dict[str, Any]]] = params.filters # type: ignore

    alias = query.alias("query")

    # Search clauses
    search_restrictions = search_builder(alias, search)
    restrictions = filter_builder(alias, filter)
    if filters:
        for filter in filters:
            f = filter_builder(alias, filter)
            search_restrictions.append(sa.and_(*f))

    if search_restrictions:
        restrictions.append(sa.or_(*search_restrictions))

    if restrictions:
        selectable = sa.select([alias], whereclause=sa.and_(*restrictions))
    else:
        selectable = sa.select([alias])

    # Ordering
    if sort:
        order_col = get_column(selectable, sort)
        if not order == "asc":
            order_col = order_col.desc()
        selectable = selectable.order_by(order_col)

    return selectable
