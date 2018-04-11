import supriya.realtime
from supriya.tools import synthdeftools
from supriya import systemtools


class Test(systemtools.TestCase):

    def setUp(self):
        super(systemtools.TestCase, self).setUp()
        self.server = supriya.realtime.Server().boot()

    def tearDown(self):
        self.server.quit()
        super(systemtools.TestCase, self).tearDown()

    def test_01(self):

        bus_group_one = supriya.realtime.BusGroup(
            bus_count=4,
            calculation_rate=synthdeftools.CalculationRate.CONTROL,
            )

        assert not bus_group_one.is_allocated
        assert bus_group_one.bus_id is None
        assert bus_group_one.server is None
        assert len(bus_group_one) == 4
        for bus in bus_group_one:
            assert not bus.is_allocated
            assert bus.bus_group is bus_group_one
            assert bus.bus_id is None
            assert bus.calculation_rate == bus_group_one.calculation_rate

        bus_group_one.allocate()
        self.server.sync()

        assert bus_group_one.is_allocated
        assert bus_group_one.bus_id is 0
        assert bus_group_one.server is self.server
        assert len(bus_group_one) == 4
        for i, bus in enumerate(bus_group_one):
            assert bus.is_allocated
            assert bus.bus_group is bus_group_one
            assert bus.bus_id == bus_group_one.bus_id + i
            assert bus.calculation_rate == bus_group_one.calculation_rate

        bus_group_two = supriya.realtime.BusGroup(
            bus_count=4,
            calculation_rate=synthdeftools.CalculationRate.CONTROL,
            )
        self.server.sync()

        assert not bus_group_two.is_allocated
        assert bus_group_two.bus_id is None
        assert bus_group_two.server is None
        assert len(bus_group_two) == 4
        for bus in bus_group_two:
            assert not bus.is_allocated
            assert bus.bus_group is bus_group_two
            assert bus.bus_id is None
            assert bus.calculation_rate == bus_group_two.calculation_rate

        bus_group_two.allocate()
        self.server.sync()

        assert bus_group_two.is_allocated
        assert bus_group_two.bus_id is 4
        assert bus_group_two.server is self.server
        assert len(bus_group_two) == 4
        for i, bus in enumerate(bus_group_two):
            assert bus.is_allocated
            assert bus.bus_group is bus_group_two
            assert bus.bus_id is bus_group_two.bus_id + i
            assert bus.calculation_rate == bus_group_two.calculation_rate

        bus_group_one.free()
        self.server.sync()

        assert not bus_group_one.is_allocated
        assert bus_group_one.bus_id is None
        assert bus_group_one.server is None
        assert len(bus_group_one) == 4
        for bus in bus_group_one:
            assert not bus.is_allocated
            assert bus.bus_group is bus_group_one
            assert bus.bus_id is None
            assert bus.calculation_rate == bus_group_one.calculation_rate

        bus_group_two.free()
        self.server.sync()

        assert not bus_group_two.is_allocated
        assert bus_group_two.bus_id is None
        assert bus_group_two.server is None
        assert len(bus_group_two) == 4
        for bus in bus_group_two:
            assert not bus.is_allocated
            assert bus.bus_group is bus_group_two
            assert bus.bus_id is None
            assert bus.calculation_rate == bus_group_two.calculation_rate
