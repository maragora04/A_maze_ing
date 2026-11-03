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


    def solve(self) -> str:
        came_from: dict[Cell, tuple[Cell, str]] = {}
        seen: set[Cell] = {self.entry}
        queue: deque[Cell] = deque([self.entry])

        while queue:
            x, y = queue.popleft()
            if (x, y) == self.exit:
                break
            for d in (N, E, S, W):
                if self.grid[y][x] & d:  # wall closed: can't go
                    continue
                nxt = (x + DX[d], y + DY[d])
                if nxt in seen:
                    continue
                seen.add(nxt)
                came_from[nxt] = ((x, y), LETTER[d])
                queue.append(nxt)

        if self.exit not in seen:
            return ""  # no path found

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


# Open the wall between (x, y) and its neighbour in direction d
    def _carve(self, x: int, y: int, d: int) -> None:
        nx, ny = x + DX[d], y + DY[d]
        self.grid[y][x] &= ~d
        self.grid[ny][nx] &= ~OPPOSITE[d]


# Place 42 in the maze
    def _place_pattern(self) -> None:
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


# Build a perfect or non perfect (pac-man like) 
# maze with an iterative recursive backtracker
# if PERFECT=False add loops and remove dead-ends
    def generate(self) -> None:
        self.grid = [[0xF] * self.width for _ in range(self.height)]
        self._place_pattern()
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

        if not self.perfect:
            self._braid()


# A cell with exactly one opening (3 closed walls)
    def _is_dead_end(self, x: int, y: int) -> bool:
        if (x, y) in self.pattern:
            return False
        return bin(self.grid[y][x]).count("1") == 3


# checks the 12 inner walls of a 3x3 block (2 per row and column)
# A 2x2 or 2x3 open area is allowed, so only a full 3x3 is rejected
    def _block_is_open(self, ox: int, oy: int) -> bool:
        for dy in range(3):
            for dx in range(3):
                cell = self.grid[oy + dy][ox + dx]
                if dx < 2 and cell & E:
                    return False
                if dy < 2 and cell & S:
                    return False
        return True


# is this cell part of a completely open 3x3 block? 
# subject says "corridors can’t be wider than 2 cells", 
# so _braid calls it before keeping any new opening
    def _would_make_3x3(self, x: int, y: int) -> bool:
        for ox in range(x - 2, x + 1):
            for oy in range(y - 2, y + 1):
                if ox < 0 or oy < 0:
                    continue
                if ox + 2 >= self.width or oy + 2 >= self.height:
                    continue
                if self._block_is_open(ox, oy):
                    return True
        return False


# carves the wall, checks both cells for a 3x3 block, 
# then restores both sides of the wall
# Both sides must be restored, or the walls become incoherent
    def _can_open(self, x: int, y: int, d: int) -> bool:
        nx, ny = x + DX[d], y + DY[d]
        if not (0 <= nx < self.width and 0 <= ny < self.height):
            return False                      # outer border stays closed
        if (nx, ny) in self.pattern or (x, y) in self.pattern:
            return False                      # the 42 stays closed
        if not self.grid[y][x] & d:
            return False                      # already open
        self._carve(x, y, d)                  # try it...
        bad = self._would_make_3x3(x, y) or self._would_make_3x3(nx, ny)
        self.grid[y][x] |= d                  # ...and undo it
        self.grid[ny][nx] |= OPPOSITE[d]
        return not bad


    def _open_wall(self, x: int, y: int) -> bool:
        options = [d for d in (N, E, S, W) if self._can_open(x, y, d)]
        if not options:
            return False
        twins = [d for d in options
                 if self._is_dead_end(x + DX[d], y + DY[d])]
        d = self._rng.choice(twins or options)
        self._carve(x, y, d)
        return True


#uses the graph formula edges - cells + 1, which is 0 for a perfect maze (a tree), 
# and the analyzer uses the same one for "independent routes"
    def _loops(self) -> int:
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


# takes the perfect maze the DFS just built 
# and turns it into a playable board with loops and no dead-ends.
    def _braid(self) -> None:
        cells = [(x, y) for y in range(self.height)
                 for x in range(self.width)]
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
