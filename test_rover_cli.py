#!/usr/bin/env python3
"""
Test suite for the Rover CLI application.
Tests all commands and edge cases.
"""
import unittest
from io import StringIO
import sys
from rover_cli import Rover, ParseError, parse_line, make_handlers


class TestRover(unittest.TestCase):
    """Test the Rover domain model."""

    def test_initial_state(self):
        rover = Rover()
        self.assertEqual(rover.x, 0)
        self.assertEqual(rover.y, 0)
        self.assertEqual(rover.heading, "N")
        self.assertEqual(rover.status_str(), "(0, 0) heading=N")

    def test_move_forward_north(self):
        rover = Rover()
        rover.move_forward()
        self.assertEqual(rover.x, 0)
        self.assertEqual(rover.y, 1)
        self.assertEqual(rover.heading, "N")

    def test_move_forward_multiple_steps(self):
        rover = Rover()
        rover.move_forward(5)
        self.assertEqual(rover.x, 0)
        self.assertEqual(rover.y, 5)

    def test_move_back(self):
        rover = Rover()
        rover.move_forward(3)
        rover.move_back(1)
        self.assertEqual(rover.x, 0)
        self.assertEqual(rover.y, 2)

    def test_turn_left(self):
        rover = Rover()
        rover.turn_left()
        self.assertEqual(rover.heading, "W")
        rover.turn_left()
        self.assertEqual(rover.heading, "S")
        rover.turn_left()
        self.assertEqual(rover.heading, "E")
        rover.turn_left()
        self.assertEqual(rover.heading, "N")  # Full circle

    def test_turn_right(self):
        rover = Rover()
        rover.turn_right()
        self.assertEqual(rover.heading, "E")
        rover.turn_right()
        self.assertEqual(rover.heading, "S")
        rover.turn_right()
        self.assertEqual(rover.heading, "W")
        rover.turn_right()
        self.assertEqual(rover.heading, "N")  # Full circle

    def test_move_in_different_directions(self):
        rover = Rover()
        
        # Move East
        rover.set_heading("E")
        rover.move_forward(2)
        self.assertEqual(rover.x, 2)
        self.assertEqual(rover.y, 0)
        
        # Move South
        rover.set_heading("S")
        rover.move_forward(3)
        self.assertEqual(rover.x, 2)
        self.assertEqual(rover.y, -3)
        
        # Move West
        rover.set_heading("W")
        rover.move_forward(1)
        self.assertEqual(rover.x, 1)
        self.assertEqual(rover.y, -3)

    def test_set_pos(self):
        rover = Rover()
        rover.set_pos(10, -5)
        self.assertEqual(rover.x, 10)
        self.assertEqual(rover.y, -5)
        self.assertEqual(rover.heading, "N")  # Heading unchanged

    def test_set_heading(self):
        rover = Rover()
        rover.set_heading("E")
        self.assertEqual(rover.heading, "E")
        rover.set_heading("s")  # Lowercase should work
        self.assertEqual(rover.heading, "S")
        rover.set_heading("w")
        self.assertEqual(rover.heading, "W")

    def test_set_heading_invalid(self):
        rover = Rover()
        with self.assertRaises(ValueError):
            rover.set_heading("X")

    def test_reset(self):
        rover = Rover()
        rover.set_pos(5, 5)
        rover.set_heading("E")
        rover.reset()
        self.assertEqual(rover.x, 0)
        self.assertEqual(rover.y, 0)
        self.assertEqual(rover.heading, "N")


class TestParser(unittest.TestCase):
    """Test the parser functions."""

    def test_parse_line_simple(self):
        cmd, args = parse_line("F")
        self.assertEqual(cmd, "F")
        self.assertEqual(args, [])

    def test_parse_line_with_args(self):
        cmd, args = parse_line("FORWARD 5")
        self.assertEqual(cmd, "FORWARD")
        self.assertEqual(args, ["5"])

    def test_parse_line_multiple_args(self):
        cmd, args = parse_line("GOTO 10 20 N")
        self.assertEqual(cmd, "GOTO")
        self.assertEqual(args, ["10", "20", "N"])

    def test_parse_line_whitespace(self):
        cmd, args = parse_line("  F  3  ")
        self.assertEqual(cmd, "F")
        self.assertEqual(args, ["3"])

    def test_parse_line_case_insensitive(self):
        cmd, args = parse_line("forward")
        self.assertEqual(cmd, "FORWARD")
        cmd, args = parse_line("left")
        self.assertEqual(cmd, "LEFT")

    def test_parse_line_empty(self):
        with self.assertRaises(ParseError):
            parse_line("")
        with self.assertRaises(ParseError):
            parse_line("   ")


