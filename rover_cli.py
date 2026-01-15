#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple, Optional


# ----------------------------
# Domain model: Rover
# ----------------------------
HEADINGS = ["N", "E", "S", "W"]
DIR_VECTORS = {
    "N": (0, 1),
    "E": (1, 0),
    "S": (0, -1),
    "W": (-1, 0),
}


@dataclass
class Rover:
    x: int = 0
    y: int = 0
    heading: str = "N"

    def _heading_index(self) -> int:
        try:
            return HEADINGS.index(self.heading)
        except ValueError:
            raise ValueError(f"Invalid heading: {self.heading}")

    def turn_left(self) -> None:
        i = self._heading_index()
        self.heading = HEADINGS[(i - 1) % len(HEADINGS)]

    def turn_right(self) -> None:
        i = self._heading_index()
        self.heading = HEADINGS[(i + 1) % len(HEADINGS)]

    def move_forward(self, steps: int = 1) -> None:
        dx, dy = DIR_VECTORS[self.heading]
        self.x += dx * steps
        self.y += dy * steps

    def move_back(self, steps: int = 1) -> None:
        dx, dy = DIR_VECTORS[self.heading]
        self.x -= dx * steps
        self.y -= dy * steps

    def reset(self) -> None:
        self.x, self.y, self.heading = 0, 0, "N"

    def set_pos(self, x: int, y: int) -> None:
        self.x, self.y = x, y

    def set_heading(self, heading: str) -> None:
        heading = heading.upper()
        if heading not in HEADINGS:
            raise ValueError(f"Heading must be one of {HEADINGS}, got {heading}")
        self.heading = heading

    def status_str(self) -> str:
        return f"({self.x}, {self.y}) heading={self.heading}"


# ----------------------------
# Parser
# ----------------------------
class ParseError(Exception):
    pass


def parse_line(line: str) -> Tuple[str, List[str]]:
    """
    Turn raw input into (command_name, args).
    - Strip whitespace
    - Uppercase command name
    - Keep args as strings (handlers validate/convert)
    """
    line = line.strip()
    if not line:
        raise ParseError("Empty command")

    parts = line.split()
    cmd = parts[0].upper()
    args = parts[1:]
    return cmd, args


def parse_int_arg(args: List[str], idx: int, default: Optional[int] = None) -> int:
    if idx >= len(args):
        if default is None:
            raise ParseError("Missing integer argument")
        return default
    try:
        return int(args[idx])
    except ValueError:
        raise ParseError(f"Expected integer, got: {args[idx]}")


# ----------------------------
# Dispatcher / command registry
# ----------------------------
Handler = Callable[[Rover, List[str]], str]


def make_handlers() -> Dict[str, Handler]:
    def h_help(_: Rover, __: List[str]) -> str:
        return (
            "Commands:\n"
            "  F [n] | FORWARD [n]    move forward n steps (default 1)\n"
            "  B [n] | BACK [n]       move back n steps (default 1)\n"
            "  L | LEFT               turn left 90°\n"
            "  R | RIGHT              turn right 90°\n"
            "  STATUS                 show current position and heading\n"
            "  GOTO x y [H]           set position to (x,y) and optional heading H in {N,E,S,W}\n"
            "  RESET                  reset to (0,0) heading N\n"
            "  QUIT | EXIT            exit the program\n"
        )

    def h_status(rover: Rover, _: List[str]) -> str:
        return rover.status_str()

    def h_left(rover: Rover, _: List[str]) -> str:
        rover.turn_left()
        return rover.status_str()

    def h_right(rover: Rover, _: List[str]) -> str:
        rover.turn_right()
        return rover.status_str()

    def h_forward(rover: Rover, args: List[str]) -> str:
        n = parse_int_arg(args, 0, default=1)
        if n < 0:
            raise ParseError("Steps must be positive (got negative value)")
        rover.move_forward(n)
        return rover.status_str()

    def h_back(rover: Rover, args: List[str]) -> str:
        n = parse_int_arg(args, 0, default=1)
        if n < 0:
            raise ParseError("Steps must be positive (got negative value)")
        rover.move_back(n)
        return rover.status_str()

    def h_reset(rover: Rover, _: List[str]) -> str:
        rover.reset()
        return rover.status_str()

    def h_goto(rover: Rover, args: List[str]) -> str:
        if len(args) < 2:
            raise ParseError("Usage: GOTO x y [H]")
        x = parse_int_arg(args, 0)
        y = parse_int_arg(args, 1)
        rover.set_pos(x, y)
        if len(args) >= 3:
            try:
                rover.set_heading(args[2])
            except ValueError as e:
                raise ParseError(str(e))
        return rover.status_str()

    # Registry with aliases
    return {
        "HELP": h_help,
        "?": h_help,

        "STATUS": h_status,

        "L": h_left,
        "LEFT": h_left,

        "R": h_right,
        "RIGHT": h_right,

        "F": h_forward,
        "FORWARD": h_forward,
        "MOVE": h_forward,     # alias if you want

        "B": h_back,
        "BACK": h_back,

        "RESET": h_reset,

        "GOTO": h_goto,
    }


# ----------------------------
# REPL loop
# ----------------------------
def repl() -> None:
    rover = Rover()
    handlers = make_handlers()

    print("Rover CLI. Type HELP for commands.")
    print(rover.status_str())

    while True:
        try:
            line = input("rover> ")
        except EOFError:
            print("\nbye")
            return
        except KeyboardInterrupt:
            print("\n(Interrupted) Type EXIT to quit.")
            continue

        line = line.strip()
        if not line:
            continue

        # Built-in exit commands (could also be in handlers)
        if line.upper() in ("QUIT", "EXIT"):
            print("bye")
            return

        try:
            cmd, args = parse_line(line)
            handler = handlers.get(cmd)
            if handler is None:
                print(f"Unknown command: {cmd}. Type HELP.")
                continue
            out = handler(rover, args)
            print(out)
        except ParseError as e:
            print(f"Parse error: {e}")
        except Exception as e:
            # Domain errors etc.
            print(f"Error: {e}")


if __name__ == "__main__":
    repl()
