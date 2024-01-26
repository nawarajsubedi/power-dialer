from krispcall.konference.billing import constant as BillingConstant
from krispcall.common.shortid import ShortId

from krispcall.konference.billing.models import (
    BillingResponse,
    CampaignOutboundCallRequest,
)
from krispcall.konference.adapters.provider import (
    call_charge_transaction,
    get_workspace_credit,
)


class BillingService:
    async def execute_campaign_call_transaction(
        data: CampaignOutboundCallRequest,
    ) -> BillingResponse:
        try:
            workspace_credit = await get_workspace_credit(
                ShortId.with_uuid(data.workspace_id)
            )

            if not BillingService.is_sufficient_credit(workspace_credit):
                return BillingResponse(is_sufficient_credit=False, success=False)

            billing_response = await call_charge_transaction(data)

            return BillingResponse(
                is_sufficient_credit=True,
                success=billing_response.success,
                charge_amount=billing_response.payload.charge_amount,
            )
        except Exception as e:
            print("Exception", e)

    @staticmethod
    def is_sufficient_credit(workspace_credit: float) -> bool:
        return float(workspace_credit) > BillingConstant.THRESHOLD_CALL_PER_MINUTE
