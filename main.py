"""Deadpan forecast for Nulverton, a city that does not exist.

The program emits exactly one line of text: a weather forecast read as if
by a straight-faced TV meteorologist. It writes the line to
``$MAKEFUN_OUTPUT_DIR/entry.txt`` (``/output/entry.txt`` when the variable
is unset), then reads the file back and confirms the bytes on disk are
identical to the line it intended to write.

The output is fully deterministic: the line is a constant, and the program
touches no network, no clock and no randomness. The only environment input
is the output directory.
"""

import os
import sys
from pathlib import Path

LINE = (
    "In Nulverton, light drizzle falls upward at 14 millimetres an hour; "
    "residents are advised to hold their umbrellas upside down and carry "
    "on as normal."
)

LIMIT = 160
DEFAULT_DIR = "/output"


def validate(line: str) -> list[str]:
    """Collect every gate violation for ``line``; an empty list means valid."""
    faults: list[str] = []
    if len(line) == 0:
        faults.append("empty line (0 chars, need 1-160)")
    if line.strip() == "":
        faults.append("line is only whitespace")
    if line != line.strip():
        faults.append("line has leading or trailing whitespace")
    if any(ch in line for ch in ("\n", "\r")):
        faults.append("line spans more than one line")
    if len(line) > LIMIT:
        faults.append(f"line is {len(line)} chars, over the {LIMIT} limit")
    try:
        line.encode("utf-8")
    except UnicodeEncodeError:
        faults.append("line is not valid UTF-8")
    return faults


def destination() -> Path:
    """Return the entry.txt path, honouring MAKEFUN_OUTPUT_DIR first."""
    directory = os.environ.get("MAKEFUN_OUTPUT_DIR") or DEFAULT_DIR
    return Path(directory) / "entry.txt"


def emit(line: str) -> int:
    """Write ``line`` to disk and verify the round-trip. Returns exit code."""
    faults = validate(line)
    if faults:
        for fault in faults:
            print(f"invalid entry: {fault}", file=sys.stderr)
        return 1

    path = destination()
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = line.encode("utf-8")
    path.write_bytes(encoded)

    if path.read_bytes() != encoded:
        print("invalid entry: bytes on disk differ from the forecast", file=sys.stderr)
        return 1

    print(f"wrote entry.txt: {len(line)} chars, {len(encoded)} bytes -> {path}")
    return 0


def main() -> int:
    return emit(LINE)


if __name__ == "__main__":
    raise SystemExit(main())
