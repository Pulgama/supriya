import asyncio
import logging
from typing import TYPE_CHECKING, Dict, List, Optional, Set

from ..clocks import AsyncClock
from ..contexts import AsyncServer
from ..enums import BootStatus
from ..osc import find_free_port
from ..ugens import SynthDef
from .components import Component

if TYPE_CHECKING:
    from .mixers import Mixer


logger = logging.getLogger(__name__)


class Session(Component):
    """
    Top-level object.

    Contains one transport.

    Contains one or more contexts.

    Contains one or more mixers.

    Each mixer references one context.

    This supports running scsynth and supernova simultaneously via two mixers.
    """

    def __init__(self) -> None:
        from .mixers import Mixer

        super().__init__()
        self._boot_future: Optional[asyncio.Future] = None
        self._clock = AsyncClock()
        self._contexts: Dict[AsyncServer, List[Mixer]] = {}
        self._lock = asyncio.Lock()
        self._mixers: Dict[Mixer, AsyncServer] = {}
        self._quit_future: Optional[asyncio.Future] = None
        self._status = BootStatus.OFFLINE
        self._synthdefs: Dict[AsyncServer, Set[SynthDef]] = {}
        # add initial context and mixer
        self._contexts[(context := self._add_context())] = [mixer := Mixer(parent=self)]
        self._mixers[mixer] = context

    def __repr__(self) -> str:
        return f"<{type(self).__name__}>"

    def __str__(self) -> str:
        parts: List[str] = [f"<{type(self).__name__} status={self.status.name}>"]
        for context, mixers in self._contexts.items():
            parts.append(
                f"    <{type(context).__name__} address={context.options.ip_address}:{context.options.port}>"
            )
            for mixer in mixers:
                parts.extend("        " + line for line in str(mixer).splitlines())
        return "\n".join(parts)

    def _add_context(self) -> AsyncServer:
        context = AsyncServer()
        self._contexts[context] = []
        self._synthdefs[context] = set()
        return context

    def _delete_mixer(self, mixer) -> None:
        if mixer in (mixers := self._contexts.get(self._mixers.pop(mixer), [])):
            mixers.remove(mixer)

    async def add_context(self) -> AsyncServer:
        async with self._lock:
            context = self._add_context()
            if self._status == BootStatus.ONLINE:
                await context.boot(port=find_free_port())
            return context

    async def add_mixer(self, context: Optional[AsyncServer] = None) -> "Mixer":
        from .mixers import Mixer

        async with self._lock:
            if not self._contexts:
                context = self._add_context()
                if self._status == BootStatus.ONLINE:
                    await context.boot(port=find_free_port())
            if context is None:
                context = list(self._contexts)[0]
            self._contexts.setdefault(context, []).append(mixer := Mixer(parent=self))
            self._mixers[mixer] = context
            if self._status == BootStatus.ONLINE:
                await mixer._allocate_deep(context=context)
            return mixer

    async def boot(self) -> None:
        async with self._lock:
            # guard against concurrent boot / quits
            if self._status == BootStatus.OFFLINE:
                self._quit_future = None
                self._boot_future = asyncio.get_running_loop().create_future()
                self._status = BootStatus.BOOTING
                await asyncio.gather(
                    *[context.boot(port=find_free_port()) for context in self._contexts]
                )
                self._status = BootStatus.ONLINE
                self._boot_future.set_result(True)
                for context, mixers in self._contexts.items():
                    for mixer in mixers:
                        await mixer._allocate_deep(context=context)
            elif self._boot_future is not None:  # BOOTING / ONLINE
                await self._boot_future
            else:  # NONREALTIME
                raise Exception(self._status)

    async def delete_context(self, context: AsyncServer) -> None:
        async with self._lock:
            for mixer in self._contexts.pop(context):
                await mixer.delete()
            await context.quit()

    async def dump_components(self) -> str:
        return ""

    async def dump_tree(self) -> str:
        # what if components and query tree stuff was intermixed?
        # we fetch the node tree once per mixer
        # and then the node tree needs to get partitioned by subtrees
        if self.status != BootStatus.ONLINE:
            raise RuntimeError
        parts: List[str] = []
        for context, mixers in self._contexts.items():
            parts.append(repr(context))
            for mixer in mixers:
                for line in str(await mixer.dump_tree()).splitlines():
                    parts.append(f"    {line}")
        return "\n".join(parts)

    async def quit(self) -> None:
        async with self._lock:
            # guard against concurrent boot / quits
            if self._status == BootStatus.ONLINE:
                self._boot_future = None
                self._quit_future = asyncio.get_running_loop().create_future()
                self._status = BootStatus.QUITTING
                for context, mixers in self._contexts.items():
                    for mixer in mixers:
                        with context.at():
                            mixer._deallocate()
                await asyncio.gather(*[context.quit() for context in self._contexts])
                self._status = BootStatus.OFFLINE
                self._quit_future.set_result(True)
            elif self._quit_future is not None:  # QUITTING / OFFLINE
                await self._quit_future
            elif self._status == BootStatus.OFFLINE:  # Never booted
                return
            else:  # NONREALTIME
                raise Exception(self._status)

    async def set_mixer_context(self, mixer: "Mixer", context: AsyncServer) -> None:
        async with self._lock:
            if mixer not in self._mixers:
                raise ValueError(mixer)
            elif context not in self._contexts:
                raise ValueError(context)
            if mixer in self._contexts[context]:
                return
            self._contexts[self._mixers[mixer]].remove(mixer)
            async with mixer._lock:
                mixer._deallocate_deep()
                if self._status == BootStatus.ONLINE:
                    await mixer._allocate_deep(context=context)
                self._contexts[context].append(mixer)
                self._mixers[mixer] = context

    async def sync(self) -> None:
        if self._status != BootStatus.ONLINE:
            raise RuntimeError
        await asyncio.gather(*[context.sync() for context in self.contexts])

    @property
    def address(self) -> str:
        return "session"

    @property
    def children(self) -> List[Component]:
        return list(self._mixers)

    @property
    def contexts(self) -> List[AsyncServer]:
        return list(self._contexts)

    @property
    def mixers(self) -> List["Mixer"]:
        return list(self._mixers)

    @property
    def status(self) -> BootStatus:
        return self._status
