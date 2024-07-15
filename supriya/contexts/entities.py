import dataclasses
import tempfile
from os import PathLike
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    Container,
    Dict,
    List,
    Optional,
    Sequence,
    SupportsFloat,
    Tuple,
    Union,
    cast,
)

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore

from ..assets.synthdefs.default import default
from ..enums import AddAction, CalculationRate
from ..io import PlayMemo
from ..typing import AddActionLike, HeaderFormatLike, SampleFormatLike, SupportsRender
from ..ugens import SynthDef
from .errors import InvalidCalculationRate, InvalidMoment
from .responses import BufferInfo, NodeInfo, QueryTreeGroup

if TYPE_CHECKING:
    import numpy

    from .core import Completion, Context
    from .realtime import AsyncServer, BaseServer, Server


@dataclasses.dataclass(frozen=True)
class ContextObject:
    r"""
    Base class for objects with context references.

    :param context: The context object's context.
    :param id\_: The context object's context ID.
    """

    context: "Context"
    id_: int

    def __float__(self) -> float:
        """
        Get the context object's ID as a float.
        """
        return float(self.id_)

    def __int__(self) -> int:
        """
        Get the context object's ID as an integer.
        """
        return self.id_

    @property
    def allocated(self) -> bool:
        """
        Get the context object's allocation status.
        """
        return self in cast("BaseServer", self.context)


