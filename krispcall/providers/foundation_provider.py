import os
import grpc
from google.protobuf.json_format import MessageToDict

from krispcall.common.utils.shortid import ShortId
from krispcall.providers.grpc import descriptors, stubs
from krispcall.providers.rpcaddress import get_foundation_rpc_address


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
            if e.code() == grpc.StatusCode.NOT_FOUND:  # type: ignore
                return None
            raise e
