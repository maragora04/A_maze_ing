## The generator does four jobs:

Build a perfect maze (DFS).
Keep the "42" out of the way.
If PERFECT=False, braid the maze (loops, no dead-ends).
Solve it (BFS).
0. The data everything rests on
python
N, E, S, W = 1, 2, 4, 8

Each cell is one number whose 4 bits are its walls (1 = closed). 0xF = 1111 = all four closed. B = 1011 means N, E and W closed, so only S is open.

grid[y][x] is row first, then column.
Moving in direction d from (x, y) goes to (x + DX[d], y + DY[d]). For example, DY[N] = -1, because row 0 is the top.
Coherence rule: a wall between two cells must be recorded on both. _carve is the only function that opens walls, and it clears the bit on both sides:
python
self.grid[y][x] &= ~d              # my wall in direction d
self.grid[ny][nx] &= ~OPPOSITE[d]  # the neighbour's wall facing me

&= ~d means "force this bit to 0". Because every opening goes through this function, maze_analyzer.py finds nothing incoherent.

1. generate(): iterative DFS
python

```
self.grid = [[0xF] * self.width for _ in range(self.height)]   # everything closed
self._place_pattern()
self._visited = set(self.pattern)                              # 42 cells count as "visited"
self._visited.add(self.entry)
stack = [self.entry]
while stack:
    x, y = stack[-1]                                # look at the top, don't remove it
    options = self._unvisited_neighbours(x, y)
    if options:
        d, (nx, ny) = self._rng.choice(options)     # random unvisited neighbour
        self._carve(x, y, d)                        # knock the wall down
        self._visited.add((nx, ny))
        stack.append((nx, ny))                      # go there
    else:
        stack.pop()                                 # dead end: backtrack
```

The stack is the trail you walked. You keep moving to a random unvisited neighbour. When a cell has none left, you pop it and fall back to the previous cell, which may still have unvisited neighbours. That's the "backtracker".

A real trace on a 3x2 maze (seed "ABC"; I ran your code and printed each step):

```
step	at	unvisited options	carves	grid (row 0 / row 1)
start	(0,0)		 FFF / FFF
1	(0,0)	E, S	S → (0,1)	BFF / EFF
2	(0,1)	E	E → (1,1)	BFF / C7F
3	(1,1)	N, E	E → (2,1)	BFF / C57
4	(2,1)	N	N → (2,0)	BFB / C56
5	(2,0)	W	W → (1,0)	BD3 / C56
```

After step 5 nothing is left, so six pops empty the stack and the loop ends. Look at step 1: carving S turned (0,0) into B (S bit cleared) and (0,1) into E (its N bit cleared). That's _carve doing both sides. The result:

```
#######
# #   #
# ### #
#     #
#######
```

entry (0,0) top-left, exit (2,1) bottom-right
solution: S, E, E

## Why the result is a perfect maze:

A cell is only ever entered from an unvisited state, so it is connected exactly once. N cells and N-1 passages give a tree: one path between any two cells, no loops.
The DFS starts at the entry and keeps going until every reachable cell has been visited, so everything is connected.
Cells in _visited from the start (the "42") are never entered, so they stay F.
Why a stack instead of recursion? Recursion depth would reach about W*H, and Python's default limit is 1000, so a 40x30 maze would crash.

Determinism: _unvisited_neighbours always lists directions in the order N, E, S, W, and self._rng.choice picks from that list. Same seed plus same order gives the same maze. If you reorder that tuple, the same seed produces a different maze.

Style of mazes: DFS carves long winding corridors with few branches and a long solution. Prim's or Kruskal's give shorter, branchier mazes. That's a nice README point for "why this algorithm".

2. _place_pattern(): the "42"

FOUR and TWO are 3x5 bitmaps. Each row is FOUR[row] + "." + TWO[row], so the drawing is 3 + 1 (gap) + 3 = 7 columns by 5 rows.

```
python
ox = (self.width - 7) // 2      # left edge so it's centred
oy = (self.height - 5) // 2     # top edge
```

Each "X" becomes (ox + col, oy + row) in self.pattern. The guards:

