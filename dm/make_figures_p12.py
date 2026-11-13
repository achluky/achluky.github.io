"""
Generate gambar ilustrasi untuk slide Pertemuan 12 "Graph Mining: Community Detection".

    pip install networkx matplotlib numpy
    python make_figures_p12.py      # output -> images/p12_*.png
"""
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from networkx.algorithms import community as nxc

OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": ["Helvetica Neue", "DejaVu Sans"], "font.size": 11})

PRIMARY, ACCENT, WARN, OK, MUTED = "#1e3a8a", "#0ea5e9", "#dc2626", "#16a34a", "#94a3b8"
C1, C2, C3, C4 = "#93c5fd", "#fcd34d", "#86efac", "#f9a8d4"

# Graf contoh untuk hitung manual (8 simpul, 11 sisi)
EDGES = [(1, 2), (1, 3), (2, 3), (2, 4), (3, 4), (4, 5), (5, 6), (5, 7), (6, 7), (6, 8), (7, 8)]
G = nx.Graph(EDGES)
POS = {1: (0, 0), 2: (1, 0.8), 3: (1, -0.8), 4: (2, 0), 5: (3.2, 0), 6: (4.2, 0.8), 7: (4.2, -0.8), 8: (5.2, 0)}


def toy_graph():
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
    # kiri: graf + derajat
    ax = axes[0]
    nx.draw_networkx_edges(G, POS, ax=ax, width=2, edge_color="#475569")
    nx.draw_networkx_nodes(G, POS, ax=ax, node_color="#e0f2fe", edgecolors=PRIMARY, node_size=900, linewidths=2)
    nx.draw_networkx_labels(G, POS, ax=ax, font_weight="bold", font_color=PRIMARY)
    for n, (x, y) in POS.items():
        ax.text(x, y - 0.33 if y <= 0 else y + 0.28, f"k={G.degree(n)}", ha="center", fontsize=9, color=MUTED)
    ax.set_title("Graf contoh G: |V| = 8, |E| = m = 11", color=PRIMARY, weight="bold")
    ax.axis("off")
    ax.set_ylim(-1.3, 1.3)
    # kanan: edge betweenness + komunitas
    ax = axes[1]
    eb = nx.edge_betweenness_centrality(G, normalized=False)
    widths = [1 + eb[e] / 3 if e in eb else 1 + eb[(e[1], e[0])] / 3 for e in G.edges()]
    colors = [WARN if set(e) == {4, 5} else "#475569" for e in G.edges()]
    nx.draw_networkx_edges(G, POS, ax=ax, width=widths, edge_color=colors)
    nx.draw_networkx_nodes(G, POS, ax=ax, nodelist=[1, 2, 3, 4], node_color=C1, edgecolors=PRIMARY, node_size=900, linewidths=2)
    nx.draw_networkx_nodes(G, POS, ax=ax, nodelist=[5, 6, 7, 8], node_color=C2, edgecolors="#b45309", node_size=900, linewidths=2)
    nx.draw_networkx_labels(G, POS, ax=ax, font_weight="bold")
    lbl = {e: f"{v:g}" for e, v in eb.items()}
    nx.draw_networkx_edge_labels(G, POS, edge_labels=lbl, ax=ax, font_size=9, font_color=PRIMARY,
                                 bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
    ax.set_title("Edge betweenness: sisi jembatan (4,5) = 16 → komunitas {1,2,3,4} | {5,6,7,8}",
                 color=PRIMARY, weight="bold", fontsize=11)
    ax.axis("off")
    ax.set_ylim(-1.3, 1.3)
    fig.tight_layout()
    fig.savefig(OUT / "p12_toy_graph.png", dpi=160)
    plt.close(fig)


def girvan_newman_steps():
    fig, axes = plt.subplots(1, 4, figsize=(15, 3.6), gridspec_kw={"width_ratios": [1, 1, 1, 1.1]})
    H = G.copy()
    titles = ["Awal: Q = 0", "Hapus (4,5) → Q = 0,409", "Hapus (1,2),(1,3) → Q = 0,302"]
    removals = [[], [(4, 5)], [(1, 2), (1, 3)]]
    palette = [C1, C2, C3, C4]
    for ax, title, rem in zip(axes[:3], titles, removals):
        H.remove_edges_from(rem)
        comps = list(nx.connected_components(H))
        cmap = {n: palette[i % 4] for i, c in enumerate(sorted(comps, key=min)) for n in c}
        nx.draw_networkx_edges(H, POS, ax=ax, width=2, edge_color="#475569")
        nx.draw_networkx_nodes(H, POS, ax=ax, node_color=[cmap[n] for n in H], edgecolors=PRIMARY, node_size=480)
        nx.draw_networkx_labels(H, POS, ax=ax, font_size=10, font_weight="bold")
        ax.set_title(title, color=PRIMARY, fontsize=11, weight="bold")
        ax.axis("off")
        ax.set_ylim(-1.2, 1.2)
    ax = axes[3]
    qs = [0.0]
    for comm in nxc.girvan_newman(G):
        qs.append(nxc.modularity(G, comm))
    ks = list(range(1, len(qs) + 1))
    ax.plot(ks, qs, "-o", color=PRIMARY)
    best = int(np.argmax(qs))
    ax.plot(ks[best], qs[best], "o", ms=13, mfc="none", mec=WARN, mew=2)
    ax.annotate(f"maks Q = {qs[best]:.3f}\n(2 komunitas)", (ks[best], qs[best]), (ks[best] + 1.4, qs[best] - 0.05),
                color=WARN, fontsize=10, arrowprops=dict(arrowstyle="->", color=WARN))
    ax.set_xlabel("jumlah komunitas")
    ax.set_ylabel("modularity Q")
    ax.set_title("Pilih potongan dendrogram dengan Q maksimum", color=PRIMARY, fontsize=11, weight="bold")
    ax.grid(alpha=.3)
    fig.tight_layout()
    fig.savefig(OUT / "p12_girvan_newman.png", dpi=160)
    plt.close(fig)


def louvain_phases():
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2), gridspec_kw={"width_ratios": [1.2, 1.2, 0.8]})
    ax = axes[0]
    nx.draw_networkx_edges(G, POS, ax=ax, width=2, edge_color="#cbd5e1")
    nx.draw_networkx_nodes(G, POS, ax=ax, node_color=[C1, C3, C4, "#e2e8f0", "#fde68a", "#fbcfe8", "#bae6fd", "#ddd6fe"],
                           edgecolors=PRIMARY, node_size=650)
    nx.draw_networkx_labels(G, POS, ax=ax, font_weight="bold")
    ax.set_title("Awal: tiap simpul = 1 komunitas", color=PRIMARY, weight="bold")
    ax.axis("off")
    ax.set_ylim(-1.2, 1.2)
    ax = axes[1]
    nx.draw_networkx_edges(G, POS, ax=ax, width=2, edge_color="#475569")
    nx.draw_networkx_nodes(G, POS, ax=ax, nodelist=[1, 2, 3, 4], node_color=C1, edgecolors=PRIMARY, node_size=650)
    nx.draw_networkx_nodes(G, POS, ax=ax, nodelist=[5, 6, 7, 8], node_color=C2, edgecolors="#b45309", node_size=650)
    nx.draw_networkx_labels(G, POS, ax=ax, font_weight="bold")
    ax.set_title("Fase 1: pindahkan simpul selama ΔQ > 0", color=PRIMARY, weight="bold")
    ax.axis("off")
    ax.set_ylim(-1.2, 1.2)
    ax = axes[2]
    ax.add_patch(plt.Circle((0, 0), 0.42, fc=C1, ec=PRIMARY, lw=2))
    ax.add_patch(plt.Circle((2, 0), 0.42, fc=C2, ec="#b45309", lw=2))
    ax.plot([0.42, 1.58], [0, 0], color="#475569", lw=2)
    ax.text(1, 0.12, "w = 1", ha="center", color=PRIMARY)
    ax.text(0, 0, "A", ha="center", va="center", weight="bold", fontsize=14)
    ax.text(2, 0, "B", ha="center", va="center", weight="bold", fontsize=14)
    for x in (0, 2):
        ax.add_patch(plt.Circle((x, 0.62), 0.2, fc="none", ec="#475569", lw=1.5))
        ax.text(x, 0.95, "self-loop w = 5", ha="center", fontsize=9, color=PRIMARY)
    ax.set_xlim(-0.7, 2.7)
    ax.set_ylim(-0.8, 1.2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Fase 2: agregasi → super-node", color=PRIMARY, weight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "p12_louvain_phases.png", dpi=160)
    plt.close(fig)


def spectral():
    nodes = list(range(1, 9))
    L = nx.laplacian_matrix(G, nodelist=nodes).toarray().astype(float)
    w, v = np.linalg.eigh(L)
    f = v[:, 1]
    if f[0] > 0:
        f = -f
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.8))
    ax = axes[0]
    ax.bar([str(n) for n in nodes], f, color=[C1 if x < 0 else C2 for x in f], edgecolor=PRIMARY)
    ax.axhline(0, color="#475569")
    for i, x in enumerate(f):
        ax.text(i, x + (0.03 if x >= 0 else -0.06), f"{x:+.3f}", ha="center", fontsize=9)
    ax.set_title(f"Fiedler vector (λ₂ = {w[1]:.3f}): tanda → partisi", color=PRIMARY, weight="bold")
    ax.set_xlabel("simpul")
    ax.set_ylim(-0.55, 0.55)
    ax = axes[1]
    ax.plot(range(1, 9), w, "-o", color=PRIMARY)
    ax.plot(2, w[1], "o", ms=13, mfc="none", mec=WARN, mew=2)
    ax.set_title("Spektrum Laplacian L = D − A", color=PRIMARY, weight="bold")
    ax.set_xlabel("indeks eigenvalue")
    ax.grid(alpha=.3)
    fig.tight_layout()
    fig.savefig(OUT / "p12_spectral.png", dpi=160)
    plt.close(fig)


