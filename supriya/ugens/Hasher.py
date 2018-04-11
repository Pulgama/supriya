from supriya.ugens.UGen import UGen


class Hasher(UGen):
    """
    A signal hasher.

    ::

        >>> source = supriya.ugens.SinOsc.ar()
        >>> hasher = supriya.ugens.Hasher.ar(
        ...     source=source,
        ...     )
        >>> hasher
        Hasher.ar()

    """

    ### CLASS VARIABLES ###

    __documentation_section__ = 'Noise UGens'

    __slots__ = ()

    _ordered_input_names = (
        'source',
        )

    _valid_calculation_rates = None

    ### INITIALIZER ###

    def __init__(
        self,
        calculation_rate=None,
        source=0,
        ):
        UGen.__init__(
            self,
            calculation_rate=calculation_rate,
            source=source,
            )

    ### PUBLIC METHODS ###

    @classmethod
    def ar(
        cls,
        source=0,
        ):
        """
        Constructs an audio-rate signal hasher.

        ::

            >>> source = supriya.ugens.SinOsc.ar(frequency=[440, 442])
            >>> hasher = supriya.ugens.Hasher.ar(
            ...     source=source,
            ...     )
            >>> hasher
            UGenArray({2})

        Returns ugen graph.
        """
        import supriya.synthdefs
        calculation_rate = supriya.synthdefs.CalculationRate.AUDIO
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            source=source,
            )
        return ugen

    @classmethod
    def kr(
        cls,
        source=0,
        ):
        """
        Constructs a control-rate signal hasher.

        ::

            >>> source = supriya.ugens.SinOsc.kr(frequency=[4, 2])
            >>> hasher = supriya.ugens.Hasher.kr(
            ...     source=source,
            ...     )
            >>> hasher
            UGenArray({2})

        Returns ugen graph.
        """
        import supriya.synthdefs
        calculation_rate = supriya.synthdefs.CalculationRate.CONTROL
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            source=source,
            )
        return ugen

    ### PUBLIC PROPERTIES ###

    @property
    def source(self):
        """
        Gets `source` input of SignalHasher.

        ::

            >>> source = supriya.ugens.SinOsc.ar()
            >>> hasher = supriya.ugens.Hasher.ar(
            ...     source=source,
            ...     )
            >>> hasher.source
            SinOsc.ar()[0]

        Returns ugen input.
        """
        index = self._ordered_input_names.index('source')
        return self._inputs[index]
