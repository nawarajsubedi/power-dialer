from __future__ import annotations
from krispcall.konference.adapters import repositories
from krispcall.common.database.unit_of_work import SqlAlchemyUnitOfWork
from krispcall.common.database.connection import DbConnection


class CampaignConversationSqlUnitOfWork(SqlAlchemyUnitOfWork):
    repository_class = repositories.CampaignConversationRepository

    def __init__(self, connection: DbConnection) -> None:
        super().__init__(connection=connection)


class ParticipantCallSqlUnitOfWork(SqlAlchemyUnitOfWork):
    repository_class = repositories.ParticipantCallRepository

    def __init__(self, connection: DbConnection) -> None:
        super().__init__(connection=connection)
