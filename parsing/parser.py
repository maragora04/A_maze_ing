#errors to handle:
#invalid config
#file not found
#bad syntax
#impossible maze params

#clear error messages

import sys
from typing import Any

from mazegen import MazeGenerator
from maze_render import (
    WALL_COLOURS, build_canvas, path_to_cells, render,
)


def parse_config(path: str) -> dict[str, Any]:
    raw: dict[str, str] = {}
    with open(path) as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ValueError(f"line {n}: expected KEY=VALUE")
            key, value = line.split("=", 1)
            raw[key.strip()] = value.strip()

    missing = {"WIDTH", "HEIGHT", "ENTRY", "EXIT",
               "OUTPUT_FILE", "PERFECT"} - raw.keys()
    if missing:
        raise ValueError(f"missing keys: {', '.join(sorted(missing))}")

    def point(s: str) -> tuple[int, int]:
        x, y = s.split(",")
        return int(x), int(y)

    seed_raw = raw.get("SEED", "")
    seed = to_int("SEED", seed_raw) if seed_raw else None

    return {
        "width": to_int("WIDTH", raw["WIDTH"]),
        "height": to_int("HEIGHT", raw["HEIGHT"]),
        "entry": to_point("ENTRY", raw["ENTRY"]),
        "exit": to_point("EXIT", raw["EXIT"]),
        "output": raw["OUTPUT_FILE"],
        "perfect": raw["PERFECT"].lower() == "true",
        "seed": seed,
    }

def to_int(key: str, value: str) -> int:
    try:
        return int(value)
    except ValueError:
        raise ValueError(
            f"{key}: expected an integer, got '{value}'"
        ) from None


def to_point(key: str, value: str) -> tuple[int, int]:
    parts = value.split(",")
    if len(parts) != 2:
        raise ValueError(f"{key}: expected 'x,y', got '{value}'")
    return to_int(key, parts[0].strip()), to_int(key, parts[1].strip())

# possibly more i missed