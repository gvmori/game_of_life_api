#!/usr/local/bin/python3

import unittest
from unittest.mock import patch
from main import app, MAX_ALLOWED_ITERATIONS
from fastapi.testclient import TestClient


class TestApp(unittest.TestCase):
    def test_create_board_invalid_format(self):
        client = TestClient(app)

        # Invalid board format (not a list of coordinates)
        response = client.post("/boards/", json={"board": "invalid_format"})
        self.assertEqual(response.status_code, 422)
        self.assertIn("Field required", response.json().get("detail", [{}])[0].get("msg", ""))
    
    # mock valkey for testing purposes
    @patch('main.v')
    # mock the Board class to avoid testing its logic here
    @patch('main.Board')
    def test_create_board_valid(self, mock_board_class, mock_valkey):
        client = TestClient(app)

        # Valid board format
        input_board = {
            "coordinates": [(0, 0), (1, 1), (2, 2)]
        }
        response = client.post("/boards/", json=input_board)
        self.assertEqual(response.status_code, 200)
        self.assertIn("board_id", response.json())
        board_id = response.json()["board_id"]
        mock_valkey.set.assert_called_once()
        self.assertIsInstance(board_id, str)

    @patch('main.v')
    @patch('main.Board')
    @patch('main._retrieve_board')
    def test_get_next_state_calls_run_iterations(self, mock_retrieve, mock_board_class, mock_valkey):
        client = TestClient(app)

        board_id = "test-board-id"
        mock_retrieve.return_value = {"coordinates": [(0, 0)], "is_finished": False}

        mock_board_instance = mock_board_class.return_value
        mock_board_instance.run_iterations.return_value = True
        mock_board_instance.to_dict.return_value = {"coordinates": [(0, 0)]}
        mock_board_instance.is_finished = False

        response = client.get(f"/boards/{board_id}/next")
        self.assertEqual(response.status_code, 200)

        self.assertIn("coordinates", response.json())
        called_kwargs = mock_board_class.call_args.kwargs
        self.assertIn("coordinates", called_kwargs)
        self.assertEqual(called_kwargs["coordinates"], [(0, 0)])
        self.assertEqual(called_kwargs["max_iterations"], MAX_ALLOWED_ITERATIONS)
        mock_board_instance.run_iterations.assert_called_once_with(1)


    @patch('main.v')
    @patch('main.Board')
    def test_get_state_invalid_num_iters(self, mock_board_class, mock_valkey):
        client = TestClient(app)

        board_id = "test-board-id"
        response = client.get(f"/boards/{board_id}/iterate/-5")
        self.assertEqual(response.status_code, 400)
        self.assertIn("num_iters must be non-negative", response.json().get("detail", ""))
    
    @patch('main.v')
    @patch('main.Board')
    def test_get_final_state_exceeds_limit(self, mock_board_class, mock_valkey):
        client = TestClient(app)

        board_id = "test-board-id"
        response = client.get(f"/boards/{board_id}/final/2000")
        self.assertEqual(response.status_code, 400)
        self.assertIn("num_iters exceeds limit", response.json().get("detail", ""))
    
    @patch('main.v')
    @patch('main.Board')
    def test_get_final_state_invalid_max_iterations(self, mock_board_class, mock_valkey):
        client = TestClient(app)

        board_id = "test-board-id"
        response = client.get(f"/boards/{board_id}/final/-10")
        self.assertEqual(response.status_code, 400)
        self.assertIn("num_iters must be non-negative", response.json().get("detail", ""))

    @patch('main.v')
    @patch('main.Board')
    def test_get_state_board_not_found(self, mock_board_class, mock_valkey):
        client = TestClient(app)

        board_id = "nonexistent-board-id"
        mock_valkey.get.return_value = None

        response = client.get(f"/boards/{board_id}/iterate/5")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Board not found", response.json().get("detail", ""))
        mock_valkey.get.assert_called_once_with(board_id)

if __name__ == '__main__':
    unittest.main()
