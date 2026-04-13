from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import scipy.stats as stats
import seaborn as sns
from scipy.stats import pearsonr, spearmanr


def _ensure_list(values: str | Sequence[str] | None) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        return [values]
    return list(values)


def plot_lineas_por_comunidad(
    df: pd.DataFrame,
    *,
    x: str,
    y: str,
    hue: str = "Sexo",
    comunidad_col: str = "Comunidades y Ciudades Autónomas",
    col_wrap: int = 4,
    marker: str = "o",
    height: float = 3.5,
    aspect: float = 1.2,
    annotate: bool = True,
    xlabel: str | None = None,
    ylabel: str | None = None,
    title: str | None = None,
) -> sns.axisgrid.FacetGrid:
    plot_df = df.copy()
    plot_df[x] = pd.to_numeric(plot_df[x], errors="coerce")
    sort_columns = [comunidad_col, x]
    if hue in plot_df.columns:
        sort_columns.insert(1, hue)
    plot_df = plot_df.sort_values(sort_columns)

    grid = sns.relplot(
        data=plot_df,
        x=x,
        y=y,
        hue=hue if hue in plot_df.columns else None,
        kind="line",
        col=comunidad_col,
        col_wrap=col_wrap,
        marker=marker,
        height=height,
        aspect=aspect,
        facet_kws={"sharey": True, "sharex": True},
    )

    grid.set_axis_labels(xlabel or x, ylabel or y)
    grid.set_titles("{col_name}")
    if title:
        grid.fig.suptitle(title, y=1.02)

    if annotate:
        for ax in grid.axes.flat:
            comunidad = ax.get_title().replace(f"{comunidad_col} = ", "")
            subset = plot_df[plot_df[comunidad_col] == comunidad]

            if hue in subset.columns:
                for _, hue_data in subset.groupby(hue, sort=False):
                    for _, row in hue_data.iterrows():
                        ax.text(
                            row[x],
                            row[y],
                            f"{row[y]:.1f}",
                            fontsize=8,
                            ha="center",
                            va="bottom",
                        )
            else:
                for _, row in subset.iterrows():
                    ax.text(
                        row[x],
                        row[y],
                        f"{row[y]:.1f}",
                        fontsize=8,
                        ha="center",
                        va="bottom",
                    )

            ax.grid(True, alpha=0.3)

    return grid


def plot_ranking_horizontal(
    df: pd.DataFrame,
    *,
    value_col: str,
    label_col: str = "Comunidades y Ciudades Autónomas",
    top_n: int | None = None,
    ascending: bool = False,
    figsize: tuple[float, float] = (10, 8),
    title: str | None = None,
    color: str = "#4C78A8",
    ax: plt.Axes | None = None,
) -> plt.Axes:
    plot_df = df.sort_values(value_col, ascending=ascending)
    if top_n is not None:
        plot_df = plot_df.head(top_n)

    if ax is None:
        _, ax = plt.subplots(figsize=figsize)

    sns.barplot(data=plot_df, x=value_col, y=label_col, color=color, ax=ax)
    ax.set_title(title or f"Ranking de {value_col}")
    ax.set_xlabel(value_col)
    ax.set_ylabel(label_col)
    ax.grid(True, axis="x", alpha=0.3)
    return ax


def plot_scatter_etiquetado(
    df: pd.DataFrame,
    *,
    x: str,
    y: str,
    label_col: str = "Comunidades y Ciudades Autónomas",
    figsize: tuple[float, float] = (8, 6),
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    text_dx: float = 50,
    text_dy: float = 0,
    ax: plt.Axes | None = None,
    scatter_kws: dict[str, Any] | None = None,
) -> plt.Axes:
    if ax is None:
        _, ax = plt.subplots(figsize=figsize)

    scatter_kws = scatter_kws or {"s": 70}
    ax.scatter(df[x], df[y], **scatter_kws)

    for _, row in df.iterrows():
        ax.text(
            row[x] + text_dx,
            row[y] + text_dy,
            row[label_col],
            fontsize=8,
        )

    ax.set_title(title or f"{y} vs {x}")
    ax.set_xlabel(xlabel or x)
    ax.set_ylabel(ylabel or y)
    ax.grid(True, alpha=0.3)
    return ax


