from typing import Dict, Optional
from pydantic import EmailStr

from krispcall.common.with_response import DataModel, ResourceModel

class BundleInput(DataModel):
    friendly_name: str
    email: EmailStr
    status_callback: Optional[str]
    iso_country: Optional[str]
    end_user_type: Optional[str]
    number_type: Optional[str]


class BundleResource(ResourceModel):
    sid: str
    account_sid: str
    friendly_name: str
    regulation_sid: str
    status: str
    email: EmailStr
    status_callback: str
    valid_until: str
    links: Dict[str, str]
