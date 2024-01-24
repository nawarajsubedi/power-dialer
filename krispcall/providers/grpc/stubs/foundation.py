from krispcall.providers.grpc.descriptors import foundation as foundation__pb2


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
