"""
game_logic.py
-------------
Pure game-logic module for Tic Tac Toe. No UI / Tkinter dependency,
so it can be unit tested and reused independently (e.g. in a CLI or
web version).

Board representation:
    A list of 9 elements, indices 0-8 laid out like:
        0 | 1 | 2
        --+---+--
        3 | 4 | 5
        --+---+--
        6 | 7 | 8
    Each cell holds "X", "O", or "" (empty).
"""

from copy import deepcopy

HUMAN = "X"
AI = "O"
EMPTY = ""

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
    (0, 4, 8), (2, 4, 6),             # diagonals
]


def new_board():
    return [EMPTY] * 9


def available_moves(board):
    return [i for i, cell in enumerate(board) if cell == EMPTY]


def winner(board):
    """Return "X", "O" if there's a winner, "draw" if the board is full
    with no winner, or None if the game is still in progress."""
    for a, b, c in WIN_LINES:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a]
    if not available_moves(board):
        return "draw"
    return None


def winning_line(board):
    """Return the winning (a, b, c) index tuple, or None."""
    for a, b, c in WIN_LINES:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return (a, b, c)
    return None


def make_move(board, index, player):
    if board[index] != EMPTY:
        raise ValueError(f"Cell {index} is already occupied.")
    new = deepcopy(board)
    new[index] = player
    return new


def _minimax(board, current_player, depth=0):
    """
    Returns (score, move_index) from the perspective of AI (maximizing).
    Score is higher for faster AI wins and slower AI losses, to make
    the AI prefer quick wins and delay unavoidable losses.
    """
    result = winner(board)
    if result == AI:
        return 10 - depth, None
    if result == HUMAN:
        return depth - 10, None
    if result == "draw":
        return 0, None

    moves = available_moves(board)
    best_move = moves[0]

    if current_player == AI:
        best_score = float("-inf")
        for move in moves:
            new_board = make_move(board, move, AI)
            score, _ = _minimax(new_board, HUMAN, depth + 1)
            if score > best_score:
                best_score = score
                best_move = move
        return best_score, best_move
    else:
        best_score = float("inf")
        for move in moves:
            new_board = make_move(board, move, HUMAN)
            score, _ = _minimax(new_board, AI, depth + 1)
            if score < best_score:
                best_score = score
                best_move = move
        return best_score, best_move


def best_ai_move(board, difficulty="unbeatable"):
    """
    Choose a move for the AI (player "O").

    difficulty:
        "unbeatable" -> perfect minimax play, never loses.
        "hard"       -> 80% minimax, 20% random.
        "easy"       -> fully random legal move.
    """
    import random

    moves = available_moves(board)
    if not moves:
        return None

    if difficulty == "easy":
        return random.choice(moves)

    if difficulty == "hard" and random.random() < 0.2:
        return random.choice(moves)

    _, move = _minimax(board, AI)
    return move
