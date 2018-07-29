from supriya.ugens.UGen import UGen


class QuadL(UGen):
    """
    A linear-interpolating general quadratic map chaotic generator.

    ::

        >>> quad_l = supriya.ugens.QuadL.ar(
        ...     a=1,
        ...     b=-1,
        ...     c=-0.75,
        ...     frequency=22050,
        ...     xi=0,
        ...     )
        >>> quad_l
        QuadL.ar()

    """

    ### CLASS VARIABLES ###

    __documentation_section__ = 'Chaos UGens'

    __slots__ = ()

    _ordered_input_names = (
        'frequency',
        'a',
        'b',
        'c',
        'xi',
        )

    _valid_calculation_rates = None

    ### INITIALIZER ###

    def __init__(
        self,
        calculation_rate=None,
        a=1,
        b=-1,
        c=-0.75,
        frequency=22050,
        xi=0,
        ):
        UGen.__init__(
            self,
            calculation_rate=calculation_rate,
            a=a,
            b=b,
            c=c,
            frequency=frequency,
            xi=xi,
            )

    ### PUBLIC METHODS ###

    @classmethod
    def ar(
        cls,
        a=1,
        b=-1,
        c=-0.75,
        frequency=22050,
        xi=0,
        ):
        """
        Constructs an audio-rate QuadL.

        ::

            >>> quad_l = supriya.ugens.QuadL.ar(
            ...     a=1,
            ...     b=-1,
            ...     c=-0.75,
            ...     frequency=22050,
            ...     xi=0,
            ...     )
            >>> quad_l
            QuadL.ar()

        Returns ugen graph.
        """
        import supriya.synthdefs
        calculation_rate = supriya.CalculationRate.AUDIO
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            a=a,
            b=b,
            c=c,
            frequency=frequency,
            xi=xi,
            )
        return ugen

    # def equation(): ...

    ### PUBLIC PROPERTIES ###

    @property
    def a(self):
        """
        Gets `a` input of QuadL.

        ::

            >>> quad_l = supriya.ugens.QuadL.ar(
            ...     a=1,
            ...     b=-1,
            ...     c=-0.75,
            ...     frequency=22050,
            ...     xi=0,
            ...     )
            >>> quad_l.a
            1.0

        Returns ugen input.
        """
        index = self._ordered_input_names.index('a')
        return self._inputs[index]

    @property
    def b(self):
        """
        Gets `b` input of QuadL.

        ::

            >>> quad_l = supriya.ugens.QuadL.ar(
            ...     a=1,
            ...     b=-1,
            ...     c=-0.75,
            ...     frequency=22050,
            ...     xi=0,
            ...     )
            >>> quad_l.b
            -1.0

        Returns ugen input.
        """
        index = self._ordered_input_names.index('b')
        return self._inputs[index]

    @property
    def c(self):
        """
        Gets `c` input of QuadL.

        ::

            >>> quad_l = supriya.ugens.QuadL.ar(
            ...     a=1,
            ...     b=-1,
            ...     c=-0.75,
            ...     frequency=22050,
            ...     xi=0,
            ...     )
            >>> quad_l.c
            -0.75

        Returns ugen input.
        """
        index = self._ordered_input_names.index('c')
        return self._inputs[index]

    @property
    def frequency(self):
        """
        Gets `frequency` input of QuadL.

        ::

            >>> quad_l = supriya.ugens.QuadL.ar(
            ...     a=1,
            ...     b=-1,
            ...     c=-0.75,
            ...     frequency=22050,
            ...     xi=0,
            ...     )
            >>> quad_l.frequency
            22050.0

        Returns ugen input.
        """
        index = self._ordered_input_names.index('frequency')
        return self._inputs[index]

    @property
    def xi(self):
        """
        Gets `xi` input of QuadL.

        ::

            >>> quad_l = supriya.ugens.QuadL.ar(
            ...     a=1,
            ...     b=-1,
            ...     c=-0.75,
            ...     frequency=22050,
            ...     xi=0,
            ...     )
            >>> quad_l.xi
            0.0

        Returns ugen input.
        """
        index = self._ordered_input_names.index('xi')
        return self._inputs[index]
