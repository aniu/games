# Rover CLI - 2D Robot Simulator

A command-line application for controlling a robot rover in a 2D plane. The rover can move forward/backward, turn left/right, and navigate to specific coordinates with directional control.

## Files

- **`rover_cli.py`** - Main application file containing:
  - `Rover` class: Domain model for the robot with position (x, y) and heading (N, E, S, W)
  - Command parser: Parses user input into commands and arguments
  - Command handlers: Implements all rover commands
  - REPL loop: Interactive command-line interface

- **`test_rover_cli.py`** - Comprehensive test suite with 37 tests covering:
  - Rover domain model functionality
  - Parser functionality
  - All command handlers and aliases
  - Edge cases and error handling
  - Complex command sequences

## Features

- Move forward/backward in the current heading direction
- Turn left/right (90° rotations)
- Set position and heading directly
- Reset to origin (0, 0) facing North
- Interactive command-line interface with helpful error messages
- Multiple command aliases for convenience

## Requirements

- Python 3.6+ (uses type hints and dataclasses)

## Basic Usage

### Running the CLI Application

```bash
python rover_cli.py
```

Or make it executable and run directly:
```bash
chmod +x rover_cli.py
./rover_cli.py
```

### Running Tests

```bash
python test_rover_cli.py
```

Or using unittest module:
```bash
python -m unittest test_rover_cli.py
```

## Command Reference

### Movement Commands

| Command | Alias | Description | Example |
|---------|-------|-------------|---------|
| `F [n]` | `FORWARD`, `MOVE` | Move forward n steps (default: 1) | `F 5` |
| `B [n]` | `BACK` | Move back n steps (default: 1) | `B 3` |

### Rotation Commands

| Command | Alias | Description | Example |
|---------|-------|-------------|---------|
| `L` | `LEFT` | Turn left 90° | `L` |
| `R` | `RIGHT` | Turn right 90° | `R` |

### Position Commands

| Command | Description | Example |
|---------|-------------|---------|
| `STATUS` | Show current position and heading | `STATUS` |
| `GOTO x y [H]` | Set position to (x, y) with optional heading | `GOTO 10 20 E` |
| `RESET` | Reset to (0, 0) heading N | `RESET` |

### Utility Commands

| Command | Alias | Description | Example |
|---------|-------|-------------|---------|
| `HELP` | `?` | Show help message | `HELP` |
| `QUIT` | `EXIT` | Exit the program | `QUIT` |

## Example Session

```
Rover CLI. Type HELP for commands.
(0, 0) heading=N
rover> F 3
(0, 3) heading=N
rover> R
(0, 3) heading=E
rover> FORWARD 2
(2, 3) heading=E
rover> L
(2, 3) heading=N
rover> STATUS
(2, 3) heading=N
rover> GOTO -5 -10 S
(-5, -10) heading=S
rover> RESET
(0, 0) heading=N
rover> QUIT
bye
```

## Coordinate System

- **X-axis**: Positive values go East, negative values go West
- **Y-axis**: Positive values go North, negative values go South
- **Headings**: N (North), E (East), S (South), W (West)

## Notes

- Commands are case-insensitive
- Multiple spaces are handled correctly
- Invalid commands show helpful error messages
- Use `Ctrl+C` to interrupt (type EXIT to quit)
- Use `Ctrl+D` (EOF) to exit gracefully
