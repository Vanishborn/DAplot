"""Matplotlib plotting for genome annotations and depth."""

from __future__ import annotations

import argparse
import datetime
import logging
import os

import numpy as np
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt

from virplot.analysis import smooth_depth
from virplot.settings import Settings

log = logging.getLogger(__name__)

# layout constants

ANNOTATION_Y_BASE = 0.5
ANNOTATION_HEIGHT = 0.6
LABEL_PAD_FRACTION = 0.02
SMALL_FEATURE_THRESHOLD = 500  # bp; features shorter than this get external labels
SMOOTH_WINDOW = 15
Y_HEADROOM = 1.05
PNG_DPI = 400
FIGURE_WIDTH = 12
FIGURE_HEIGHT = 4
HEIGHT_RATIO_ANNOTATION = 1
HEIGHT_RATIO_DEPTH = 1


def plot(
    sequence_length: int,
    features: list[dict],
    x_full: np.ndarray,
    y_list: list[np.ndarray],
    threshold_results: list[tuple],
    settings: Settings,
    labels: list[str],
    args: argparse.Namespace,
) -> None:
    """Build the combined annotation + depth figure and save to disk."""
    fig, (ax_ann, ax_depth) = plt.subplots(
        2, 1,
        figsize=(FIGURE_WIDTH, FIGURE_HEIGHT),
        sharex=True,
        gridspec_kw={"height_ratios": [HEIGHT_RATIO_ANNOTATION, HEIGHT_RATIO_DEPTH]},
    )
    fig.subplots_adjust(hspace=0)

    # --- annotation panel ---
    prime_5, prime_3 = _draw_annotations(
        ax_ann, features, sequence_length, settings, args,
    )

    # --- depth panel ---
    layers = _draw_depth(
        ax_depth, x_full, y_list, settings, args,
    )

    if args.legend:
        _add_legend(ax_depth, layers, labels, settings)

    if args.shade_breaks:
        for _, _, gaps, _ in threshold_results:
            for g in gaps:
                ax_depth.axvspan(g["start_bp"], g["end_bp"],
                                 color=settings.shade_color, alpha=0.15, lw=0)

    ax_depth.set_ylabel("Read Depth", fontsize=10)
    ax_depth.set_xlabel("Genome Position (bp)", fontsize=10)

    if args.yscale == "symlog":
        ax_depth.set_yscale("symlog", linthresh=args.linthresh, linscale=1)

    y_plot = np.sum(y_list, axis=0) if len(y_list) > 1 else y_list[0]
    if args.smooth:
        y_plot = smooth_depth(y_plot, window_size=SMOOTH_WINDOW)
    if args.normalize:
        y_plot = y_plot / (y_plot.max() or 1.0)
    ax_depth.set_ylim(0, y_plot.max() * Y_HEADROOM if y_plot.size else 1)

    if args.grid:
        ax_depth.grid(True, linestyle="--", linewidth=0.3)

    title_artist = None
    if args.title:
        title_artist = fig.text(
            0.5, 0.95, settings.title,
            ha="center", va="bottom", fontsize=14, fontweight="bold",
        )

    # --- save ---
    _save_figure(fig, args, title_artist, prime_5, prime_3)
    plt.close(fig)


# private helpers


