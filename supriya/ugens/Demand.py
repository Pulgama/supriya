import collections
from supriya.ugens.MultiOutUGen import MultiOutUGen


class Demand(MultiOutUGen):
    """
    Demands results from demand-rate UGens.

    ::

        >>> source = [
        ...     supriya.ugens.Dseries(),
        ...     supriya.ugens.Dwhite(),
        ...     ]
        >>> trigger = supriya.ugens.Impulse.kr(1)
        >>> demand = supriya.ugens.Demand.ar(
        ...     reset=0,
        ...     source=source,
        ...     trigger=trigger,
        ...     )
        >>> demand
        UGenArray({2})

    """

    ### CLASS VARIABLES ###

    __documentation_section__ = 'Demand UGens'

    __slots__ = ()

    _ordered_input_names = (
        'trigger',
        'reset',
        'source',
        )

    _unexpanded_input_names = (
        'source',
        )

    _valid_calculation_rates = None

    ### INITIALIZER ###

    def __init__(
        self,
        calculation_rate=None,
        reset=None,
        source=None,
        trigger=None,
        ):
        if not isinstance(source, collections.Sequence):
            source = (source,)
        channel_count = len(source)
        MultiOutUGen.__init__(
            self,
            calculation_rate=calculation_rate,
            channel_count=channel_count,
            reset=reset,
            source=source,
            trigger=trigger,
            )

    ### PUBLIC METHODS ###

    @classmethod
    def ar(
        cls,
        reset=None,
        source=None,
        trigger=None,
        ):
        """
        Constructs an audio-rate Demand.

        ::

            >>> source = [
            ...     supriya.ugens.Dseries(),
            ...     supriya.ugens.Dwhite(),
            ...     ]
            >>> trigger = supriya.ugens.Impulse.kr(1)
            >>> demand = supriya.ugens.Demand.ar(
            ...     reset=0,
            ...     source=source,
            ...     trigger=trigger,
            ...     )
            >>> demand
            UGenArray({2})

        Returns ugen graph.
        """
        import supriya.synthdefs
        calculation_rate = supriya.synthdefs.CalculationRate.AUDIO
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            source=source,
            reset=reset,
            trigger=trigger,
            )
        return ugen

    @classmethod
    def kr(
        cls,
        source=None,
        reset=None,
        trigger=None,
        ):
        """
        Constructs a control-rate Demand.

        ::

            >>> source = [
            ...     supriya.ugens.Dseries(),
            ...     supriya.ugens.Dwhite(),
            ...     ]
            >>> trigger = supriya.ugens.Impulse.kr(1)
            >>> demand = supriya.ugens.Demand.kr(
            ...     reset=0,
            ...     source=source,
            ...     trigger=trigger,
            ...     )
            >>> demand
            UGenArray({2})

        Returns ugen graph.
        """
        import supriya.synthdefs
        calculation_rate = supriya.synthdefs.CalculationRate.CONTROL
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            source=source,
            reset=reset,
            trigger=trigger,
            )
        return ugen

    # def newFromDesc(): ...

    ### PUBLIC PROPERTIES ###

    @property
    def has_done_flag(self):
        """
        Is true if UGen has a done flag.

        Returns boolean.
        """
        return True

    @property
    def reset(self):
        """
        Gets `reset` input of Demand.

        ::

            >>> source = [
            ...     supriya.ugens.Dseries(),
            ...     supriya.ugens.Dwhite(),
            ...     ]
            >>> trigger = supriya.ugens.Impulse.kr(1)
            >>> demand = supriya.ugens.Demand.ar(
            ...     reset=0,
            ...     source=source,
            ...     trigger=trigger,
            ...     )
            >>> demand[0].source.reset
            0.0

        Returns ugen input.
        """
        index = self._ordered_input_names.index('reset')
        return self._inputs[index]

    @property
    def source(self):
        """
        Gets `source` input of Demand.

        ::

            >>> source = [
            ...     supriya.ugens.Dseries(),
            ...     supriya.ugens.Dwhite(),
            ...     ]
            >>> trigger = supriya.ugens.Impulse.kr(1)
            >>> demand = supriya.ugens.Demand.ar(
            ...     reset=0,
            ...     source=source,
            ...     trigger=trigger,
            ...     )
            >>> demand[0].source.source
            (Dseries()[0], Dwhite()[0])

        Returns ugen input.
        """
        index = self._ordered_input_names.index('source')
        return tuple(self._inputs[index:])

    @property
    def trigger(self):
        """
        Gets `trigger` input of Demand.

        ::

            >>> source = [
            ...     supriya.ugens.Dseries(),
            ...     supriya.ugens.Dwhite(),
            ...     ]
            >>> trigger = supriya.ugens.Impulse.kr(1)
            >>> demand = supriya.ugens.Demand.ar(
            ...     reset=0,
            ...     source=source,
            ...     trigger=trigger,
            ...     )
            >>> demand[0].source.trigger
            Impulse.kr()[0]

        Returns ugen input.
        """
        index = self._ordered_input_names.index('trigger')
        return self._inputs[index]
