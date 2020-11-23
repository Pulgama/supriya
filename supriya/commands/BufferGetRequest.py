import supriya.osc
from .bases import Request
from supriya.enums import RequestId


class BufferGetRequest(Request):
    """
    A /b_get request.

    ::

        >>> import supriya.commands
        >>> request = supriya.commands.BufferGetRequest(
        ...     buffer_id=23,
        ...     indices=(0, 4, 8, 16),
        ...     )
        >>> request
        BufferGetRequest(
            buffer_id=23,
            indices=(0, 4, 8, 16),
            )

    ::

        >>> request.to_osc()
        OscMessage('/b_get', 23, 0, 4, 8, 16)

    """

    ### CLASS VARIABLES ###

    request_id = RequestId.BUFFER_GET

    ### INITIALIZER ###

    def __init__(self, buffer_id=None, indices=None):
        Request.__init__(self)
        self._buffer_id = int(buffer_id)
        self._indices = tuple(int(index) for index in indices)

    ### PUBLIC METHODS ###

    def to_osc(self, *, with_placeholders=False):
        request_id = self.request_name
        buffer_id = int(self.buffer_id)
        contents = [request_id, buffer_id]
        if self.indices:
            for index in self.indices:
                contents.append(index)
        message = supriya.osc.OscMessage(*contents)
        return message

    ### PUBLIC PROPERTIES ###

    @property
    def buffer_id(self):
        return self._buffer_id

    @property
    def indices(self):
        return self._indices

    @property
    def response_patterns(self):
        return ["/b_set", self.buffer_id], ["/fail", "/b_get"]
