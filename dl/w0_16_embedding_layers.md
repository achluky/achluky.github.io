---
marp: true
theme: default
paginate: true
size: 16:9
math: mathjax
header: 'Building Blocks of Deep Learning · Number Representation (Embedding Layers)'
footer: 'Deep Learning · Sains Data ITERA · Ahmad Luky Ramdani'
style: |
  :root { --primary: #1e3a8a; --accent: #0ea5e9; --warn: #dc2626; --ok: #16a34a; --muted: #64748b; }
  section { font-family: 'Inter', 'Segoe UI', 'Helvetica Neue', sans-serif; font-size: 24px; padding: 56px 66px; color: #0f172a; background: #fff; }
  h1 { color: var(--primary); font-size: 1.45em; border-bottom: 3px solid var(--accent); padding-bottom: 6px; }
  h2 { color: var(--primary); font-size: 1.15em; }
  h3 { color: var(--accent); font-size: 1.0em; margin-bottom: 4px; }
  strong { color: var(--primary); }
  table { font-size: 0.72em; margin: 0 auto; }
  th { background: var(--primary); color: #fff; }
  pre { font-size: 0.62em; line-height: 1.35; border-radius: 8px; }
  blockquote { border-left: 5px solid var(--accent); background: #f0f9ff; padding: 8px 18px; font-style: normal; color: #0f172a; }
  header, footer { color: var(--muted); font-size: 0.55em; }
  img { display: block; margin: 0 auto; }
  section.two { display: block; column-count: 2; column-gap: 34px; }
  section.two h1, section.two blockquote.full { column-span: all; }
  section.two pre, section.two table, section.two ul, section.two ol, section.two p, section.two blockquote { break-inside: avoid; }
  section.two h3 { break-after: avoid; }
  section.two h3 ~ h3 { break-before: column; }
  section.small { font-size: 20px; }
  section.small pre { font-size: 0.7em; }
  section.tiny { font-size: 17px; }
  section.lead { background: linear-gradient(135deg, #1e3a8a 0%, #0ea5e9 100%); color: #fff; justify-content: center; }
  section.lead h1 { color: #fff; border: none; font-size: 2.0em; }
  section.lead h2, section.lead h3, section.lead p, section.lead strong { color: #e0f2fe; }
  section.divider { background: #0f172a; color: #fff; justify-content: center; }
  section.divider h1 { color: #fff; border-color: var(--accent); }
  section.divider p { color: #cbd5e1; }
---

<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _header: '' -->

# Number Representation
## Embedding Layers: dari Simbol ke Vektor

### Minggu 0 — Deep Learning
**Sains Data ITERA · Ganjil 2026/2025**

---

# Capaian Pembelajaran & Agenda

> Mahasiswa mampu menjelaskan bagaimana data diskret (kata, token, kategori) dan bilangan direpresentasikan di dalam jaringan saraf, serta menghitung secara manual *lookup*, gradien, dan kemiripan pada **embedding layer**.

1. Masalah: neural network hanya memproses **bilangan**
2. **One-hot** vs **dense embedding**
3. Embedding = *lookup table* = one-hot × matriks — hitung manual
4. Gradien embedding: hanya baris yang dipakai yang diperbarui
5. Kemiripan vektor: dot product & cosine — hitung manual
6. Tokenisasi, word2vec, GloVe, **positional encoding**
7. Entity embedding untuk data tabular kategorikal
8. Representasi bilangan di komputer: **float32, float16, bfloat16**
9. PyTorch `nn.Embedding` · jebakan · latihan

---

# Masalah: Jaringan Saraf Hanya Memproses Bilangan

| Jenis data | Contoh | Representasi numerik |
|---|---|---|
| Kontinu | Suhu, harga, piksel | Sudah bilangan → cukup **dinormalisasi** |
| Kategorikal | Provinsi, jenis produk | ? |
| Teks | "saya suka kopi" | ? |
| ID entitas | ID pengguna, ID film | ? |

**Pendekatan naif — label encoding** (kopi = 2, teh = 4, mobil = 3):
- Membuat urutan & jarak palsu: "mobil (3) lebih dekat ke kopi (2) daripada teh (4)"
- Operasi linear $w \cdot 3$ tidak bermakna untuk kategori

> Kita butuh representasi yang **tidak memaksakan urutan** dan idealnya **menangkap kemiripan makna**.

---

# One-Hot Encoding

Kosakata $V$ berukuran $\lvert V \rvert$; token ke-$i$ → vektor $e_i \in \{0,1\}^{\lvert V \rvert}$ dengan satu angka 1.

Kosakata contoh (5 token): **0 = susu, 1 = motor, 2 = kopi, 3 = mobil, 4 = teh**

| Token | One-hot |
|---|---|
| kopi | $[0, 0, 1, 0, 0]$ |
| teh | $[0, 0, 0, 0, 1]$ |
| mobil | $[0, 0, 0, 1, 0]$ |

**Kelemahan**:
- Dimensi = ukuran kosakata (puluhan ribu) dan sangat *sparse*
- Semua pasangan **ortogonal**: $e_\text{kopi} \cdot e_\text{teh} = e_\text{kopi} \cdot e_\text{mobil} = 0$ → tidak ada informasi kemiripan
- Tidak ada parameter yang dipelajari

---

# Dense Embedding

Setiap token dipetakan ke vektor **padat berdimensi kecil** $d \ll \lvert V \rvert$ yang **dipelajari** saat training:

$$E \in \mathbb{R}^{\lvert V \rvert \times d}, \qquad \text{embed}(i) = E_{i,:} \in \mathbb{R}^d$$

| | One-hot | Dense embedding |
|---|---|---|
| Dimensi | $\lvert V \rvert$ (mis. 30.000) | $d$ (mis. 64–1024) |
| Nilai | 0/1, *sparse* | Real, padat |
| Kemiripan | Selalu 0 | Token serupa → vektor berdekatan |
| Parameter | 0 | $\lvert V \rvert \times d$ |

Gagasan ini diperkenalkan dalam *neural language model* oleh Bengio dkk. (2003): kata dipetakan ke "distributed feature vector" yang dipelajari bersama model.

---

<!-- _class: small -->

# Hitung Manual: Embedding = One-Hot × Matriks

Matriks embedding contoh ($\lvert V \rvert = 5$, $d = 3$; nilai ilustrasi, bukan hasil training):

$$E = \begin{bmatrix} 0{,}1 & 0{,}3 & -0{,}2 \\ 0{,}5 & -0{,}1 & 0{,}4 \\ 0{,}2 & 0{,}6 & 0{,}0 \\ -0{,}3 & 0{,}2 & 0{,}7 \\ 0{,}4 & 0{,}4 & 0{,}1 \end{bmatrix} \begin{matrix} \leftarrow \text{susu (0)} \\ \leftarrow \text{motor (1)} \\ \leftarrow \text{kopi (2)} \\ \leftarrow \text{mobil (3)} \\ \leftarrow \text{teh (4)} \end{matrix}$$

One-hot "kopi" dikali $E$, elemen ke-$j$:
$$(e_2^\top E)_j = \sum_{i=0}^{4} (e_2)_i E_{ij} = 0 \cdot E_{0j} + 0 \cdot E_{1j} + 1 \cdot E_{2j} + 0 \cdot E_{3j} + 0 \cdot E_{4j} = E_{2j}$$
$$e_2^\top E = [0{,}2;\; 0{,}6;\; 0{,}0] = \text{baris ke-2 dari } E$$

> Embedding layer **matematis setara** dengan lapisan linear tanpa bias atas input one-hot, tetapi diimplementasikan sebagai **pengambilan baris (lookup)** — tanpa perkalian $\lvert V \rvert \times d$ yang boros.

---

# Kemiripan Antar-Embedding: Hitung Manual

$$\text{dot}(u, v) = \sum_k u_k v_k, \qquad \cos(u, v) = \frac{u \cdot v}{\lVert u \rVert \, \lVert v \rVert}$$

Dengan $\text{kopi} = [0{,}2;\, 0{,}6;\, 0{,}0]$, $\;\lVert \text{kopi} \rVert = \sqrt{0{,}04 + 0{,}36} = 0{,}6325$:

| Pasangan | Dot product | $\lVert v \rVert$ | Cosine |
|---|---|---|---|
| kopi – teh $[0{,}4;\, 0{,}4;\, 0{,}1]$ | 0,08 + 0,24 + 0 = **0,32** | $\sqrt{0{,}33} = 0{,}5745$ | 0,32 / (0,6325 × 0,5745) = **0,881** |
| kopi – susu $[0{,}1;\, 0{,}3;\, -0{,}2]$ | 0,02 + 0,18 + 0 = **0,20** | $\sqrt{0{,}14} = 0{,}3742$ | **0,845** |
| kopi – mobil $[-0{,}3;\, 0{,}2;\, 0{,}7]$ | −0,06 + 0,12 + 0 = **0,06** | $\sqrt{0{,}62} = 0{,}7874$ | **0,120** |

> Pada embedding hasil training, token yang muncul dalam **konteks serupa** memiliki cosine tinggi (*distributional hypothesis*). Dot product embedding juga menjadi inti **attention** dan **sistem rekomendasi**.

---

<!-- _class: small -->

# Gradien Embedding: Hanya Baris yang Dipakai

Kalimat (indeks) $[2, 0, 2]$ = "kopi susu kopi". Misalkan gradien dari lapisan atas untuk tiap posisi:

| Posisi | Token | $\partial L / \partial (\text{output posisi})$ |
|---|---|---|
| 1 | kopi (2) | $[0{,}1;\; -0{,}2;\; 0{,}3]$ |
| 2 | susu (0) | $[0{,}05;\; 0{,}05;\; 0{,}0]$ |
| 3 | kopi (2) | $[-0{,}4;\; 0{,}1;\; 0{,}2]$ |

Karena output posisi = baris $E$ yang diambil, gradien **dijumlahkan** ke baris tersebut (*scatter-add*):

| Baris $E$ | $\partial L / \partial E_{i,:}$ | Setelah SGD $\eta = 0{,}1$ |
|---|---|---|
| 0 (susu) | $[0{,}05;\; 0{,}05;\; 0]$ | $[0{,}095;\; 0{,}295;\; -0{,}2]$ |
| 1 (motor), 3 (mobil), 4 (teh) | $[0;\; 0;\; 0]$ | **tidak berubah** |
| 2 (kopi) | $[0{,}1 - 0{,}4;\; -0{,}2 + 0{,}1;\; 0{,}3 + 0{,}2] = [-0{,}3;\; -0{,}1;\; 0{,}5]$ | $[0{,}23;\; 0{,}61;\; -0{,}05]$ |

> Gradien embedding bersifat **sparse**: dari $\lvert V \rvert$ baris, hanya token yang muncul di batch yang menerima gradien. Token langka jarang diperbarui → kualitas embedding-nya lebih rendah.

---

# Berapa Banyak Parameternya?

$$\#\text{param} = \lvert V \rvert \times d$$

| Model / kasus | $\lvert V \rvert$ | $d$ | Parameter embedding |
|---|---|---|---|
| Contoh slide | 5 | 3 | 15 |
| BERT-base (Devlin dkk., 2019) | 30.522 | 768 | 23.440.896 (≈ 23,4 juta) |
| Kosakata 50.000, $d = 768$ | 50.000 | 768 | 38.400.000 |

- Pada model bahasa berukuran kecil–menengah, embedding bisa menjadi **porsi besar** dari seluruh parameter.
- **Weight tying** (Press & Wolf, 2017): matriks embedding input dipakai juga sebagai matriks proyeksi output (*softmax layer*) → menghemat $\lvert V \rvert \times d$ parameter dan sering memperbaiki *perplexity*.

---

# Dari Teks ke Indeks: Tokenisasi

Embedding membutuhkan **indeks bilangan bulat**; tokenisasi memecah teks menjadi unit yang ada di kosakata.

| Tingkat | Contoh "pembelajaran" | Kelebihan | Kekurangan |
|---|---|---|---|
| Kata | `pembelajaran` | Intuitif | Kosakata sangat besar; kata baru → `<unk>` |
| Karakter | `p e m b e l ...` | Kosakata kecil | Urutan sangat panjang |
| **Subword** (BPE, WordPiece, SentencePiece) | mis. `pem` `bel` `ajaran` (bergantung pada data latih) | Kosakata terkendali, tanpa `<unk>` | Pemecahan kadang tidak intuitif |

**Byte Pair Encoding** (Sennrich dkk., 2016): mulai dari karakter, lalu berulang kali **gabungkan pasangan simbol yang paling sering** muncul hingga ukuran kosakata tercapai.

Token khusus: `<pad>` (penyamaan panjang), `<unk>`, `[CLS]`, `[SEP]`, `<bos>`, `<eos>`.

---

# Embedding Kata Pra-latih: word2vec & GloVe

| Metode | Ide | Tujuan training |
|---|---|---|
| **word2vec** — CBOW & Skip-gram (Mikolov dkk., 2013a, 2013b) | Prediksi kata dari konteks (CBOW) atau konteks dari kata (Skip-gram) | Dengan *negative sampling*: dot product pasangan kata–konteks nyata dinaikkan, pasangan acak diturunkan |
| **GloVe** (Pennington dkk., 2014) | Faktorisasi statistik ko-okurensi global | $\sum_{i,j} f(X_{ij})\,(w_i^\top \tilde{w}_j + b_i + \tilde{b}_j - \log X_{ij})^2$ |

Sifat yang terkenal — **analogi linear** (Mikolov dkk., 2013a):
$$\mathbf{v}_{\text{king}} - \mathbf{v}_{\text{man}} + \mathbf{v}_{\text{woman}} \approx \mathbf{v}_{\text{queen}}$$

**Keterbatasan**: satu vektor per kata (**statis**) — "bisa" (dapat) dan "bisa" (racun) mendapat vektor sama. Model Transformer menghasilkan embedding **kontekstual** yang berbeda menurut kalimat.

---

<!-- _class: small -->

# Positional Encoding (Vaswani dkk., 2017)

Self-attention tidak mengenal urutan, sehingga informasi posisi **ditambahkan** ke embedding token: $x_\text{pos} = \text{embed}(\text{token}) + PE(\text{pos})$.

$$PE(\text{pos}, 2i) = \sin\!\left(\frac{\text{pos}}{10000^{2i/d}}\right), \qquad PE(\text{pos}, 2i+1) = \cos\!\left(\frac{\text{pos}}{10000^{2i/d}}\right)$$

**Hitung manual**, $d = 4$ (sudut dalam radian):

| Dimensi | $i$ | Pembagi $10000^{2i/4}$ | pos = 0 | pos = 1 | pos = 2 |
|---|---|---|---|---|---|
| 0 (sin) | 0 | 1 | 0 | sin(1) = 0,8415 | sin(2) = 0,9093 |
| 1 (cos) | 0 | 1 | 1 | cos(1) = 0,5403 | cos(2) = −0,4161 |
| 2 (sin) | 1 | 100 | 0 | sin(0,01) = 0,0100 | sin(0,02) = 0,0200 |
| 3 (cos) | 1 | 100 | 1 | cos(0,01) = 0,99995 | cos(0,02) = 0,9998 |

- Dimensi rendah berosilasi **cepat**, dimensi tinggi **lambat** — seperti jarum detik vs jarum jam.
- Alternatif: **learned positional embedding** (tabel `nn.Embedding(max_len, d)`, dipakai BERT dan GPT-2), serta RoPE.

---

# Entity Embedding untuk Data Tabular

Guo & Berkhahn (2016): variabel kategorikal (toko, hari, negara bagian) pada data penjualan Rossmann dipetakan ke embedding yang dipelajari jaringan.

| Fitur | Kardinalitas | Representasi |
|---|---|---|
| ID toko | ±1.000 | `nn.Embedding(n_toko, 10)` |
| Hari dalam minggu | 7 | `nn.Embedding(7, 4)` |
| Fitur numerik | — | Standardisasi $z = (x - \mu)/\sigma$ |

```text
[emb(toko) ; emb(hari) ; fitur_numerik] → concat → MLP → prediksi
```

Manfaat yang dilaporkan: embedding yang dipelajari mengelompokkan kategori serupa dan dapat **dipakai ulang** sebagai fitur bagi model lain.

> Aturan praktis dimensi embedding bersifat heuristik (mis. $\min(50, \lceil n/2 \rceil)$ di beberapa pustaka); perlakukan sebagai hiperparameter.

---

<!-- _class: divider -->

# Representasi Bilangan di Komputer

Bagaimana nilai-nilai embedding & bobot disimpan?

---

# Floating Point IEEE 754

$$x = (-1)^{s} \times 1.f \times 2^{\,e - \text{bias}}$$

| Format | Bit total | Sign | Exponent | Fraction (mantissa) | Bias | Nilai maksimum |
|---|---|---|---|---|---|---|
| **float32** (FP32) | 32 | 1 | 8 | 23 | 127 | ≈ 3,40 × 10³⁸ |
| **float16** (FP16) | 16 | 1 | 5 | 10 | 15 | 65.504 |
| **bfloat16** (BF16) | 16 | 1 | 8 | 7 | 127 | ≈ 3,39 × 10³⁸ |

- **FP16**: presisi lebih baik dari BF16, tetapi **rentang sempit** → gradien kecil bisa *underflow* → perlu *loss scaling* (Micikevicius dkk., 2018).
- **BF16**: rentang sama dengan FP32 (8 bit exponent), presisi lebih rendah → populer untuk training (Kalamkar dkk., 2019).
- Memori: 1 juta parameter = 4 MB (FP32) atau 2 MB (FP16/BF16).

---

<!-- _class: tiny -->

# Hitung Manual: Encoding float32

**Contoh 1: $6{,}5$**
- Biner: $6{,}5 = 110{,}1_2 = 1{,}101_2 \times 2^2$
- Sign $s = 0$; exponent $= 2 + 127 = 129 = 10000001_2$; fraction $= 101\,0000\ldots0$ (23 bit)
- Bit: `0 | 10000001 | 10100000000000000000000`

**Contoh 2: $-0{,}15625$**
- $0{,}15625 = 0{,}00101_2 = 1{,}01_2 \times 2^{-3}$
- $s = 1$; exponent $= -3 + 127 = 124 = 01111100_2$; fraction $= 01\,0000\ldots0$
- Bit: `1 | 01111100 | 01000000000000000000000`

**Contoh 3: $0{,}1$ tidak dapat disimpan tepat** (biner berulang $0{,}0\overline{0011}_2$)

| Format | Nilai yang tersimpan untuk 0,1 |
|---|---|
| float32 | 0,100000001490116… |
| float16 | 0,0999755859375 |
| bfloat16 | 0,10009765625 |

> Inilah sebabnya `0.1 + 0.2 == 0.3` bernilai `False`, dan mengapa *mixed precision* perlu dikelola hati-hati.

---

<!-- _class: small -->

# PyTorch: `nn.Embedding`

```python
import torch, torch.nn as nn

emb = nn.Embedding(num_embeddings=5, embedding_dim=3)   # bobot awal ~ N(0, 1)
with torch.no_grad():
    emb.weight.copy_(torch.tensor([[0.1, 0.3, -0.2], [0.5, -0.1, 0.4], [0.2, 0.6, 0.0],
                                   [-0.3, 0.2, 0.7], [0.4, 0.4, 0.1]]))

ids = torch.tensor([2, 0, 2])                  # "kopi susu kopi"
out = emb(ids)                                 # shape (3, 3) = baris 2, 0, 2
print(out[0])                                  # tensor([0.2000, 0.6000, 0.0000])

G = torch.tensor([[0.1, -0.2, 0.3], [0.05, 0.05, 0.0], [-0.4, 0.1, 0.2]])
out.backward(G)                                # gradien dari lapisan atas
print(emb.weight.grad)                         # baris 2 = [-0.3, -0.1, 0.5]; baris 0 = [0.05, 0.05, 0.0]; lainnya 0

print(nn.functional.cosine_similarity(emb.weight[2], emb.weight[4], dim=0))   # ~0.881
```

| Argumen | Fungsi |
|---|---|
| `padding_idx=0` | Baris untuk token `<pad>` diinisialisasi nol dan **tidak diperbarui** |
| `sparse=True` | Gradien disimpan sebagai tensor *sparse* (hemat untuk kosakata sangat besar) |
| `nn.Embedding.from_pretrained(W, freeze=True)` | Memuat embedding pra-latih (mis. GloVe) |

---

# Jebakan Umum

| Jebakan | Akibat | Solusi |
|---|---|---|
| Indeks di luar rentang $[0, \lvert V \rvert - 1]$ | Error *index out of range* (di GPU: *device-side assert*) | Validasi tokenizer & ukuran kosakata |
| Token `<pad>` ikut dipelajari & dirata-rata | Representasi kalimat bias oleh panjang padding | `padding_idx` + *masking* |
| Memakai label encoding sebagai input numerik | Urutan palsu antar-kategori | Embedding atau one-hot |
| Kosakata tidak disimpan bersama model | Indeks tidak cocok saat inferensi | Simpan tokenizer/vocab sebagai artefak |
| Membandingkan embedding dengan jarak Euclid tanpa normalisasi | Didominasi norma vektor | Cosine similarity / normalisasi |
| Training FP16 tanpa loss scaling | Gradien underflow → NaN / tidak belajar | AMP (`torch.autocast` + `GradScaler`) atau BF16 |

---

# Latihan

Kosakata 4 token dengan $E = \begin{bmatrix} 1 & 0 \\ 0 & 1 \\ 1 & 1 \\ -1 & 1 \end{bmatrix}$ (baris 0–3).

1. Hitung $e_2^\top E$ dengan perkalian one-hot dan tunjukkan hasilnya sama dengan *lookup* baris 2.
2. Hitung cosine similarity pasangan (0, 2), (0, 3), dan (2, 3).
3. Kalimat $[3, 1, 3]$ menerima gradien $[0{,}1;\, 0{,}2]$, $[0{,}3;\, -0{,}1]$, $[-0{,}2;\, 0{,}4]$. Tentukan gradien setiap baris $E$.
4. Berapa parameter embedding untuk $\lvert V \rvert = 30.000$, $d = 512$?
5. Hitung positional encoding $PE(0, \cdot)$ untuk $d = 4$.
6. Tuliskan representasi float32 dari $5{,}0$ dan $-2{,}75$.

---

<!-- _class: small -->

# Kunci Jawaban Latihan

1. $e_2 = [0, 0, 1, 0]$; $e_2^\top E = 0 \cdot [1, 0] + 0 \cdot [0, 1] + 1 \cdot [1, 1] + 0 \cdot [-1, 1] = \mathbf{[1, 1]}$ = baris 2 ✓
2. $\cos(0, 2) = \frac{1}{1 \cdot \sqrt{2}} = \mathbf{0{,}707}$; $\cos(0, 3) = \frac{-1}{1 \cdot \sqrt{2}} = \mathbf{-0{,}707}$; $\cos(2, 3) = \frac{-1 + 1}{\sqrt{2}\sqrt{2}} = \mathbf{0}$
3. Baris 3: $[0{,}1 - 0{,}2;\; 0{,}2 + 0{,}4] = \mathbf{[-0{,}1;\; 0{,}6]}$; baris 1: $\mathbf{[0{,}3;\; -0{,}1]}$; baris 0 dan 2: $\mathbf{[0;\; 0]}$
4. $30.000 \times 512 = \mathbf{15.360.000}$ parameter
5. $PE(0) = [\sin 0, \cos 0, \sin 0, \cos 0] = \mathbf{[0, 1, 0, 1]}$
6. $5{,}0 = 1{,}01_2 \times 2^2$ → `0 | 10000001 | 01000000000000000000000`
   $-2{,}75 = -10{,}11_2 = -1{,}011_2 \times 2^1$ → exponent $1 + 127 = 128$ → `1 | 10000000 | 01100000000000000000000`

---

# Ringkasan

1. Data diskret harus diubah menjadi bilangan; **label encoding** memaksakan urutan palsu, **one-hot** besar dan tidak menangkap kemiripan.
2. **Embedding layer** = tabel $E \in \mathbb{R}^{\lvert V \rvert \times d}$ yang dipelajari; secara matematis one-hot × $E$, secara implementasi **lookup baris**.
3. Gradien embedding **sparse**: hanya baris token yang muncul yang diperbarui; token berulang → gradien **dijumlahkan**.
4. Kemiripan diukur dengan **dot product / cosine**; dasar word2vec, GloVe, attention, rekomendasi.
5. Transformer menambahkan **positional encoding** (sinusoidal atau dipelajari).
6. Bilangan disimpan sebagai **floating point**: FP32, FP16 (rentang sempit), BF16 (rentang FP32, presisi rendah).

---

<!-- _class: tiny -->

# Referensi

1. Bengio, Y., Ducharme, R., Vincent, P., & Jauvin, C. (2003). A neural probabilistic language model. *JMLR*, 3, 1137–1155.
2. Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. *NAACL-HLT*.
3. Goodfellow, I., Bengio, Y., & Courville, A. (2016). *Deep Learning*, §4.1 (Overflow and Underflow) & §12.4 (Natural Language Processing). MIT Press.
4. Guo, C., & Berkhahn, F. (2016). Entity embeddings of categorical variables. *arXiv:1604.06737*.
5. IEEE (2019). *IEEE Standard for Floating-Point Arithmetic* (IEEE Std 754-2019).
6. Kalamkar, D., dkk. (2019). A study of BFLOAT16 for deep learning training. *arXiv:1905.12322*.
7. Micikevicius, P., dkk. (2018). Mixed precision training. *ICLR*.
8. Mikolov, T., Chen, K., Corrado, G., & Dean, J. (2013a). Efficient estimation of word representations in vector space. *arXiv:1301.3781*.
9. Mikolov, T., Sutskever, I., Chen, K., Corrado, G., & Dean, J. (2013b). Distributed representations of words and phrases and their compositionality. *NeurIPS*.
10. Pennington, J., Socher, R., & Manning, C. D. (2014). GloVe: Global vectors for word representation. *EMNLP*.
11. Press, O., & Wolf, L. (2017). Using the output embedding to improve language models. *EACL*.
12. Sennrich, R., Haddow, B., & Birch, A. (2016). Neural machine translation of rare words with subword units. *ACL*.
13. Vaswani, A., dkk. (2017). Attention is all you need. *NeurIPS*.
14. Zhang, A., Lipton, Z. C., Li, M., & Smola, A. J. (2023). *Dive into Deep Learning*, Bab 15 (NLP: Pretraining). Cambridge University Press.

---

<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _header: '' -->

# Terima Kasih

### Building Blocks of Deep Learning — selesai

Kerjakan latihan dan coba `nn.Embedding` di PyTorch
