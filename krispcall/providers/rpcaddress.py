import os


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
