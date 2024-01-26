"""
UnitOfWork Protocol definition
"""
from __future__ import annotations

import logging
import typing

from krispcall.common.database.connection import (
    DbConnection,
    DbTransaction,
    SqlAlchemyRepository,
)

LOGGER = logging.getLogger(__name__)


class SqlAlchemyUnitOfWork:
    """
    SqlAlchemy Unit of Work
    """

    _repository: SqlAlchemyRepository
    repository_class: typing.Type[SqlAlchemyRepository]

    def __init__(self, connection: DbConnection):
        self._transaction: DbTransaction = None
        self._conn = connection
        self._repository = self.repository_class(self._conn)

    @property
    def repository(self) -> SqlAlchemyRepository:
        return self._repository

    def subunit(self, unit: typing.Type[SqlAlchemyUnitOfWork]) -> SqlAlchemyUnitOfWork:
        return unit(self._conn)

    async def commit(self) -> None:
        """
        commit db transaction
        """
        LOGGER.debug("COMMIT transaction")
        # await self._transaction.commit()

    async def rollback(self) -> None:
        """
        rollback db transaction
        """
        LOGGER.debug("ROLLBACK transaction")
        # await self._transaction.rollback()

    async def __aenter__(self) -> SqlAlchemyUnitOfWork:
        LOGGER.debug("BEGIN transaction")
        # self._transaction = await self._conn.transaction().start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        if exc_type is not None:
            LOGGER.exception(exc_val)
            await self.rollback()
            raise  # pylint: disable=misplaced-bare-raise
        await self.commit()
