*This project has been created as part of the 42 curriculum by mamendes, andmigue.*

## Description
**A-Maze-ing** is a Python application designed to generate, analyze, solve, and visually render 2D mazes. The project supports two primary generation modes:
1. **Perfect Maze (`PERFECT=True`)**: Generates a standard labyrinth with a unique path between any two points (spanning tree, zero loops).
2. **Pac-Man Style Board (`PERFECT=False`)**: A fully connected, playable board featuring multiple independent loops, reachable corners and center for game assets, and zero (or minimal) dead-ends (braided board).

The generator embeds a solid "42" pattern formed by fully enclosed cells in the center of the grid, provided the maze dimensions allow it (at least 9x7).

---

## Instructions

### Dependencies & Setup
The project requires Python 3.10+ and standard build/linting tools.

```bash
# Install dependencies (flake8, mypy, build)
make install
```

### Running the Program
Execute the main program with a configuration file:
```bash
make run
# or directly:
python3 a_maze_ing.py config.txt
```

### Interactive Controls
Once launched, the terminal displays an interactive menu:
- `1`: Re-generate a maze with the current settings.
- `2`: Toggle show/hide for the shortest solution path.
- `3`: Rotate wall colors (ANSI 256-color palette).
- `4`: Rotate path colors.
- `5`: Exit application.

### Verification & Linting
```bash
make lint         # Runs flake8 and mandatory mypy checks
make lint-strict  # Runs mypy in strict mode
make clean        # Removes build artifacts, dist/, and python caches
```

### Building the Reusable Wheel
```bash
make build        # Builds wheel/sdist and copies mazegen-*.whl to project root
```

---

## Configuration File Format
The configuration file accepts one `KEY=VALUE` entry per line. Empty lines and lines beginning with `#` are ignored as comments.

| Key | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `WIDTH` | Integer | Maze width (cells, must be > 0) | `WIDTH=20` |
| `HEIGHT` | Integer | Maze height (cells, must be > 0) | `HEIGHT=15` |
| `ENTRY` | Coordinates (`x,y`) | Starting position inside maze bounds | `ENTRY=0,0` |
| `EXIT` | Coordinates (`x,y`) | Target position inside maze bounds | `EXIT=19,14` |
| `OUTPUT_FILE` | String | Target destination for hexadecimal maze export | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Boolean | `True` for unique path; `False` for Pac-Man board | `PERFECT=False` |
| `SEED` | String/Number (Optional) | Reproducibility seed for the RNG | `SEED=42` |

---

## Generation Algorithm & Technical Choices

### Choice of Algorithm: Iterative Recursive Backtracker (DFS)
We chose a depth-first search (DFS) with an explicit stack for the base maze generation.
- **Why this algorithm?** DFS produces long, winding corridors with high bottleneck complexity and minimal short branching, which creates engaging and challenging mazes. Implementing it iteratively with a stack avoids Python's recursion limit on large grids.
- **Braid Post-Processing**: For `PERFECT=False`, the generated tree is post-processed by eliminating dead-ends (cells with 3 walls closed) and ensuring at least two independent loops (`edges - nodes + 1 >= 2`).
- **3x3 Open Area Safeguard**: The subject forbids open areas wider than 2 cells (e.g. 3x3 open blocks). Before opening any wall during braiding, candidate walls are verified to ensure no full 3x3 grid of interior passages is formed.

### Solver: Breadth-First Search (BFS)
The `solve()` method executes a BFS traversal from `ENTRY` to `EXIT`. Because BFS explores cell distances uniformly, it guarantees finding the shortest path in terms of steps.

---

## Code Reusability: `mazegen` Module
The core generation engine is isolated in the `mazegen` package and can be installed via `pip`:

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Usage Example
```python
from mazegen import MazeGenerator

# 1. Instantiate generator (width, height, entry, exit, perfect, seed)
gen = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit_=(19, 14),
    perfect=False,
    seed="my_custom_seed"
)

# 2. Generate the maze
gen.generate()

# 3. Access internal structure
# grid is a 2D list of bitmasked integers (North=1, East=2, South=4, West=8)
print("Grid rows:", len(gen.grid))
print("Top-left cell walls:", hex(gen.grid[0][0]))

# 4. Access solution
path_letters = gen.solve()  # e.g., "EESSEEN..."
print("Solution steps:", path_letters)
```

---

## Team & Project Management

### Roles & Responsibilities
- **mamendes**: Implementation of the parsing engine, file input/output validation, error handling, packaging setup (`pyproject.toml`, wheel creation), and `Makefile`.
- **andmigue**: Core algorithm design (`mazegen`), DFS generation, 3x3 open space prevention, braid loop generation, BFS solver, and ANSI terminal rendering.

### Anticipated Planning vs. Evolution
- **Phase 1**: Configuration file parsing and data structures definition.
- **Phase 2**: Maze generation via DFS and hexadecimal wall encoding matching subject bit values.
- **Phase 3**: Integration of the mandatory "42" pattern and braiding algorithm for Pac-Man mode.
- **Phase 4**: Terminal visual interface, interactive loop, color alternation, and packaging into a standalone wheel.
- **Evolution**: The initial braid algorithm created occasional 3x3 voids, which required adding an explicit geometric validator (`_would_make_3x3`) before opening candidate walls.

### Retrospective & Tools
- **What worked well**: Modularity between parsing, core generation (`mazegen`), and rendering enabled independent testing and validation against `maze_analyzer.py`.
- **What could be improved**: Adding automated unit tests (`pytest`) covering invalid config edges.
- **Tools used**: `Git`, `Python 3.10+`, `flake8`, `mypy`, `build`.

---

## Resources & AI Usage
- **References**:
  - *Jamis Buck - "Mazes for Programmers"* (Graph algorithms, DFS, Braid mazes).
  - Python PEP 257 (Docstring conventions) and PEP 484 (Type Hints).
  - Graph Theory: Spanning Trees and Cycle rank (`Edges - Vertices + Components`).
- **AI Usage**:
  - AI was utilized as an architectural sounding board to discuss dead-end pruning algorithms without creating 3x3 open areas.
  - Assisted in designing the ANSI color palette tuples and reviewing PEP 257 compliance across modules. All generated code and algorithms were thoroughly analyzed, adapted, and tested by team members.
