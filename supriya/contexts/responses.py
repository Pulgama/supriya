"""
Classes for modeling responses from :term:`scsynth`.
"""

import dataclasses
import re
from collections import deque
from typing import (
    Deque,
    Dict,
    Generator,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
    cast,
)

from ..enums import NodeAction
from ..osc import OscMessage


@dataclasses.dataclass
class Response:
    @classmethod
    def from_osc(cls, osc_message: OscMessage) -> "Response":
        mapping: Dict[str, Type[Response]] = {
            "/b_info": BufferInfo,
            "/b_set": GetBufferInfo,
            "/b_setn": GetBufferRangeInfo,
            "/c_set": GetControlBusInfo,
            "/c_setn": GetControlBusRangeInfo,
            "/d_removed": SynthDefRemovedInfo,
            "/done": DoneInfo,
            "/fail": FailInfo,
            "/g_queryTree.reply": QueryTreeInfo,
            "/n_end": NodeInfo,
            "/n_go": NodeInfo,
            "/n_info": NodeInfo,
            "/n_move": NodeInfo,
            "/n_off": NodeInfo,
            "/n_on": NodeInfo,
            "/n_set": GetNodeControlInfo,
            "/n_setn": GetNodeControlRangeInfo,
            "/status.reply": StatusInfo,
            "/synced": SyncedInfo,
            "/tr": TriggerInfo,
            "/version.reply": VersionInfo,
        }
        return mapping[str(osc_message.address)].from_osc(osc_message)


@dataclasses.dataclass
class BufferInfo(Response):
    """
    A ``/b_info`` response.
    """

    @dataclasses.dataclass
    class Item:
        buffer_id: int
        frame_count: int
        channel_count: int
        sample_rate: float

    items: Sequence[Item]

    @classmethod
    def from_osc(cls, osc_message: OscMessage) -> "Response":
        return cls(
            items=[
                cls.Item(*osc_message.contents[i : i + 4])
                for i in range(0, len(osc_message.contents), 4)
            ]
        )


@dataclasses.dataclass
class DoneInfo(Response):
    """
    A ``/done`` response.
    """

    command_name: str
    other: Sequence[Union[float, str]]

    @classmethod
    def from_osc(cls, osc_message: OscMessage) -> "Response":
        command_name, *other = osc_message.contents
        return cls(command_name=command_name, other=other)


@dataclasses.dataclass
class FailInfo(Response):
    """
    A ``/fail`` response.
    """

    command_name: str
    error: str
    other: Sequence[Union[float, str]]

    @classmethod
    def from_osc(cls, osc_message: OscMessage) -> "Response":
        return cls(
            command_name=osc_message.contents[0],
            error=osc_message.contents[1],
            other=osc_message.contents[2:],
        )


@dataclasses.dataclass
class GetBufferInfo(Response):
    """
    A ``/b_set`` response.
    """

    buffer_id: int
    items: Sequence[Tuple[int, float]]

    @classmethod
    def from_osc(cls, osc_message: OscMessage) -> "Response":
        buffer_id = osc_message.contents[0]
        items: List[Tuple[int, float]] = []
        for i in range(1, len(osc_message.contents), 2):
            index, value = osc_message.contents[i : i + 2]
            items.append((int(index), float(value)))
        return cls(buffer_id=buffer_id, items=items)


@dataclasses.dataclass
class GetBufferRangeInfo(Response):
    """
    A ``/b_setn`` response.
    """

    buffer_id: int
    items: Sequence[Tuple[int, Sequence[float]]]

    @classmethod
    def from_osc(cls, osc_message: OscMessage) -> "Response":
        buffer_id = osc_message.contents[0]
        items: List[Tuple[int, Sequence[float]]] = []
        current_index = 1
        while current_index < len(osc_message.contents):
            index, count = osc_message.contents[current_index : current_index + 2]
            current_index += 2
            values = osc_message.contents[current_index : current_index + count]
            items.append((index, tuple(values)))
            current_index += count
        return cls(buffer_id=buffer_id, items=items)