width < 9 or height < 7 means no room for a 1-cell margin, so the pattern is skipped and pattern_fits = False (that's the error message in main).
If the entry or exit lands inside the pattern, it's dropped for the same reason.
3. _braid(): perfect maze to Pac-Man board

_is_dead_end: bin(cell).count("1") == 3 counts closed walls. Three closed means one opening. Pattern cells are excluded.

_can_open(x, y, d) is the gatekeeper. It refuses when:

the neighbour is outside the grid (the border stays closed),
either cell is part of the "42",
the wall is already open,
opening it would create a 3x3 open area.

The last check is a try, test, undo. It carves the wall, asks _would_make_3x3 for both cells, then restores both sides (|= d and |= OPPOSITE[d]). The "would" in the name is why the wall has to be open for a moment, because you can't test the result otherwise.

_would_make_3x3(x, y): a 3x3 block containing (x, y) can start at any (ox, oy) with ox in x-2..x and oy in y-2..y, which is 9 candidates. The continue lines skip blocks that stick out of the grid.

_block_is_open(ox, oy): inside a 3x3 block there are 12 inner walls (2 per row x 3 rows, plus 2 per column x 3 columns). Looking only at each cell's E (when dx < 2) and S (when dy < 2) covers all 12 exactly once. Any closed one means the block isn't open. A 2x2 or 2x3 open area passes, because the subject allows those.

_open_wall(x, y) opens one safe wall from a dead-end. It prefers twins: neighbours that are themselves dead-ends, so one hole fixes two of them.

_braid() itself:

It shuffles all cells (so the result isn't biased toward the top-left) and, for each one that is still a dead-end when its turn comes, calls _open_wall. The re-check matters, because an earlier opening may already have fixed it.
_loops() uses the graph formula edges - cells + 1, which is 0 for a tree. If there are fewer than 2 loops (tiny mazes), it opens random safe walls until there are 2, with a cap of 1000 attempts so it can never loop forever.

## Why it stays valid:

It only removes walls, so connectivity can't break and no new dead-end can appear.
A dead-end may stay if every candidate wall is unsafe. That's rare, and the analyzer tolerates a couple.
4. solve(): BFS
python
```
queue = deque([entry]); seen = {entry}; came_from = {}
while queue:
    x, y = queue.popleft()           # FIFO: oldest (closest) first
    if (x, y) == exit: break
    for d in (N, E, S, W):
        if self.grid[y][x] & d: continue    # closed wall, can't pass
        ...
        came_from[nxt] = ((x, y), LETTER[d])
```

Why shortest: a FIFO queue explores cells in order of distance, so the first time it reaches the exit, no shorter route exists. This is also why it works on the braided maze with loops, where DFS wouldn't guarantee the shortest.
seen prevents re-visiting, otherwise loops would make it run forever.
came_from stores for each cell where you came from and which letter. You can't know the path while searching, only after reaching the exit. So you walk back from the exit to the entry collecting letters and reverse them. That's the string at the end of maze.txt.
No bounds check is needed, because the outer wall bits are never cleared.

Cost: generation and BFS are both O(W x H). Every cell is pushed and popped once, with 4 neighbour checks.

The one random source

The DFS choice, the braid shuffle and the extra-loop attempts all use self._rng, the generator seeded from self.seed. That's why one seed reproduces a whole maze.

## Things the evaluator could ask, all explained here: 

1. Why can't the DFS create a loop, and why is every cell reachable?

No loops. The DFS only carves toward an unvisited neighbour, and the moment it carves, that neighbour becomes visited. So every cell except the entry gets exactly one carved passage, the one that first reached it. A loop would need a second passage into a cell that is already visited, and the code never does that.

In numbers: N cells get N-1 passages, and a connected structure like that is a tree (no cycles). I checked it on a 20x15 maze: 280 cells (the "42" excluded) and 279 open passages.

python
```
g = MazeGenerator(20, 15, (0, 0), (19, 14), True, "x")
g.generate()
print(g._loops())    # 0 -> edges - cells + 1 = 0 means a tree
```

Everything is reachable. A cell is popped only when all its neighbours are visited. When the stack is finally empty, no visited cell touches an unvisited one. If some cell were still unvisited, then since the grid is one connected block, a path from the entry to it would have to cross from visited to unvisited somewhere, which contradicts that. Each visited cell was reached by carving from an earlier visited one, so all of them connect back to the entry.

The one exception is the "42": it's marked visited beforehand and stays closed. That's why the pattern keeps a margin, so it can't cut the grid in two.

In one sentence: we only ever carve into a cell we haven't visited yet, so there are no loops, and we don't stop until no visited cell has an unvisited neighbour, so nothing is left out.

2. What does the stack contain?

The stack is the route from the entry to where you are now. The top is your current cell. It isn't "all the visited cells", because that's the separate set _visited.

Here is a real run on a 3x3 maze (seed "a"):

action	stack afterwards
```
carve S, E, S, E, N, N, W (walking forward)	[(0,0),(0,1),(1,1),(1,2),(2,2),(2,1),(2,0),(1,0)]
POP (1,0): no unvisited neighbours	[... (2,2),(2,1),(2,0)]
POP (2,0), POP (2,1), POP (2,2)	[(0,0),(0,1),(1,1),(1,2)]
carve W from (1,2) to (0,2)	[(0,0),(0,1),(1,1),(1,2),(0,2)]
POP (0,2), then pops back to the start	[]
```

The interesting moment is the four pops in the middle. The corridor ran into a dead end at (1,0), so the stack walks it backwards until it reaches (1,2), which still had an unvisited neighbour (0,2). From there it starts a new branch. That's what "backtracking" means, and it's where the side branches and dead-ends of the maze come from.

Popped cells stay in _visited, so they're never carved into again.

In one sentence: the stack is the path back to the entry, and popping is stepping back along it to the nearest cell that still has somewhere new to go.

3. Why does _carve clear a bit on both cells?

Each cell stores only its own four walls, so a wall between two neighbours exists in two places. If you clear only one, the data contradicts itself:

```
A = (0,0), B = (1,0)
only A cleared:  A=D  B=F      A says "east is open", B says "west is closed"
both cleared:    A=D  B=7      consistent
```

What breaks when they disagree:

The subject forbids it ("each neighbouring cell must have the same wall").
maze_analyzer.py checks it, and its coherence line would stop saying OK.
BFS reads grid[y][x] & d from whichever cell it is standing on, so a route could work in one direction but not the other.
It's also why the renderer can look only at E and S. That's only valid because the opposite side always matches.

You can see it yourself by commenting out the second line of _carve and running the analyzer.

In one sentence: a wall belongs to two cells, so both must agree, and _carve is the single place that writes both.

4. Why does _can_open undo its test?

To check whether opening a wall would create a 3x3 room, the wall has to actually be open while you look at the grid. But _can_open is only a question ("is this allowed?"), not an action. The decision about which wall to open happens later, in _open_wall:

python
```
options = [d for d in (N, E, S, W) if self._can_open(x, y, d)]   # asks about up to 4 walls
...
d = self._rng.choice(twins or options)                           # chooses ONE
self._carve(x, y, d)                                             # opens only that one
```

If _can_open didn't restore the wall:

Testing 4 directions would leave all 4 walls open, instead of one.
A wall that fails the 3x3 test would stay open, and that is exactly the 3x3 room we're trying to avoid.
The "choose one" step would do nothing, because everything is already open.

Think of trying on a jacket in a shop: you wear it to check the fit, then take it off before you decide. Both sides must be restored (|= d and |= OPPOSITE[d]), for the same reason as in question 3.

In one sentence: it opens the wall only to look at the result, then closes it again, so that asking never changes the maze.

5. Why BFS and not DFS for the solution?

The subject wants the shortest valid path. In a perfect maze there's only one path, so any search would find it. But the braided maze has loops, so there are several routes, and DFS returns the first one it stumbles on, not the shortest.

Smallest example: a fully open 2x2 area.

```
(0,0) (1,0)
(0,1) (1,1)       from (0,0) to (1,0):
                  direct route: E       (1 step)
                  DFS trying S first: S, E, N   (3 steps, valid but not shortest)
```

BFS uses a first-in-first-out queue, so it finishes every cell at distance 1 before any cell at distance 2, and so on. The first time it reaches the exit, no shorter route can exist. If two routes tie for shortest, you get one of them, which is fine because the subject asks for a shortest path.

Two supporting details:

seen stops it from revisiting cells (otherwise loops would make it cycle).
came_from remembers where each cell was reached from, and the BFS walks backwards from the exit through it and reverses the letters. You can't know the path while searching, only after you've reached the exit.

In one sentence: BFS explores outward in layers, so the first time it touches the exit is by a shortest route, which matters now that the braided maze has loops.