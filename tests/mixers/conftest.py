import contextlib
import difflib
from typing import List, Optional, Union

import pytest
from uqbar.strings import normalize

from supriya import AsyncServer, OscBundle, OscMessage
from supriya.mixers import Session
from supriya.mixers.mixers import Mixer
from supriya.mixers.tracks import Track


@contextlib.contextmanager
def capture(context: Optional[AsyncServer]):
    entries: List[Union[OscBundle, OscMessage]] = []
    if context is None:
        yield entries
    else:
        with context.osc_protocol.capture() as transcript:
            yield entries
    entries.extend(transcript.filtered(received=False, status=False))


async def debug_tree(session: Session, label: str = "initial tree") -> str:
    tree = str(await session.dump_tree())
    for i, context in enumerate(session.contexts):
        tree = tree.replace(repr(context), f"<session.contexts[{i}]>")
    print(f"{label}:\n{tree}")
    return tree


async def assert_diff(
    session: Session, expected_diff: str, expected_initial_tree: str
) -> None:
    await session.sync()
    print(f"expected initial tree:\n{normalize(expected_initial_tree)}")
    actual_tree = await debug_tree(session, "actual tree")
    actual_diff = "".join(
        difflib.unified_diff(
            normalize(expected_initial_tree).splitlines(True),
            actual_tree.splitlines(True),
            tofile="mutation",
            fromfile="initial",
        )
    )
    print(f"actual diff:\n{normalize(actual_diff)}")
    assert normalize(expected_diff) == normalize(actual_diff)


does_not_raise = contextlib.nullcontext()


@pytest.fixture
def mixer(session: Session) -> Mixer:
    return session.mixers[0]


@pytest.fixture
def session() -> Session:
    return Session()


@pytest.fixture
def track(mixer: Mixer) -> Track:
    return mixer.tracks[0]
