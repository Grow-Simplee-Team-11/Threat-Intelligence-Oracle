from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class threatRequest(_message.Message):
    __slots__ = ["latitude", "longitude"]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    latitude: int
    longitude: int
    def __init__(self, longitude: _Optional[int] = ..., latitude: _Optional[int] = ...) -> None: ...

class threatResponse(_message.Message):
    __slots__ = ["threat"]
    THREAT_FIELD_NUMBER: _ClassVar[int]
    threat: float
    def __init__(self, threat: _Optional[float] = ...) -> None: ...
