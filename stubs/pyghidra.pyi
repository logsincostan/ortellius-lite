from contextlib import AbstractContextManager
from pathlib import Path

from ghidra.program.flatapi import FlatProgramAPI

def start(verbose: bool = False, *, install_dir: Path | None = None) -> None: ...
def open_program(
    binary_path: str | Path,
    project_location: str | Path | None = None,
    project_name: str | None = None,
    analyze: bool = True,
    language: str | None = None,
    compiler: str | None = None,
    loader: str | None = None,
) -> AbstractContextManager[FlatProgramAPI]: ...
