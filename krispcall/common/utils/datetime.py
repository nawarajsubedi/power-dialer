"""
helper functions around pendulum
"""
from __future__ import annotations

import time
from functools import partial

import pendulum
from pendulum.date import Date as Date  # noqa: F401
from pendulum.datetime import DateTime as DateTime
from pendulum.duration import Duration as Duration  # noqa: F401
from pendulum.parser import parse

# partial functions
utc_now = partial(pendulum.now, "UTC")
utc_today = partial(pendulum.today, "UTC")
parse_datetime = partial(parse, strict=True)
from_isoformat = partial(pendulum.from_format)
duration = partial(pendulum.duration)

# deprecated
date_fromisoformat = partial(
    pendulum.from_format,
)
# deprecated
datetime_fromisoformat = partial(
    pendulum.from_format,
)


def time_in_nanoseconds() -> int:
    """return time in nanoseconds"""
    return int(time.time() * 1e9)


def days_in_future(days: int = 1) -> DateTime:
    """return datetime in future in days from now"""
    return utc_now().add(days=days)


def days_in_past(days: int = 1) -> DateTime:
    """return datetime in past in days from now"""
    return utc_now().subtract(days=days)  # type: ignore
