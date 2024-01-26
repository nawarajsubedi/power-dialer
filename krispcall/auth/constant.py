"""
"""
from __future__ import annotations

AUTHENTICATED_ACCESS_USER = ["authenticated", "token.kind:access"]
AUTHENTICATED_AUTH_USER = ["authenticated", "token.kind:auth"]
AUTHENTICATED_REFRESH = ["authenticated", "token.kind:refresh"]
TOKEN_EXPIRED = ["unauthenticated", "token.kind:expired"]
