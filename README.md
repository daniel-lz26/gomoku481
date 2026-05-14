# Gomoku AI: A Monte Carlo Tree Search Agent with Heuristic Evaluation

**Author:** Daniel Lopez
**Course:** CPSC 481, California State University Fullerton, Spring 2026

---

## Problem Statement

Gomoku is a two-player strategy game played on a 15x15 grid. Players alternate placing stones, and the first player to place five consecutive pieces in any direction (horizontal, vertical, or diagonal) wins. Black always moves first.

Gomoku is a good AI problem because the search space is far too large to enumerate exhaustively. On a 15x15 board with typical move counts, brute-force search is computationally infeasible. The AI must instead use a guided search algorithm paired with a smart evaluation function to identify strong moves within a fixed time budget.

This project builds a fully playable human-vs-AI Gomoku game. The AI uses Monte Carlo Tree Search (MCTS) combined with a custom heuristic board evaluation function. The project also includes two simpler baseline agents and a benchmarking pipeline to measure how well the MCTS agent performs as its search budget increases.

---

## Approach

The AI uses Monte Carlo Tree Search via the `mcts` Python library. MCTS was not implemented from scratch. The work in this project is in adapting the game to the library's interface and designing the evaluation function that drives the search.

MCTS works by building a partial game tree over many iterations. Each iteration selects a promising node using the UCB1 formula, expands it with a new child, runs a rollout from that child, and propagates the result back up the tree. After all iterations, the move with the highest visit count is returned.

In standard MCTS, rollouts use random play. This project replaces random rollouts with an immediate call to the heuristic evaluation function. This makes each simulation more informative, allowing the AI to play well at modest budgets (500 to 1000 iterations).

The heuristic evaluation function scores a board position from one player's perspective by scanning every row, column, and diagonal for patterns. It assigns large scores to patterns like open fours and open threes, and subtracts the opponent's pattern scores, so the AI considers both attack and defense.

Move candidate pruning limits the set of legal moves to cells within two squares of any existing piece on the board. This cuts the branching factor significantly and makes the search much faster without sacrificing move quality in typical positions.

The simulation budget parameter controls AI difficulty. A higher budget means more iterations per move, stronger play, and slower response time.

---

## Project Structure

```
gomoku481/
|
+-- main.py
+-- requirements.txt
+-- README.md
|
+-- gomoku/
|   +-- __init__.py
|   +-- game.py
|   +-- heuristic.py
|   +-- ai.py
|   +-- gui.py
|   |
|   +-- agents/
|   |   +-- random_agent.py
|   |   +-- greedy_agent.py
|   |
|   +-- evaluation/
|       +-- benchmark.py
|       +-- metrics_logger.py
|       +-- analyze_results.py
|
+-- tests/
|   +-- test_game.py
|   +-- test_heuristic.py
|
+-- data/
    +-- game_log.csv
    +-- summary_table.csv
    +-- win_rate_vs_budget.png
    +-- move_time_vs_budget.png
    +-- win_rate_by_color.png
```

---

## File Descriptions

### `main.py`

The entry point for the application. It imports `run_game` from `gui.py` and calls it. Running this file starts the Pygame window and begins a human-vs-AI game. No logic lives here; it exists solely to launch the program.

---

### `gomoku/game.py`

The game engine. It contains the `GomokuGame` class and enforces all Gomoku rules with no knowledge of AI or rendering. The board is represented as a 15x15 list of integers where `EMPTY=0`, `BLACK=1`, and `WHITE=2`. Key methods include `make_move`, which places a piece and checks for a win; `get_legal_moves`, which returns only cells within two squares of existing pieces to limit the search space; `check_win`, which scans all four directions from the last-placed stone; and `clone`, which returns a full independent copy of the board state. The `clone` method is critical because MCTS calls it thousands of times per move to simulate futures without modifying the real game. Every other file in the project depends on this one.

---

### `gomoku/heuristic.py`

The board evaluation function. It contains `evaluate(board, player)`, which returns a floating-point score representing how favorable the current board position is for the given player. The function scans every row, column, and both diagonal directions. For each line it identifies consecutive runs of the player's pieces and classifies them by length and how open their ends are. An open four scores 100,000 points, a blocked four scores 10,000, an open three scores 1,000, and so on up to a completed five-in-a-row which scores 1,000,000. The final result is the sum of the player's pattern scores minus the opponent's pattern scores. This function is the main intellectual contribution of the project and directly determines how well the AI plays. It is used during MCTS rollouts in `ai.py` and as the sole decision criterion in `greedy_agent.py`.

---

### `gomoku/ai.py`

The MCTS integration layer. It contains three classes. `GomokuAction` is a lightweight hashable wrapper around a `(row, col)` coordinate, which the `mcts` library requires. `GomokuState` adapts a `GomokuGame` instance to the interface the library expects: `getPossibleActions` returns the list of legal moves, `takeAction` returns a new state after applying a move, and `getReward` returns a score between -1 and 1 from the AI's fixed perspective. `GomokuAI` is the public-facing class used by the GUI and the benchmark. It accepts a `simulation_budget` parameter and exposes `get_best_move(game)`, which runs the MCTS search and returns a `(row, col)` coordinate. The reward signal is always computed from one fixed player's perspective throughout the entire tree because the `mcts` library does not flip rewards between players automatically. Getting this wrong would cause the AI to play against itself.

