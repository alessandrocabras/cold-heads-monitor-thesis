from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle


OUTPUT_DIR = Path("thesis_figures")
OUTPUT_DIR.mkdir(exist_ok=True)

BLACK = "#000000"
CYAN = "#13dfe2"
GREEN = "#22c522"
RED = "#e9282f"
LIGHT_GRAY = "#f5f5f5"
PALE_CYAN = "#dffbfc"


def setup_axes(width=12, height=8, xlim=(0, 12), ylim=(0, 8)):
    fig, ax = plt.subplots(figsize=(width, height), dpi=180)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    return fig, ax


def add_box(ax, xy, w, h, text, *, facecolor="white", fontsize=16, lw=2.0):
    x, y = xy
    patch = Rectangle((x, y), w, h, facecolor=facecolor, edgecolor=BLACK, linewidth=lw)
    ax.add_patch(patch)
    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        color=BLACK,
        linespacing=0.95,
    )
    return patch


def add_arrow(ax, start, end, *, color=BLACK, lw=2.5, mutation_scale=18, style="-|>"):
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle=style,
        mutation_scale=mutation_scale,
        linewidth=lw,
        color=color,
        shrinkA=0,
        shrinkB=0,
        capstyle="butt",
        joinstyle="miter",
    )
    ax.add_patch(arrow)
    return arrow


def add_polyline_arrow(ax, points, *, color=BLACK, lw=2.5, mutation_scale=18):
    xs, ys = zip(*points)
    ax.plot(xs[:-1], ys[:-1], color=color, linewidth=lw, solid_capstyle="butt")
    add_arrow(ax, points[-2], points[-1], color=color, lw=lw, mutation_scale=mutation_scale)


def add_bus_marker(ax, xy, label, *, angle=55, fontsize=18):
    x, y = xy
    dx = 0.10
    dy = 0.16
    ax.plot([x - dx, x + dx], [y - dy, y + dy], color=BLACK, linewidth=2.0)
    ax.text(x + 0.18, y, label, ha="left", va="center", fontsize=fontsize)


