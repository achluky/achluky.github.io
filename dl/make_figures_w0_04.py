"""
Gambar untuk slide Minggu 0 — Convolutional Layers.

    pip install numpy scipy matplotlib
    python make_figures_w0_04.py      # output -> images/w0_04_*.png
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from scipy.signal import correlate2d

OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": ["Helvetica Neue", "DejaVu Sans"], "font.size": 12})
PRIMARY, ACCENT, WARN, OK = "#1e3a8a", "#0ea5e9", "#dc2626", "#16a34a"

X = np.array([[1, 2, 0, 1], [0, 1, 3, 1], [2, 1, 0, 2], [1, 0, 1, 3]])
K = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]])


def grid(ax, M, x0, y0, title, hi=None, color=ACCENT, fc="#ffffff"):
    n, m = M.shape
    for i in range(n):
        for j in range(m):
            inside = hi is not None and hi[0] <= i < hi[0] + hi[2] and hi[1] <= j < hi[1] + hi[2]
            ax.add_patch(Rectangle((x0 + j, y0 - i), 1, 1, fc="#e0f2fe" if inside else fc, ec="#475569"))
            ax.text(x0 + j + 0.5, y0 - i + 0.5, f"{M[i, j]:g}", ha="center", va="center", fontsize=13)
    if hi is not None:
        ax.add_patch(Rectangle((x0 + hi[1], y0 - hi[0] - hi[2] + 1), hi[2], hi[2], fc="none", ec=color, lw=3))
    ax.text(x0 + m / 2, y0 + 1.35, title, ha="center", color=PRIMARY, weight="bold")


def sliding():
    Y = correlate2d(X, K, "valid")
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.2))
    for ax, (i, j) in zip(axes, [(0, 0), (1, 1)]):
        grid(ax, X, 0, 3, "Input X (4×4)", hi=(i, j, 3))
        ax.text(4.6, 1.5, "⋆", fontsize=26, ha="center", va="center")
        grid(ax, K, 5.2, 2.5, "Kernel K (3×3)", fc="#fef3c7")
        ax.text(8.8, 1.5, "=", fontsize=24, ha="center", va="center")
        grid(ax, Y, 9.5, 2, "Output Y (2×2)", hi=(i, j, 1), color=WARN)
        win = X[i:i + 3, j:j + 3]
        ax.text(5.8, -1.6, f"Y[{i},{j}] = Σ X[{i}:{i + 3},{j}:{j + 3}] ⊙ K = {(win * K).sum()}", ha="center",
                color=PRIMARY, fontsize=12)
        ax.set_xlim(-0.3, 12)
        ax.set_ylim(-2.2, 5)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(OUT / "w0_04_sliding.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    sliding()
    print("Gambar tersimpan di", OUT)