@dataclasses.dataclass
class GetControlBusInfo(Response):
    """
    A ``/c_set`` response.
    """

    items: Sequence[Tuple[int, float]]

    @classmethod
    def from_osc(cls, osc_message: OscMessage) -> "Response":
        items: List[Tuple[int, float]] = []
        for i in range(0, len(osc_message.contents), 2):
            index, value = osc_message.contents[i : i + 2]
            items.append((int(index), float(value)))
        return cls(items=items)


@dataclasses.dataclass
class GetControlBusRangeInfo(Response):
    """
    A ``/c_setn`` response.
    """

    items: Sequence[Tuple[int, Sequence[float]]]

    @classmethod
    def from_osc(cls, osc_message: OscMessage) -> "Response":
        items: List[Tuple[int, Sequence[float]]] = []
        current_index = 0
        while current_index < len(osc_message.contents):
            index, count = osc_message.contents[current_index : current_index + 2]
            current_index += 2
            values = osc_message.contents[current_index : current_index + count]
            items.append((index, tuple(values)))
            current_index += count
        return cls(items=items)


@dataclasses.dataclass
class GetNodeControlInfo(Response):
    node_id: int
    items: Sequence[Tuple[Union[int, str], float]]

    @classmethod
    def from_osc(cls, osc_message: OscMessage) -> "Response":
        node_id, *rest = osc_message.contents
        items: List[Tuple[Union[int, str], float]] = []
        for i in range(1, len(osc_message.contents), 2):
            name_or_index, value = osc_message.contents[i : i + 2]
            items.append(
                (
                    (
                        name_or_index
                        if isinstance(name_or_index, str)
                        else int(name_or_index)
                    ),
                    float(value),
                )
            )
        return cls(node_id=node_id, items=items)


@dataclasses.dataclass
class GetNodeControlRangeInfo(Response):
    node_id: int
    items: Sequence[Tuple[Union[int, str], Sequence[float]]]

    @classmethod
    def from_osc(cls, osc_message: OscMessage) -> "Response":
        node_id, *rest = osc_message.contents
        items: List[Tuple[Union[int, str], Sequence[float]]] = []
        current_index = 1
        while current_index < len(osc_message.contents):
            name_or_index, count = osc_message.contents[
                current_index : current_index + 2
            ]
            current_index += 2
            values = osc_message.contents[current_index : current_index + count]
            items.append(
                (
                    (
                        name_or_index
                        if isinstance(name_or_index, str)
                        else int(name_or_index)
                    ),
                    tuple(values),
                )
            )
            current_index += count
        return cls(node_id=node_id, items=items)


@dataclasses.dataclass
class NodeInfo(Response):
    action: NodeAction
    node_id: int
    parent_id: int
    previous_id: int
    next_id: int
    is_group: bool
    head_id: Optional[int] = None
    tail_id: Optional[int] = None

    @classmethod
    def from_osc(cls, osc_message: OscMessage) -> "Response":
        action = osc_message.address
        (
            node_id,
            parent_id,
            previous_id,
            next_id,
            is_group,
            *rest,
        ) = osc_message.contents
        if is_group:
            head_id: Optional[int] = int(rest[0])
            tail_id: Optional[int] = int(rest[1])
        else:
            head_id, tail_id = None, None
        return cls(
            action=NodeAction.from_expr(action),
            node_id=int(node_id),
            parent_id=int(parent_id),
            previous_id=int(previous_id),
            next_id=int(next_id),
            is_group=bool(is_group),
            head_id=head_id,
            tail_id=tail_id,
        )


