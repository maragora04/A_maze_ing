#errors to handle:
#invalid config
#file not found
#bad syntax
#impossible maze params

#clear error messages

import sys
from typing import Any, Optional

from mazegen import MazeGenerator
from maze_render import (
    WALL_COLOURS, PATH_COLOURS, build_canvas, path_to_cells, render,
)

RED = "\033[38;5;196m"


def parse_config(path: str) -> dict[str, Any]:
    raw: dict[str, str] = {}
    with open(path) as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ValueError(f"{RED}line {n}: expected KEY=VALUE")
            key, value = line.split("=", 1)
            raw[key.strip()] = value.strip()

    missing = {"WIDTH", "HEIGHT", "ENTRY", "EXIT",
               "OUTPUT_FILE", "PERFECT"} - raw.keys()
    if missing:
        raise ValueError(f"{RED}missing keys: {', '.join(sorted(missing))}")

    def point(s: str) -> tuple[int, int]:
        x, y = s.split(",")
        return int(x), int(y)

    seed = to_seed(raw.get("SEED", ""))

    return {
        "width": to_int("WIDTH", raw["WIDTH"]),
        "height": to_int("HEIGHT", raw["HEIGHT"]),
        "entry": to_point("ENTRY", raw["ENTRY"]),
        "exit": to_point("EXIT", raw["EXIT"]),
        "output": raw["OUTPUT_FILE"],
        "perfect": raw["PERFECT"].lower() == "true",
        "seed": seed,
    }

def to_seed(value: str) -> Optional[str]:
    # the seed string None if empty, refuses integers
    if not value:
        return None
    try:
        int(value)
    except ValueError:
        return value
    raise ValueError(f"{RED}SEED: expected a string, got integer '{value}'")


def to_int(key: str, value: str) -> int:
    # Convert a config value to int, naming the key on failure
    try:
        return int(value)
    except ValueError:
        raise ValueError(
            f"{key}: expected an integer, got '{value}'"
        ) from None


def to_point(key: str, value: str) -> tuple[int, int]:
    parts = value.split(",")
    if len(parts) != 2:
        raise ValueError(f"{RED}{key}: expected 'x,y', got '{value}'")
    return to_int(key, parts[0].strip()), to_int(key, parts[1].strip())
