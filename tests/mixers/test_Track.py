import asyncio
from typing import Dict, List, Optional, Tuple, Union, cast

import pytest

from supriya import BusGroup, OscBundle, OscMessage
from supriya.mixers import Session
from supriya.mixers.mixers import Mixer
from supriya.mixers.tracks import Track, TrackContainer, TrackSend
from supriya.typing import DEFAULT, Default

from .conftest import assert_diff, capture, debug_tree, does_not_raise


@pytest.mark.parametrize("online", [False, True])
@pytest.mark.parametrize(
    "postfader, source, target, maybe_raises, expected_commands, expected_diff",
    [
        (
            True,
            "mixers[0].tracks[1]",
            "mixers[0]",
            does_not_raise,
            [
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
                    16.0,
                ),
            ],
            """
            --- initial
            +++ mutation
            @@ -56,6 +56,8 @@
                             1036 group (session.mixers[0].tracks[1]:devices)
                             1037 supriya:channel-strip:2 (session.mixers[0].tracks[1]:channel-strip)
                                 active: c29, bus: 26.0, gain: c30, gate: 1.0
            +                1066 supriya:patch-cable:2x2 (session.mixers[0].tracks[1].sends[1]:synth)
            +                    active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 16.0
                             1042 supriya:patch-cable:2x2 (session.mixers[0].tracks[1].sends[0]:synth)
                                 active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 28.0
                             1039 supriya:meters:2 (session.mixers[0].tracks[1]:output-levels)
            """,
        ),
        (
            True,
            "mixers[0].tracks[1]",
            "mixers[0].tracks[2]",
            does_not_raise,
            [
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
                    30.0,
                ),
            ],
            """
            --- initial
            +++ mutation
            @@ -56,6 +56,8 @@
                             1036 group (session.mixers[0].tracks[1]:devices)
                             1037 supriya:channel-strip:2 (session.mixers[0].tracks[1]:channel-strip)
                                 active: c29, bus: 26.0, gain: c30, gate: 1.0
            +                1066 supriya:patch-cable:2x2 (session.mixers[0].tracks[1].sends[1]:synth)
            +                    active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 30.0
                             1042 supriya:patch-cable:2x2 (session.mixers[0].tracks[1].sends[0]:synth)
                                 active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 28.0
                             1039 supriya:meters:2 (session.mixers[0].tracks[1]:output-levels)
            """,
        ),
        (
            False,
            "mixers[0].tracks[1]",
            "mixers[0].tracks[2]",
            does_not_raise,
            [
                OscMessage(
                    "/s_new",
                    "supriya:patch-cable:2x2",
                    1066,
                    2,
                    1037,
                    "active",
                    "c29",
                    "in_",
                    26.0,
                    "out",
                    30.0,
                ),
            ],
            """
            --- initial
            +++ mutation
            @@ -54,6 +54,8 @@
                             1038 supriya:meters:2 (session.mixers[0].tracks[1]:input-levels)
                                 in_: 26.0, out: 31.0
                             1036 group (session.mixers[0].tracks[1]:devices)
            +                1066 supriya:patch-cable:2x2 (session.mixers[0].tracks[1].sends[1]:synth)
            +                    active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 30.0
                             1037 supriya:channel-strip:2 (session.mixers[0].tracks[1]:channel-strip)
                                 active: c29, bus: 26.0, gain: c30, gate: 1.0
                             1042 supriya:patch-cable:2x2 (session.mixers[0].tracks[1].sends[0]:synth)
            """,
        ),
        (
            False,
            "mixers[0].tracks[1]",
            "mixers[0].tracks[1]",
            does_not_raise,
            [
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
                OscMessage(
                    "/s_new",
                    "supriya:patch-cable:2x2",
                    1067,
                    2,
                    1037,
                    "active",
                    "c29",
                    "in_",
                    26.0,
                    "out",
                    36.0,
                ),
            ],
            """
            --- initial
            +++ mutation
            @@ -50,10 +50,14 @@
                             1033 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].output:synth)
                                 active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 16.0
                         1034 group (session.mixers[0].tracks[1]:group)
            +                1066 supriya:fb-patch-cable:2x2 (session.mixers[0].tracks[1].feedback:synth)
            +                    active: c29, gain: 0.0, gate: 1.0, in_: 36.0, out: 26.0
                             1035 group (session.mixers[0].tracks[1]:tracks)
                             1038 supriya:meters:2 (session.mixers[0].tracks[1]:input-levels)
                                 in_: 26.0, out: 31.0
                             1036 group (session.mixers[0].tracks[1]:devices)
            +                1067 supriya:patch-cable:2x2 (session.mixers[0].tracks[1].sends[1]:synth)
            +                    active: c29, gain: 0.0, gate: 1.0, in_: 26.0, out: 36.0
                             1037 supriya:channel-strip:2 (session.mixers[0].tracks[1]:channel-strip)
                                 active: c29, bus: 26.0, gain: c30, gate: 1.0
                             1042 supriya:patch-cable:2x2 (session.mixers[0].tracks[1].sends[0]:synth)
            """,
        ),
        (
            True,
            "mixers[0].tracks[2]",
            "mixers[0].tracks[1]",
            does_not_raise,
            [
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
                OscMessage(
                    "/s_new",
                    "supriya:patch-cable:2x2",
                    1067,
                    3,
                    1046,
                    "active",
                    "c35",
                    "in_",
                    30.0,
                    "out",
                    36.0,
                ),
            ],
            """
            --- initial
            +++ mutation
            @@ -50,6 +50,8 @@
                             1033 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].output:synth)
                                 active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 16.0
                         1034 group (session.mixers[0].tracks[1]:group)
            +                1066 supriya:fb-patch-cable:2x2 (session.mixers[0].tracks[1].feedback:synth)
            +                    active: c29, gain: 0.0, gate: 1.0, in_: 36.0, out: 26.0
                             1035 group (session.mixers[0].tracks[1]:tracks)
                             1038 supriya:meters:2 (session.mixers[0].tracks[1]:input-levels)
                                 in_: 26.0, out: 31.0
            @@ -69,6 +71,8 @@
                             1045 group (session.mixers[0].tracks[2]:devices)
                             1046 supriya:channel-strip:2 (session.mixers[0].tracks[2]:channel-strip)
                                 active: c35, bus: 30.0, gain: c36, gate: 1.0
            +                1067 supriya:patch-cable:2x2 (session.mixers[0].tracks[2].sends[0]:synth)
            +                    active: c35, gain: 0.0, gate: 1.0, in_: 30.0, out: 36.0
                             1048 supriya:meters:2 (session.mixers[0].tracks[2]:output-levels)
                                 in_: 30.0, out: 39.0
                             1049 supriya:patch-cable:2x2 (session.mixers[0].tracks[2].output:synth)
            """,
        ),
        (
            True,
            "mixers[0].tracks[1]",
            "mixers[1].tracks[0]",
            pytest.raises(RuntimeError),
            [],
            """
            """,
        ),
    ],
)
@pytest.mark.asyncio
async def test_Track_add_send(
    complex_session: Tuple[Session, str],
    expected_commands: List[Union[OscBundle, OscMessage]],
    expected_diff: str,
    maybe_raises,
    online: bool,
    postfader: bool,
    source: str,
    target: str,
) -> None:
    # Pre-conditions
    session, initial_tree = complex_session
    if online:
        await session.boot()
    source_ = session[source]
    target_ = session[target]
    assert isinstance(source_, Track)
    assert isinstance(target_, TrackContainer)
    if online:
        await debug_tree(session)
    # Operation
    send: Optional[TrackSend] = None
    with maybe_raises, capture(session["mixers[0]"].context) as commands:
        send = await source_.add_send(postfader=postfader, target=target_)
    # Post-conditions
    if send is not None:
        assert isinstance(send, TrackSend)
        assert send in source_.sends
        assert send.parent is source_
        assert send.postfader == postfader
        assert send.target is target_
        assert source_.sends[-1] is send
    if not online:
        return
    await assert_diff(
        session,
        expected_diff,
        expected_initial_tree=initial_tree,
    )
    assert commands == expected_commands


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


