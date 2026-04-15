"""Ortellius analyzes and compares SVD files for ARM Cortex-M MCUs."""

from logging import getLogger
from pathlib import Path

from serstor import Storage
from svdmap.model import Shadow

from .access_map import AnalysisResult

log = getLogger(__name__)


def rank_shadows(
    device_shadow: Path | list[Shadow], firmware_shadow: Path | AnalysisResult
) -> list[tuple[str, float]]:
    """Rank all known devices by Shadow Jaccard similarity to the given memory dump."""
    if isinstance(device_shadow, Path):
        with Storage(device_shadow) as storage:
            shadow_base = [
                storage.get_and_unserialize(name, Shadow) for name in storage
            ]
    else:
        shadow_base = device_shadow
    if isinstance(firmware_shadow, Path):
        firmware = AnalysisResult.model_validate_json(firmware_shadow.read_text())
    else:
        firmware = firmware_shadow

    ranks: dict[str, float] = {}
    for shadow in shadow_base:
        intersection = len(shadow.read & firmware.read)
        union = len(shadow.read | firmware.read)
        similarity = intersection / union if union > 0 else 0.0
        ranks[shadow.name] = similarity

    log.info("Sorting by similarity...")
    return sorted(ranks.items(), key=lambda x: x[1], reverse=True)
