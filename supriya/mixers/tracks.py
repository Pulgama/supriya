from typing import List, Optional, Tuple, Union, cast

from ..contexts import AsyncServer, BusGroup
from ..enums import AddAction
from ..typing import DEFAULT, Default
from ..ugens import SynthDef
from .components import AllocatableComponent, C, Component, ComponentNames
from .devices import DeviceContainer
from .routing import Connection
from .synthdefs import CHANNEL_STRIP_2, FB_PATCH_CABLE_2_2, METERS_2, PATCH_CABLE_2_2


class TrackContainer(AllocatableComponent[C]):

    def __init__(self) -> None:
        self._tracks: List[Track] = []

    def _delete_track(self, track: "Track") -> None:
        self._tracks.remove(track)

    async def add_track(self) -> "Track":
        async with self._lock:
            self._tracks.append(track := Track(parent=self))
            if context := self._can_allocate():
                await track._allocate_deep(context=context)
            return track

    @property
    def tracks(self) -> List["Track"]:
        return self._tracks[:]


class TrackFeedback(Connection["Track", BusGroup, "Track"]):
    def __init__(
        self,
        *,
        parent: "Track",
        source: Optional[BusGroup] = None,
    ) -> None:
        super().__init__(
            name="feedback",
            parent=parent,
            source=source,
            target=parent,
        )

    def _allocate_synth(
        self,
        *,
        context: AsyncServer,
        parent: AllocatableComponent,
        new_state: Connection.State,
    ) -> None:
        self._nodes[ComponentNames.SYNTH] = parent._nodes[
            ComponentNames.GROUP
        ].add_synth(
            active=parent._control_buses[ComponentNames.ACTIVE].map_symbol(),
            add_action=AddAction.ADD_TO_HEAD,
            in_=new_state.source_bus,
            out=new_state.target_bus,
            synthdef=FB_PATCH_CABLE_2_2,
        )


class TrackInput(Connection["Track", Union[BusGroup, TrackContainer], "Track"]):

    def __init__(
        self,
        *,
        parent: "Track",
        source: Optional[Union[BusGroup, "Track"]] = None,
    ) -> None:
        super().__init__(
            name="input",
            parent=parent,
            source=source,
            target=parent,
        )

    def _allocate_synth(
        self,
        *,
        context: AsyncServer,
        parent: AllocatableComponent,
        new_state: Connection.State,
    ) -> None:
        self._nodes[ComponentNames.SYNTH] = parent._nodes[
            ComponentNames.TRACKS
        ].add_synth(
            active=parent._control_buses[ComponentNames.ACTIVE].map_symbol(),
            add_action=AddAction.ADD_BEFORE,
            in_=new_state.source_bus,
            out=new_state.target_bus,
            synthdef=PATCH_CABLE_2_2,
        )

    async def set_source(self, source: Optional[Union[BusGroup, "Track"]]) -> None:
        async with self._lock:
            if source is self.parent:
                raise RuntimeError
            self._set_source(source)


class TrackOutput(
    Connection["Track", "Track", Union[BusGroup, Default, TrackContainer]]
):

    def __init__(
        self,
        *,
        parent: "Track",
        target: Optional[Union[BusGroup, Default, TrackContainer]] = DEFAULT,
    ) -> None:
        super().__init__(
            name="output",
            parent=parent,
            source=parent,
            target=target,
        )

    def _resolve_default_target(
        self, context: Optional[AsyncServer]
    ) -> Tuple[Optional[AllocatableComponent], Optional[BusGroup]]:
        return (self.parent and self.parent.parent), None

    async def set_target(
        self, target: Optional[Union[BusGroup, Default, TrackContainer]]
    ) -> None:
        async with self._lock:
            if target is self.parent:
                raise RuntimeError
            self._set_target(target)


class TrackSend(Connection["Track", "Track", TrackContainer]):
    def __init__(
        self,
        *,
        parent: "Track",
        target: TrackContainer,
        postfader: bool = True,
    ) -> None:
        super().__init__(
            name="send",
            parent=parent,
            postfader=postfader,
            source=parent,
            target=target,
        )

    def _allocate_synth(
        self,
        *,
        context: AsyncServer,
        parent: AllocatableComponent,
        new_state: Connection.State,
    ) -> None:
        self._nodes[ComponentNames.SYNTH] = parent._nodes[
            ComponentNames.CHANNEL_STRIP
        ].add_synth(
            active=parent._control_buses[ComponentNames.ACTIVE].map_symbol(),
            add_action=(
                AddAction.ADD_AFTER if new_state.postfader else AddAction.ADD_BEFORE
            ),
            in_=new_state.source_bus,
            out=new_state.target_bus,
            synthdef=PATCH_CABLE_2_2,
        )

    def _resolve_default_source(
        self, context: Optional[AsyncServer]
    ) -> Tuple[Optional[AllocatableComponent], Optional[BusGroup]]:
        return self.parent, None

    async def delete(self) -> None:
        async with self._lock:
            if self._parent is not None and self in self._parent._sends:
                self._parent._sends.remove(self)
            self._delete()

    async def set_postfader(self, postfader: bool) -> None:
        async with self._lock:
            self._set_postfader(postfader)

    async def set_target(self, target: TrackContainer) -> None:
        async with self._lock:
            if target is self.parent:
                raise RuntimeError
            self._set_target(target)

    @property
    def address(self) -> str:
        if self.parent is None:
            return "sends[?]"
        index = self.parent.sends.index(self)
        return f"{self.parent.address}.sends[{index}]"

    @property
    def postfader(self) -> bool:
        return self._postfader

    @property
    def target(self) -> Union[AllocatableComponent, BusGroup]:
        # TODO: Can this be parameterized via generics?
        return cast(Union[AllocatableComponent, BusGroup], self._target)