@pytest.mark.parametrize("online", [False, True])
@pytest.mark.parametrize(
    "source, target, maybe_raises, expected_commands, expected_diff",
    [
        # none
        (
            "mixers[0].tracks[0].tracks[0]",
            None,
            does_not_raise,
            [],
            """
            """,
        ),
        # self
        (
            "mixers[0].tracks[0].tracks[0]",
            "mixers[0].tracks[0].tracks[0]",
            pytest.raises(RuntimeError),
            [],
            "",
        ),
        # parent
        # TODO: This should feedback, because the reader is calculated before
        #       the writer.
        (
            "mixers[0].tracks[0].tracks[0]",
            "mixers[0].tracks[0]",
            does_not_raise,
            [
                OscMessage(
                    "/s_new",
                    "supriya:fb-patch-cable:2x2",
                    1066,
                    2,
                    1013,
                    "active",
                    "c11",
                    "in_",
                    18.0,
                    "out",
                    20.0,
                ),
            ],
            """
            --- initial
            +++ mutation
            @@ -6,6 +6,8 @@
                                 1012 group (session.mixers[0].tracks[0].tracks[0]:group)
                                     1041 supriya:fb-patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].feedback:synth)
                                         active: c11, gain: 0.0, gate: 1.0, in_: 28.0, out: 20.0
            +                        1066 supriya:fb-patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].input:synth)
            +                            active: c11, gain: 0.0, gate: 1.0, in_: 18.0, out: 20.0
                                     1013 group (session.mixers[0].tracks[0].tracks[0]:tracks)
                                         1018 group (session.mixers[0].tracks[0].tracks[0].tracks[0]:group)
                                             1019 group (session.mixers[0].tracks[0].tracks[0].tracks[0]:tracks)
            """,
        ),
        # child
        (
            "mixers[0].tracks[0].tracks[0]",
            "mixers[0].tracks[0].tracks[0].tracks[0]",
            does_not_raise,
            [
                OscMessage(
                    "/s_new",
                    "supriya:patch-cable:2x2",
                    1066,
                    2,
                    1013,
                    "active",
                    "c11",
                    "in_",
                    22.0,
                    "out",
                    20.0,
                ),
            ],
            """
            --- initial
            +++ mutation
            @@ -6,6 +6,8 @@
                                 1012 group (session.mixers[0].tracks[0].tracks[0]:group)
                                     1041 supriya:fb-patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].feedback:synth)
                                         active: c11, gain: 0.0, gate: 1.0, in_: 28.0, out: 20.0
            +                        1066 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].input:synth)
            +                            active: c11, gain: 0.0, gate: 1.0, in_: 22.0, out: 20.0
                                     1013 group (session.mixers[0].tracks[0].tracks[0]:tracks)
                                         1018 group (session.mixers[0].tracks[0].tracks[0].tracks[0]:group)
                                             1019 group (session.mixers[0].tracks[0].tracks[0].tracks[0]:tracks)
            """,
        ),
        # auntie
        # TODO: This should feedback, because the reader is calculated before
        #       the writer.
        (
            "mixers[0].tracks[0].tracks[0]",
            "mixers[0].tracks[1]",
            does_not_raise,
            [
                OscMessage(
                    "/s_new",
                    "supriya:fb-patch-cable:2x2",
                    1066,
                    2,
                    1013,
                    "active",
                    "c11",
                    "in_",
                    26.0,
                    "out",
                    20.0,
                ),
            ],
            """
            --- initial
            +++ mutation
            @@ -6,6 +6,8 @@
                                 1012 group (session.mixers[0].tracks[0].tracks[0]:group)
                                     1041 supriya:fb-patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].feedback:synth)
                                         active: c11, gain: 0.0, gate: 1.0, in_: 28.0, out: 20.0
            +                        1066 supriya:fb-patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].input:synth)
            +                            active: c11, gain: 0.0, gate: 1.0, in_: 26.0, out: 20.0
                                     1013 group (session.mixers[0].tracks[0].tracks[0]:tracks)
                                         1018 group (session.mixers[0].tracks[0].tracks[0].tracks[0]:group)
                                             1019 group (session.mixers[0].tracks[0].tracks[0].tracks[0]:tracks)
            """,
        ),
        # sibling, reversed
        # NOTE: Does not need to feedback.
        (
            "mixers[0].tracks[1]",
            "mixers[0].tracks[0]",
            does_not_raise,
            [
                OscMessage(
                    "/s_new",
                    "supriya:patch-cable:2x2",
                    1066,
                    2,
                    1035,
                    "active",
                    "c29",
                    "in_",
                    18.0,
                    "out",
                    26.0,
                ),
            ],
            """
            --- initial
            +++ mutation
            @@ -50,6 +50,8 @@
                             1033 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].output:synth)
                                 active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 16.0
                         1034 group (session.mixers[0].tracks[1]:group)
            +                1066 supriya:patch-cable:2x2 (session.mixers[0].tracks[1].input:synth)
            +                    active: c29, gain: 0.0, gate: 1.0, in_: 18.0, out: 26.0
                             1035 group (session.mixers[0].tracks[1]:tracks)
                             1038 supriya:meters:2 (session.mixers[0].tracks[1]:input-levels)
                                 in_: 26.0, out: 31.0
            """,
        ),
        # sibling
        # TODO: This should feedback, because the reader is calculated before
        #       the writer.
        (
            "mixers[0].tracks[0].tracks[0]",
            "mixers[0].tracks[0].tracks[1]",
            does_not_raise,
            [
                OscMessage(
                    "/s_new",
                    "supriya:fb-patch-cable:2x2",
                    1066,
                    2,
                    1013,
                    "active",
                    "c11",
                    "in_",
                    24.0,
                    "out",
                    20.0,
                ),
            ],
            """
            --- initial
            +++ mutation
            @@ -6,6 +6,8 @@
                                 1012 group (session.mixers[0].tracks[0].tracks[0]:group)
                                     1041 supriya:fb-patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].feedback:synth)
                                         active: c11, gain: 0.0, gate: 1.0, in_: 28.0, out: 20.0
            +                        1066 supriya:fb-patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].input:synth)
            +                            active: c11, gain: 0.0, gate: 1.0, in_: 24.0, out: 20.0
                                     1013 group (session.mixers[0].tracks[0].tracks[0]:tracks)
                                         1018 group (session.mixers[0].tracks[0].tracks[0].tracks[0]:group)
                                             1019 group (session.mixers[0].tracks[0].tracks[0].tracks[0]:tracks)
            """,
        ),
        # other mixer
        (
            "mixers[0].tracks[0]",
            "mixers[1].tracks[0]",
            pytest.raises(RuntimeError),
            [],
            "",
        ),
    ],
)
@pytest.mark.asyncio
async def test_Track_set_input(
    complex_session: Tuple[Session, str],
    expected_commands: List[Union[OscBundle, OscMessage]],
    expected_diff: str,
    maybe_raises,
    online: bool,
    source: str,
    target: Optional[Union[str, Tuple[int, int]]],
) -> None:
    # Pre-conditions
    session, initial_tree = complex_session
    if online:
        await session.boot()
    source_ = session[source]
    assert isinstance(source_, Track)
    target_: Optional[Union[BusGroup, Track]] = None
    # TODO: Because the context could be null, we need the "promise" of a bus group.
    if isinstance(target, str):
        target_component = session[target]
        assert isinstance(target_component, Track)
        target_ = target_component
    # elif isinstance(target, tuple):
    #     index, count = target
    #     target_ = BusGroup(
    #         context=session["mixers[0]"].context,
    #         calculation_rate=CalculationRate.AUDIO,
    #         id_=index,
    #         count=count,
    #     )
    # Operation
    with maybe_raises, capture(session["mixers[0]"].context) as commands:
        await source_.set_input(target_)
    # Post-conditions
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
    "target, muted, expected_commands, expected_state",
    [
        (
            "mixers[0].tracks[0]",
            True,
            [OscMessage("/c_set", 5, 0.0)],
            [
                ("m[0].t[0]", (0.0, 0.0), False),
                ("m[0].t[0].t[0]", (1.0, 1.0), True),
                ("m[0].t[0].t[0].t[0]", (1.0, 1.0), True),
                ("m[0].t[0].t[1]", (0.0, 0.0), True),
                ("m[0].t[1]", (0.0, 0.0), True),
                ("m[0].t[2]", (0.0, 0.0), True),
                ("m[1].t[0]", (0.0, 0.0), True),
            ],
        ),
        (
            "mixers[0].tracks[0].tracks[0]",
            True,
            [OscMessage("/c_set", 11, 0.0)],
            [
                ("m[0].t[0]", (0.0, 0.0), True),
                ("m[0].t[0].t[0]", (0.0, 0.0), False),
                ("m[0].t[0].t[0].t[0]", (1.0, 1.0), True),
                ("m[0].t[0].t[1]", (0.0, 0.0), True),
                ("m[0].t[1]", (0.0, 0.0), True),
                ("m[0].t[2]", (0.0, 0.0), True),
                ("m[1].t[0]", (0.0, 0.0), True),
            ],
        ),
    ],
)
@pytest.mark.asyncio
async def test_Track_set_muted(
    muted: bool,
    complex_session: Tuple[Session, str],
    expected_commands: List[Union[OscBundle, OscMessage]],
    expected_state: List[Tuple[str, Tuple[float, ...], bool]],
    online: bool,
    target: str,
) -> None:
    # Pre-conditions
    session, _ = complex_session
    if online:
        await session.boot()
        await session.mixers[0].tracks[0].tracks[0].tracks[0].add_device()
        await session.mixers[0].tracks[1].sends[0].delete()
        await asyncio.sleep(0.25)
        initial_tree = await debug_tree(session)
    target_ = session[target]
    assert isinstance(target_, Track)
    # Operation
    with capture(session["mixers[0]"].context) as commands:
        await target_.set_muted(muted)
    # Post-conditions
    if not online:
        return
    await assert_diff(
        session,
        "",
        expected_initial_tree=initial_tree,
    )
    assert commands == expected_commands
    assert [
        (
            track.short_address,
            tuple(round(x, 6) for x in cast(Track, track).output_levels),
            track.is_active,
        )
        for track in session._walk(Track)
    ] == expected_state


