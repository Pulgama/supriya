# flake8: noqa
"""
Tools for object-modeling OSC responses received from ``scsynth``.
"""

from .bases import Request, RequestBundle, Requestable, Response
from .buffers import (
    BufferAllocateReadChannelRequest,
    BufferAllocateReadRequest,
    BufferAllocateRequest,
    BufferCloseRequest,
    BufferCopyRequest,
    BufferFillRequest,
    BufferFreeRequest,
    BufferGenerateRequest,
    BufferGetContiguousRequest,
    BufferGetRequest,
    BufferInfo,
    BufferNormalizeRequest,
    BufferQueryRequest,
    BufferReadChannelRequest,
    BufferReadRequest,
    BufferSetContiguousRequest,
    BufferSetContiguousResponse,
    BufferSetRequest,
    BufferSetResponse,
    BufferWriteRequest,
    BufferZeroRequest,
)
from .buses import (
    ControlBusFillRequest,
    ControlBusGetContiguousRequest,
    ControlBusGetRequest,
    ControlBusSetContiguousRequest,
    ControlBusSetContiguousResponse,
    ControlBusSetRequest,
    ControlBusSetResponse,
)
from .groups import (
    GroupDeepFreeRequest,
    GroupDumpTreeRequest,
    GroupFreeAllRequest,
    GroupNewRequest,
    GroupQueryTreeRequest,
    ParallelGroupNewRequest,
    QueryTreeResponse,
)
from .movement import (
    GroupHeadRequest,
    GroupTailRequest,
    MoveRequest,
    NodeAfterRequest,
    NodeBeforeRequest,
)
from .nodes import (
    NodeFreeRequest,
    NodeInfoResponse,
    NodeMapToAudioBusRequest,
    NodeMapToControlBusRequest,
    NodeQueryRequest,
    NodeRunRequest,
    NodeSetContiguousResponse,
    NodeSetRequest,
    NodeSetResponse,
)
from .server import (
    ClearScheduleRequest,
    DoneResponse,
    DumpOscRequest,
    FailResponse,
    NothingRequest,
    NotifyRequest,
    QuitRequest,
    StatusRequest,
    StatusResponse,
    SyncRequest,
    SyncedResponse,
)
from .synthdefs import (
    SynthDefFreeAllRequest,
    SynthDefFreeRequest,
    SynthDefLoadDirectoryRequest,
    SynthDefLoadRequest,
    SynthDefReceiveRequest,
    SynthDefRemovedResponse,
)
from .synths import SynthNewRequest, TriggerResponse

__all__ = [
    "BufferAllocateReadChannelRequest",
    "BufferAllocateReadRequest",
    "BufferAllocateRequest",
    "BufferCloseRequest",
    "BufferCopyRequest",
    "BufferFillRequest",
    "BufferFreeRequest",
    "BufferGenerateRequest",
    "BufferGetContiguousRequest",
    "BufferGetRequest",
    "BufferInfo",
    "BufferNormalizeRequest",
    "BufferQueryRequest",
    "BufferReadChannelRequest",
    "BufferReadRequest",
    "BufferSetContiguousRequest",
    "BufferSetContiguousResponse",
    "BufferSetRequest",
    "BufferSetResponse",
    "BufferWriteRequest",
    "BufferZeroRequest",
    "ClearScheduleRequest",
    "ControlBusFillRequest",
    "ControlBusGetContiguousRequest",
    "ControlBusGetRequest",
    "ControlBusSetContiguousRequest",
    "ControlBusSetContiguousResponse",
    "ControlBusSetRequest",
    "ControlBusSetResponse",
    "DoneResponse",
    "DumpOscRequest",
    "FailResponse",
    "GroupDeepFreeRequest",
    "GroupDumpTreeRequest",
    "GroupFreeAllRequest",
    "GroupHeadRequest",
    "GroupNewRequest",
    "GroupQueryTreeRequest",
    "GroupTailRequest",
    "MoveRequest",
    "NodeAfterRequest",
    "NodeBeforeRequest",
    "NodeCommandRequest",
    "NodeFillRequest",
    "NodeFreeRequest",
    "NodeInfoResponse",
    "NodeMapToAudioBusRequest",
    "NodeMapToControlBusRequest",
    "NodeOrderRequest",
    "NodeQueryRequest",
    "NodeRunRequest",
    "NodeSetContiguousRequest",
    "NodeSetContiguousResponse",
    "NodeSetRequest",
    "NodeSetResponse",
    "NodeTraceRequest",
    "NothingRequest",
    "NotifyRequest",
    "ParallelGroupNewRequest",
    "QueryTreeResponse",
    "QuitRequest",
    "Request",
    "RequestBundle",
    "Requestable",
    "Response",
    "StatusRequest",
    "StatusResponse",
    "SyncRequest",
    "SyncedResponse",
    "SynthDefFreeAllRequest",
    "SynthDefFreeRequest",
    "SynthDefLoadDirectoryRequest",
    "SynthDefLoadRequest",
    "SynthDefReceiveRequest",
    "SynthDefRemovedResponse",
    "SynthNewRequest",
    "TriggerResponse",
]
