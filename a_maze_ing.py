"""Main entry point for the a_maze_ing application."""

import sys
from maze_render import (
    PATH_COLOURS,
    WALL_COLOURS,
    build_canvas,
    path_to_cells,
    render,
)
from mazegen import MazeGenerator
from parsing import parse_config

RED = "\033[38;5;196m"
GREY = "\033[38;5;245m"
GREEN = "\033[38;5;114m"
MENU = (
    "1. Re-generate a new maze\n"
    "2. Show / Hide the shortest path\n"
    "3. Rotate the wall colours\n"
    "4. Rotate the path colours\n"
    "5. Quit"
)


def write_output(gen: MazeGenerator, path: str) -> None:
    """Write the generated maze to disk in the required format.

    Args:
        gen: The MazeGenerator instance containing the grid and solution.
        path: Destination file path.
    """
    lines = ["".join(format(cell, "X") for cell in row) for row in gen.grid]
    lines.append("")
    lines.append(f"{gen.entry[0]},{gen.entry[1]}")
    lines.append(f"{gen.exit[0]},{gen.exit[1]}")
    lines.append(gen.solve())
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def generate_and_save(gen: MazeGenerator, output: str) -> None:
    """Trigger maze generation, validate pattern display, and save to file.

    Args:
        gen: The MazeGenerator instance to execute.
        output: Destination output filename.
    """
    gen.generate()
    if not gen.pattern_fits:
        print(
            f"{RED}Error: maze too small (or entry/exit in the way) "
            "to display the '42' pattern"
        )
    try:
        write_output(gen, output)
    except OSError as e:
        print(f"{RED}Error: cannot write '{output}': {e}")


def main() -> None:
    """Parse arguments, run generation, and start terminal interaction loop."""
    if len(sys.argv) != 2:
        print(f"{RED}Usage: python3 a_maze_ing.py config.txt")
        sys.exit(1)

    try:
        cfg = parse_config(sys.argv[1])
        gen = MazeGenerator(
            cfg["width"],
            cfg["height"],
            cfg["entry"],
            cfg["exit"],
            cfg["perfect"],
            cfg["seed"],
        )
    except (OSError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    generate_and_save(gen, cfg["output"])
    show_path = False
    colour_idx = 0
    colour_idx2 = 0

    while True:
        moves = gen.solve()
        path = path_to_cells(cfg["entry"], moves) if show_path else None
        canvas = build_canvas(
            gen.grid, cfg["entry"], cfg["exit"], gen.pattern, path
        )
        print(render(canvas, WALL_COLOURS[colour_idx],
                     PATH_COLOURS[colour_idx2]))
        print("=== A-Maze-ing ===")
        print(f"{GREY}{MENU}")

        try:
            choice = input(f"{GREEN}Choice? (1-5): ".strip())
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if choice == "1":
            generate_and_save(gen, cfg["output"])
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            colour_idx = (colour_idx + 1) % len(WALL_COLOURS)
        elif choice == "4":
            colour_idx2 = (colour_idx2 + 1) % len(PATH_COLOURS)
        elif choice == "5":
            break
        else:
            print(f"{RED}Invalid choice, enter 1 - 5.")


if __name__ == "__main__":
    main()