@pytest.mark.parametrize("online", [False, True])
@pytest.mark.parametrize(
    "source, target, maybe_raises, expected_commands, expected_diff",
    [
        # none
        (
            "mixers[0].tracks[0].tracks[0]",
            None,
            does_not_raise,
            [
                OscMessage("/n_set", 1025, "gate", 0.0),
            ],
            """
            --- initial
            +++ mutation
            @@ -25,8 +25,8 @@
                                         active: c11, bus: 20.0, gain: c12, gate: 1.0
                                     1017 supriya:meters:2 (session.mixers[0].tracks[0].tracks[0]:output-levels)
                                         in_: 20.0, out: 15.0
            -                        1025 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].output:synth)
            -                            active: c11, gain: 0.0, gate: 1.0, in_: 20.0, out: 18.0
            +                        1025 supriya:patch-cable:2x2
            +                            active: c11, gain: 0.0, gate: 0.0, in_: 20.0, out: 18.0
                                 1026 group (session.mixers[0].tracks[0].tracks[1]:group)
                                     1027 group (session.mixers[0].tracks[0].tracks[1]:tracks)
                                     1030 supriya:meters:2 (session.mixers[0].tracks[0].tracks[1]:input-levels)
            """,
        ),
        # default: no-op
        (
            "mixers[0].tracks[0].tracks[0]",
            DEFAULT,
            does_not_raise,
            [],
            "",
        ),
        # self
        (
            "mixers[0].tracks[0].tracks[0]",
            "mixers[0].tracks[0].tracks[0]",
            pytest.raises(RuntimeError),
            [],
            "",
        ),
        # parent: no-op
        (
            "mixers[0].tracks[0].tracks[0]",
            "mixers[0].tracks[0]",
            does_not_raise,
            [],
            "",
        ),
        # child
        (
            "mixers[0].tracks[0].tracks[0]",
            "mixers[0].tracks[0].tracks[0].tracks[0]",
            does_not_raise,
            [
                OscMessage(
                    "/s_new",
                    "supriya:fb-patch-cable:2x2",
                    1066,
                    0,
                    1018,
                    "active",
                    "c17",
                    "in_",
                    36.0,
                    "out",
                    22.0,
                ),
                OscBundle(
                    contents=(
                        OscMessage("/n_set", 1025, "gate", 0.0),
                        OscMessage(
                            "/s_new",
                            "supriya:patch-cable:2x2",
                            1067,
                            1,
                            1012,
                            "active",
                            "c11",
                            "in_",
                            20.0,
                            "out",
                            36.0,
                        ),
                    ),
                ),
            ],
            """
            --- initial
            +++ mutation
            @@ -8,6 +8,8 @@
                                         active: c11, gain: 0.0, gate: 1.0, in_: 28.0, out: 20.0
                                     1013 group (session.mixers[0].tracks[0].tracks[0]:tracks)
                                         1018 group (session.mixers[0].tracks[0].tracks[0].tracks[0]:group)
            +                                1066 supriya:fb-patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].tracks[0].feedback:synth)
            +                                    active: c17, gain: 0.0, gate: 1.0, in_: 36.0, out: 22.0
                                             1019 group (session.mixers[0].tracks[0].tracks[0].tracks[0]:tracks)
                                             1022 supriya:meters:2 (session.mixers[0].tracks[0].tracks[0].tracks[0]:input-levels)
                                                 in_: 22.0, out: 19.0
            @@ -25,8 +27,10 @@
                                         active: c11, bus: 20.0, gain: c12, gate: 1.0
                                     1017 supriya:meters:2 (session.mixers[0].tracks[0].tracks[0]:output-levels)
                                         in_: 20.0, out: 15.0
            -                        1025 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].output:synth)
            -                            active: c11, gain: 0.0, gate: 1.0, in_: 20.0, out: 18.0
            +                        1025 supriya:patch-cable:2x2
            +                            active: c11, gain: 0.0, gate: 0.0, in_: 20.0, out: 18.0
            +                        1067 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].output:synth)
            +                            active: c11, gain: 0.0, gate: 1.0, in_: 20.0, out: 36.0
                                 1026 group (session.mixers[0].tracks[0].tracks[1]:group)
                                     1027 group (session.mixers[0].tracks[0].tracks[1]:tracks)
                                     1030 supriya:meters:2 (session.mixers[0].tracks[0].tracks[1]:input-levels)
            """,
        ),
        # auntie
        (
            "mixers[0].tracks[0].tracks[0]",
            "mixers[0].tracks[1]",
            does_not_raise,
            [
                OscBundle(
                    contents=(
                        OscMessage("/n_set", 1025, "gate", 0.0),
                        OscMessage(
                            "/s_new",
                            "supriya:patch-cable:2x2",
                            1066,
                            1,
                            1012,
                            "active",
                            "c11",
                            "in_",
                            20.0,
                            "out",
                            26.0,
                        ),
                    ),
                ),
            ],
            """
            --- initial
            +++ mutation
            @@ -25,8 +25,10 @@
                                         active: c11, bus: 20.0, gain: c12, gate: 1.0
                                     1017 supriya:meters:2 (session.mixers[0].tracks[0].tracks[0]:output-levels)
                                         in_: 20.0, out: 15.0
            -                        1025 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].output:synth)
            -                            active: c11, gain: 0.0, gate: 1.0, in_: 20.0, out: 18.0
            +                        1025 supriya:patch-cable:2x2
            +                            active: c11, gain: 0.0, gate: 0.0, in_: 20.0, out: 18.0
            +                        1066 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].output:synth)
            +                            active: c11, gain: 0.0, gate: 1.0, in_: 20.0, out: 26.0
                                 1026 group (session.mixers[0].tracks[0].tracks[1]:group)
                                     1027 group (session.mixers[0].tracks[0].tracks[1]:tracks)
                                     1030 supriya:meters:2 (session.mixers[0].tracks[0].tracks[1]:input-levels)
            """,
        ),
        # mixer: no-op
        (
            "mixers[0].tracks[0]",
            "mixers[0]",
            does_not_raise,
            [],
            """
            """,
        ),
        # sibling
        (
            "mixers[0].tracks[0].tracks[0]",
            "mixers[0].tracks[0].tracks[1]",
            does_not_raise,
            [
                OscBundle(
                    contents=(
                        OscMessage("/n_set", 1025, "gate", 0.0),
                        OscMessage(
                            "/s_new",
                            "supriya:patch-cable:2x2",
                            1066,
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
            @@ -25,8 +25,10 @@
                                         active: c11, bus: 20.0, gain: c12, gate: 1.0
                                     1017 supriya:meters:2 (session.mixers[0].tracks[0].tracks[0]:output-levels)
                                         in_: 20.0, out: 15.0
            -                        1025 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].output:synth)
            -                            active: c11, gain: 0.0, gate: 1.0, in_: 20.0, out: 18.0
            +                        1025 supriya:patch-cable:2x2
            +                            active: c11, gain: 0.0, gate: 0.0, in_: 20.0, out: 18.0
            +                        1066 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].tracks[0].output:synth)
            +                            active: c11, gain: 0.0, gate: 1.0, in_: 20.0, out: 24.0
                                 1026 group (session.mixers[0].tracks[0].tracks[1]:group)
                                     1027 group (session.mixers[0].tracks[0].tracks[1]:tracks)
                                     1030 supriya:meters:2 (session.mixers[0].tracks[0].tracks[1]:input-levels)
            """,
        ),
        # other mixer
        (
            "mixers[0].tracks[0]",
            "mixers[1].tracks[0]",
            pytest.raises(RuntimeError),
            [],
            "",
        ),
    ],
)
@pytest.mark.asyncio
async def test_Track_set_output(
    complex_session: Tuple[Session, str],
    expected_commands: List[Union[OscBundle, OscMessage]],
    expected_diff: str,
    maybe_raises,
    online: bool,
    source: str,
    target: Optional[Union[Default, str, Tuple[int, int]]],
) -> None:
    # Pre-conditions
    session, initial_tree = complex_session
    if online:
        await session.boot()
    source_ = session[source]
    assert isinstance(source_, Track)
    target_: Optional[Union[BusGroup, Default, TrackContainer]] = None
    if isinstance(target, Default):
        target_ = DEFAULT
    elif isinstance(target, str):
        target_component = session[target]
        assert isinstance(target_component, TrackContainer)
        target_ = target_component
    # TODO: Because the context could be null, we need the "promise" of a bus group.
    # elif isinstance(target, tuple):
    #     index, count = target
    #     target_ = BusGroup(
    #         context=session["mixers[0]"].context,
    #         calculation_rate=CalculationRate.AUDIO,
    #         id_=index,
    #         count=count,
    #     )
    # Operation
    with maybe_raises, capture(session["mixers[0]"].context) as commands:
        await source_.set_output(target_)
    # Post-conditions
    if not online:
        return
    await assert_diff(
        session,
        expected_diff,
        expected_initial_tree=initial_tree,
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
    assert isinstance(target_, Track)
    # Operation
    with capture(session["mixers[0]"].context) as commands:
        await target_.set_soloed()
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
    assert isinstance(target_, Track)
    # Operation
    with capture(session["mixers[0]"].context) as commands:
        await target_.ungroup()
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
