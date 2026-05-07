# metrics_logger.py — Lightweight CSV logging for benchmark games
#
# Two output files:
#   data/game_log.csv  — one row per game
#   data/move_log.csv  — one row per AI move (optional, higher detail)
#
# Import log_game() / log_move() from here. Both are no-ops when
# LOGGING_ENABLED = False, so this module can stay imported during
# live human-vs-AI play without producing output.

import csv
import os

LOGGING_ENABLED = True

GAME_LOG_PATH = "data/game_log.csv"
MOVE_LOG_PATH = "data/move_log.csv"

_GAME_HEADERS = [
    "game_id", "budget", "ai_color", "opponent_type",
    "winner", "num_moves", "game_duration_sec", "avg_move_time_sec",
]
_MOVE_HEADERS = [
    "game_id", "move_number", "nodes_explored", "estimated_win_rate",
]


def _ensure_file(path, headers):
    """Create the CSV file with headers if it does not exist yet."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", newline="") as f:
            csv.writer(f).writerow(headers)


def next_game_id():
    """Return the next auto-incrementing game_id based on existing rows."""
    if not os.path.exists(GAME_LOG_PATH):
        return 1
    with open(GAME_LOG_PATH, "r", newline="") as f:
        rows = list(csv.reader(f))
    # rows[0] is the header; last data row holds the most recent id
    if len(rows) <= 1:
        return 1
    try:
        return int(rows[-1][0]) + 1
    except (ValueError, IndexError):
        return len(rows)  # fallback


def log_game(game_id, budget, ai_color, opponent_type,
             winner, num_moves, game_duration_sec, avg_move_time_sec):
    """
    Append one row to data/game_log.csv.

    Parameters
    ----------
    game_id          : int    — auto-incrementing identifier
    budget           : int    — MCTS simulation count (0 for non-MCTS agents)
    ai_color         : str    — "black" or "white"
    opponent_type    : str    — "random", "greedy", or "human"
    winner           : str    — "AI", "opponent", or "draw"
    num_moves        : int    — total moves made in the game
    game_duration_sec: float  — wall-clock seconds for the full game
    avg_move_time_sec: float  — average seconds the AI spent per move
    """
    if not LOGGING_ENABLED:
        return
    _ensure_file(GAME_LOG_PATH, _GAME_HEADERS)
    with open(GAME_LOG_PATH, "a", newline="") as f:
        csv.writer(f).writerow([
            game_id, budget, ai_color, opponent_type, winner,
            num_moves, round(game_duration_sec, 3), round(avg_move_time_sec, 4),
        ])


def log_move(game_id, move_number, nodes_explored, estimated_win_rate):
    """
    Append one row to data/move_log.csv.

    Parameters
    ----------
    game_id            : int   — links to game_log.csv
    move_number        : int   — which move in the game (1-indexed)
    nodes_explored     : int   — MCTS iterations used this turn
    estimated_win_rate : float — win rate of chosen move from MCTS root
    """
    if not LOGGING_ENABLED:
        return
    _ensure_file(MOVE_LOG_PATH, _MOVE_HEADERS)
    with open(MOVE_LOG_PATH, "a", newline="") as f:
        csv.writer(f).writerow([
            game_id, move_number, nodes_explored, round(estimated_win_rate, 4),
        ])
