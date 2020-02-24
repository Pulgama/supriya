import asyncio
import logging
import queue
import traceback
from typing import Optional, Tuple

from .bases import (
    BaseTempoClock,
)
from .ephemera import (
    CallbackCommand,
    ChangeCommand,
    ClockState,
    EventType,
    Moment,
)
from .ephemera import TimeUnit, CallbackEvent, ChangeEvent

logger = logging.getLogger("supriya.clock")


class AsyncTempoClock(BaseTempoClock):
    def __init__(self):
        BaseTempoClock.__init__(self)
        self._lock = asyncio.Lock()
        self._condition = asyncio.Condition(self._lock)
        self._task = None
        self._slop = 1.0

    ### SCHEDULING METHODS ###

    def _cancel(self, event_id) -> Optional[Tuple]:
        event = self._events_by_id.pop(event_id, None)
        if event is not None and not isinstance(
            event, (CallbackCommand, ChangeCommand)
        ):
            self._event_queue.remove(event)
            if event.offset is not None:
                self._offset_relative_event_ids.remove(event.event_id)
                if event.measure is not None:
                    self._measure_relative_event_ids.remove(event.event_id)
        return event

    async def _enqueue_command(self, command):
        super()._enqueue_command(command)
        async with self._lock:
            self._condition.notify()

    async def _perform_callback_event(self, event, current_moment, desired_moment):
        logger.debug(
            f"[{self.name}] ... ... Performing {event.procedure} at "
            f"{desired_moment.seconds - self._state.initial_seconds}:s / "
            f"{desired_moment.offset}:o"
        )
        try:
            result = event.procedure(
                current_moment,
                desired_moment,
                event,
                *(event.args or ()),
                **(event.kwargs or {}),
            )
            if asyncio.iscoroutine(result):
                result = await result
        except Exception:
            traceback.print_exc()
            return
        self._process_callback_event_result(desired_moment, event, result)

    async def _perform_events(self, current_moment: Moment):
        logger.debug(
            f"[{self.name}] ... Ready to perform at "
            f"{current_moment.seconds - self._state.initial_seconds}:s / "
            f"{current_moment.offset}:o"
        )
        while self._is_running and self._event_queue.qsize():
            (
                event,
                desired_moment,
                should_continue,
                should_break,
            ) = self._process_perform_event_loop(current_moment)
            if should_continue:
                continue
            elif should_break:
                break
            if event.event_type == EventType.CHANGE:
                current_moment, should_continue = self._perform_change_event(
                    event, current_moment, desired_moment
                )
                if not should_continue:
                    break
            else:
                await self._perform_callback_event(
                    event, current_moment, desired_moment
                )
                self._process_command_deque()
        return current_moment

    async def _run(self, *args, offline=False, **kwargs):
        logger.debug(f"[{self.name}] Coroutine start")
        async with self._lock:
            self._process_command_deque(first_run=True)
            while self._is_running:
                logger.debug(f"[{self.name}] Loop start")
                if not await self._wait_for_queue():
                    return
                try:
                    current_moment = await self._wait_for_moment()
                except queue.Empty:
                    continue
                if current_moment is None:
                    return
                current_moment = await self._perform_events(current_moment)
                self._state = self._state._replace(
                    previous_seconds=current_moment.seconds,
                    previous_offset=current_moment.offset,
                )
                """
                if not offline:
                    try:
                        await asyncio.wait_for(self._condition.wait(), self._slop)
                    except (asyncio.TimeoutError, RuntimeError):
                        pass
                """
        logger.debug(f"[{self.name}] Coroutine terminating")

    async def _wait_for_moment(self, offline=False) -> Optional[Moment]:
        logger.debug(f"[{self.name}] ... Waiting for next moment")
        current_time = self.get_current_time()
        next_time = self._event_queue.peek().seconds
        while current_time < next_time:
            if not offline:
                try:
                    # TODO: Rewrite this without wait_for().
                    # TODO: Notify condition when scheduling / canceling.
                    sleep_time = min([self._slop, next_time - current_time])
                    await asyncio.wait_for(self._condition.wait(), sleep_time)
                except (asyncio.TimeoutError, RuntimeError):
                    pass
            if not self._is_running:
                return None
            self._process_command_deque()
            current_time = self.get_current_time()
            next_time = self._event_queue.peek().seconds
        return self._seconds_to_moment(current_time)

    async def _wait_for_queue(self, offline=False) -> bool:
        logger.debug(f"[{self.name}] ... Waiting for events")
        self._process_command_deque()
        while not self._event_queue.qsize():
            if not offline:
                try:
                    # TODO: Rewrite this without wait_for()
                    # TODO: Notify condition when scheduling / canceling.
                    # await asyncio.wait_for(self._condition.wait(), self._slop)
                    await self._condition.wait()
                except (asyncio.TimeoutError, RuntimeError):
                    pass
            if not self._is_running:
                return False
            self._process_command_deque()
        return True

    ### PUBLIC METHODS ###

    async def cancel(self, event_id) -> Optional[Tuple]:
        logger.debug(f"[{self.name}] Canceling {event_id}")
        event_id = self._cancel(event_id)
        async with self._lock:
            self._condition.notify()
        return event_id

    async def change(
        self,
        beats_per_minute: Optional[float] = None,
        time_signature: Optional[Tuple[int, int]] = None,
    ) -> Optional[int]:
        if not self._is_running:
            self._state = self._state._replace(
                beats_per_minute=beats_per_minute or self._state.beats_per_minute,
                time_signature=time_signature or self._state.time_signature,
            )
            return None
        event_id = next(self._counter)
        command = ChangeCommand(
            event_id=event_id,
            event_type=EventType.CHANGE,
            beats_per_minute=beats_per_minute,
            time_signature=time_signature,
            quantization=None,
            schedule_at=self.get_current_time(),
            time_unit=None,
        )
        await self._enqueue_command(command)
        return event_id

    async def cue(
        self,
        procedure,
        *,
        args=None,
        event_type: EventType = EventType.SCHEDULE,
        kwargs=None,
        quantization: str = None,
    ) -> int:
        if event_type <= 0:
            raise ValueError(f"Invalid event type {event_type}")
        elif quantization is not None and quantization not in self._valid_quantizations:
            raise ValueError(f"Invalid quantization: {quantization}")
        event_id = next(self._counter)
        command = CallbackCommand(
            args=args,
            event_id=event_id,
            event_type=event_type,
            kwargs=kwargs,
            procedure=procedure,
            quantization=quantization,
            schedule_at=self.get_current_time() if self.is_running else 0,
            time_unit=None,
        )
        await self._enqueue_command(command)
        return event_id

    async def cue_change(
        self,
        *,
        beats_per_minute: Optional[float] = None,
        quantization: str = None,
        time_signature: Optional[Tuple[int, int]] = None,
    ) -> int:
        if quantization is not None and quantization not in self._valid_quantizations:
            raise ValueError(f"Invalid quantization: {quantization}")
        event_id = next(self._counter)
        command = ChangeCommand(
            beats_per_minute=beats_per_minute,
            event_id=event_id,
            event_type=EventType.CHANGE,
            quantization=quantization,
            schedule_at=self.get_current_time() if self.is_running else 0,
            time_signature=time_signature,
            time_unit=None,
        )
        await self._enqueue_command(command)
        return event_id

    async def reschedule(
        self, event_id, *, schedule_at=0.0, time_unit=TimeUnit.BEATS
    ) -> Optional[int]:
        event_or_command = await self.cancel(event_id)
        if event_or_command is None:
            return None
        if isinstance(event_or_command, (CallbackCommand, ChangeCommand)):
            command = event_or_command._replace(
                schedule_at=schedule_at, time_unit=time_unit
            )
        elif isinstance(event_or_command, CallbackEvent):
            command = CallbackCommand(
                args=event_or_command.args,
                event_id=event_or_command.event_id,
                event_type=event_or_command.event_type,
                kwargs=event_or_command.kwargs,
                procedure=event_or_command.procedure,
                quantization=None,
                schedule_at=schedule_at,
                time_unit=time_unit,
            )
        elif isinstance(event_or_command, ChangeEvent):
            command = ChangeCommand(
                beats_per_minute=event_or_command.beats_per_minute,
                event_id=event_or_command.event_id,
                event_type=EventType.CHANGE,
                quantization=None,
                schedule_at=schedule_at,
                time_signature=event_or_command.time_signature,
                time_unit=time_unit,
            )
        await self._enqueue_command(command)
        return event_id

    async def schedule(
        self,
        procedure,
        *,
        event_type: EventType = EventType.SCHEDULE,
        schedule_at: float = 0.0,
        time_unit: TimeUnit = TimeUnit.BEATS,
        args=None,
        kwargs=None,
    ) -> int:
        logger.debug(f"[{self.name}] Scheduling {procedure}")
        if event_type <= 0:
            raise ValueError(f"Invalid event type {event_type}")
        event_id = next(self._counter)
        command = CallbackCommand(
            args=args,
            event_id=event_id,
            event_type=event_type,
            kwargs=kwargs,
            procedure=procedure,
            quantization=None,
            schedule_at=schedule_at,
            time_unit=time_unit,
        )
        await self._enqueue_command(command)
        return event_id

    async def schedule_change(
        self,
        *,
        beats_per_minute: Optional[float] = None,
        schedule_at: float = 0.0,
        time_signature: Optional[Tuple[int, int]] = None,
        time_unit: TimeUnit = TimeUnit.BEATS,
        moment: Moment = None,
    ) -> int:
        event_id = next(self._counter)
        command = ChangeCommand(
            beats_per_minute=beats_per_minute,
            event_id=event_id,
            event_type=EventType.CHANGE,
            quantization=None,
            schedule_at=schedule_at,
            time_signature=time_signature,
            time_unit=time_unit,
        )
        await self._enqueue_command(command)
        return event_id

    async def start(
        self,
        initial_time: Optional[float] = None,
        initial_offset: float = 0.0,
        initial_measure: int = 1,
        beats_per_minute: Optional[float] = None,
        time_signature: Optional[Tuple[int, int]] = None,
    ):
        if self._is_running:
            raise RuntimeError("Already started")
        if initial_time is None:
            initial_time = self.get_current_time()
        self._state = ClockState(
            beats_per_minute=beats_per_minute or self._state.beats_per_minute,
            initial_seconds=initial_time,
            previous_measure=int(initial_measure),
            previous_offset=float(initial_offset),
            previous_seconds=float(initial_time),
            previous_time_signature_change_offset=float(initial_offset),
            time_signature=time_signature or self._state.time_signature,
        )
        self._is_running = True
        loop = asyncio.get_running_loop()
        self._task = loop.create_task(self._run())

    async def stop(self):
        if not self._is_running:
            return
        self._is_running = False
        async with self._lock:
            self._condition.notify()
        await self._task
