"""
Generate gambar ilustrasi untuk slide Pertemuan 11 "Pattern Mining: Itemset Mining".

    python make_figures_p11.py      # output -> images/p11_*.png
"""
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)

plt.rcParams.update({"font.family": ["Helvetica Neue", "DejaVu Sans"], "font.size": 11})

PRIMARY = "#1e3a8a"
ACCENT = "#0ea5e9"
WARN = "#dc2626"
OK = "#16a34a"
MUTED = "#94a3b8"


def box(ax, x, y, text, fc, ec, tc="#0f172a", w=0.9, h=0.42, fs=10, weight="normal"):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=ec, lw=1.6))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=tc, weight=weight)


# ---------------------------------------------------------------------------
# 1. Itemset lattice + prinsip Apriori (anti-monotone pruning)
# ---------------------------------------------------------------------------
def lattice():
    items = "ABCD"
    levels = [[""]] + [["".join(c) for c in combinations(items, k)] for k in range(1, 5)]
    infrequent = "AB"
    pos = {}
    fig, ax = plt.subplots(figsize=(12, 6.2))
    for lvl, nodes in enumerate(levels):
        n = len(nodes)
        for i, node in enumerate(nodes):
            pos[node] = ((i - (n - 1) / 2) * 1.75, -lvl * 1.35)
    for lvl in range(1, len(levels)):
        for node in levels[lvl]:
            for sub in combinations(node, len(node) - 1):
                sub = "".join(sub)
                pruned = infrequent in node or (set(infrequent) <= set(node))
                ax.plot(*zip(pos[sub], pos[node]), color=WARN if pruned and set(infrequent) <= set(sub) or
                        (pruned and sub == infrequent) else "#cbd5e1", lw=1.2, zorder=0)
    for node, (x, y) in pos.items():
        label = "∅" if node == "" else "{" + ",".join(node) + "}"
        if node == infrequent:
            box(ax, x, y, label, "#fee2e2", WARN, WARN, w=1.25, weight="bold")
        elif set(infrequent) <= set(node):
            box(ax, x, y, label, "#f1f5f9", MUTED, MUTED, w=1.25)
            ax.text(x, y - 0.33, "dipangkas", ha="center", fontsize=8, color=WARN, style="italic")
        else:
            box(ax, x, y, label, "#eff6ff", ACCENT, w=1.25)
    ax.text(-6.6, 0.1, "k = 0", color=MUTED)
    for k in range(1, 5):
        ax.text(-6.6, -k * 1.35, f"k = {k}", color=MUTED)
    ax.set_title("Jika {A,B} tidak frequent → semua superset-nya pasti tidak frequent (tidak perlu dihitung)",
                 color=PRIMARY, fontsize=13, weight="bold")
    ax.set_xlim(-6.9, 5.9)
    ax.set_ylim(-5.9, 0.6)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(OUT / "p11_lattice_pruning.png", dpi=160)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 2. FP-tree contoh Han et al. (min_sup = 2)
