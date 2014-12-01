# -*- encoding: utf-8 -*-
from supriya.tools.ugentools.Filter import Filter


class CombFormlet(Filter):
    r'''

    ::

        >>> source = ugentools.In.ar(bus=0)
        >>> comb_formlet = ugentools.CombFormlet.ar(
        ...     attack_time=1,
        ...     decay_time=1,
        ...     frequency=440,
        ...     min_frequency=20,
        ...     source=source,
        ...     )
        >>> comb_formlet
        CombFormlet.ar()

    '''

    ### CLASS VARIABLES ###

    __documentation_section__ = None

    __slots__ = ()

    _ordered_input_names = (
        'source',
        'frequency',
        'attack_time',
        'decay_time',
        'min_frequency',
        )

    _valid_calculation_rates = None

    ### INITIALIZER ###

    def __init__(
        self,
        calculation_rate=None,
        attack_time=1,
        decay_time=1,
        frequency=440,
        min_frequency=20,
        source=None,
        ):
        Filter.__init__(
            self,
            calculation_rate=calculation_rate,
            attack_time=attack_time,
            decay_time=decay_time,
            frequency=frequency,
            min_frequency=min_frequency,
            source=source,
            )

    ### PUBLIC METHODS ###

    @classmethod
    def ar(
        cls,
        attack_time=1,
        decay_time=1,
        frequency=440,
        min_frequency=20,
        source=None,
        ):
        r'''Constructs an audio-rate CombFormlet.

        ::

            >>> source = ugentools.In.ar(bus=0)
            >>> comb_formlet = ugentools.CombFormlet.ar(
            ...     attack_time=1,
            ...     decay_time=1,
            ...     frequency=440,
            ...     min_frequency=20,
            ...     source=source,
            ...     )
            >>> comb_formlet
            CombFormlet.ar()

        Returns ugen graph.
        '''
        from supriya.tools import synthdeftools
        calculation_rate = synthdeftools.CalculationRate.AUDIO
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            attack_time=attack_time,
            decay_time=decay_time,
            frequency=frequency,
            min_frequency=min_frequency,
            source=source,
            )
        return ugen

    # def coeffs(): ...

    # def magResponse(): ...

    # def magResponse2(): ...

    # def magResponse5(): ...

    # def magResponseN(): ...

    # def scopeResponse(): ...

    ### PUBLIC PROPERTIES ###

    @property
    def attack_time(self):
        r'''Gets `attack_time` input of CombFormlet.

        ::

            >>> source = ugentools.In.ar(bus=0)
            >>> comb_formlet = ugentools.CombFormlet.ar(
            ...     attack_time=1,
            ...     decay_time=1,
            ...     frequency=440,
            ...     min_frequency=20,
            ...     source=source,
            ...     )
            >>> comb_formlet.attack_time
            1.0

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('attack_time')
        return self._inputs[index]

    @property
    def decay_time(self):
        r'''Gets `decay_time` input of CombFormlet.

        ::

            >>> source = ugentools.In.ar(bus=0)
            >>> comb_formlet = ugentools.CombFormlet.ar(
            ...     attack_time=1,
            ...     decay_time=1,
            ...     frequency=440,
            ...     min_frequency=20,
            ...     source=source,
            ...     )
            >>> comb_formlet.decay_time
            1.0

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('decay_time')
        return self._inputs[index]

    @property
    def frequency(self):
        r'''Gets `frequency` input of CombFormlet.

        ::

            >>> source = ugentools.In.ar(bus=0)
            >>> comb_formlet = ugentools.CombFormlet.ar(
            ...     attack_time=1,
            ...     decay_time=1,
            ...     frequency=440,
            ...     min_frequency=20,
            ...     source=source,
            ...     )
            >>> comb_formlet.frequency
            440.0

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('frequency')
        return self._inputs[index]

    @property
    def min_frequency(self):
        r'''Gets `min_frequency` input of CombFormlet.

        ::

            >>> source = ugentools.In.ar(bus=0)
            >>> comb_formlet = ugentools.CombFormlet.ar(
            ...     attack_time=1,
            ...     decay_time=1,
            ...     frequency=440,
            ...     min_frequency=20,
            ...     source=source,
            ...     )
            >>> comb_formlet.min_frequency
            20.0

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('min_frequency')
        return self._inputs[index]

    @property
    def source(self):
        r'''Gets `source` input of CombFormlet.

        ::

            >>> source = ugentools.In.ar(bus=0)
            >>> comb_formlet = ugentools.CombFormlet.ar(
            ...     attack_time=1,
            ...     decay_time=1,
            ...     frequency=440,
            ...     min_frequency=20,
            ...     source=source,
            ...     )
            >>> comb_formlet.source
            OutputProxy(
                source=In(
                    bus=0.0,
                    calculation_rate=<CalculationRate.AUDIO: 2>,
                    channel_count=1
                    ),
                output_index=0
                )

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('source')
        return self._inputs[index]