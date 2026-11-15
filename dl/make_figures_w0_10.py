"""
Gambar untuk slide Minggu 0 — Attention Layers.

    python make_figures_w0_10.py      # output -> images/w0_10_*.png
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": ["Helvetica Neue", "DejaVu Sans"], "font.size": 12})
PRIMARY, ACCENT, WARN, OK, MUTED = "#1e3a8a", "#0ea5e9", "#dc2626", "#16a34a", "#94a3b8"


def softmax(S):
    e = np.exp(S - S.max(-1, keepdims=True))
    return e / e.sum(-1, keepdims=True)


X = np.array([[1, 0], [0, 1], [1, 1]], float)
WQ = np.array([[1, 0], [1, 2]], float)
WK = np.array([[1, 1], [0, 1]], float)
WV = np.array([[1, 0], [0, 2]], float)
Q, K, V = X @ WQ, X @ WK, X @ WV


def heat(ax, A, title):
    ax.imshow(A, cmap="Blues", vmin=0, vmax=1)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{A[i, j]:.3f}", ha="center", va="center", color="white" if A[i, j] > 0.55 else "#0f172a")
    ax.set_xticks(range(3), ["k₁", "k₂", "k₃"])
    ax.set_yticks(range(3), ["q₁", "q₂", "q₃"])
    ax.set_title(title, color=PRIMARY, weight="bold")


def main():
    S = Q @ K.T / np.sqrt(2)
    A = softmax(S)
    mask = np.triu(np.ones((3, 3)), 1) * -1e9
    Am = softmax(S + mask)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))
    heat(axes[0], A, "Bobot attention A (tanpa mask)")
    heat(axes[1], Am, "Dengan causal mask")
    d = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
    rng = np.random.default_rng(0)
    var_raw, var_sc = [], []
    for dk in d:
        q = rng.standard_normal((20000, dk))
        k = rng.standard_normal((20000, dk))
        dots = (q * k).sum(1)
        var_raw.append(dots.var())
        var_sc.append((dots / np.sqrt(dk)).var())
    ax = axes[2]
    ax.loglog(d, var_raw, "-o", color=WARN, label="Var(q·k)")
    ax.loglog(d, var_sc, "-o", color=OK, label="Var(q·k / √d_k)")
    ax.set_xlabel("d_k")
    ax.set_title("Mengapa dibagi √d_k", color=PRIMARY, weight="bold")
    ax.legend()
    ax.grid(alpha=.3, which="both")
    fig.tight_layout()
    fig.savefig(OUT / "w0_10_attention.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
    print("Gambar tersimpan di", OUT)
