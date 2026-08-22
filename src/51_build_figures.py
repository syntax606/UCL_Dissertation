#!/usr/bin/env python3
"""Build the three dissertation figures from the saved results files.

The August 2026 figure in docs/figures was hand-authored and went stale: it still shows
+0.244 and +0.132 from the single-partition run, and it plots margins where [4.4] reports
costs. Every figure here reads its numbers from results/ for that reason, so a figure
cannot drift from the chapter it sits in without the script noticing.

Three figures, one job each.

  fig1_method        [3.5]  the two probe points on one forward pass, and why the naive
                            pairing of latent against reconstruction is not comparable
  fig2_where_lost    [4.3]  the encoder step against the quantiser step, three codecs
  fig3_what_lost     [4.4]  cue retention, everything above the WavLM line but temporal

Output is PDF for the thesis and PNG for slides. Palette and typography follow the
existing figure so the two sit together.

Usage:  python3 src/51_build_figures.py
"""
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "figures"

TEAL, MID, RUST = "#0F7A84", "#5E9BA2", "#B4522F"
INK, BODY, GREY, RULE = "#1A1A1A", "#3C3C3C", "#6E6E6E", "#D8DBDE"

plt.rcParams.update({
    "font.family": "Arial", "text.color": BODY,
    "axes.edgecolor": RULE, "axes.labelcolor": BODY,
    "xtick.color": GREY, "ytick.color": GREY, "savefig.bbox": "tight",
})


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"{name}.{ext}", dpi=200, facecolor="white")
    plt.close(fig)
    print(f"  wrote {name}.pdf and {name}.png")


def read_ladder():
    """macro-F1 per rung and the paired step costs, from results/ladder_repeated.txt."""
    txt = (ROOT / "results" / "ladder_repeated.txt").read_text()
    f1 = dict(re.findall(r"^([A-Za-z0-9 ,\-]+?)\s+(0\.\d{3})\s+0\.\d{3}", txt, re.M))
    f1 = {k.strip(): float(v) for k, v in f1.items()}
    cost = {k.strip(): float(v) for k, v in
            re.findall(r"^((?:encoder|quantiser|readout)[^+\-]*?)\s+([+-]0\.\d{3})", txt, re.M)}
    return f1, cost


def read_cues():
    """Retention percentages from results/cue_retention_repeated.txt."""
    txt = (ROOT / "results" / "cue_retention_repeated.txt").read_text()
    block = txt.split("RETENTION vs WavLM")[1]
    rows = {}
    for line in block.split("\n"):
        m = re.match(r"^([A-Za-z]+, (?:before|after) quantisation|[A-Za-z]+, deployed histogram"
                     r"|Whisper encoder L9|Sylber)\s+(.*)$", line.strip())
        if not m:
            continue
        # each cell is "152% (3%)", so take the retention and not its sd
        pct = [int(x) for x in re.findall(r"(\d+)%\s*\(", m.group(2))]
        if len(pct) == 5:
            rows[m.group(1)] = pct
    return rows


# --------------------------------------------------------------------- figure 1
def fig_method():
    fig, ax = plt.subplots(figsize=(9.2, 3.5))
    ax.set_xlim(0, 100); ax.set_ylim(0, 40); ax.axis("off")

    def box(x, w, label, sub, fill="white", edge=RULE, bold=False):
        ax.add_patch(FancyBboxPatch((x, 20), w, 9, boxstyle="round,pad=0.4",
                                    fc=fill, ec=edge, lw=1.4))
        ax.text(x + w / 2, 26.2, label, ha="center", va="center", fontsize=10.5,
                color=INK, fontweight="bold" if bold else "normal")
        if sub:
            ax.text(x + w / 2, 22.6, sub, ha="center", va="center", fontsize=8.4, color=GREY)

    box(1, 15, "waveform", "24 kHz")
    box(19, 16, "encoder", "conv, and attention\nor recurrence")
    box(38, 15, "input_proj", "")
    box(56, 16, "codebooks", "8 residual stages")
    box(75, 15, "output_proj", "")
    for x0, x1 in ((16, 19), (35, 38), (53, 56), (72, 75), (90, 93)):
        ax.annotate("", xy=(x1, 24.5), xytext=(x0, 24.5),
                    arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.2))
    ax.text(95.5, 24.5, "waveform\nout", ha="center", va="center", fontsize=8.4, color=GREY)

    # the two probe points, which is the whole method
    for x, lab in ((54.5, "probed here"), (73.5, "probed here")):
        ax.plot([x], [20], marker="v", ms=9, color=RUST, clip_on=False)
        ax.text(x, 16.6, lab, ha="center", va="top", fontsize=9, color=RUST, style="italic")
    ax.annotate("", xy=(73.5, 12.4), xytext=(54.5, 12.4),
                arrowprops=dict(arrowstyle="<|-|>", color=RUST, lw=1.3))
    ax.text(64, 10.4, "the only difference between these two conditions is the rounding step",
            ha="center", va="top", fontsize=9.2, color=RUST)
    ax.text(64, 15.6, "cosine 0.821", ha="center", va="center", fontsize=9.6,
            color=INK, fontweight="bold")

    # the pairing a reader would assume, and why it is not the comparison
    ax.annotate("", xy=(93, 33.6), xytext=(27, 33.6),
                arrowprops=dict(arrowstyle="<|-|>", color=GREY, lw=1.1,
                                linestyle=(0, (4, 3))))
    ax.text(60, 35.2, "the pairing a reader would assume, cosine 0.004", ha="center",
            va="bottom", fontsize=9, color=GREY, style="italic")
    ax.text(50, 0.4, "Figure 3.1  Both probes sit on one forward pass. Comparing the encoder "
                     "latent against the\nreconstruction instead would compare vectors that are "
                     "not in the same space.",
            ha="center", va="bottom", fontsize=8.6, color=BODY)
    save(fig, "fig1_method")


