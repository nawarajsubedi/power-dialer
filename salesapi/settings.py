""" Loads settings"""

from __future__ import annotations
import os
import sys
import typing
from pathlib import Path
from uuid import UUID
from functools import lru_cache
import logging
from pydantic import PositiveInt

from krispcall.common.configs.app_settings import CoreSettings, Settings, resolve_path_from_config
from pydantic import (
    ValidationError,
)
from yaml import safe_load
from krispcall.common.configs.log_config import LOG_BACKUP_FILES_COUNT, LOG_FILE_MAX_SIZE


ENV_PREFIX = "KRISPCALL_"
APP_PATH = Path(__file__).parent
BASE_PATH = APP_PATH.parent
API_BASE_VERSION = "v1"
LOGGER = logging.getLogger(__name__)

def _load_config(
    app_env: str, config_dir: Path
) -> typing.Dict[typing.Any, typing.Any]:
    """load config file"""
    config_file = config_dir.joinpath(f"{app_env}.yaml")
    if not config_file.exists():
        raise ValueError(f"Config file {config_file} doesn't exists")
    LOGGER.info("Found configuration ... %s", config_file)
    return safe_load(open(config_file, "r").read())

def settings_factory(
    settings_class: typing.Type[CoreSettings], env_prefix: str, base_path: Path
) -> CoreSettings:
    """generate settings object using provided class"""
    app_env = os.getenv(env_prefix + "APP_ENV", "production")
    # config_dir = base_path.joinpath("config")
    try:
        settings = settings_class(
            _env_file=f"{app_env}.env",
            base_path=base_path,
            app_env=app_env,
            **_load_config(app_env, base_path),
        )
    except ValidationError as e:
        LOGGER.error("Invalid Config/Settings.")
        print(e)
        sys.exit(-1)
    else:
        return settings


class AppSettings(Settings):
    app_id: str = "com.krispcall.salesapi"
    app_name: str = "salesapi"
    allowed_media_types: typing.Tuple[str, ...] = (
        "image/png",
        "image/jpg",
        "image/jpeg",
    )
    components: typing.List[str] = [
        "krispcall.campaigns",
        "krispcall.konference",
    ]

    agent_jwt_audience: str = "com.timetracko.tracker"
    jwt_audiences: typing.List[str] = [
        "com.krispcall.api",
    ]
    jwt_auth_token_lifetime_minutes: PositiveInt = typing.cast(
        PositiveInt, 1 * 7 * 24 * 60
    )
    jwt_access_token_lifetime_minutes: PositiveInt = typing.cast(
        PositiveInt, 1 * 7 * 24 * 60  # 1 week
    )
    jwt_refresh_token_lifetime_minutes: PositiveInt = typing.cast(
        PositiveInt, 2 * 7 * 24 * 60  # 2 week
    )

    jwt_reset_token_lifetime_minutes: PositiveInt = typing.cast(
        PositiveInt, 20  # 20 min
    )

    authenticate_devices: typing.Dict[str, UUID] = {
        "web": UUID("befecbb1-5d20-448d-bf79-fe8a60dc2dca"),
        "desktop": UUID("d470cbb8-8bd6-4528-8f28-aeaf118f32ae"),
    }
    test_access_token: str = ""
    gateway_uri: str = (
        ""  # uri of the main application, required to place in the audio urls
    )

    class Config:  # pylint: disable=too-few-public-methods
        env_prefix = ENV_PREFIX


@lru_cache()
def get_application_settings(env_prefix=ENV_PREFIX, base_path=BASE_PATH):
    return settings_factory(
        settings_class=AppSettings,
        env_prefix=env_prefix,
        base_path=base_path,
    )


def get_loggers_config(settings):
    logpath = resolve_path_from_config(settings, settings.log_dir)
    _handlers = {
        "accesslog": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": logpath / settings.access_log_file,
            "level": "DEBUG",
            "maxBytes": LOG_FILE_MAX_SIZE,
            "backupCount": LOG_BACKUP_FILES_COUNT,
            "formatter": "default",
        },
        "rollbar": {
            "class": "rollbar.logger.RollbarHandler",
            "level": "ERROR",
            "formatter": "default",
        },
    }
    _loggers = {
        "uvicorn": {
            "handlers": ["console", "accesslog", "errorlog"],
            "level": "DEBUG",
            "propagate": False,
        },
        "service": {
            "level": "DEBUG",
            "handlers": ["console", "applog", "errorlog", "rollbar"],
            "propagate": False,
        },
    }
    return _loggers, _handlers
