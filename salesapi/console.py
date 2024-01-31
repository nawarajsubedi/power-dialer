from __future__ import annotations
import uvicorn
import typing
from pathlib import Path
from krispcall.common.database.settings import DatabaseSettings
from salesapi import settings
from alembic import command  # type: ignore
from alembic.config import Config

from salesapi.alembic import constants  # type: ignore\
from krispcall.common.configs.app_settings import resolve_component_module_location

class CliCommand:
    """Sales dialer cli command"""

    def __init__(self) -> None:
        _settings = settings.get_application_settings()
        self.alembic = AlembicCommand(_settings)

    def serve(self, host: str = "127.0.0.1", port: int = 3001):
        """Serves the sales dialer api"""
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            log_level="info",
            reload=True,
        )


class AlembicCommand:
    """alembic migration commands"""

    def __init__(self, settings: DatabaseSettings):
        self.alembic_cfg = get_alembic_config()
        self.alembic_cfg.set_main_option("sqlalchemy.url", settings.pg_dsn)
        self.alembic_cfg.set_main_option("database_schema", "public")

        migration_paths = []
        for component in settings.components:
            migration_paths.append(
                resolve_component_module_location(
                    component, "alembic_versions"
                )
            )
        self.alembic_cfg.set_main_option(
            "version_locations",
            " ".join([str(path) for path in migration_paths]),
        )

    def current(self) -> None:
        """show current revision"""
        command.current(self.alembic_cfg)

    def heads(self, verbose: bool = False) -> None:
        """show available heads"""
        command.heads(self.alembic_cfg, verbose=verbose)

    def history(self) -> None:
        """show revision history"""
        command.history(self.alembic_cfg)

    def initrevision(
        self,
        message: str,
        branch_label: str,
        version_path: str,
        head: str = "base",
    ) -> None:
        """initialize a branch"""
        command.revision(
            self.alembic_cfg,
            message=message,
            autogenerate=False,
            head=head,
            branch_label=branch_label,
            version_path=version_path,
        )

    def makemigrations(
        self,
        message: str,
        branch_label: typing.Optional[str] = None,
        depends: typing.Optional[str] = None,
        auto: bool = False,
    ) -> None:
        """create migration script"""
        _head = f"{branch_label}@head"
        command.revision(
            self.alembic_cfg,
            autogenerate=auto,
            message=message,
            head=_head,
            depends_on=depends,
        )

    def migrate(self, revision: str = "head", sql: bool = False) -> None:
        """upgrade to a revision"""
        command.upgrade(self.alembic_cfg, revision=revision, sql=sql, tag=None)

    def rollback(self, revision: str) -> None:
        """downgrade revision"""
        command.downgrade(self.alembic_cfg, revision=revision)

    def branches(self, verbose: bool = False) -> None:
        """list all branches"""
        command.branches(self.alembic_cfg, verbose=verbose)

    def show(self, rev: str) -> None:
        """show revision info"""
        command.show(self.alembic_cfg, rev=rev)


def get_alembic_config() -> Config:
    """return alembic config object"""
    alembic_path = Path(constants.__file__).parent
    alembic_ini_file = alembic_path.joinpath("alembic.ini")
    config = Config(str(alembic_ini_file))
    config.set_main_option("script_location", str(alembic_path))
    return config

