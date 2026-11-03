import sys
from typing import Any
from parsing import parse_config

from mazegen import MazeGenerator
from maze_render import (
    WALL_COLOURS, 
    PATH_COLOURS, 
    build_canvas, 
    path_to_cells, 
    render,
)

# colors
RED = "\033[38;5;196m"	
GREY = "\033[38;5;245m"
GREEN = "\033[38;5;114m"
MENU = (
    "1. Re-generate a new maze\n"
    "2. Show / Hide the shortest path\n"
    "3. Rotate the wall colours\n"
    "4. Rotate the path colours\n"
    "5. Quit" )


def write_output(gen: MazeGenerator, path: str) -> None:
    lines = ["".join(format(cell, "X") for cell in row)
             for row in gen.grid]
    lines.append("")                                  # empty line
    lines.append(f"{gen.entry[0]},{gen.entry[1]}")    # entry x,y
    lines.append(f"{gen.exit[0]},{gen.exit[1]}")      # exit x,y
    lines.append(gen.solve())                         # shortest path
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def generate_and_save(gen: MazeGenerator, output: str) -> None:
    gen.generate()
    if not gen.pattern_fits:
        print(f"{RED}Error: maze too small (or entry/exit in the way) "
              "to display the '42' pattern")
    try:
        write_output(gen, output)
    except OSError as e:
        print(f"{RED}Error: cannot write '{output}': {e}")


def main() -> None:
    if len(sys.argv) != 2:
        print(f"{RED}Usage: python3 a_maze_ing.py config.txt")
        sys.exit(1)

    try:
        cfg = parse_config(sys.argv[1])
        gen = MazeGenerator(cfg["width"], cfg["height"],
                            cfg["entry"], cfg["exit"],
                            cfg["perfect"], cfg["seed"])
    except (OSError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    generate_and_save(gen, cfg["output"])
    show_path = False
    colour_idx = 0
    colour_idx2 = 0

 # MENU
    while True:
        moves = gen.solve()  # e.g. "ESSEE"
        path = path_to_cells(cfg["entry"], moves) if show_path else None
        canvas = build_canvas(gen.grid, cfg["entry"], cfg["exit"],
                              gen.pattern, path)
        print(render(canvas, WALL_COLOURS[colour_idx], PATH_COLOURS[colour_idx2]))
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
