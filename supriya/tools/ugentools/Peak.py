from supriya.tools.ugentools.UGen import UGen


class Peak(UGen):
    """
    Tracks peak signal amplitude.

    ::

        >>> source = ugentools.In.ar(0)
        >>> trigger = ugentools.Impulse.kr(1)
        >>> peak = ugentools.Peak.ar(
        ...     source=source,
        ...     trigger=trigger,
        ...     )
        >>> peak
        Peak.ar()

    """

    ### CLASS VARIABLES ###

    __documentation_section__ = 'Trigger Utility UGens'

    __slots__ = ()

    _ordered_input_names = (
        'source',
        'trigger',
        )

    _valid_calculation_rates = None

    ### INITIALIZER ###

    def __init__(
        self,
        calculation_rate=None,
        source=None,
        trigger=0,
        ):
        UGen.__init__(
            self,
            calculation_rate=calculation_rate,
            source=source,
            trigger=trigger,
            )

    ### PUBLIC METHODS ###

    @classmethod
    def ar(
        cls,
        source=None,
        trigger=0,
        ):
        """
        Constructs an audio-rate Peak.

        ::

            >>> source = ugentools.In.ar(0)
            >>> trigger = ugentools.Impulse.kr(1)
            >>> peak = ugentools.Peak.ar(
            ...     source=source,
            ...     trigger=trigger,
            ...     )
            >>> peak
            Peak.ar()

        Returns ugen graph.
        """
        from supriya.tools import synthdeftools
        calculation_rate = synthdeftools.CalculationRate.AUDIO
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            source=source,
            trigger=trigger,
            )
        return ugen

    @classmethod
    def kr(
        cls,
        source=None,
        trigger=0,
        ):
        """
        Constructs a control-rate Peak.

        ::

            >>> source = ugentools.In.ar(0)
            >>> trigger = ugentools.Impulse.kr(1)
            >>> peak = ugentools.Peak.kr(
            ...     source=source,
            ...     trigger=trigger,
            ...     )
            >>> peak
            Peak.kr()

        Returns ugen graph.
        """
        from supriya.tools import synthdeftools
        calculation_rate = synthdeftools.CalculationRate.CONTROL
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            source=source,
            trigger=trigger,
            )
        return ugen

    ### PUBLIC PROPERTIES ###

    @property
    def source(self):
        """
        Gets `source` input of Peak.

        ::

            >>> source = ugentools.In.ar(0)
            >>> trigger = ugentools.Impulse.kr(1)
            >>> peak = ugentools.Peak.ar(
            ...     source=source,
            ...     trigger=trigger,
            ...     )
            >>> peak.source
            In.ar()[0]

        Returns ugen input.
        """
        index = self._ordered_input_names.index('source')
        return self._inputs[index]

    @property
    def trigger(self):
        """
        Gets `trigger` input of Peak.

        ::

            >>> source = ugentools.In.ar(0)
            >>> trigger = ugentools.Impulse.kr(1)
            >>> peak = ugentools.Peak.ar(
            ...     source=source,
            ...     trigger=trigger,
            ...     )
            >>> peak.trigger
            Impulse.kr()[0]

        Returns ugen input.
        """
        index = self._ordered_input_names.index('trigger')
        return self._inputs[index]
