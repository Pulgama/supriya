from typing import TYPE_CHECKING, List, Optional, Tuple

from ..contexts import AsyncServer, BusGroup
from ..enums import AddAction
from ..typing import DEFAULT, Default
from ..ugens import SynthDef
from .components import AllocatableComponent, Component, ComponentNames
from .devices import DeviceContainer
from .routing import Connection
from .synthdefs import CHANNEL_STRIP_2, METERS_2, PATCH_CABLE_2_2
from .tracks import Track, TrackContainer

if TYPE_CHECKING:
    from .sessions import Session


class MixerOutput(Connection["Mixer", "Mixer", Default]):
    def __init__(
        self,
        *,
        parent: "Mixer",
    ) -> None:
        super().__init__(
            name="output",
            parent=parent,
            source=parent,
            target=DEFAULT,
        )

    def _allocate_synth(
        self,
        *,
        context: AsyncServer,
        parent: AllocatableComponent,
        new_state: "Connection.State",
    ) -> None:
        self._nodes[ComponentNames.SYNTH] = parent._nodes[
            ComponentNames.GROUP
        ].add_synth(
            add_action=AddAction.ADD_TO_TAIL,
            in_=new_state.source_bus,
            out=new_state.target_bus,
            synthdef=PATCH_CABLE_2_2,
        )

    def _resolve_default_target(
        self, context: Optional[AsyncServer]
    ) -> Tuple[Optional[AllocatableComponent], Optional[BusGroup]]:
        if not context:
            return None, None
        return None, context.audio_output_bus_group


class Mixer(TrackContainer["Session"], DeviceContainer):

    # TODO: add_device() -> Device
    # TODO: group_devices(index: int, count: int) -> Rack
    # TODO: set_channel_count(self, channel_count: ChannelCount) -> None
    # TODO: set_output(output: int) -> None

    def __init__(self, *, parent: Optional["Session"]) -> None:
        AllocatableComponent.__init__(self, parent=parent)
        DeviceContainer.__init__(self)
        TrackContainer.__init__(self)
        self._tracks.append(Track(parent=self))
        self._output = MixerOutput(parent=self)

    def _allocate(self, context: AsyncServer) -> bool:
        if not super()._allocate(context=context):
            return False
        # self._audio_buses["main"] = context.add_bus_group(
        #     calculation_rate=CalculationRate.AUDIO,
        #     count=2,
        # )
        main_audio_bus = self._get_audio_bus(
            context, name=ComponentNames.MAIN, can_allocate=True
        )
        gain_control_bus = self._get_control_bus(
            context, name=ComponentNames.GAIN, can_allocate=True
        )
        input_levels_control_bus = self._get_control_bus(
            context,
            name=ComponentNames.INPUT_LEVELS,
            can_allocate=True,
            channel_count=2,
        )
        output_levels_control_bus = self._get_control_bus(
            context,
            name=ComponentNames.OUTPUT_LEVELS,
            can_allocate=True,
            channel_count=2,
        )
        target_node = context.default_group
        with context.at():
            gain_control_bus.set(0.0)
            input_levels_control_bus.set(0.0)
            output_levels_control_bus.set(0.0)
            self._nodes[ComponentNames.GROUP] = group = target_node.add_group(
                add_action=AddAction.ADD_TO_TAIL
            )
            self._nodes[ComponentNames.TRACKS] = tracks = group.add_group(
                add_action=AddAction.ADD_TO_HEAD
            )
            self._nodes[ComponentNames.DEVICES] = group.add_group(
                add_action=AddAction.ADD_TO_TAIL
            )
            self._nodes[ComponentNames.CHANNEL_STRIP] = channel_strip = group.add_synth(
                add_action=AddAction.ADD_TO_TAIL,
                bus=main_audio_bus,
                gain=gain_control_bus.map_symbol(),
                synthdef=CHANNEL_STRIP_2,
            )
            self._nodes[ComponentNames.INPUT_LEVELS] = tracks.add_synth(
                add_action=AddAction.ADD_AFTER,
                synthdef=METERS_2,
                in_=self._audio_buses[ComponentNames.MAIN],
                out=input_levels_control_bus,
            )
            self._nodes[ComponentNames.OUTPUT_LEVELS] = channel_strip.add_synth(
                add_action=AddAction.ADD_AFTER,
                synthdef=METERS_2,
                in_=self._audio_buses[ComponentNames.MAIN],
                out=output_levels_control_bus,
            )
        return True

    def _get_synthdefs(self) -> List[SynthDef]:
        return [
            CHANNEL_STRIP_2,
            METERS_2,
        ]

    async def delete(self) -> None:
        # TODO: What are delete semantics actually?
        async with self._lock:
            if self.session is not None:
                self.session._delete_mixer(self)
            self._delete()

    @property
    def address(self) -> str:
        if self.session is None:
            return "mixers[?]"
        index = self.session.mixers.index(self)
        return f"session.mixers[{index}]"

    @property
    def children(self) -> List[Component]:
        return [*self._tracks, *self._devices, self._output]

    @property
    def context(self) -> Optional[AsyncServer]:
        if self.parent is None:
            return None
        return self.parent._mixers[self]
