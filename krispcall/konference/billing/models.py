from typing import List, Optional
from dataclasses import dataclass

from krispcall.konference.billing.enums import BillingTypeEnum
from krispcall.konference.domain.models import (
    WorkspaceReference,
    TwilioCallSid,
    TwilioConferenceFriendlyName,
    TwilioConferenceSid,
    CampaignConversationReference,
    TwilioConferenceSid,
)


@dataclass
class CampaignOutboundCallRequest:
    workspace_id: WorkspaceReference
    from_: str
    to: str
    call_sid: TwilioCallSid
    child_call_sid: TwilioCallSid
    parent_call_sid: TwilioCallSid
    conference_sid: TwilioConferenceSid
    campaign_id: CampaignConversationReference
    conference_friendly_name: TwilioConferenceFriendlyName
    conversation_id: CampaignConversationReference
    total_participants: int
    remarks: str
    billing_types: Optional[List[BillingTypeEnum]]


@dataclass
class BillingResponse:
    success: bool = False
    is_sufficient_credit: bool = False
    is_call_inprogress: bool = False
    charge_amount: float = 0
