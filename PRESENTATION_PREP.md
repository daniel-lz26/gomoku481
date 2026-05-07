# Gomoku481 — Presentation Prep Context

**Use this file as context when continuing on a stronger machine.**
**Presentation date: 2026-05-07 (tomorrow)**

---

## Project Summary

CPSC 481, CSUF Spring 2026. Gomoku AI on a 15x15 board.

**Three AI agents implemented:**
1. **MCTS Agent** (`gomoku/ai.py`) — Monte Carlo Tree Search with heuristic rollouts, configurable simulation budget
2. **Greedy Agent** (`gomoku/agents/greedy_agent.py`) — One-step heuristic lookahead, baseline #2
3. **Random Agent** (`gomoku/agents/random_agent.py`) — Uniformly random moves, baseline #1

**Full evaluation pipeline:**
- `gomoku/evaluation/benchmark.py` — Headless game runner, logs results to `data/game_log.csv`
- `gomoku/evaluation/analyze_results.py` — Reads CSV, generates 3 charts + summary table
- `gomoku/evaluation/metrics_logger.py` — CSV logging utilities

**GUI:** `gomoku/gui.py` — Pygame, human (BLACK) vs MCTS AI (WHITE), has retry button

---

## Current State (as of 2026-05-06)

- `data/` directory is **EMPTY** — no benchmark runs have been done yet
- Code is complete and appears functional
- `gomoku/Ai.py` and `Requirements.txt` have uncommitted changes (check before running)
- The benchmark is the critical path — start it immediately when on the stronger machine

---

## Step-by-Step Instructions

### 1. Install Dependencies
```bash
pip install -r Requirements.txt
```
Required: `pygame`, `mcts`, `pandas`, `matplotlib`

---

### 2. Quick Smoke Test (~2 min)
Before running the full benchmark, verify nothing crashes.

Temporarily edit the top of `gomoku/evaluation/benchmark.py`:
```python
EXPERIMENTS = [
    ("random", 500, 1),
    ("greedy", 500, 1),
]
```
Then run:
```bash
python -m gomoku.evaluation.benchmark
```
Check: Did `data/game_log.csv` get created with 2 rows? If yes, proceed.

---

### 3. Run the Full Benchmark
Restore the full experiment config in `gomoku/evaluation/benchmark.py`:
```python
EXPERIMENTS = [
    ("random",   1_000,  20),
    ("greedy",     500,  20),
    ("greedy",   1_000,  20),
    ("greedy",   5_000,  20),
    ("greedy",  10_000,  20),
]
```
Run:
```bash
python -m gomoku.evaluation.benchmark
```
**Time estimate:** 30–90 min. Start this and let it run.

**If time is too tight**, reduce to 10 games and skip the 10K run:
```python
EXPERIMENTS = [
    ("random",   1_000,  10),
    ("greedy",     500,  10),
    ("greedy",   1_000,  10),
    ("greedy",   5_000,  10),
]
```

What it outputs per game (printed live):
```
Game 5/20 | Budget: 1000 | vs: greedy | AI color: white | Winner: AI | Moves: 47 | Time: 18.4s
```

---

### 4. Generate Charts
After benchmark completes:
```bash
python -m gomoku.evaluation.analyze_results
```

This reads `data/game_log.csv` and produces:
| File | Description |
|------|-------------|
| `data/win_rate_vs_budget.png` | MCTS win rate vs. simulation budget (key chart) |
| `data/move_time_vs_budget.png` | Avg move time vs. budget (compute/quality tradeoff) |
| `data/win_rate_by_color.png` | Win rate as BLACK vs WHITE (first-mover advantage) |
| `data/summary_table.csv` | Aggregated stats table |

---

### 5. Verify the Live Demo
```bash
python -m gomoku.gui
```
Confirm: GUI opens, human plays as BLACK, AI responds as WHITE, retry button works.

---

## Presentation Talking Points

### Architecture
- MCTS explores the game tree by simulating possible futures
- Simulation budget controls depth/quality of search (tradeoff: time vs strength)
- **Heuristic rollout** instead of random — evaluates positions using pattern scoring (five-in-a-row=1M pts, open four=100K, etc.)
- Always evaluates reward from the AI's color perspective (critical implementation detail)

### Key Metrics to Show

| Chart | What to say |
|---|---|
| `win_rate_vs_budget.png` | "More simulations = better decisions. Win rate climbs as budget increases." |
| `move_time_vs_budget.png` | "Clear compute/quality tradeoff — budget 500 is fast, 5K+ is much stronger." |
| `win_rate_by_color.png` | "First-mover (BLACK) has measurable advantage, so we alternated colors in benchmarks for fair comparison." |
| Summary table | Win rates, average game length, move time per configuration |

### Interesting Discussion Points
- Why does MCTS beat Greedy even though both use the same heuristic?
  → MCTS looks many moves ahead via tree search; Greedy only looks 1 move ahead
- Why alternate colors in the benchmark?
  → Gomoku has known first-mover advantage; fair evaluation requires controlling for this
- What would make the AI stronger?
  → Higher budget, opening book, better heuristic weights

---

## Architecture Notes (for technical questions)

- **MCTS library:** Uses `mcts` package. Does NOT negate rewards per player in backprop.
  Reward must always be from `ai_color` perspective — handled by `GomokuState.ai_color`
- **`GomokuState.getReward()`:** Returns 1.0 (win), -1.0 (loss), 0.0 (draw), or clamped heuristic score for non-terminal states
- **`GomokuState.takeAction()`:** Always clones game state before making move (no mutation)
- **Color alternation in benchmark:** Even game indices = AI plays BLACK, odd = AI plays WHITE

---

## File Map
```
gomoku481/
├── Requirements.txt
├── CHANGES.md                          (recent change log)
├── PRESENTATION_PREP.md                (this file)
├── gomoku/
│   ├── game.py                         (GomokuGame, BLACK=1, WHITE=2, EMPTY=0)
│   ├── heuristic.py                    (evaluate(board, player) -> float)
│   ├── ai.py                           (GomokuAI, GomokuState, GomokuAction)
│   ├── gui.py                          (Pygame GUI)
│   └── agents/
│       ├── random_agent.py             (RandomAgent)
│       └── greedy_agent.py             (GreedyAgent(color))
│   └── evaluation/
│       ├── metrics_logger.py           (log_game(), log_move(), LOGGING_ENABLED)
│       ├── benchmark.py                (EXPERIMENTS config + runner)
│       └── analyze_results.py          (chart generation)
└── data/                               (empty — will fill after benchmark)
```

---

## Prompt to Give Claude on the Stronger Machine

> "I'm preparing for a Gomoku AI presentation. I've attached PRESENTATION_PREP.md which has full context on the project state. The `data/` directory is empty and I need to run the benchmark pipeline to generate results. Please help me: (1) do a quick smoke test, (2) run the full benchmark, and (3) generate the charts. Let me know if anything looks broken."