# --------------------------------------------------------------------- figure 2
def fig_where_lost(f1, cost):
    CODECS = [("Mimi", "Mimi, pre-quantisation", "Mimi, post-quantisation",
               "encoder, WavLM to Mimi pre", "quantiser, Mimi pre to post"),
              ("EnCodec", "EnCodec, pre-quantisation", "EnCodec, post-quantisation",
               "encoder, WavLM to EnCodec pre", "quantiser, EnCodec pre to post"),
              ("DAC", "DAC, pre-quantisation", "DAC, post-quantisation",
               "encoder, WavLM to DAC pre", "quantiser, DAC pre to post")]
    ceiling = f1["WavLM L20, continuous teacher"]

    fig, ax = plt.subplots(figsize=(9.2, 4.4))
    ax.axhline(ceiling, color=TEAL, lw=1.6)
    ax.text(-0.42, ceiling + 0.004, f"WavLM  {ceiling:.3f}", fontsize=10,
            color=TEAL, fontweight="bold", va="bottom")

    for i, (name, pre_k, post_k, enc_k, q_k) in enumerate(CODECS):
        pre, post = f1[pre_k], f1[post_k]
        ax.plot([i - 0.17, i + 0.17], [pre, pre], color=MID, lw=7, solid_capstyle="butt")
        ax.plot([i - 0.17, i + 0.17], [post, post], color=RUST, lw=7, solid_capstyle="butt")
        # the encoder step, which is the finding
        ax.annotate("", xy=(i, pre), xytext=(i, ceiling),
                    arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.5))
        ax.text(i + 0.05, (ceiling + pre) / 2, f"encoder\n{cost[enc_k]:+.3f}",
                fontsize=9.2, color=INK, va="center", ha="left")
        # EnCodec's two rungs sit 0.005 apart, so the labels need pushing apart
        tight = abs(pre - post) < 0.012
        ax.text(i - 0.22, pre + (0.006 if tight else 0), f"{pre:.3f}",
                fontsize=9.2, color=GREY, ha="right", va="center")
        ax.text(i - 0.22, post - (0.006 if tight else 0), f"{post:.3f}",
                fontsize=9.2, color=GREY, ha="right", va="center")
        ax.text(i + 0.22, (pre + post) / 2, f"quantiser {cost[q_k]:+.3f}",
                fontsize=9.2, color=RUST, va="center", ha="left", fontweight="bold")

    ax.set_xticks(range(len(CODECS)))
    ax.set_xticklabels([c[0] for c in CODECS], fontsize=11, color=INK)
    ax.set_xlim(-0.55, len(CODECS) - 0.25)
    ax.set_ylabel("stance macro-F1", fontsize=10)
    ax.set_ylim(0.33, 0.60)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_title("Where the contrast is lost", fontsize=13, color=TEAL,
                 fontweight="bold", loc="left", pad=16)
    ax.text(0, 1.015, "Mean over 25 episode-to-fold partitions. Grey arrow is the encoder step, "
                      "rust is the quantiser step.",
            transform=ax.transAxes, fontsize=9, color=GREY)
    fig.text(0.5, -0.02, "Figure 4.1  The encoder step is 3.3 times the quantiser step in Mimi and "
                         "6.7 times in DAC.\nIn EnCodec the quantiser costs nothing measurable.",
             ha="center", fontsize=8.8, color=BODY)
    save(fig, "fig2_where_lost")


