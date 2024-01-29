from typing import Dict, List, Any
from uuid import UUID

import re
import dateutil
from shortuuid import encode, decode, uuid
from ariadne import ScalarType
from base64 import b64encode, b64decode
from datetime import datetime


datetime_scalar = ScalarType("Datetime")
uid_scalar = ScalarType("ShortId")
cursor_scalar = ScalarType("Cursor")
email_scalar = ScalarType("EmailAddress")
filter_scalar = ScalarType("FilterParams")


@datetime_scalar.serializer
def serialize_datetime(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return value


@datetime_scalar.value_parser
def parse_datetime_value(value):
    if value:
        return dateutil.parser.parse(value)


@datetime_scalar.literal_parser
def parse_datetime_literal(ast):
    value = str(ast.value)
    return parse_datetime_value(value)


@uid_scalar.serializer
def serialize_uid(value: UUID) -> uuid:
    try:
        if isinstance(value, str):
            # handles case of UUID as string
            return encode(UUID(value))
        # normal case UUID -> shortuuid
        return encode(value)
    except ValueError:
        # handles case of shortid as string
        return value


@uid_scalar.value_parser
def parse_uid_value(value: uuid) -> UUID:
    return decode(value)


@cursor_scalar.serializer
def serialize_cursor(value: Any) -> str:
    """
    datetime to base64 isodate
    """
    if isinstance(value, datetime):
        isodate = value.isoformat()
        return b64encode(isodate.encode()).decode()
    return str(value)


@cursor_scalar.value_parser
def parse_cursor(value: Any) -> Any:
    """
    base64 isodate to datetime
    """
    isodate = b64decode(value).decode()
    return datetime.fromisoformat(isodate)


@email_scalar.value_parser
def parse_email_value(value: str) -> str:
    if re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", value):
        return value
    else:
        raise ValueError(f'"{value}" is not a valid email address')


@filter_scalar.value_parser
def parse_filter_value(value: Dict[str, str]) -> List[Dict[str, str]]:
    filters = []
    for key, val in value.items():
        key_op = key.rsplit(".")
        if len(key_op) == 2:
            name, op = key_op
        else:
            raise ValueError(f"invalid key: {key}")
        filters.append({"name": name, "operation": op, "value": val})
    return filters
