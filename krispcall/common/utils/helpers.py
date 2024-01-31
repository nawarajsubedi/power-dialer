from __future__ import annotations

import base64


def url_safe_encode(string: str) -> str:
    encoded_bytes = base64.urlsafe_b64encode(string.encode("ascii"))
    return str(encoded_bytes)[2:-1]


def url_safe_decode(string: str) -> str:
    encoded_bytes = base64.urlsafe_b64decode(string)
    return str(encoded_bytes, "ascii")


async def get_ip_address(request):
    ip_address = request.headers.get("x-original-forwarded-for")
    if not ip_address:
        ip_address = list(request.scope.get("client"))
        ip_address = ip_address[0]
    return ip_address
