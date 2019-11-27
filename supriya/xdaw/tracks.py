import abc
from types import MappingProxyType
from typing import List, Optional, Set, Tuple, Type
from uuid import UUID, uuid4

import supriya.xdaw  # noqa
from supriya.enums import AddAction, CalculationRate
from supriya.synthdefs import SynthDefFactory
from supriya.typing import Default
from supriya.ugens import In

from .bases import Allocatable, AllocatableContainer, Mixer
from .clips import Slot
from .devices import DeviceObject
from .sends import Receive, Send, Target
from .synthdefs import (
    build_peak_rms_synthdef,
    gain_block,
    gate_block,
    hard_gate_block,
    sanitize_block,
)


class TrackObject(Allocatable):

    ### INITIALIZER ###

    def __init__(self, *, channel_count=None, name=None, uuid=None):
        Allocatable.__init__(self, channel_count=channel_count, name=name)
        self._uuid = uuid or uuid4()
        self._peak_levels = {}
        self._rms_levels = {}
        self._soloed_tracks: Set[TrackObject] = set()
        self._devices = AllocatableContainer(
            "input_levels", AddAction.ADD_AFTER, label="Devices"
        )
        self._postfader_sends = AllocatableContainer(
            "output", AddAction.ADD_AFTER, label="PostFaderSends"
        )
        self._prefader_sends = AllocatableContainer(
            "output", AddAction.ADD_BEFORE, label="PreFaderSends"
        )
        self._receive_target = Target(label="ReceiveTarget")
        self._receives = AllocatableContainer(
            "parameters", AddAction.ADD_AFTER, label="Receives"
        )
        self._send_target = Target(label="SendTarget")
        self._mutate(
            slice(None),
            [
                self._send_target,
                self._receives,
                self._devices,
                self._prefader_sends,
                self._postfader_sends,
                self._receive_target,
            ],
        )

    ### SPECIAL METHODS ###

    def __str__(self):
        line = f"<{type(self).__name__} [...] {self.uuid}>"
        if self.node_proxy is not None:
            line = f"<{type(self).__name__} [{int(self.node_proxy)}] {self.uuid}>"
        lines = [line]
        for child in self:
            for line in str(child).splitlines():
                lines.append(f"    {line}")
        return "\n".join(lines)

    ### PRIVATE METHODS ###

    def _activate(self):
        Allocatable._activate(self)
        if not self.provider:
            return
        self.node_proxies["output"]["active"] = 1

    def _allocate(self, provider, target_node, add_action):
        Allocatable._allocate(self, provider, target_node, add_action)
        channel_count = self.effective_channel_count
        self._node_proxies["node"] = provider.add_group(
            target_node=target_node, add_action=add_action, name=self.label
        )
        self._node_proxies["parameters"] = provider.add_group(
            target_node=self.node_proxy,
            add_action=AddAction.ADD_TO_HEAD,
            name="Parameters",
        )
        self._allocate_audio_buses(provider, channel_count)
        self._allocate_synths(
            provider,
            channel_count,
            input_pair=(self.node_proxy, AddAction.ADD_TO_TAIL),
            input_levels_pair=(self.node_proxy, AddAction.ADD_TO_TAIL),
            prefader_levels_pair=(self.node_proxy, AddAction.ADD_TO_TAIL),
            output_pair=(self.node_proxy, AddAction.ADD_TO_TAIL),
            postfader_levels_pair=(self.node_proxy, AddAction.ADD_TO_TAIL),
        )
        self._allocate_osc_callbacks(provider)

    def _allocate_audio_buses(self, provider, channel_count):
        self._audio_bus_proxies["input"] = provider.add_bus_group(
            calculation_rate=CalculationRate.AUDIO,
            channel_count=self.effective_channel_count,
        )
        self._audio_bus_proxies["output"] = provider.add_bus_group(
            calculation_rate=CalculationRate.AUDIO,
            channel_count=self.effective_channel_count,
        )

    def _allocate_synths(
        self,
        provider,
        channel_count,
        *,
        input_pair=None,
        input_levels_pair=None,
        prefader_levels_pair=None,
        output_pair=None,
        postfader_levels_pair=None,
    ):
        input_target, input_action = input_pair
        self._node_proxies["input"] = provider.add_synth(
            add_action=input_action,
            in_=self._audio_bus_proxies["input"],
            out=self._audio_bus_proxies["output"],
            synthdef=self.build_input_synthdef(channel_count),
            target_node=input_target,
            name="Input",
        )
        input_levels_target, input_levels_action = input_levels_pair
        self._node_proxies["input_levels"] = provider.add_synth(
            add_action=input_levels_action,
            out=self._audio_bus_proxies["output"],
            synthdef=build_peak_rms_synthdef(channel_count),
            target_node=input_levels_target,
            name="InputLevel",
        )
        prefader_levels_target, prefader_levels_action = prefader_levels_pair
        self._node_proxies["prefader_levels"] = provider.add_synth(
            add_action=prefader_levels_action,
            out=self._audio_bus_proxies["output"],
            synthdef=build_peak_rms_synthdef(channel_count),
            target_node=prefader_levels_target,
            name="PrefaderLevels",
        )
        output_target, output_action = output_pair
        self._node_proxies["output"] = provider.add_synth(
            active=self.is_active,
            add_action=output_action,
            out=self._audio_bus_proxies["output"],
            synthdef=self.build_output_synthdef(channel_count),
            target_node=output_target,
            name="Output",
        )
        postfader_levels_target, postfader_levels_action = postfader_levels_pair
        self._node_proxies["postfader_levels"] = provider.add_synth(
            add_action=postfader_levels_action,
            out=self._audio_bus_proxies["output"],
            synthdef=build_peak_rms_synthdef(channel_count),
            target_node=postfader_levels_target,
            name="PostfaderLevels",
        )

    def _allocate_osc_callbacks(self, provider):
        self._osc_callback_proxies["input"] = provider.register_osc_callback(
            pattern=["/levels", self.node_proxies["input_levels"].identifier],
            procedure=lambda osc_message: self._update_levels("input", osc_message),
        )
        self._osc_callback_proxies["prefader"] = provider.register_osc_callback(
            pattern=["/levels", self.node_proxies["prefader_levels"].identifier],
            procedure=lambda osc_message: self._update_levels("prefader", osc_message),
        )
        self._osc_callback_proxies["postfader"] = provider.register_osc_callback(
            pattern=["/levels", self.node_proxies["postfader_levels"].identifier],
            procedure=lambda osc_message: self._update_levels("postfader", osc_message),
        )

    def _deactivate(self):
        Allocatable._deactivate(self)
        if not self.provider:
            return
        self.node_proxies["output"]["active"] = 0

    def _perform_input(self):
        pass

    def _perform_output(self):
        pass

    def _reallocate(self, difference):
        channel_count = self.effective_channel_count
        # buses
        input_bus_group = self._audio_bus_proxies.pop("input")
        output_bus_group = self._audio_bus_proxies.pop("output")
        for bus_group in [input_bus_group, output_bus_group]:
            bus_group.free()
        self._allocate_audio_buses(self.provider, channel_count)
        # synths
        input_synth = self._node_proxies.pop("input")
        input_levels_synth = self._node_proxies.pop("input_levels")
        prefader_levels_synth = self._node_proxies.pop("prefader_levels")
        output_synth = self._node_proxies.pop("output")
        postfader_levels_synth = self._node_proxies.pop("postfader_levels")
        self._allocate_synths(
            self.provider,
            self.effective_channel_count,
            input_pair=(input_synth, AddAction.ADD_AFTER),
            input_levels_pair=(input_levels_synth, AddAction.ADD_AFTER),
            prefader_levels_pair=(prefader_levels_synth, AddAction.ADD_AFTER),
            output_pair=(output_synth, AddAction.ADD_AFTER),
            postfader_levels_pair=(postfader_levels_synth, AddAction.ADD_AFTER),
        )
        for synth in [
            input_synth,
            input_levels_synth,
            prefader_levels_synth,
            output_synth,
            postfader_levels_synth,
        ]:
            synth.free()
        # osc callbacks
        input_callback = self._osc_callback_proxies.pop("input")
        prefader_callback = self._osc_callback_proxies.pop("prefader")
        postfader_callback = self._osc_callback_proxies.pop("postfader")
        for osc_callback in [input_callback, prefader_callback, postfader_callback]:
            osc_callback.unregister()
        self._allocate_osc_callbacks(self.provider)

    def _reconcile_dependents(self):
        for send in sorted(self.send_target._dependencies, key=lambda x: x.graph_order):
            send._reconcile()

    def _update_levels(self, key, osc_message):
        levels = list(osc_message.contents[2:])
        peak, rms = [], []
        while levels:
            peak.append(levels.pop(0))
            rms.append(levels.pop(0))
        self._peak_levels[key] = tuple(peak)
        self._rms_levels[key] = tuple(rms)

    ### PUBLIC METHODS ###

    def add_device(self, device_class: Type[DeviceObject], **kwargs):
        with self.lock([self]):
            device = device_class(**kwargs)
            self.devices._append(device)
            return device

    def add_send(self, target, postfader=True):
        with self.lock([self]):
            send = Send(target)
            if postfader:
                self.postfader_sends._append(send)
            else:
                self.prefader_sends._append(send)
            if send.effective_target is not None:
                send.effective_target.send_target._dependencies.add(send)
            return send

    def add_receive(self, source):
        with self.lock([self]):
            receive = Receive(source)
            self.receives._append(receive)
            if receive.effective_source is not None:
                receive.effective_source.receive_target._dependencies.add(receive)
            return receive

    @classmethod
    def build_input_synthdef(cls, channel_count):
        """
        Build track input SynthDef.

        ::

            >>> synthdef = TrackObject.build_input_synthdef(channel_count=1)
            >>> print(synthdef)
            synthdef:
                name: mixer/track-input/1
                ugens:
                -   Control.ir: null
                -   InFeedback.ar:
                        bus: Control.ir[0:in_]
                -   In.ar:
                        bus: Control.ir[1:out]
                -   BinaryOpUGen(ADDITION).ar:
                        left: In.ar[0]
                        right: InFeedback.ar[0]
                -   Control.kr: null
                -   Linen.kr/0:
                        attack_time: Control.kr[3:lag]
                        done_action: 0.0
                        gate: Control.kr[0:active]
                        release_time: Control.kr[3:lag]
                        sustain_level: 1.0
                -   Linen.kr/1:
                        attack_time: Control.kr[3:lag]
                        done_action: 2.0
                        gate: Control.kr[2:gate]
                        release_time: Control.kr[3:lag]
                        sustain_level: 1.0
                -   BinaryOpUGen(MULTIPLICATION).ar/0:
                        left: BinaryOpUGen(ADDITION).ar[0]
                        right: Linen.kr/1[0]
                -   BinaryOpUGen(MULTIPLICATION).ar/1:
                        left: BinaryOpUGen(MULTIPLICATION).ar/0[0]
                        right: Linen.kr/0[0]
                -   UnaryOpUGen(DB_TO_AMPLITUDE).kr:
                        source: Control.kr[1:gain]
                -   BinaryOpUGen(GREATER_THAN).kr:
                        left: Control.kr[1:gain]
                        right: -96.0
                -   BinaryOpUGen(MULTIPLICATION).kr:
                        left: UnaryOpUGen(DB_TO_AMPLITUDE).kr[0]
                        right: BinaryOpUGen(GREATER_THAN).kr[0]
                -   Lag.kr:
                        lag_time: Control.kr[3:lag]
                        source: BinaryOpUGen(MULTIPLICATION).kr[0]
                -   BinaryOpUGen(MULTIPLICATION).ar/2:
                        left: BinaryOpUGen(MULTIPLICATION).ar/1[0]
                        right: Lag.kr[0]
                -   ReplaceOut.ar:
                        bus: Control.ir[1:out]
                        source[0]: BinaryOpUGen(MULTIPLICATION).ar/2[0]

        """

        def in_signal_block(builder, source, state):
            return (
                In.ar(bus=builder["out"], channel_count=state["channel_count"]) + source
            )

        factory = (
            SynthDefFactory(active=1, gain=0, gate=1, lag=0.01)
            .with_output(replacing=True)
            .with_input(feedback=True, private=True)
            .with_channel_count(channel_count)
            .with_signal_block(in_signal_block)
            .with_signal_block(gate_block)
            .with_signal_block(gain_block)
        )
        return factory.build(name=f"mixer/track-input/{channel_count}")

    @classmethod
    def build_output_synthdef(cls, channel_count):
        """
        Build track output SynthDef.

        ::

            >>> synthdef = TrackObject.build_output_synthdef(channel_count=1)
            >>> print(synthdef)
            synthdef:
                name: mixer/track-output/1
                ugens:
                -   Control.ir: null
                -   In.ar:
                        bus: Control.ir[0:out]
                -   Control.kr: null
                -   Linen.kr/0:
                        attack_time: Control.kr[4:lag]
                        done_action: 0.0
                        gate: Control.kr[0:active]
                        release_time: Control.kr[4:lag]
                        sustain_level: 1.0
                -   Linen.kr/1:
                        attack_time: Control.kr[4:lag]
                        done_action: 2.0
                        gate: Control.kr[2:gate]
                        release_time: Control.kr[4:lag]
                        sustain_level: 1.0
                -   BinaryOpUGen(MULTIPLICATION).ar/0:
                        left: In.ar[0]
                        right: Linen.kr/1[0]
                -   Linen.kr/2:
                        attack_time: Control.kr[4:lag]
                        done_action: 14.0
                        gate: Control.kr[3:hard_gate]
                        release_time: Control.kr[4:lag]
                        sustain_level: 1.0
                -   BinaryOpUGen(MULTIPLICATION).ar/1:
                        left: BinaryOpUGen(MULTIPLICATION).ar/0[0]
                        right: Linen.kr/2[0]
                -   BinaryOpUGen(MULTIPLICATION).ar/2:
                        left: BinaryOpUGen(MULTIPLICATION).ar/1[0]
                        right: Linen.kr/0[0]
                -   UnaryOpUGen(DB_TO_AMPLITUDE).kr:
                        source: Control.kr[1:gain]
                -   BinaryOpUGen(GREATER_THAN).kr:
                        left: Control.kr[1:gain]
                        right: -96.0
                -   BinaryOpUGen(MULTIPLICATION).kr:
                        left: UnaryOpUGen(DB_TO_AMPLITUDE).kr[0]
                        right: BinaryOpUGen(GREATER_THAN).kr[0]
                -   Lag.kr:
                        lag_time: Control.kr[4:lag]
                        source: BinaryOpUGen(MULTIPLICATION).kr[0]
                -   BinaryOpUGen(MULTIPLICATION).ar/3:
                        left: BinaryOpUGen(MULTIPLICATION).ar/2[0]
                        right: Lag.kr[0]
                -   Sanitize.ar:
                        replace: 0.0
                        source: BinaryOpUGen(MULTIPLICATION).ar/3[0]
                -   ReplaceOut.ar:
                        bus: Control.ir[0:out]
                        source[0]: Sanitize.ar[0]

        """
        factory = (
            SynthDefFactory(active=1, gain=0, gate=1, hard_gate=1, lag=0.01)
            .with_output(replacing=True)
            .with_input()
            .with_channel_count(channel_count)
            .with_signal_block(hard_gate_block)
            .with_signal_block(gain_block)
            .with_signal_block(sanitize_block)
        )
        return factory.build(name=f"mixer/track-output/{channel_count}")

    def perform(self, moment, in_midi_messages):
        with self.lock([self]):
            if not self.devices:
                return

    def remove_devices(self, *devices: DeviceObject):
        with self.lock([self, *devices]):
            if not all(device in self.devices for device in devices):
                raise ValueError(devices)
            for device in devices:
                self.devices._remove(device)

    def remove_sends(self, *sends: Send):
        with self.lock([self, *sends]):
            if not all(
                send in self.prefader_sends or send in self.postfader_sends
                for send in sends
            ):
                raise ValueError(sends)
            for send in sends:
                if send in self.prefader_sends:
                    self.prefader_sends._remove(send)
                else:
                    self.postfader_sends._remove(send)
                if send.effective_target is not None:
                    send.effective_target.send_target._dependencies.remove(send)

    def set_channel_count(self, channel_count: Optional[int]):
        with self.lock([self]):
            if channel_count is not None:
                assert 1 <= channel_count <= 8
                channel_count = int(channel_count)
            self._set(channel_count=channel_count)

    ### PUBLIC PROPERTIES ###

    @property
    def devices(self) -> AllocatableContainer:
        return self._devices

    @property
    def mixer(self) -> Optional[Mixer]:
        for parent in self.parentage:
            if isinstance(parent, Mixer):
                return parent
        return None

    @property
    def peak_levels(self):
        return MappingProxyType(self._peak_levels)

    @property
    def rms_levels(self):
        return MappingProxyType(self._rms_levels)

    @property
    def prefader_sends(self) -> AllocatableContainer:
        return self._prefader_sends

    @property
    def postfader_sends(self) -> AllocatableContainer:
        return self._postfader_sends

    @property
    def receive_target(self) -> Target:
        return self._receive_target

    @property
    def receives(self) -> AllocatableContainer:
        return self._receives

    @property
    def send_target(self) -> Target:
        return self._send_target

    @property
    def uuid(self) -> UUID:
        return self._uuid


