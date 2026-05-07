# random_agent.py — Weakest baseline: picks a random legal move

import random
from gomoku.game import GomokuGame


class RandomAgent:
    """Picks a uniformly random legal move. Used as a sanity-check baseline."""

    def get_best_move(self, game: GomokuGame):
        return random.choice(game.get_legal_moves())