@dataclasses.dataclass
class QueryTreeInfo(Response):
    """
    A ``/g_queryTree.reply`` response.
    """

    @dataclasses.dataclass
    class Item:
        node_id: int
        child_count: int
        synthdef_name: Optional[str] = None
        controls: Optional[Dict[Union[int, str], Union[float, str]]] = None

    node_id: int
    child_count: int
    items: Sequence[Item]

    @classmethod
    def from_osc(cls, osc_message: OscMessage) -> "Response":
        flag = osc_message.contents[0]
        node_id = int(osc_message.contents[1])
        child_count = int(osc_message.contents[2])
        items: List["QueryTreeInfo.Item"] = []
        index = 3
        while index < len(osc_message.contents):
            child_id = int(osc_message.contents[index])
            child_child_count = int(osc_message.contents[index + 1])
            synthdef_name: Optional[str] = None
            controls: Optional[Dict[Union[int, str], Union[float, str]]] = None
            index += 2
            if child_child_count < 0:
                synthdef_name = osc_message.contents[index]
                index += 1
                if flag:
                    controls = {}
                    control_count = osc_message.contents[index]
                    index += 1
                    for i in range(control_count):
                        name_or_index: Union[int, str] = osc_message.contents[index]
                        value: Union[float, str] = osc_message.contents[index + 1]
                        controls[name_or_index] = value
                        index += 2
            items.append(
                cls.Item(
                    node_id=child_id,
                    child_count=child_child_count,
                    controls=controls,
                    synthdef_name=synthdef_name,
                )
            )
        return cls(node_id=node_id, child_count=child_count, items=items)


@dataclasses.dataclass
class QueryTreeControl:
    name_or_index: Union[int, str]
    value: Union[float, str]

    def __str__(self):
        value = self.value
        try:
            value = round(value, 6)
        except Exception:
            pass
        return f"{self.name_or_index}: {value!s}"


@dataclasses.dataclass
class QueryTreeNode:
    node_id: int
    annotation: Optional[str] = None


@dataclasses.dataclass
class QueryTreeSynth(QueryTreeNode):
    node_id: int
    synthdef_name: Optional[str] = None
    controls: List[QueryTreeControl] = dataclasses.field(default_factory=list)
    annotation: Optional[str] = None

    def __format__(self, format_spec):
        return "\n".join(
            self._get_str_format_pieces(unindexed=format_spec == "unindexed")
        )

    def __str__(self):
        return "\n".join(self._get_str_format_pieces())

    def _get_str_format_pieces(self, unindexed=False):
        result = []
        node_id = self.node_id
        if unindexed:
            node_id = "..."
        string = f"{node_id} {self.synthdef_name}"
        if self.annotation:
            string += f" ({self.annotation})"
        result.append(string)
        if self.controls:
            result.append("    " + ", ".join(str(control) for control in self.controls))
        return result


@dataclasses.dataclass
class QueryTreeGroup(QueryTreeNode):
    node_id: int
    children: List[QueryTreeNode] = dataclasses.field(default_factory=list)
    annotation: Optional[str] = None

    ### SPECIAL METHODS ###

    def __format__(self, format_spec):
        return "NODE TREE " + "\n".join(
            self._get_str_format_pieces(unindexed=format_spec == "unindexed")
        )

    def __str__(self):
        return "NODE TREE " + "\n".join(self._get_str_format_pieces())

    ### PRIVATE METHODS ###

    def _get_str_format_pieces(self, unindexed=False):
        result = []
        node_id = self.node_id
        if unindexed:
            node_id = "..."
        string = f"{node_id} group"
        if self.annotation:
            string += f" ({self.annotation})"
        result.append(string)
        for child in self.children:
            for line in child._get_str_format_pieces(unindexed=unindexed):
                result.append("    {}".format(line))
        return result

    ### PUBLIC METHODS ###

    def annotate(self, annotations: Dict[int, str]) -> "QueryTreeGroup":
        root = self
        if root.node_id in annotations:
            root = dataclasses.replace(root, annotation=annotations[root.node_id])
        for group in root.walk():
            for i, child in enumerate(group.children):
                if child.node_id in annotations:
                    group.children[i] = dataclasses.replace(
                        child, annotation=annotations[child.node_id]
                    )
        return root

    @classmethod
    def from_query_tree_info(cls, response: QueryTreeInfo) -> "QueryTreeGroup":
        def recurse(
            item: QueryTreeInfo.Item, items: Deque[QueryTreeInfo.Item]
        ) -> Union[QueryTreeGroup, QueryTreeSynth]:
            if item.child_count < 0:
                return QueryTreeSynth(
                    node_id=item.node_id,
                    synthdef_name=item.synthdef_name,
                    controls=[
                        QueryTreeControl(name_or_index=name_or_index, value=value)
                        for name_or_index, value in (item.controls or {}).items()
                    ],
                )
            children: List[QueryTreeNode] = []
            for _ in range(item.child_count):
                children.append(recurse(items.popleft(), items))
            return QueryTreeGroup(node_id=item.node_id, children=children)

        return cast(
            QueryTreeGroup,
            recurse(
                QueryTreeInfo.Item(
                    node_id=response.node_id, child_count=response.child_count
                ),
                deque(response.items),
            ),
        )

    @classmethod
    def from_string(cls, string) -> "QueryTreeGroup":
        node_pattern = re.compile(r"^\s*(\d+) (\S+)$")
        control_pattern = re.compile(r"\w+: \S+")
        lines = string.splitlines()
        while not lines[0].startswith("NODE TREE"):
            lines.pop(0)
        if not lines:
            raise ValueError(string)
        stack: List[QueryTreeGroup] = [
            QueryTreeGroup(node_id=int(lines.pop(0).rpartition(" ")[-1]))
        ]
        for line in lines:
            indent = line.count("   ")
            if match := (node_pattern.match(line)):
                while len(stack) > indent:
                    stack.pop()
                node_id = int(match.groups()[0])
                if (name := match.groups()[1]) == "group":
                    stack[-1].children.append(group := QueryTreeGroup(node_id=node_id))
                    stack.append(group)
                else:
                    stack[-1].children.append(
                        synth := QueryTreeSynth(node_id=node_id, synthdef_name=name)
                    )
            else:
                for pair in control_pattern.findall(line):
                    name_string, _, value_string = pair.partition(": ")
                    try:
                        name_or_index: Union[int, str] = int(name_string)
                    except ValueError:
                        name_or_index = name_string
                    try:
                        value: Union[float, str] = float(value_string)
                    except ValueError:
                        value = value_string
                    synth.controls.append(
                        QueryTreeControl(name_or_index=name_or_index, value=value)
                    )
        return stack[0]

    def walk(self) -> Generator["QueryTreeGroup", None, None]:
        yield self
        for child in self.children:
            if isinstance(child, QueryTreeGroup):
                yield from child.walk()


