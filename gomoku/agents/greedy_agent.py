# greedy_agent.py — Heuristic-only baseline: picks the best move by evaluate() alone

from gomoku.game import GomokuGame, BLACK, WHITE
from gomoku.heuristic import evaluate


class GreedyAgent:
    """
    Picks the move that maximizes the heuristic score from this agent's perspective.
    No tree search — pure one-step lookahead using the same evaluate() function
    that MCTS uses for rollout evaluation.

    This is the meaningful baseline: if MCTS can beat it consistently, that proves
    the tree search adds real value beyond the heuristic alone.
    """

    def __init__(self, color=BLACK):
        self.color = color

    def get_best_move(self, game: GomokuGame):
        best_move = None
        best_score = float('-inf')

        for row, col in game.get_legal_moves():
            clone = game.clone()
            clone.make_move(row, col)

            # If this move wins immediately, take it
            if clone.winner == self.color:
                return (row, col)

            score = evaluate(clone.board, self.color)
            if score > best_score:
                best_score = score
                best_move = (row, col)

        return best_move
