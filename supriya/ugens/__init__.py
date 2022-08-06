"""
Tools for modeling unit generators (UGens).
"""
from .basic import Mix, MulAdd, Sum3, Sum4
from .beq import (
    BAllPass,
    BBandPass,
    BBandStop,
    BHiCut,
    BHiPass,
    BHiShelf,
    BLowCut,
    BLowPass,
    BLowShelf,
    BPeakEQ,
)
from .bufio import BufRd, BufWr, ClearBuf, LocalBuf, MaxLocalBufs, PlayBuf, RecordBuf
from .chaos import (
    CuspL,
    CuspN,
    FBSineC,
    FBSineL,
    FBSineN,
    GbmanL,
    GbmanN,
    HenonC,
    HenonL,
    HenonN,
    LatoocarfianC,
    LatoocarfianL,
    LatoocarfianN,
    LinCongC,
    LinCongL,
    LinCongN,
    LorenzL,
    QuadC,
    QuadL,
    QuadN,
    StandardL,
    StandardN,
)
from .convolution import Convolution, Convolution2, Convolution2L, Convolution3
from .delay import (
    AllpassC,
    AllpassL,
    AllpassN,
    BufAllpassC,
    BufAllpassL,
    BufAllpassN,
    BufCombC,
    BufCombL,
    BufCombN,
    BufDelayC,
    BufDelayL,
    BufDelayN,
    CombC,
    CombL,
    CombN,
    DelTapRd,
    DelTapWr,
    Delay1,
    Delay2,
    DelayC,
    DelayL,
    DelayN,
)
from .demand import (
    DUGen,
    Dbrown,
    Dbufrd,
    Dbufwr,
    Demand,
    DemandEnvGen,
    Dgeom,
    Dibrown,
    Diwhite,
    Drand,
    Dreset,
    Dseq,
    Dser,
    Dseries,
    Dshuf,
    Dstutter,
    Dswitch,
    Dswitch1,
    Dunique,
    Duty,
    Dwhite,
    Dwrand,
    Dxrand,
)
from .diskio import DiskIn, DiskOut, VDiskIn
from .dynamics import Amplitude, Compander, CompanderD, Limiter, Normalizer
from .envelopes import (
    Done,
    EnvGen,
    Free,
    FreeSelf,
    FreeSelfWhenDone,
    Linen,
    Pause,
    PauseSelf,
    PauseSelfWhenDone,
)
from .ffsinosc import Blip, FSinOsc, Klank, Pulse, Saw
from .filters import (
    APF,
    BPF,
    BPZ2,
    BRF,
    BRZ2,
    FOS,
    HPF,
    HPZ1,
    HPZ2,
    LPF,
    LPZ1,
    LPZ2,
    RHPF,
    RLPF,
    SOS,
    Changed,
    Decay,
    Decay2,
    DetectSilence,
    Filter,
    Formlet,
    Integrator,
    Lag,
    Lag2,
    Lag2UD,
    Lag3,
    Lag3UD,
    LagUD,
    LeakDC,
    Median,
    MidEQ,
    MoogFF,
    OnePole,
    OneZero,
    Ramp,
    Ringz,
    Slew,
    Slope,
    TwoPole,
    TwoZero,
)
from .gendyn import Gendy1, Gendy2, Gendy3
from .granular import GrainBuf, GrainIn, PitchShift, Warp1
from .hilbert import FreqShift, Hilbert, HilbertFIR
from .info import (
    BlockSize,
    BufChannels,
    BufDur,
    BufFrames,
    BufRateScale,
    BufSampleRate,
    BufSamples,
    ControlDur,
    ControlRate,
    NodeID,
    NumAudioBuses,
    NumBuffers,
    NumControlBuses,
    NumInputBuses,
    NumOutputBuses,
    NumRunningSynths,
    RadiansPerSample,
    SampleDur,
    SampleRate,
    SubsampleOffset,
)
from .inout import In, InFeedback, LocalIn, LocalOut, OffsetOut, Out, ReplaceOut, XOut
from .lines import A2K, DC, K2A, AmpComp, AmpCompA, LinExp, LinLin, Line, Silence, XLine
from .mac import KeyState, MouseButton, MouseX, MouseY
from .ml import (
    MFCC,
    BeatTrack,
    BeatTrack2,
    KeyTrack,
    Loudness,
    Onsets,
    Pitch,
    SpecCentroid,
    SpecFlatness,
    SpecPcile,
)
from .noise import (
    BrownNoise,
    ClipNoise,
    CoinGate,
    Crackle,
    Dust,
    Dust2,
    ExpRand,
    GrayNoise,
    Hasher,
    IRand,
    LFClipNoise,
    LFDClipNoise,
    LFDNoise0,
    LFDNoise1,
    LFDNoise3,
    LFNoise0,
    LFNoise1,
    LFNoise2,
    LinRand,
    Logistic,
    MantissaMask,
    NRand,
    PinkNoise,
    Rand,
    RandID,
    RandSeed,
    TExpRand,
    TIRand,
    TRand,
    TWindex,
    WhiteNoise,
)
from .osc import (
    COsc,
    DegreeToKey,
    Impulse,
    Index,
    LFCub,
    LFGauss,
    LFPar,
    LFPulse,
    LFSaw,
    LFTri,
    Select,
    SinOsc,
    SyncSaw,
    VOsc,
    VOsc3,
    VarSaw,
    Vibrato,
    WrapIndex,
)
from .panning import (
    Balance2,
    BiPanB2,
    DecodeB2,
    Pan2,
    Pan4,
    PanAz,
    PanB,
    PanB2,
    Rotate2,
    Splay,
    XFade2,
)
from .physical import Ball, Pluck, Spring, TBall
from .pv import (
    FFT,
    IFFT,
    PV_Add,
    PV_BinScramble,
    PV_BinShift,
    PV_BinWipe,
    PV_BrickWall,
    PV_ChainUGen,
    PV_ConformalMap,
    PV_Conj,
    PV_Copy,
    PV_CopyPhase,
    PV_Diffuser,
    PV_Div,
    PV_HainsworthFoote,
    PV_JensenAndersen,
    PV_LocalMax,
    PV_MagAbove,
    PV_MagBelow,
    PV_MagClip,
    PV_MagDiv,
    PV_MagFreeze,
    PV_MagMul,
    PV_MagNoise,
    PV_MagShift,
    PV_MagSmear,
    PV_MagSquared,
    PV_Max,
    PV_Min,
    PV_Mul,
    PV_PhaseShift,
    PV_PhaseShift90,
    PV_PhaseShift270,
    PV_RandComb,
    PV_RandWipe,
    PV_RectComb,
    PV_RectComb2,
    RunningSum,
)
from .reverb import FreeVerb
from .safety import CheckBadValues, Sanitize
from .triggers import (
    Clip,
    Fold,
    Gate,
    InRange,
    Latch,
    LeastChange,
    MostChange,
    Peak,
    PeakFollower,
    Phasor,
    Poll,
    RunningMax,
    RunningMin,
    Schmidt,
    SendPeakRMS,
    SendReply,
    SendTrig,
    Sweep,
    TDelay,
    ToggleFF,
    Trig,
    Trig1,
    Wrap,
    ZeroCrossing,
)

