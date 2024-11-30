from typing import Dict, List, Optional, Union

import pytest

from supriya import OscBundle, OscMessage
from supriya.mixers import Session
from supriya.mixers.mixers import Mixer
from supriya.mixers.synthdefs import DEVICE_DC_TESTER_2
from supriya.mixers.tracks import Track, TrackContainer
from supriya.typing import DEFAULT, Default

from .conftest import assert_diff, capture, debug_tree, does_not_raise


@pytest_asyncio.fixture
async def complex_session() -> Session:
    session = Session()
    await sesison.add_mixer()
    mixer_one = session.mixers[0]
    session.mixers[1]
    await session.boot()
    await session.quit()
    return session


@pytest.mark.parametrize("online", [False, True])
@pytest.mark.parametrize(
    "expected_commands, expected_diff",
    [
        (
            [
                OscMessage("/d_recv", DEVICE_DC_TESTER_2.compile()),
                OscMessage("/sync", 2),
                OscBundle(
                    contents=(
                        OscMessage("/g_new", 1014, 1, 1008),
                        OscMessage(
                            "/s_new", "supriya:device-dc-tester:2", 1015, 1, 1014
                        ),
                    ),
                ),
            ],
            """
            --- initial
            +++ mutation
            @@ -6,6 +6,9 @@
                             1010 supriya:meters:2 (session.mixers[0].tracks[0]:input-levels)
                                 in_: 18.0, out: 7.0
                             1008 group (session.mixers[0].tracks[0]:devices)
            +                    1014 group (session.mixers[0].tracks[0].devices[0]:group)
            +                        1015 supriya:device-dc-tester:2 (session.mixers[0].tracks[0].devices[0]:synth)
            +                            dc: 1.0, out: 0.0
                             1009 supriya:channel-strip:2 (session.mixers[0].tracks[0]:channel-strip)
                                 active: c5, bus: 18.0, gain: c6, gate: 1.0
                             1011 supriya:meters:2 (session.mixers[0].tracks[0]:output-levels)
            """,
        ),
    ],
)
@pytest.mark.asyncio
async def test_Track_add_device(
    expected_commands: List[Union[OscBundle, OscMessage]],
    expected_diff: str,
    mixer: Mixer,
    online: bool,
    session: Session,
    track: Track,
) -> None:
    # Pre-conditions
    if online:
        await session.boot()
    # Operation
    with capture(mixer.context) as commands:
        device = await track.add_device()
    # Post-conditions
    assert device in track.devices
    assert device.parent is track
    assert track.devices[0] is device
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


@pytest.mark.parametrize("online", [False, True])
@pytest.mark.parametrize(
    "postfader, source, target, expected_commands, expected_diff",
    [
        (
            True,
            "self",
            "mixer",
            [
                OscMessage(
                    "/s_new",
                    "supriya:patch-cable:2x2",
                    1021,
                    3,
                    1009,
                    "active",
                    "c5",
                    "in_",
                    18.0,
                    "out",
                    16.0,
                )
            ],
            """
            --- initial
            +++ mutation
            @@ -8,6 +8,8 @@
                             1008 group (session.mixers[0].tracks[0]:devices)
                             1009 supriya:channel-strip:2 (session.mixers[0].tracks[0]:channel-strip)
                                 active: c5, bus: 18.0, gain: c6, gate: 1.0
            +                1021 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].sends[0]:synth)
            +                    active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 16.0
                             1011 supriya:meters:2 (session.mixers[0].tracks[0]:output-levels)
                                 in_: 18.0, out: 9.0
                             1012 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].output:synth)
            """,
        ),
        (
            True,
            "self",
            "other",
            [
                OscMessage(
                    "/s_new",
                    "supriya:patch-cable:2x2",
                    1021,
                    3,
                    1009,
                    "active",
                    "c5",
                    "in_",
                    18.0,
                    "out",
                    20.0,
                )
            ],
            """
            --- initial
            +++ mutation
            @@ -8,6 +8,8 @@
                             1008 group (session.mixers[0].tracks[0]:devices)
                             1009 supriya:channel-strip:2 (session.mixers[0].tracks[0]:channel-strip)
                                 active: c5, bus: 18.0, gain: c6, gate: 1.0
            +                1021 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].sends[0]:synth)
            +                    active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 20.0
                             1011 supriya:meters:2 (session.mixers[0].tracks[0]:output-levels)
                                 in_: 18.0, out: 9.0
                             1012 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].output:synth)
            """,
        ),
        (
            False,
            "self",
            "other",
            [
                OscMessage(
                    "/s_new",
                    "supriya:patch-cable:2x2",
                    1021,
                    2,
                    1009,
                    "active",
                    "c5",
                    "in_",
                    18.0,
                    "out",
                    20.0,
                )
            ],
            """
            --- initial
            +++ mutation
            @@ -6,6 +6,8 @@
                             1010 supriya:meters:2 (session.mixers[0].tracks[0]:input-levels)
                                 in_: 18.0, out: 7.0
                             1008 group (session.mixers[0].tracks[0]:devices)
            +                1021 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].sends[0]:synth)
            +                    active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 20.0
                             1009 supriya:channel-strip:2 (session.mixers[0].tracks[0]:channel-strip)
                                 active: c5, bus: 18.0, gain: c6, gate: 1.0
                             1011 supriya:meters:2 (session.mixers[0].tracks[0]:output-levels)
            """,
        ),
        (
            False,
            "self",
            "self",
            [
                OscMessage(
                    "/s_new",
                    "supriya:fb-patch-cable:2x2",
                    1021,
                    0,
                    1006,
                    "active",
                    "c5",
                    "in_",
                    22.0,
                    "out",
                    18.0,
                ),
                OscMessage(
                    "/s_new",
                    "supriya:patch-cable:2x2",
                    1022,
                    2,
                    1009,
                    "active",
                    "c5",
                    "in_",
                    18.0,
                    "out",
                    22.0,
                ),
            ],
            """
            --- initial
            +++ mutation
            @@ -2,10 +2,14 @@
                 NODE TREE 1000 group (session.mixers[0]:group)
                     1001 group (session.mixers[0]:tracks)
                         1006 group (session.mixers[0].tracks[0]:group)
            +                1021 supriya:fb-patch-cable:2x2 (session.mixers[0].tracks[0].feedback:synth)
            +                    active: c5, gain: 0.0, gate: 1.0, in_: 22.0, out: 18.0
                             1007 group (session.mixers[0].tracks[0]:tracks)
                             1010 supriya:meters:2 (session.mixers[0].tracks[0]:input-levels)
                                 in_: 18.0, out: 7.0
                             1008 group (session.mixers[0].tracks[0]:devices)
            +                1022 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].sends[0]:synth)
            +                    active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 22.0
                             1009 supriya:channel-strip:2 (session.mixers[0].tracks[0]:channel-strip)
                                 active: c5, bus: 18.0, gain: c6, gate: 1.0
                             1011 supriya:meters:2 (session.mixers[0].tracks[0]:output-levels)
            """,
        ),
        (
            True,
            "other",
            "self",
            [
                OscMessage(
                    "/s_new",
                    "supriya:fb-patch-cable:2x2",
                    1021,
                    0,
                    1006,
                    "active",
                    "c5",
                    "in_",
                    22.0,
                    "out",
                    18.0,
                ),
                OscMessage(
                    "/s_new",
                    "supriya:patch-cable:2x2",
                    1022,
                    3,
                    1017,
                    "active",
                    "c11",
                    "in_",
                    20.0,
                    "out",
                    22.0,
                ),
            ],
            """
            --- initial
            +++ mutation
            @@ -2,6 +2,8 @@
                 NODE TREE 1000 group (session.mixers[0]:group)
                     1001 group (session.mixers[0]:tracks)
                         1006 group (session.mixers[0].tracks[0]:group)
            +                1021 supriya:fb-patch-cable:2x2 (session.mixers[0].tracks[0].feedback:synth)
            +                    active: c5, gain: 0.0, gate: 1.0, in_: 22.0, out: 18.0
                             1007 group (session.mixers[0].tracks[0]:tracks)
                             1010 supriya:meters:2 (session.mixers[0].tracks[0]:input-levels)
                                 in_: 18.0, out: 7.0
            @@ -19,6 +21,8 @@
                             1016 group (session.mixers[0].tracks[1]:devices)
                             1017 supriya:channel-strip:2 (session.mixers[0].tracks[1]:channel-strip)
                                 active: c11, bus: 20.0, gain: c12, gate: 1.0
            +                1022 supriya:patch-cable:2x2 (session.mixers[0].tracks[1].sends[0]:synth)
            +                    active: c11, gain: 0.0, gate: 1.0, in_: 20.0, out: 22.0
                             1019 supriya:meters:2 (session.mixers[0].tracks[1]:output-levels)
                                 in_: 20.0, out: 15.0
                             1020 supriya:patch-cable:2x2 (session.mixers[0].tracks[1].output:synth)
            """,
        ),
    ],
)
@pytest.mark.asyncio
async def test_Track_add_send(
    expected_commands: List[Union[OscBundle, OscMessage]],
    expected_diff: str,
    mixer: Mixer,
    online: bool,
    postfader: bool,
    session: Session,
    source: str,
    target: str,
    track: Track,
) -> None:
    # Pre-conditions
    if online:
        await session.boot()
    targets: Dict[str, TrackContainer] = {
        "mixer": mixer,
        "other": await mixer.add_track(),
        "self": track,
    }
    source_ = targets[source]
    target_ = targets[target]
    assert isinstance(source_, Track)
    if online:
        await debug_tree(session)
    # Operation
    with capture(mixer.context) as commands:
        send = await source_.add_send(postfader=postfader, target=target_)
    # Post-conditions
    assert send in source_.sends
    assert send.parent is source_
    assert send.postfader == postfader
    assert send.target is target_
    assert source_.sends[0] is send
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
                    1014 group (session.mixers[0].tracks[1]:group)
                        1015 group (session.mixers[0].tracks[1]:tracks)
                        1018 supriya:meters:2 (session.mixers[0].tracks[1]:input-levels)
                            in_: 20.0, out: 13.0
                        1016 group (session.mixers[0].tracks[1]:devices)
                        1017 supriya:channel-strip:2 (session.mixers[0].tracks[1]:channel-strip)
                            active: c11, bus: 20.0, gain: c12, gate: 1.0
                        1019 supriya:meters:2 (session.mixers[0].tracks[1]:output-levels)
                            in_: 20.0, out: 15.0
                        1020 supriya:patch-cable:2x2 (session.mixers[0].tracks[1].output:synth)
                            active: c11, gain: 0.0, gate: 1.0, in_: 20.0, out: 16.0
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


