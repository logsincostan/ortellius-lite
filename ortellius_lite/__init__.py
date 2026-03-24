"""Ortellius is a tool for analyzing and comparing SVD files for ARM Cortex-M microcontrollers."""

from logging import getLogger
from pathlib import Path

from serstor import Storage
from svdmap.model import Shadow

from .imported_models import AnalysisResult

log = getLogger(__name__)


def rank_shadows(device_shadow: Path, firmware_shadow: Path) -> list[tuple[str, float]]:
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
    return sorted(ranks.items(), key=lambda x: x[1], reverse=True)
