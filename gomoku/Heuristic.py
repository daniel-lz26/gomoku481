# heuristic.py — Board evaluation function
# This is the main intellectual contribution of the project.

from gomoku.game import BLACK, WHITE, BOARD_SIZE, EMPTY


def evaluate(board, player) -> float:
    """
    Score the board from `player`'s perspective.
    Higher = better for player.

    Patterns to detect and weight:
      - Five in a row     → immediate win, return huge score
      - Open four         → one move from winning, very high score
      - Blocked four      → still dangerous
      - Open three        → building toward a win
      - Double threat     → two threats at once (very strong)
    """
    # TODO: implement pattern scoring
    pass


def _count_pattern(board, player, dr, dc, length, open_ends):
    """
    Helper: count occurrences of a pattern (sequence of `length` pieces
    for `player` with `open_ends` unblocked ends) across the board
    in direction (dr, dc).
    """
    pass