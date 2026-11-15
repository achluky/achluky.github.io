"""
Gambar untuk slide Minggu 0 — Normalization Layers.
Diagram sumbu normalisasi (terinspirasi Gambar 2 pada Wu & He, 2018).

    pip install matplotlib
    python make_figures_w0_06.py      # output -> images/w0_06_*.png
"""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": ["Helvetica Neue", "DejaVu Sans"], "font.size": 12})
PRIMARY, ACCENT = "#1e3a8a", "#0ea5e9"
N, C = 4, 6


def axes_diagram():
    fig, axes = plt.subplots(1, 4, figsize=(15, 4.4))
    specs = {
        "Batch Norm": lambda n, c: c == 1,
        "Layer Norm": lambda n, c: n == 1,
        "Instance Norm": lambda n, c: n == 1 and c == 1,
        "Group Norm (G = 2)": lambda n, c: n == 1 and c < 3,
    }
    for ax, (title, sel) in zip(axes, specs.items()):
        for n in range(N):
            for c in range(C):
                ax.add_patch(Rectangle((c, N - 1 - n), 1, 1, fc=ACCENT if sel(n, c) else "#f1f5f9",
                                       ec="#475569", lw=1))
        ax.set_xlim(-0.6, C + 0.2)
        ax.set_ylim(-0.9, N + 0.6)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(title, color=PRIMARY, weight="bold")
        ax.text(C / 2, -0.6, "C (kanal / fitur) →", ha="center", fontsize=10)
        ax.text(-0.35, N / 2, "N (sampel) →", rotation=90, va="center", fontsize=10)
    fig.suptitle("Setiap sel = satu peta fitur H×W. Sel biru = himpunan nilai yang berbagi satu μ dan σ²",
                 color=PRIMARY, fontsize=12, y=0.04)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(OUT / "w0_06_axes.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    axes_diagram()
    print("Gambar tersimpan di", OUT)
