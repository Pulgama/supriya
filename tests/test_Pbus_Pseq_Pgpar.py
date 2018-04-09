import uqbar.strings
from patterntools_testbase import TestCase
from supriya.tools import patterntools


class TestCase(TestCase):

    pattern = patterntools.Pbus(
        pattern=patterntools.Pseq([
            patterntools.Pgpar([
                patterntools.Pbind(
                    amplitude=1.0,
                    duration=patterntools.Pseq([1.0], 1),
                    frequency=patterntools.Pseq([440], 1),
                    ),
                patterntools.Pbind(
                    amplitude=0.75,
                    duration=patterntools.Pseq([1.0], 1),
                    frequency=patterntools.Pseq([880], 1),
                    ),
                ]),
            patterntools.Pgpar([
                patterntools.Pbind(
                    amplitude=0.5,
                    duration=patterntools.Pseq([2.0], 1),
                    frequency=patterntools.Pseq([330], 1),
                    ),
                patterntools.Pbind(
                    amplitude=0.25,
                    duration=patterntools.Pseq([2.0], 1),
                    frequency=patterntools.Pseq([660], 1),
                    ),
                ]),
            ]),
        release_time=0.25,
        )

    def test___iter__(self):
        events = list(self.pattern)
        assert self.get_objects_as_string(
            events,
            replace_uuids=True,
        ) == uqbar.strings.normalize('''
            CompositeEvent(
                events=(
                    BusEvent(
                        calculation_rate=CalculationRate.AUDIO,
                        channel_count=2,
                        uuid=UUID('A'),
                        ),
                    GroupEvent(
                        uuid=UUID('B'),
                        ),
                    SynthEvent(
                        add_action=AddAction.ADD_AFTER,
                        amplitude=1.0,
                        fade_time=0.25,
                        in_=UUID('A'),
                        synthdef=<SynthDef: system_link_audio_2>,
                        target_node=UUID('B'),
                        uuid=UUID('C'),
                        ),
                    ),
                )
            CompositeEvent(
                events=(
                    GroupEvent(
                        add_action=AddAction.ADD_TO_TAIL,
                        target_node=UUID('B'),
                        uuid=UUID('D'),
                        ),
                    GroupEvent(
                        add_action=AddAction.ADD_TO_TAIL,
                        target_node=UUID('B'),
                        uuid=UUID('E'),
                        ),
                    ),
                )
            NoteEvent(
                amplitude=1.0,
                delta=0.0,
                duration=1.0,
                frequency=440,
                out=UUID('A'),
                target_node=UUID('D'),
                uuid=UUID('F'),
                )
            NoteEvent(
                amplitude=0.75,
                delta=1.0,
                duration=1.0,
                frequency=880,
                out=UUID('A'),
                target_node=UUID('E'),
                uuid=UUID('G'),
                )
            CompositeEvent(
                events=(
                    NullEvent(
                        delta=0.25,
                        ),
                    GroupEvent(
                        is_stop=True,
                        uuid=UUID('D'),
                        ),
                    GroupEvent(
                        is_stop=True,
                        uuid=UUID('E'),
                        ),
                    ),
                is_stop=True,
                )
            CompositeEvent(
                events=(
                    GroupEvent(
                        add_action=AddAction.ADD_TO_TAIL,
                        target_node=UUID('B'),
                        uuid=UUID('H'),
                        ),
                    GroupEvent(
                        add_action=AddAction.ADD_TO_TAIL,
                        target_node=UUID('B'),
                        uuid=UUID('I'),
                        ),
                    ),
                )
            NoteEvent(
                amplitude=0.5,
                delta=0.0,
                duration=2.0,
                frequency=330,
                out=UUID('A'),
                target_node=UUID('H'),
                uuid=UUID('J'),
                )
            NoteEvent(
                amplitude=0.25,
                delta=2.0,
                duration=2.0,
                frequency=660,
                out=UUID('A'),
                target_node=UUID('I'),
                uuid=UUID('K'),
                )
            CompositeEvent(
                events=(
                    NullEvent(
                        delta=0.25,
                        ),
                    GroupEvent(
                        is_stop=True,
                        uuid=UUID('H'),
                        ),
                    GroupEvent(
                        is_stop=True,
                        uuid=UUID('I'),
                        ),
                    ),
                is_stop=True,
                )
            CompositeEvent(
                events=(
                    SynthEvent(
                        is_stop=True,
                        uuid=UUID('C'),
                        ),
                    NullEvent(
                        delta=0.25,
                        ),
                    GroupEvent(
                        is_stop=True,
                        uuid=UUID('B'),
                        ),
                    BusEvent(
                        calculation_rate=None,
                        channel_count=None,
                        is_stop=True,
                        uuid=UUID('A'),
                        ),
                    ),
                is_stop=True,
                )
            ''')