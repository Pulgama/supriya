from contextlib import nullcontext as does_not_raise

import pytest
from uqbar.strings import normalize

from supriya.enums import BootStatus
from supriya.mixers import Session

from .conftest import assert_diff, debug_tree


@pytest.mark.parametrize("online", [False, True])
@pytest.mark.asyncio
async def test_Session_boot(online: bool, session: Session) -> None:
    # Pre-conditions
    assert session.status == BootStatus.OFFLINE
    if online:
        await session.boot()
        assert session.status == BootStatus.ONLINE
    # Operation
    await session.boot()  # idempotent
    # Post-conditions
    assert session.status == BootStatus.ONLINE
    assert await session.dump_tree() == normalize(
        f"""
        {session.contexts[0]!r}
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
        """
    )


@pytest.mark.parametrize("online", [False, True])
@pytest.mark.asyncio
async def test_Session_quit(online: bool, session: Session) -> None:
    # Pre-conditions
    assert session.status == BootStatus.OFFLINE
    if online:
        await session.boot()
        assert session.status == BootStatus.ONLINE
    # Operation
    await session.quit()
    # Post-conditions
    assert session.status == BootStatus.OFFLINE
    with pytest.raises(RuntimeError):
        assert await session.dump_tree()


@pytest.mark.parametrize(
    "online, expectation",
    [
        (False, pytest.raises(RuntimeError)),
        (True, does_not_raise()),
    ],
)
@pytest.mark.asyncio
async def test_Session_add_context(expectation, online: bool, session: Session) -> None:
    # Pre-conditions
    if online:
        await session.boot()
    assert len(session.contexts) == 1
    # Operation
    context = await session.add_context()
    # Post-conditions
    assert len(session.contexts) == 2
    assert context in session.contexts
    assert context.boot_status == session.status
    with expectation:
        assert await session.dump_tree() == normalize(
            f"""
            {session.contexts[0]!r}
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
            {session.contexts[1]!r}
            """
        )


@pytest.mark.parametrize(
    "online, expectation, reuse_context",
    [
        (False, pytest.raises(RuntimeError), False),
        (True, does_not_raise(), False),
        (True, does_not_raise(), True),
    ],
)
@pytest.mark.asyncio
async def test_Session_add_mixer(
    expectation, online: bool, reuse_context, session: Session
) -> None:
    # Pre-conditions
    if online:
        await session.boot()
    await session.add_context()
    assert len(session.mixers) == 1
    # Operation
    await session.add_mixer(context=None if reuse_context else session.contexts[1])
    # Post-conditions
    assert len(session.mixers) == 2
    with expectation:
        if not reuse_context:
            assert await session.dump_tree() == normalize(
                f"""
                {session.contexts[0]!r}
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
                {session.contexts[1]!r}
                    NODE TREE 1000 group (session.mixers[1]:group)
                        1001 group (session.mixers[1]:tracks)
                            1006 group (session.mixers[1].tracks[0]:group)
                                1007 group (session.mixers[1].tracks[0]:tracks)
                                1010 supriya:meters:2 (session.mixers[1].tracks[0]:input-levels)
                                    in_: 18.0, out: 7.0
                                1008 group (session.mixers[1].tracks[0]:devices)
                                1009 supriya:channel-strip:2 (session.mixers[1].tracks[0]:channel-strip)
                                    active: c5, bus: 18.0, gain: c6, gate: 1.0
                                1011 supriya:meters:2 (session.mixers[1].tracks[0]:output-levels)
                                    in_: 18.0, out: 9.0
                                1012 supriya:patch-cable:2x2 (session.mixers[1].tracks[0].output:synth)
                                    active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 16.0
                        1004 supriya:meters:2 (session.mixers[1]:input-levels)
                            in_: 16.0, out: 1.0
                        1002 group (session.mixers[1]:devices)
                        1003 supriya:channel-strip:2 (session.mixers[1]:channel-strip)
                            active: 1.0, bus: 16.0, gain: c0, gate: 1.0
                        1005 supriya:meters:2 (session.mixers[1]:output-levels)
                            in_: 16.0, out: 3.0
                        1013 supriya:patch-cable:2x2 (session.mixers[1].output:synth)
                            active: 1.0, gain: 0.0, gate: 1.0, in_: 16.0, out: 0.0
                """
            )
        else:
            assert await session.dump_tree() == normalize(
                f"""
                {session.contexts[0]!r}
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
                    NODE TREE 1014 group (session.mixers[1]:group)
                        1015 group (session.mixers[1]:tracks)
                            1020 group (session.mixers[1].tracks[0]:group)
                                1021 group (session.mixers[1].tracks[0]:tracks)
                                1024 supriya:meters:2 (session.mixers[1].tracks[0]:input-levels)
                                    in_: 22.0, out: 18.0
                                1022 group (session.mixers[1].tracks[0]:devices)
                                1023 supriya:channel-strip:2 (session.mixers[1].tracks[0]:channel-strip)
                                    active: c16, bus: 22.0, gain: c17, gate: 1.0
                                1025 supriya:meters:2 (session.mixers[1].tracks[0]:output-levels)
                                    in_: 22.0, out: 20.0
                                1026 supriya:patch-cable:2x2 (session.mixers[1].tracks[0].output:synth)
                                    active: c16, gain: 0.0, gate: 1.0, in_: 22.0, out: 20.0
                        1018 supriya:meters:2 (session.mixers[1]:input-levels)
                            in_: 20.0, out: 12.0
                        1016 group (session.mixers[1]:devices)
                        1017 supriya:channel-strip:2 (session.mixers[1]:channel-strip)
                            active: 1.0, bus: 20.0, gain: c11, gate: 1.0
                        1019 supriya:meters:2 (session.mixers[1]:output-levels)
                            in_: 20.0, out: 14.0
                        1027 supriya:patch-cable:2x2 (session.mixers[1].output:synth)
                            active: 1.0, gain: 0.0, gate: 1.0, in_: 20.0, out: 0.0
                {session.contexts[1]!r}
                """
            )


