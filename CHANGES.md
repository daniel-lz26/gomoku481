# Evaluation & Metrics — Implementation Summary

## What Was Added

This document explains every file added or modified as part of the evaluation and
metrics implementation for the Gomoku MCTS project (CPSC 481, CSUF Spring 2026).

---

## Bug Fix: `gomoku/ai.py`

### Problem
`getReward()` was hardcoded to return a reward from **WHITE's perspective**. When the
MCTS engine needed to play as BLACK (e.g., in benchmarks where AI alternates color),
it would evaluate positions as if it were the opponent — effectively playing badly on
purpose.

### Fix
`GomokuState` now accepts an `ai_color` parameter (default `WHITE` for backward
compatibility). `getReward()` uses `ai_color` to determine which win/loss is +1 or −1.

`GomokuAI` also gains a `color` parameter:

```python
# Before
ai = GomokuAI(simulation_budget=1000)         # always WHITE

# After
ai = GomokuAI(simulation_budget=1000, color=BLACK)   # or WHITE
```

The existing human-vs-AI GUI is unaffected because `GomokuAI()` still defaults to
`color=WHITE`.

---

## New Files

### `gomoku/agents/random_agent.py`

The weakest possible baseline. Picks a uniformly random move from the legal move list.

**Purpose:** Sanity check. MCTS should win 90%+ of games against this agent.
If it doesn't, something is fundamentally wrong with the MCTS setup.

```python
from gomoku.agents.random_agent import RandomAgent
agent = RandomAgent()
move = agent.get_best_move(game)   # returns (row, col)
```

---

### `gomoku/agents/greedy_agent.py`

One-step lookahead heuristic agent. Evaluates every legal move by calling the same
`evaluate()` function that MCTS uses for rollouts, and picks the highest-scoring move.
No tree search — pure heuristic.

**Purpose:** The meaningful baseline. Beating the greedy agent consistently proves that
the MCTS tree search adds real strategic value beyond what the heuristic alone can see.
This is the core experimental claim of the project.

```python
from gomoku.agents.greedy_agent import GreedyAgent
from gomoku.game import BLACK
agent = GreedyAgent(color=BLACK)
move = agent.get_best_move(game)
```

**Implementation note:** Uses `game.clone()` before simulating each move to avoid
mutating the real game state. Includes an early-exit optimization: if any move wins
the game immediately, it takes it without evaluating further.

---

### `gomoku/evaluation/metrics_logger.py`

Lightweight CSV logger. Writes one row per game to `data/game_log.csv` and one row
per AI move to `data/move_log.csv`.

**Designed to be non-intrusive:** A single `LOGGING_ENABLED = True/False` flag at the
top of the file lets you disable all output during live human-vs-AI play without
changing any call sites.

**Game-level log fields:**

| Field | Description |
|---|---|
| `game_id` | Auto-incrementing integer |
| `budget` | MCTS simulation count used |
| `ai_color` | `"black"` or `"white"` |
| `opponent_type` | `"random"`, `"greedy"`, or `"human"` |
| `winner` | `"AI"`, `"opponent"`, or `"draw"` |
| `num_moves` | Total moves in the game |
| `game_duration_sec` | Wall-clock time for the full game |
| `avg_move_time_sec` | Average time the AI spent per move |

**Example row:**
```
1, 1000, black, greedy, AI, 47, 18.4, 0.391
```

**Move-level log fields** (optional detail, used by `log_move()`):

| Field | Description |
|---|---|
| `game_id` | Links to game_log.csv |
| `move_number` | Which move in the game (1-indexed) |
| `nodes_explored` | MCTS iterations used that turn |
| `estimated_win_rate` | Win rate of chosen move from MCTS root |

---

### `gomoku/evaluation/benchmark.py`

Headless game runner. Runs all experiments automatically with no Pygame window.

**How to run:**
```bash
python -m gomoku.evaluation.benchmark
```

**Experiment matrix** (configurable via the `EXPERIMENTS` list at the top of the file):

| Opponent | Budget | Games |
|---|---|---|
| Random | 1,000 | 20 |
| Greedy | 500 | 20 |
| Greedy | 1,000 | 20 |
| Greedy | 5,000 | 20 |
| Greedy | 10,000 | 20 |

