"""
Gambar untuk slide Minggu 0 — Residual (Skip) Connections.

    pip install matplotlib
    python make_figures_w0_05.py      # output -> images/w0_05_*.png
"""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": ["Helvetica Neue", "DejaVu Sans"], "font.size": 12})
PRIMARY, ACCENT, WARN, OK = "#1e3a8a", "#0ea5e9", "#dc2626", "#16a34a"


def box(ax, x, y, text, fc="#e0f2fe", w=2.2, h=0.55):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.03,rounding_size=0.12",
                                fc=fc, ec=PRIMARY, lw=1.6))
    ax.text(x, y, text, ha="center", va="center", fontsize=12)


def arrow(ax, p, q, color="#334155", rad=0.0, lw=1.6):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=14, color=color, lw=lw,
                                 connectionstyle=f"arc3,rad={rad}"))


def blocks():
    fig, axes = plt.subplots(1, 3, figsize=(14, 5.6))
    specs = [
        ("Blok biasa (plain)", ["3×3 conv, 64", "BN + ReLU", "3×3 conv, 64", "BN"], False, "ReLU"),
        ("Blok residual dasar", ["3×3 conv, 64", "BN + ReLU", "3×3 conv, 64", "BN"], True, "ReLU"),
        ("Blok bottleneck (256-d)", ["1×1 conv, 64", "3×3 conv, 64", "1×1 conv, 256", "BN"], True, "ReLU"),  # BN+ReLU antar-conv disederhanakan
    ]
    for ax, (title, layers, skip, act) in zip(axes, specs):
        ys = [4.2, 3.3, 2.4, 1.5]
        ax.text(0, 5.4, "x", ha="center", fontsize=14, weight="bold")
        arrow(ax, (0, 5.25), (0, ys[0] + 0.3))
        for i, (yy, t) in enumerate(zip(ys, layers)):
            box(ax, 0, yy, t, fc="#fef3c7" if "conv" in t else "#e0f2fe")
            if i < len(ys) - 1:
                arrow(ax, (0, yy - 0.28), (0, ys[i + 1] + 0.28))
        if skip:
            ax.add_patch(plt.Circle((0, 0.65), 0.22, fc="white", ec=OK, lw=2))
            ax.text(0, 0.65, "+", ha="center", va="center", fontsize=16, color=OK, weight="bold")
            arrow(ax, (0, ys[-1] - 0.28), (0, 0.88))
            ax.plot([0, 1.6, 1.6], [4.95, 4.95, 0.65], color=OK, lw=2.2)
            arrow(ax, (1.6, 0.65), (0.24, 0.65), color=OK, lw=2.2)
            ax.text(2.0, 2.9, "identitas\nx", color=OK, ha="center", weight="bold")
            arrow(ax, (0, 0.43), (0, -0.05))
            box(ax, 0, -0.35, act, w=1.2, h=0.45)
            ax.text(0, -1.05, "y = ReLU(F(x) + x)", ha="center", color=PRIMARY)
        else:
            arrow(ax, (0, ys[-1] - 0.28), (0, -0.05))
            box(ax, 0, -0.35, act, w=1.2, h=0.45)
            ax.text(0, -1.05, "y = ReLU(H(x))", ha="center", color=PRIMARY)
        ax.set_title(title, color=PRIMARY, weight="bold")
        if "bottleneck" in title:
            ax.text(0, -1.4, "(BN + ReLU di antara conv tidak digambar)", ha="center", fontsize=9, color="#64748b")
        ax.set_xlim(-2.4, 2.6)
        ax.set_ylim(-1.6, 5.8)
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(OUT / "w0_05_blocks.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    blocks()
    print("Gambar tersimpan di", OUT)
