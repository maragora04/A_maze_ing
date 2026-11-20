"""Terminal renderer for a_maze_ing."""

from typing import Optional

N, E, S, W = 1, 2, 4, 8
Cell = tuple[int, int]  # (x, y)

WALL, OPEN, PATH, ENTRY, EXIT, PATTERN = range(6)

DIRS: dict[str, Cell] = {
    "N": (0, -1),
    "E": (1, 0),
    "S": (0, 1),
    "W": (-1, 0),
}


def path_to_cells(entry: Cell, moves: str) -> list[Cell]:
    """Convert a sequence of move letters into cell coordinate steps.

    Args:
        entry: Starting (x, y) coordinates.
        moves: String of moves ('N', 'E', 'S', 'W').

    Returns:
        A list of (x, y) coordinates traversed along the path.
    """
    cells = [entry]
    x, y = entry
    for m in moves:
        dx, dy = DIRS[m]
        x, y = x + dx, y + dy
        cells.append((x, y))
    return cells


def build_canvas(
    grid: list[list[int]],
    entry: Cell,
    exit_: Cell,
    pattern: set[Cell],
    path: Optional[list[Cell]] = None,
) -> list[list[int]]:
    """Build an expanded 2D grid matrix suitable for character rendering.

    Args:
        grid: Hex-encoded wall grid of the maze.
        entry: Entrance cell coordinate.
        exit_: Exit cell coordinate.
        pattern: Set of coordinates forming the '42' pattern.
        path: Optional list of cell coordinates representing the solution.

    Returns:
        A 2D integer matrix with identifiers for wall, passage, path, etc.
    """
    h, w = len(grid), len(grid[0])
    canvas = [[WALL] * (2 * w + 1) for _ in range(2 * h + 1)]

    for y in range(h):
        for x in range(w):
            cy, cx = 2 * y + 1, 2 * x + 1
            cell = grid[y][x]
            if (x, y) in pattern:
                canvas[cy][cx] = PATTERN
                if (x + 1, y) in pattern:
                    canvas[cy][cx + 1] = PATTERN
                if (x, y + 1) in pattern:
                    canvas[cy + 1][cx] = PATTERN
                continue
            canvas[cy][cx] = OPEN
            if not cell & E:
                canvas[cy][cx + 1] = OPEN
            if not cell & S:
                canvas[cy + 1][cx] = OPEN

    if path:
        for (x1, y1), (x2, y2) in zip(path, path[1:]):
            canvas[2 * y1 + 1][2 * x1 + 1] = PATH
            canvas[y1 + y2 + 1][x1 + x2 + 1] = PATH
        x, y = path[-1]
        canvas[2 * y + 1][2 * x + 1] = PATH

    canvas[2 * entry[1] + 1][2 * entry[0] + 1] = ENTRY
    canvas[2 * exit_[1] + 1][2 * exit_[0] + 1] = EXIT
    return canvas


def bg(code: int) -> str:
    """Format an ANSI 256-color background block string.

    Args:
        code: ANSI 256 color number.

    Returns:
        ANSI escape sequence representing a colored block.
    """
    return f"\033[48;5;{code}m  \033[0m"


WALL_COLOURS = [
    15, 217, 218, 224, 182,
    153, 159, 117, 152,
    157, 121, 158, 115,
    223, 229, 222, 180,
    183, 147, 177, 139,
]

PATH_COLOURS = [
    51, 45, 81, 39, 123,
    46, 50, 82, 118, 154,
    201, 198, 205, 213, 165,
    226, 214, 208, 196, 220,
    93, 129, 141, 135, 171,
]


def render(canvas: list[list[int]],
           wall_colour: int, path_colours: int) -> str:
    """Convert the 2D canvas into a multi-line colorized string.

    Args:
        canvas: 2D integer matrix of elements.
        wall_colour: ANSI code for maze walls.
        path_colours: ANSI code for the solution path.

    Returns:
        Full rendered ASCII canvas string.
    """
    palette = {
        WALL: bg(wall_colour),
        OPEN: "  ",
        PATH: bg(path_colours),
        ENTRY: bg(201),
        EXIT: bg(196),
        PATTERN: bg(244),
    }
    return "\n".join("".join(palette[tile] for tile in row) for row in canvas)
