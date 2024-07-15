import asyncio
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Dict,
    Generator,
    Generic,
    Iterator,
    List,
    Literal,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    cast,
)

try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias  # noqa

from ..contexts import AsyncServer, Buffer, BusGroup, Context, Group, Node
from ..contexts.responses import QueryTreeGroup
from ..enums import BootStatus, CalculationRate
from ..ugens import SynthDef
from ..utils import iterate_nwise

C = TypeVar("C", bound="Component")

A = TypeVar("A", bound="AllocatableComponent")

# TODO: Integrate this with channel logic
ChannelCount: TypeAlias = Literal[1, 2, 4, 8]

if TYPE_CHECKING:
    from .mixers import Mixer
    from .sessions import Session


class ComponentNames:
    ACTIVE = "active"
    CHANNEL_STRIP = "channel-strip"
    DEVICES = "devices"
    FEEDBACK = "feedback"
    GAIN = "gain"
    GROUP = "group"
    INPUT = "input"
    INPUT_LEVELS = "input-levels"
    MAIN = "main"
    OUTPUT = "output"
    OUTPUT_LEVELS = "output-levels"
    SYNTH = "synth"
    TRACKS = "tracks"


class Component(Generic[C]):

    def __init__(
        self,
        *,
        parent: Optional[C] = None,
    ) -> None:
        self._lock = asyncio.Lock()
        self._parent: Optional[C] = parent
        self._dependents: Set[Component] = set()
        self._feedback_dependents: Set[Component] = set()

    def __repr__(self) -> str:
        return f"<{type(self).__name__}>"

    def _activate(self) -> None:
        self._is_active = True

    async def _allocate_deep(self, *, context: AsyncServer) -> None:
        if self.session is None:
            raise RuntimeError
        fifo: List[Tuple[Component, int]] = []
        current_synthdefs = self.session._synthdefs[context]
        desired_synthdefs: Set[SynthDef] = set()
        for component in self._walk():
            fifo.append((component, 0))
            desired_synthdefs.update(component._get_synthdefs())
        if required_synthdefs := sorted(
            desired_synthdefs - current_synthdefs, key=lambda x: x.effective_name
        ):
            for synthdef in required_synthdefs:
                context.add_synthdefs(synthdef)
            await context.sync()
            current_synthdefs.update(required_synthdefs)
        while fifo:
            component, attempts = fifo.pop(0)
            if attempts > 2:
                raise RuntimeError(component, attempts)
            if not component._allocate(context=context):
                fifo.append((component, attempts + 1))

    def _allocate(self, *, context: AsyncServer) -> bool:
        return True

    def _deallocate(self) -> None:
        pass

    def _deallocate_deep(self) -> None:
        for component in self._walk():
            component._deallocate()

    def _deactivate(self) -> None:
        self._is_active = False

    def _delete(self) -> None:
        self._deallocate_deep()
        self._parent = None

    def _get_synthdefs(self) -> List[SynthDef]:
        return []

    def _iterate_parentage(self) -> Iterator["Component"]:
        component = self
        while component.parent is not None:
            yield component
            component = component.parent
        yield component

    def _reconcile(self, context: Optional[AsyncServer] = None) -> bool:
        return True

    def _register_dependency(self, dependent: "Component") -> None:
        self._dependents.add(dependent)

    def _register_feedback(
        self, context: Optional[AsyncServer], dependent: "Component"
    ) -> Optional[BusGroup]:
        self._dependents.add(dependent)
        self._feedback_dependents.add(dependent)
        return None

    def _unregister_dependency(self, dependent: "Component") -> bool:
        self._dependents.discard(dependent)
        return self._unregister_feedback(dependent)

    def _unregister_feedback(self, dependent: "Component") -> bool:
        had_feedback = bool(self._feedback_dependents)
        self._feedback_dependents.discard(dependent)
        return had_feedback and not self._feedback_dependents

    def _walk(
        self, component_class: Optional[Type["Component"]] = None
    ) -> Generator["Component", None, None]:
        component_class_ = component_class or Component
        if isinstance(self, component_class_):
            yield self
        for child in self.children:
            if isinstance(child, component_class_):
                yield from child._walk(component_class_)

    @property
    def address(self) -> str:
        raise NotImplementedError

    @property
    def children(self) -> List["Component"]:
        return []

    @property
    def context(self) -> Optional[AsyncServer]:
        if (mixer := self.mixer) is not None:
            return mixer.context
        return None

    @property
    def graph_order(self) -> Tuple[int, ...]:
        # TODO: Cache this
        graph_order = []
        for parent, child in iterate_nwise(reversed(list(self._iterate_parentage()))):
            graph_order.append(parent.children.index(child))
        return tuple(graph_order)

    @property
    def mixer(self) -> Optional["Mixer"]:
        # TODO: Cache this
        from .mixers import Mixer

        for component in self._iterate_parentage():
            if isinstance(component, Mixer):
                return component
        return None

    @property
    def parent(self) -> Optional[C]:
        return self._parent

    @property
    def parentage(self) -> List["Component"]:
        # TODO: Cache this
        return list(self._iterate_parentage())

    @property
    def session(self) -> Optional["Session"]:
        # TODO: Cache this
        from .sessions import Session

        for component in self._iterate_parentage():
            if isinstance(component, Session):
                return component
        return None


