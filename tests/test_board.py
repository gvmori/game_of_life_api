#!/usr/local/bin/python3

from contextlib import AbstractContextManager
from typing import Any
import unittest
from lib.board import Board

class TestBoard(unittest.TestCase):
    def test_board_initialization(self):
        # Test valid initialization
        coordinates = {(0, 0), (1, 1), (2, 2)}
        board = Board(coordinates=coordinates)
        self.assertEqual(board._coords, coordinates)
        
        # Test invalid initialization
        with self.assertRaises(ValueError):
            Board(coordinates="invalid_format")  # type: ignore
    
    def test_board_to_dict(self):
        coordinates = {(0, 0), (1, 1)}
        board = Board(coordinates=coordinates)
        board_dict = board.to_dict()
        self.assertEqual(board_dict["coordinates"], coordinates)
        self.assertFalse(board_dict["is_finished"])
    
    def test_board_run_iterations(self):
        coordinates = {(0, 0), (0, 1), (0, 2)}
        board = Board(coordinates=coordinates)
        
        # Run one iteration
        completed_all_iterations_without_finishing = board.run_iterations(1)
        expected_coordinates_after_1 = {( -1, 1), (0, 1), (1, 1)}
        self.assertEqual(board._coords, expected_coordinates_after_1)
        self.assertTrue(completed_all_iterations_without_finishing)
        
        # Run another iteration
        completed_all_iterations_without_finishing = board.run_iterations(1)
        expected_coordinates_after_2 = {(0, 0), (0, 1), (0, 2)}
        self.assertEqual(board._coords, expected_coordinates_after_2)
        self.assertTrue(completed_all_iterations_without_finishing)
        
        # Test finishing condition
        board = Board(coordinates={(0, 0)})
        completed_all_iterations_without_finishing = board.run_iterations(1)
        self.assertTrue(board.is_finished)
        self.assertFalse(completed_all_iterations_without_finishing)
    
    def test_board_to_dense(self):
        coordinates = {(0, 0), (1, 2), (2, 1)}
        board = Board(coordinates=coordinates)
        dense = board.to_dense()
        expected_dense = [
            [1, 0, 0],
            [0, 0, 1],
            [0, 1, 0]
        ]
        self.assertEqual(dense, expected_dense)
    
    def test_board_invalid_iterations(self):
        board = Board(coordinates={(0, 0)})
        with self.assertRaises(ValueError):
            board.run_iterations(-1)
    
    def test_board_no_coordinates(self):
        board = Board(coordinates=set())
        self.assertTrue(board.is_finished)
        dense = board.to_dense()
        self.assertEqual(dense, [[]])
        dict_repr = board.to_dict()
        self.assertEqual(dict_repr["coordinates"], set())
    
    def test_board_large_iterations_limit(self):
        coordinates = {(0, 0), (0, 1), (0, 2)}
        board = Board(coordinates=coordinates, max_iterations=10)
        
        # Run more iterations than max_iterations
        with self.assertRaises(ValueError):
            board.run_iterations(15)

        board = Board(coordinates=coordinates, max_iterations=15)
        board.run_iterations(15)
        self.assertEqual(board._coords, {( -1, 1), (0, 1), (1, 1)})

    def test_long_running_infinite_pattern(self):
        coordinates = {(0, 1), (1, 2), (2, 0), (2, 1), (2, 2), # Glider
                       (-1, -1), (-2, -2), (-3, -3), (-3, -2), (-3, -1) # Negative direction glider
                    }
        board = Board(coordinates=coordinates, max_iterations=1000)
        
        completed_all_iterations_without_finishing = board.run_iterations(1000)
        self.assertFalse(board.is_finished)
        self.assertTrue(completed_all_iterations_without_finishing)

    def test_to_string_and_from_string(self):
        coordinates = {(0, 0), (1, 1)}
        board = Board(coordinates=coordinates)
        board_str = board.to_string()
        
        # Simulate loading from string
        import json
        data = json.loads(board_str)
        loaded_coordinates = set(tuple(coord) for coord in data["coordinates"])
        loaded_is_finished = data["is_finished"]
        
        self.assertEqual(loaded_coordinates, coordinates)
        self.assertEqual(loaded_is_finished, board.is_finished)

if __name__ == '__main__':
    unittest.main()