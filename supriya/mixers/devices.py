from typing import List

from ..contexts import AsyncServer
from ..enums import AddAction
from ..ugens import SynthDef
from .components import AllocatableComponent, C, ComponentNames
from .synthdefs import DEVICE_DC_TESTER_2


class DeviceContainer(AllocatableComponent[C]):

    def __init__(self) -> None:
        self._devices: List[Device] = []

    def _delete_device(self, device: "Device") -> None:
        self._devices.remove(device)

    async def add_device(self) -> "Device":
        async with self._lock:
            self._devices.append(device := Device(parent=self))
            if context := self._can_allocate():
                await device._allocate_deep(context=context)
            return device

    @property
    def devices(self) -> List["Device"]:
        return self._devices[:]


class Device(AllocatableComponent):

    def _allocate(self, *, context: AsyncServer) -> bool:
        if not super()._allocate(context=context):
            return False
        elif self.parent is None:
            raise RuntimeError
        main_audio_bus = self.parent._get_audio_bus(context, name=ComponentNames.MAIN)
        target_node = self.parent._nodes[ComponentNames.DEVICES]
        with context.at():
            self._nodes[ComponentNames.GROUP] = group = target_node.add_group(
                add_action=AddAction.ADD_TO_TAIL
            )
            self._nodes[ComponentNames.SYNTH] = group.add_synth(
                add_action=AddAction.ADD_TO_TAIL,
                out=main_audio_bus,
                synthdef=DEVICE_DC_TESTER_2,
            )
        return True

    def _get_synthdefs(self) -> List[SynthDef]:
        return [DEVICE_DC_TESTER_2]

    async def set_active(self, active: bool = True) -> None:
        async with self._lock:
            pass

    @property
    def address(self) -> str:
        if self.parent is None:
            return "devices[?]"
        index = self.parent.devices.index(self)
        return f"{self.parent.address}.devices[{index}]"
