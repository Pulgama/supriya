# -*- encoding: utf-8 -*-
from supriya.tools.ugentools.PV_ChainUGen import PV_ChainUGen


class PV_JensenAndersen(PV_ChainUGen):
    r'''A FFT feature detector for onset detection.

    ::

        >>> pv_chain = ugentools.FFT(
        ...     source=ugentools.WhiteNoise.ar(),
        ...     )
        >>> pv_jensen_andersen = ugentools.PV_JensenAndersen(
        ...     pv_chain=pv_chain,
        ...     prophfc=0.25,
        ...     prophfe=0.25,
        ...     propsc=0.25,
        ...     propsf=0.25,
        ...     threshold=1,
        ...     waittime=0.04,
        ...     )
        >>> pv_jensen_andersen
        PV_JensenAndersen.kr()
        
    '''

    ### CLASS VARIABLES ###

    __documentation_section__ = 'FFT UGens'

    __slots__ = ()

    _ordered_input_names = (
        'pv_chain',
        'propsc',
        'prophfe',
        'prophfc',
        'propsf',
        'threshold',
        'waittime',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        pv_chain=None,
        prophfc=0.25,
        prophfe=0.25,
        propsc=0.25,
        propsf=0.25,
        threshold=1,
        waittime=0.04,
        ):
        PV_ChainUGen.__init__(
            self,
            pv_chain=pv_chain,
            prophfc=prophfc,
            prophfe=prophfe,
            propsc=propsc,
            propsf=propsf,
            threshold=threshold,
            waittime=waittime,
            )

    ### PUBLIC METHODS ###

    @classmethod
    def new(
        cls,
        pv_chain=None,
        prophfc=0.25,
        prophfe=0.25,
        propsc=0.25,
        propsf=0.25,
        threshold=1,
        waittime=0.04,
        ):
        r'''Constructs an audio-rate PV_JensenAndersen.

        ::

            >>> pv_chain = ugentools.FFT(
            ...     source=ugentools.WhiteNoise.ar(),
            ...     )
            >>> pv_jensen_andersen = ugentools.PV_JensenAndersen(
            ...     pv_chain=pv_chain,
            ...     prophfc=0.25,
            ...     prophfe=0.25,
            ...     propsc=0.25,
            ...     propsf=0.25,
            ...     threshold=1,
            ...     waittime=0.04,
            ...     )
            >>> pv_jensen_andersen
            PV_JensenAndersen.kr()

        Returns ugen graph.
        '''
        ugen = cls._new_expanded(
            pv_chain=pv_chain,
            prophfc=prophfc,
            prophfe=prophfe,
            propsc=propsc,
            propsf=propsf,
            threshold=threshold,
            waittime=waittime,
            )
        return ugen

    ### PUBLIC PROPERTIES ###

    @property
    def pv_chain(self):
        r'''Gets `pv_chain` input of PV_JensenAndersen.

        ::

            >>> pv_chain = ugentools.FFT(
            ...     source=ugentools.WhiteNoise.ar(),
            ...     )
            >>> pv_jensen_andersen = ugentools.PV_JensenAndersen(
            ...     pv_chain=pv_chain,
            ...     prophfc=0.25,
            ...     prophfe=0.25,
            ...     propsc=0.25,
            ...     propsf=0.25,
            ...     threshold=1,
            ...     waittime=0.04,
            ...     )
            >>> pv_jensen_andersen.pv_chain
            OutputProxy(
                source=FFT(
                    buffer_id=OutputProxy(
                        source=LocalBuf(
                            frame_count=2048.0,
                            channel_count=1.0,
                            calculation_rate=CalculationRate.SCALAR
                            ),
                        output_index=0
                        ),
                    source=OutputProxy(
                        source=WhiteNoise(
                            calculation_rate=CalculationRate.AUDIO
                            ),
                        output_index=0
                        ),
                    active=1.0,
                    hop=0.5,
                    window_size=0.0,
                    window_type=0.0
                    ),
                output_index=0
                )

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('pv_chain')
        return self._inputs[index]

    @property
    def prophfc(self):
        r'''Gets `prophfc` input of PV_JensenAndersen.

        ::

            >>> pv_chain = ugentools.FFT(
            ...     source=ugentools.WhiteNoise.ar(),
            ...     )
            >>> pv_jensen_andersen = ugentools.PV_JensenAndersen(
            ...     pv_chain=pv_chain,
            ...     prophfc=0.25,
            ...     prophfe=0.25,
            ...     propsc=0.25,
            ...     propsf=0.25,
            ...     threshold=1,
            ...     waittime=0.04,
            ...     )
            >>> pv_jensen_andersen.prophfc
            0.25

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('prophfc')
        return self._inputs[index]

    @property
    def prophfe(self):
        r'''Gets `prophfe` input of PV_JensenAndersen.

        ::

            >>> pv_jensen_andersen = ugentools.PV_JensenAndersen(
            ...     pv_chain=pv_chain,
            ...     prophfc=0.25,
            ...     prophfe=0.25,
            ...     propsc=0.25,
            ...     propsf=0.25,
            ...     threshold=1,
            ...     waittime=0.04,
            ...     )
            >>> pv_jensen_andersen.prophfe
            0.25

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('prophfe')
        return self._inputs[index]

    @property
    def propsc(self):
        r'''Gets `propsc` input of PV_JensenAndersen.

        ::

            >>> pv_chain = ugentools.FFT(
            ...     source=ugentools.WhiteNoise.ar(),
            ...     )
            >>> pv_jensen_andersen = ugentools.PV_JensenAndersen(
            ...     pv_chain=pv_chain,
            ...     prophfc=0.25,
            ...     prophfe=0.25,
            ...     propsc=0.25,
            ...     propsf=0.25,
            ...     threshold=1,
            ...     waittime=0.04,
            ...     )
            >>> pv_jensen_andersen.propsc
            0.25

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('propsc')
        return self._inputs[index]

    @property
    def propsf(self):
        r'''Gets `propsf` input of PV_JensenAndersen.

        ::

            >>> pv_chain = ugentools.FFT(
            ...     source=ugentools.WhiteNoise.ar(),
            ...     )
            >>> pv_jensen_andersen = ugentools.PV_JensenAndersen(
            ...     pv_chain=pv_chain,
            ...     prophfc=0.25,
            ...     prophfe=0.25,
            ...     propsc=0.25,
            ...     propsf=0.25,
            ...     threshold=1,
            ...     waittime=0.04,
            ...     )
            >>> pv_jensen_andersen.propsf
            0.25

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('propsf')
        return self._inputs[index]

    @property
    def threshold(self):
        r'''Gets `threshold` input of PV_JensenAndersen.

        ::

            >>> pv_chain = ugentools.FFT(
            ...     source=ugentools.WhiteNoise.ar(),
            ...     )
            >>> pv_jensen_andersen = ugentools.PV_JensenAndersen(
            ...     pv_chain=pv_chain,
            ...     prophfc=0.25,
            ...     prophfe=0.25,
            ...     propsc=0.25,
            ...     propsf=0.25,
            ...     threshold=1,
            ...     waittime=0.04,
            ...     )
            >>> pv_jensen_andersen.threshold
            1.0

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('threshold')
        return self._inputs[index]

    @property
    def waittime(self):
        r'''Gets `waittime` input of PV_JensenAndersen.

        ::

            >>> pv_chain = ugentools.FFT(
            ...     source=ugentools.WhiteNoise.ar(),
            ...     )
            >>> pv_jensen_andersen = ugentools.PV_JensenAndersen(
            ...     pv_chain=pv_chain,
            ...     prophfc=0.25,
            ...     prophfe=0.25,
            ...     propsc=0.25,
            ...     propsf=0.25,
            ...     threshold=1,
            ...     waittime=0.04,
            ...     )
            >>> pv_jensen_andersen.waittime
            0.04

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('waittime')
        return self._inputs[index]