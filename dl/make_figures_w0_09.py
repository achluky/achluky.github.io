"""
Gambar untuk slide Minggu 0 — Pooling Layers.

    python make_figures_w0_09.py      # output -> images/w0_09_*.png
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": ["Helvetica Neue", "DejaVu Sans"], "font.size": 12})
PRIMARY, ACCENT, WARN, OK, MUTED = "#1e3a8a", "#0ea5e9", "#dc2626", "#16a34a", "#94a3b8"
BLOCK = ["#dbeafe", "#fef3c7", "#dcfce7", "#fce7f3"]

X = np.array([[1, 3, 2, 1], [4, 6, 5, 0], [3, 1, 1, 2], [0, 2, 7, 4]], float)


def grid(ax, M, title, colors=None, bold=None, fmt="{:g}"):
    n, m = M.shape
    for i in range(n):
        for j in range(m):
            fc = colors[i][j] if colors is not None else "#f8fafc"
            ax.add_patch(plt.Rectangle((j, n - 1 - i), 1, 1, fc=fc, ec="#334155", lw=1.2))
            w = "bold" if bold is not None and bold[i][j] else "normal"
            c = WARN if bold is not None and bold[i][j] else "#0f172a"
            ax.text(j + 0.5, n - 0.5 - i, fmt.format(M[i, j]), ha="center", va="center", fontsize=15, weight=w, color=c)
    ax.set_xlim(-0.1, m + 0.1)
    ax.set_ylim(-0.1, n + 0.1)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, color=PRIMARY, weight="bold", fontsize=12)


def main():
    cols = [[BLOCK[(i // 2) * 2 + j // 2] for j in range(4)] for i in range(4)]
    isMax = np.zeros_like(X, bool)
    for bi in range(2):
        for bj in range(2):
            b = X[2 * bi:2 * bi + 2, 2 * bj:2 * bj + 2]
            a = np.unravel_index(b.argmax(), b.shape)
            isMax[2 * bi + a[0], 2 * bj + a[1]] = True
    mp = np.array([[6, 5], [3, 7]], float)
    ap = np.array([[3.5, 2], [1.5, 3.5]])
    small = [[BLOCK[0], BLOCK[1]], [BLOCK[2], BLOCK[3]]]
    fig, axes = plt.subplots(1, 3, figsize=(12, 4), gridspec_kw={"width_ratios": [2, 1, 1]})
    grid(axes[0], X, "Input X (4×4), blok 2×2 stride 2", cols, isMax)
    grid(axes[1], mp, "Max pooling → 2×2", small)
    grid(axes[2], ap, "Average pooling → 2×2", small)
    fig.tight_layout()
    fig.savefig(OUT / "w0_09_pool_forward.png", dpi=160)
    plt.close(fig)

    dmax = np.array([[0, 0, 0, 0], [0, 1, 2, 0], [3, 0, 0, 0], [0, 0, 4, 0]], float)
    davg = np.kron(np.array([[1, 2], [3, 4]], float), np.ones((2, 2))) / 4
    fig, axes = plt.subplots(1, 3, figsize=(12, 4), gridspec_kw={"width_ratios": [1, 2, 2]})
    grid(axes[0], np.array([[1, 2], [3, 4]], float), "Gradien dari atas G", small)
    grid(axes[1], dmax, "∂L/∂X (max pool): ke posisi argmax", cols, dmax > 0)
    grid(axes[2], davg, "∂L/∂X (avg pool): dibagi rata /4", cols)
    fig.tight_layout()
    fig.savefig(OUT / "w0_09_pool_backward.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
    print("Gambar tersimpan di", OUT)
