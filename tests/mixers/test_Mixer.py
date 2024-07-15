from typing import List, Union

import pytest

from supriya import OscBundle, OscMessage
from supriya.mixers import Session
from supriya.mixers.mixers import Mixer

from .conftest import assert_diff, capture, debug_tree


@pytest.mark.parametrize("online", [False, True])
@pytest.mark.parametrize(
    "expected_commands, expected_diff",
    [
        (
            [
                OscBundle(
                    contents=(
                        OscMessage("/c_set", 11, 1.0, 12, 0.0),
                        OscMessage("/c_fill", 13, 2, 0.0, 15, 2, 0.0),
                        OscMessage(
                            "/g_new", 1014, 1, 1001, 1015, 0, 1014, 1016, 1, 1014
                        ),
                        OscMessage(
                            "/s_new",
                            "supriya:channel-strip:2",
                            1017,
                            1,
                            1014,
                            "active",
                            "c11",
                            "bus",
                            20.0,
                            "gain",
                            "c12",
                        ),
                        OscMessage(
                            "/s_new",
                            "supriya:meters:2",
                            1018,
                            3,
                            1015,
                            "in_",
                            20.0,
                            "out",
                            13.0,
                        ),
                        OscMessage(
                            "/s_new",
                            "supriya:meters:2",
                            1019,
                            3,
                            1017,
                            "in_",
                            20.0,
                            "out",
                            15.0,
                        ),
                    ),
                ),
                OscMessage(
                    "/s_new",
                    "supriya:patch-cable:2x2",
                    1020,
                    1,
                    1014,
                    "active",
                    "c11",
                    "in_",
                    20.0,
                    "out",
                    16.0,
                ),
            ],
            """
            --- initial
            +++ mutation
            @@ -12,6 +12,17 @@
                                 in_: 18.0, out: 9.0
                             1012 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].output:synth)
                                 active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 16.0
            +            1014 group (session.mixers[0].tracks[1]:group)
            +                1015 group (session.mixers[0].tracks[1]:tracks)
            +                1018 supriya:meters:2 (session.mixers[0].tracks[1]:input-levels)
            +                    in_: 20.0, out: 13.0
            +                1016 group (session.mixers[0].tracks[1]:devices)
            +                1017 supriya:channel-strip:2 (session.mixers[0].tracks[1]:channel-strip)
            +                    active: c11, bus: 20.0, gain: c12, gate: 1.0
            +                1019 supriya:meters:2 (session.mixers[0].tracks[1]:output-levels)
            +                    in_: 20.0, out: 15.0
            +                1020 supriya:patch-cable:2x2 (session.mixers[0].tracks[1].output:synth)
            +                    active: c11, gain: 0.0, gate: 1.0, in_: 20.0, out: 16.0
                     1004 supriya:meters:2 (session.mixers[0]:input-levels)
                         in_: 16.0, out: 1.0
                     1002 group (session.mixers[0]:devices)
            """,
        ),
    ],
)
@pytest.mark.asyncio
async def test_Mixer_add_track(
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
        await debug_tree(session)
    # Operation
    print("Operation")
    with capture(mixer.context) as commands:
        track = await mixer.add_track()
    # Post-conditions
    print("Post-conditions")
    assert track in mixer.tracks
    assert track.parent is mixer
    assert mixer.tracks[-1] is track
    if not online:
        return
    await assert_diff(
        session,
        expected_diff,
        expected_initial_tree="""
        <session.contexts[0]>
            NODE TREE 1000 group (session.mixers[0]:group)
                1001 group (session.mixers[0]:tracks)
                    1006 group (session.mixers[0].tracks[0]:group)
                        1007 group (session.mixers[0].tracks[0]:tracks)
                        1010 supriya:meters:2 (session.mixers[0].tracks[0]:input-levels)
                            in_: 18.0, out: 7.0
                        1008 group (session.mixers[0].tracks[0]:devices)
                        1009 supriya:channel-strip:2 (session.mixers[0].tracks[0]:channel-strip)
                            active: c5, bus: 18.0, gain: c6, gate: 1.0
                        1011 supriya:meters:2 (session.mixers[0].tracks[0]:output-levels)
                            in_: 18.0, out: 9.0
                        1012 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].output:synth)
                            active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 16.0
                1004 supriya:meters:2 (session.mixers[0]:input-levels)
                    in_: 16.0, out: 1.0
                1002 group (session.mixers[0]:devices)
                1003 supriya:channel-strip:2 (session.mixers[0]:channel-strip)
                    active: 1.0, bus: 16.0, gain: c0, gate: 1.0
                1005 supriya:meters:2 (session.mixers[0]:output-levels)
                    in_: 16.0, out: 3.0
                1013 supriya:patch-cable:2x2 (session.mixers[0].output:synth)
                    active: 1.0, gain: 0.0, gate: 1.0, in_: 16.0, out: 0.0
        """,
    )
    assert commands == expected_commands


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
