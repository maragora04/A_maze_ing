"""Configuration file parser for a_maze_ing."""

from typing import Any, Optional

RED = "\033[38;5;196m"


def parse_config(path: str) -> dict[str, Any]:
    """Parse and validate the maze configuration file.

    Args:
        path: Path to the configuration file.

    Returns:
        A dictionary containing validated configuration parameters:
        width, height, entry, exit, output, perfect, and seed.

    Raises:
        FileNotFoundError: If the config file does not exist.
        ValueError: If mandatory keys are missing, syntax is invalid,
            or parameters are outside allowable bounds.
    """
    raw: dict[str, str] = {}
    with open(path, "r", encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ValueError(f"{RED}line {n}: expected KEY=VALUE")
            key, value = line.split("=", 1)
            raw[key.strip()] = value.strip()

    mandatory = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"}
    missing = mandatory - raw.keys()
    if missing:
        raise ValueError(f"{RED}missing keys: {', '.join(sorted(missing))}")

    width = to_int("WIDTH", raw["WIDTH"])
    height = to_int("HEIGHT", raw["HEIGHT"])
    if width <= 0 or height <= 0:
        raise ValueError(f"{RED}WIDTH and HEIGHT must be strictly positive integers.")

    entry = to_point("ENTRY", raw["ENTRY"])
    exit_ = to_point("EXIT", raw["EXIT"])

    if not (0 <= entry[0] < width and 0 <= entry[1] < height):
        raise ValueError(f"{RED}ENTRY {entry} is outside the maze dimensions ({width}x{height}).")

    if not (0 <= exit_[0] < width and 0 <= exit_[1] < height):
        raise ValueError(f"{RED}EXIT {exit_} is outside the maze dimensions ({width}x{height}).")

    if entry == exit_:
        raise ValueError(f"{RED}ENTRY and EXIT coordinates must be distinct.")

    perfect_str = raw["PERFECT"].lower()
    if perfect_str not in ("true", "false"):
        raise ValueError(f"{RED}PERFECT must be 'True' or 'False', got '{raw['PERFECT']}'")

    seed = to_seed(raw.get("SEED", ""))

    return {
        "width": width,
        "height": height,
        "entry": entry,
        "exit": exit_,
        "output": raw["OUTPUT_FILE"],
        "perfect": perfect_str == "true",
        "seed": seed,
    }


def to_seed(value: str) -> Optional[str]:
    """Extract and validate the seed value.

    Args:
        value: The raw seed string from the config file.

    Returns:
        The seed string, or None if the value is empty.
    """
    cleaned = value.strip()
    return cleaned if cleaned else None


def to_int(key: str, value: str) -> int:
    """Convert a config value to an integer with descriptive error reporting.

    Args:
        key: The configuration key being parsed.
        value: The raw string value.

    Returns:
        The parsed integer.

    Raises:
        ValueError: If the string cannot be converted to an integer.
    """
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"{RED}{key}: expected an integer, got '{value}'") from None


def to_point(key: str, value: str) -> tuple[int, int]:
    """Convert a coordinate string 'x,y' to a tuple of integers.

    Args:
        key: The configuration key being parsed.
        value: The raw coordinate string.

    Returns:
        A tuple of (x, y) coordinates.

    Raises:
        ValueError: If format is not 'x,y' or coordinates are invalid integers.
    """
    parts = value.split(",")
    if len(parts) != 2:
        raise ValueError(f"{RED}{key}: expected 'x,y', got '{value}'")
    return to_int(f"{key} X", parts[0].strip()), to_int(f"{key} Y", parts[1].strip())
