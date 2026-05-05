# ai.py — Wraps the MCTS library and interfaces it with GomokuGame

from gomoku.game import GomokuGame
from gomoku.heuristic import evaluate

# TODO: import chosen MCTS library here
# e.g.: from mcts import mcts


class GomokuAI:
    def __init__(self, simulation_budget=500):
        self.simulation_budget = simulation_budget  # controls difficulty

    def get_best_move(self, game: GomokuGame):
        """
        Given the current game state, return the best (row, col) move.
        Uses MCTS with the heuristic evaluation to guide rollouts.
        """
        # TODO: interface game state with MCTS library
        pass