class TestHandlers(unittest.TestCase):
    """Test command handlers."""

    def setUp(self):
        self.rover = Rover()
        self.handlers = make_handlers()

    def test_help(self):
        result = self.handlers["HELP"](self.rover, [])
        self.assertIn("Commands:", result)
        self.assertIn("FORWARD", result)

    def test_status(self):
        result = self.handlers["STATUS"](self.rover, [])
        self.assertEqual(result, "(0, 0) heading=N")

    def test_left(self):
        result = self.handlers["L"](self.rover, [])
        self.assertEqual(self.rover.heading, "W")
        self.assertEqual(result, "(0, 0) heading=W")

    def test_right(self):
        result = self.handlers["R"](self.rover, [])
        self.assertEqual(self.rover.heading, "E")
        self.assertEqual(result, "(0, 0) heading=E")

    def test_forward_default(self):
        result = self.handlers["F"](self.rover, [])
        self.assertEqual(self.rover.y, 1)
        self.assertEqual(result, "(0, 1) heading=N")

    def test_forward_with_steps(self):
        result = self.handlers["FORWARD"](self.rover, ["5"])
        self.assertEqual(self.rover.y, 5)
        self.assertEqual(result, "(0, 5) heading=N")

    def test_forward_zero_steps(self):
        result = self.handlers["F"](self.rover, ["0"])
        self.assertEqual(self.rover.y, 0)
        self.assertEqual(result, "(0, 0) heading=N")

    def test_forward_negative_steps(self):
        with self.assertRaises(ParseError):
            self.handlers["F"](self.rover, ["-1"])

    def test_back_default(self):
        result = self.handlers["B"](self.rover, [])
        self.assertEqual(self.rover.y, -1)
        self.assertEqual(result, "(0, -1) heading=N")

    def test_back_with_steps(self):
        result = self.handlers["BACK"](self.rover, ["3"])
        self.assertEqual(self.rover.y, -3)
        self.assertEqual(result, "(0, -3) heading=N")

    def test_back_negative_steps(self):
        with self.assertRaises(ParseError):
            self.handlers["B"](self.rover, ["-2"])

    def test_reset(self):
        self.rover.set_pos(10, 10)
        self.rover.set_heading("E")
        result = self.handlers["RESET"](self.rover, [])
        self.assertEqual(self.rover.x, 0)
        self.assertEqual(self.rover.y, 0)
        self.assertEqual(self.rover.heading, "N")
        self.assertEqual(result, "(0, 0) heading=N")

    def test_goto_position_only(self):
        result = self.handlers["GOTO"](self.rover, ["5", "-3"])
        self.assertEqual(self.rover.x, 5)
        self.assertEqual(self.rover.y, -3)
        self.assertEqual(self.rover.heading, "N")  # Unchanged
        self.assertEqual(result, "(5, -3) heading=N")

    def test_goto_with_heading(self):
        result = self.handlers["GOTO"](self.rover, ["10", "20", "E"])
        self.assertEqual(self.rover.x, 10)
        self.assertEqual(self.rover.y, 20)
        self.assertEqual(self.rover.heading, "E")
        self.assertEqual(result, "(10, 20) heading=E")

    def test_goto_with_lowercase_heading(self):
        result = self.handlers["GOTO"](self.rover, ["0", "0", "s"])
        self.assertEqual(self.rover.heading, "S")

    def test_goto_invalid_heading(self):
        with self.assertRaises(ParseError):
            self.handlers["GOTO"](self.rover, ["0", "0", "X"])

    def test_goto_missing_args(self):
        with self.assertRaises(ParseError):
            self.handlers["GOTO"](self.rover, ["5"])
        with self.assertRaises(ParseError):
            self.handlers["GOTO"](self.rover, [])

    def test_goto_invalid_coordinates(self):
        with self.assertRaises(ParseError):
            self.handlers["GOTO"](self.rover, ["abc", "5"])

    def test_command_aliases(self):
        # Test that aliases work
        self.handlers["LEFT"](self.rover, [])
        self.assertEqual(self.rover.heading, "W")
        
        self.rover.reset()
        self.handlers["RIGHT"](self.rover, [])
        self.assertEqual(self.rover.heading, "E")
        
        self.rover.reset()
        self.handlers["MOVE"](self.rover, ["2"])
        self.assertEqual(self.rover.y, 2)

    def test_complex_sequence(self):
        """Test a complex sequence of commands."""
        # Start at origin facing North
        self.assertEqual(self.rover.status_str(), "(0, 0) heading=N")
        
        # Move forward 3 steps
        self.handlers["F"](self.rover, ["3"])
        self.assertEqual(self.rover.status_str(), "(0, 3) heading=N")
        
        # Turn right and move forward 2
        self.handlers["R"](self.rover, [])
        self.handlers["FORWARD"](self.rover, ["2"])
        self.assertEqual(self.rover.status_str(), "(2, 3) heading=E")
        
        # Turn left twice and move back
        self.handlers["L"](self.rover, [])
        self.handlers["LEFT"](self.rover, [])
        self.handlers["BACK"](self.rover, ["1"])
        self.assertEqual(self.rover.status_str(), "(3, 3) heading=W")
        
        # Goto new position with heading
        self.handlers["GOTO"](self.rover, ["-5", "-10", "S"])
        self.assertEqual(self.rover.status_str(), "(-5, -10) heading=S")
        
        # Reset
        self.handlers["RESET"](self.rover, [])
        self.assertEqual(self.rover.status_str(), "(0, 0) heading=N")


if __name__ == "__main__":
    unittest.main()
