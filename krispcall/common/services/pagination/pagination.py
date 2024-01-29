"""
"""
from __future__ import annotations

import typing
from krispcall.common.database.connection import DbConnection
from krispcall.common.services.pagination.query_builder import (
    query_builder,
    get_column,
    offset_query,
    query_builder_before_paginated,
)
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.selectable import Selectable
from krispcall.common.responses.response_model import (
    OffsetPageInfo,
    PaginationParams,
    PageInfo,
    PaginatedResource,
    Edges,
    OffsetPaginationParams,
    OffsetPaginatedResource,
)
from datetime import datetime
from sqlalchemy import func


class PaginationError(Exception):
    pass


class CursorPagination(object):
    """
    parameters:
    query: query to execute
    db_conn: database connection
    node_model: model to format data node
    """

    def __init__(
        self,
        db_conn: DbConnection,
        query: Selectable = None, # type: ignore
        node_model=None,
        cursor_column="created_on",
    ):
        self.db = db_conn
        self.query = None
        self.cursor_column = cursor_column
        self.node_model = node_model
        self._query = query

    async def resource(self, params: PaginationParams):
        limit = self.page_limit(params)
        if limit:
            return await self.db.fetch_all(query=self.query.limit(limit)) # type: ignore
        else:
            return await self.db.fetch_all(self.query)

    async def total_count(self, initial_query):
        return 0
        # self.count = initial_query.alias("count")
        # count_query = select([func.count()]).select_from(self.count)
        # return await self.db.fetch_val(count_query)

    async def page(self, params: PaginationParams):
        initial_query_builder = query_builder_before_paginated(
            self._query, params
        )
        self.query = query_builder(
            initial_query_builder, params, self.cursor_column
        )
        edges = await self.edges(params)
        start_cursor = self.__start_cursor(edges)
        end_cursor = self.__end_cursor(edges)
        has_next_page = await self.__has_next(params, end_cursor) # type: ignore
        has_previous_page = await self.__has_previous(params, start_cursor) # type: ignore
        total_count = await self.total_count(initial_query_builder)
        paginated_data = PaginatedResource.construct(
            edges=edges,
            page_info=PageInfo.construct(
                start_cursor=start_cursor,
                end_cursor=end_cursor,
                has_next_page=has_next_page,
                has_previous_page=has_previous_page,
                total_count=total_count,
            ),
        )
        return paginated_data

    async def edges(self, params: PaginationParams):
        resource = await self.resource(params)
        paging = self.paging_direction(params)
        edges = []
        # for node in resource:
        #     try:
        #         print("##### \n", node.get("content"))
        #         edges.append(
        #             Edges.construct(
        #                 cursor=node.get(self.cursor_column, None),
        #                 node=self.__node(dict(node)),
        #             )
        #         )
        #     except Exception as e:
        #         print(e)
        #         print(dir(node))
        #         print(node)
        #         continue
        edges = [
            Edges.construct(
                cursor=node.get(self.cursor_column, None),
                node=self.__node(node),
            )
            for node in resource
        ]

        if paging == "backward":
            edges.reverse()
        return edges

    def __start_cursor(self, edges: typing.List[Edges]):
        try:
            return edges[0].cursor
        except Exception:
            return None

    def __end_cursor(self, edges: typing.List[Edges]):
        try:
            return edges[-1].cursor
        except Exception:
            return None

    def __node(self, node):
        if self.node_model:
            return self.node_model(**dict(node))
        return dict(node)

    async def __has_next(self, params: PaginationParams, beyond: datetime):
        before = params.before
        query = query_builder_before_paginated(self._query, params).alias(
            "alias"
        )

        if beyond is None:
            if before is None:
                return False
            beyond = before

        cursor = get_column(query, self.cursor_column)
        beyond_the_limit = await self.db.fetch_all(
            query=select([query]).where(cursor < beyond)
        )
        return bool(beyond_the_limit)

    async def __has_previous(self, params: PaginationParams, beyond: datetime):
        after = params.after
        query = query_builder_before_paginated(self._query, params).alias(
            "alias"
        )

        if beyond is None:
            if after is None:
                return False
            beyond = after

        cursor = get_column(query, self.cursor_column)
        beyond_the_limit = await self.db.fetch_all(
            query=select([query]).where(cursor > beyond)
        )
        return bool(beyond_the_limit)

    def __enter__(self):
        return self

    def __exit__(self, typ, value, traceback):
        pass

    def _get_column(self, name):
        return getattr(self._query.c, name)

    @staticmethod
    def paging_direction(params: PaginationParams):
        first = params.first
        last = params.last
        after = params.after
        before = params.before
        after_with = params.after_with
        before_with = params.before_with

        if after or first or after_with:
            return "forward"
        elif before or last or before_with:
            return "backward"
        else:
            raise PaginationError("Invalid paging parameters")

    @staticmethod
    def page_limit(params: PaginationParams):
        return params.first or params.last


class OffsetPagination(object):
    """
    parameters:
    query: query to execute
    db_conn: database connection
    """

    def __init__(
        self,
        db_conn: DbConnection,
        query: Selectable = None, # type: ignore
        node_model=None,
    ):
        self.db = db_conn
        self.query = None
        self.node_model = node_model
        self._query = query

    async def resource(self, params: OffsetPaginationParams):
        offset = self.page_limit(params)
        if not offset:
            return await self.db.fetch_all(self.query)

        if params.limit:
            query1 = offset_query(self._query, params)
            query = query1.limit(params.limit)
            if offset:
                query = query.offset((offset - 1) * params.limit)
            return await self.db.fetch_all(query=query)

    async def page_info(self, params: OffsetPaginationParams):
        total_count = self._query.alias("total_count")
        count_query = select([func.count()]).select_from(total_count)
        total_count = await self.db.fetch_val(count_query)
        edges = await self.edges(params)

        return OffsetPaginatedResource.construct(
            edges=edges,
            page_info=OffsetPageInfo.construct(
                offset=params.offset,
                limit=params.limit,
                total=total_count,
            ),
        )

    async def edges(self, params: OffsetPaginationParams):
        resource = await self.resource(params)
        edges = [
            Edges.construct(
                node=self.__node(node),
            )
            for node in resource # type: ignore
        ]
        return edges

    def __node(self, node):
        if self.node_model:
            return self.node_model(**dict(node))
        return dict(node)

    @staticmethod
    def page_limit(params: OffsetPaginationParams):
        return params.offset
