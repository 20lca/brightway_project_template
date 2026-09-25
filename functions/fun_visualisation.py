"""A small, reusable Matplotlib/Seaborn module for report-ready charts using the
2-0 LCA visual identity. The module intentionally contains no Brightway imports
and no table/export utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping, Sequence
import re
import textwrap

import matplotlib.pyplot as plt
from matplotlib import font_manager, rcParams
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
import seaborn as sns

from functions.utils import Config

COLORS = Config.COLORS
PALETTE = Config.PALETTE
RED_GRADIENT = Config.RED_GRADIENT
BLUE_GRADIENT = Config.BLUE_GRADIENT
TITLE_FONT = Config.TITLE_FONT
BODY_FONT = Config.BODY_FONT

# -----------------------------------------------------------------------------
# Styling helpers
# -----------------------------------------------------------------------------

def _available_font(preferred: str, fallbacks: Sequence[str]) -> str:
    """Return the first installed font from the preferred/fallback sequence."""
    available = {font.name for font in font_manager.fontManager.ttflist}
    for name in (preferred, *fallbacks):
        if name in available:
            return name
    return "DejaVu Sans"


def _fonts() -> tuple[str, str]:
    title = _available_font(TITLE_FONT, ("Aptos Display", "Arial", "Liberation Sans"))
    body = _available_font(BODY_FONT, ("Aptos", "Arial", "Liberation Sans"))
    return title, body


def apply_20lca_theme() -> None:
    """Apply 2-0 LCA colours, typography and Matplotlib defaults globally."""
    _, body_font = _fonts()
    rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [
                body_font,
                "Aptos",
                "Arial",
                "Liberation Sans",
                "DejaVu Sans",
            ],
            "font.size": 9,
            "axes.titlesize": 14,
            "axes.titleweight": "normal",
            "axes.titlecolor": COLORS["passion_red"],
            "axes.labelsize": 11,
            "axes.labelcolor": COLORS["dark_grey"],
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "xtick.color": COLORS["dark_grey"],
            "ytick.color": COLORS["dark_grey"],
            "legend.fontsize": 9,
            "text.color": COLORS["dark_grey"],
            "figure.facecolor": COLORS["white"],
            "axes.facecolor": COLORS["white"],
            "axes.edgecolor": COLORS["future_green"],
            "axes.linewidth": 0.6,
            "axes.grid": True,
            "grid.color": COLORS["future_green"],
            "grid.linestyle": "-",
            "grid.linewidth": 0.6,
            "grid.alpha": 0.65,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.axisbelow": True,
            "figure.dpi": 150,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.facecolor": COLORS["white"],
        }
    )
    sns.set_palette(PALETTE)


def _finish(figure: Figure, save_path: str | Path | None, show: bool) -> None:
    """Apply the shared save/show behaviour used by all plotting functions."""
    if save_path:
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(path, dpi=300, bbox_inches="tight", facecolor=COLORS["white"])
    if show:
        plt.show()


def _set_title(ax: Axes, title: str) -> None:
    title_font, _ = _fonts()
    ax.set_title(
        textwrap.fill(title, width=75),
        fontfamily=title_font,
        fontsize=14,
        color=COLORS["passion_red"],
        pad=12,
    )


def _category_colours(values: Sequence[object]) -> dict[str, str]:
    """Assign stable colours in first-occurrence order within a chart."""
    unique = list(dict.fromkeys(str(value) for value in values))
    return {name: PALETTE[index % len(PALETTE)] for index, name in enumerate(unique)}


def _subscript_formula(label: object) -> object:
    """Convert simple chemical-formula digits to Matplotlib subscripts."""
    if not isinstance(label, str):
        return label
    return re.sub(r"([A-Za-z])(\d+)", r"\1$_{\2}$", label)


# -----------------------------------------------------------------------------
# Elementary plots
# -----------------------------------------------------------------------------

def plot_bar(
    df: pd.DataFrame,
    *,
    x: str,
    y: str,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    horizontal: bool = False,
    sort: bool = False,
    color: str | None = None,
    figsize: tuple[float, float] = (7, 4),
    save_path: str | Path | None = None,
    show: bool = True,
) -> tuple[Figure, Axes]:
    """Create a basic branded bar chart from a DataFrame."""
    apply_20lca_theme()
    _, body_font = _fonts()
    data = df.copy()

    value_column = x if horizontal else y
    if sort:
        data = data.loc[data[value_column].sort_values(ascending=horizontal).index]

    figure, ax = plt.subplots(figsize=figsize)
    sns.barplot(data=data, x=x, y=y, color=color or COLORS["passion_red"], ax=ax)

    if horizontal:
        ax.axvline(0, color=COLORS["dark_grey"], linewidth=0.9)
        ax.yaxis.grid(False)
    else:
        ax.axhline(0, color=COLORS["dark_grey"], linewidth=0.9)
        ax.xaxis.grid(False)

    _set_title(ax, title)
    ax.set_xlabel(xlabel, fontfamily=body_font)
    ax.set_ylabel(ylabel, fontfamily=body_font)

    figure.tight_layout()
    _finish(figure, save_path, show)
    return figure, ax


def plot_line(
    df: pd.DataFrame,
    *,
    x: str,
    y: str,
    hue: str | None = None,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    marker: str = "o",
    figsize: tuple[float, float] = (7, 4),
    save_path: str | Path | None = None,
    show: bool = True,
) -> tuple[Figure, Axes]:
    """Create a branded line chart for trends or scenario series."""
    apply_20lca_theme()
    _, body_font = _fonts()
    figure, ax = plt.subplots(figsize=figsize)
    sns.lineplot(data=df, x=x, y=y, hue=hue, marker=marker, palette=PALETTE if hue else None, ax=ax)
    _set_title(ax, title)
    ax.set_xlabel(xlabel, fontfamily=body_font)
    ax.set_ylabel(ylabel, fontfamily=body_font)
    figure.tight_layout()
    _finish(figure, save_path, show)
    return figure, ax


def plot_scatter(
    df: pd.DataFrame,
    *,
    x: str,
    y: str,
    hue: str | None = None,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    figsize: tuple[float, float] = (7, 4),
    save_path: str | Path | None = None,
    show: bool = True,
) -> tuple[Figure, Axes]:
    """Create a branded scatter plot for relationships or sensitivity results."""
    apply_20lca_theme()
    _, body_font = _fonts()
    figure, ax = plt.subplots(figsize=figsize)
    sns.scatterplot(
        data=df,
        x=x,
        y=y,
        hue=hue,
        palette=PALETTE if hue else None,
        color=None if hue else COLORS["passion_red"],
        ax=ax,
    )
    _set_title(ax, title)
    ax.set_xlabel(xlabel, fontfamily=body_font)
    ax.set_ylabel(ylabel, fontfamily=body_font)
    figure.tight_layout()
    _finish(figure, save_path, show)
    return figure, ax


# -----------------------------------------------------------------------------
# LCA-focused plots
# -----------------------------------------------------------------------------

def plot_contribution_bar(
    df: pd.DataFrame,
    *,
    title: str = "Contribution analysis",
    unit: str = "",
    name_column: str = "name",
    score_column: str = "score",
    parent_column: str | None = "parent",
    top_n: int | None = None,
    figsize: tuple[float, float] = (7, 4),
    save_path: str | Path | None = None,
    show: bool = True,
) -> tuple[Figure, Axes]:
    """Plot an LCA contribution table as sorted horizontal bars.

    Designed for Brightway recursive contribution DataFrames containing
    ``name`` and ``score`` and, optionally, ``parent``. Positive and negative
    contributions are retained and sorting is by absolute contribution.
    """
    apply_20lca_theme()
    _, body_font = _fonts()
    data = df.copy()

    if parent_column and parent_column in data.columns:
        data = data[data[parent_column].notna()].copy()
    required = {name_column, score_column}
    missing = required - set(data.columns)
    if missing:
        raise KeyError(f"Missing required columns: {sorted(missing)}")

    data = data.loc[data[score_column].abs().sort_values(ascending=False).index]
    if top_n is not None:
        data = data.head(top_n)

    colours = [RED_GRADIENT[index % len(RED_GRADIENT)] for index in range(len(data))]
    figure, ax = plt.subplots(figsize=figsize)
    sns.barplot(
        data=data,
        y=name_column,
        x=score_column,
        hue=name_column,
        order=data[name_column],
        palette=colours,
        legend=False,
        ax=ax,
    )

    ax.axvline(0, color=COLORS["dark_grey"], linewidth=1.0)
    ax.yaxis.grid(False)
    _set_title(ax, title)
    ax.set_xlabel(unit, fontfamily=body_font)
    ax.set_ylabel("")

    labels = [_subscript_formula(label.get_text()) for label in ax.get_yticklabels()]
    ax.set_yticks(ax.get_yticks())
    ax.set_yticklabels(labels, fontfamily=body_font)

    figure.tight_layout()
    _finish(figure, save_path, show)
    return figure, ax


def plot_stacked(
    *dfs: pd.DataFrame,
    title: str = "LCA result",
    unit: str = "",
    labels: Sequence[str] | None = None,
    figsize: tuple[float, float] | None = None,
    save_path: str | Path | None = None,
    show: bool = True,
) -> tuple[Figure, Axes, dict[str, str]]:
    """Compare multiple LCA results as stacked positive/negative contributions.

    Each DataFrame must contain ``score`` plus either ``name`` or ``contributor``.
    Brightway recursive tables with a ``parent`` column are filtered to child
    contributions automatically.
    """
    apply_20lca_theme()
    _, body_font = _fonts()
    if not dfs:
        raise ValueError("plot_stacked requires at least one DataFrame.")
    if labels is None:
        labels = [f"Process {index + 1}" for index in range(len(dfs))]
    if len(labels) != len(dfs):
        raise ValueError("labels must have the same length as the supplied DataFrames.")

    def prepare(dataframe: pd.DataFrame) -> pd.DataFrame:
        if "score" not in dataframe.columns:
            raise KeyError("Each DataFrame must contain a 'score' column.")
        data = dataframe.copy()
        if "contributor" in data.columns and "name" not in data.columns:
            data = data.rename(columns={"contributor": "name"})
        if "name" not in data.columns:
            raise KeyError("Each DataFrame must contain 'name' or 'contributor'.")
        if "parent" in data.columns:
            data = data[data["parent"].notna()].copy()
        return data.reset_index(drop=True)

    processed = [prepare(df) for df in dfs]
    all_names = [str(name) for data in processed for name in data["name"]]
    colour_map = _category_colours(all_names)

    if figsize is None:
        figsize = (max(7.5, 2.2 + len(dfs) * 1.8), 5)
    figure, ax = plt.subplots(figsize=figsize)

    for x_position, data in enumerate(processed):
        positive_bottom = 0.0
        negative_bottom = 0.0
        for _, row in data.iterrows():
            score = float(row["score"])
            name = str(row["name"])
            bottom = positive_bottom if score >= 0 else negative_bottom
            ax.bar(
                x_position,
                score,
                bottom=bottom,
                width=0.55,
                color=colour_map[name],
                edgecolor=COLORS["white"],
                linewidth=0.6,
                label=name,
            )
            if score >= 0:
                positive_bottom += score
            else:
                negative_bottom += score

    ax.set_xticks(range(len(dfs)))
    ax.set_xticklabels(
        [textwrap.fill(str(label).replace("_", " "), width=18) for label in labels],
        fontfamily=body_font,
    )
    ax.set_xlabel("")
    ax.set_ylabel(unit, fontfamily=body_font)
    ax.axhline(0, color=COLORS["dark_grey"], linewidth=1.0)
    ax.xaxis.grid(False)
    _set_title(ax, title)

    handles, legend_labels = ax.get_legend_handles_labels()
    unique_handles: dict[str, object] = {}
    for handle, label in zip(handles, legend_labels):
        unique_handles.setdefault(label, handle)
    if unique_handles:
        ax.legend(
            unique_handles.values(),
            [textwrap.fill(label, width=28) for label in unique_handles],
            loc="upper center",
            bbox_to_anchor=(0.5, -0.18),
            ncol=min(3, len(unique_handles)),
            frameon=False,
            prop={"family": body_font, "size": 9},
        )
        figure.tight_layout(rect=(0, 0.18, 1, 1))
    else:
        figure.tight_layout()

    _finish(figure, save_path, show)
    return figure, ax, colour_map


def plot_pie(
    df: pd.DataFrame,
    *,
    label_column: str,
    value_column: str = "score",
    title: str = "LCA result",
    figsize: tuple[float, float] = (8, 4.5),
    save_path: str | Path | None = None,
    show: bool = True,
) -> tuple[Figure, Axes, dict[str, str]]:
    """Plot a simple positive part-to-whole composition.

    Use only when the values represent meaningful parts of one positive total.
    For contribution analyses containing negative values, prefer ``plot_stacked``
    or ``plot_contribution_bar``.
    """
    apply_20lca_theme()
    _, body_font = _fonts()
    data = df[[label_column, value_column]].dropna().copy()
    data = data[data[value_column] > 0]
    if data.empty or data[value_column].sum() <= 0:
        raise ValueError("plot_pie requires at least one positive value.")

    labels = [str(value) for value in data[label_column]]
    colour_map = _category_colours(labels)
    colours = [colour_map[label] for label in labels]

    figure, ax = plt.subplots(figsize=figsize)
    wedges, _, _ = ax.pie(
        data[value_column],
        labels=None,
        colors=colours,
        startangle=90,
        autopct=lambda pct: f"{pct:.1f}%" if pct >= 5 else "",
        pctdistance=0.7,
        textprops={"fontfamily": body_font, "fontsize": 9},
        wedgeprops={"edgecolor": COLORS["white"], "linewidth": 0.8},
    )
    _set_title(ax, title)
    ax.legend(
        wedges,
        [textwrap.fill(label, width=28) for label in labels],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.05),
        ncol=2,
        frameon=False,
        prop={"family": body_font, "size": 9},
    )
    ax.grid(False)
    figure.tight_layout(rect=(0, 0.12, 1, 1))
    _finish(figure, save_path, show)
    return figure, ax, colour_map


__all__ = [
    "COLORS",
    "PALETTE",
    "RED_GRADIENT",
    "BLUE_GRADIENT",
    "TITLE_FONT",
    "BODY_FONT",
    "apply_20lca_theme",
    "plot_bar",
    "plot_line",
    "plot_scatter",
    "plot_contribution_bar",
    "plot_stacked",
    "plot_pie",
]