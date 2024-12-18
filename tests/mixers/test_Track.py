from typing import Dict, List, Optional, Tuple, Union

import pytest

from supriya import OscBundle, OscMessage
from supriya.mixers import Session
from supriya.mixers.devices import Device, DeviceContainer
from supriya.mixers.mixers import Mixer
from supriya.mixers.synthdefs import DEVICE_DC_TESTER_2
from supriya.mixers.tracks import Track, TrackContainer
from supriya.typing import DEFAULT, Default

from .conftest import assert_diff, capture, debug_tree, does_not_raise


@pytest.mark.parametrize("online", [False, True])
@pytest.mark.parametrize(
    "target, expected_diff, expected_commands",
    [
        (
            "mixers[0]",
            """
            --- initial
            +++ mutation
            @@ -76,6 +76,9 @@
                     1004 supriya:meters:2 (session.mixers[0]:input-levels)
                         in_: 16.0, out: 1.0
                     1002 group (session.mixers[0]:devices)
            +            1066 group (session.mixers[0].devices[0]:group)
            +                1067 supriya:device-dc-tester:2 (session.mixers[0].devices[0]:synth)
            +                    dc: 1.0, out: 0.0
                     1003 supriya:channel-strip:2 (session.mixers[0]:channel-strip)
                         active: 1.0, bus: 16.0, gain: c0, gate: 1.0
                     1005 supriya:meters:2 (session.mixers[0]:output-levels)
            """,
            [
                OscMessage("/d_recv", DEVICE_DC_TESTER_2.compile()),
                OscMessage("/sync", 2),
                OscBundle(
                    contents=(
                        OscMessage("/g_new", 1066, 1, 1002),
                        OscMessage(
                            "/s_new", "supriya:device-dc-tester:2", 1067, 1, 1066
                        ),
                    ),
                ),
            ],
        ),
        (
            "mixers[0].tracks[0]",
            """
            --- initial
            +++ mutation
            @@ -41,6 +41,9 @@
                             1010 supriya:meters:2 (session.mixers[0].tracks[0]:input-levels)
                                 in_: 18.0, out: 7.0
                             1008 group (session.mixers[0].tracks[0]:devices)
            +                    1066 group (session.mixers[0].tracks[0].devices[0]:group)
            +                        1067 supriya:device-dc-tester:2 (session.mixers[0].tracks[0].devices[0]:synth)
            +                            dc: 1.0, out: 0.0
                             1009 supriya:channel-strip:2 (session.mixers[0].tracks[0]:channel-strip)
                                 active: c5, bus: 18.0, gain: c6, gate: 1.0
                             1051 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].sends[0]:synth)
            """,
            [
                OscMessage("/d_recv", DEVICE_DC_TESTER_2.compile()),
                OscMessage("/sync", 2),
                OscBundle(
                    contents=(
                        OscMessage("/g_new", 1066, 1, 1008),
                        OscMessage(
                            "/s_new", "supriya:device-dc-tester:2", 1067, 1, 1066
                        ),
                    ),
                ),
            ],
        ),
    ],
)
@pytest.mark.asyncio
async def test_Track_add_device(
    complex_session: Tuple[Session, str],
    expected_commands: List[Union[OscBundle, OscMessage]],
    expected_diff: str,
    online: bool,
    target: str,
) -> None:
    # Pre-conditions
    session, initial_tree = complex_session
    if online:
        await session.boot()
    target_ = session[target]
    assert isinstance(target_, DeviceContainer)
    # Operation
    with capture(session["mixers[0]"].context) as commands:
        device = await target_.add_device()
    # Post-conditions
    assert isinstance(device, Device)
    assert device in target_.devices
    assert device.parent is target_
    assert target_.devices[0] is device
    if not online:
        return
    await assert_diff(
        session,
        expected_diff,
        expected_initial_tree=initial_tree,
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
    "target, parent, index, maybe_raises, expected_graph_order, expected_diff, expected_commands",
    [
        (
            "mixers[0].tracks[0]",
            "mixers[0]",
            1,
            does_not_raise,
            (0, 1),
            """
            --- initial
            +++ mutation
            @@ -1,6 +1,21 @@
             <session.contexts[0]>
                 NODE TREE 1000 group
                     1001 group
            +            1034 group
            +                1066 supriya:fb-patch-cable:2x2
            +                    active: c29, gain: 0.0, gate: 1.0, in_: 36.0, out: 26.0
            +                1035 group
            +                1038 supriya:meters:2
            +                    in_: 26.0, out: 31.0
            +                1036 group
            +                1037 supriya:channel-strip:2
            +                    active: c29, bus: 26.0, gain: c30, gate: 1.0
            +                1042 supriya:patch-cable:2x2
            +                    active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 28.0
            +                1039 supriya:meters:2
            +                    in_: 26.0, out: 33.0
            +                1040 supriya:patch-cable:2x2
            +                    active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 16.0
                         1006 group
                             1007 group
                                 1012 group
            @@ -43,25 +58,14 @@
                             1008 group
                             1009 supriya:channel-strip:2
                                 active: c5, bus: 18.0, gain: c6, gate: 1.0
            +                1067 supriya:patch-cable:2x2
            +                    active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 36.0
                             1051 supriya:patch-cable:2x2
            -                    active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 26.0
            +                    active: c5, gain: 0.0, gate: 0.0, in_: 18.0, out: 26.0
                             1011 supriya:meters:2
                                 in_: 18.0, out: 9.0
                             1033 supriya:patch-cable:2x2
                                 active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 16.0
            -            1034 group
            -                1035 group
            -                1038 supriya:meters:2
            -                    in_: 26.0, out: 31.0
            -                1036 group
            -                1037 supriya:channel-strip:2
            -                    active: c29, bus: 26.0, gain: c30, gate: 1.0
            -                1042 supriya:patch-cable:2x2
            -                    active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 28.0
            -                1039 supriya:meters:2
            -                    in_: 26.0, out: 33.0
            -                1040 supriya:patch-cable:2x2
            -                    active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 16.0
                         1043 group
                             1044 group
                             1047 supriya:meters:2
            """,
            [
                OscMessage("/n_after", 1006, 1034),
                OscMessage(
                    "/s_new",
                    "supriya:fb-patch-cable:2x2",
                    1066,
                    0,
                    1034,
                    "active",
                    "c29",
                    "in_",
                    36.0,
                    "out",
                    26.0,
                ),
                OscBundle(
                    contents=(
                        OscMessage("/n_set", 1051, "gate", 0.0),
                        OscMessage(
                            "/s_new",
                            "supriya:patch-cable:2x2",
                            1067,
                            3,
                            1009,
                            "active",
                            "c5",
                            "in_",
                            18.0,
                            "out",
                            36.0,
                        ),
                    ),
                ),
            ],
        ),
        (
            "mixers[0].tracks[0]",
            "mixers[0].tracks[0].tracks[0]",
            0,
            pytest.raises(RuntimeError),
            (0, 0),
            "",
            [],
        ),
        (
            "mixers[0].tracks[1]",
            "mixers[0]",
            0,
            does_not_raise,
            (0, 0),
            """
            --- initial
            +++ mutation
            @@ -1,11 +1,28 @@
             <session.contexts[0]>
                 NODE TREE 1000 group
                     1001 group
            +            1034 group
            +                1067 supriya:fb-patch-cable:2x2
            +                    active: c29, gain: 0.0, gate: 1.0, in_: 28.0, out: 26.0
            +                1035 group
            +                1038 supriya:meters:2
            +                    in_: 26.0, out: 31.0
            +                1036 group
            +                1037 supriya:channel-strip:2
            +                    active: c29, bus: 26.0, gain: c30, gate: 1.0
            +                1066 supriya:patch-cable:2x2
            +                    active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 20.0
            +                1042 supriya:patch-cable:2x2
            +                    active: c29, gain: 0.0, gate: 0.0, in_: 26.0, out: 28.0
            +                1039 supriya:meters:2
            +                    in_: 26.0, out: 33.0
            +                1040 supriya:patch-cable:2x2
            +                    active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 16.0
                         1006 group
                             1007 group
                                 1012 group
                                     1041 supriya:fb-patch-cable:2x2
            -                            active: c11, gain: 0.0, gate: 1.0, in_: 28.0, out: 20.0
            +                            active: c11, gain: 0.0, gate: 0.0, in_: 28.0, out: 20.0
                                     1013 group
                                         1018 group
                                             1019 group
            @@ -43,25 +60,14 @@
                             1008 group
                             1009 supriya:channel-strip:2
                                 active: c5, bus: 18.0, gain: c6, gate: 1.0
            +                1068 supriya:patch-cable:2x2
            +                    active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 28.0
                             1051 supriya:patch-cable:2x2
            -                    active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 26.0
            +                    active: c5, gain: 0.0, gate: 0.0, in_: 18.0, out: 26.0
                             1011 supriya:meters:2
                                 in_: 18.0, out: 9.0
                             1033 supriya:patch-cable:2x2
                                 active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 16.0
            -            1034 group
            -                1035 group
            -                1038 supriya:meters:2
            -                    in_: 26.0, out: 31.0
            -                1036 group
            -                1037 supriya:channel-strip:2
            -                    active: c29, bus: 26.0, gain: c30, gate: 1.0
            -                1042 supriya:patch-cable:2x2
            -                    active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 28.0
            -                1039 supriya:meters:2
            -                    in_: 26.0, out: 33.0
            -                1040 supriya:patch-cable:2x2
            -                    active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 16.0
                         1043 group
                             1044 group
                             1047 supriya:meters:2
            """,
            [
                OscMessage("/g_head", 1001, 1034),
                OscMessage("/n_set", 1041, "gate", 0.0),
                OscBundle(
                    contents=(
                        OscMessage("/n_set", 1042, "gate", 0.0),
                        OscMessage(
                            "/s_new",
                            "supriya:patch-cable:2x2",
                            1066,
                            3,
                            1037,
                            "active",
                            "c29",
                            "in_",
                            26.0,
                            "out",
                            20.0,
                        ),
                    ),
                ),
                OscMessage(
                    "/s_new",
                    "supriya:fb-patch-cable:2x2",
                    1067,
                    0,
                    1034,
                    "active",
                    "c29",
                    "in_",
                    28.0,
                    "out",
                    26.0,
                ),
                OscBundle(
                    contents=(
                        OscMessage("/n_set", 1051, "gate", 0.0),
                        OscMessage(
                            "/s_new",
                            "supriya:patch-cable:2x2",
                            1068,
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
        ("mixers[0].tracks[1]", "mixers[0]", 1, does_not_raise, (0, 1), "", []),
        (
            "mixers[0].tracks[1]",
            "mixers[0]",
            2,
            does_not_raise,
            (0, 2),
            """
            --- initial
            +++ mutation
            @@ -49,6 +49,17 @@
                                 in_: 18.0, out: 9.0
                             1033 supriya:patch-cable:2x2
                                 active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 16.0
            +            1043 group
            +                1044 group
            +                1047 supriya:meters:2
            +                    in_: 30.0, out: 37.0
            +                1045 group
            +                1046 supriya:channel-strip:2
            +                    active: c35, bus: 30.0, gain: c36, gate: 1.0
            +                1048 supriya:meters:2
            +                    in_: 30.0, out: 39.0
            +                1049 supriya:patch-cable:2x2
            +                    active: c35, gain: 0.0, gate: 1.0, in_: 30.0, out: 16.0
                         1034 group
                             1035 group
                             1038 supriya:meters:2
            @@ -62,17 +73,6 @@
                                 in_: 26.0, out: 33.0
                             1040 supriya:patch-cable:2x2
                                 active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 16.0
            -            1043 group
            -                1044 group
            -                1047 supriya:meters:2
            -                    in_: 30.0, out: 37.0
            -                1045 group
            -                1046 supriya:channel-strip:2
            -                    active: c35, bus: 30.0, gain: c36, gate: 1.0
            -                1048 supriya:meters:2
            -                    in_: 30.0, out: 39.0
            -                1049 supriya:patch-cable:2x2
            -                    active: c35, gain: 0.0, gate: 1.0, in_: 30.0, out: 16.0
                     1004 supriya:meters:2
                         in_: 16.0, out: 1.0
                     1002 group
            """,
            [OscMessage("/n_after", 1034, 1043)],
        ),
        (
            "mixers[0].tracks[1]",
            "mixers[0]",
            3,
            pytest.raises(RuntimeError),
            (0, 1),
            "",
            [],
        ),
        (
            "mixers[0].tracks[1]",
            "mixers[0].tracks[0]",
            0,
            does_not_raise,
            (0, 0, 2),
            """
            --- initial
            +++ mutation
            @@ -3,9 +3,28 @@
                     1001 group
                         1006 group
                             1007 group
            +                    1034 group
            +                        1068 supriya:fb-patch-cable:2x2
            +                            active: c29, gain: 0.0, gate: 1.0, in_: 28.0, out: 26.0
            +                        1035 group
            +                        1038 supriya:meters:2
            +                            in_: 26.0, out: 31.0
            +                        1036 group
            +                        1037 supriya:channel-strip:2
            +                            active: c29, bus: 26.0, gain: c30, gate: 1.0
            +                        1067 supriya:patch-cable:2x2
            +                            active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 20.0
            +                        1042 supriya:patch-cable:2x2
            +                            active: c29, gain: 0.0, gate: 0.0, in_: 26.0, out: 28.0
            +                        1039 supriya:meters:2
            +                            in_: 26.0, out: 33.0
            +                        1040 supriya:patch-cable:2x2
            +                            active: c29, gain: 0.0, gate: 0.0, in_: 26.0, out: 16.0
            +                        1066 supriya:patch-cable:2x2
            +                            active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 18.0
                                 1012 group
                                     1041 supriya:fb-patch-cable:2x2
            -                            active: c11, gain: 0.0, gate: 1.0, in_: 28.0, out: 20.0
            +                            active: c11, gain: 0.0, gate: 0.0, in_: 28.0, out: 20.0
                                     1013 group
                                         1018 group
                                             1019 group
            @@ -43,25 +62,14 @@
                             1008 group
                             1009 supriya:channel-strip:2
                                 active: c5, bus: 18.0, gain: c6, gate: 1.0
            +                1069 supriya:patch-cable:2x2
            +                    active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 28.0
                             1051 supriya:patch-cable:2x2
            -                    active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 26.0
            +                    active: c5, gain: 0.0, gate: 0.0, in_: 18.0, out: 26.0
                             1011 supriya:meters:2
                                 in_: 18.0, out: 9.0
                             1033 supriya:patch-cable:2x2
                                 active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 16.0
            -            1034 group
            -                1035 group
            -                1038 supriya:meters:2
            -                    in_: 26.0, out: 31.0
            -                1036 group
            -                1037 supriya:channel-strip:2
            -                    active: c29, bus: 26.0, gain: c30, gate: 1.0
            -                1042 supriya:patch-cable:2x2
            -                    active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 28.0
            -                1039 supriya:meters:2
            -                    in_: 26.0, out: 33.0
            -                1040 supriya:patch-cable:2x2
            -                    active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 16.0
                         1043 group
                             1044 group
                             1047 supriya:meters:2
            """,
            [
                OscMessage("/g_head", 1007, 1034),
                OscBundle(
                    contents=(
                        OscMessage("/n_set", 1040, "gate", 0.0),
                        OscMessage(
                            "/s_new",
                            "supriya:patch-cable:2x2",
                            1066,
                            1,
                            1034,
                            "active",
                            "c29",
                            "in_",
                            26.0,
                            "out",
                            18.0,
                        ),
                    ),
                ),
                OscMessage("/n_set", 1041, "gate", 0.0),
                OscBundle(
                    contents=(
                        OscMessage("/n_set", 1042, "gate", 0.0),
                        OscMessage(
                            "/s_new",
                            "supriya:patch-cable:2x2",
                            1067,
                            3,
                            1037,
                            "active",
                            "c29",
                            "in_",
                            26.0,
                            "out",
                            20.0,
                        ),
                    ),
                ),
                OscMessage(
                    "/s_new",
                    "supriya:fb-patch-cable:2x2",
                    1068,
                    0,
                    1034,
                    "active",
                    "c29",
                    "in_",
                    28.0,
                    "out",
                    26.0,
                ),
                OscBundle(
                    contents=(
                        OscMessage("/n_set", 1051, "gate", 0.0),
                        OscMessage(
                            "/s_new",
                            "supriya:patch-cable:2x2",
                            1069,
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
            "mixers[0].tracks[1]",
            "mixers[0].tracks[0].tracks[0]",
            0,
            does_not_raise,
            (0, 0, 2, 2),
            """
            --- initial
            +++ mutation
            @@ -5,8 +5,27 @@
                             1007 group
                                 1012 group
                                     1041 supriya:fb-patch-cable:2x2
            -                            active: c11, gain: 0.0, gate: 1.0, in_: 28.0, out: 20.0
            +                            active: c11, gain: 0.0, gate: 0.0, in_: 28.0, out: 20.0
                                     1013 group
            +                            1034 group
            +                                1068 supriya:fb-patch-cable:2x2
            +                                    active: c29, gain: 0.0, gate: 1.0, in_: 28.0, out: 26.0
            +                                1035 group
            +                                1038 supriya:meters:2
            +                                    in_: 26.0, out: 31.0
            +                                1036 group
            +                                1037 supriya:channel-strip:2
            +                                    active: c29, bus: 26.0, gain: c30, gate: 1.0
            +                                1067 supriya:patch-cable:2x2
            +                                    active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 20.0
            +                                1042 supriya:patch-cable:2x2
            +                                    active: c29, gain: 0.0, gate: 0.0, in_: 26.0, out: 28.0
            +                                1039 supriya:meters:2
            +                                    in_: 26.0, out: 33.0
            +                                1040 supriya:patch-cable:2x2
            +                                    active: c29, gain: 0.0, gate: 0.0, in_: 26.0, out: 16.0
            +                                1066 supriya:patch-cable:2x2
            +                                    active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 20.0
                                         1018 group
                                             1019 group
                                             1022 supriya:meters:2
            @@ -43,25 +62,14 @@
                             1008 group
                             1009 supriya:channel-strip:2
                                 active: c5, bus: 18.0, gain: c6, gate: 1.0
            +                1069 supriya:patch-cable:2x2
            +                    active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 28.0
                             1051 supriya:patch-cable:2x2
            -                    active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 26.0
            +                    active: c5, gain: 0.0, gate: 0.0, in_: 18.0, out: 26.0
                             1011 supriya:meters:2
                                 in_: 18.0, out: 9.0
                             1033 supriya:patch-cable:2x2
                                 active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 16.0
            -            1034 group
            -                1035 group
            -                1038 supriya:meters:2
            -                    in_: 26.0, out: 31.0
            -                1036 group
            -                1037 supriya:channel-strip:2
            -                    active: c29, bus: 26.0, gain: c30, gate: 1.0
            -                1042 supriya:patch-cable:2x2
            -                    active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 28.0
            -                1039 supriya:meters:2
            -                    in_: 26.0, out: 33.0
            -                1040 supriya:patch-cable:2x2
            -                    active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 16.0
                         1043 group
                             1044 group
                             1047 supriya:meters:2
            """,
            [
                OscMessage("/g_head", 1013, 1034),
                OscBundle(
                    contents=(
                        OscMessage("/n_set", 1040, "gate", 0.0),
                        OscMessage(
                            "/s_new",
                            "supriya:patch-cable:2x2",
                            1066,
                            1,
                            1034,
                            "active",
                            "c29",
                            "in_",
                            26.0,
                            "out",
                            20.0,
                        ),
                    ),
                ),
                OscMessage("/n_set", 1041, "gate", 0.0),
                OscBundle(
                    contents=(
                        OscMessage("/n_set", 1042, "gate", 0.0),
                        OscMessage(
                            "/s_new",
                            "supriya:patch-cable:2x2",
                            1067,
                            3,
                            1037,
                            "active",
                            "c29",
                            "in_",
                            26.0,
                            "out",
                            20.0,
                        ),
                    ),
                ),
                OscMessage(
                    "/s_new",
                    "supriya:fb-patch-cable:2x2",
                    1068,
                    0,
                    1034,
                    "active",
                    "c29",
                    "in_",
                    28.0,
                    "out",
                    26.0,
                ),
                OscBundle(
                    contents=(
                        OscMessage("/n_set", 1051, "gate", 0.0),
                        OscMessage(
                            "/s_new",
                            "supriya:patch-cable:2x2",
                            1069,
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
            "mixers[0].tracks[1]",
            "mixers[0].tracks[1]",
            0,
            pytest.raises(RuntimeError),
            (0, 1),
            "",
            [],
        ),
        (
            "mixers[0].tracks[1]",
            "mixers[0].tracks[2]",
            0,
            does_not_raise,
            (0, 1, 2),
            """
            --- initial
            +++ mutation
            @@ -49,21 +49,23 @@
                                 in_: 18.0, out: 9.0
                             1033 supriya:patch-cable:2x2
                                 active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 16.0
            -            1034 group
            -                1035 group
            -                1038 supriya:meters:2
            -                    in_: 26.0, out: 31.0
            -                1036 group
            -                1037 supriya:channel-strip:2
            -                    active: c29, bus: 26.0, gain: c30, gate: 1.0
            -                1042 supriya:patch-cable:2x2
            -                    active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 28.0
            -                1039 supriya:meters:2
            -                    in_: 26.0, out: 33.0
            -                1040 supriya:patch-cable:2x2
            -                    active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 16.0
                         1043 group
                             1044 group
            +                    1034 group
            +                        1035 group
            +                        1038 supriya:meters:2
            +                            in_: 26.0, out: 31.0
            +                        1036 group
            +                        1037 supriya:channel-strip:2
            +                            active: c29, bus: 26.0, gain: c30, gate: 1.0
            +                        1042 supriya:patch-cable:2x2
            +                            active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 28.0
            +                        1039 supriya:meters:2
            +                            in_: 26.0, out: 33.0
            +                        1040 supriya:patch-cable:2x2
            +                            active: c29, gain: 0.0, gate: 0.0, in_: 26.0, out: 16.0
            +                        1066 supriya:patch-cable:2x2
            +                            active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 30.0
                             1047 supriya:meters:2
                                 in_: 30.0, out: 37.0
                             1045 group
            """,
            [
                OscMessage("/g_head", 1044, 1034),
                OscBundle(
                    contents=(
                        OscMessage("/n_set", 1040, "gate", 0.0),
                        OscMessage(
                            "/s_new",
                            "supriya:patch-cable:2x2",
                            1066,
                            1,
                            1034,
                            "active",
                            "c29",
                            "in_",
                            26.0,
                            "out",
                            30.0,
                        ),
                    ),
                ),
            ],
        ),
        (
            "mixers[0].tracks[2]",
            "mixers[0]",
            0,
            does_not_raise,
            (0, 0),
            """
            --- initial
            +++ mutation
            @@ -1,6 +1,17 @@
             <session.contexts[0]>
                 NODE TREE 1000 group
                     1001 group
            +            1043 group
            +                1044 group
            +                1047 supriya:meters:2
            +                    in_: 30.0, out: 37.0
            +                1045 group
            +                1046 supriya:channel-strip:2
            +                    active: c35, bus: 30.0, gain: c36, gate: 1.0
            +                1048 supriya:meters:2
            +                    in_: 30.0, out: 39.0
            +                1049 supriya:patch-cable:2x2
            +                    active: c35, gain: 0.0, gate: 1.0, in_: 30.0, out: 16.0
                         1006 group
                             1007 group
                                 1012 group
            @@ -62,17 +73,6 @@
                                 in_: 26.0, out: 33.0
                             1040 supriya:patch-cable:2x2
                                 active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 16.0
            -            1043 group
            -                1044 group
            -                1047 supriya:meters:2
            -                    in_: 30.0, out: 37.0
            -                1045 group
            -                1046 supriya:channel-strip:2
            -                    active: c35, bus: 30.0, gain: c36, gate: 1.0
            -                1048 supriya:meters:2
            -                    in_: 30.0, out: 39.0
            -                1049 supriya:patch-cable:2x2
            -                    active: c35, gain: 0.0, gate: 1.0, in_: 30.0, out: 16.0
                     1004 supriya:meters:2
                         in_: 16.0, out: 1.0
                     1002 group
            """,
            [OscMessage("/g_head", 1001, 1043)],
        ),
        (
            "mixers[0].tracks[1]",
            "mixers[1]",
            0,
            pytest.raises(RuntimeError),
            (0, 1),
            "",
            [],
        ),
    ],
)
@pytest.mark.asyncio
async def test_Track_move(
    complex_session: Tuple[Session, str],
    expected_commands: List[Union[OscBundle, OscMessage]],
    expected_graph_order: List[int],
    expected_diff: str,
    index: int,
    online: bool,
    parent: str,
    target: str,
    maybe_raises,
) -> None:
    # Pre-conditions
    print("Pre-conditions")
    session, _ = complex_session
    if online:
        await session.boot()
        initial_tree = await debug_tree(session, annotated=False)
    target_ = session[target]
    parent_ = session[parent]
    assert isinstance(target_, Track)
    assert isinstance(parent_, TrackContainer)
    # Operation
    print("Operation")
    with maybe_raises, capture(session["mixers[0]"].context) as commands:
        await target_.move(index=index, parent=parent_)
    # Post-conditions
    print("Post-conditions")
    assert target_.graph_order == expected_graph_order
    if not online:
        return
    await assert_diff(
        session,
        expected_diff,
        expected_initial_tree=initial_tree,
        annotated=False,
    )
    assert commands == expected_commands


@pytest.mark.xfail
@pytest.mark.parametrize("online", [False, True])
@pytest.mark.parametrize("expected_commands, expected_diff", [([], "")])
@pytest.mark.asyncio
async def test_Track_set_active(
    complex_session: Tuple[Session, str],
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