class AllocatableComponent(Component[C]):

    def __init__(
        self,
        *,
        parent: Optional[C] = None,
    ) -> None:
        super().__init__(parent=parent)
        self._audio_buses: Dict[str, BusGroup] = {}
        self._buffers: Dict[str, Buffer] = {}
        self._context: Optional[Context] = None
        self._control_buses: Dict[str, BusGroup] = {}
        self._is_active: bool = True
        self._nodes: Dict[str, Node] = {}

    def _activate(self) -> None:
        super()._activate()
        if group := self._nodes.get(ComponentNames.GROUP):
            group.unpause()
            group.set(active=1)

    def _can_allocate(self) -> Optional[AsyncServer]:
        if (
            context := self.context
        ) is not None and context.boot_status == BootStatus.ONLINE:
            return context
        return None

    def _deactivate(self) -> None:
        super()._deactivate()
        if group := self._nodes.get(ComponentNames.GROUP):
            group.set(active=0)

    def _deallocate(self) -> None:
        super()._deallocate()
        for key in tuple(self._audio_buses):
            self._audio_buses.pop(key).free()
        for key in tuple(self._control_buses):
            self._control_buses.pop(key).free()
        if group := self._nodes.get(ComponentNames.GROUP):
            if not self._is_active:
                group.free()
            else:
                group.set(gate=0)
        self._nodes.clear()
        for key in tuple(self._buffers):
            self._buffers.pop(key).free()

    def _get_audio_bus(
        self,
        context: Optional[AsyncServer],
        name: str,
        can_allocate: bool = False,
        channel_count: int = 2,
    ) -> BusGroup:
        return self._get_buses(
            calculation_rate=CalculationRate.AUDIO,
            can_allocate=can_allocate,
            channel_count=channel_count,
            context=context,
            name=name,
        )

    def _get_buses(
        self,
        context: Optional[AsyncServer],
        name: str,
        *,
        calculation_rate: CalculationRate,
        can_allocate: bool = False,
        channel_count: int = 1,
    ) -> BusGroup:
        if calculation_rate == CalculationRate.CONTROL:
            buses = self._control_buses
        elif calculation_rate == CalculationRate.AUDIO:
            buses = self._audio_buses
        else:
            raise ValueError(calculation_rate)
        if (name not in buses) and can_allocate and context:
            buses[name] = context.add_bus_group(
                calculation_rate=calculation_rate,
                count=channel_count,
            )
        return buses[name]

    def _get_control_bus(
        self,
        context: Optional[AsyncServer],
        name: str,
        can_allocate: bool = False,
        channel_count: int = 1,
    ) -> BusGroup:
        return self._get_buses(
            calculation_rate=CalculationRate.CONTROL,
            can_allocate=can_allocate,
            channel_count=channel_count,
            context=context,
            name=name,
        )

    async def dump_tree(self) -> QueryTreeGroup:
        if self.session and self.session.status != BootStatus.ONLINE:
            raise RuntimeError
        annotations: Dict[int, str] = {}
        tree = await cast(
            Awaitable[QueryTreeGroup],
            cast(Group, self._nodes[ComponentNames.GROUP]).dump_tree(),
        )
        for component in self._walk():
            if not isinstance(component, AllocatableComponent):
                continue
            address = component.address
            for name, node in component._nodes.items():
                annotations[node.id_] = f"{address}:{name}"
        return tree.annotate(annotations)
