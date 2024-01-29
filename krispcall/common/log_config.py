"""
"""
from __future__ import annotations

import logging
import logging.config
import typing
from copy import deepcopy
from krispcall.common.app_settings.app_settings import CoreSettings, resolve_path_from_config

# logging
ONE_MB_IN_BYTES: int = 10_00_000
LOG_FILE_MAX_SIZE: int = ONE_MB_IN_BYTES * 100
LOG_BACKUP_FILES_COUNT: int = 3

LOG_CONFIG: typing.Dict[str, typing.Any] = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "[{asctime}] {levelname}:{name} ({module}@{lineno}) {message}",
            "style": "{",
        },
        # "accesslog": {
        #     "format": '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"',
        #     "style": "%",
        # },
    },
    "filters": {},
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "stream": "ext://sys.stdout",  # Default is stderr
        },
        "applog": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "",
            "level": "WARNING",
            "maxBytes": LOG_FILE_MAX_SIZE,
            "backupCount": LOG_BACKUP_FILES_COUNT,
            "formatter": "default",
        },
        "errorlog": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "",
            "level": "ERROR",
            "maxBytes": LOG_FILE_MAX_SIZE,
            "backupCount": LOG_BACKUP_FILES_COUNT,
            "formatter": "default",
        },
    },
    "loggers": {
        "": {"level": "WARNING", "handlers": ["console"]},
        "krispcall_utils": {
            "level": "WARNING",
            "handlers": ["console", "applog", "errorlog"],
            "propagate": False,
        },
    },
    "root": {"handlers": ["console"], "level": "ERROR"},
}


def configure_logging(
    settings: CoreSettings,
    handlers: typing.Optional[typing.Dict[str, typing.Any]] = None,
    loggers: typing.Optional[typing.Dict[str, typing.Any]] = None,
) -> None:
    log_config = deepcopy(LOG_CONFIG)
    if settings.debug:
        log_config["handlers"]["console"]["level"] = "DEBUG"
        log_config["loggers"]["krispcall_utils"]["level"] = "DEBUG"
        log_config["root"]["level"] = "DEBUG"

    log_path = resolve_path_from_config(settings, settings.log_dir)
    log_config["handlers"]["applog"]["filename"] = (
        log_path / settings.application_log_file
    )
    log_config["handlers"]["errorlog"]["filename"] = (
        log_path / settings.error_log_file
    )

    if handlers:
        log_config["handlers"] |= handlers
    if loggers:
        log_config["loggers"] |= loggers

    logging.config.dictConfig(log_config)
