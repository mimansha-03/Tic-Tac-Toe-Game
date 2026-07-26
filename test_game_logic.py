"""
test_game_logic.py
-------------------
Unit tests for game_logic.py (no Tkinter / UI involved).

Run with:
    python -m unittest test_game_logic.py -v
"""

import unittest
import game_logic as gl


class TestWinner(unittest.TestCase):
    def test_no_winner_empty_board(self):
        self.assertIsNone(gl.winner(gl.new_board()))

    def test_row_win(self):
        board = ["X", "X", "X", "", "", "", "", "", ""]
        self.assertEqual(gl.winner(board), "X")

    def test_column_win(self):
        board = ["O", "", "", "O", "", "", "O", "", ""]
        self.assertEqual(gl.winner(board), "O")

    def test_diagonal_win(self):
        board = ["X", "", "", "", "X", "", "", "", "X"]
        self.assertEqual(gl.winner(board), "X")

    def test_draw(self):
        board = ["X", "O", "X",
                  "X", "O", "O",
                  "O", "X", "X"]
        self.assertEqual(gl.winner(board), "draw")

    def test_winning_line_indices(self):
        board = ["X", "X", "X", "", "", "", "", "", ""]
        self.assertEqual(gl.winning_line(board), (0, 1, 2))


class TestMakeMove(unittest.TestCase):
    def test_make_move_places_mark(self):
        board = gl.new_board()
        new_board = gl.make_move(board, 4, "X")
        self.assertEqual(new_board[4], "X")
        # original board is untouched (immutability)
        self.assertEqual(board[4], gl.EMPTY)

    def test_make_move_on_occupied_cell_raises(self):
        board = gl.make_move(gl.new_board(), 0, "X")
        with self.assertRaises(ValueError):
            gl.make_move(board, 0, "O")


class TestAI(unittest.TestCase):
    def test_ai_blocks_immediate_human_win(self):
        # X X _  -> AI (O) must block at index 2
        board = ["X", "X", "", "", "O", "", "", "", ""]
        move = gl.best_ai_move(board, difficulty="unbeatable")
        self.assertEqual(move, 2)

    def test_ai_takes_winning_move(self):
        # O O _  -> AI should win at index 2
        board = ["O", "O", "", "X", "X", "", "", "", ""]
        move = gl.best_ai_move(board, difficulty="unbeatable")
        self.assertEqual(move, 2)

    def test_unbeatable_ai_never_loses_full_game(self):
        # Simulate a full game where a "perfect" human (also minimax)
        # plays against the unbeatable AI. Result must never be a human win.
        board = gl.new_board()
        current = gl.HUMAN
        while gl.winner(board) is None:
            if current == gl.HUMAN:
                move = gl.best_ai_move(board, difficulty="unbeatable")  # perfect play as X too
                board = gl.make_move(board, move, gl.HUMAN)
                current = gl.AI
            else:
                move = gl.best_ai_move(board, difficulty="unbeatable")
                board = gl.make_move(board, move, gl.AI)
                current = gl.HUMAN
        self.assertIn(gl.winner(board), ("draw", gl.AI))

    def test_easy_ai_returns_legal_move(self):
        board = gl.new_board()
        move = gl.best_ai_move(board, difficulty="easy")
        self.assertIn(move, gl.available_moves(board))

    def test_no_moves_returns_none(self):
        full_board = ["X", "O", "X", "X", "O", "O", "O", "X", "X"]
        self.assertIsNone(gl.best_ai_move(full_board))


if __name__ == "__main__":
    unittest.main()
