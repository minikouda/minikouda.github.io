#!/usr/bin/env python3
"""Regenerate the three "Ask or Commit?" carousel figures.

Typeset in the style of an AI/ML conference paper: Times New Roman body text
with STIX Two (Times-metric) math, rather than the UI sans-serif the original
figures used.

    python3 scripts/make_refgame_figures.py

Writes assets/refgame_demo.png, refgame_decision.png, refgame_result.png.
"""

import os

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle

# ── Paper typography ────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":       "serif",
    "font.serif":        ["Times New Roman", "STIX Two Text", "DejaVu Serif"],
    "mathtext.fontset":  "stix",
    "text.color":        "#1a2233",
    "savefig.facecolor": "white",
})

# ── Palette (unchanged from the original figures) ───────────────────────────
INK     = "#1a2233"
MUTED   = "#6b7280"
GREEN   = "#22b344"
GREEN_D = "#1a9c3a"
BLUE    = "#2b8df5"
GOLD    = "#f0ad3c"
YELLOW  = "#fdd017"
GREY    = "#9ca3af"
RED     = "#dc2626"
PANEL   = "#f7f8fa"
EDGE    = "#d8dce4"
TRACK   = "#eef0f4"
DARK    = "#111827"

DPI = 200
ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")


def canvas(w_units, h_units):
    """An axes measured in the same units in x and y, so circles stay round."""
    fig = plt.figure(figsize=(w_units / 20, h_units / 20), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w_units)
    ax.set_ylim(0, h_units)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def rounded(ax, x, y, w, h, r=2.0, fc="none", ec=EDGE, lw=1.2, z=1):
    ax.add_patch(FancyBboxPatch(
        (x + r, y + r), w - 2 * r, h - 2 * r,
        boxstyle=f"round,pad={r},rounding_size={r}",
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z,
    ))


def badge(ax, x, y, text, color, fs=11, pad=1.5, tc="white"):
    """A small filled pill, centred on (x, y)."""
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=tc,
            zorder=6, fontweight="bold",
            bbox=dict(boxstyle=f"round,pad={pad / 5},rounding_size=0.35",
                      facecolor=color, edgecolor="none"))


def shape(ax, kind, cx, cy, size, color, label=None, z=4):
    """Draw one scene object; `size` is the width/diameter in axis units."""
    if kind == "circle":
        ax.add_patch(Circle((cx, cy), size / 2, facecolor=color, edgecolor="none", zorder=z))
    elif kind == "square":
        ax.add_patch(Rectangle((cx - size / 2, cy - size / 2), size, size,
                               facecolor=color, edgecolor="none", zorder=z))
    elif kind == "triangle":
        h = size * 0.88
        ax.add_patch(Polygon([(cx, cy + h / 2), (cx - size / 2, cy - h / 2),
                              (cx + size / 2, cy - h / 2)],
                             closed=True, facecolor=color, edgecolor="none", zorder=z))
    if label:
        ax.text(cx, cy, label, ha="center", va="center", fontsize=10,
                color="white", fontweight="bold", zorder=z + 1)


# Objects shared by the two scene panels of figure 1, in panel-relative
# coordinates: (kind, x, y, size, colour).
SCENE = [
    ("square",   0.22, 0.74, 0.21, GREEN),
    ("square",   0.66, 0.76, 0.16, BLUE),
    ("triangle", 0.44, 0.53, 0.14, YELLOW),
    ("circle",   0.22, 0.28, 0.26, GREEN),
    ("square",   0.55, 0.25, 0.13, GREEN),
    ("square",   0.79, 0.24, 0.14, YELLOW),
]


