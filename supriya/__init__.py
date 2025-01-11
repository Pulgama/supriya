from pathlib import Path

import platformdirs

from ._version import __version__, __version_info__
from .clocks import (
    AsyncClock,
    AsyncOfflineClock,
    BaseClock,
    Clock,
    ClockContext,
    OfflineClock,
    TimeUnit,
)
from .contexts import (
    AsyncServer,
    BaseServer,
    Buffer,
    BufferGroup,
    Bus,
    BusGroup,
    Context,
    Group,
    Node,
    Score,
    Server,
    ServerLifecycleEvent,
    ServerShutdownEvent,
    Synth,
)
from .enums import (  # noqa
    AddAction,
    CalculationRate,
    DoneAction,
    HeaderFormat,
    ParameterRate,
    SampleFormat,
)
from .io import graph, play, plot, render
from .osc import OscBundle, OscCallback, OscMessage
from .patterns import Pattern
from .ugens import (
    Envelope,
    UGen,
    UGenVector,
    UGenOperable,
    SynthDef,
    SynthDefBuilder,
    synthdef,
)
from .assets.synthdefs import default
from .scsynth import Options


if not (
    output_path := Path(platformdirs.user_cache_dir("supriya", "supriya"))
).exists():
    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except IOError:
        pass

assets_path = Path(__file__).parent / "assets"


__all__ = [
    "AddAction",
    "AsyncClock",
    "AsyncOfflineClock",
    "AsyncServer",
    "BaseClock",
    "BaseServer",
    "Buffer",
    "BufferGroup",
    "Bus",
    "BusGroup",
    "CalculationRate",
    "Clock",
    "ClockContext",
    "Context",
    "DoneAction",
    "Envelope",
    "Group",
    "HeaderFormat",
    "Node",
    "OfflineClock",
    "Options",
    "OscBundle",
    "OscCallback",
    "OscMessage",
    "Pattern",
    "SampleFormat",
    "Score",
    "Server",
    "ServerLifecycleEvent",
    "ServerShutdownEvent",
    "Synth",
    "SynthDef",
    "SynthDefBuilder",
    "TimeUnit",
    "UGen",
    "UGenVector",
    "UGenOperable",
    "__version__",
    "__version_info__",
    "default",
    "graph",
    "output_path",
    "play",
    "plot",
    "render",
    "synthdef",
]

del Path
del platformdirs