@dataclasses.dataclass(frozen=True)
class Buffer(ContextObject):
    r"""
    A buffer.

    :param context: The context object's context.
    :param id\_: The context object's context ID.
    :param completion: The buffer's allocation completion.
    """

    completion: Optional["Completion"] = dataclasses.field(default=None, compare=False)

    def __enter__(self) -> "Completion":
        """
        Enter the buffer's allocation completion.
        """
        if self.completion is None:
            raise InvalidMoment
        return self.completion.__enter__()

    def __exit__(self, *args) -> None:
        """
        Exit the buffer's allocation completion.
        """
        if self.completion is None:
            raise InvalidMoment
        return self.completion.__exit__(*args)

    def __plot__(self) -> Tuple["numpy.ndarray", float]:
        import librosa

        with tempfile.TemporaryDirectory() as temp_directory:
            file_path = Path(temp_directory) / "tmp.wav"
            self.write(file_path=file_path, header_format="wav", sample_format="int32")
            cast("Server", self.context).sync()
            return librosa.load(file_path, mono=False, sr=None)

    def __render_memo__(
        self,
        output_file_path: Optional[PathLike] = None,
        render_directory_path: Optional[PathLike] = None,
        **kwargs,
    ) -> SupportsRender:
        with tempfile.TemporaryDirectory() as temp_directory:
            path = Path(temp_directory) / "tmp.wav"
            self.write(file_path=path, header_format="wav", sample_format="int32")
            cast("Server", self.context).sync()
            return PlayMemo.from_path(path)

    def close(
        self, on_completion: Optional[Callable[["Context"], None]] = None
    ) -> "Completion":
        """
        Close the buffer.

        Emit ``/b_close`` requests.

        :param on_completion: A callable with the buffer's context as the only argument.
            Permits building an "on completion" argument to this method's request
            without an active moment.
        """
        return self.context.close_buffer(self, on_completion=on_completion)

    def copy(
        self,
        *,
        target_buffer: "Buffer",
        starting_frame: int,
        target_starting_frame: int,
        frame_count: int,
    ) -> None:
        """
        Copy the buffer.

        Emit ``/b_gen <buffer.id_> copy ...`` requests.

        :param target_buffer: The buffer to copy to.
        :param starting_frame: The frame index in the this buffer to start reading from.
        :param target_starting_frame: The frame index in the target buffer to start
            writing at.
        :param frame_count: The number of frames to copy.
        """
        self.context.copy_buffer(
            frame_count=frame_count,
            source_buffer=self,
            source_starting_frame=starting_frame,
            target_buffer=target_buffer,
            target_starting_frame=target_starting_frame,
        )

    def fill(self, starting_frame: int, frame_count: int, value: float) -> None:
        """
        Fill the buffer with a single value.

        Emit ``/b_fill`` requests.

        :param starting_frame: The frame index to start filling at.
        :param frame_count: The number of frames to fill.
        :param value: The value to fill with.
        """
        self.context.fill_buffer(self, starting_frame, frame_count, value)

    def free(
        self, on_completion: Optional[Callable[["Context"], None]] = None
    ) -> "Completion":
        """
        Free the buffer.

        Emit ``/b_free`` requests.

        :param on_completion: A callable with the buffer's context as the only argument.
            Permits building an "on completion" argument to this method's request
            without an active moment.
        """
        return self.context.free_buffer(self, on_completion=on_completion)

    def generate(
        self,
        command_name: Literal["sine1", "sine2", "sine3", "cheby"],
        amplitudes: Sequence[float],
        frequencies: Optional[Sequence[float]] = None,
        phases: Optional[Sequence[float]] = None,
        as_wavetable: bool = False,
        should_clear_first: bool = False,
        should_normalize: bool = False,
    ) -> None:
        """
        Generate the buffer.

        Emit ``/b_gen`` requests.

        :param command_name: The generation command name.
        :param amplitudes: A sequence of partial amplitudes.
        :param frequencies: A sequence of partial frequencies.
        :param phases: A sequence of partial phases.
        :param as_wavetable: Flag for generating the output in wavetable format.
        :param should_clear_first: Flag for clearing the buffer before generating.
        :param should_normalize: Flag for normalizing the generated output.
        """
        self.context.generate_buffer(
            buffer=self,
            command_name=command_name,
            amplitudes=amplitudes,
            frequencies=frequencies,
            phases=phases,
            as_wavetable=as_wavetable,
            should_clear_first=should_clear_first,
            should_normalize=should_normalize,
        )

    def get(
        self, *indices: int, sync: bool = True
    ) -> Union[Awaitable[Optional[Dict[int, float]]], Optional[Dict[int, float]]]:
        """
        Get a sample.

        Emit ``/b_get`` requests.

        :param indices: The sample indices to read.
        :param sync: If true, communicate the request immediately. Otherwise bundle it
            with the current request context.
        """
        return cast(Union["AsyncServer", "Server"], self.context).get_buffer(
            self, *indices, sync=sync
        )

    def get_range(
        self, index: int, count: int, sync: bool = True
    ) -> Union[Awaitable[Optional[Sequence[float]]], Optional[Sequence[float]]]:
        """
        Get a sample range.

        Emit ``/b_getn`` requests.

        :param index: The sample index to start reading at.
        :param count: The number of samples to read.
        :param sync: If true, communicate the request immediately. Otherwise bundle it
            with the current request context.
        """
        return cast(Union["AsyncServer", "Server"], self.context).get_buffer_range(
            self, index, count, sync=sync
        )

    def normalize(self, new_maximum: float = 1.0, as_wavetable: bool = False) -> None:
        """
        Normalize the buffer.

        Emit ``/b_gen <buffer.id_> (w)?normalize`` requests depending on parameters.

        :param new_maximum: The new maximum to normalize to.
        :param as_wavetable: Flag for treating the buffer contents as a wavetable.
        """
        self.context.normalize_buffer(
            self, new_maximum=new_maximum, as_wavetable=as_wavetable
        )

    def query(
        self, sync: bool = True
    ) -> Union[Awaitable[Optional[BufferInfo]], Optional[BufferInfo]]:
        """
        Query the buffer.

        Emit ``/b_query`` requests.

        :param sync: If true, communicate the request immediately. Otherwise bundle it
            with the current request context.
        """
        return cast(Union["AsyncServer", "Server"], self.context).query_buffer(
            self, sync=sync
        )

    def read(
        self,
        file_path: PathLike,
        *,
        buffer_starting_frame: Optional[int] = None,
        channel_indices: Optional[List[int]] = None,
        frame_count: Optional[int] = None,
        leave_open: bool = False,
        on_completion: Optional[Callable[["Context"], None]] = None,
        starting_frame: Optional[int] = None,
    ) -> "Completion":
        """
        Read a file into the buffer.

        Emit ``/b_read`` or ``/b_readChannel`` requests, depending on parameters.

        :param file_path: The file path to read from.
        :param channel_indices: A list of channel indices to read from when reading from
            a file.
        :param frame_count: The number of frames to read.
        :param leave_open: Flag for leaving the file open (e.g. to continue reading via
            :py:class:`~supriya.ugens.diskio.DiskIn`) or close it.
        :param starting_frame: The starting frame in the buffer to begin reading into
            at.
        :param on_completion: A callable with the buffer's context as the only argument.
            Permits building an "on completion" argument to this method's request
            without an active moment.
        """
        return self.context.read_buffer(
            self,
            file_path,
            buffer_starting_frame=buffer_starting_frame,
            channel_indices=channel_indices,
            frame_count=frame_count,
            leave_open=leave_open,
            on_completion=on_completion,
            starting_frame=starting_frame,
        )

    def set(self, index: int, value: float) -> None:
        """
        Set a sample.

        Emit ``/b_set`` requests.

        :param index: The sample index to write at.
        :param value: The value to write.
        """
        self.context.set_buffer(buffer=self, index=index, value=value)

    def set_range(self, index: int, values: Sequence[float]) -> None:
        """
        Set a sample range.

        Emit ``/b_setn`` requests.

        :param index: The sample index to start writing at.
        :param values: The values to write.
        """
        self.context.set_buffer_range(buffer=self, index=index, values=values)

    def write(
        self,
        file_path: PathLike,
        *,
        frame_count: Optional[int] = None,
        header_format: HeaderFormatLike = "aiff",
        leave_open: bool = False,
        on_completion: Optional[Callable[["Context"], None]] = None,
        sample_format: SampleFormatLike = "int24",
        starting_frame: Optional[int] = None,
    ) -> "Completion":
        """
        Write the buffer to disk.

        Emit ``/b_write`` requests.

        :param file_path: The file path to write into.
        :param frame_count: The number of frames to write.
        :param header_format: The header format to use, e.g. ``AIFF`` or ``WAVE``.
        :param leave_open: Flag for leaving the file open (e.g. to continue writing via
            :py:class:`~supriya.ugens.diskio.DiskOut`) or close it.
        :param sample_format: The sample format to use, e.g. ``INT24`` or ``FLOAT``.
        :param starting_frame: The starting frame in the buffer to start writing from.
        :param on_completion: A callable with the buffer's context as the only argument.
            Permits building an "on completion" argument to this method's request
            without an active moment.
        """
        return self.context.write_buffer(
            self,
            file_path,
            frame_count=frame_count,
            header_format=header_format,
            leave_open=leave_open,
            on_completion=on_completion,
            sample_format=sample_format,
            starting_frame=starting_frame,
        )

    def zero(
        self, on_completion: Optional[Callable[["Context"], None]] = None
    ) -> "Completion":
        """
        Zero the buffer.

        Emit ``/b_zero`` requests.

        :param on_completion: A callable with the buffer's context as the only argument.
            Permits building an "on completion" argument to this method's request
            without an active moment.
        """
        return self.context.zero_buffer(self, on_completion=on_completion)


