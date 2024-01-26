from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

CALL_CHARGE: BillingType
CONFERENCE_CHARGE: BillingType
DESCRIPTOR: _descriptor.FileDescriptor
SIP_CHARGE: BillingType

class CampiagnOutboundCallRequest(_message.Message):
    __slots__ = [
        "billing_types",
        "call_sid",
        "child_call_sid",
        "conference_sid",
        "from_",
        "parent_call_sid",
        "remarks",
        "to",
        "total_participants",
        "workspace_id",
    ]
    BILLING_TYPES_FIELD_NUMBER: _ClassVar[int]
    CALL_SID_FIELD_NUMBER: _ClassVar[int]
    CHILD_CALL_SID_FIELD_NUMBER: _ClassVar[int]
    CONFERENCE_SID_FIELD_NUMBER: _ClassVar[int]
    FROM__FIELD_NUMBER: _ClassVar[int]
    PARENT_CALL_SID_FIELD_NUMBER: _ClassVar[int]
    REMARKS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PARTICIPANTS_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    billing_types: _containers.RepeatedScalarFieldContainer[BillingType]
    call_sid: str
    child_call_sid: str
    conference_sid: str
    from_: str
    parent_call_sid: str
    remarks: str
    to: str
    total_participants: int
    workspace_id: str
    def __init__(
        self,
        workspace_id: _Optional[str] = ...,
        from_: _Optional[str] = ...,
        to: _Optional[str] = ...,
        call_sid: _Optional[str] = ...,
        child_call_sid: _Optional[str] = ...,
        parent_call_sid: _Optional[str] = ...,
        conference_sid: _Optional[str] = ...,
        total_participants: _Optional[int] = ...,
        billing_types: _Optional[_Iterable[_Union[BillingType, str]]] = ...,
        remarks: _Optional[str] = ...,
    ) -> None: ...

class CampiagnOutboundCallResponse(_message.Message):
    __slots__ = ["charge_amount", "workspace_id"]
    CHARGE_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    charge_amount: float
    workspace_id: str
    def __init__(
        self,
        workspace_id: _Optional[str] = ...,
        charge_amount: _Optional[float] = ...,
    ) -> None: ...

class GrpcError(_message.Message):
    __slots__ = ["code", "message"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    def __init__(
        self, code: _Optional[int] = ..., message: _Optional[str] = ...
    ) -> None: ...

class GrpcResponse(_message.Message):
    __slots__ = ["error", "payload", "success"]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    error: GrpcError
    payload: CampiagnOutboundCallResponse
    success: bool
    def __init__(
        self,
        success: bool = ...,
        error: _Optional[_Union[GrpcError, _Mapping]] = ...,
        payload: _Optional[
            _Union[CampiagnOutboundCallResponse, _Mapping]
        ] = ...,
    ) -> None: ...

class BillingType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