def generate_chm_integration_schematic():
    fig, ax = setup_axes(width=11.5, height=9.2, xlim=(0, 11.5), ylim=(0, 9.2))

    # Main blocks.
    add_box(ax, (0.7, 4.25), 4.1, 4.0, "", fontsize=30, lw=2.1)
    ax.text(2.75, 7.68, "COMPRESSOR", ha="center", va="center", fontsize=28)
    add_box(ax, (8.7, 4.45), 2.0, 2.1, "COLD\nHEAD", fontsize=30, lw=2.1)
    add_box(ax, (5.35, 1.55), 2.1, 2.25, "COLD\nHEAD\nMONITOR", facecolor=CYAN, fontsize=18, lw=2.0)

    # Compressor ports.
    ax.text(1.55, 6.78, "On-Board\nPower", ha="center", va="center", fontsize=12, linespacing=0.9)
    ax.text(2.75, 6.78, "Helium\nReturn", ha="center", va="center", fontsize=12, linespacing=0.9)
    ax.text(3.95, 6.78, "Helium\nSupply", ha="center", va="center", fontsize=12, linespacing=0.9)
    for x, color in [(1.55, BLACK), (2.75, RED), (3.95, GREEN)]:
        circle = plt.Circle((x, 6.42), 0.12, edgecolor=BLACK, facecolor="white", linewidth=1.0)
        ax.add_patch(circle)
        ax.plot([x, x], [6.42, 6.05], color=color, linewidth=2.4)

    # 400 VAC input.
    ax.text(2.7, 9.15, "400 VAC\nIN", ha="center", va="top", fontsize=22, linespacing=0.85)
    add_arrow(ax, (2.7, 8.62), (2.7, 8.25), lw=2.4, mutation_scale=18)
    ax.plot([2.95, 3.12], [8.42, 8.62], color=BLACK, linewidth=2.0)
    ax.text(3.18, 8.53, "4", ha="left", va="center", fontsize=17)

    # Helium lines.
    ax.plot([3.95, 3.95], [6.05, 6.05], color=GREEN, linewidth=2.6)
    add_arrow(ax, (3.95, 6.05), (8.7, 6.05), color=GREEN, lw=2.6, mutation_scale=18)
    ax.text(6.45, 6.33, "Helium Supply", color=BLACK, fontsize=20, ha="center")

    add_arrow(ax, (2.75, 5.45), (8.7, 5.45), color=RED, lw=2.6, mutation_scale=18)
    ax.plot([2.75, 2.75], [6.42, 5.45], color=RED, linewidth=2.6)
    ax.text(6.45, 5.73, "Helium Return", color=BLACK, fontsize=20, ha="center")

    # Power path from compressor to CHM.
    ax.plot([1.55, 1.55, 5.0], [6.3, 4.75, 4.75], color=BLACK, linewidth=2.6)
    ax.text(2.82, 4.93, "L1, L2, L3, E", fontsize=18, ha="center")
    add_polyline_arrow(ax, [(5.0, 4.75), (5.0, 2.7), (5.35, 2.7)], lw=2.6, mutation_scale=18)
    add_bus_marker(ax, (4.9, 2.95), "4", fontsize=17)

    # Power path from CHM to cold head.
    add_polyline_arrow(ax, [(7.45, 2.7), (7.95, 2.7), (7.95, 5.0), (8.7, 5.0)], lw=2.6, mutation_scale=18)
    ax.text(8.35, 3.45, "L1, L2, L3, E", fontsize=18, ha="left")
    add_bus_marker(ax, (8.05, 2.95), "4", fontsize=17)

    # Ethernet.
    add_arrow(ax, (6.4, 3.8), (6.4, 4.45), lw=2.2, mutation_scale=16)
    ax.text(6.55, 4.08, "ETH", fontsize=18, ha="left")

    # 230 VAC input.
    ax.text(6.35, 0.15, "230 VAC\nIN", ha="center", va="bottom", fontsize=22, linespacing=0.85)
    add_arrow(ax, (6.35, 0.8), (6.35, 1.55), lw=2.4, mutation_scale=18)
    add_bus_marker(ax, (6.35, 0.9), "3", fontsize=17)

    out = OUTPUT_DIR / "chm_integration_schematic.png"
    fig.savefig(out, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print(f"saved {out}")


def generate_monitoring_update_workflow():
    fig, ax = setup_axes(width=11.5, height=8.3, xlim=(0, 11.5), ylim=(0, 8.3))

    # Left-to-right monitoring chain.
    add_box(ax, (0.45, 6.55), 2.1, 0.75, "Three-channel\nacquisition", fontsize=12)
    add_box(ax, (3.0, 6.55), 1.85, 0.75, "128-point\nwindow", fontsize=12)
    add_box(ax, (5.3, 6.55), 2.35, 0.75, "Select\nCHANNEL_INDEX=1", fontsize=11)
    add_box(ax, (8.1, 6.55), 2.9, 0.75, "Feature extraction\nor raw waveform model", facecolor=PALE_CYAN, fontsize=11)

    add_arrow(ax, (2.55, 6.93), (3.0, 6.93), lw=1.8, mutation_scale=14)
    add_arrow(ax, (4.85, 6.93), (5.3, 6.93), lw=1.8, mutation_scale=14)
    add_arrow(ax, (7.65, 6.93), (8.1, 6.93), lw=1.8, mutation_scale=14)

    # Decision and outputs.
    add_box(ax, (4.35, 4.55), 2.8, 0.9, "Known domain?", facecolor=LIGHT_GRAY, fontsize=14)
    add_arrow(ax, (9.55, 6.55), (5.75, 5.45), lw=1.8, mutation_scale=14)

    add_box(ax, (1.25, 2.85), 3.05, 0.95, "Known status\nNormal, Maintenance, Down", fontsize=13)
    add_box(ax, (7.25, 2.85), 3.15, 0.95, "Unknown Anomaly\nstore for engineering review", facecolor=LIGHT_GRAY, fontsize=12)

    add_arrow(ax, (4.65, 4.55), (3.0, 3.8), lw=1.9, mutation_scale=15)
    ax.text(3.45, 4.25, "yes", fontsize=12, ha="center")
    add_arrow(ax, (6.85, 4.55), (8.8, 3.8), lw=1.9, mutation_scale=15)
    ax.text(8.05, 4.25, "no", fontsize=12, ha="center")

    # Controlled update path.
    add_box(ax, (7.25, 1.45), 3.15, 0.9, "Verified new data\nlabel, inspect, group", facecolor=LIGHT_GRAY, fontsize=12)
    add_box(ax, (7.25, 0.2), 3.15, 0.9, "Retrain, validate, version\nand deploy later model", facecolor=PALE_CYAN, fontsize=12)

    add_arrow(ax, (8.8, 2.85), (8.8, 2.35), lw=1.9, mutation_scale=15)
    add_arrow(ax, (8.8, 1.45), (8.8, 1.1), lw=1.9, mutation_scale=15)

    add_polyline_arrow(
        ax,
        [(7.25, 0.65), (5.75, 0.65), (5.75, 4.55)],
        lw=1.9,
        mutation_scale=15,
    )
    ax.text(5.38, 2.3, "controlled\nmodel update", fontsize=11, ha="right", va="center")

    out = OUTPUT_DIR / "monitoring_model_update_workflow.png"
    fig.savefig(out, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print(f"saved {out}")


if __name__ == "__main__":
    generate_chm_integration_schematic()
    generate_monitoring_update_workflow()