# ---------------------------------------------------------------------------
def fptree():
    # node: (label, x, y)
    nodes = {
        "root": ("null", 5.0, 6.0),
        "I2": ("I2:7", 3.0, 4.8),
        "I1b": ("I1:2", 8.0, 4.8),
        "I2-I1": ("I1:4", 1.6, 3.6),
        "I2-I3": ("I3:2", 3.6, 3.6),
        "I2-I4": ("I4:1", 5.4, 3.0),
        "I1b-I3": ("I3:2", 8.0, 3.6),
        "I2-I1-I5": ("I5:1", 0.0, 2.4),
        "I2-I1-I4": ("I4:1", 1.4, 1.2),
        "I2-I1-I3": ("I3:2", 2.8, 2.4),
        "I2-I1-I3-I5": ("I5:1", 2.8, 1.2),
    }
    edges = [("root", "I2"), ("root", "I1b"), ("I2", "I2-I1"), ("I2", "I2-I3"), ("I2", "I2-I4"),
             ("I1b", "I1b-I3"), ("I2-I1", "I2-I1-I5"), ("I2-I1", "I2-I1-I4"), ("I2-I1", "I2-I1-I3"),
             ("I2-I1-I3", "I2-I1-I3-I5")]
    colors = {"I1": "#dbeafe", "I2": "#fef3c7", "I3": "#dcfce7", "I4": "#fce7f3", "I5": "#ede9fe"}
    fig, ax = plt.subplots(figsize=(12, 6))
    for a, b in edges:
        ax.plot([nodes[a][1], nodes[b][1]], [nodes[a][2], nodes[b][2]], color="#475569", lw=1.5, zorder=0)
    # node-link (garis putus-putus antar node dengan item sama)
    links = {"I2": ["I2"], "I1": ["I2-I1", "I1b"], "I3": ["I2-I3", "I2-I1-I3", "I1b-I3"], "I4": ["I2-I4", "I2-I1-I4"],
             "I5": ["I2-I1-I5", "I2-I1-I3-I5"]}
    header_y = {"I2": 5.4, "I1": 4.5, "I3": 3.6, "I4": 2.7, "I5": 1.8}
    for item, chain in links.items():
        pts = [(nodes[c][1], nodes[c][2]) for c in chain]
        pts = sorted(pts, key=lambda p: -p[0])
        hx, hy = 11.2, header_y[item]
        seq = [(hx - 0.55, hy)] + pts
        for p, q in zip(seq, seq[1:]):
            ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="->", color=ACCENT, ls="--", lw=1.0,
                                                            shrinkA=14, shrinkB=14, alpha=.7))
    for key, (label, x, y) in nodes.items():
        item = label.split(":")[0]
        box(ax, x, y, label, colors.get(item, "#f1f5f9"), PRIMARY, w=0.95, weight="bold")
    # header table
    ax.text(11.6, 6.1, "Header table", ha="center", weight="bold", color=PRIMARY)
    ax.text(11.35, 5.85, "item  sup", ha="center", fontsize=9, color=MUTED)
    for item, cnt in [("I2", 7), ("I1", 6), ("I3", 6), ("I4", 2), ("I5", 2)]:
        box(ax, 11.5, header_y[item], f"{item}    {cnt}", colors[item], PRIMARY, w=1.1)
    ax.text(5, 0.35, "garis putus-putus biru = node-link (menghubungkan node dengan item yang sama)",
            ha="center", color=ACCENT, fontsize=10, style="italic")
    ax.set_xlim(-0.8, 12.4)
    ax.set_ylim(0.0, 6.5)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(OUT / "p11_fptree.png", dpi=160)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 3. Frequent ⊇ Closed ⊇ Maximal
# ---------------------------------------------------------------------------
def closed_maximal():
    fig, ax = plt.subplots(figsize=(8, 4.6))
    from matplotlib.patches import Ellipse
    ax.add_patch(Ellipse((0, 0), 9.6, 5.4, fc="#eff6ff", ec=ACCENT, lw=2))
    ax.add_patch(Ellipse((0.8, -0.3), 6.2, 3.7, fc="#dcfce7", ec=OK, lw=2))
    ax.add_patch(Ellipse((1.6, -0.6), 3.2, 2.0, fc="#fef3c7", ec="#d97706", lw=2))
    ax.text(-3.4, 1.6, "Frequent\n(13 itemset)", color=PRIMARY, weight="bold", ha="center")
    ax.text(-1.3, 0.6, "Closed\n(9)", color=OK, weight="bold", ha="center")
    ax.text(1.6, -0.25, "Maximal (3)", color="#b45309", weight="bold", ha="center")
    ax.text(1.6, -0.85, "{I2,I4} {I1,I2,I3}\n{I1,I2,I5}", ha="center", fontsize=9)
    ax.text(-3.4, -1.0, "{I4} {I5}\n{I1,I5} {I2,I5}", ha="center", fontsize=9, color=MUTED)
    ax.text(-0.9, -0.9, "{I1} {I2} {I3}\n{I1,I2} {I1,I3}\n{I2,I3}", ha="center", fontsize=9)
    ax.set_xlim(-5, 5)
    ax.set_ylim(-2.9, 2.9)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(OUT / "p11_closed_maximal.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    lattice()
    fptree()
    closed_maximal()
    print("Gambar tersimpan di", OUT)