class CueTrack(TrackObject):
    def __init__(self, *, uuid=None):
        TrackObject.__init__(self, channel_count=2, uuid=uuid)


class MasterTrack(TrackObject):
    def __init__(self, *, uuid=None):
        TrackObject.__init__(self, uuid=uuid)


class UserTrackObject(TrackObject):

    ### INITIALIZER ###

    def __init__(self, *, channel_count=None, name=None, uuid=None):
        TrackObject.__init__(self, channel_count=channel_count, name=name, uuid=uuid)
        self._is_cued = False
        self._is_muted = False
        self._is_soloed = False

    ### PUBLIC METHODS ###

    def cue(self):
        with self.lock([self]):
            pass

    def delete(self):
        with self.lock([self]):
            if self.parent is None:
                raise ValueError
            self.parent._remove(self)

    def duplicate(self):
        with self.lock([self]):
            pass

    def mute(self):
        with self.lock([self]):
            if self.is_muted:
                return
            self._is_muted = True
            self._update_activation(self)

    @abc.abstractmethod
    def solo(self, exclusive=True):
        raise NotImplementedError

    def uncue(self):
        with self.lock([self]):
            pass

    def unmute(self):
        with self.lock([self]):
            if not self.is_muted:
                return
            self._is_muted = False
            self._update_activation(self)

    @abc.abstractmethod
    def unsolo(self, exclusive=False):
        raise NotImplementedError

    ### PUBLIC PROPERTIES ###

    @property
    def is_cued(self) -> bool:
        return self._is_cued

    @property
    def is_muted(self) -> bool:
        return self._is_muted

    @property
    def is_soloed(self) -> bool:
        return self._is_soloed