---

### `gomoku/gui.py`

The graphical interface built with Pygame. It draws the board grid, renders stone pieces, highlights the most recent move with a marker, and shows an overlay when the game ends along with a Retry button. The function `pixel_to_cell` converts a mouse click position into a board grid coordinate. The function `run_game` contains the main event loop: it waits for the human to click, calls `game.make_move`, then calls `ai.get_best_move` and displays a status message while MCTS is running. The human always plays as Black and the AI always plays as White. This file connects `game.py`, `ai.py`, and the Pygame display layer.

---

### `gomoku/agents/random_agent.py`

A baseline agent that picks a uniformly random legal move on each turn. It requires no heuristic or search and serves as a lower bound on performance. The MCTS agent should beat this opponent easily and consistently. A failure to do so would indicate a bug in the AI or the reward signal.

---

### `gomoku/agents/greedy_agent.py`

A one-step lookahead baseline agent. For every legal move, it clones the board using `game.clone()`, applies the move, and scores the resulting position with `heuristic.evaluate()`. It then picks the move with the highest score. There is no tree search; it considers exactly one move into the future. This is the meaningful baseline for the project. If the MCTS agent consistently beats the Greedy agent, it demonstrates that the tree search adds genuine value beyond what the heuristic alone can provide.

---

### `gomoku/evaluation/benchmark.py`

A headless game runner that executes many complete games without opening a Pygame window. It runs MCTS at budgets of 500, 1000, 5000, and 10000 against the Greedy agent, and MCTS at 1000 against the Random agent, with 20 games per condition. The AI's color alternates between Black and White across games to control for first-mover advantage. Results are written to `data/game_log.csv` via `metrics_logger.py`. This file is run as a module with `python -m gomoku.evaluation.benchmark`.

---

### `gomoku/evaluation/metrics_logger.py`

Handles writing benchmark results to disk. The function `log_game` appends one row to `data/game_log.csv` containing the game ID, simulation budget, AI color, opponent type, winner, total moves, game duration, and average AI move time. The function `next_game_id` reads the last row of the CSV to auto-increment the game counter across separate benchmark runs. The `LOGGING_ENABLED` flag at the top of the file is set to `False` during live GUI play so that normal games do not produce CSV output.

---

### `gomoku/evaluation/analyze_results.py`

Reads `data/game_log.csv` produced by the benchmark and generates three charts. `win_rate_vs_budget.png` shows whether giving MCTS more simulations increases its win rate against the Greedy agent. `move_time_vs_budget.png` shows the performance cost of increasing the budget. `win_rate_by_color.png` shows whether the AI wins more often when it plays Black (the first mover). A `summary_table.csv` of aggregated statistics is also saved. This file is run as a module with `python -m gomoku.evaluation.analyze_results`.

---

### `tests/test_game.py`

Unit tests for the game engine using `pytest`. The tests verify that the initial board state is empty, that `make_move` places pieces correctly, that `undo_move` restores the previous state, that `check_win` detects five-in-a-row in all four directions, that draw detection works when the board fills completely, and that `clone` produces a fully independent copy so that modifying the clone does not affect the original.

---

### `tests/test_heuristic.py`

Sanity checks for the evaluation function. The tests verify that a completed five-in-a-row scores at the maximum win threshold, that an empty board scores zero, and that a board position that is threatening for the opponent scores negatively from the current player's perspective.

---

## How to Run

```bash
# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run the game (human vs AI)
python main.py

# Run the automated benchmark (headless, no window)
python -m gomoku.evaluation.benchmark

# Generate charts from benchmark results
python -m gomoku.evaluation.analyze_results

# Run unit tests
python -m pytest tests/
```

---

## How to Play

You play as Black. The AI plays as White. Click any intersection on the board to place your piece. The AI will respond automatically after your move. The first player to place five pieces in a row in any direction wins. To change the AI difficulty, open `gui.py` and adjust the `simulation_budget` value passed to `GomokuAI`. Suggested values: 200 for easy, 500 for medium, 1000 for hard.

---

## Component Diagram

```
Human clicks board
       |
       v
   gui.py
   draws board, handles input
       |
       v
   game.py
   enforces rules, updates board state
       |
       v
   ai.py
   wraps game state, calls MCTS library
       |
       v
   heuristic.py
   scores board positions to guide MCTS
```

---

## Libraries and Dependencies

| Library | Version | Purpose |
|---|---|---|
| `pygame` | 2.5.0+ | Game window, board rendering, mouse input |
| `mcts` | 1.0.3+ | Monte Carlo Tree Search algorithm |
| `pandas` | 2.0.0+ | Reading and aggregating benchmark CSV data |
| `matplotlib` | 3.7.0+ | Generating result charts |

No external datasets were used. The AI learns entirely through MCTS simulation guided by the hand-crafted heuristic function.
