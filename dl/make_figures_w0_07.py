"""
Gambar untuk slide Minggu 0 — Dropout Layers.

    python make_figures_w0_07.py      # output -> images/w0_07_*.png
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": ["Helvetica Neue", "DejaVu Sans"], "font.size": 11})
PRIMARY, ACCENT, WARN, OK, MUTED = "#1e3a8a", "#0ea5e9", "#dc2626", "#16a34a", "#94a3b8"


def network(ax, layers, dropped, title):
    xs = np.arange(len(layers)) * 2.0
    pos = {}
    for li, n in enumerate(layers):
        ys = np.linspace(-(n - 1) / 2, (n - 1) / 2, n)
        for ni, y in enumerate(ys):
            pos[(li, ni)] = (xs[li], y)
    for li in range(len(layers) - 1):
        for a in range(layers[li]):
            for b in range(layers[li + 1]):
                off = (li, a) in dropped or (li + 1, b) in dropped
                ax.plot(*zip(pos[(li, a)], pos[(li + 1, b)]), color="#e2e8f0" if off else "#64748b",
                        lw=0.8 if off else 1.2, zorder=0)
    for key, (x, y) in pos.items():
        off = key in dropped
        ax.scatter(x, y, s=520, c="#f1f5f9" if off else "#dbeafe", edgecolors=MUTED if off else PRIMARY,
                   linewidths=2, zorder=2)
        if off:
            ax.text(x, y, "×", ha="center", va="center", color=WARN, fontsize=18, weight="bold", zorder=3)
    ax.set_title(title, color=PRIMARY, weight="bold")
    ax.axis("off")
    ax.set_xlim(-0.8, xs[-1] + 0.8)
    ax.set_ylim(-3, 3)


def main():
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    layers = [4, 5, 5, 2]
    network(axes[0], layers, set(), "(a) Jaringan penuh (saat inference)")
    network(axes[1], layers, {(1, 1), (1, 3), (2, 0), (2, 2), (2, 4), (0, 2)},
            "(b) Satu 'sub-jaringan' saat training (p = 0,5)")
    fig.tight_layout()
    fig.savefig(OUT / "w0_07_dropout_net.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
    print("Gambar tersimpan di", OUT)