@pytest.mark.parametrize("online", [False, True])
@pytest.mark.asyncio
async def test_Track_add_track(
    mixer: Mixer,
    online: bool,
    session: Session,
    track: Track,
) -> None:
    # Pre-conditions
    if online:
        await session.boot()
    # Operation
    with capture(mixer.context) as commands:
        child_track = await track.add_track()
    # Post-conditions
    assert child_track in track.tracks
    assert child_track.parent is track
    assert track.tracks[0] is child_track
    if not online:
        return
    await assert_diff(
        session,
        expected_diff="""
        --- initial
        +++ mutation
        @@ -3,6 +3,17 @@
                 1001 group (session.mixers[0]:tracks)
                     1006 group (session.mixers[0].tracks[0]:group)
                         1007 group (session.mixers[0].tracks[0]:tracks)
        +                    1014 group (session.mixers[0].tracks[0].tracks[0]:group)
        +                        1015 group (session.mixers[0].tracks[0].tracks[0]:tracks)
        +                        1018 supriya:meters:2 (session.mixers[0].tracks[0].tracks[0]:input-levels)
        +                            in_: 20.0, out: 13.0
        +                        1016 group (session.mixers[0].tracks[0].tracks[0]:devices)
        +                        1017 supriya:channel-strip:2 (session.mixers[0].tracks[0].tracks[0]:channel-strip)
        +                            active: c11, bus: 20.0, gain: c12, gate: 1.0
        +                        1019 supriya:meters:2 (session.mixers[0].tracks[0].tracks[0]:output-levels)
        +                            in_: 20.0, out: 15.0
        +                        1020 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].output:synth)
        +                            active: c11, gain: 0.0, gate: 1.0, in_: 20.0, out: 18.0
                         1010 supriya:meters:2 (session.mixers[0].tracks[0]:input-levels)
                             in_: 18.0, out: 7.0
                         1008 group (session.mixers[0].tracks[0]:devices)
        """,
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
    assert commands == [
        OscBundle(
            contents=(
                OscMessage("/c_set", 11, 1.0, 12, 0.0),
                OscMessage("/c_fill", 13, 2, 0.0, 15, 2, 0.0),
                OscMessage("/g_new", 1014, 1, 1007, 1015, 0, 1014, 1016, 1, 1014),
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
            18.0,
        ),
    ]


@pytest.mark.xfail
@pytest.mark.parametrize("online", [False, True])
@pytest.mark.parametrize(
    "target, expected_commands, expected_diff",
    [
        ("parent", [], ""),
        ("self", [], ""),
        ("child", [], ""),
        ("sibling", [], ""),
    ],
)
@pytest.mark.asyncio
async def test_Track_delete(
    expected_commands: List[Union[OscBundle, OscMessage]],
    expected_diff: str,
    online: bool,
    mixer: Mixer,
    session: Session,
    target: str,
) -> None:
    # Pre-conditions
    if online:
        await session.boot()
    targets: Dict[str, Track] = {
        "parent": (parent := await mixer.add_track()),
        "self": (track := await parent.add_track()),
        "child": await track.add_track(),
        "sibling": (sibling := await mixer.add_track()),
    }
    await sibling.set_output(track)
    target_ = targets[target]
    parent_ = target_.parent
    # Operation
    with capture(mixer.context) as commands:
        await target_.delete()
    # Post-conditions
    assert parent_ and target_ not in parent_.children
    if not online:
        raise Exception
    await assert_diff(
        session,
        expected_diff,
        expected_initial_tree="""
        """,
    )
    assert commands == expected_commands
    raise Exception


@pytest.mark.parametrize("online", [False, True])
@pytest.mark.parametrize(
    "parent, index, maybe_raises, expected_graph_order, expected_diff, expected_commands",
    [
        ("self", 0, pytest.raises(RuntimeError), (0, 0), "", []),
        ("mixer", 0, does_not_raise, (0, 0), "", []),
        (
            "mixer",
            1,
            does_not_raise,
            (0, 1),
            """
            --- initial
            +++ mutation
            @@ -1,30 +1,30 @@
             <session.contexts[0]>
                 NODE TREE 1000 group (session.mixers[0]:group)
                     1001 group (session.mixers[0]:tracks)
            -            1006 group (session.mixers[0].tracks[0]:group)
            -                1007 group (session.mixers[0].tracks[0]:tracks)
            -                1010 supriya:meters:2 (session.mixers[0].tracks[0]:input-levels)
            +            1014 group (session.mixers[0].tracks[0]:group)
            +                1015 group (session.mixers[0].tracks[0]:tracks)
            +                1018 supriya:meters:2 (session.mixers[0].tracks[0]:input-levels)
            +                    in_: 20.0, out: 13.0
            +                1016 group (session.mixers[0].tracks[0]:devices)
            +                1017 supriya:channel-strip:2 (session.mixers[0].tracks[0]:channel-strip)
            +                    active: c11, bus: 20.0, gain: c12, gate: 1.0
            +                1019 supriya:meters:2 (session.mixers[0].tracks[0]:output-levels)
            +                    in_: 20.0, out: 15.0
            +                1020 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].output:synth)
            +                    active: c11, gain: 0.0, gate: 1.0, in_: 20.0, out: 16.0
            +            1006 group (session.mixers[0].tracks[1]:group)
            +                1007 group (session.mixers[0].tracks[1]:tracks)
            +                1010 supriya:meters:2 (session.mixers[0].tracks[1]:input-levels)
                                 in_: 18.0, out: 7.0
            -                1008 group (session.mixers[0].tracks[0]:devices)
            -                1009 supriya:channel-strip:2 (session.mixers[0].tracks[0]:channel-strip)
            +                1008 group (session.mixers[0].tracks[1]:devices)
            +                1009 supriya:channel-strip:2 (session.mixers[0].tracks[1]:channel-strip)
                                 active: c5, bus: 18.0, gain: c6, gate: 1.0
            -                1042 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].sends[0]:synth)
            +                1042 supriya:patch-cable:2x2 (session.mixers[0].tracks[1].sends[0]:synth)
                                 active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 22.0
            -                1011 supriya:meters:2 (session.mixers[0].tracks[0]:output-levels)
            +                1011 supriya:meters:2 (session.mixers[0].tracks[1]:output-levels)
                                 in_: 18.0, out: 9.0
            -                1012 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].output:synth)
            +                1012 supriya:patch-cable:2x2 (session.mixers[0].tracks[1].output:synth)
                                 active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 16.0
            -            1014 group (session.mixers[0].tracks[1]:group)
            -                1015 group (session.mixers[0].tracks[1]:tracks)
            -                1018 supriya:meters:2 (session.mixers[0].tracks[1]:input-levels)
            -                    in_: 20.0, out: 13.0
            -                1016 group (session.mixers[0].tracks[1]:devices)
            -                1017 supriya:channel-strip:2 (session.mixers[0].tracks[1]:channel-strip)
            -                    active: c11, bus: 20.0, gain: c12, gate: 1.0
            -                1019 supriya:meters:2 (session.mixers[0].tracks[1]:output-levels)
            -                    in_: 20.0, out: 15.0
            -                1020 supriya:patch-cable:2x2 (session.mixers[0].tracks[1].output:synth)
            -                    active: c11, gain: 0.0, gate: 1.0, in_: 20.0, out: 16.0
                         1021 group (session.mixers[0].tracks[2]:group)
                             1022 group (session.mixers[0].tracks[2]:tracks)
                             1025 supriya:meters:2 (session.mixers[0].tracks[2]:input-levels)
            """,
            [OscMessage("/n_after", 1006, 1014)],
        ),
        (
            "mixer",
            2,
            does_not_raise,
            (0, 2),
            """
            --- initial
            +++ mutation
            @@ -1,41 +1,45 @@
             <session.contexts[0]>
                 NODE TREE 1000 group (session.mixers[0]:group)
                     1001 group (session.mixers[0]:tracks)
            -            1006 group (session.mixers[0].tracks[0]:group)
            -                1007 group (session.mixers[0].tracks[0]:tracks)
            -                1010 supriya:meters:2 (session.mixers[0].tracks[0]:input-levels)
            +            1014 group (session.mixers[0].tracks[0]:group)
            +                1015 group (session.mixers[0].tracks[0]:tracks)
            +                1018 supriya:meters:2 (session.mixers[0].tracks[0]:input-levels)
            +                    in_: 20.0, out: 13.0
            +                1016 group (session.mixers[0].tracks[0]:devices)
            +                1017 supriya:channel-strip:2 (session.mixers[0].tracks[0]:channel-strip)
            +                    active: c11, bus: 20.0, gain: c12, gate: 1.0
            +                1019 supriya:meters:2 (session.mixers[0].tracks[0]:output-levels)
            +                    in_: 20.0, out: 15.0
            +                1020 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].output:synth)
            +                    active: c11, gain: 0.0, gate: 1.0, in_: 20.0, out: 16.0
            +            1021 group (session.mixers[0].tracks[1]:group)
            +                1043 supriya:fb-patch-cable:2x2 (session.mixers[0].tracks[1].feedback:synth)
            +                    active: c17, gain: 0.0, gate: 1.0, in_: 28.0, out: 22.0
            +                1022 group (session.mixers[0].tracks[1]:tracks)
            +                1025 supriya:meters:2 (session.mixers[0].tracks[1]:input-levels)
            +                    in_: 22.0, out: 19.0
            +                1023 group (session.mixers[0].tracks[1]:devices)
            +                1024 supriya:channel-strip:2 (session.mixers[0].tracks[1]:channel-strip)
            +                    active: c17, bus: 22.0, gain: c18, gate: 1.0
            +                1026 supriya:meters:2 (session.mixers[0].tracks[1]:output-levels)
            +                    in_: 22.0, out: 21.0
            +                1027 supriya:patch-cable:2x2 (session.mixers[0].tracks[1].output:synth)
            +                    active: c17, gain: 0.0, gate: 1.0, in_: 22.0, out: 16.0
            +            1006 group (session.mixers[0].tracks[2]:group)
            +                1007 group (session.mixers[0].tracks[2]:tracks)
            +                1010 supriya:meters:2 (session.mixers[0].tracks[2]:input-levels)
                                 in_: 18.0, out: 7.0
            -                1008 group (session.mixers[0].tracks[0]:devices)
            -                1009 supriya:channel-strip:2 (session.mixers[0].tracks[0]:channel-strip)
            +                1008 group (session.mixers[0].tracks[2]:devices)
            +                1009 supriya:channel-strip:2 (session.mixers[0].tracks[2]:channel-strip)
                                 active: c5, bus: 18.0, gain: c6, gate: 1.0
            -                1042 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].sends[0]:synth)
            -                    active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 22.0
            -                1011 supriya:meters:2 (session.mixers[0].tracks[0]:output-levels)
            +                1044 supriya:patch-cable:2x2 (session.mixers[0].tracks[2].sends[0]:synth)
            +                    active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 28.0
            +                1042 supriya:patch-cable:2x2
            +                    active: c5, gain: 0.0, gate: 0.0, in_: 18.0, out: 22.0
            +                1011 supriya:meters:2 (session.mixers[0].tracks[2]:output-levels)
                                 in_: 18.0, out: 9.0
            -                1012 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].output:synth)
            +                1012 supriya:patch-cable:2x2 (session.mixers[0].tracks[2].output:synth)
                                 active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 16.0
            -            1014 group (session.mixers[0].tracks[1]:group)
            -                1015 group (session.mixers[0].tracks[1]:tracks)
            -                1018 supriya:meters:2 (session.mixers[0].tracks[1]:input-levels)
            -                    in_: 20.0, out: 13.0
            -                1016 group (session.mixers[0].tracks[1]:devices)
            -                1017 supriya:channel-strip:2 (session.mixers[0].tracks[1]:channel-strip)
            -                    active: c11, bus: 20.0, gain: c12, gate: 1.0
            -                1019 supriya:meters:2 (session.mixers[0].tracks[1]:output-levels)
            -                    in_: 20.0, out: 15.0
            -                1020 supriya:patch-cable:2x2 (session.mixers[0].tracks[1].output:synth)
            -                    active: c11, gain: 0.0, gate: 1.0, in_: 20.0, out: 16.0
            -            1021 group (session.mixers[0].tracks[2]:group)
            -                1022 group (session.mixers[0].tracks[2]:tracks)
            -                1025 supriya:meters:2 (session.mixers[0].tracks[2]:input-levels)
            -                    in_: 22.0, out: 19.0
            -                1023 group (session.mixers[0].tracks[2]:devices)
            -                1024 supriya:channel-strip:2 (session.mixers[0].tracks[2]:channel-strip)
            -                    active: c17, bus: 22.0, gain: c18, gate: 1.0
            -                1026 supriya:meters:2 (session.mixers[0].tracks[2]:output-levels)
            -                    in_: 22.0, out: 21.0
            -                1027 supriya:patch-cable:2x2 (session.mixers[0].tracks[2].output:synth)
            -                    active: c17, gain: 0.0, gate: 1.0, in_: 22.0, out: 16.0
                     1004 supriya:meters:2 (session.mixers[0]:input-levels)
                         in_: 16.0, out: 1.0
                     1002 group (session.mixers[0]:devices)
            """,
            [
                OscMessage("/n_after", 1006, 1021),
                OscMessage(
                    "/s_new",
                    "supriya:fb-patch-cable:2x2",
                    1043,
                    0,
                    1021,
                    "active",
                    "c17",
                    "in_",
                    28.0,
                    "out",
                    22.0,
                ),
                OscBundle(
                    contents=(
                        OscMessage("/n_set", 1042, "gate", 0.0),
                        OscMessage(
                            "/s_new",
                            "supriya:patch-cable:2x2",
                            1044,
                            3,
                            1009,
                            "active",
                            "c5",
                            "in_",
                            18.0,
                            "out",
                            28.0,
                        ),
                    ),
                ),
            ],
        ),
        (
            "other",
            0,
            does_not_raise,
            (0, 0, 2),
            """
            --- initial
            +++ mutation
            @@ -1,40 +1,42 @@
             <session.contexts[0]>
                 NODE TREE 1000 group (session.mixers[0]:group)
                     1001 group (session.mixers[0]:tracks)
            -            1006 group (session.mixers[0].tracks[0]:group)
            -                1007 group (session.mixers[0].tracks[0]:tracks)
            -                1010 supriya:meters:2 (session.mixers[0].tracks[0]:input-levels)
            -                    in_: 18.0, out: 7.0
            -                1008 group (session.mixers[0].tracks[0]:devices)
            -                1009 supriya:channel-strip:2 (session.mixers[0].tracks[0]:channel-strip)
            -                    active: c5, bus: 18.0, gain: c6, gate: 1.0
            -                1042 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].sends[0]:synth)
            -                    active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 22.0
            -                1011 supriya:meters:2 (session.mixers[0].tracks[0]:output-levels)
            -                    in_: 18.0, out: 9.0
            -                1012 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].output:synth)
            -                    active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 16.0
            -            1014 group (session.mixers[0].tracks[1]:group)
            -                1015 group (session.mixers[0].tracks[1]:tracks)
            -                1018 supriya:meters:2 (session.mixers[0].tracks[1]:input-levels)
            +            1014 group (session.mixers[0].tracks[0]:group)
            +                1015 group (session.mixers[0].tracks[0]:tracks)
            +                    1006 group (session.mixers[0].tracks[0].tracks[0]:group)
            +                        1007 group (session.mixers[0].tracks[0].tracks[0]:tracks)
            +                        1010 supriya:meters:2 (session.mixers[0].tracks[0].tracks[0]:input-levels)
            +                            in_: 18.0, out: 7.0
            +                        1008 group (session.mixers[0].tracks[0].tracks[0]:devices)
            +                        1009 supriya:channel-strip:2 (session.mixers[0].tracks[0].tracks[0]:channel-strip)
            +                            active: c5, bus: 18.0, gain: c6, gate: 1.0
            +                        1042 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].sends[0]:synth)
            +                            active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 22.0
            +                        1011 supriya:meters:2 (session.mixers[0].tracks[0].tracks[0]:output-levels)
            +                            in_: 18.0, out: 9.0
            +                        1012 supriya:patch-cable:2x2
            +                            active: c5, gain: 0.0, gate: 0.0, in_: 18.0, out: 16.0
            +                        1043 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].output:synth)
            +                            active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 20.0
            +                1018 supriya:meters:2 (session.mixers[0].tracks[0]:input-levels)
                                 in_: 20.0, out: 13.0
            -                1016 group (session.mixers[0].tracks[1]:devices)
            -                1017 supriya:channel-strip:2 (session.mixers[0].tracks[1]:channel-strip)
            +                1016 group (session.mixers[0].tracks[0]:devices)
            +                1017 supriya:channel-strip:2 (session.mixers[0].tracks[0]:channel-strip)
                                 active: c11, bus: 20.0, gain: c12, gate: 1.0
            -                1019 supriya:meters:2 (session.mixers[0].tracks[1]:output-levels)
            +                1019 supriya:meters:2 (session.mixers[0].tracks[0]:output-levels)
                                 in_: 20.0, out: 15.0
            -                1020 supriya:patch-cable:2x2 (session.mixers[0].tracks[1].output:synth)
            +                1020 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].output:synth)
                                 active: c11, gain: 0.0, gate: 1.0, in_: 20.0, out: 16.0
            -            1021 group (session.mixers[0].tracks[2]:group)
            -                1022 group (session.mixers[0].tracks[2]:tracks)
            -                1025 supriya:meters:2 (session.mixers[0].tracks[2]:input-levels)
            +            1021 group (session.mixers[0].tracks[1]:group)
            +                1022 group (session.mixers[0].tracks[1]:tracks)
            +                1025 supriya:meters:2 (session.mixers[0].tracks[1]:input-levels)
                                 in_: 22.0, out: 19.0
            -                1023 group (session.mixers[0].tracks[2]:devices)
            -                1024 supriya:channel-strip:2 (session.mixers[0].tracks[2]:channel-strip)
            +                1023 group (session.mixers[0].tracks[1]:devices)
            +                1024 supriya:channel-strip:2 (session.mixers[0].tracks[1]:channel-strip)
                                 active: c17, bus: 22.0, gain: c18, gate: 1.0
            -                1026 supriya:meters:2 (session.mixers[0].tracks[2]:output-levels)
            +                1026 supriya:meters:2 (session.mixers[0].tracks[1]:output-levels)
                                 in_: 22.0, out: 21.0
            -                1027 supriya:patch-cable:2x2 (session.mixers[0].tracks[2].output:synth)
            +                1027 supriya:patch-cable:2x2 (session.mixers[0].tracks[1].output:synth)
                                 active: c17, gain: 0.0, gate: 1.0, in_: 22.0, out: 16.0
                     1004 supriya:meters:2 (session.mixers[0]:input-levels)
                         in_: 16.0, out: 1.0
            """,
            [
                OscMessage("/g_head", 1015, 1006),
                OscBundle(
                    contents=(
                        OscMessage("/n_set", 1012, "gate", 0.0),
                        OscMessage(
                            "/s_new",
                            "supriya:patch-cable:2x2",
                            1043,
                            1,
                            1006,
                            "active",
                            "c5",
                            "in_",
                            18.0,
                            "out",
                            20.0,
                        ),
                    ),
                ),
            ],
        ),
        (
            "other_other",
            0,
            does_not_raise,
            (0, 1, 2),
            """
            --- initial
            +++ mutation
            @@ -1,40 +1,42 @@
             <session.contexts[0]>
                 NODE TREE 1000 group (session.mixers[0]:group)
                     1001 group (session.mixers[0]:tracks)
            -            1006 group (session.mixers[0].tracks[0]:group)
            -                1007 group (session.mixers[0].tracks[0]:tracks)
            -                1010 supriya:meters:2 (session.mixers[0].tracks[0]:input-levels)
            -                    in_: 18.0, out: 7.0
            -                1008 group (session.mixers[0].tracks[0]:devices)
            -                1009 supriya:channel-strip:2 (session.mixers[0].tracks[0]:channel-strip)
            -                    active: c5, bus: 18.0, gain: c6, gate: 1.0
            -                1042 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].sends[0]:synth)
            -                    active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 22.0
            -                1011 supriya:meters:2 (session.mixers[0].tracks[0]:output-levels)
            -                    in_: 18.0, out: 9.0
            -                1012 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].output:synth)
            -                    active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 16.0
            -            1014 group (session.mixers[0].tracks[1]:group)
            -                1015 group (session.mixers[0].tracks[1]:tracks)
            -                1018 supriya:meters:2 (session.mixers[0].tracks[1]:input-levels)
            +            1014 group (session.mixers[0].tracks[0]:group)
            +                1015 group (session.mixers[0].tracks[0]:tracks)
            +                1018 supriya:meters:2 (session.mixers[0].tracks[0]:input-levels)
                                 in_: 20.0, out: 13.0
            -                1016 group (session.mixers[0].tracks[1]:devices)
            -                1017 supriya:channel-strip:2 (session.mixers[0].tracks[1]:channel-strip)
            +                1016 group (session.mixers[0].tracks[0]:devices)
            +                1017 supriya:channel-strip:2 (session.mixers[0].tracks[0]:channel-strip)
                                 active: c11, bus: 20.0, gain: c12, gate: 1.0
            -                1019 supriya:meters:2 (session.mixers[0].tracks[1]:output-levels)
            +                1019 supriya:meters:2 (session.mixers[0].tracks[0]:output-levels)
                                 in_: 20.0, out: 15.0
            -                1020 supriya:patch-cable:2x2 (session.mixers[0].tracks[1].output:synth)
            +                1020 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].output:synth)
                                 active: c11, gain: 0.0, gate: 1.0, in_: 20.0, out: 16.0
            -            1021 group (session.mixers[0].tracks[2]:group)
            -                1022 group (session.mixers[0].tracks[2]:tracks)
            -                1025 supriya:meters:2 (session.mixers[0].tracks[2]:input-levels)
            +            1021 group (session.mixers[0].tracks[1]:group)
            +                1022 group (session.mixers[0].tracks[1]:tracks)
            +                    1006 group (session.mixers[0].tracks[1].tracks[0]:group)
            +                        1007 group (session.mixers[0].tracks[1].tracks[0]:tracks)
            +                        1010 supriya:meters:2 (session.mixers[0].tracks[1].tracks[0]:input-levels)
            +                            in_: 18.0, out: 7.0
            +                        1008 group (session.mixers[0].tracks[1].tracks[0]:devices)
            +                        1009 supriya:channel-strip:2 (session.mixers[0].tracks[1].tracks[0]:channel-strip)
            +                            active: c5, bus: 18.0, gain: c6, gate: 1.0
            +                        1042 supriya:patch-cable:2x2 (session.mixers[0].tracks[1].tracks[0].sends[0]:synth)
            +                            active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 22.0
            +                        1011 supriya:meters:2 (session.mixers[0].tracks[1].tracks[0]:output-levels)
            +                            in_: 18.0, out: 9.0
            +                        1012 supriya:patch-cable:2x2
            +                            active: c5, gain: 0.0, gate: 0.0, in_: 18.0, out: 16.0
            +                        1043 supriya:patch-cable:2x2 (session.mixers[0].tracks[1].tracks[0].output:synth)
            +                            active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 22.0
            +                1025 supriya:meters:2 (session.mixers[0].tracks[1]:input-levels)
                                 in_: 22.0, out: 19.0
            -                1023 group (session.mixers[0].tracks[2]:devices)
            -                1024 supriya:channel-strip:2 (session.mixers[0].tracks[2]:channel-strip)
            +                1023 group (session.mixers[0].tracks[1]:devices)
            +                1024 supriya:channel-strip:2 (session.mixers[0].tracks[1]:channel-strip)
                                 active: c17, bus: 22.0, gain: c18, gate: 1.0
            -                1026 supriya:meters:2 (session.mixers[0].tracks[2]:output-levels)
            +                1026 supriya:meters:2 (session.mixers[0].tracks[1]:output-levels)
                                 in_: 22.0, out: 21.0
            -                1027 supriya:patch-cable:2x2 (session.mixers[0].tracks[2].output:synth)
            +                1027 supriya:patch-cable:2x2 (session.mixers[0].tracks[1].output:synth)
                                 active: c17, gain: 0.0, gate: 1.0, in_: 22.0, out: 16.0
                     1004 supriya:meters:2 (session.mixers[0]:input-levels)
                         in_: 16.0, out: 1.0
            """,
            [
                OscMessage("/g_head", 1022, 1006),
                OscBundle(
                    contents=(
                        OscMessage("/n_set", 1012, "gate", 0.0),
                        OscMessage(
                            "/s_new",
                            "supriya:patch-cable:2x2",
                            1043,
                            1,
                            1006,
                            "active",
                            "c5",
                            "in_",
                            18.0,
                            "out",
                            22.0,
                        ),
                    ),
                ),
            ],
        ),
        ("other_mixer", 0, pytest.raises(RuntimeError), (0, 0), "", []),
    ],
)
@pytest.mark.asyncio
async def test_Track_move(
    expected_commands: List[Union[OscBundle, OscMessage]],
    expected_graph_order: List[int],
    expected_diff: str,
    index: int,
    mixer: Mixer,
    online: bool,
    parent: str,
    maybe_raises,
    session: Session,
    track: Track,
) -> None:
    # Pre-conditions
    print("Pre-conditions")
    if online:
        await session.boot()
    targets: Dict[str, TrackContainer] = {
        "self": track,
        "mixer": mixer,
        "other": await mixer.add_track(),
        "other_other": (other_other := await mixer.add_track()),
        "other_mixer": await session.add_mixer(),
    }
    await track.add_send(target=other_other)
    if online:
        await debug_tree(session)
    # Operation
    print("Operation")
    with maybe_raises, capture(mixer.context) as commands:
        await track.move(index=index, parent=targets[parent])
    # Post-conditions
    print("Post-conditions")
    assert track.graph_order == expected_graph_order
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
                        1042 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].sends[0]:synth)
                            active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 22.0
                        1011 supriya:meters:2 (session.mixers[0].tracks[0]:output-levels)
                            in_: 18.0, out: 9.0
                        1012 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].output:synth)
                            active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 16.0
                    1014 group (session.mixers[0].tracks[1]:group)
                        1015 group (session.mixers[0].tracks[1]:tracks)
                        1018 supriya:meters:2 (session.mixers[0].tracks[1]:input-levels)
                            in_: 20.0, out: 13.0
                        1016 group (session.mixers[0].tracks[1]:devices)
                        1017 supriya:channel-strip:2 (session.mixers[0].tracks[1]:channel-strip)
                            active: c11, bus: 20.0, gain: c12, gate: 1.0
                        1019 supriya:meters:2 (session.mixers[0].tracks[1]:output-levels)
                            in_: 20.0, out: 15.0
                        1020 supriya:patch-cable:2x2 (session.mixers[0].tracks[1].output:synth)
                            active: c11, gain: 0.0, gate: 1.0, in_: 20.0, out: 16.0
                    1021 group (session.mixers[0].tracks[2]:group)
                        1022 group (session.mixers[0].tracks[2]:tracks)
                        1025 supriya:meters:2 (session.mixers[0].tracks[2]:input-levels)
                            in_: 22.0, out: 19.0
                        1023 group (session.mixers[0].tracks[2]:devices)
                        1024 supriya:channel-strip:2 (session.mixers[0].tracks[2]:channel-strip)
                            active: c17, bus: 22.0, gain: c18, gate: 1.0
                        1026 supriya:meters:2 (session.mixers[0].tracks[2]:output-levels)
                            in_: 22.0, out: 21.0
                        1027 supriya:patch-cable:2x2 (session.mixers[0].tracks[2].output:synth)
                            active: c17, gain: 0.0, gate: 1.0, in_: 22.0, out: 16.0
                1004 supriya:meters:2 (session.mixers[0]:input-levels)
                    in_: 16.0, out: 1.0
                1002 group (session.mixers[0]:devices)
                1003 supriya:channel-strip:2 (session.mixers[0]:channel-strip)
                    active: 1.0, bus: 16.0, gain: c0, gate: 1.0
                1005 supriya:meters:2 (session.mixers[0]:output-levels)
                    in_: 16.0, out: 3.0
                1013 supriya:patch-cable:2x2 (session.mixers[0].output:synth)
                    active: 1.0, gain: 0.0, gate: 1.0, in_: 16.0, out: 0.0
            NODE TREE 1028 group (session.mixers[1]:group)
                1029 group (session.mixers[1]:tracks)
                    1034 group (session.mixers[1].tracks[0]:group)
                        1035 group (session.mixers[1].tracks[0]:tracks)
                        1038 supriya:meters:2 (session.mixers[1].tracks[0]:input-levels)
                            in_: 26.0, out: 30.0
                        1036 group (session.mixers[1].tracks[0]:devices)
                        1037 supriya:channel-strip:2 (session.mixers[1].tracks[0]:channel-strip)
                            active: c28, bus: 26.0, gain: c29, gate: 1.0
                        1039 supriya:meters:2 (session.mixers[1].tracks[0]:output-levels)
                            in_: 26.0, out: 32.0
                        1040 supriya:patch-cable:2x2 (session.mixers[1].tracks[0].output:synth)
                            active: c28, gain: 0.0, gate: 1.0, in_: 26.0, out: 24.0
                1032 supriya:meters:2 (session.mixers[1]:input-levels)
                    in_: 24.0, out: 24.0
                1030 group (session.mixers[1]:devices)
                1031 supriya:channel-strip:2 (session.mixers[1]:channel-strip)
                    active: 1.0, bus: 24.0, gain: c23, gate: 1.0
                1033 supriya:meters:2 (session.mixers[1]:output-levels)
                    in_: 24.0, out: 26.0
                1041 supriya:patch-cable:2x2 (session.mixers[1].output:synth)
                    active: 1.0, gain: 0.0, gate: 1.0, in_: 24.0, out: 0.0
        """,
    )
    assert commands == expected_commands


@pytest.mark.xfail
@pytest.mark.parametrize("online", [False, True])
@pytest.mark.parametrize("expected_commands, expected_diff", [([], "")])
@pytest.mark.asyncio
async def test_Track_set_active(
    expected_commands: List[Union[OscBundle, OscMessage]],
    expected_diff: str,
    mixer: Mixer,
    online: bool,
    session: Session,
    track: Track,
) -> None:
    # Pre-conditions
    if online:
        await session.boot()
    # Operation
    with capture(mixer.context) as commands:
        await track.set_active()
    # Post-conditions
    if not online:
        raise Exception
    await assert_diff(
        session,
        expected_diff,
        expected_initial_tree="""
        """,
    )
    assert commands == expected_commands
    raise Exception


@pytest.mark.xfail
@pytest.mark.parametrize("online", [False, True])
@pytest.mark.parametrize("expected_commands, expected_diff", [([], "")])
@pytest.mark.asyncio
async def test_Track_set_input(
    expected_commands: List[Union[OscBundle, OscMessage]],
    expected_diff: str,
    mixer: Mixer,
    online: bool,
    session: Session,
    track: Track,
) -> None:
    # Pre-conditions
    if online:
        await session.boot()
    # Operation
    with capture(mixer.context) as commands:
        await track.set_input(None)
    # Post-conditions
    if not online:
        raise Exception
    await assert_diff(
        session,
        expected_diff,
        expected_initial_tree="""
        """,
    )
    assert commands == expected_commands
    raise Exception


@pytest.mark.parametrize("online", [False, True])
@pytest.mark.parametrize(
    "output, maybe_raises, expected_commands, expected_diff",
    [
        (
            "none",
            does_not_raise,
            [OscMessage("/n_set", 1025, "gate", 0.0)],
            """
            --- initial
            +++ mutation
            @@ -23,8 +23,8 @@
                                         active: c11, bus: 20.0, gain: c12, gate: 1.0
                                     1017 supriya:meters:2 (session.mixers[0].tracks[0].tracks[0]:output-levels)
                                         in_: 20.0, out: 15.0
            -                        1025 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].output:synth)
            -                            active: c11, gain: 0.0, gate: 1.0, in_: 20.0, out: 18.0
            +                        1025 supriya:patch-cable:2x2
            +                            active: c11, gain: 0.0, gate: 0.0, in_: 20.0, out: 18.0
                             1010 supriya:meters:2 (session.mixers[0].tracks[0]:input-levels)
                                 in_: 18.0, out: 7.0
                             1008 group (session.mixers[0].tracks[0]:devices)
            """,
        ),
        (
            "default",
            does_not_raise,
            [],
            "",
        ),
        (
            "self",
            pytest.raises(RuntimeError),
            [],
            "",
        ),
        (
            "parent",
            does_not_raise,
            [],
            "",
        ),
        (
            "child",
            does_not_raise,
            [
                OscMessage(
                    "/s_new",
                    "supriya:fb-patch-cable:2x2",
                    1049,
                    0,
                    1018,
                    "active",
                    "c17",
                    "in_",
                    30.0,
                    "out",
                    22.0,
                ),
                OscBundle(
                    contents=(
                        OscMessage("/n_set", 1025, "gate", 0.0),
                        OscMessage(
                            "/s_new",
                            "supriya:patch-cable:2x2",
                            1050,
                            1,
                            1012,
                            "active",
                            "c11",
                            "in_",
                            20.0,
                            "out",
                            30.0,
                        ),
                    ),
                ),
            ],
            """
            --- initial
            +++ mutation
            @@ -6,6 +6,8 @@
                                 1012 group (session.mixers[0].tracks[0].tracks[0]:group)
                                     1013 group (session.mixers[0].tracks[0].tracks[0]:tracks)
                                         1018 group (session.mixers[0].tracks[0].tracks[0].tracks[0]:group)
            +                                1049 supriya:fb-patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].tracks[0].feedback:synth)
            +                                    active: c17, gain: 0.0, gate: 1.0, in_: 30.0, out: 22.0
                                             1019 group (session.mixers[0].tracks[0].tracks[0].tracks[0]:tracks)
                                             1022 supriya:meters:2 (session.mixers[0].tracks[0].tracks[0].tracks[0]:input-levels)
                                                 in_: 22.0, out: 19.0
            @@ -23,8 +25,10 @@
                                         active: c11, bus: 20.0, gain: c12, gate: 1.0
                                     1017 supriya:meters:2 (session.mixers[0].tracks[0].tracks[0]:output-levels)
                                         in_: 20.0, out: 15.0
            -                        1025 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].output:synth)
            -                            active: c11, gain: 0.0, gate: 1.0, in_: 20.0, out: 18.0
            +                        1025 supriya:patch-cable:2x2
            +                            active: c11, gain: 0.0, gate: 0.0, in_: 20.0, out: 18.0
            +                        1050 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].output:synth)
            +                            active: c11, gain: 0.0, gate: 1.0, in_: 20.0, out: 30.0
                             1010 supriya:meters:2 (session.mixers[0].tracks[0]:input-levels)
                                 in_: 18.0, out: 7.0
                             1008 group (session.mixers[0].tracks[0]:devices)
            """,
        ),
        (
            "mixer",
            does_not_raise,
            [
                OscBundle(
                    contents=(
                        OscMessage("/n_set", 1025, "gate", 0.0),
                        OscMessage(
                            "/s_new",
                            "supriya:patch-cable:2x2",
                            1049,
                            1,
                            1012,
                            "active",
                            "c11",
                            "in_",
                            20.0,
                            "out",
                            16.0,
                        ),
                    ),
                ),
            ],
            """
            --- initial
            +++ mutation
            @@ -23,8 +23,10 @@
                                         active: c11, bus: 20.0, gain: c12, gate: 1.0
                                     1017 supriya:meters:2 (session.mixers[0].tracks[0].tracks[0]:output-levels)
                                         in_: 20.0, out: 15.0
            -                        1025 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].output:synth)
            -                            active: c11, gain: 0.0, gate: 1.0, in_: 20.0, out: 18.0
            +                        1025 supriya:patch-cable:2x2
            +                            active: c11, gain: 0.0, gate: 0.0, in_: 20.0, out: 18.0
            +                        1049 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].output:synth)
            +                            active: c11, gain: 0.0, gate: 1.0, in_: 20.0, out: 16.0
                             1010 supriya:meters:2 (session.mixers[0].tracks[0]:input-levels)
                                 in_: 18.0, out: 7.0
                             1008 group (session.mixers[0].tracks[0]:devices)
            """,
        ),
        (
            "sibling",
            does_not_raise,
            [
                OscBundle(
                    contents=(
                        OscMessage("/n_set", 1025, "gate", 0.0),
                        OscMessage(
                            "/s_new",
                            "supriya:patch-cable:2x2",
                            1049,
                            1,
                            1012,
                            "active",
                            "c11",
                            "in_",
                            20.0,
                            "out",
                            24.0,
                        ),
                    ),
                ),
            ],
            """
            --- initial
            +++ mutation
            @@ -23,8 +23,10 @@
                                         active: c11, bus: 20.0, gain: c12, gate: 1.0
                                     1017 supriya:meters:2 (session.mixers[0].tracks[0].tracks[0]:output-levels)
                                         in_: 20.0, out: 15.0
            -                        1025 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].output:synth)
            -                            active: c11, gain: 0.0, gate: 1.0, in_: 20.0, out: 18.0
            +                        1025 supriya:patch-cable:2x2
            +                            active: c11, gain: 0.0, gate: 0.0, in_: 20.0, out: 18.0
            +                        1049 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].output:synth)
            +                            active: c11, gain: 0.0, gate: 1.0, in_: 20.0, out: 24.0
                             1010 supriya:meters:2 (session.mixers[0].tracks[0]:input-levels)
                                 in_: 18.0, out: 7.0
                             1008 group (session.mixers[0].tracks[0]:devices)
            """,
        ),
        (
            "other_mixer",
            pytest.raises(RuntimeError),
            [],
            "",
        ),
    ],
)
@pytest.mark.asyncio
async def test_Track_set_output(
    expected_commands: List[Union[OscBundle, OscMessage]],
    expected_diff: str,
    maybe_raises,
    mixer: Mixer,
    online: bool,
    output: str,
    session: Session,
    track: Track,
) -> None:
    # Pre-conditions
    subtrack = await track.add_track()
    subsubtrack = await subtrack.add_track()
    sibling = await mixer.add_track()
    targets: Dict[str, Optional[Union[Default, TrackContainer]]] = {
        "child": subsubtrack,
        "default": DEFAULT,
        "mixer": mixer,
        "none": None,
        "other_mixer": await session.add_mixer(),
        "parent": track,
        "self": subtrack,
        "sibling": sibling,
    }
    if online:
        await session.boot()
        await debug_tree(session)
    # Operation
    with maybe_raises, capture(mixer.context) as commands:
        await subtrack.set_output(targets[output])
    # Post-conditions
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
                            1012 group (session.mixers[0].tracks[0].tracks[0]:group)
                                1013 group (session.mixers[0].tracks[0].tracks[0]:tracks)
                                    1018 group (session.mixers[0].tracks[0].tracks[0].tracks[0]:group)
                                        1019 group (session.mixers[0].tracks[0].tracks[0].tracks[0]:tracks)
                                        1022 supriya:meters:2 (session.mixers[0].tracks[0].tracks[0].tracks[0]:input-levels)
                                            in_: 22.0, out: 19.0
                                        1020 group (session.mixers[0].tracks[0].tracks[0].tracks[0]:devices)
                                        1021 supriya:channel-strip:2 (session.mixers[0].tracks[0].tracks[0].tracks[0]:channel-strip)
                                            active: c17, bus: 22.0, gain: c18, gate: 1.0
                                        1023 supriya:meters:2 (session.mixers[0].tracks[0].tracks[0].tracks[0]:output-levels)
                                            in_: 22.0, out: 21.0
                                        1024 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].tracks[0].output:synth)
                                            active: c17, gain: 0.0, gate: 1.0, in_: 22.0, out: 20.0
                                1016 supriya:meters:2 (session.mixers[0].tracks[0].tracks[0]:input-levels)
                                    in_: 20.0, out: 13.0
                                1014 group (session.mixers[0].tracks[0].tracks[0]:devices)
                                1015 supriya:channel-strip:2 (session.mixers[0].tracks[0].tracks[0]:channel-strip)
                                    active: c11, bus: 20.0, gain: c12, gate: 1.0
                                1017 supriya:meters:2 (session.mixers[0].tracks[0].tracks[0]:output-levels)
                                    in_: 20.0, out: 15.0
                                1025 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].output:synth)
                                    active: c11, gain: 0.0, gate: 1.0, in_: 20.0, out: 18.0
                        1010 supriya:meters:2 (session.mixers[0].tracks[0]:input-levels)
                            in_: 18.0, out: 7.0
                        1008 group (session.mixers[0].tracks[0]:devices)
                        1009 supriya:channel-strip:2 (session.mixers[0].tracks[0]:channel-strip)
                            active: c5, bus: 18.0, gain: c6, gate: 1.0
                        1011 supriya:meters:2 (session.mixers[0].tracks[0]:output-levels)
                            in_: 18.0, out: 9.0
                        1026 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].output:synth)
                            active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 16.0
                    1027 group (session.mixers[0].tracks[1]:group)
                        1028 group (session.mixers[0].tracks[1]:tracks)
                        1031 supriya:meters:2 (session.mixers[0].tracks[1]:input-levels)
                            in_: 24.0, out: 25.0
                        1029 group (session.mixers[0].tracks[1]:devices)
                        1030 supriya:channel-strip:2 (session.mixers[0].tracks[1]:channel-strip)
                            active: c23, bus: 24.0, gain: c24, gate: 1.0
                        1032 supriya:meters:2 (session.mixers[0].tracks[1]:output-levels)
                            in_: 24.0, out: 27.0
                        1033 supriya:patch-cable:2x2 (session.mixers[0].tracks[1].output:synth)
                            active: c23, gain: 0.0, gate: 1.0, in_: 24.0, out: 16.0
                1004 supriya:meters:2 (session.mixers[0]:input-levels)
                    in_: 16.0, out: 1.0
                1002 group (session.mixers[0]:devices)
                1003 supriya:channel-strip:2 (session.mixers[0]:channel-strip)
                    active: 1.0, bus: 16.0, gain: c0, gate: 1.0
                1005 supriya:meters:2 (session.mixers[0]:output-levels)
                    in_: 16.0, out: 3.0
                1034 supriya:patch-cable:2x2 (session.mixers[0].output:synth)
                    active: 1.0, gain: 0.0, gate: 1.0, in_: 16.0, out: 0.0
            NODE TREE 1035 group (session.mixers[1]:group)
                1036 group (session.mixers[1]:tracks)
                    1041 group (session.mixers[1].tracks[0]:group)
                        1042 group (session.mixers[1].tracks[0]:tracks)
                        1045 supriya:meters:2 (session.mixers[1].tracks[0]:input-levels)
                            in_: 28.0, out: 36.0
                        1043 group (session.mixers[1].tracks[0]:devices)
                        1044 supriya:channel-strip:2 (session.mixers[1].tracks[0]:channel-strip)
                            active: c34, bus: 28.0, gain: c35, gate: 1.0
                        1046 supriya:meters:2 (session.mixers[1].tracks[0]:output-levels)
                            in_: 28.0, out: 38.0
                        1047 supriya:patch-cable:2x2 (session.mixers[1].tracks[0].output:synth)
                            active: c34, gain: 0.0, gate: 1.0, in_: 28.0, out: 26.0
                1039 supriya:meters:2 (session.mixers[1]:input-levels)
                    in_: 26.0, out: 30.0
                1037 group (session.mixers[1]:devices)
                1038 supriya:channel-strip:2 (session.mixers[1]:channel-strip)
                    active: 1.0, bus: 26.0, gain: c29, gate: 1.0
                1040 supriya:meters:2 (session.mixers[1]:output-levels)
                    in_: 26.0, out: 32.0
                1048 supriya:patch-cable:2x2 (session.mixers[1].output:synth)
                    active: 1.0, gain: 0.0, gate: 1.0, in_: 26.0, out: 0.0
        """,
    )
    assert commands == expected_commands


