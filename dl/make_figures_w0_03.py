"""
Gambar untuk slide Minggu 0 — Nonlinearitas (fungsi aktivasi).

    pip install numpy scipy matplotlib
    python make_figures_w0_03.py      # output -> images/w0_03_*.png
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.special import erf

OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": ["Helvetica Neue", "DejaVu Sans"], "font.size": 11})
PRIMARY, ACCENT, WARN, OK = "#1e3a8a", "#0ea5e9", "#dc2626", "#16a34a"

z = np.linspace(-4, 4, 801)
sig = 1 / (1 + np.exp(-z))
Phi = 0.5 * (1 + erf(z / np.sqrt(2)))
phi = np.exp(-z ** 2 / 2) / np.sqrt(2 * np.pi)
ACT = {
    "Sigmoid": (sig, sig * (1 - sig)),
    "Tanh": (np.tanh(z), 1 - np.tanh(z) ** 2),
    "ReLU": (np.maximum(0, z), (z > 0).astype(float)),
    "Leaky ReLU (0,1)": (np.where(z > 0, z, 0.1 * z), np.where(z > 0, 1, 0.1)),
    "ELU (α=1)": (np.where(z > 0, z, np.exp(z) - 1), np.where(z > 0, 1, np.exp(z))),
    "GELU": (z * Phi, Phi + z * phi),
    "SiLU / Swish": (z * sig, sig + z * sig * (1 - sig)),
}


def activations():
    fig, axes = plt.subplots(2, 4, figsize=(15, 6.4))
    for ax, (name, (f, df)) in zip(axes.flat, ACT.items()):
        ax.axhline(0, color="#cbd5e1", lw=1)
        ax.axvline(0, color="#cbd5e1", lw=1)
        ax.plot(z, f, color=PRIMARY, lw=2.4, label="f(z)")
        ax.plot(z, df, color=WARN, lw=1.8, ls="--", label="f'(z)")
        ax.set_title(name, color=PRIMARY, weight="bold")
        ax.set_ylim(-1.5, 3)
        ax.grid(alpha=.25)
    axes.flat[0].legend(loc="upper left", fontsize=9)
    ax = axes.flat[-1]
    ax.axis("off")
    ax.text(0.02, 0.6, "Garis biru  : f(z)\nGaris merah : turunan f'(z)\n\n"
            "Sigmoid/tanh: turunan → 0\nsaat |z| besar (saturasi)", fontsize=11, color=PRIMARY, va="center")
    fig.tight_layout()
    fig.savefig(OUT / "w0_03_activations.png", dpi=160)
    plt.close(fig)


def xor():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    pts = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    lab = np.array([0, 1, 1, 0])
    ax = axes[0]
    for p, l in zip(pts, lab):
        ax.scatter(*p, s=260, c=OK if l else WARN, edgecolors="k", zorder=3)
        ax.annotate(f"y={l}", p, (p[0] + 0.07, p[1] + 0.07))
    ax.set_title("Ruang input x: tidak terpisah linear", color=PRIMARY, weight="bold")
    ax.set_xlim(-0.4, 1.5)
    ax.set_ylim(-0.4, 1.5)
    ax.set_xlabel("x₁")
    ax.set_ylabel("x₂")
    ax.grid(alpha=.3)
    ax = axes[1]
    H = np.maximum(0, pts @ np.array([[1, 1], [1, 1]]).T + np.array([0, -1]))
    for p, h, l in zip(pts, H, lab):
        ax.scatter(*h, s=260, c=OK if l else WARN, edgecolors="k", zorder=3)
    ax.annotate("(0,1),(1,0) → h=(1,0)", (1, 0), (1.05, -0.35))
    ax.annotate("(0,0) → h=(0,0)", (0, 0), (-0.3, 0.2))
    ax.annotate("(1,1) → h=(2,1)", (2, 1), (1.3, 1.25))
    xs = np.linspace(-0.3, 2.4, 10)
    ax.plot(xs, (xs - 0.5) / 2, color=ACCENT, lw=2, ls="--")
    ax.text(2.0, 0.45, "h₁ − 2h₂ = 0,5", color=ACCENT)
    ax.set_title("Ruang tersembunyi h = ReLU(Wx + c): terpisah linear", color=PRIMARY, weight="bold")
    ax.set_xlim(-0.4, 2.6)
    ax.set_ylim(-0.5, 1.6)
    ax.set_xlabel("h₁")
    ax.set_ylabel("h₂")
    ax.grid(alpha=.3)
    fig.tight_layout()
    fig.savefig(OUT / "w0_03_xor.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    activations()
    xor()
    print("Gambar tersimpan di", OUT)
