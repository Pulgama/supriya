import time

from uqbar.strings import normalize

from supriya.xdaw import Allocatable


def test_channel_count(channel_count_application):
    items = [channel_count_application]
    items.extend(x for x in channel_count_application.depth_first() if x.name)
    assert {
        x.name: (x.channel_count, x.effective_channel_count) for x in items[1:]
    } == {
        "Chain": (None, 2),
        "Context": (None, 2),
        "Device": (None, 2),
        "One": (None, 2),
        "Rack": (None, 2),
        "Three": (None, 2),
        "Two": (None, 2),
    }
    channel_count_application["Rack"].set_channel_count(4)
    assert {
        x.name: (x.channel_count, x.effective_channel_count) for x in items[1:]
    } == {
        "Chain": (None, 4),
        "Context": (None, 2),
        "Device": (None, 4),
        "One": (None, 2),
        "Rack": (4, 4),
        "Three": (None, 2),
        "Two": (None, 2),
    }


def test_audio_buses(channel_count_application):
    for node in channel_count_application.depth_first(prototype=Allocatable):
        for audio_bus_proxy in node.audio_bus_proxies.values():
            assert audio_bus_proxy.channel_count == node.effective_channel_count
    channel_count_application["Rack"].set_channel_count(4)
    for node in channel_count_application.depth_first(prototype=Allocatable):
        for audio_bus_proxy in node.audio_bus_proxies.values():
            assert audio_bus_proxy.channel_count == node.effective_channel_count


def test_levels(channel_count_application):
    channel_count_application.boot()
    master_levels = channel_count_application.primary_context.master_track.rms_levels
    track_levels = channel_count_application.primary_context["One"].rms_levels
    time.sleep(0.2)
    assert [round(x, 2) for x in track_levels["postfader"]] == [1.0, 0.0]
    assert [round(x, 2) for x in master_levels["input"]] == [1.0, 0.0]
    channel_count_application["Rack"].set_channel_count(4)
    time.sleep(0.2)
    assert [round(x, 2) for x in track_levels["postfader"]] == [0.41, 0.0]
    assert [round(x, 2) for x in master_levels["input"]] == [0.41, 0.0]


