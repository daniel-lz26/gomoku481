# game.py — Board state, move validation, win detection

BOARD_SIZE = 15
EMPTY = 0
BLACK = 1  # Human
WHITE = 2  # AI


class GomokuGame:
    def __init__(self):
        self.board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.current_player = BLACK
        self.winner = None
        self.last_move = None

    def get_legal_moves(self):
        """Return list of (row, col) tuples for all empty cells."""
        # TODO: optionally prune to local neighborhood of existing pieces
        pass

    def make_move(self, row, col):
        """Place current player's piece. Returns True if successful."""
        pass

    def undo_move(self, row, col):
        """Remove a piece from the board (needed by MCTS)."""
        pass

    def check_win(self, row, col, player):
        """Check if placing at (row, col) gives player a 5-in-a-row."""
        pass

    def is_terminal(self):
        """Return True if game is over (win or draw)."""
        pass

    def clone(self):
        """Return a deep copy of the game state (needed by MCTS)."""
        pass