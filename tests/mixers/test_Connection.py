from typing import Dict

import pytest

from supriya.mixers.components import Component
from supriya.mixers.mixers import Mixer
from supriya.mixers.routing import Connection


@pytest.mark.parametrize(
    "source_name, target_name, feedsback",
    [
        ("mixer", "mixer", True),
        ("mixer", "track_one", True),
        ("mixer", "track_two", True),
        ("mixer", "track_one_child", True),
        ("mixer", "track_two_child", True),
        ("track_one", "mixer", False),
        ("track_one", "track_one", True),
        ("track_one", "track_two", False),
        ("track_one", "track_one_child", True),
        ("track_one", "track_two_child", False),
        ("track_two", "mixer", False),
        ("track_two", "track_one", True),
        ("track_two", "track_two", True),
        ("track_two", "track_one_child", True),
        ("track_two", "track_two_child", True),
        ("track_one_child", "mixer", False),
        ("track_one_child", "track_one", False),
        ("track_one_child", "track_two", False),
        ("track_one_child", "track_one_child", True),
        ("track_one_child", "track_two_child", False),
        ("track_two_child", "mixer", False),
        ("track_two_child", "track_one", True),
        ("track_two_child", "track_two", False),
        ("track_two_child", "track_one_child", True),
        ("track_two_child", "track_two_child", True),
    ],
)
@pytest.mark.asyncio
async def test_Connection_feedsback(
    source_name: str, target_name: str, feedsback: bool, mixer: Mixer
) -> None:
    components: Dict[str, Component] = {
        "mixer": mixer,
        "track_one": (track_one := mixer.tracks[0]),
        "track_two": (track_two := await mixer.add_track()),
        "track_one_child": await track_one.add_track(),
        "track_two_child": await track_two.add_track(),
    }
    source = components[source_name]
    target = components[target_name]
    assert Connection.feedsback(source.graph_order, target.graph_order) == feedsback, (
        source_name,
        target_name,
    )