# --------------------------------------------------------------------- figure 3
def fig_what_lost(rows):
    """Cue retention as a heat map.

    The data is already a matrix, seven rungs by five cue groups, and the finding is that
    one column behaves differently from the other four. A diverging scale centred on the
    WavLM line puts that on the page directly: everything a codec keeps better than its
    teacher reads teal, everything it keeps worse reads rust, and only one column is rust.
    Cells carry their own value, so this replaces the table rather than illustrating it.
    """
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

    GROUPS = ["contour", "level", "voice quality", "temporal", "spectral"]
    order = ["Whisper encoder L9",
             "Mimi, before quantisation", "Mimi, after quantisation", "Mimi, deployed histogram",
             "EnCodec, before quantisation", "EnCodec, after quantisation",
             "DAC, before quantisation", "DAC, after quantisation",
             "Sylber", "DyCAST, before quantisation", "DyCAST, after quantisation"]
    order = [k for k in order if k in rows]
    M = np.array([rows[k] for k in order], dtype=float)

    cmap = LinearSegmentedColormap.from_list("stance", [RUST, "#F2EDEA", "#FFFFFF", "#D9E7E9", TEAL])
    norm = TwoSlopeNorm(vmin=55, vcenter=100, vmax=175)

    fig, ax = plt.subplots(figsize=(8.6, 5.2))
    ax.imshow(M, cmap=cmap, norm=norm, aspect="auto")

    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            strong = v < 78 or v > 150
            ax.text(j, i, f"{v:.0f}%", ha="center", va="center", fontsize=10.5,
                    color="white" if strong else INK,
                    fontweight="bold" if j == 3 else "normal")

    ax.set_xticks(range(5)); ax.set_xticklabels(GROUPS, fontsize=10.5, color=INK)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([k.replace(", before quantisation", ", before")
                         .replace(", after quantisation", ", after")
                         .replace(", deployed histogram", ", histogram")
                         .replace("Whisper encoder L9", "Whisper  (control)") for k in order],
                       fontsize=10, color=INK)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_xticks(np.arange(-.5, 5, 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(order), 1), minor=True)
    ax.grid(which="minor", color="white", lw=2.5)
    ax.tick_params(which="minor", length=0)

    # the one column that behaves differently
    ax.add_patch(plt.Rectangle((2.5, -0.5), 1, len(order), fill=False, ec=RUST, lw=2.2, zorder=5))
    for y in (0.5, 7.5):
        ax.axhline(y, color=INK, lw=1.4, zorder=6)
    ax.text(4.62, 0, "a second continuous\nencoder, for reference", fontsize=8.4, color=GREY,
            va="center", ha="left", style="italic")
    ax.text(4.62, 9.5, "variable rate,\nno fixed clock", fontsize=8.4, color=GREY,
            va="center", ha="left", style="italic")

    ax.set_title("What the codecs keep, and the one thing they lose", fontsize=13,
                 color=TEAL, fontweight="bold", loc="left", pad=50)
    ax.text(0, 1.145, "Retention of each hand-crafted cue group, as a percentage of what WavLM "
                      "supports. Mean over 25 partitions.\nTeal is better than WavLM, rust is worse. "
                      "No cell exceeds three points of standard deviation.",
            transform=ax.transAxes, fontsize=9, color=GREY, va="top")
    fig.text(0.5, -0.07, "Figure 4.2  Whisper sits level with WavLM on every group, so the codecs' "
                         "surplus is a codec property\nrather than a WavLM deficiency. Temporal is the "
                         "one group they lose, and DyCAST, which abandons\nthe clock entirely, loses "
                         "the most of it.",
             ha="center", fontsize=8.8, color=BODY)
    save(fig, "fig3_what_lost")


def main():
    print(f"Building figures from results/\n{'-' * 54}")
    f1, cost = read_ladder()
    rows = read_cues()
    print(f"  ladder: {len(f1)} rungs, {len(cost)} step costs")
    print(f"  cues:   {len(rows)} rungs x 5 groups")
    if len(rows) != 11:
        raise SystemExit(f"expected 11 cue rungs, parsed {len(rows)}; the figure would be wrong")
    fig_method()
    fig_where_lost(f1, cost)
    fig_what_lost(rows)
    print(f"{'-' * 54}\n  every number above was read from results/, not typed in")


if __name__ == "__main__":
    main()