@dataclasses.dataclass(frozen=True)
class BufferGroup(ContextObject):
    r"""
    A buffer group.

    :param context: The buffer group's context.
    :param id\_: The buffer group's context ID.
    :param count: The number of child buffers.
    """

    count: int = 1
    buffers: Tuple[Buffer, ...] = dataclasses.field(
        init=False, repr=False, default_factory=tuple
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "buffers",
            tuple(
                Buffer(context=self.context, id_=i)
                for i in range(self.id_, self.id_ + self.count)
            ),
        )

    def __getitem__(self, item):
        return self.buffers[item]

    def __len__(self) -> int:
        return len(self.buffers)

    def free(self):
        """
        Free the buffer group.

        Emit ``/b_free`` requests.
        """
        self.context.free_buffer_group(self)


@dataclasses.dataclass(frozen=True)
class Bus(ContextObject):
    r"""
    A bus.

    :param context: The bus' context.
    :param id\_: The bus' context ID.
    :param calculation_rate: The bus' calculation rate.
    """

    calculation_rate: CalculationRate

    def fill(self, count: int, value: float) -> None:
        """
        Fill contiguous buses with a single value, starting with this bus.

        Emit ``/c_fill`` requests.

        :param count: The number of buses to fill.
        :param value: The value to fill with.
        """
        self.context.fill_bus_range(self, count, value)

    def free(self) -> None:
        """
        Free the bus.

        Emit no requests.
        """
        self.context.free_bus(self)

    def get(
        self, sync: bool = True
    ) -> Union[Awaitable[Optional[float]], Optional[float]]:
        """
        Get the control bus' value.

        Emit ``/c_get`` requests.

        :param sync: If true, communicate the request immediately. Otherwise bundle it
            with the current request context.
        """
        return cast(Union["AsyncServer", "Server"], self.context).get_bus(
            self, sync=sync
        )

    def get_range(
        self, count: int, sync: bool = True
    ) -> Union[Awaitable[Optional[Sequence[float]]], Optional[Sequence[float]]]:
        """
        Get a range of control bus values.

        Emit ``/c_getn`` requests.

        :param count: The number of contiguous buses whose values to get.
        :param sync: If true, communicate the request immediately. Otherwise bundle it
            with the current request context.
        """
        return cast(Union["AsyncServer", "Server"], self.context).get_bus_range(
            self, count, sync=sync
        )

    def map_symbol(self) -> str:
        """
        Get the bus' map symbol.
        """
        if self.calculation_rate is CalculationRate.AUDIO:
            return f"a{self.id_}"
        elif self.calculation_rate is CalculationRate.CONTROL:
            return f"c{self.id_}"
        raise InvalidCalculationRate

    def set(self, value: float) -> None:
        """
        Set the control bus's value.

        Emit ``/c_set`` requests.

        :param value: The value to set the control bus to.
        """
        self.context.set_bus(self, value)

    def set_range(self, values: Sequence[float]) -> None:
        """
        Set a range of control buses.

        Emit ``/c_setn`` requests.

        :param values: The values to write.
        """
        self.context.set_bus_range(self, values)


