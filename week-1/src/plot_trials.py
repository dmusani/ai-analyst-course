"""Write trial conversion charts to outputs/ (never committed)."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from src.trials_analysis import cancel_timing, matured_trials, weekly_conversion  # noqa: E402

PROCESSED_PATH = Path("data/processed/trials_clean.csv")
OUTPUT_DIR = Path("outputs")

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
GRID = "#e6e5e1"
SERIES = "#2a78d6"  # categorical slot 1, single series


def _style(ax: plt.Axes) -> None:
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=INK_SECONDARY, length=0)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def plot_weekly_conversion(weekly: pd.DataFrame, overall: float, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.8), facecolor=SURFACE)
    _style(ax)
    x = range(len(weekly))
    rates = weekly["rate"] * 100
    ax.plot(x, rates, color=SERIES, linewidth=2, zorder=3)
    ax.scatter(x, rates, s=64, color=SERIES, edgecolor=SURFACE, linewidth=2, zorder=4)
    # First week is partial (Aug 1-2 only): hollow marker.
    ax.scatter(
        [0],
        [rates.iloc[0]],
        s=64,
        color=SURFACE,
        edgecolor=SERIES,
        linewidth=2,
        zorder=5,
    )
    ax.axhline(overall * 100, color=INK_SECONDARY, linewidth=1, linestyle=(0, (4, 3)))
    ax.text(
        3.5,
        overall * 100 - 4,
        f"All matured trials: {overall:.1%}",
        ha="center",
        color=INK_SECONDARY,
        fontsize=9,
    )
    for i in (0, int(rates.idxmin()), len(weekly) - 1):
        ax.annotate(
            f"{rates.iloc[i]:.1f}%",
            (i, rates.iloc[i]),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
            color=INK,
            fontsize=10,
        )
    ax.set_xticks(list(x))
    ax.set_xticklabels(
        [
            f"{d:%b} {d.day}\nn={n}"
            for d, n in zip(weekly["week_start"], weekly["trials"])
        ],
        fontsize=9,
    )
    ax.set_ylim(30, 80)
    ax.set_yticks(range(30, 81, 10))
    ax.set_yticklabels([f"{v}%" for v in range(30, 81, 10)])
    ax.set_xlabel(
        "Trial start week (Monday). First week is partial (Aug 1-2).",
        color=INK_SECONDARY,
    )
    ax.set_title(
        "Trial conversion rate by start week",
        loc="left",
        color=INK,
        fontsize=13,
        fontweight="bold",
    )
    fig.text(
        0.01,
        0.01,
        "Trials with a full 14 days to resolve (started on or before Sep 10). Y-axis starts at 30%.",
        color=INK_SECONDARY,
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(path, dpi=160, facecolor=SURFACE)
    plt.close(fig)


def plot_cancel_timing(timing: pd.Series, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.4), facecolor=SURFACE)
    _style(ax)
    days = list(range(0, 14))
    counts = [int(timing.get(d, 0)) for d in days]
    ax.bar(days, counts, color=SERIES, width=0.72, zorder=3)
    ax.text(
        1.5,
        6,
        "No cancellations in days 0-3",
        ha="center",
        color=INK_SECONDARY,
        fontsize=9,
    )
    ax.set_xticks(days)
    ax.set_xticklabels([str(d) for d in days], fontsize=9)
    ax.set_xlabel("Days from trial start to cancellation", color=INK_SECONDARY)
    ax.set_ylabel("Canceled trials", color=INK_SECONDARY)
    ax.set_title(
        "When trials cancel",
        loc="left",
        color=INK,
        fontsize=13,
        fontweight="bold",
    )
    fig.text(
        0.01,
        0.01,
        f"{sum(counts)} canceled trials among those with a full 14 days to resolve.",
        color=INK_SECONDARY,
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(path, dpi=160, facecolor=SURFACE)
    plt.close(fig)


def main() -> None:
    df = pd.read_csv(
        PROCESSED_PATH, parse_dates=["started_at", "ends_at", "outcome_at"]
    )
    matured = matured_trials(df)
    weekly = weekly_conversion(matured)
    OUTPUT_DIR.mkdir(exist_ok=True)
    plot_weekly_conversion(
        weekly, matured["converted"].mean(), OUTPUT_DIR / "trials_conversion_weekly.png"
    )
    plot_cancel_timing(cancel_timing(matured), OUTPUT_DIR / "trials_cancel_timing.png")
    print(f"Wrote charts to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
