import os
import grpc
from google.protobuf.json_format import MessageToDict

from krispcall.common.utils.shortid import ShortId
from krispcall.providers.grpc import descriptors, stubs

BILLING_RPC_LOCAL_ADDRESS = "[::]:8005"
BILLING_RPC_REMOTE_ADDRESS = "krispcall-billinggrpc-service:8005"

FOUNDATION_RPC_LOCAL_ADDRESS = "[::]:8003"
FOUNDATION_RPC_REMOTE_ADDRESS = "krispcall-grpc-service:8003"


def get_billing_rpc_address():
    is_local_env = True if os.getenv("app_env") == "development" else False
    address = BILLING_RPC_LOCAL_ADDRESS if is_local_env else BILLING_RPC_REMOTE_ADDRESS
    return address


def get_foundation_rpc_address():
    is_local_env = True if os.getenv("app_env") == "development" else False
    address = (
        FOUNDATION_RPC_LOCAL_ADDRESS if is_local_env else FOUNDATION_RPC_REMOTE_ADDRESS
    )
    return address


async def get_workspace_feature(workspace_id: ShortId, feature_name: str):
    address = get_foundation_rpc_address()
    with grpc.insecure_channel(address) as channel:
        stub = stubs.foundation.FoundationRPCStub(channel)
        try:
            workspace_feature = stub.GetWorkspaceFeature(
                descriptors.foundation.GetWorkspaceFeatureRequest(
                    workspace_id=workspace_id, feature_name=feature_name
                )
            )
            return MessageToDict(
                workspace_feature,
                preserving_proto_field_name=True,
                including_default_value_fields=True,
            )
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND: # type: ignore
                return None
            raise e
