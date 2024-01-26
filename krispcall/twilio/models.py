from dataclasses import dataclass

from krispcall.konference.domain.models import ConferenceStatus


@dataclass
class ConferenceResource:
    conference_status: ConferenceStatus = None # type: ignore
    conference_id: str = None # type: ignore


@dataclass
class AccountCredential:
    account_sid: str = None # type: ignore
    auth_token: str = None # type: ignore
    api_key: str = None # type: ignore
    api_secret: str = None # type: ignore
