"""
Demo Pertemuan 12 — Community Detection dengan NetworkX.

    pip install networkx scikit-learn
    python p12_community_detection_demo.py
"""
import networkx as nx
from networkx.algorithms import community as nxc
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

# 1. Graf contoh slide (hitung manual)
G = nx.Graph([(1, 2), (1, 3), (2, 3), (2, 4), (3, 4), (4, 5), (5, 6), (5, 7), (6, 7), (6, 8), (7, 8)])
P = [{1, 2, 3, 4}, {5, 6, 7, 8}]
print("Modularity partisi {1-4}|{5-8} :", round(nxc.modularity(G, P), 4))
print("Edge betweenness               :", nx.edge_betweenness_centrality(G, normalized=False))
print("Girvan-Newman level 1          :", next(nxc.girvan_newman(G)))
print("Louvain                        :", nxc.louvain_communities(G, seed=42))
print("Clique percolation (k=3)       :", list(nxc.k_clique_communities(G, 3)), "\n")

# 2. Zachary's Karate Club (34 anggota, 78 relasi) — ada ground truth
club = nx.karate_club_graph()
K = nx.Graph()
K.add_nodes_from(club)                         # urutan simpul 0..33
K.add_edges_from(club.edges())                 # abaikan bobot -> graf tak berbobot
truth = [0 if club.nodes[n]["club"] == "Mr. Hi" else 1 for n in K]


def labels(partition):
    lookup = {n: i for i, c in enumerate(partition) for n in c}
    return [lookup[n] for n in K]


hasil = {
    "Girvan-Newman (2)": list(next(nxc.girvan_newman(K))),
    "Greedy modularity": list(nxc.greedy_modularity_communities(K)),
    "Louvain": nxc.louvain_communities(K, seed=42),
    "Label propagation": list(nxc.asyn_lpa_communities(K, seed=42)),
}
print(f"{'Algoritma':<20}{'#kom':>5}{'Q':>8}{'NMI':>8}{'ARI':>8}")
for nama, part in hasil.items():
    print(f"{nama:<20}{len(part):>5}{nxc.modularity(K, part):>8.3f}"
          f"{normalized_mutual_info_score(truth, labels(part)):>8.3f}"
          f"{adjusted_rand_score(truth, labels(part)):>8.3f}")
print(f"{'Ground truth':<20}{2:>5}{nxc.modularity(K, [{n for n in K if truth[n] == c} for c in (0, 1)]):>8.3f}")