@dataclasses.dataclass(frozen=True)
class BusGroup(ContextObject):
    r"""
    A bus group.

    :param context: The bus group's context.
    :param id\_: The bus group's context ID.
    :param calculation_rate: The bus group's calculation rate.
    :param count: The number of child buses.
    """

    calculation_rate: CalculationRate
    count: int = 1
    buses: Tuple[Bus, ...] = dataclasses.field(
        init=False, repr=False, default_factory=tuple
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "buses",
            tuple(
                Bus(calculation_rate=self.calculation_rate, context=self.context, id_=i)
                for i in range(self.id_, self.id_ + self.count)
            ),
        )

    def __getitem__(self, item):
        return self.buses[item]

    def __len__(self) -> int:
        return len(self.buses)

    def free(self):
        """
        Free the bus group.

        Emit no requests.
        """
        self.context.free_bus_group(self)

    def get(
        self, sync: bool = True
    ) -> Union[Awaitable[Optional[Sequence[float]]], Optional[Sequence[float]]]:
        """
        Get the control bus group's values.

        Emit ``/c_getn`` requests.

        :param sync: If true, communicate the request immediately. Otherwise bundle it
            with the current request context.
        """
        return cast(Union["AsyncServer", "Server"], self.context).get_bus_range(
            bus=self[0], count=len(self), sync=sync
        )

    def map_symbol(self) -> str:
        """
        Get the bus group's map symbol.
        """
        if self.calculation_rate is CalculationRate.AUDIO:
            return f"a{self.id_}"
        elif self.calculation_rate is CalculationRate.CONTROL:
            return f"c{self.id_}"
        raise InvalidCalculationRate

    def set(self, values: Union[float, Sequence[float]]) -> None:
        """
        Set a range of control buses.

        Emit ``/c_setn`` or ``/c_fill`` requests.

        :param values: The values to write. If a float is passed, use that as a fill.
        """
        if isinstance(values, float):
            if len(self) == 1:
                self.context.set_bus(bus=self[0], value=values)
            else:
                self.context.fill_bus_range(bus=self[0], count=len(self), value=values)
        else:
            self.context.set_bus_range(bus=self[0], values=values)