def _draw_annotations(ax: plt.Axes, features: list[dict], seq_len: int,
                      settings: Settings, args: argparse.Namespace) -> tuple:
    """Draw genome line and feature rectangles on the annotation axis."""
    pad = int(seq_len * LABEL_PAD_FRACTION)

    ax.plot([-pad, seq_len + pad], [ANNOTATION_Y_BASE, ANNOTATION_Y_BASE],
            color="black", linewidth=1.2)
    p5 = ax.text(-pad * 0.4, ANNOTATION_Y_BASE, "5'", va="center", ha="right",
                 fontsize=10, fontweight="bold")
    p3 = ax.text(seq_len + pad * 0.4, ANNOTATION_Y_BASE, "3'", va="center", ha="left",
                 fontsize=10, fontweight="bold")

    alternate = True
    for feat in features:
        start, end = feat["start"], feat["end"]
        product = feat["product"]
        color = settings.color_mapping.get(product, settings.default_color)

        y = ANNOTATION_Y_BASE if alternate else ANNOTATION_Y_BASE - ANNOTATION_HEIGHT
        rect = Rectangle(
            (start, y), end - start, ANNOTATION_HEIGHT,
            facecolor=color,
            edgecolor="none" if args.no_border else "black",
        )
        ax.add_patch(rect)

        if not args.no_label:
            lx = (start + end) / 2
            length = end - start
            if length < SMALL_FEATURE_THRESHOLD:
                ly = (y + ANNOTATION_HEIGHT * 1.5 if alternate
                      else y - ANNOTATION_HEIGHT * 0.5)
            else:
                ly = y + ANNOTATION_HEIGHT / 2
            ax.text(lx, ly, product, ha="center", va="center",
                    fontsize=settings.annotation_fontsize, color="black")

        alternate = not alternate

    ax.set_xlim(0, seq_len)
    ax.set_ylim(-1.5, 2.0)
    ax.axis("off")
    return p5, p3


def _draw_depth(ax: plt.Axes, x_full: np.ndarray, y_list: list[np.ndarray],
                settings: Settings, args: argparse.Namespace) -> list:
    """Plot depth as a single line+fill or stacked area chart.

    Returns the layer artists for legend construction.
    """
    y_list_plot = [smooth_depth(y, window_size=SMOOTH_WINDOW) for y in y_list] if args.smooth else list(y_list)

    y_plot = np.sum(y_list_plot, axis=0) if len(y_list_plot) > 1 else y_list_plot[0]

    if args.normalize:
        denom = y_plot.max() or 1.0
        y_list_plot = [y / denom for y in y_list_plot]
        y_plot = y_plot / denom

    if len(y_list_plot) == 1:
        layers = ax.plot(x_full, y_plot, color=settings.depth_line_color,
                         linewidth=0.8, alpha=0.9)
        ax.fill_between(x_full, y_plot, color=settings.depth_line_color, alpha=0.3)
    else:
        k = len(y_list_plot)
        colors = settings.stacked_area_colors[:k] + [settings.default_color] * max(0, k - len(settings.stacked_area_colors))
        layers = ax.stackplot(x_full, *reversed(y_list_plot), colors=colors,
                              alpha=0.9, step="pre")
        ax.plot(x_full, y_plot, color="black", linewidth=0.3, alpha=0.8,
                label="Combined depth")

    ax.set_xlim(x_full[0], x_full[-1])
    return layers


def _add_legend(ax: plt.Axes, layers: list, labels: list[str],
                settings: Settings) -> None:
    """Add a legend to the depth axis."""
    legend = ax.legend(
        handles=reversed(layers),
        labels=labels,
        loc=settings.legend_location,
        fontsize=8,
        frameon=True,
        fancybox=False,
        framealpha=1.0,
        facecolor="white",
        edgecolor="black",
    )
    legend.get_frame().set_linewidth(0.5)


def _save_figure(fig: plt.Figure, args: argparse.Namespace,
                 title_artist, prime_5, prime_3) -> None:
    """Determine output path/format and save the figure."""
    os.makedirs(args.outdir, exist_ok=True)

    extra = [a for a in (title_artist, prime_5, prime_3) if a is not None]
    save_kwargs = dict(bbox_inches="tight", bbox_extra_artists=extra, pad_inches=0.05)

    ext = args.format
    if ext == "png":
        save_kwargs["dpi"] = PNG_DPI

    output_path = os.path.join(args.outdir, f"{args.name}.{ext}")

    if os.path.exists(output_path):
        ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        alt = f"{args.name}-{ts}.{ext}"
        output_path = os.path.join(args.outdir, alt)
        log.warning("File already exists. Saving to file: %s", alt)
    else:
        log.info("Saving to file: %s", os.path.basename(output_path))

    fig.savefig(output_path, format=ext, **save_kwargs)
    log.info("Plot saved to: %s", output_path)
