from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class WorkspaceCreditRequest(_message.Message):
    __slots__ = ["workspace_id"]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    workspace_id: str
    def __init__(self, workspace_id: _Optional[str] = ...) -> None: ...

class WorkspaceCreditResponse(_message.Message):
    __slots__ = ["workspace_credit"]
    WORKSPACE_CREDIT_FIELD_NUMBER: _ClassVar[int]
    workspace_credit: float
    def __init__(self, workspace_credit: _Optional[float] = ...) -> None: ...
