# game.py — Board state, move validation, win detection

BOARD_SIZE = 15
EMPTY = 0
BLACK = 1  # Human
WHITE = 2  # AI

_DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]


class GomokuGame:
    def __init__(self):
        self.board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.current_player = BLACK
        self.winner = None
        self.last_move = None

    def get_legal_moves(self):
        """Return list of (row, col) tuples for empty cells near existing pieces."""
        has_pieces = False
        candidates = set()

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] != EMPTY:
                    has_pieces = True
                    for dr in range(-2, 3):
                        for dc in range(-2, 3):
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and self.board[nr][nc] == EMPTY:
                                candidates.add((nr, nc))

        if not has_pieces:
            return [(7, 7)]
        return list(candidates)

    def make_move(self, row, col):
        """Place current player's piece. Returns True if successful."""
        if self.board[row][col] != EMPTY or self.winner is not None:
            return False
        self.board[row][col] = self.current_player
        self.last_move = (row, col)
        if self.check_win(row, col, self.current_player):
            self.winner = self.current_player
        self.current_player = WHITE if self.current_player == BLACK else BLACK
        return True

    def undo_move(self, row, col):
        """Remove a piece from the board (needed by MCTS)."""
        self.board[row][col] = EMPTY
        self.winner = None
        self.current_player = WHITE if self.current_player == BLACK else BLACK
        self.last_move = None

    def check_win(self, row, col, player):
        """Check if placing at (row, col) gives player a 5-in-a-row."""
        for dr, dc in _DIRECTIONS:
            count = 1
            # Forward direction
            r, c = row + dr, col + dc
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == player:
                count += 1
                r += dr
                c += dc
            # Backward direction
            r, c = row - dr, col - dc
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == player:
                count += 1
                r -= dr
                c -= dc
            if count >= 5:
                return True
        return False

    def is_terminal(self):
        """Return True if game is over (win or draw)."""
        if self.winner is not None:
            return True
        return all(self.board[r][c] != EMPTY for r in range(BOARD_SIZE) for c in range(BOARD_SIZE))

    def clone(self):
        """Return a deep copy of the game state (needed by MCTS)."""
        new_game = GomokuGame()
        new_game.board = [row[:] for row in self.board]
        new_game.current_player = self.current_player
        new_game.winner = self.winner
        new_game.last_move = self.last_move
        return new_game
