from dataclasses import dataclass
from typing import List

from krispcall.konference.billing.enums import BillingTypeEnum


@dataclass
class CampaignOutboundCallRequest:
    workspace_id: str
    from_: str
    to: str
    call_sid: str
    child_call_sid: str
    parent_call_sid: str
    conference_sid: str
    campaign_id: str
    conference_friendly_name: str
    conversation_id: str
    total_participants: int
    billing_types: List[BillingTypeEnum]
    remarks: str


@dataclass
class BillingResponse:
    success: bool = False
    is_sufficient_credit: bool = False
    is_call_inprogress: bool = False
    charge_amount: float = 0
