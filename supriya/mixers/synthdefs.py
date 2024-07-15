from ..ugens import (
    DC,
    Amplitude,
    In,
    InFeedback,
    Linen,
    Out,
    Parameter,
    ReplaceOut,
    SynthDef,
    SynthDefBuilder,
)

LAG_TIME = 0.005


def build_channel_strip(channel_count: int = 2) -> SynthDef:
    with SynthDefBuilder(
        active=1,
        bus=0,
        gain=Parameter(value=0, lag=LAG_TIME),
        gate=1,
    ) as builder:
        source = In.ar(
            channel_count=channel_count,
            bus=builder["bus"],
        )
        active_gate = Linen.kr(
            attack_time=LAG_TIME,
            gate=builder["active"],
            release_time=LAG_TIME,
        )
        free_gate = Linen.kr(
            attack_time=LAG_TIME,
            gate=builder["gate"],
            release_time=LAG_TIME,
        )
        source *= builder["gain"].db_to_amplitude()
        source *= active_gate
        source *= free_gate
        ReplaceOut.ar(bus=builder["bus"], source=source)
    return builder.build(f"supriya:channel-strip:{channel_count}")


def build_device_dc_tester(channel_count: int = 2) -> SynthDef:
    with SynthDefBuilder(dc=1, out=0) as builder:
        Out.ar(bus=builder["out"], source=[DC.ar(source=builder["dc"])] * channel_count)
    return builder.build(f"supriya:device-dc-tester:{channel_count}")


def build_meters(channel_count: int = 2) -> SynthDef:
    with SynthDefBuilder(in_=0, out=0) as builder:
        Out.kr(
            bus=builder["out"],
            source=Amplitude.kr(
                source=In.ar(bus=builder["in_"], channel_count=channel_count)
            ),
        )
    return builder.build(f"supriya:meters:{channel_count}")


def build_patch_cable(
    input_channel_count: int = 2, output_channel_count: int = 2, feedback: bool = False
) -> SynthDef:
    # TODO: Implement up/down channel mixing
    with SynthDefBuilder(active=1, in_=0, out=0, gain=0, gate=1) as builder:
        if feedback:
            source = InFeedback.ar(
                channel_count=input_channel_count,
                bus=builder["in_"],
            )
        else:
            source = In.ar(
                channel_count=input_channel_count,
                bus=builder["in_"],
            )
        active_gate = Linen.kr(
            attack_time=LAG_TIME,
            gate=builder["active"],
            release_time=LAG_TIME,
        )
        free_gate = Linen.kr(
            attack_time=LAG_TIME,
            gate=builder["gate"],
            release_time=LAG_TIME,
        )
        source *= builder["gain"].db_to_amplitude()
        source *= free_gate * active_gate
        Out.ar(bus=builder["out"], source=source)

    name = (
        f"supriya:{'fb-' if feedback else ''}"
        f"patch-cable:{input_channel_count}x{output_channel_count}"
    )
    return builder.build(name)


CHANNEL_STRIP_2 = build_channel_strip(2)
DEVICE_DC_TESTER_2 = build_device_dc_tester(2)
FB_PATCH_CABLE_2_2 = build_patch_cable(2, 2, feedback=True)
METERS_2 = build_meters(2)
PATCH_CABLE_2_2 = build_patch_cable(2, 2)