# ───────────────────────────────────────────────────────────── figure 1 ─────
def fig_demo():
    W, H = 266, 118
    fig, ax = canvas(W, H)

    ax.text(W / 2, 109, "How a reference game works",
            ha="center", va="center", fontsize=23, fontweight="bold")

    lp = (12, 30, 60, 58)    # left panel:  x, y, w, h
    rp = (194, 30, 60, 58)   # right panel

    badge(ax, lp[0] + lp[2] / 2, 96, "1  ·  SPEAKER", BLUE)
    badge(ax, W / 2, 96, "2  ·  DESCRIBE", GOLD)
    badge(ax, rp[0] + rp[2] / 2, 96, "3  ·  LISTENER", GREEN_D)

    def draw_scene(panel, numbered):
        x, y, w, h = panel
        rounded(ax, x, y, w, h, r=2.2, fc="white", ec=EDGE)
        for i, (kind, rx, ry, rs, color) in enumerate(SCENE, start=1):
            cx, cy, size = x + rx * w, y + ry * h, rs * w
            shape(ax, kind, cx, cy, size, color, label=str(i) if numbered else None)
            if not numbered and i == 4:  # ring the secret target
                ax.add_patch(Circle((cx, cy), size / 2 + 2.6, facecolor="none",
                                    edgecolor=GOLD, linewidth=1.8, zorder=3))
                ax.text(cx, cy + size / 2 + 5.4, "target", ha="center", va="bottom",
                        fontsize=10, color=GOLD, style="italic")

    draw_scene(lp, numbered=False)
    draw_scene(rp, numbered=True)

    rounded(ax, 100, 52, 66, 20, r=2.2, fc=PANEL, ec=GOLD, lw=1.5)
    ax.text(133, 62, '“the big green circle,\nbottom-left”', ha="center", va="center",
            fontsize=15, style="italic", linespacing=1.5)
    ax.text(133, 44, "writes one short\nreferring expression", ha="center", va="center",
            fontsize=12, color=MUTED, linespacing=1.5)

    for x0, x1 in ((74, 96), (170, 192)):
        ax.annotate("", xy=(x1, 62), xytext=(x0, 62),
                    arrowprops=dict(arrowstyle="-|>", color="#586173", lw=1.6,
                                    mutation_scale=16))

    ax.text(lp[0] + lp[2] / 2, 25, "sees the scene and a secret target",
            ha="center", va="center", fontsize=12, color=MUTED)
    ax.text(rp[0] + rp[2] / 2, 25, "sees numbered objects + the description",
            ha="center", va="center", fontsize=12, color=MUTED)

    rounded(ax, 12, 6, 242, 13, r=2.0, fc=DARK, ec="none")
    ax.text(133, 12.5,
            "then it must DECIDE:   commit to its best guess     •     "
            "or ask a clarifying question?",
            ha="center", va="center", fontsize=14, color="white", zorder=5)

    return fig


# ───────────────────────────────────────────────────────────── figure 2 ─────
def fig_decision():
    W, H = 266, 122
    fig, ax = canvas(W, H)

    ax.text(W / 2, 113, "When should the agent ask a question?",
            ha="center", va="center", fontsize=23, fontweight="bold")

    cases = [
        dict(x=14, tag="CLEAR", tag_c=GREEN_D, quote="“the blue square”",
             conf=0.92, bar_c=GREEN_D, act=r"$\checkmark$   COMMIT", act_c=GREEN_D,
             note="one object matches → confidence high",
             objs=[("square", 0.26, 0.66, 0.30, BLUE, True),
                   ("circle", 0.68, 0.66, 0.22, GREEN, False),
                   ("circle", 0.26, 0.26, 0.16, GREEN, False),
                   ("triangle", 0.62, 0.24, 0.17, YELLOW, False)]),
        dict(x=139, tag="AMBIGUOUS", tag_c=GOLD, quote="“the large green triangle”",
             conf=0.50, bar_c=GOLD, act="?   ASK", act_c=GOLD,
             note="two objects match → confidence too low",
             objs=[("triangle", 0.28, 0.64, 0.26, GREEN, True),
                   ("square", 0.72, 0.70, 0.22, BLUE, False),
                   ("circle", 0.16, 0.24, 0.15, YELLOW, False),
                   ("triangle", 0.62, 0.30, 0.26, GREEN, True)]),
    ]

    for c in cases:
        px, py, pw, ph = c["x"], 12, 113, 88
        rounded(ax, px, py, pw, ph, r=2.4, fc=PANEL, ec=EDGE)
        badge(ax, px + 13, py + ph - 9, c["tag"], c["tag_c"], fs=11)

        sx, sy, sw, sh = px + 6, py + 26, 40, 40
        rounded(ax, sx, sy, sw, sh, r=1.8, fc="white", ec=EDGE)
        for kind, rx, ry, rs, color, ringed in c["objs"]:
            cx, cy, size = sx + rx * sw, sy + ry * sh, rs * sw
            shape(ax, kind, cx, cy, size, color)
            if ringed:
                ax.add_patch(Circle((cx, cy), size / 2 + 2.2, facecolor="none",
                                    edgecolor=GOLD, linewidth=1.6, zorder=3))

        rx0 = px + 52
        rw = pw - 58
        ax.text(rx0 + rw / 2, py + ph - 26, c["quote"], ha="center", va="center",
                fontsize=14, style="italic")
        ax.text(rx0 + rw / 2, py + ph - 39, "model's confidence\nin its top guess",
                ha="center", va="center", fontsize=11, color=MUTED, linespacing=1.5)

        # confidence meter with the 1 − c decision threshold
        bx, by, bw, bh = rx0 + 2, py + 26, rw - 8, 7
        thresh = 0.75
        rounded(ax, bx, by, bw, bh, r=1.2, fc=TRACK, ec="none")
        rounded(ax, bx, by, bw * c["conf"], bh, r=1.2, fc=c["bar_c"], ec="none", z=2)
        ax.plot([bx + bw * thresh] * 2, [by - 1.4, by + bh + 1.4],
                color=INK, lw=1.3, ls=(0, (3, 2)), zorder=5)
        ax.text(bx + bw * thresh, by + bh + 3.4, "$1-c$", ha="center", va="bottom",
                fontsize=12)
        ax.text(bx + bw * c["conf"] + 2.4, by + bh / 2, f"{c['conf']:.0%}",
                ha="left", va="center", fontsize=13, fontweight="bold", zorder=6)

        badge(ax, rx0 + rw / 2, py + 12, c["act"], c["act_c"], fs=16, pad=3.2)
        ax.text(px + pw / 2, py + 3.6, c["note"], ha="center", va="center",
                fontsize=11.5, color=MUTED)

    ax.text(W / 2, 5,
            "Rule:   ask only when confidence   "
            r"$\max_i \, P(\mathrm{target} = i) \;<\; 1-c$"
            "   ($c$ = cost of asking)",
            ha="center", va="center", fontsize=15)

    return fig


