# analyze_results.py — Generate charts and summary table from benchmark data
#
# Run from the project root after benchmark.py has produced data/game_log.csv:
#   python -m gomoku.evaluation.analyze_results
#
# Outputs saved to data/:
#   win_rate_vs_budget.png
#   move_time_vs_budget.png
#   win_rate_by_color.png
#   summary_table.csv

import os
import sys

try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
except ImportError:
    print("Missing dependencies. Run:  pip install pandas matplotlib")
    sys.exit(1)

GAME_LOG_PATH = "data/game_log.csv"
OUTPUT_DIR = "data"


def _load():
    if not os.path.exists(GAME_LOG_PATH):
        print(f"No data found at {GAME_LOG_PATH}. Run benchmark.py first.")
        sys.exit(1)
    df = pd.read_csv(GAME_LOG_PATH)
    df["win"] = (df["winner"] == "AI").astype(int)
    return df


# ---------------------------------------------------------------------------
# Chart 1 — Win Rate vs. Simulation Budget (vs greedy only)
# ---------------------------------------------------------------------------
def chart_win_rate_vs_budget(df):
    greedy = df[df["opponent_type"] == "greedy"]
    if greedy.empty:
        print("  [skip] No greedy games found for win_rate_vs_budget chart.")
        return

    summary = (
        greedy.groupby("budget")["win"]
        .agg(win_rate="mean", games="count")
        .reset_index()
    )
    summary["win_pct"] = summary["win_rate"] * 100

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(summary["budget"], summary["win_pct"], marker="o", linewidth=2, color="#2c7bb6")
    ax.axhline(50, linestyle="--", color="gray", linewidth=0.8, label="50% baseline")

    for _, row in summary.iterrows():
        ax.annotate(
            f"{row['win_pct']:.0f}%",
            (row["budget"], row["win_pct"]),
            textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9,
        )

    ax.set_xlabel("Simulation Budget (iterations)")
    ax.set_ylabel("Win Rate (%)")
    ax.set_title("MCTS Win Rate vs. Simulation Budget\n(opponent: greedy heuristic)")
    ax.set_ylim(0, 110)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.legend()
    ax.grid(True, alpha=0.4)
    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, "win_rate_vs_budget.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved {path}")


# ---------------------------------------------------------------------------
# Chart 2 — Average AI Move Time vs. Simulation Budget
# ---------------------------------------------------------------------------
def chart_move_time_vs_budget(df):
    summary = (
        df.groupby("budget")["avg_move_time_sec"]
        .mean()
        .reset_index()
        .rename(columns={"avg_move_time_sec": "avg_time"})
    )

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(summary["budget"], summary["avg_time"], marker="s", linewidth=2, color="#d7191c")

    for _, row in summary.iterrows():
        ax.annotate(
            f"{row['avg_time']:.2f}s",
            (row["budget"], row["avg_time"]),
            textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9,
        )

    ax.set_xlabel("Simulation Budget (iterations)")
    ax.set_ylabel("Avg AI Move Time (seconds)")
    ax.set_title("Average AI Move Time vs. Simulation Budget\n(compute cost tradeoff)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.grid(True, alpha=0.4)
    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, "move_time_vs_budget.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved {path}")


# ---------------------------------------------------------------------------
# Chart 3 — Win Rate: AI as Black vs. White
# ---------------------------------------------------------------------------
def chart_win_rate_by_color(df):
    summary = (
        df.groupby("ai_color")["win"]
        .agg(win_rate="mean", games="count")
        .reset_index()
    )
    summary["win_pct"] = summary["win_rate"] * 100

    colors = {"black": "#333333", "white": "#cccccc"}
    bar_colors = [colors.get(c, "#888888") for c in summary["ai_color"]]

    fig, ax = plt.subplots(figsize=(5, 4))
    bars = ax.bar(summary["ai_color"], summary["win_pct"],
                  color=bar_colors, edgecolor="black", width=0.5)

    for bar, (_, row) in zip(bars, summary.iterrows()):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.5,
            f"{row['win_pct']:.0f}%\n(n={row['games']})",
            ha="center", va="bottom", fontsize=9,
        )

    ax.set_xlabel("AI Color")
    ax.set_ylabel("Win Rate (%)")
    ax.set_title("Win Rate by AI Color\n(first-mover effect)")
    ax.set_ylim(0, 115)
    ax.grid(True, axis="y", alpha=0.4)
    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, "win_rate_by_color.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved {path}")


# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------
def print_summary_table(df):
    table = (
        df.groupby(["opponent_type", "budget"])
        .agg(
            games=("win", "count"),
            win_rate=("win", "mean"),
            avg_move_time=("avg_move_time_sec", "mean"),
            avg_game_len=("num_moves", "mean"),
        )
        .reset_index()
    )
    table["win_rate_pct"] = (table["win_rate"] * 100).round(1)
    table["avg_move_time"] = table["avg_move_time"].round(3)
    table["avg_game_len"] = table["avg_game_len"].round(1)

    print("\n" + "=" * 65)
    print("  SUMMARY TABLE")
    print("=" * 65)
    print(
        f"  {'Opponent':<8} {'Budget':>8}  {'Games':>6}  "
        f"{'Win%':>6}  {'Avg Move(s)':>11}  {'Avg Moves':>9}"
    )
    print(f"  {'-'*8} {'-'*8}  {'-'*6}  {'-'*6}  {'-'*11}  {'-'*9}")
    for _, row in table.iterrows():
        print(
            f"  {row['opponent_type']:<8} {int(row['budget']):>8,}  "
            f"{int(row['games']):>6}  {row['win_rate_pct']:>5.1f}%  "
            f"{row['avg_move_time']:>11.3f}  {row['avg_game_len']:>9.1f}"
        )

    csv_path = os.path.join(OUTPUT_DIR, "summary_table.csv")
    table.to_csv(csv_path, index=False)
    print(f"\n  Saved {csv_path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    print("=" * 55)
    print("  Gomoku MCTS — Result Analysis")
    print("=" * 55)

    df = _load()
    print(f"\n  Loaded {len(df)} games from {GAME_LOG_PATH}\n")

    chart_win_rate_vs_budget(df)
    chart_move_time_vs_budget(df)
    chart_win_rate_by_color(df)
    print_summary_table(df)

    print("\nAnalysis complete.")


if __name__ == "__main__":
    main()
