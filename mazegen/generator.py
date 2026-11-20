"""Maze generation module providing the reusable MazeGenerator class."""

import random
from collections import deque
from typing import Optional

Cell = tuple[int, int]  # (x, y)

N, E, S, W = 1, 2, 4, 8
DX = {N: 0, E: 1, S: 0, W: -1}
DY = {N: -1, E: 0, S: 1, W: 0}
OPPOSITE = {N: S, E: W, S: N, W: E}
LETTER = {N: "N", E: "E", S: "S", W: "W"}

# 42 pattern drawn as 3x5 bitmaps (X = closed cell)
FOUR = [
    "X.X",
    "X.X",
    "XXX",
    "..X",
    "..X",
]
TWO = [
    "XXX",
    "..X",
    "XXX",
    "X..",
    "XXX",
]


class MazeGenerator:
    """Generates perfect and Pac-Man style mazes \
    with customizable parameters."""

    def __init__(
        self,
        width: int,
        height: int,
        entry: Cell,
        exit_: Cell,
        perfect: bool = True,
        seed: Optional[str] = None,
    ) -> None:
        """Initialize the maze generator.

        Args:
            width: Maze width in cells.
            height: Maze height in cells.
            entry: (x, y) coordinates of the entrance.
            exit_: (x, y) coordinates of the exit.
            perfect: True for a perfect maze, False for Pac-Man style.
            seed: Optional random generator seed for reproducibility.
        """
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit_
        self.perfect = perfect
        self.seed: str = (
            seed if seed is not None else "".join(random.choices("NESW", k=16))
        )
        self._rng = random.Random(self.seed)
        self.grid: list[list[int]] = []
        self.pattern: set[Cell] = set()
        self.pattern_fits: bool = True
        self._visited: set[Cell] = set()

    def solve(self) -> str:
        """Find the shortest path from entry to exit using BFS.

        Returns:
            A string containing directions ('N', 'E', 'S', 'W'),
            or an empty string if no valid path exists.
        """
        came_from: dict[Cell, tuple[Cell, str]] = {}
        seen: set[Cell] = {self.entry}
        queue: deque[Cell] = deque([self.entry])

        while queue:
            x, y = queue.popleft()
            if (x, y) == self.exit:
                break
            for d in (N, E, S, W):
                if self.grid[y][x] & d:
                    continue
                nxt = (x + DX[d], y + DY[d])
                if nxt in seen:
                    continue
                seen.add(nxt)
                came_from[nxt] = ((x, y), LETTER[d])
                queue.append(nxt)

        if self.exit not in seen:
            return ""

        moves: list[str] = []
        cell = self.exit
        while cell != self.entry:
            cell, letter = came_from[cell]
            moves.append(letter)
        return "".join(reversed(moves))

    def _unvisited_neighbours(
        self, x: int, y: int
    ) -> list[tuple[int, Cell]]:
        """Find all orthogonally adjacent cells not yet visited during DFS.

        Args:
            x: Current cell X coordinate.
            y: Current cell Y coordinate.

        Returns:
            A list of tuples with direction flag and neighbor coordinate.
        """
        found: list[tuple[int, Cell]] = []
        for d in (N, E, S, W):
            nx, ny = x + DX[d], y + DY[d]
            if (
                0 <= nx < self.width
                and 0 <= ny < self.height
                and (nx, ny) not in self._visited
            ):
                found.append((d, (nx, ny)))
        return found

    def _carve(self, x: int, y: int, d: int) -> None:
        """Carve an open passage between (x, y) \
        and its neighbour in direction d.

        Args:
            x: Cell X coordinate.
            y: Cell Y coordinate.
            d: Direction bit (N, E, S, or W).
        """
        nx, ny = x + DX[d], y + DY[d]
        self.grid[y][x] &= ~d
        self.grid[ny][nx] &= ~OPPOSITE[d]

    def _place_pattern(self) -> None:
        """Position the fully enclosed '42' pattern \
        in the center of the grid."""
        self.pattern = set()
        self.pattern_fits = True
        if self.width < 9 or self.height < 7:
            self.pattern_fits = False
            return
        ox = (self.width - 7) // 2
        oy = (self.height - 5) // 2
        for row in range(5):
            line = FOUR[row] + "." + TWO[row]
            for col, ch in enumerate(line):
                if ch == "X":
                    self.pattern.add((ox + col, oy + row))
        if self.entry in self.pattern or self.exit in self.pattern:
            self.pattern = set()
            self.pattern_fits = False

    def generate(self) -> None:
        """Generate the maze grid using iterative DFS and optional braiding."""
        self.grid = [[0xF] * self.width for _ in range(self.height)]
        self._place_pattern()
        self._visited = set(self.pattern)

        self._visited.add(self.entry)
        stack: list[Cell] = [self.entry]
        while stack:
            x, y = stack[-1]
            options = self._unvisited_neighbours(x, y)
            if options:
                d, (nx, ny) = self._rng.choice(options)
                self._carve(x, y, d)
                self._visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()

        if not self.perfect:
            self._braid()

    def _is_dead_end(self, x: int, y: int) -> bool:
        """Check if a cell is a dead-end (has exactly three walls closed).

        Args:
            x: Cell X coordinate.
            y: Cell Y coordinate.

        Returns:
            True if the cell has only one passage open, False otherwise.
        """
        if (x, y) in self.pattern:
            return False
        return bin(self.grid[y][x]).count("1") == 3

    def _block_is_open(self, ox: int, oy: int) -> bool:
        """Check whether a 3x3 block of cells is completely open.

        Args:
            ox: Top-left origin X coordinate of the 3x3 block.
            oy: Top-left origin Y coordinate of the 3x3 block.

        Returns:
            True if all interior walls in the 3x3 square are open.
        """
        for dy in range(3):
            for dx in range(3):
                cell = self.grid[oy + dy][ox + dx]
                if dx < 2 and cell & E:
                    return False
                if dy < 2 and cell & S:
                    return False
        return True

    def _would_make_3x3(self, x: int, y: int) -> bool:
        """Verify if opening a wall at (x, y) forms an illegal 3x3 open room.

        Args:
            x: Cell X coordinate.
            y: Cell Y coordinate.

        Returns:
            True if a 3x3 open space is created, False otherwise.
        """
        for ox in range(x - 2, x + 1):
            for oy in range(y - 2, y + 1):
                if ox < 0 or oy < 0:
                    continue
                if ox + 2 >= self.width or oy + 2 >= self.height:
                    continue
                if self._block_is_open(ox, oy):
                    return True
        return False

    def _can_open(self, x: int, y: int, d: int) -> bool:
        """Test if a wall can be safely opened without violating rules.

        Args:
            x: Cell X coordinate.
            y: Cell Y coordinate.
            d: Direction to open.

        Returns:
            True if opening the wall maintains validity, False otherwise.
        """
        nx, ny = x + DX[d], y + DY[d]
        if not (0 <= nx < self.width and 0 <= ny < self.height):
            return False
        if (nx, ny) in self.pattern or (x, y) in self.pattern:
            return False
        if not self.grid[y][x] & d:
            return False
        self._carve(x, y, d)
        bad = self._would_make_3x3(x, y) or self._would_make_3x3(nx, ny)
        self.grid[y][x] |= d
        self.grid[ny][nx] |= OPPOSITE[d]
        return not bad

    def _open_wall(self, x: int, y: int) -> bool:
        """Open a valid wall from cell (x, y) to remove a dead-end.

        Args:
            x: Cell X coordinate.
            y: Cell Y coordinate.

        Returns:
            True if a wall was opened, False if no candidate was valid.
        """
        options = [d for d in (N, E, S, W) if self._can_open(x, y, d)]
        if not options:
            return False
        twins = [d for d in options if self._is_dead_end(x + DX[d], y + DY[d])]
        d = self._rng.choice(twins or options)
        self._carve(x, y, d)
        return True

    def _loops(self) -> int:
        """Calculate independent cycles using edges - vertices + 1.

        Returns:
            Number of independent loops in the navigable region.
        """
        cells = self.width * self.height - len(self.pattern)
        edges = 0
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern:
                    continue
                if not self.grid[y][x] & E and x + 1 < self.width:
                    edges += 1
                if not self.grid[y][x] & S and y + 1 < self.height:
                    edges += 1
        return edges - cells + 1

    def _braid(self) -> None:
        """Transform a perfect maze into a braided Pac-Man board."""
        cells = [(x, y) for y in range(self.height) for x in range(self.width)]
        self._rng.shuffle(cells)
        for x, y in cells:
            if self._is_dead_end(x, y):
                self._open_wall(x, y)
        attempts = 0
        while self._loops() < 2 and attempts < 1000:
            x = self._rng.randrange(self.width)
            y = self._rng.randrange(self.height)
            d = self._rng.choice((N, E, S, W))
            if self._can_open(x, y, d):
                self._carve(x, y, d)
            attempts += 1
