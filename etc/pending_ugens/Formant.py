from supriya.tools.ugentools.PureUGen import PureUGen


class Formant(PureUGen):
    """

    ::

        >>> formant = ugentools.Formant.ar(
        ...     bwfrequency=880,
        ...     formfrequency=1760,
        ...     fundfrequency=440,
        ...     )
        >>> formant
        Formant.ar()

    """

    ### CLASS VARIABLES ###

    __documentation_section__ = None

    __slots__ = ()

    _ordered_input_names = (
        'fundfrequency',
        'formfrequency',
        'bwfrequency',
        )

    _valid_calculation_rates = None

    ### INITIALIZER ###

    def __init__(
        self,
        calculation_rate=None,
        bwfrequency=880,
        formfrequency=1760,
        fundfrequency=440,
        ):
        PureUGen.__init__(
            self,
            calculation_rate=calculation_rate,
            bwfrequency=bwfrequency,
            formfrequency=formfrequency,
            fundfrequency=fundfrequency,
            )

    ### PUBLIC METHODS ###

    @classmethod
    def ar(
        cls,
        bwfrequency=880,
        formfrequency=1760,
        fundfrequency=440,
        ):
        """
        Constructs an audio-rate Formant.

        ::

            >>> formant = ugentools.Formant.ar(
            ...     bwfrequency=880,
            ...     formfrequency=1760,
            ...     fundfrequency=440,
            ...     )
            >>> formant
            Formant.ar()

        Returns ugen graph.
        """
        import supriya.synthdefs
        calculation_rate = supriya.synthdefs.CalculationRate.AUDIO
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            bwfrequency=bwfrequency,
            formfrequency=formfrequency,
            fundfrequency=fundfrequency,
            )
        return ugen

    ### PUBLIC PROPERTIES ###

    @property
    def bwfrequency(self):
        """
        Gets `bwfrequency` input of Formant.

        ::

            >>> formant = ugentools.Formant.ar(
            ...     bwfrequency=880,
            ...     formfrequency=1760,
            ...     fundfrequency=440,
            ...     )
            >>> formant.bwfrequency
            880.0

        Returns ugen input.
        """
        index = self._ordered_input_names.index('bwfrequency')
        return self._inputs[index]

    @property
    def formfrequency(self):
        """
        Gets `formfrequency` input of Formant.

        ::

            >>> formant = ugentools.Formant.ar(
            ...     bwfrequency=880,
            ...     formfrequency=1760,
            ...     fundfrequency=440,
            ...     )
            >>> formant.formfrequency
            1760.0

        Returns ugen input.
        """
        index = self._ordered_input_names.index('formfrequency')
        return self._inputs[index]

    @property
    def fundfrequency(self):
        """
        Gets `fundfrequency` input of Formant.

        ::

            >>> formant = ugentools.Formant.ar(
            ...     bwfrequency=880,
            ...     formfrequency=1760,
            ...     fundfrequency=440,
            ...     )
            >>> formant.fundfrequency
            440.0

        Returns ugen input.
        """
        index = self._ordered_input_names.index('fundfrequency')
        return self._inputs[index]
