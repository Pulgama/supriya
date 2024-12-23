from typing import Tuple

import pytest

from supriya.mixers import Session

from .conftest import debug_tree


@pytest.mark.asyncio
async def test_complex_session(complex_session: Tuple[Session, str]) -> None:
    """
    Check idempotency of node / bus IDs
    """
    session, initial_tree = complex_session
    await session.boot()
    actual_initial_tree = await debug_tree(session)
    assert initial_tree == actual_initial_tree