@dataclasses.dataclass(frozen=True)
class Node(ContextObject):
    r"""
    A node.

    :param context: The node's context.
    :param id\_: The node's context ID.
    """

    def add_group(
        self,
        add_action: AddActionLike = AddAction.ADD_TO_HEAD,
        parallel: bool = False,
        permanent: bool = False,
    ) -> "Group":
        """
        Add a new group relative to this node.

        Emit ``/g_new`` or ``/p_new`` requests depending on parameters.

        :param add_action: The :term:`add action` to use when placing the new group.
        :param parallel: Flag for parallel vs non-parallel groups.
        :param permanent: Flag for using a permanent node ID.
        """
        return self.context.add_group(
            add_action=add_action,
            parallel=parallel,
            permanent=permanent,
            target_node=self,
        )

    def add_synth(
        self,
        synthdef: SynthDef,
        *,
        add_action: AddActionLike = AddAction.ADD_TO_HEAD,
        permanent: bool = False,
        **settings,
    ) -> "Synth":
        """
        Add a new synth relative to this node.

        Emit ``/s_new`` requests.

        :param synthdef: The :term:`SynthDef` to use for the new synth.
        :param add_action: The :term:`add action` to use when placing the new synth.
        :param permanent: Flag for using a permanent node ID.
        :param settings: The new synth's control settings.
        """
        return self.context.add_synth(
            synthdef=synthdef,
            add_action=add_action,
            permanent=permanent,
            target_node=self,
            **settings,
        )

    def free(self, force: bool = False) -> None:
        """
        Free the node.

        Emit ``/n_free`` for groups, for synths without a ``gate`` control, or when
        ``force`` is ``True``.

        Emit ``/n_set <node.id_> gate 0`` for synths with ``gate`` controls.

        :param force: Flag for force-freeing, without releasing.
        """
        return self.context.free_node(self, force=force)

    def map(self, **settings: Union[Bus, None]) -> None:
        """
        Map the node's controls to buses.

        Emit ``/n_map`` and ``/n_mapa`` requests.

        :param settings: A mapping of control names to buses (or to ``None`` to unmap
            the control).
        """
        self.context.map_node(self, **settings)

    def move(self, target_node: "Node", add_action: AddActionLike = None) -> None:
        """
        Move the node.

        Emit ``/n_after``, ``/n_before``, ``/g_head`` and ``/g_tail`` requests depending
        on parameters.

        :param add_action: The :term:`add action` to use when moving the node.
        :param target_node: The target node to place the node relative to.
        """
        self.context.move_node(
            node=self, add_action=add_action, target_node=target_node
        )

    def order(self, *nodes: "Node", add_action: AddActionLike = None) -> None:
        """
        Re-order nodes relative to the node.

        Emit ``/n_order`` requests.

        :param nodes: The nodes to re-order.
        :param add_action: The :term:`add action` to use when re-ordering the nodes.
        """
        self.context.order_nodes(self, *nodes, add_action=add_action)

    def pause(self) -> None:
        """
        Pause the node.

        Emit ``/n_run <node.id_> 0`` requests.
        """
        self.context.pause_node(self)

    def query(
        self, sync: bool = True
    ) -> Union[Awaitable[Optional[NodeInfo]], Optional[NodeInfo]]:
        """
        Query the node.

        Emit ``/n_query`` requests.

        :param sync: If true, communicate the request immediately. Otherwise bundle it
            with the current request context.
        """
        return cast(Union["AsyncServer", "Server"], self.context).query_node(
            self, sync=sync
        )

    def set(
        self,
        *indexed_settings: Tuple[int, Union[SupportsFloat, Sequence[SupportsFloat]]],
        **settings: Union[SupportsFloat, Sequence[SupportsFloat]],
    ) -> None:
        """
        Set the node's controls.

        :param indexed_settings: A sequence of control indices to values.
        :param settings: A mapping of control names to values.
        """
        self.context.set_node(self, *indexed_settings, **settings)

    def set_range(
        self,
        *indexed_settings: Tuple[int, Sequence[SupportsFloat]],
        **settings: Sequence[SupportsFloat],
    ) -> None:
        """
        Set a range of the node's controls.

        :param indexed_settings: A sequence of control indices to values.
        :param settings: A mapping of control names to values.
        """
        self.context.set_node_range(self, *indexed_settings, **settings)

    def unpause(self) -> None:
        """
        Unpause the node.

        Emit ``/n_run <node.id_> 1`` requests.
        """
        self.context.unpause_node(self)

    @property
    def _valid_add_actions(self) -> Container[int]:
        return (
            AddAction.ADD_AFTER,
            AddAction.ADD_BEFORE,
            AddAction.ADD_TO_HEAD,
            AddAction.ADD_TO_TAIL,
            AddAction.REPLACE,
        )

    @property
    def active(self) -> bool:
        """
        Get the node's paused/unpaused status.
        """
        return cast("BaseServer", self.context)._node_active.get(self.id_, True)

    @property
    def parent(self) -> Optional["Group"]:
        """
        Get the node's parent, as currently cached on the context.
        """
        parent_id = cast("BaseServer", self.context)._node_parents.get(self.id_)
        if parent_id is None:
            return None
        elif parent_id == 0:
            return RootNode(context=self.context, id_=0)
        return Group(context=self.context, id_=parent_id)

    @property
    def parentage(self) -> Sequence["Node"]:
        """
        Get the node's parentage, as currently cached on the context.
        """
        context = cast("BaseServer", self.context)
        parentage: List["Node"] = [self]
        while (parent_id := context._node_parents.get(parentage[-1].id_)) is not None:
            if parent_id:
                parentage.append(Group(context=context, id_=parent_id))
            else:
                parentage.append(context.root_node)
        return parentage


