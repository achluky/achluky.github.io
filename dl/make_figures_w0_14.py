"""
Gambar untuk slide Minggu 0 — Gradient Descent (w0_14_gradient_descent.md).

    pip install numpy matplotlib
    python make_figures_w0_14.py      # output -> images/w0_14_*.png
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": ["Helvetica Neue", "DejaVu Sans"], "font.size": 11})
PRIMARY, ACCENT, WARN, OK = "#1e3a8a", "#0ea5e9", "#dc2626", "#16a34a"

# Data regresi contoh di slide: y_hat = w * x
X = np.array([1.0, 2.0, 3.0])
Y = np.array([2.0, 3.0, 7.0])


def loss(w):
    return np.mean((w * X - Y) ** 2)


def grad(w, idx):
    idx = np.array(idx)
    return np.mean(2 * (w * X[idx] - Y[idx]) * X[idx])


def batch_vs_sgd():
    eta = 0.05
    ws = np.linspace(-0.2, 3.2, 300)
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.3))
    ax = axes[0]
    ax.plot(ws, [loss(w) for w in ws], color="#475569", lw=2)
    for label, color, steps in [("Batch GD (3 iterasi)", PRIMARY, [[0, 1, 2]] * 3),
                                ("SGD (1 epoch = 3 iterasi)", WARN, [[0], [1], [2]]),
                                ("Mini-batch {1,2},{3}", OK, [[0, 1], [2]])]:
        w, path = 0.0, [0.0]
        for b in steps:
            w = w - eta * grad(w, b)
            path.append(w)
        ax.plot(path, [loss(p) for p in path], "-o", color=color, label=label, ms=6)
    ax.axvline(29 / 14, color=ACCENT, ls="--", lw=1)
    ax.text(29 / 14 + 0.05, 25, "w* = 29/14 ≈ 2,071", color=ACCENT)
    ax.set_xlabel("w")
    ax.set_ylabel("L(w) = MSE")
    ax.set_title("Lintasan pada kurva loss (η = 0,05, w₀ = 0)", color=PRIMARY, weight="bold")
    ax.legend(fontsize=9)
    ax.grid(alpha=.3)
    ax = axes[1]
    for eta, color in [(0.1, OK), (0.9, ACCENT), (1.1, WARN)]:
        w, path = 1.0, [1.0]
        for _ in range(6):
            w = w - eta * 2 * w
            path.append(w)
        ax.plot(range(7), path, "-o", color=color, label=f"η = {str(eta).replace('.', ',')}")
    ax.axhline(0, color="#475569", lw=1)
    ax.set_xlabel("iterasi t")
    ax.set_ylabel("w_t")
    ax.set_title("f(w) = w²: η terlalu besar → divergen", color=PRIMARY, weight="bold")
    ax.legend()
    ax.grid(alpha=.3)
    fig.tight_layout()
    fig.savefig(OUT / "w0_14_batch_vs_sgd.png", dpi=160)
    plt.close(fig)


def optimizers_2d():
    """Lintasan optimizer pada f(w1, w2) = 0.5 * (w1^2 + 10 w2^2) dari (-4, 2)."""
    A = np.array([1.0, 10.0])

    def g(w):
        return A * w

    def run(update, steps=40):
        w = np.array([-4.0, 2.0])
        state = {}
        path = [w.copy()]
        for t in range(1, steps + 1):
            w = update(w, g(w), state, t)
            path.append(w.copy())
        return np.array(path)

    def gd(w, gr, s, t, lr=0.15):
        return w - lr * gr

    def momentum(w, gr, s, t, lr=0.03, beta=0.8):
        s["v"] = beta * s.get("v", 0) + gr
        return w - lr * s["v"]

    def adam(w, gr, s, t, lr=0.3, b1=0.9, b2=0.999, eps=1e-8):
        s["m"] = b1 * s.get("m", 0) + (1 - b1) * gr
        s["v"] = b2 * s.get("v", 0) + (1 - b2) * gr ** 2
        mh, vh = s["m"] / (1 - b1 ** t), s["v"] / (1 - b2 ** t)
        return w - lr * mh / (np.sqrt(vh) + eps)

    w1, w2 = np.meshgrid(np.linspace(-4.5, 1.5, 200), np.linspace(-2.5, 2.5, 200))
    Z = 0.5 * (w1 ** 2 + 10 * w2 ** 2)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.contour(w1, w2, Z, levels=20, colors="#cbd5e1", linewidths=1)
    for name, fn, color in [("GD (η=0,15)", gd, PRIMARY), ("Momentum (η=0,03; β=0,8)", momentum, OK),
                            ("Adam (η=0,3)", adam, WARN)]:
        p = run(fn)
        ax.plot(p[:, 0], p[:, 1], "-o", ms=3, color=color, label=name, lw=1.5)
    ax.plot(0, 0, "*", ms=16, color="#f59e0b")
    ax.set_title("f(w₁,w₂) = ½(w₁² + 10 w₂²): lembah sempit — 40 iterasi dari (−4, 2)", color=PRIMARY, weight="bold")
    ax.set_xlabel("w₁")
    ax.set_ylabel("w₂")
    ax.legend(loc="upper right")
    ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(OUT / "w0_14_optimizers_2d.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    batch_vs_sgd()
    optimizers_2d()
    print("Gambar tersimpan di", OUT)
