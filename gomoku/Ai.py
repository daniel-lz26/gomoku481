# ai.py — Wraps the MCTS library and interfaces it with GomokuGame

from mcts import mcts
from gomoku.game import GomokuGame, BLACK, WHITE
from gomoku.heuristic import evaluate


def _heuristic_rollout(state):
    """Evaluate immediately using the heuristic instead of random playout."""
    return state.getReward()


class GomokuAction:
    """Hashable action representing a board move."""
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __hash__(self):
        return hash((self.row, self.col))

    def __eq__(self, other):
        return isinstance(other, GomokuAction) and self.row == other.row and self.col == other.col

    def __repr__(self):
        return f"Action({self.row}, {self.col})"


class GomokuState:
    """Adapts GomokuGame to the interface expected by the mcts library."""

    def __init__(self, game: GomokuGame):
        self.game = game

    def getCurrentPlayer(self):
        return 1 if self.game.current_player == BLACK else -1

    def getPossibleActions(self):
        return [GomokuAction(r, c) for r, c in self.game.get_legal_moves()]

    def takeAction(self, action):
        new_game = self.game.clone()
        new_game.make_move(action.row, action.col)
        return GomokuState(new_game)

    def isTerminal(self):
        return self.game.is_terminal()

    def getReward(self):
        """
        Reward from WHITE's (AI) perspective, normalized to [-1, 1].
        The mcts library does not negate rewards per player, so we anchor
        to a fixed side (WHITE = AI) throughout the tree.
        """
        if self.game.winner == WHITE:
            return 1.0
        if self.game.winner == BLACK:
            return -1.0
        if self.game.is_terminal():
            return 0.0

        raw = evaluate(self.game.board, WHITE)
        # Clamp to [-1, 1] using the five-in-a-row score as the ceiling
        return max(-1.0, min(1.0, raw / 1_000_000))


class GomokuAI:
    def __init__(self, simulation_budget=500):
        self.simulation_budget = simulation_budget
        self._searcher = mcts(
            iterationLimit=simulation_budget,
            rolloutPolicy=_heuristic_rollout,
        )

    def get_best_move(self, game: GomokuGame):
        """
        Given the current game state, return the best (row, col) move.
        Uses MCTS guided by the heuristic evaluation function.
        """
        legal = game.get_legal_moves()
        if len(legal) == 1:
            return legal[0]

        state = GomokuState(game.clone())
        action = self._searcher.search(initialState=state)
        return (action.row, action.col)
