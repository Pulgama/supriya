from supriya.ugens.UGen import UGen


class TWindex(UGen):
    """
    A triggered windex.

    ::

        >>> trigger = supriya.ugens.Impulse.ar()
        >>> t_windex = supriya.ugens.TWindex.ar(
        ...     trigger=trigger,
        ...     normalize=0,
        ...     array=[1, 2, 3],
        ...     )
        >>> t_windex
        TWindex.ar()

    """

    ### CLASS VARIABLES ###

    __documentation_section__ = 'Noise UGens'

    __slots__ = ()

    _ordered_input_names = (
        'trigger',
        'normalize',
        'array',
        )

    _unexpanded_input_names = (
        'array',
        )

    _valid_calculation_rates = None

    ### INITIALIZER ###

    def __init__(
        self,
        calculation_rate=None,
        array=None,
        normalize=0,
        trigger=None,
        ):
        UGen.__init__(
            self,
            calculation_rate=calculation_rate,
            array=array,
            normalize=normalize,
            trigger=trigger,
            )

    ### PUBLIC METHODS ###

    @classmethod
    def ar(
        cls,
        array=None,
        normalize=0,
        trigger=None,
        ):
        """
        Constructs an audio-rate triggered windex.

        ::

            >>> trigger = supriya.ugens.Impulse.ar(frequency=[1, 1.4])
            >>> t_windex = supriya.ugens.TWindex.ar(
            ...     trigger=trigger,
            ...     normalize=0,
            ...     array=[1, 2, 3],
            ...     )
            >>> t_windex
            UGenArray({2})

        Returns ugen graph.
        """
        import supriya.synthdefs
        calculation_rate = supriya.CalculationRate.AUDIO
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            array=array,
            normalize=normalize,
            trigger=trigger,
            )
        return ugen

    @classmethod
    def kr(
        cls,
        array=None,
        normalize=0,
        trigger=None,
        ):
        """
        Constructs a control-rate triggered windex.

        ::

            >>> trigger = supriya.ugens.Impulse.kr(frequency=[1, 1.4])
            >>> t_windex = supriya.ugens.TWindex.kr(
            ...     trigger=trigger,
            ...     normalize=0,
            ...     array=[1, 2, 3],
            ...     )
            >>> t_windex
            UGenArray({2})

        Returns ugen graph.
        """
        import supriya.synthdefs
        calculation_rate = supriya.CalculationRate.CONTROL
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            array=array,
            normalize=normalize,
            trigger=trigger,
            )
        return ugen

    ### PUBLIC PROPERTIES ###

    @property
    def array(self):
        """
        Gets `array` input of TWindex.

        ::

            >>> trigger = supriya.ugens.Impulse.ar()
            >>> t_windex = supriya.ugens.TWindex.ar(
            ...     trigger=trigger,
            ...     normalize=0,
            ...     array=[1, 2, 3],
            ...     )
            >>> t_windex.array
            (1.0, 2.0, 3.0)

        Returns ugen input.
        """
        index = self._ordered_input_names.index('array')
        return tuple(self._inputs[index:])

    @property
    def normalize(self):
        """
        Gets `normalize` input of TWindex.

        ::

            >>> trigger = supriya.ugens.Impulse.ar()
            >>> t_windex = supriya.ugens.TWindex.ar(
            ...     trigger=trigger,
            ...     normalize=0,
            ...     array=[1, 2, 3],
            ...     )
            >>> t_windex.normalize
            False

        Returns ugen input.
        """
        index = self._ordered_input_names.index('normalize')
        return bool(self._inputs[index])

    @property
    def trigger(self):
        """
        Gets `trigger` input of TWindex.

        ::

            >>> trigger = supriya.ugens.Impulse.ar()
            >>> t_windex = supriya.ugens.TWindex.ar(
            ...     trigger=trigger,
            ...     normalize=0,
            ...     array=[1, 2, 3],
            ...     )
            >>> t_windex.trigger
            Impulse.ar()[0]

        Returns ugen input.
        """
        index = self._ordered_input_names.index('trigger')
        return self._inputs[index]
