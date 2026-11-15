"""
Generate gambar untuk slide Pertemuan 12 "Transformer".

    pip install numpy matplotlib
    python make_figures_p12.py      # output -> images/p12_*.png
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": ["Helvetica Neue", "DejaVu Sans"], "font.size": 11})
PRIMARY, ACCENT, WARN, OK, MUTED = "#1e3a8a", "#0ea5e9", "#dc2626", "#16a34a", "#94a3b8"


def softmax(z, axis=-1):
    z = z - z.max(axis=axis, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=axis, keepdims=True)


# Contoh manual di slide
X = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [1, 1, 1, 1]], float)
WQ = np.array([[1, 0], [0, 1], [1, 0], [0, 1]], float)
WK = np.array([[0, 1], [1, 0], [0, 1], [1, 0]], float)
TOK = ["saya", "suka", "kopi"]


def attention_heatmaps():
    S = (X @ WQ) @ (X @ WK).T / np.sqrt(2)
    A = softmax(S)
    mask = np.triu(np.full((3, 3), -np.inf), 1)
    Ac = softmax(S + mask)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    for ax, M, title in [(axes[0], A, "Self-attention (encoder)"), (axes[1], Ac, "Masked / causal (decoder)")]:
        ax.imshow(M, cmap="Blues", vmin=0, vmax=1)
        for i in range(3):
            for j in range(3):
                ax.text(j, i, f"{M[i, j]:.3f}", ha="center", va="center",
                        color="white" if M[i, j] > 0.6 else PRIMARY, fontsize=13, weight="bold")
        ax.set_xticks(range(3), [f"{t}\n(key)" for t in TOK])
        ax.set_yticks(range(3), [f"{t} (query)" for t in TOK])
        ax.set_title(title, color=PRIMARY, weight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "p12_attention_manual.png", dpi=160)
    plt.close(fig)


def positional_encoding():
    n, d = 60, 64
    pos = np.arange(n)[:, None]
    i = np.arange(d // 2)[None, :]
    ang = pos / (10000 ** (2 * i / d))
    pe = np.zeros((n, d))
    pe[:, 0::2], pe[:, 1::2] = np.sin(ang), np.cos(ang)
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.2), gridspec_kw={"width_ratios": [1.4, 1]})
    im = axes[0].imshow(pe, cmap="RdBu", aspect="auto", vmin=-1, vmax=1)
    axes[0].set_xlabel("dimensi i")
    axes[0].set_ylabel("posisi pos")
    axes[0].set_title("Sinusoidal PE (d_model = 64): frekuensi menurun ke kanan", color=PRIMARY, weight="bold")
    fig.colorbar(im, ax=axes[0], fraction=0.03)
    for dim, col in [(0, PRIMARY), (2, ACCENT), (10, OK), (30, WARN)]:
        axes[1].plot(pe[:, dim], color=col, label=f"dimensi {dim}")
    axes[1].set_xlabel("posisi")
    axes[1].set_title("Tiap dimensi = gelombang dengan panjang berbeda", color=PRIMARY, weight="bold")
    axes[1].legend(fontsize=9, loc="lower left")
    axes[1].grid(alpha=.3)
    fig.tight_layout()
    fig.savefig(OUT / "p12_positional_encoding.png", dpi=160)
    plt.close(fig)


def temperature():
    logits = np.array([2.0, 1.0, 0.1])
    labels = ["kopi", "teh", "susu"]
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.4), sharey=True)
    for ax, T, col in zip(axes, [0.5, 1.0, 2.0], [PRIMARY, ACCENT, WARN]):
        p = softmax(logits / T)
        ax.bar(labels, p, color=col)
        for k, v in enumerate(p):
            ax.text(k, v + 0.02, f"{v:.3f}", ha="center")
        ax.set_title(f"T = {T}", color=PRIMARY, weight="bold")
        ax.set_ylim(0, 1)
    axes[0].set_ylabel("peluang")
    fig.suptitle("softmax(z / T) dengan logit z = [2,0; 1,0; 0,1]", color=PRIMARY, weight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "p12_temperature.png", dpi=160)
    plt.close(fig)


def box(ax, x, y, w, h, text, fc, ec=PRIMARY, fs=10, weight="normal"):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=fc, ec=ec, lw=1.5))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, weight=weight, color="#0f172a")


def arrow(ax, x0, y0, x1, y1, col="#475569"):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="->", color=col, lw=1.4))


def architecture():
    fig, ax = plt.subplots(figsize=(11, 7.2))
    W = 2.6
    # Encoder (kiri)
    ex = 2.0
    ax.add_patch(FancyBboxPatch((ex - 1.75, 2.35), 3.5, 3.0, boxstyle="round,pad=0.05", fc="#f8fafc", ec=MUTED, ls="--"))
    ax.text(ex - 1.95, 3.85, "N ×", fontsize=13, weight="bold", color=PRIMARY, ha="right")
    box(ax, ex, 0.4, W, 0.45, "Input embedding", "#e0f2fe")
    box(ax, ex, 1.25, W, 0.45, "+ Positional encoding", "#fef3c7")
    box(ax, ex, 2.8, W, 0.5, "Multi-Head\nSelf-Attention", "#dbeafe", fs=9)
    box(ax, ex, 3.55, W, 0.35, "Add & Norm", "#fde68a")
    box(ax, ex, 4.25, W, 0.45, "Feed-Forward", "#dcfce7")
    box(ax, ex, 4.95, W, 0.35, "Add & Norm", "#fde68a")
    for y0, y1 in [(0.62, 1.02), (1.47, 2.55), (3.05, 3.37), (3.73, 4.02), (4.48, 4.77)]:
        arrow(ax, ex, y0, ex, y1)
    ax.text(ex - 2.3, 2.45, "ENCODER", ha="center", weight="bold", color=PRIMARY)
    # Decoder (kanan)
    dx = 7.0
    ax.add_patch(FancyBboxPatch((dx - 1.75, 2.35), 3.5, 4.0, boxstyle="round,pad=0.05", fc="#f8fafc", ec=MUTED, ls="--"))
    ax.text(dx + 1.95, 4.3, "× N", fontsize=13, weight="bold", color=PRIMARY)
    box(ax, dx, 0.4, W, 0.45, "Output embedding\n(digeser ke kanan)", "#e0f2fe", fs=9)
    box(ax, dx, 1.25, W, 0.45, "+ Positional encoding", "#fef3c7")
    box(ax, dx, 2.8, W, 0.5, "Masked Multi-Head\nSelf-Attention", "#dbeafe", fs=9)
    box(ax, dx, 3.5, W, 0.32, "Add & Norm", "#fde68a")
    box(ax, dx, 4.2, W, 0.5, "Multi-Head\nCross-Attention", "#e9d5ff", fs=9)
    box(ax, dx, 4.9, W, 0.32, "Add & Norm", "#fde68a")
    box(ax, dx, 5.5, W, 0.4, "Feed-Forward", "#dcfce7")
    box(ax, dx, 6.1, W, 0.32, "Add & Norm", "#fde68a")
    for y0, y1 in [(0.62, 1.02), (1.47, 2.55), (3.05, 3.34), (3.66, 3.95), (4.45, 4.74), (5.06, 5.3), (5.7, 5.94)]:
        arrow(ax, dx, y0, dx, y1)
    box(ax, dx, 6.8, W, 0.4, "Linear + Softmax", "#fee2e2")
    arrow(ax, dx, 6.26, dx, 6.6)
    ax.text(dx, 7.25, "peluang token berikutnya", ha="center", color=WARN, fontsize=10)
    ax.text(dx + 2.3, 2.45, "DECODER", ha="center", weight="bold", color=PRIMARY)
    # K, V dari encoder ke cross-attention
    ax.annotate("", xy=(dx - W / 2, 4.2), xytext=(ex + W / 2, 4.95),
                arrowprops=dict(arrowstyle="->", color="#7c3aed", lw=2, connectionstyle="arc3,rad=-0.2"))
    ax.text(4.5, 5.35, "K, V dari encoder", color="#7c3aed", ha="center", fontsize=10, weight="bold")
    ax.set_xlim(-0.6, 9.8)
    ax.set_ylim(-0.3, 7.5)
    ax.axis("off")
    ax.set_title("Transformer encoder–decoder (Vaswani dkk., 2017) — Post-LN", color=PRIMARY, weight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "p12_architecture.png", dpi=160)
    plt.close(fig)


def modern_block():
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.6))
    for ax, title, rows in [
        (axes[0], "Post-LN (Transformer 2017)",
         [("x", "#f1f5f9"), ("Multi-Head Attention", "#dbeafe"), ("Add  (x + ·)", "#fde68a"), ("LayerNorm", "#fde68a"),
          ("FFN: ReLU", "#dcfce7"), ("Add", "#fde68a"), ("LayerNorm", "#fde68a")]),
        (axes[1], "Pre-Norm modern (gaya Llama)",
         [("x", "#f1f5f9"), ("RMSNorm", "#fde68a"), ("Attention: RoPE + GQA", "#dbeafe"), ("Add  (x + ·)", "#fde68a"),
          ("RMSNorm", "#fde68a"), ("FFN: SwiGLU", "#dcfce7"), ("Add", "#fde68a")]),
    ]:
        for k, (t, c) in enumerate(rows):
            y = 6.2 - k * 0.9
            box(ax, 0, y, 3.2, 0.55, t, c, fs=10)
            if k:
                arrow(ax, 0, y + 0.63, 0, y + 0.3)
        ax.set_xlim(-2.2, 2.2)
        ax.set_ylim(0.2, 6.8)
        ax.axis("off")
        ax.set_title(title, color=PRIMARY, weight="bold")
    axes[1].text(1.75, 3.5, "jalur residual\nbersih (identitas)\n→ training stabil", color=OK, fontsize=9, ha="left")
    fig.tight_layout()
    fig.savefig(OUT / "p12_modern_block.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    attention_heatmaps()
    positional_encoding()
    temperature()
    architecture()
    modern_block()
    print("Gambar tersimpan di", OUT)
