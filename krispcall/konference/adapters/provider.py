# Provides sub client for the workspace
from dataclasses import dataclass
from krispcall.konference.billing.models import CampaignOutboundCallRequest
import grpc
import os
from krispcall.konference.adapters import rpc_descriptors as foundation__pb2
from krispcall.konference.adapters.protobufs import (
    workspace_credit_pb2,
    workspace_credit_pb2_grpc,
    outbound_call_pb2,
    outbound_call_pb2_grpc,
)
from krispcall.common.utils.shortid import ShortId
from krispcall.providers.rpcaddress import get_billing_rpc_address, get_foundation_rpc_address


BILLING_RPC_LOCAL_ADDRESS = "[::]:8005"
BILLING_RPC_REMOTE_ADDRESS = "krispcall-billinggrpc-service:8005"

FOUNDATION_RPC_LOCAL_ADDRESS = "[::]:8003"
FOUNDATION_RPC_REMOTE_ADDRESS = "krispcall-grpc-service:8003"


@dataclass
class PlanSubscriptionResponse:
    plan_id: str
    plan_title: str
    subscription_status: str
    success: str


class FoundationRPCStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetProviderDetails = channel.unary_unary(
            "/foundation.FoundationRPC/GetProviderDetails",
            request_serializer=foundation__pb2.WorkspaceDetails.SerializeToString,
            response_deserializer=foundation__pb2.ProviderDetails.FromString,
        )
        self.GetWorkspaceFeature = channel.unary_unary(
            "/foundation.FoundationRPC/GetWorkspaceFeature",
            request_serializer=foundation__pb2.GetWorkspaceFeatureRequest.SerializeToString,
            response_deserializer=foundation__pb2.WorkspaceFeature.FromString,
        )
        self.GetPlanSubscription = channel.unary_unary(
            "/foundation.FoundationRPC/GetPlanSubscription",
            request_serializer=foundation__pb2.PlanSubscriptionRequest.SerializeToString,
            response_deserializer=foundation__pb2.PlanSubscriptionResponse.FromString,
        )


async def get_provider_details(workspace_id: ShortId):
    """Sends requests via the grpc channel to foundation
    and fetches the provider details
    @returns
    ProviderDetails
    auth_id,
    auth_token,
    api_key,
    api_secret
    success

    """

    address = get_foundation_rpc_address()

    with grpc.insecure_channel(address) as channel:
        stub = FoundationRPCStub(channel)
        response = stub.GetProviderDetails(
            foundation__pb2.WorkspaceDetails(
                workspace_id=workspace_id,
                provider_type="twilio",
            )
        )
    return response


async def get_plan_subscription(
    workspace_id: ShortId,
) -> PlanSubscriptionResponse:
    """Sends requests via the grpc channel to subscription plan
    and fetches the workspace plan
    @returns
    PlanSubscriptionResponse
    plan_id,
    plan_title,
    subscription_status,
    success
    """

    address = get_foundation_rpc_address()

    with grpc.insecure_channel(address) as channel:
        stub = FoundationRPCStub(channel)
        response = stub.GetPlanSubscription(
            foundation__pb2.PlanSubscriptionRequest(
                workspace_id=workspace_id,
            )
        )
    return response


async def get_workspace_credit(workspace_id: ShortId) -> float:
    """Sends requests via the grpc channel to krispcall billing
    and fetches workspace credit.

    @returns
    float: workspace_credit
    """

    address = get_billing_rpc_address()

    with grpc.insecure_channel(address) as channel:
        stub = workspace_credit_pb2_grpc.WorkspaceCreditStub(channel)
        response = stub.GetWorkspaceCredit(
            workspace_credit_pb2.WorkspaceCreditRequest(
                workspace_id=workspace_id
            )
        )
    return float(response.workspace_credit)


async def call_charge_transaction(data: CampaignOutboundCallRequest):
    """Sends requests via the grpc channel to execute charge transaction"""

    try:
        address = get_billing_rpc_address()

        with grpc.insecure_channel(address) as channel:
            stub = outbound_call_pb2_grpc.CampaignOutboundCallChargeStub(
                channel
            )

            response: outbound_call_pb2.GrpcResponse = (
                stub.ExecutePaymentTransaction(
                    outbound_call_pb2.CampiagnOutboundCallRequest(
                        workspace_id=str(data.workspace_id),
                        call_sid=str(data.call_sid),
                        child_call_sid=str(data.child_call_sid),
                        conference_sid=str(data.conference_sid),
                        from_=data.from_,
                        to=data.to,
                        total_participants=data.total_participants,
                        billing_types=list(set(data.billing_types)),
                        remarks=data.remarks,
                    )
                )
            )
        return response
    except Exception as e:
        print("Exception on grpc", e)
