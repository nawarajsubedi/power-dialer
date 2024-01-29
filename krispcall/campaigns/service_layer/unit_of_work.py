"""
unit of work classes
"""
from __future__ import annotations

from krispcall.campaigns.adapters.repositories import (
    CampaignCallNotesRepository,
    CampaignContactListRepository,
    CampaignVoicemailRepository,
    CampaignCallScriptsRepository,
    CampaignsRepository,
    CampaignStatRepository,
)
from krispcall.common.database.connection import DbConnection
from krispcall.common.database.unit_of_work import SqlAlchemyUnitOfWork


class CampaignContactSqlUnitOfWork(SqlAlchemyUnitOfWork):
    repository_class = CampaignContactListRepository

    def __init__(self, connection: DbConnection):
        super().__init__(connection=connection)


class CampaignVoicemailSqlUnitOfWork(SqlAlchemyUnitOfWork):
    repository_class = CampaignVoicemailRepository

    def __init__(self, connection: DbConnection):
        super().__init__(connection=connection)


class CampaignCallScriptsSqlUnitOfWork(SqlAlchemyUnitOfWork):
    repository_class = CampaignCallScriptsRepository

    def __init__(self, connection: DbConnection):
        super().__init__(connection=connection)


class CampaignCallNotesSqlUnitOfWork(SqlAlchemyUnitOfWork):
    repository_class = CampaignCallNotesRepository

    def __init__(self, connection: DbConnection):
        super().__init__(connection=connection)


class CampaignStatsSqlUnitOfWork(SqlAlchemyUnitOfWork):
    repository_class = CampaignStatRepository

    def __init__(self, connection: DbConnection):
        super().__init__(connection=connection)


class CampaignSqlUnitOfWork(SqlAlchemyUnitOfWork):
    repository_class = CampaignsRepository

    def __init__(self, connection: DbConnection):
        super().__init__(connection=connection)
