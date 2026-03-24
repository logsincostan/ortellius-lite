"""Tools for building access maps from firmware binaries."""

from collections.abc import Iterable, Iterator
from collections.abc import Set as AbstractSet
from pathlib import Path
from shutil import move
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING
from urllib.request import urlretrieve
from zipfile import ZipFile

import pyghidra
from pydantic import BaseModel, field_serializer, field_validator

from .typing import is_list, is_set

if TYPE_CHECKING:
    from ghidra.program.flatapi import FlatProgramAPI


GHIDRA_URL = (
    "https://github.com/NationalSecurityAgency/ghidra/releases/download/"
    "Ghidra_12.0_build/ghidra_12.0_PUBLIC_20251205.zip"
)


def install_ghidra(install_dir: Path) -> None:
    """Download and extract Ghidra."""
    if install_dir.is_dir():
        return
    install_dir.parent.mkdir(parents=True, exist_ok=True)

    with TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        ghidra_zip, _ = urlretrieve(GHIDRA_URL, tmpdir / "ghidra.zip")  # noqa: S310
        with ZipFile(ghidra_zip) as zf:
            zf.extractall(tmpdir)
        move(next(tmpdir.glob("ghidra_*")), install_dir)


class AnalysisResult(BaseModel):
    """Serializable result of an analysis."""

    read: set[int]
    write: set[int]

    @field_serializer("read", "write")
    def serialize_read(self, value: list[int]) -> list[str]:
        """Serialize hexadecimally."""
        return [f"{addr:08x}" for addr in sorted(value)]

    @field_validator("read", "write", mode="before")
    @classmethod
    def validate_from_hex(cls, value: object) -> AbstractSet[int]:
        """Unserialize from hex."""
        if is_set(value, int):
            return value

        if is_list(value, str):
            return {int(v, 16) for v in value}

        msg = "Unexpected type."
        raise ValueError(msg)


def analyze_file(flatapi: "FlatProgramAPI") -> AnalysisResult:
    """Analyze loaded file and write results to outfile."""
    program = flatapi.getCurrentProgram()
    memory = program.memory
    for block in memory.blocks:
        block.setRead(True)
        block.setWrite(False)
        block.setExecute(True)
    flatapi.analyzeAll(program)

    instruction = flatapi.firstInstruction
    reads: set[int] = set()
    writes: set[int] = set()
    while instruction is not None:
        for ref in instruction.referencesFrom:
            if ref.stackReference:
                continue
            if ref.referenceType.read:
                reads.add((int(ref.toAddress.offset) // 4) * 4)
            if ref.referenceType.write:
                writes.add((int(ref.toAddress.offset) // 4) * 4)
        instruction = instruction.next
    return AnalysisResult(read=reads, write=writes)


def analyze(
    source: Path, ghidra_dir: Path = Path("deps/ghidra")
) -> Iterator[tuple[Path, AnalysisResult]]:
    """Identify xrefs in firmware binaries."""
    install_ghidra(ghidra_dir)
    pyghidra.start(install_dir=ghidra_dir)

    if source.is_dir():
        files: Iterable[Path] = source.rglob("*")
    elif source.is_file():
        files = [source]
    else:
        msg = f"Source {source} is neither a file nor a directory."
        raise ValueError(msg)

    for file in files:
        if not file.is_file():
            continue
        with (
            TemporaryDirectory() as tmpdir,
            pyghidra.open_program(
                file,
                analyze=False,
                language="ARM:LE:32:Cortex",
                project_location=tmpdir,
            ) as api,
        ):
            yield file, analyze_file(api)