# ───────────────────────────────────────────────────────────── figure 3 ─────
def fig_result():
    W, H = 266, 118
    fig, ax = canvas(W, H)

    ax.text(11, 106, "The surprising result", ha="left", va="center",
            fontsize=23, fontweight="bold")
    ax.text(11, 94, "Cost-penalized score  (accuracy minus a penalty for every "
                    "question asked — higher is better)",
            ha="left", va="center", fontsize=13, color=MUTED)

    rows = [
        ("Never asks — just commits", 0.92, GREEN_D, "the simplest listener"),
        ("Direct guess",              0.74, BLUE,    None),
        ("Image-based guess",         0.30, GREY,    None),
        ("Chain-of-Thought — over-asks", 0.24, RED,   "the most ‘reasoning’"),
    ]

    x0, x1 = 96, 242          # bar track
    bh = 7.6
    ys = [77, 60, 43, 26]

    for (label, val, color, note), y in zip(rows, ys):
        ax.text(x0 - 4, y, label, ha="right", va="center", fontsize=14)
        rounded(ax, x0, y - bh / 2, x1 - x0, bh, r=1.3, fc=TRACK, ec="none")
        bw = (x1 - x0) * val
        rounded(ax, x0, y - bh / 2, bw, bh, r=1.3, fc=color, ec="none", z=2)
        ax.text(x0 + bw + 3.5, y, f"{val:.2f}", ha="left", va="center",
                fontsize=14, fontweight="bold")
        if note:
            ax.text(x0 + bw - 3, y, note, ha="right", va="center", fontsize=10.5,
                    color="white", style="italic", zorder=4)

    ax.text(11, 10,
            "More reasoning → more needless questions → lower score.  The bottleneck "
            "isn't reasoning ability,\nit's miscalibrated confidence: the model asks "
            "even when its top guess was already right.",
            ha="left", va="center", fontsize=14, linespacing=1.7)

    return fig


if __name__ == "__main__":
    for name, builder in (("refgame_demo", fig_demo),
                          ("refgame_decision", fig_decision),
                          ("refgame_result", fig_result)):
        out = os.path.join(ASSETS, f"{name}.png")
        fig = builder()
        fig.savefig(out, dpi=DPI, facecolor="white")
        plt.close(fig)
        print(f"wrote {out}")
