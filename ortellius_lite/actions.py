"""CLI actions."""

from logging import getLogger
from pathlib import Path
from sys import stdout
from typing import TextIO

from serstor import Storage
from svdmap.model import Shadow

from .imported_models import AnalysisResult

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
    with Storage(device_shadow) as storage:
        shadow_base = [storage.get_and_unserialize(name, Shadow) for name in storage]
    firmware = AnalysisResult.model_validate_json(firmware_shadow.read_text())

    ranks: dict[str, float] = {}
    for shadow in shadow_base:
        intersection = len(shadow.read & firmware.read)
        union = len(shadow.read | firmware.read)
        similarity = intersection / union if union > 0 else 0.0
        ranks[shadow.name] = similarity

    log.info("Sorting by similarity...")
    ranking = sorted(ranks.items(), key=lambda x: x[1], reverse=True)
    _print_ranking(ranking, stream)
