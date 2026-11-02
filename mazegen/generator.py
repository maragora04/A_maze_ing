import random
from typing import Optional
from collections import deque


Cell = tuple[int, int]  # (x, y)

N, E, S, W = 1, 2, 4, 8
DX = {N: 0, E: 1, S: 0, W: -1}
DY = {N: -1, E: 0, S: 1, W: 0}
OPPOSITE = {N: S, E: W, S: N, W: E}
LETTER = {N: "N", E: "E", S: "S", W: "W"}

# 42 drawn as 3x5 bitmaps (X = closed cell)
FOUR = ["X.X",
        "X.X",
        "XXX",
        "..X",
        "..X"]
TWO = ["XXX",
       "..X",
       "XXX",
       "X..",
       "XXX"]


class MazeGenerator:
    def __init__(
        self,
        width: int,
        height: int,
        entry: Cell,
        exit_: Cell,
        perfect: bool = True,
        seed: Optional[int] = None,
    ) -> None:
        # validate, then store everything
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit_
        self.perfect = perfect
        self.seed = seed if seed is not None else random.randrange(2**32)
        self._rng = random.Random(self.seed)
        self.grid: list[list[int]] = []
        self.pattern: set[Cell] = set()

    # next steps: carve passages (DFS), place 42 pattern

    def solve(self) -> str:
        came_from: dict[Cell, tuple[Cell, str]] = {}
        seen: set[Cell] = {self.entry}
        queue: deque[Cell] = deque([self.entry])

        while queue:
            x, y = queue.popleft()
            if (x, y) == self.exit:
                break
            for d in (N, E, S, W):
                if self.grid[y][x] & d:       # wall closed: can't go
                    continue
                nxt = (x + DX[d], y + DY[d])
                if nxt in seen:
                    continue
                seen.add(nxt)
                came_from[nxt] = ((x, y), LETTER[d])
                queue.append(nxt)

        if self.exit not in seen:
            return ""                          # no path found

        moves: list[str] = []
        cell = self.exit
        while cell != self.entry:
            cell, letter = came_from[cell]
            moves.append(letter)
        return "".join(reversed(moves))

    def _unvisited_neighbours(
        self, x: int, y: int
    ) -> list[tuple[int, Cell]]:
        # Return (direction, (nx, ny)) for each unvisited neighbour
        found: list[tuple[int, Cell]] = []
        for d in (N, E, S, W):
            nx, ny = x + DX[d], y + DY[d]
            if (0 <= nx < self.width and 0 <= ny < self.height
                    and (nx, ny) not in self._visited):
                found.append((d, (nx, ny)))
        return found

    def _carve(self, x: int, y: int, d: int) -> None:
        # Open the wall between (x, y) and its neighbour in direction d
        nx, ny = x + DX[d], y + DY[d]
        self.grid[y][x] &= ~d
        self.grid[ny][nx] &= ~OPPOSITE[d]


    def _place_pattern(self) -> None: # place 42 in the maze
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
        # Build a perfect maze with an iterative recursive backtracker
        self.grid = [[0xF] * self.width for _ in range(self.height)]  # the 42 cells go here
        self.grid = [[0xF] * self.width for _ in range(self.height)]
        self._place_pattern()
        self._visited: set[Cell] = set(self.pattern) 
        self._visited: set[Cell] = set(self.pattern)

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
