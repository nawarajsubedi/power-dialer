"""
"""
from __future__ import annotations

import typing
from functools import wraps


class Command:
    pass


R = typing.Union[Command, typing.Any]
T = typing.Callable[[Command], R]


def handler(klass: typing.Type[Command]) -> typing.Callable[[T], R]:
    def inner(func: T) -> T:
        @wraps(func)
        def wrapper(command: Command) -> R:
            if not isinstance(command, klass):
                return command
            return func(command)

        return wrapper

    return inner