def plot_regresion_con_stats(
    df: pd.DataFrame,
    *,
    x: str,
    y: str,
    label_col: str = "Comunidades y Ciudades Autónomas",
    group_col: str | None = None,
    metodo: str = "pearson",
    figsize_per_plot: tuple[float, float] = (8, 6),
    scatter_kws: dict[str, Any] | None = None,
    line_kws: dict[str, Any] | None = None,
    title_prefix: str = "",
) -> tuple[plt.Figure, Any]:
    scatter_kws = scatter_kws or {"s": 60}
    line_kws = line_kws or {"color": "red"}

    corr_fn = {"pearson": pearsonr, "spearman": spearmanr}.get(metodo)
    if corr_fn is None:
        raise ValueError(f"Metodo no soportado: {metodo}")

    groups = sorted(df[group_col].dropna().unique()) if group_col else [None]
    fig, axes = plt.subplots(
        1,
        len(groups),
        figsize=(figsize_per_plot[0] * len(groups), figsize_per_plot[1]),
        sharey=True,
    )

    if len(groups) == 1:
        axes = [axes]

    for ax, group_value in zip(axes, groups):
        subset = df.copy() if group_value is None else df[df[group_col] == group_value].copy()
        clean = subset[[x, y, label_col]].dropna()

        if len(clean) >= 2:
            corr, pvalue = corr_fn(clean[x], clean[y])
        else:
            corr, pvalue = float("nan"), float("nan")

        sns.regplot(
            data=clean,
            x=x,
            y=y,
            ax=ax,
            scatter_kws=scatter_kws,
            line_kws=line_kws,
        )

        for _, row in clean.iterrows():
            ax.text(
                row[x] + 50,
                row[y],
                row[label_col],
                fontsize=8,
            )

        ax.text(
            0.05,
            0.95,
            f"r = {corr:.3f}\np = {pvalue:.3f}",
            transform=ax.transAxes,
            ha="left",
            va="top",
            bbox={"facecolor": "white", "alpha": 0.8},
        )

        if group_value is None:
            ax.set_title(f"{title_prefix}{y} vs {x}")
        else:
            ax.set_title(f"{title_prefix}{group_value}")

        ax.set_xlabel(x)
        ax.grid(True, alpha=0.3)

    axes[0].set_ylabel(y)
    plt.tight_layout()
    return fig, axes


def plot_qqplots(
    df: pd.DataFrame,
    *,
    columns: Sequence[str],
    group_cols: str | Sequence[str] | None = None,
    figsize: tuple[float, float] = (10, 4),
    dist: str = "norm",
) -> list[tuple[Any, plt.Figure, Any]]:
    groups = _ensure_list(group_cols)
    figures: list[tuple[Any, plt.Figure, Any]] = []

    if not groups:
        fig, axes = plt.subplots(1, len(columns), figsize=figsize)
        if len(columns) == 1:
            axes = [axes]

        for ax, column in zip(axes, columns):
            values = pd.to_numeric(df[column], errors="coerce").dropna()
            stats.probplot(values, dist=dist, plot=ax)
            ax.set_title(column)

        plt.tight_layout()
        figures.append((None, fig, axes))
        return figures

    for group_keys, subset in df.groupby(groups, sort=True):
        fig, axes = plt.subplots(1, len(columns), figsize=figsize)
        if len(columns) == 1:
            axes = [axes]

        for ax, column in zip(axes, columns):
            values = pd.to_numeric(subset[column], errors="coerce").dropna()
            stats.probplot(values, dist=dist, plot=ax)
            ax.set_title(f"{column} - {group_keys}")

        plt.tight_layout()
        figures.append((group_keys, fig, axes))

    return figures


__all__ = [
    "plot_lineas_por_comunidad",
    "plot_qqplots",
    "plot_ranking_horizontal",
    "plot_regresion_con_stats",
    "plot_scatter_etiquetado",
]