__all__ = [
    "A2K",
    "APF",
    "AllpassC",
    "AllpassL",
    "AllpassN",
    "AmpComp",
    "AmpCompA",
    "Amplitude",
    "BAllPass",
    "BBandPass",
    "BBandStop",
    "BHiCut",
    "BHiPass",
    "BHiShelf",
    "BLowCut",
    "BLowPass",
    "BLowShelf",
    "BPF",
    "BPZ2",
    "BPeakEQ",
    "BRF",
    "BRZ2",
    "Balance2",
    "Ball",
    "BeatTrack",
    "BeatTrack2",
    "BiPanB2",
    "Blip",
    "BlockSize",
    "BrownNoise",
    "BufAllpassC",
    "BufAllpassL",
    "BufAllpassN",
    "BufChannels",
    "BufCombC",
    "BufCombL",
    "BufCombN",
    "BufDelayC",
    "BufDelayL",
    "BufDelayN",
    "BufDur",
    "BufFrames",
    "BufRateScale",
    "BufRd",
    "BufSampleRate",
    "BufSamples",
    "BufWr",
    "COsc",
    "Changed",
    "CheckBadValues",
    "ClearBuf",
    "Clip",
    "ClipNoise",
    "CoinGate",
    "CombC",
    "CombL",
    "CombN",
    "Compander",
    "CompanderD",
    "ControlDur",
    "ControlRate",
    "Convolution",
    "Convolution2",
    "Convolution2L",
    "Convolution3",
    "Crackle",
    "CuspL",
    "CuspN",
    "DC",
    "DUGen",
    "Dbrown",
    "Dbufrd",
    "Dbufwr",
    "Decay",
    "Decay2",
    "DecodeB2",
    "DegreeToKey",
    "DelTapRd",
    "DelTapWr",
    "Delay1",
    "Delay2",
    "DelayC",
    "DelayL",
    "DelayN",
    "Demand",
    "DemandEnvGen",
    "DetectSilence",
    "Dgeom",
    "Dibrown",
    "DiskIn",
    "DiskOut",
    "Diwhite",
    "Done",
    "Drand",
    "Dreset",
    "Dseq",
    "Dser",
    "Dseries",
    "Dshuf",
    "Dstutter",
    "Dswitch",
    "Dswitch1",
    "Dunique",
    "Dust",
    "Dust2",
    "Duty",
    "Dwhite",
    "Dwrand",
    "Dxrand",
    "EnvGen",
    "ExpRand",
    "FBSineC",
    "FBSineL",
    "FBSineN",
    "FFT",
    "FOS",
    "FSinOsc",
    "Filter",
    "Fold",
    "Formlet",
    "Free",
    "FreeSelf",
    "FreeSelfWhenDone",
    "FreeVerb",
    "FreqShift",
    "Gate",
    "GbmanL",
    "GbmanN",
    "Gendy1",
    "Gendy2",
    "Gendy3",
    "GrainBuf",
    "GrainIn",
    "GrayNoise",
    "HPF",
    "HPZ1",
    "HPZ2",
    "Hasher",
    "HenonC",
    "HenonL",
    "HenonN",
    "Hilbert",
    "HilbertFIR",
    "IFFT",
    "IRand",
    "Impulse",
    "In",
    "InFeedback",
    "InRange",
    "Index",
    "Integrator",
    "K2A",
    "KeyState",
    "KeyTrack",
    "Klank",
    "LFClipNoise",
    "LFCub",
    "LFDClipNoise",
    "LFDNoise0",
    "LFDNoise1",
    "LFDNoise3",
    "LFGauss",
    "LFNoise0",
    "LFNoise1",
    "LFNoise2",
    "LFPar",
    "LFPulse",
    "LFSaw",
    "LFTri",
    "LPF",
    "LPZ1",
    "LPZ2",
    "Lag",
    "Lag2",
    "Lag2UD",
    "Lag3",
    "Lag3UD",
    "LagUD",
    "Latch",
    "LatoocarfianC",
    "LatoocarfianL",
    "LatoocarfianN",
    "LeakDC",
    "LeastChange",
    "Limiter",
    "LinCongC",
    "LinCongL",
    "LinCongN",
    "LinExp",
    "LinLin",
    "LinRand",
    "Line",
    "Linen",
    "LocalBuf",
    "LocalIn",
    "LocalOut",
    "Logistic",
    "LorenzL",
    "Loudness",
    "MFCC",
    "MantissaMask",
    "MaxLocalBufs",
    "Median",
    "MidEQ",
    "Mix",
    "MoogFF",
    "MostChange",
    "MouseButton",
    "MouseX",
    "MouseY",
    "MulAdd",
    "NRand",
    "NodeID",
    "Normalizer",
    "NumAudioBuses",
    "NumBuffers",
    "NumControlBuses",
    "NumInputBuses",
    "NumOutputBuses",
    "NumRunningSynths",
    "OffsetOut",
    "OnePole",
    "OneZero",
    "Onsets",
    "Out",
    "PV_Add",
    "PV_BinScramble",
    "PV_BinShift",
    "PV_BinWipe",
    "PV_BrickWall",
    "PV_ChainUGen",
    "PV_ConformalMap",
    "PV_Conj",
    "PV_Copy",
    "PV_CopyPhase",
    "PV_Diffuser",
    "PV_Div",
    "PV_HainsworthFoote",
    "PV_JensenAndersen",
    "PV_LocalMax",
    "PV_MagAbove",
    "PV_MagBelow",
    "PV_MagClip",
    "PV_MagDiv",
    "PV_MagFreeze",
    "PV_MagMul",
    "PV_MagNoise",
    "PV_MagShift",
    "PV_MagSmear",
    "PV_MagSquared",
    "PV_Max",
    "PV_Min",
    "PV_Mul",
    "PV_PhaseShift",
    "PV_PhaseShift270",
    "PV_PhaseShift90",
    "PV_RandComb",
    "PV_RandWipe",
    "PV_RectComb",
    "PV_RectComb2",
    "Pan2",
    "Pan4",
    "PanAz",
    "PanB",
    "PanB2",
    "Pause",
    "PauseSelf",
    "PauseSelfWhenDone",
    "Peak",
    "PeakFollower",
    "Phasor",
    "PinkNoise",
    "Pitch",
    "PitchShift",
    "PlayBuf",
    "Pluck",
    "Poll",
    "Pulse",
    "QuadC",
    "QuadL",
    "QuadN",
    "RHPF",
    "RLPF",
    "RadiansPerSample",
    "Ramp",
    "Rand",
    "RandID",
    "RandSeed",
    "RecordBuf",
    "ReplaceOut",
    "Ringz",
    "Rotate2",
    "RunningMax",
    "RunningMin",
    "RunningSum",
    "SOS",
    "SampleDur",
    "SampleRate",
    "Sanitize",
    "Saw",
    "Schmidt",
    "Select",
    "SendPeakRMS",
    "SendTrig",
    "Silence",
    "SinOsc",
    "Slew",
    "Slope",
    "SpecCentroid",
    "SpecFlatness",
    "SpecPcile",
    "Splay",
    "Spring",
    "StandardL",
    "StandardN",
    "SubsampleOffset",
    "Sum3",
    "Sum4",
    "Sweep",
    "SyncSaw",
    "TBall",
    "TDelay",
    "TExpRand",
    "TIRand",
    "TRand",
    "TWindex",
    "ToggleFF",
    "Trig",
    "Trig1",
    "TwoPole",
    "TwoZero",
    "VDiskIn",
    "VOsc",
    "VOsc3",
    "VarSaw",
    "Vibrato",
    "Warp1",
    "WhiteNoise",
    "Wrap",
    "WrapIndex",
    "XFade2",
    "XLine",
    "XOut",
    "ZeroCrossing",
]