class Track(TrackContainer[TrackContainer], DeviceContainer):

    # TODO: add_device() -> Device
    # TODO: add_send(destination: Track) -> Send
    # TODO: group_devices(index: int, count: int) -> Rack
    # TODO: group_tracks(index: int, count: int) -> Track
    # TODO: set_channel_count(self, channel_count: Optional[ChannelCount] = None) -> None
    # TODO: set_input(None | Default | Track | BusGroup)

    def __init__(
        self,
        *,
        parent: Optional[TrackContainer] = None,
    ) -> None:
        AllocatableComponent.__init__(self, parent=parent)
        DeviceContainer.__init__(self)
        TrackContainer.__init__(self)
        self._feedback = TrackFeedback(parent=self)
        self._input = TrackInput(parent=self)
        self._output = TrackOutput(parent=self)
        # TODO: Are sends the purview of track containers in general?
        self._sends: List[TrackSend] = []

    def _allocate(self, *, context: AsyncServer) -> bool:
        if not super()._allocate(context=context):
            return False
        elif self.parent is None:
            raise RuntimeError
        main_audio_bus = self._get_audio_bus(
            context, name=ComponentNames.MAIN, can_allocate=True
        )
        active_control_bus = self._get_control_bus(
            context, name=ComponentNames.ACTIVE, can_allocate=True
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
        target_node = self.parent._nodes[ComponentNames.TRACKS]
        with context.at():
            active_control_bus.set(1.0)
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
                active=active_control_bus.map_symbol(),
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

    def _register_feedback(
        self, context: Optional[AsyncServer], dependent: "Component"
    ) -> Optional[BusGroup]:
        super()._register_feedback(context, dependent)
        # check if feedback should be setup
        if not context:
            return None
        if self._feedback_dependents:
            self._feedback._set_source(
                self._get_audio_bus(
                    context, name=ComponentNames.FEEDBACK, can_allocate=True
                )
            )
        return self._get_audio_bus(context, name=ComponentNames.FEEDBACK)

    def _unregister_feedback(self, dependent: "Component") -> bool:
        if should_tear_down := super()._unregister_feedback(dependent):
            # check if feedback should be torn down
            if bus_group := self._audio_buses.get(ComponentNames.FEEDBACK):
                bus_group.free()
            self._feedback._set_source(None)
        return should_tear_down

    async def add_send(
        self, target: TrackContainer, postfader: bool = True
    ) -> TrackSend:
        async with self._lock:
            self._sends.append(
                send := TrackSend(parent=self, postfader=postfader, target=target)
            )
            if context := self._can_allocate():
                await send._allocate_deep(context=context)
            return send

    async def delete(self) -> None:
        # TODO: What are delete semantics actually?
        async with self._lock:
            if self._parent is not None:
                self._parent._delete_track(self)
            self._delete()

    async def move(self, parent: TrackContainer, index: int) -> None:
        async with self._lock:
            # Validate if moving is possible
            if self.mixer is not parent.mixer:
                raise RuntimeError
            elif self in parent.parentage:
                raise RuntimeError
            elif index < 0 or index > len(parent.tracks):
                raise RuntimeError
            # Reconfigure parentage and bail if this is a no-op
            old_parent, old_index = self._parent, 0
            if old_parent is not None:
                old_index = old_parent._tracks.index(self)
            if old_parent is parent and old_index == index:
                return  # Bail
            if old_parent is not None:
                old_parent._tracks.remove(self)
            self._parent = parent
            parent._tracks.insert(index, self)
            # Apply changes against the context
            if (context := self._can_allocate()) is not None:
                if index == 0:
                    node_id = self._parent._nodes[ComponentNames.TRACKS]
                    add_action = AddAction.ADD_TO_HEAD
                else:
                    node_id = self._parent._tracks[index - 1]._nodes[
                        ComponentNames.GROUP
                    ]
                    add_action = AddAction.ADD_AFTER
                with context.at():
                    self._nodes[ComponentNames.GROUP].move(
                        target_node=node_id, add_action=add_action
                    )
            for component in self._dependents:
                component._reconcile(context)

    async def set_active(self, active: bool = True) -> None:
        async with self._lock:
            pass

    async def set_input(self, input_: Optional[Union[BusGroup, "Track"]]) -> None:
        await self._input.set_source(input_)

    async def set_output(
        self, output: Optional[Union[Default, TrackContainer]]
    ) -> None:
        await self._output.set_target(output)

    async def set_soloed(self, soloed: bool = True, exclusive: bool = True) -> None:
        async with self._lock:
            pass

    async def ungroup(self) -> None:
        async with self._lock:
            pass

    @property
    def address(self) -> str:
        if self.parent is None:
            return "tracks[?]"
        index = self.parent.tracks.index(self)
        return f"{self.parent.address}.tracks[{index}]"

    @property
    def children(self) -> List[Component]:
        prefader_sends = []
        postfader_sends = []
        for send in self._sends:
            if send.postfader:
                postfader_sends.append(send)
            else:
                prefader_sends.append(send)
        return [
            self._feedback,
            self._input,
            *self._tracks,
            *self._devices,
            *prefader_sends,
            self._output,
            *postfader_sends,
        ]

    @property
    def input_(self) -> Optional[Union[BusGroup, TrackContainer]]:
        return self._input._source

    @property
    def output(self) -> Optional[Union[BusGroup, Default, TrackContainer]]:
        return self._output._target

    @property
    def sends(self) -> List[TrackSend]:
        return self._sends[:]
