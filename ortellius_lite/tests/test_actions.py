"""Test ortellius."""

import unittest
from io import StringIO
from pathlib import Path

from ..actions import rank_shadow_jaccard

DEVICE_SHADOW = Path("test_input/device_shadow.tar.gz")
FIRMWARE_SHADOW = Path("test_input/firmware_shadow.json")
REFERENCE_RANKING = Path("test_input/ranking.txt")

# ruff: noqa: S101


class TestUserCommands(unittest.TestCase):
    """Test CLI commands."""

    def test_rank_shadow_jaccard(self) -> None:
        """Test rank_shadow_jaccard."""
        buffer = StringIO()

        rank_shadow_jaccard(DEVICE_SHADOW, FIRMWARE_SHADOW, stream=buffer)

        assert buffer.getvalue() == REFERENCE_RANKING.read_text()