def karate():
    K = nx.Graph()
    K.add_nodes_from(range(34))
    K.add_edges_from(nx.karate_club_graph().edges())   # tanpa bobot
    pos = nx.spring_layout(K, seed=7)
    club = nx.karate_club_graph()
    gt = {n: (C1 if club.nodes[n]["club"] == "Mr. Hi" else C2) for n in K}
    lv = nxc.louvain_communities(K, seed=42)
    pal = [C1, C2, C3, C4, "#c4b5fd"]
    lvc = {n: pal[i] for i, c in enumerate(sorted(lv, key=min)) for n in c}
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, cmap, title in [(axes[0], gt, "Ground truth: klub pecah menjadi 2 (Zachary, 1977)"),
                            (axes[1], lvc, f"Louvain: {len(lv)} komunitas, Q = {nxc.modularity(K, lv):.3f}")]:
        nx.draw_networkx_edges(K, pos, ax=ax, edge_color="#cbd5e1")
        nx.draw_networkx_nodes(K, pos, ax=ax, node_color=[cmap[n] for n in K], edgecolors="#334155", node_size=300)
        nx.draw_networkx_labels(K, pos, ax=ax, font_size=8)
        ax.set_title(title, color=PRIMARY, weight="bold")
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(OUT / "p12_karate.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    toy_graph()
    girvan_newman_steps()
    louvain_phases()
    spectral()
    karate()
    print("Gambar tersimpan di", OUT)
