"""
Demo Pertemuan 12 — Transformer: semua perhitungan manual di slide, dalam NumPy.

    pip install numpy
    python p12_transformer_demo.py
"""
import numpy as np

np.set_printoptions(precision=4, suppress=True)


def softmax(z, axis=-1):
    z = z - z.max(axis=axis, keepdims=True)          # trik numerik: kurangi maksimum
    e = np.exp(z)
    return e / e.sum(axis=axis, keepdims=True)


def attention(Q, K, V, causal=False):
    S = Q @ K.T / np.sqrt(K.shape[1])
    if causal:
        S = S + np.triu(np.full(S.shape, -np.inf), 1)
    A = softmax(S)
    return A, A @ V


print("== 1. Distance & similarity ==")
a, b, c = np.array([1., 2, 2]), np.array([2., 1, 2]), np.array([-1., 0, 1])
for nama, (u, w) in {"a,b": (a, b), "a,c": (a, c), "b,c": (b, c)}.items():
    cos = u @ w / (np.linalg.norm(u) * np.linalg.norm(w))
    print(f"{nama}: dot={u @ w:.0f} euclid={np.linalg.norm(u - w):.3f} "
          f"manhattan={np.abs(u - w).sum():.0f} cosine={cos:.3f}")
print("softmax(9, 8, 1) =", softmax(np.array([9., 8, 1])))

print("\n== 2. Self-attention 'saya suka kopi' ==")
X = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [1, 1, 1, 1]], float)
WQ = np.array([[1, 0], [0, 1], [1, 0], [0, 1]], float)
WK = np.array([[0, 1], [1, 0], [0, 1], [1, 0]], float)
WV = np.array([[1, 0], [0, 1], [0, 0], [1, 1]], float)
Q, K, V = X @ WQ, X @ WK, X @ WV
print("Q =\n", Q, "\nK =\n", K, "\nV =\n", V)
print("QK^T =\n", Q @ K.T)
A, Z = attention(Q, K, V)
print("A =\n", A, "\nZ = AV =\n", Z)
Ac, Zc = attention(Q, K, V, causal=True)
print("A causal =\n", Ac, "\nZ causal =\n", Zc)

# head ke-2 (multi-head)
WQ2 = np.array([[1, 1], [0, 0], [0, 1], [1, 0]], float)
WK2 = np.array([[1, 0], [1, 0], [0, 1], [0, 1]], float)
WV2 = np.array([[0, 1], [1, 0], [1, 0], [0, 1]], float)
_, Z2 = attention(X @ WQ2, X @ WK2, X @ WV2)
print("Z head-2 =\n", Z2, "\nConcat =\n", np.hstack([Z, Z2]))

print("\n== 3. Positional encoding (d_model = 4) ==")
for pos in range(4):
    print(pos, np.array([np.sin(pos), np.cos(pos), np.sin(pos / 100), np.cos(pos / 100)]))

print("\n== 4. LayerNorm & RMSNorm ==")
x = np.array([2., 4, 6, 8])
print("LN  =", (x - x.mean()) / np.sqrt(x.var() + 1e-5))
print("RMS =", x / np.sqrt((x ** 2).mean() + 1e-5))

print("\n== 5. Parameter satu layer encoder (base) ==")
d, f = 512, 2048
mha, ffn, ln = 4 * (d * d + d), (d * f + f) + (f * d + d), 2 * 2 * d
print("MHA", mha, "FFN", ffn, "LN", ln, "total", mha + ffn + ln, "x6", 6 * (mha + ffn + ln))
print("Embedding BERT/GPT-2/Llama3:", 30522 * 768, 50257 * 768, 128256 * 4096)

print("\n== 6. Learning rate Vaswani ==")
for step in (1000, 4000, 16000):
    print(step, 512 ** -0.5 * min(step ** -0.5, step * 4000 ** -1.5))

print("\n== 7. Cross-entropy, temperature, top-p ==")
p = softmax(np.array([2.0, 1.0, 0.1, 0.5]))
print("p =", p, "loss(kopi) =", -np.log(p[2]), "grad =", p - np.array([0, 0, 1, 0]))
for T in (0.5, 1.0, 2.0):
    print("T =", T, softmax(np.array([2.0, 1.0, 0.1]) / T))
probs = np.array([0.5, 0.2, 0.15, 0.1, 0.05])
print("kumulatif:", probs.cumsum(), "top-p 0.8:", probs[:3] / probs[:3].sum(), "top-p 0.9:", probs[:4] / probs[:4].sum())

print("\n== 8. RoPE: skor hanya bergantung jarak relatif ==")


def R(t):
    return np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])


q, k, th = np.array([1., 2]), np.array([3., 1]), 0.5
for m, n in [(2, 5), (3, 6), (10, 13), (5, 2)]:
    print(f"(m={m}, n={n}) ->", round((R(m * th) @ q) @ (R(n * th) @ k), 4))

print("\n== 9. KV cache, MoE, Chinchilla, ViT ==")
print("Llama2-7B KiB/token:", 2 * 32 * 32 * 128 * 2 / 1024, "| Llama3-8B KiB/token:", 2 * 32 * 8 * 128 * 2 / 1024)
print("Matriks skor 8192 token, 32 head, fp16 (GiB):", 32 * 8192 ** 2 * 2 / 2 ** 30)
g = np.array([1.2, 0.3, 2.0, -0.5])
top = np.argsort(-g)[:2]
print("MoE top-2 expert:", top + 1, "bobot:", softmax(g[top]))
N = 7e9
print("Chinchilla D =", 20 * N, "C = 6ND =", 6 * N * 20 * N)
print("ViT-B/16 patch:", (224 // 16) ** 2, "dim patch:", 16 * 16 * 3)

print("\n== 10. Kunci jawaban latihan ==")
u, w = np.array([3., 4]), np.array([4., 3])
print("1:", u @ w, np.linalg.norm(u - w), u @ w / 25)
Q2, K2, V2 = np.eye(2), np.array([[1., 0], [1, 1]]), np.array([[2., 0], [0, 2]])
print("2:", *attention(Q2, K2, V2))
print("3:", *attention(Q2, K2, V2, causal=True))
print("4:", [np.sin(3), np.cos(3), np.sin(.03), np.cos(.03)])
print("5:", 4 * (768 ** 2 + 768))
pp = softmax(np.array([1., 2, 0]))
print("6:", pp, -np.log(pp[1]))
print("7: KiB/token", 2 * 16 * 8 * 64 * 2 / 1024, "MiB total", 2 * 16 * 8 * 64 * 2 * 2048 / 2 ** 20)
