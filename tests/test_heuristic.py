import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from gomoku.game import BLACK, WHITE, EMPTY, BOARD_SIZE
from gomoku.heuristic import evaluate, FIVE, OPEN_FOUR, OPEN_THREE


def _empty_board():
    return [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]


def test_empty_board_is_zero():
    board = _empty_board()
    assert evaluate(board, BLACK) == 0.0


def test_player_five_in_a_row():
    board = _empty_board()
    for c in range(5):
        board[7][c] = BLACK
    score = evaluate(board, BLACK)
    assert score >= FIVE


def test_opponent_five_in_a_row():
    board = _empty_board()
    for c in range(5):
        board[7][c] = WHITE
    score = evaluate(board, BLACK)
    assert score <= -FIVE


def test_open_four_positive():
    """Player with open four should have a high positive score."""
    board = _empty_board()
    # _BBBB_ on row 7, cols 2-5, ends at col 1 and col 6 are empty
    for c in range(2, 6):
        board[7][c] = BLACK
    score = evaluate(board, BLACK)
    assert score >= OPEN_FOUR


def test_opponent_open_four_negative():
    """Opponent with open four means a large negative score for player."""
    board = _empty_board()
    for c in range(2, 6):
        board[7][c] = WHITE
    score = evaluate(board, BLACK)
    assert score <= -OPEN_FOUR


def test_open_three_positive():
    """Player with open three should yield a positive score."""
    board = _empty_board()
    # _BBB_ on row 5, cols 2-4, ends are open
    for c in range(2, 5):
        board[5][c] = BLACK
    score = evaluate(board, BLACK)
    assert score >= OPEN_THREE


def test_symmetry():
    """Mirrored position should give equal scores for each player."""
    board = _empty_board()
    # BLACK open three on top half
    for c in range(2, 5):
        board[3][c] = BLACK
    # WHITE open three on bottom half (mirror)
    for c in range(2, 5):
        board[11][c] = WHITE
    black_score = evaluate(board, BLACK)
    white_score = evaluate(board, WHITE)
    assert black_score == white_score


def test_evaluate_favors_own_pieces():
    board = _empty_board()
    board[7][7] = BLACK
    board[7][8] = BLACK
    assert evaluate(board, BLACK) > 0


def test_vertical_open_three():
    board = _empty_board()
    for r in range(3, 6):
        board[r][7] = WHITE
    score = evaluate(board, WHITE)
    assert score >= OPEN_THREE


def test_diagonal_five_in_a_row():
    board = _empty_board()
    for i in range(5):
        board[i][i] = BLACK
    score = evaluate(board, BLACK)
    assert score >= FIVE
