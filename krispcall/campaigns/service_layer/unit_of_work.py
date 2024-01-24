"""
unit of work classes
"""
from __future__ import annotations

from krispcall.addon.databases.unit_of_work import SqlAlchemyUnitOfWork
from krispcall.core.protocols.database import DbConnection

from krispcall.campaigns.adapters.repositories import (
    CampaignCallNotesRepository,
    CampaignContactListRepository,
    CampaignVoicemailRepository,
    CampaignCallScriptsRepository,
    CampaignsRepository,
    CampaignStatRepository,
)


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
