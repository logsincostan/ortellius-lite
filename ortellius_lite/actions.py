"""CLI actions."""

from logging import getLogger
from pathlib import Path
from sys import stdout
from typing import TextIO

from . import rank_shadows

log = getLogger(__name__)


def _print_ranking(ranking: list[tuple[str, float]], stream: TextIO = stdout) -> None:
    last_score = None
    rank = 1
    with_this_rank = 0
    for name, s in ranking:
        if s != last_score:
            last_score = s
            if with_this_rank > 0:
                stream.write(f"{with_this_rank} devices with rank #{rank - 1}\n")
            stream.write(
                f"Rank #{rank}: (score {s}, normalized score {s / ranking[0][1]})\n"
            )
            rank += 1
            with_this_rank = 0
        with_this_rank += 1

        stream.write(f"\t{name}\n")

    if with_this_rank > 0:
        stream.write(f"{with_this_rank} devices with rank #{rank}\n")


def rank_shadow_jaccard(
    device_shadow: Path, firmware_shadow: Path, stream: TextIO = stdout
) -> None:
    """Rank all known devices by Shadow Jaccard similarity to the given memory dump."""
    ranking = rank_shadows(device_shadow, firmware_shadow)
    _print_ranking(ranking, stream)