@pytest.mark.xfail
@pytest.mark.parametrize("online", [False, True])
@pytest.mark.parametrize(
    "expected_commands, expected_diff",
    [
        ([], ""),
    ],
)
@pytest.mark.asyncio
async def test_Track_set_soloed(
    expected_commands: List[Union[OscBundle, OscMessage]],
    expected_diff: str,
    mixer: Mixer,
    online: bool,
    session: Session,
    track: Track,
) -> None:
    # Pre-conditions
    if online:
        await session.boot()
    # Operation
    with capture(mixer.context) as commands:
        await track.set_soloed()
    # Post-conditions
    if not online:
        raise Exception
    await assert_diff(
        session,
        expected_diff,
        expected_initial_tree="""
        """,
    )
    assert commands == expected_commands
    raise Exception


@pytest.mark.xfail
@pytest.mark.parametrize("online", [False, True])
@pytest.mark.parametrize(
    "expected_commands, expected_diff",
    [
        ([], ""),
    ],
)
@pytest.mark.asyncio
async def test_Track_ungroup(
    expected_commands: List[Union[OscBundle, OscMessage]],
    expected_diff: str,
    mixer: Mixer,
    online: bool,
    session: Session,
    track: Track,
) -> None:
    # Pre-conditions
    if online:
        await session.boot()
    # Operation
    with capture(mixer.context) as commands:
        await track.ungroup()
    # Post-conditions
    if not online:
        raise Exception
    await assert_diff(
        session,
        expected_diff,
        expected_initial_tree="""
        """,
    )
    assert commands == expected_commands
    raise Exception
