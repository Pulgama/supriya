import asyncio
import concurrent.futures
from os import PathLike
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Coroutine,
    Dict,
    Optional,
    Protocol,
    SupportsFloat,
    SupportsInt,
    Tuple,
    TypeVar,
    Union,
    runtime_checkable,
)

try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias  # noqa

from .enums import (
    AddAction,
    CalculationRate,
    DoneAction,
    EnvelopeShape,
    HeaderFormat,
    ParameterRate,
    SampleFormat,
)

if TYPE_CHECKING:
    import numpy

    from .osc import OscBundle, OscMessage


class Default:
    pass


DEFAULT = Default()


class Missing:
    pass


MISSING = Missing()


@runtime_checkable
class SupportsOsc(Protocol):
    def to_osc(self) -> Union["OscBundle", "OscMessage"]:
        pass


@runtime_checkable
class SupportsPlot(Protocol):
    def __plot__(self) -> "numpy.ndarray":
        pass


@runtime_checkable
class SupportsRender(Protocol):
    def __render__(
        self,
        output_file_path: Optional[PathLike] = None,
        render_directory_path: Optional[PathLike] = None,
        **kwargs,
    ) -> Coroutine[None, None, Tuple[Optional[Path], int]]:
        pass


@runtime_checkable
class SupportsRenderMemo(Protocol):
    def __render_memo__(self) -> SupportsRender:
        pass


E = TypeVar("E")

_EnumLike = Optional[Union[E, SupportsInt, str, None]]

AddActionLike: TypeAlias = _EnumLike[AddAction]
DoneActionLike: TypeAlias = _EnumLike[DoneAction]
CalculationRateLike: TypeAlias = _EnumLike[CalculationRate]
FutureLike: TypeAlias = Union[concurrent.futures.Future[E], asyncio.Future[E]]
ParameterRateLike: TypeAlias = _EnumLike[ParameterRate]
RateLike: TypeAlias = _EnumLike[CalculationRate]
EnvelopeShapeLike: TypeAlias = _EnumLike[EnvelopeShape]
HeaderFormatLike: TypeAlias = _EnumLike[HeaderFormat]
SampleFormatLike: TypeAlias = _EnumLike[SampleFormat]
UGenInputMap: TypeAlias = Optional[Dict[str, Union[SupportsFloat, str, None]]]