**Key design decisions:**
- AI color **alternates** every game (black on even games, white on odd) to control
  for the first-mover advantage inherent in Gomoku.
- Each game result is logged immediately so a partial run still produces usable data
  if you interrupt early.
- Progress is printed to the terminal in real time including the running win rate.

**Sample terminal output:**
```
-------------------------------------------------------
  GREEDY  | budget= 1,000 | 20 games
-------------------------------------------------------
  Game  1/20 | AI=black | AI       |  43 moves |  18.4s | running win rate: 100%
  Game  2/20 | AI=white | opponent |  51 moves |  22.1s | running win rate: 50%
  ...
  FINAL: 14/20 wins  (70% win rate)
```

---

### `gomoku/evaluation/analyze_results.py`

Generates charts and a summary table from `data/game_log.csv`.

**How to run** (after benchmark.py has produced data):
```bash
python -m gomoku.evaluation.analyze_results
```

**Outputs:**

| File | Description |
|---|---|
| `data/win_rate_vs_budget.png` | Line chart: MCTS win rate vs. simulation budget (vs greedy) |
| `data/move_time_vs_budget.png` | Line chart: avg AI move time vs. budget (compute tradeoff) |
| `data/win_rate_by_color.png` | Bar chart: win rate when AI plays black vs. white |
| `data/summary_table.csv` | Full summary table for all conditions |

**Chart 1 — Win Rate vs. Budget** is the most important chart for the presentation.
It shows whether more computation translates to better play, which is the central
question for MCTS performance evaluation.

**Chart 2 — Move Time vs. Budget** quantifies the compute cost of each budget level,
allowing a clear tradeoff argument: "MCTS at 5,000 iterations wins X% more often than
at 1,000 iterations, at the cost of Y additional seconds per move."

**Chart 3 — Win Rate by Color** reveals whether the first-mover advantage (black moves
first in Gomoku) is significant. Since the benchmark alternates colors, this also
validates that the evaluation is unbiased.

---

## File Structure Added

```
gomoku/
├── agents/
│   ├── __init__.py
│   ├── random_agent.py        ← weakest baseline
│   └── greedy_agent.py        ← heuristic-only baseline
└── evaluation/
    ├── __init__.py
    ├── metrics_logger.py      ← CSV logging module
    ├── benchmark.py           ← headless game runner
    └── analyze_results.py     ← charts + summary table
data/
    ├── game_log.csv           ← generated by benchmark.py
    ├── move_log.csv           ← generated if log_move() is called
    ├── summary_table.csv      ← generated by analyze_results.py
    ├── win_rate_vs_budget.png
    ├── move_time_vs_budget.png
    └── win_rate_by_color.png
requirements.txt               ← added pandas, matplotlib
```

---

## How to Run the Full Evaluation Pipeline

```bash
# 1. Install new dependencies
pip install -r requirements.txt

# 2. Run all benchmark experiments (writes data/game_log.csv)
#    Warning: full matrix takes ~30–90 minutes depending on hardware
python -m gomoku.evaluation.benchmark

# 3. Generate charts and summary table
python -m gomoku.evaluation.analyze_results
```

To run a quick smoke test with fewer games, edit the `EXPERIMENTS` list in
`benchmark.py` and change `num_games` to a smaller number (e.g., 3).

---

## Presentation Talking Points

1. **Baseline comparison:** "We implemented two baselines — a random agent and a
   greedy agent that applies the heuristic without tree search. MCTS at 1,000
   iterations beat the random agent X% of the time and the greedy agent Y% of the
   time."

2. **Budget tradeoff:** "Increasing the simulation budget from 500 to 10,000 raised
   the win rate against greedy from X% to Y%, but increased average move time from
   A seconds to B seconds. This is the core compute-quality tradeoff in MCTS."

3. **First-mover effect:** "Black (first mover) won Z% of the time overall. By
   alternating AI color in our experiments, we ensured the win rate numbers aren't
   inflated by always giving the AI the first-move advantage."

4. **Why MCTS beats greedy:** "The greedy agent picks the locally best move according
   to the heuristic. MCTS looks further ahead by simulating many possible continuations.
   The win rate gap between them quantifies how much lookahead is worth."