@pytest.mark.parametrize(
    "online, expectation",
    [
        (False, pytest.raises(RuntimeError)),
        (True, does_not_raise()),
    ],
)
@pytest.mark.asyncio
async def test_Session_delete_context(
    expectation, online: bool, session: Session
) -> None:
    # Pre-conditions
    if online:
        await session.boot()
    await session.add_context()
    # Operation
    await session.delete_context(session.contexts[0])
    # Post-conditions
    assert len(session.contexts) == 1
    assert len(session.mixers) == 0
    with expectation:
        assert await session.dump_tree() == normalize(
            f"""
            {session.contexts[0]!r}
            """
        )


@pytest.mark.parametrize("online", [False, True])
@pytest.mark.parametrize(
    "mixer_index, context_index, expected_diff",
    [
        (0, 0, ""),
        (
            0,
            1,
            """
            --- initial
            +++ mutation
            @@ -1,26 +1,4 @@
             <session.contexts[0]>
            -    NODE TREE 1000 group (session.mixers[0]:group)
            -        1001 group (session.mixers[0]:tracks)
            -            1006 group (session.mixers[0].tracks[0]:group)
            -                1007 group (session.mixers[0].tracks[0]:tracks)
            -                1010 supriya:meters:2 (session.mixers[0].tracks[0]:input-levels)
            -                    in_: 18.0, out: 7.0
            -                1008 group (session.mixers[0].tracks[0]:devices)
            -                1009 supriya:channel-strip:2 (session.mixers[0].tracks[0]:channel-strip)
            -                    active: c5, bus: 18.0, gain: c6, gate: 1.0
            -                1011 supriya:meters:2 (session.mixers[0].tracks[0]:output-levels)
            -                    in_: 18.0, out: 9.0
            -                1012 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].output:synth)
            -                    active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 16.0
            -        1004 supriya:meters:2 (session.mixers[0]:input-levels)
            -            in_: 16.0, out: 1.0
            -        1002 group (session.mixers[0]:devices)
            -        1003 supriya:channel-strip:2 (session.mixers[0]:channel-strip)
            -            active: 1.0, bus: 16.0, gain: c0, gate: 1.0
            -        1005 supriya:meters:2 (session.mixers[0]:output-levels)
            -            in_: 16.0, out: 3.0
            -        1013 supriya:patch-cable:2x2 (session.mixers[0].output:synth)
            -            active: 1.0, gain: 0.0, gate: 1.0, in_: 16.0, out: 0.0
                 NODE TREE 1014 group (session.mixers[1]:group)
                     1015 group (session.mixers[1]:tracks)
                         1020 group (session.mixers[1].tracks[0]:group)
            @@ -43,4 +21,26 @@
                         in_: 20.0, out: 14.0
                     1027 supriya:patch-cable:2x2 (session.mixers[1].output:synth)
                         active: 1.0, gain: 0.0, gate: 1.0, in_: 20.0, out: 0.0
            -<session.contexts[1]>+<session.contexts[1]>
            +    NODE TREE 1000 group (session.mixers[0]:group)
            +        1001 group (session.mixers[0]:tracks)
            +            1006 group (session.mixers[0].tracks[0]:group)
            +                1007 group (session.mixers[0].tracks[0]:tracks)
            +                1010 supriya:meters:2 (session.mixers[0].tracks[0]:input-levels)
            +                    in_: 18.0, out: 7.0
            +                1008 group (session.mixers[0].tracks[0]:devices)
            +                1009 supriya:channel-strip:2 (session.mixers[0].tracks[0]:channel-strip)
            +                    active: c5, bus: 18.0, gain: c6, gate: 1.0
            +                1011 supriya:meters:2 (session.mixers[0].tracks[0]:output-levels)
            +                    in_: 18.0, out: 9.0
            +                1012 supriya:patch-cable:2x2 (session.mixers[0].tracks[0].output:synth)
            +                    active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 16.0
            +        1004 supriya:meters:2 (session.mixers[0]:input-levels)
            +            in_: 16.0, out: 1.0
            +        1002 group (session.mixers[0]:devices)
            +        1003 supriya:channel-strip:2 (session.mixers[0]:channel-strip)
            +            active: 1.0, bus: 16.0, gain: c0, gate: 1.0
            +        1005 supriya:meters:2 (session.mixers[0]:output-levels)
            +            in_: 16.0, out: 3.0
            +        1013 supriya:patch-cable:2x2 (session.mixers[0].output:synth)
            +            active: 1.0, gain: 0.0, gate: 1.0, in_: 16.0, out: 0.0
            """,
        ),
        (1, 0, ""),
        (
            1,
            1,
            """
            --- initial
            +++ mutation
            @@ -21,26 +21,26 @@
                         in_: 16.0, out: 3.0
                     1013 supriya:patch-cable:2x2 (session.mixers[0].output:synth)
                         active: 1.0, gain: 0.0, gate: 1.0, in_: 16.0, out: 0.0
            -    NODE TREE 1014 group (session.mixers[1]:group)
            -        1015 group (session.mixers[1]:tracks)
            -            1020 group (session.mixers[1].tracks[0]:group)
            -                1021 group (session.mixers[1].tracks[0]:tracks)
            -                1024 supriya:meters:2 (session.mixers[1].tracks[0]:input-levels)
            -                    in_: 22.0, out: 18.0
            -                1022 group (session.mixers[1].tracks[0]:devices)
            -                1023 supriya:channel-strip:2 (session.mixers[1].tracks[0]:channel-strip)
            -                    active: c16, bus: 22.0, gain: c17, gate: 1.0
            -                1025 supriya:meters:2 (session.mixers[1].tracks[0]:output-levels)
            -                    in_: 22.0, out: 20.0
            -                1026 supriya:patch-cable:2x2 (session.mixers[1].tracks[0].output:synth)
            -                    active: c16, gain: 0.0, gate: 1.0, in_: 22.0, out: 20.0
            -        1018 supriya:meters:2 (session.mixers[1]:input-levels)
            -            in_: 20.0, out: 12.0
            -        1016 group (session.mixers[1]:devices)
            -        1017 supriya:channel-strip:2 (session.mixers[1]:channel-strip)
            -            active: 1.0, bus: 20.0, gain: c11, gate: 1.0
            -        1019 supriya:meters:2 (session.mixers[1]:output-levels)
            -            in_: 20.0, out: 14.0
            -        1027 supriya:patch-cable:2x2 (session.mixers[1].output:synth)
            -            active: 1.0, gain: 0.0, gate: 1.0, in_: 20.0, out: 0.0
            -<session.contexts[1]>+<session.contexts[1]>
            +    NODE TREE 1000 group (session.mixers[1]:group)
            +        1001 group (session.mixers[1]:tracks)
            +            1006 group (session.mixers[1].tracks[0]:group)
            +                1007 group (session.mixers[1].tracks[0]:tracks)
            +                1010 supriya:meters:2 (session.mixers[1].tracks[0]:input-levels)
            +                    in_: 18.0, out: 7.0
            +                1008 group (session.mixers[1].tracks[0]:devices)
            +                1009 supriya:channel-strip:2 (session.mixers[1].tracks[0]:channel-strip)
            +                    active: c5, bus: 18.0, gain: c6, gate: 1.0
            +                1011 supriya:meters:2 (session.mixers[1].tracks[0]:output-levels)
            +                    in_: 18.0, out: 9.0
            +                1012 supriya:patch-cable:2x2 (session.mixers[1].tracks[0].output:synth)
            +                    active: c5, gain: 0.0, gate: 1.0, in_: 18.0, out: 16.0
            +        1004 supriya:meters:2 (session.mixers[1]:input-levels)
            +            in_: 16.0, out: 1.0
            +        1002 group (session.mixers[1]:devices)
            +        1003 supriya:channel-strip:2 (session.mixers[1]:channel-strip)
            +            active: 1.0, bus: 16.0, gain: c0, gate: 1.0
            +        1005 supriya:meters:2 (session.mixers[1]:output-levels)
            +            in_: 16.0, out: 3.0
            +        1013 supriya:patch-cable:2x2 (session.mixers[1].output:synth)
            +            active: 1.0, gain: 0.0, gate: 1.0, in_: 16.0, out: 0.0
            """,
        ),
    ],
)
@pytest.mark.asyncio
async def test_Session_set_mixer_context(
    context_index: int,
    expected_diff: str,
    mixer_index: int,
    online: bool,
    session: Session,
) -> None:
    # Pre-conditions
    if online:
        await session.boot()
    await session.add_mixer()
    await session.add_context()
    assert len(session.contexts) == 2
    assert len(session.mixers) == 2
    if online:
        await debug_tree(session)
    # Operation
    await session.set_mixer_context(
        mixer=session.mixers[mixer_index], context=session.contexts[context_index]
    )
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
            NODE TREE 1014 group (session.mixers[1]:group)
                1015 group (session.mixers[1]:tracks)
                    1020 group (session.mixers[1].tracks[0]:group)
                        1021 group (session.mixers[1].tracks[0]:tracks)
                        1024 supriya:meters:2 (session.mixers[1].tracks[0]:input-levels)
                            in_: 22.0, out: 18.0
                        1022 group (session.mixers[1].tracks[0]:devices)
                        1023 supriya:channel-strip:2 (session.mixers[1].tracks[0]:channel-strip)
                            active: c16, bus: 22.0, gain: c17, gate: 1.0
                        1025 supriya:meters:2 (session.mixers[1].tracks[0]:output-levels)
                            in_: 22.0, out: 20.0
                        1026 supriya:patch-cable:2x2 (session.mixers[1].tracks[0].output:synth)
                            active: c16, gain: 0.0, gate: 1.0, in_: 22.0, out: 20.0
                1018 supriya:meters:2 (session.mixers[1]:input-levels)
                    in_: 20.0, out: 12.0
                1016 group (session.mixers[1]:devices)
                1017 supriya:channel-strip:2 (session.mixers[1]:channel-strip)
                    active: 1.0, bus: 20.0, gain: c11, gate: 1.0
                1019 supriya:meters:2 (session.mixers[1]:output-levels)
                    in_: 20.0, out: 14.0
                1027 supriya:patch-cable:2x2 (session.mixers[1].output:synth)
                    active: 1.0, gain: 0.0, gate: 1.0, in_: 20.0, out: 0.0
        <session.contexts[1]>
        """,
    )