@dataclasses.dataclass(frozen=True)
class Group(Node):
    r"""
    A group node.

    :param context: The group's context.
    :param id\_: The group's context ID.
    :param parallel: Flag for parallel vs non-parallel groups.
    """

    parallel: bool = False

    def dump_tree(
        self,
        include_controls: bool = True,
        sync: bool = True,
    ) -> Union[Awaitable[Optional[QueryTreeGroup]], Optional[QueryTreeGroup]]:
        """
        Dump the group's node tree.

        Emit ``/g_dumpTree`` requests.

        :param include_controls: Flag for including synth control values.
        :param sync: If true, communicate the request immediately. Otherwise bundle it
            with the current request context.
        """
        return cast(Union["AsyncServer", "Server"], self.context).dump_tree(
            group=self, include_controls=include_controls, sync=sync
        )

    def free_children(self, synths_only: bool = False) -> None:
        """
        Free the group's children.

        Emit ``/g_deepFree`` or ``/g_freeAll`` requests depending on parameters.

        :param synths_only: Flag for freeing only child synths, or all children.
        """
        self.context.free_group_children(self, synths_only=synths_only)

    def query_tree(
        self,
        include_controls: bool = True,
        sync: bool = True,
    ) -> Union[Awaitable[Optional[QueryTreeGroup]], Optional[QueryTreeGroup]]:
        """
        Query the group's node tree.

        Emit ``/g_queryTree`` requests.

        :param include_controls: Flag for including synth control values.
        :param sync: If true, communicate the request immediately. Otherwise bundle it
            with the current request context.
        """
        return cast(Union["AsyncServer", "Server"], self.context).query_tree(
            group=self, include_controls=include_controls, sync=sync
        )

    @property
    def children(self) -> List[Node]:
        """
        Get the group's children, as currently cached on the context.
        """
        children: List[Node] = []
        for id_ in cast("BaseServer", self.context)._node_children.get(self.id_, []):
            if id_ in cast("BaseServer", self.context)._node_children:
                children.append(Group(context=self.context, id_=id_))
            else:
                # cannot get synthdef name without running /g_queryTree
                children.append(Synth(context=self.context, id_=id_, synthdef=default))
        return children


@dataclasses.dataclass(frozen=True)
class RootNode(Group):
    r"""
    A root node.

    :param context: The root node's context.
    """

    def __post_init__(self) -> None:
        """
        Force ``id_`` to ``0``, and ``parallel`` to ``False``.
        """
        object.__setattr__(self, "id_", 0)
        object.__setattr__(self, "parallel", False)

    @property
    def _valid_add_actions(self) -> Container[int]:
        return (AddAction.ADD_TO_HEAD, AddAction.ADD_TO_TAIL)


@dataclasses.dataclass(frozen=True)
class Synth(Node):
    r"""
    A synth node.

    :param context: The synth's context.
    :param id\_: The synth's context ID.
    :param synthdef: The synth's SynthDef.
    """

    synthdef: SynthDef

    def get(self, *controls: Union[int, str], sync: bool = True) -> Union[
        Awaitable[Optional[Dict[Union[int, str], float]]],
        Optional[Dict[Union[int, str], float]],
    ]:
        """
        Get a control.

        Emit ``/s_get`` requests.

        :param controls: The control to get.
        :param sync: If true, communicate the request immediately. Otherwise bundle it
            with the current request context.
        """
        return cast(Union["AsyncServer", "Server"], self.context).get_synth_controls(
            self, *controls, sync=sync
        )

    def get_range(
        self, control: Union[int, str], count: int, sync: bool = True
    ) -> Union[
        Awaitable[Optional[Sequence[Union[float, str]]]],
        Optional[Sequence[Union[float, str]]],
    ]:
        """
        Get a range of controls.

        Emit ``/s_get`` requests.

        :param control: The control to start reading at.
        :param count: The number of contiguous controls to get.
        :param sync: If true, communicate the request immediately. Otherwise bundle it
            with the current request context.
        """
        return cast(
            Union["AsyncServer", "Server"], self.context
        ).get_synth_control_range(self, control, count, sync=sync)

    @property
    def _valid_add_actions(self) -> Container[int]:
        return (AddAction.ADD_AFTER, AddAction.ADD_BEFORE, AddAction.REPLACE)