class Track(UserTrackObject):

    ### INITIALIZER ###

    def __init__(self, *, channel_count=None, name=None, uuid=None):
        UserTrackObject.__init__(
            self, channel_count=channel_count, name=name, uuid=uuid
        )
        self._tracks = TrackContainer("input", AddAction.ADD_AFTER, label="SubTracks")
        self._slots: List[Slot, ...] = []
        self._mutate(slice(0, 0), [self._tracks])
        self.add_send(Default())

    ### PRIVATE METHODS ###

    def _cleanup(self):
        Track._update_activation(self)

    @classmethod
    def _recurse_activation(
        cls,
        track,
        any_tracks_are_soloed=False,
        tree_is_muted=False,
        tree_is_soloed=False,
    ):
        to_activate, to_deactivate = [], []
        should_mute = bool(tree_is_muted or track.is_muted)
        should_solo = bool(tree_is_soloed or track._soloed_tracks)
        active = True
        if any_tracks_are_soloed:
            active = should_solo
        if should_mute:
            active = False
        if not track.is_active and active:
            to_activate.append(track)
        elif track.is_active and not active:
            to_deactivate.append(track)
        for child in track.tracks:
            result = cls._recurse_activation(
                child,
                any_tracks_are_soloed=any_tracks_are_soloed,
                tree_is_muted=should_mute,
                tree_is_soloed=tree_is_soloed or track.is_soloed,
            )
            to_activate.extend(result[0])
            to_deactivate.extend(result[1])
        return to_activate, to_deactivate

    def _set_parent(self, new_parent):
        from .contexts import Context

        if self.is_soloed:
            for node in self.parentage:
                if isinstance(node, (UserTrackObject, Context)):
                    node._soloed_tracks.remove(self)
        UserTrackObject._set_parent(self, new_parent)
        if self.is_soloed:
            for node in self.parentage:
                if isinstance(node, (UserTrackObject, Context)):
                    node._soloed_tracks.add(self)

    @classmethod
    def _update_activation(cls, object_):
        from .contexts import Context

        parentage = [
            x for x in object_.parentage if isinstance(x, (UserTrackObject, Context))
        ]
        any_tracks_are_soloed = bool(parentage[-1]._soloed_tracks)
        if isinstance(parentage[-1], Context):
            to_activate, to_deactivate = [], []
            for track in parentage[-1].tracks:
                result = Track._recurse_activation(
                    track, any_tracks_are_soloed=any_tracks_are_soloed
                )
                to_activate.extend(result[0])
                to_deactivate.extend(result[1])
        else:
            to_activate, to_deactivate = Track._recurse_activation(
                parentage[-1], any_tracks_are_soloed=any_tracks_are_soloed
            )
        for track in to_activate:
            track._activate()
        for track in to_deactivate:
            track._deactivate()

    ### PUBLIC METHODS ###

    def add_track(self, *, name=None):
        with self.lock([self]):
            track = Track(name=name)
            self._tracks._append(track)
            return track

    @classmethod
    def group(cls, tracks, *, name=None):
        with cls.lock(tracks):
            group_track = Track(name=name)
            if tracks[0].parent:
                index = tracks[0].parent.index(tracks[0])
                tracks[0].parent._mutate(slice(index, index), [group_track])
                group_track.add_send(Default())
            group_track.tracks._mutate(slice(None), tracks)
            return group_track

    def move(self, container, position):
        with self.lock([self, container]):
            container.tracks._mutate(slice(position, position), [self])

    def remove_tracks(self, *tracks: "Track"):
        with self.lock([self, *tracks]):
            if not all(track in self.tracks for track in tracks):
                raise ValueError
            for track in tracks:
                self._tracks._remove(track)

    def solo(self, exclusive=True):
        from .contexts import Context

        with self.lock([self]):
            if self.is_soloed:
                return
            parentage = [
                x for x in self.parentage if isinstance(x, (UserTrackObject, Context))
            ]
            self._is_soloed = True
            if exclusive:
                for track in tuple(parentage[-1]._soloed_tracks):
                    track._is_soloed = False
                    for node in track.parentage:
                        if isinstance(node, (UserTrackObject, Context)):
                            node._soloed_tracks.remove(track)
            for node in parentage:
                node._soloed_tracks.add(self)
            self._update_activation(self)

    def ungroup(self):
        with self.lock([self]):
            if self.parent:
                index = self.parent.index(self)
                self.parent._mutate(slice(index, index + 1), self.tracks[:])
            else:
                self.tracks._mutate(slice(None), [])

    def unsolo(self, exclusive=False):
        from .contexts import Context

        with self.lock([self]):
            if not self.is_soloed:
                return
            parentage = [
                x for x in self.parentage if isinstance(x, (UserTrackObject, Context))
            ]
            if exclusive:
                tracks = (self,)
            else:
                tracks = tuple(parentage[-1]._soloed_tracks)
            for track in tracks:
                track._is_soloed = False
                for node in track.parentage:
                    if isinstance(node, (UserTrackObject, Context)):
                        node._soloed_tracks.remove(track)
            self._update_activation(self)

    ### PUBLIC PROPERTIES ###

    @property
    def default_send_target(self):
        for parent in self.parentage[1:]:
            if hasattr(parent, "tracks"):
                if hasattr(parent, "master_track"):
                    return parent.master_track
                return parent

    @property
    def slots(self) -> Tuple[Slot, ...]:
        return tuple(self._slots)

    @property
    def tracks(self) -> "TrackContainer":
        return self._tracks


class TrackContainer(AllocatableContainer):
    def _collect_for_cleanup(self, new_items, old_items):
        items = set()
        for item in [self] + new_items:
            mixer = item.mixer or item.root
            if mixer is not None:
                items.add(mixer)
        items.update(old_items)
        return items

    @property
    def mixer(self) -> Optional["supriya.xdaw.Context"]:
        for parent in self.parentage:
            if isinstance(parent, supriya.xdaw.Context):
                return parent
        return None