def test_query(channel_count_application):
    context = channel_count_application["Context"]
    channel_count_application.boot()
    with context.provider.server.osc_io.capture() as transcript:
        context["Rack"].set_channel_count(4)
    time.sleep(0.1)
    assert len(transcript.sent_messages) == 1
    after = str(context.query())
    assert after == normalize(
        """
        NODE TREE 1000 group (Context)
            1001 group (Tracks)
                1002 group (One)
                    1003 group (Parameters)
                    1010 group (Receives)
                    1004 mixer/track-input/2 (Input)
                        in_: 16.0, out: 18.0, active: 1.0, gain: 0.0, gate: 1.0, lag: 0.01
                    1009 group (SubTracks)
                    1005 mixer/levels/2 (InputLevel)
                        out: 18.0, gate: 1.0, lag: 0.01
                    1011 group (Devices)
                        1012 group (Rack)
                            1087 mix/patch[gain]/2x4 (RackIn)
                                active: 1.0, gain: 0.0, gate: 1.0, in_: 18.0, lag: 0.01, out: 44.0
                            1015 group (ChainContainer)
                                1016 group (Chain)
                                    1017 group (Parameters)
                                    1023 group (Receives)
                                    1089 mixer/track-input/4 (Input)
                                        in_: 20.0, out: 48.0, active: 1.0, gain: 0.0, gate: 1.0, lag: 0.01
                                    1090 mixer/levels/4 (InputLevel)
                                        out: 48.0, gate: 1.0, lag: 0.01
                                    1024 group (Devices)
                                        1025 group (Device)
                                            1095 mix/patch[replace]/4x4 (DeviceIn)
                                                active: 1.0, gate: 1.0, in_: 48.0, lag: 0.01, out: 24.0
                                            1026 group (Parameters)
                                            1027 group (Body)
                                                1094 15a77f27cd96f4488c4a9b094478d045
                                                    out: 24.0, index: 0.0
                                            1096 mix/patch[hard,mix]/4x4 (DeviceOut)
                                                active: 1.0, gate: 1.0, hard_gate: 1.0, in_: 24.0, lag: 0.01, mix: 1.0, out: 48.0
                                    1091 mixer/levels/4 (PrefaderLevels)
                                        out: 48.0, gate: 1.0, lag: 0.01
                                    1031 group (PreFaderSends)
                                    1092 mixer/track-output/4 (Output)
                                        out: 48.0, active: 1.0, gain: 0.0, gate: 1.0, hard_gate: 1.0, lag: 0.01
                                    1032 group (PostFaderSends)
                                        1097 mix/patch[gain]/4x4 (Send)
                                            active: 1.0, gain: 0.0, gate: 1.0, in_: 48.0, lag: 0.01, out: 44.0
                                    1093 mixer/levels/4 (PostfaderLevels)
                                        out: 48.0, gate: 1.0, lag: 0.01
                            1088 mix/patch[hard,mix]/4x2 (RackOut)
                                active: 1.0, gate: 1.0, hard_gate: 1.0, in_: 44.0, lag: 0.01, mix: 1.0, out: 18.0
                    1006 mixer/levels/2 (PrefaderLevels)
                        out: 18.0, gate: 1.0, lag: 0.01
                    1034 group (PreFaderSends)
                    1007 mixer/track-output/2 (Output)
                        out: 18.0, active: 1.0, gain: 0.0, gate: 1.0, hard_gate: 1.0, lag: 0.01
                    1035 group (PostFaderSends)
                        1073 mix/patch[gain]/2x2 (Send)
                            active: 1.0, gain: 0.0, gate: 1.0, in_: 18.0, lag: 0.01, out: 38.0
                    1008 mixer/levels/2 (PostfaderLevels)
                        out: 18.0, gate: 1.0, lag: 0.01
                1036 group (Two)
                    1037 group (Parameters)
                    1057 group (Receives)
                    1038 mixer/track-input/2 (Input)
                        in_: 28.0, out: 30.0, active: 1.0, gain: 0.0, gate: 1.0, lag: 0.01
                    1043 group (SubTracks)
                        1044 group (Three)
                            1045 group (Parameters)
                            1052 group (Receives)
                            1046 mixer/track-input/2 (Input)
                                in_: 32.0, out: 34.0, active: 1.0, gain: 0.0, gate: 1.0, lag: 0.01
                            1051 group (SubTracks)
                            1047 mixer/levels/2 (InputLevel)
                                out: 34.0, gate: 1.0, lag: 0.01
                            1053 group (Devices)
                            1048 mixer/levels/2 (PrefaderLevels)
                                out: 34.0, gate: 1.0, lag: 0.01
                            1054 group (PreFaderSends)
                            1049 mixer/track-output/2 (Output)
                                out: 34.0, active: 1.0, gain: 0.0, gate: 1.0, hard_gate: 1.0, lag: 0.01
                            1055 group (PostFaderSends)
                                1056 mix/patch[gain]/2x2 (Send)
                                    active: 1.0, gain: 0.0, gate: 1.0, in_: 34.0, lag: 0.01, out: 30.0
                            1050 mixer/levels/2 (PostfaderLevels)
                                out: 34.0, gate: 1.0, lag: 0.01
                    1039 mixer/levels/2 (InputLevel)
                        out: 30.0, gate: 1.0, lag: 0.01
                    1058 group (Devices)
                    1040 mixer/levels/2 (PrefaderLevels)
                        out: 30.0, gate: 1.0, lag: 0.01
                    1059 group (PreFaderSends)
                    1041 mixer/track-output/2 (Output)
                        out: 30.0, active: 1.0, gain: 0.0, gate: 1.0, hard_gate: 1.0, lag: 0.01
                    1060 group (PostFaderSends)
                        1074 mix/patch[gain]/2x2 (Send)
                            active: 1.0, gain: 0.0, gate: 1.0, in_: 30.0, lag: 0.01, out: 38.0
                    1042 mixer/levels/2 (PostfaderLevels)
                        out: 30.0, gate: 1.0, lag: 0.01
            1061 group (MasterTrack)
                1062 group (Parameters)
                1068 group (Receives)
                1063 mixer/track-input/2 (Input)
                    in_: 36.0, out: 38.0, active: 1.0, gain: 0.0, gate: 1.0, lag: 0.01
                1064 mixer/levels/2 (InputLevel)
                    out: 38.0, gate: 1.0, lag: 0.01
                1069 group (Devices)
                1065 mixer/levels/2 (PrefaderLevels)
                    out: 38.0, gate: 1.0, lag: 0.01
                1070 group (PreFaderSends)
                1066 mixer/track-output/2 (Output)
                    out: 38.0, active: 1.0, gain: 0.0, gate: 1.0, hard_gate: 1.0, lag: 0.01
                1071 group (PostFaderSends)
                    1072 mix/patch/2x2 (DirectOut)
                        active: 1.0, gate: 1.0, in_: 38.0, lag: 0.01, out: 0.0
                1067 mixer/levels/2 (PostfaderLevels)
                    out: 38.0, gate: 1.0, lag: 0.01
            1075 group (CueTrack)
                1076 group (Parameters)
                1082 group (Receives)
                1077 mixer/track-input/2 (Input)
                    in_: 40.0, out: 42.0, active: 1.0, gain: 0.0, gate: 1.0, lag: 0.01
                1078 mixer/levels/2 (InputLevel)
                    out: 42.0, gate: 1.0, lag: 0.01
                1083 group (Devices)
                1079 mixer/levels/2 (PrefaderLevels)
                    out: 42.0, gate: 1.0, lag: 0.01
                1084 group (PreFaderSends)
                1080 mixer/track-output/2 (Output)
                    out: 42.0, active: 1.0, gain: 0.0, gate: 1.0, hard_gate: 1.0, lag: 0.01
                1085 group (PostFaderSends)
                    1086 mix/patch/2x2 (DirectOut)
                        active: 1.0, gate: 1.0, in_: 42.0, lag: 0.01, out: 2.0
                1081 mixer/levels/2 (PostfaderLevels)
                    out: 42.0, gate: 1.0, lag: 0.01
        """
    )