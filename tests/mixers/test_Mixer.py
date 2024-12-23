from typing import List, Union

import pytest

from supriya import OscBundle, OscMessage
from supriya.mixers import Session
from supriya.mixers.mixers import Mixer

from .conftest import assert_diff, capture


@pytest.mark.xfail
@pytest.mark.parametrize("online", [False, True])
@pytest.mark.parametrize(
    "expected_commands, expected_diff",
    [
        (
            [
                OscMessage("/n_set", 1000, "gate", 0.0),
                OscMessage("/n_set", 1004, "gate", 0.0),
            ],
            "",
        ),
    ],
)
@pytest.mark.asyncio
async def test_Mixer_delete(
    expected_commands: List[Union[OscBundle, OscMessage]],
    expected_diff: str,
    mixer: Mixer,
    online: bool,
    session: Session,
) -> None:
    # Pre-conditions
    print("Pre-conditions")
    if online:
        await session.boot()
    # Operation
    print("Operation")
    with capture(mixer.context) as commands:
        await mixer.delete()
    # Post-conditions
    print("Post-conditions")
    if not online:
        raise Exception
    await assert_diff(
        session,
        expected_diff,
        expected_initial_tree="""
        <session.contexts[0]>
        """,
    )
    assert commands == expected_commands
    raise Exception
