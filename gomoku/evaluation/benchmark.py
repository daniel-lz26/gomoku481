# benchmark.py — Headless game runner for automated performance evaluation
#
# Run from the project root:
#   python -m gomoku.evaluation.benchmark
#
# Results are written to data/game_log.csv.
# No Pygame window is opened — all games run in pure Python.

import time
from gomoku.game import GomokuGame, BLACK, WHITE
from gomoku.ai import GomokuAI
from gomoku.agents.random_agent import RandomAgent
from gomoku.agents.greedy_agent import GreedyAgent
from gomoku.evaluation.metrics_logger import log_game, next_game_id

# ---------------------------------------------------------------------------
# Experiment matrix: (opponent_type, budget, num_games)
# ---------------------------------------------------------------------------
EXPERIMENTS = [
    ("random", 1_000,  20),
    ("greedy",   500,  20),
    ("greedy", 1_000,  20),
    ("greedy", 5_000,  20),
    ("greedy", 10_000, 20),
]


def _make_opponent(opponent_type, color):
    if opponent_type == "random":
        return RandomAgent()
    if opponent_type == "greedy":
        return GreedyAgent(color=color)
    raise ValueError(f"Unknown opponent type: {opponent_type!r}")


def run_single_game(ai, opponent, ai_color):
    """
    Play one complete headless game between ai and opponent.

    The AI always plays as ai_color; the opponent plays the other color.

    Returns
    -------
    winner          : str   — "AI", "opponent", or "draw"
    num_moves       : int
    game_duration   : float — wall-clock seconds
    avg_ai_move_time: float — average seconds the AI spent per move
    """
    game = GomokuGame()
    opp_color = BLACK if ai_color == WHITE else WHITE

    ai_move_times = []
    total_moves = 0
    start = time.time()

    while not game.is_terminal():
        if game.current_player == ai_color:
            t0 = time.time()
            row, col = ai.get_best_move(game)
            ai_move_times.append(time.time() - t0)
        else:
            row, col = opponent.get_best_move(game)

        game.make_move(row, col)
        total_moves += 1

    duration = time.time() - start
    avg_ai_time = sum(ai_move_times) / len(ai_move_times) if ai_move_times else 0.0

    if game.winner == ai_color:
        result = "AI"
    elif game.winner == opp_color:
        result = "opponent"
    else:
        result = "draw"

    return result, total_moves, duration, avg_ai_time


def run_experiment(opponent_type, budget, num_games=20):
    """
    Run num_games games for one experimental condition and log every result.

    AI color alternates black/white each game to control for first-mover advantage.
    """
    header = f"  {opponent_type.upper():6s} | budget={budget:>6,} | {num_games} games"
    print(f"\n{'─' * 55}")
    print(header)
    print(f"{'─' * 55}")

    wins = 0
    for i in range(num_games):
        ai_color = BLACK if i % 2 == 0 else WHITE
        opp_color = WHITE if ai_color == BLACK else BLACK
        game_id = next_game_id()

        ai = GomokuAI(simulation_budget=budget, color=ai_color)
        opponent = _make_opponent(opponent_type, opp_color)

        result, num_moves, duration, avg_time = run_single_game(ai, opponent, ai_color)

        color_label = "black" if ai_color == BLACK else "white"
        log_game(
            game_id=game_id,
            budget=budget,
            ai_color=color_label,
            opponent_type=opponent_type,
            winner=result,
            num_moves=num_moves,
            game_duration_sec=duration,
            avg_move_time_sec=avg_time,
        )

        if result == "AI":
            wins += 1

        current_rate = wins / (i + 1)
        print(
            f"  Game {i+1:2d}/{num_games} | AI={color_label:5s} | "
            f"{result:8s} | {num_moves:3d} moves | "
            f"{duration:5.1f}s | running win rate: {current_rate:.0%}"
        )

    final_rate = wins / num_games
    print(f"\n  FINAL: {wins}/{num_games} wins  ({final_rate:.0%} win rate)\n")
    return wins, num_games


def main():
    print("=" * 55)
    print("  Gomoku MCTS Benchmark")
    print("  Results -> data/game_log.csv")
    print("=" * 55)

    summary = []
    for opponent_type, budget, num_games in EXPERIMENTS:
        wins, total = run_experiment(opponent_type, budget, num_games)
        summary.append((opponent_type, budget, wins, total))

    print("\n" + "=" * 55)
    print("  SUMMARY")
    print("=" * 55)
    print(f"  {'Opponent':<8} {'Budget':>8}   {'Wins':>6}   {'Win Rate':>9}")
    print(f"  {'-'*8} {'-'*8}   {'-'*6}   {'-'*9}")
    for opp, budget, wins, total in summary:
        print(f"  {opp:<8} {budget:>8,}   {wins:>4}/{total}   {wins/total:>8.0%}")

    print("\nBenchmark complete. Run analyze_results.py to generate charts.")


if __name__ == "__main__":
    main()
