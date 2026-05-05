import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from gomoku.game import GomokuGame, BLACK, WHITE, EMPTY, BOARD_SIZE


def test_initial_state():
    game = GomokuGame()
    assert game.current_player == BLACK
    assert game.winner is None
    assert game.last_move is None
    assert all(game.board[r][c] == EMPTY for r in range(BOARD_SIZE) for c in range(BOARD_SIZE))


def test_make_move_places_piece():
    game = GomokuGame()
    result = game.make_move(7, 7)
    assert result is True
    assert game.board[7][7] == BLACK
    assert game.current_player == WHITE
    assert game.last_move == (7, 7)


def test_make_move_invalid_occupied():
    game = GomokuGame()
    game.make_move(7, 7)
    result = game.make_move(7, 7)
    assert result is False


def test_undo_move():
    game = GomokuGame()
    game.make_move(7, 7)
    game.undo_move(7, 7)
    assert game.board[7][7] == EMPTY
    assert game.current_player == BLACK
    assert game.winner is None


def test_win_horizontal():
    game = GomokuGame()
    for c in range(5):
        game.board[0][c] = BLACK
    assert game.check_win(0, 4, BLACK) is True


def test_win_vertical():
    game = GomokuGame()
    for r in range(5):
        game.board[r][3] = BLACK
    assert game.check_win(4, 3, BLACK) is True


def test_win_diagonal():
    game = GomokuGame()
    for i in range(5):
        game.board[i][i] = WHITE
    assert game.check_win(4, 4, WHITE) is True


def test_no_win_four_in_a_row():
    game = GomokuGame()
    for c in range(4):
        game.board[0][c] = BLACK
    assert game.check_win(0, 3, BLACK) is False


def test_is_terminal_win():
    game = GomokuGame()
    for c in range(5):
        game.board[0][c] = BLACK
    game.winner = BLACK
    assert game.is_terminal() is True


def test_draw():
    game = GomokuGame()
    # Fill the entire board alternating in a pattern that avoids 5-in-a-row
    # Use a simple checkerboard-like pattern (won't produce 5 in a row)
    player = BLACK
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            game.board[r][c] = player
            player = WHITE if player == BLACK else BLACK
    game.winner = None  # ensure no winner was set
    assert game.is_terminal() is True
    assert game.winner is None


def test_clone_independence():
    game = GomokuGame()
    game.make_move(7, 7)
    clone = game.clone()
    clone.make_move(0, 0)
    assert game.board[0][0] == EMPTY  # original unaffected
    assert clone.board[0][0] == WHITE


def test_legal_moves_empty_board():
    game = GomokuGame()
    moves = game.get_legal_moves()
    assert moves == [(7, 7)]


def test_legal_moves_near_pieces():
    game = GomokuGame()
    game.board[7][7] = BLACK
    moves = game.get_legal_moves()
    assert (7, 7) not in moves
    assert (7, 8) in moves
    assert (5, 5) in moves
    # Cell 3 squares away should not be included
    assert (7, 10) not in moves