@dataclasses.dataclass
class StatusInfo(Response):
    """
    A ``/status.reply`` response.
    """

    actual_sample_rate: float
    average_cpu_usage: float
    group_count: int
    peak_cpu_usage: float
    synth_count: int
    synthdef_count: int
    target_sample_rate: float
    ugen_count: int

    @classmethod
    def from_osc(cls, osc_message: OscMessage) -> "Response":
        (
            _,
            ugen_count,
            synth_count,
            group_count,
            synthdef_count,
            average_cpu_usage,
            peak_cpu_usage,
            target_sample_rate,
            actual_sample_rate,
        ) = osc_message.contents
        return cls(
            actual_sample_rate=actual_sample_rate,
            average_cpu_usage=average_cpu_usage,
            group_count=group_count,
            peak_cpu_usage=peak_cpu_usage,
            synth_count=synth_count,
            synthdef_count=synthdef_count,
            target_sample_rate=target_sample_rate,
            ugen_count=ugen_count,
        )


@dataclasses.dataclass
class SyncedInfo(Response):
    """
    A ``/synced`` response.
    """

    sync_id: int

    @classmethod
    def from_osc(cls, osc_message: OscMessage) -> "Response":
        return cls(*osc_message.contents)


@dataclasses.dataclass
class SynthDefRemovedInfo(Response):
    """
    A ``/d_removed`` response.
    """

    name: str

    @classmethod
    def from_osc(cls, osc_message: OscMessage) -> "Response":
        return cls(*osc_message.contents)


@dataclasses.dataclass
class TriggerInfo(Response):
    """
    A ``/tr`` response.
    """

    node_id: int
    trigger_id: int
    value: float

    @classmethod
    def from_osc(cls, osc_message: OscMessage) -> "Response":
        return cls(*osc_message.contents)


@dataclasses.dataclass
class VersionInfo(Response):
    """
    A ``/version.reply`` response.
    """

    program_name: str
    major: int
    minor: int
    patch: str
    branch: str
    commit: str

    @classmethod
    def from_osc(cls, osc_message: OscMessage) -> "Response":
        return cls(*osc_message.contents)
