---
marp: true
theme: default
paginate: true
size: 16:9
math: mathjax
header: 'Building Blocks of Deep Learning · Multiplicative Layers'
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

# Multiplicative Layers
## Gating · GLU/SwiGLU · Highway · Bilinear · Squeeze-and-Excitation

### Minggu 0 — Deep Learning: Building Blocks
**Sains Data ITERA · Ganjil 2026/2025**

---

# Capaian Pembelajaran & Agenda

> Mahasiswa mampu menjelaskan peran **interaksi multiplikatif** dalam jaringan saraf, menghitung manual GLU, SwiGLU, layer bilinear, dan blok Squeeze-and-Excitation, serta menganalisis bagaimana *gate* mengatur aliran gradien.

1. Apa yang dimaksud *multiplicative layer*? (batasan istilah)
2. Penjumlahan vs perkalian: mengapa perkalian menambah ekspresivitas
3. **Gating**: $\sigma(\cdot) \odot (\cdot)$ dan gradiennya
4. **GLU** dan varian **SwiGLU/GEGLU** (dipakai di LLM modern)
5. **Highway network** & *gate* pada LSTM/GRU
6. **Layer bilinear** dan kerangka *multiplicative interactions*
7. **Squeeze-and-Excitation**: *gating* per kanal pada CNN
8. Attention sebagai interaksi multiplikatif · PyTorch · latihan

---

# Batasan Istilah

"*Multiplicative layer*" **bukan** nama satu layer baku di pustaka seperti `nn.Linear` atau `nn.Conv2d`. Dalam materi ini istilah tersebut dipakai untuk:

> **Layer yang menggabungkan dua sinyal hasil pembelajaran melalui perkalian** (elemen-per-elemen atau bilinear), bukan hanya penjumlahan berbobot.

| Layer biasa (aditif) | Layer multiplikatif |
|---|---|
| $y = Wx + b$ | $y = (W x) \odot \sigma(V x)$ (gating) |
| $y = W_1 x + W_2 z$ | $y = x^\top W z$ (bilinear) |
| Kontribusi tiap input **dijumlahkan** | Satu sinyal **mengatur skala** sinyal lain |

Kerangka umum ini dibahas oleh Jayakumar dkk. (2020), *"Multiplicative Interactions and Where to Find Them"* (ICLR), yang menunjukkan bahwa *gating*, *hypernetwork*, dan *attention* adalah kasus khusus interaksi multiplikatif.

---

# Mengapa Perkalian?

Perhatikan fungsi dua input $f(x, z) = x \cdot z$.

- Layer linear $w_1 x + w_2 z + b$ **tidak bisa** merepresentasikannya secara tepat: hasilnya bidang datar, sedangkan $x \cdot z$ berbentuk pelana.
- MLP dengan aktivasi non-linear **bisa mendekati** $x \cdot z$, tetapi butuh banyak neuron.
- Layer multiplikatif mendapatkannya **langsung** dengan satu operasi.

| Peran perkalian | Contoh |
|---|---|
| **Saklar / filter** konteks | $\sigma(\cdot) \approx 0$ menutup, $\approx 1$ membuka |
| **Skala adaptif** per fitur | SE-block mengalikan setiap kanal dengan bobot 0–1 |
| **Kesamaan** dua representasi | $q^\top k$ pada attention |
| **Pengondisian** | Representasi $z$ (mis. teks) memodulasi $x$ (mis. citra) |

---

<!-- _class: divider -->

# Gating & Gradiennya

---

# Gate: Perkalian dengan Nilai di $(0, 1)$

$$y = a \odot s, \qquad s = \sigma(b) = \frac{1}{1 + e^{-b}} \in (0, 1)$$

$a$ = **isi** (konten), $s$ = **gate** (berapa banyak isi yang dilewatkan). Keduanya hasil layer yang dipelajari.

**Gradien (aturan perkalian)**:
$$\frac{\partial y}{\partial a} = s, \qquad \frac{\partial y}{\partial b} = a \cdot s(1 - s)$$

**Hitung manual** dengan $a = 2$:

| Kondisi gate | $s$ | $\partial y / \partial a = s$ | $\partial y / \partial b = a\,s(1-s)$ |
|---|---|---|---|
| Tertutup | 0,01 | 0,01 | 2(0,01)(0,99) = 0,0198 |
| Setengah | 0,50 | 0,50 | 2(0,5)(0,5) = 0,5000 |
| Terbuka | 0,99 | 0,99 | 2(0,99)(0,01) = 0,0198 |

> Gate **tertutup** juga memblokir gradien ke $a$; gate **terbuka** meneruskan gradien hampir utuh. Inilah mekanisme LSTM/GRU untuk menjaga gradien jangka panjang.

---

# GLU — Gated Linear Unit (Dauphin dkk., 2017)

$$\text{GLU}(x) = (xW + b) \odot \sigma(xV + c)$$

- Diperkenalkan untuk *language modeling* dengan CNN.
- Gradien: $\nabla[X \odot \sigma(X')] = \nabla X \odot \sigma(X') + X \odot \sigma'(X')\nabla X'$. Suku pertama adalah **jalur linear** yang hanya diskalakan oleh gate — tidak melewati turunan aktivasi — sehingga gradien lebih mudah mengalir dibanding tanh-gating.

**Versi PyTorch `nn.GLU(dim)`**: input dibagi dua sama besar $[a \,|\, b]$ pada dimensi `dim`, lalu $\text{GLU} = a \odot \sigma(b)$.

**Hitung manual**: input $v = (2,\; -1,\; 0{,}5 \;|\; 3,\; 0,\; -2)$

| | Elemen 1 | Elemen 2 | Elemen 3 |
|---|---|---|---|
| $a$ | 2 | −1 | 0,5 |
| $b$ | 3 | 0 | −2 |
| $\sigma(b)$ | 0,9526 | 0,5000 | 0,1192 |
| $a \odot \sigma(b)$ | **1,9051** | **−0,5000** | **0,0596** |

Output berdimensi **setengah** input (6 → 3).

---

<!-- _class: small -->

# Hitung Manual: GLU dengan Bobot

$x = (1, 2)$, tanpa bias:
$$W = \begin{bmatrix} 1 & 0 & 1 \\ 0 & 1 & -1 \end{bmatrix}, \qquad V = \begin{bmatrix} 0{,}5 & 0 & 1 \\ -1 & 1 & 0 \end{bmatrix}$$

| Langkah | Elemen 1 | Elemen 2 | Elemen 3 |
|---|---|---|---|
| $xW$ | $1(1) + 2(0) = 1$ | $1(0) + 2(1) = 2$ | $1(1) + 2(-1) = -1$ |
| $xV$ | $1(0{,}5) + 2(-1) = -1{,}5$ | $1(0) + 2(1) = 2$ | $1(1) + 2(0) = 1$ |
| $\sigma(xV)$ | 0,1824 | 0,8808 | 0,7311 |
| $\text{GLU} = xW \odot \sigma(xV)$ | **0,1824** | **1,7616** | **−0,7311** |

**Interpretasi**: fitur 1 bernilai 1 tetapi "ditekan" gate (18%); fitur 2 diloloskan 88%; fitur 3 diloloskan 73%. Gate bergantung pada **input itu sendiri** → penyaringan adaptif per sampel.

---

# Varian GLU: SwiGLU & GEGLU (Shazeer, 2020)

Ganti $\sigma$ pada gate dengan aktivasi lain, dipakai di **feed-forward block Transformer**:

$$\text{FFN}_{\text{GLU}}(x) = \left(\sigma(xW) \odot xV\right)W_2$$
$$\text{FFN}_{\text{GEGLU}}(x) = \left(\text{GELU}(xW) \odot xV\right)W_2$$
$$\text{FFN}_{\text{SwiGLU}}(x) = \left(\text{Swish}_1(xW) \odot xV\right)W_2, \qquad \text{Swish}_1(u) = u\,\sigma(u)$$

- Bias dihilangkan mengikuti Shazeer (2020).
- Ada **3 matriks** ($W, V, W_2$) dibanding 2 pada FFN biasa → agar jumlah parameter setara, dimensi tersembunyi dikecilkan menjadi $\tfrac{2}{3}$ dari biasanya (mis. $\tfrac{2}{3} \cdot 4d$).
- Shazeer (2020) melaporkan GEGLU dan SwiGLU memberi *perplexity* lebih baik daripada FFN ReLU/GELU pada T5.
- SwiGLU dipakai pada **PaLM** (Chowdhery dkk., 2022) dan **LLaMA** (Touvron dkk., 2023).

---

<!-- _class: small -->

# Hitung Manual: SwiGLU

Memakai $x$, $W$, $V$ dari slide sebelumnya ($xW = (1, 2, -1)$, $xV = (-1{,}5;\; 2;\; 1)$), dan
$$W_2 = \begin{bmatrix} 1 & 0 \\ 0 & 1 \\ 1 & 1 \end{bmatrix}$$

| Langkah | Elemen 1 | Elemen 2 | Elemen 3 |
|---|---|---|---|
| $u = xW$ | 1 | 2 | −1 |
| $\sigma(u)$ | 0,7311 | 0,8808 | 0,2689 |
| $\text{Swish}(u) = u\,\sigma(u)$ | 0,7311 | 1,7616 | −0,2689 |
| $xV$ | −1,5 | 2 | 1 |
| $\text{Swish}(u) \odot xV$ | −1,0966 | 3,5232 | −0,2689 |

$$\text{output} = (-1{,}0966;\; 3{,}5232;\; -0{,}2689)\,W_2 = (-1{,}0966 - 0{,}2689;\;\; 3{,}5232 - 0{,}2689) = (\mathbf{-1{,}3655};\; \mathbf{3{,}2542})$$

> Bandingkan dengan GLU: di sini **gate** adalah $xV$ (linear, bisa negatif) dan **isi** melewati Swish. Dalam literatur, peran "isi" dan "gate" pada SwiGLU sering dipertukarkan — yang penting adalah **perkalian dua proyeksi**.

---

# Highway Network (Srivastava dkk., 2015) & Gate pada RNN

$$y = H(x) \odot T(x) + x \odot (1 - T(x)), \qquad T(x) = \sigma(W_T x + b_T)$$

$T$ = *transform gate*; $1 - T$ = *carry gate*. Bias $b_T$ diinisialisasi **negatif** agar awalnya informasi cenderung di-*carry*.

**Hitung manual**: $x = (1, 1)$, $H(x) = (2, -1)$, pra-aktivasi gate $(0, -2)$:

| | Elemen 1 | Elemen 2 |
|---|---|---|
| $T = \sigma(\cdot)$ | 0,5000 | 0,1192 |
| $H \odot T$ | 1,0000 | −0,1192 |
| $x \odot (1 - T)$ | 0,5000 | 0,8808 |
| $y$ | **1,5000** | **0,7616** |

| Arsitektur | Persamaan multiplikatif |
|---|---|
| LSTM | $c_t = f_t \odot c_{t-1} + i_t \odot g_t$, $h_t = o_t \odot \tanh(c_t)$ |
| GRU | $h_t = (1 - z_t) \odot \tilde{h}_t + z_t \odot h_{t-1}$ |
| Highway | interpolasi $H(x)$ dan $x$ |
| ResNet | kasus khusus tanpa gate: $y = F(x) + x$ |

---

<!-- _class: divider -->

# Bilinear & Multiplicative Interactions

---

# Layer Bilinear

Untuk dua input $x_1 \in \mathbb{R}^{d_1}$ dan $x_2 \in \mathbb{R}^{d_2}$, setiap output $k$:

$$y_k = x_1^\top A_k\, x_2 + b_k, \qquad A_k \in \mathbb{R}^{d_1 \times d_2}$$

PyTorch: `nn.Bilinear(in1_features, in2_features, out_features)` dengan bobot berbentuk `(out, in1, in2)`.

**Hitung manual** ($1$ output): $x_1 = (1, 2)$, $x_2 = (3, -1)$, $b = 0{,}1$
$$A = \begin{bmatrix} 1 & 0{,}5 \\ -1 & 2 \end{bmatrix}, \quad A x_2 = \begin{bmatrix} 1(3) + 0{,}5(-1) \\ -1(3) + 2(-1) \end{bmatrix} = \begin{bmatrix} 2{,}5 \\ -5 \end{bmatrix}$$
$$y = x_1^\top (A x_2) + b = 1(2{,}5) + 2(-5) + 0{,}1 = \mathbf{-7{,}4}$$

- Setiap pasangan $(x_{1,i}, x_{2,j})$ memiliki bobot sendiri $A_{ij}$ → menangkap **interaksi** antar-fitur.
- Jumlah parameter $= \text{out} \times d_1 \times d_2$ — cepat membesar; dalam praktik sering difaktorkan (*low-rank*).

---

# Kerangka Multiplicative Interactions (Jayakumar dkk., 2020)

Layer **MI** untuk input $x$ dan konteks $z$:

$$f(x, z) = z^\top \mathbb{W} x + z^\top U + V x + b$$

dengan $\mathbb{W}$ tensor orde-3 (bilinear), $U$, $V$ matriks, $b$ bias.

| Kasus khusus | Bentuk |
|---|---|
| Layer linear biasa (konkatenasi $[x; z]$) | $\mathbb{W} = 0$ |
| **Gating** | $\mathbb{W}$ diagonal → $z$ menskala tiap komponen $x$ |
| **Hypernetwork** | $z$ menghasilkan bobot $W(z) = z^\top \mathbb{W}$ yang diterapkan ke $x$ |
| **Attention** | skor $q^\top k$ = bilinear antara dua proyeksi |

Temuan utama makalah: interaksi multiplikatif memperluas kelas fungsi yang dapat direpresentasikan secara **efisien** (lebih sedikit parameter/layer) dibanding hanya konkatenasi + MLP.

---

# Attention sebagai Interaksi Multiplikatif

$$\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V, \qquad Q = XW_Q,\; K = XW_K,\; V = XW_V$$

Dua tingkat perkalian:
1. **Skor** $q_i^\top k_j = x_i^\top (W_Q W_K^\top) x_j$ → bentuk **bilinear** dalam $x_i$ dan $x_j$.
2. **Bobot attention** $\alpha_{ij}$ (bergantung data) **dikalikan** dengan $v_j$ → bobot "dinamis", tidak tetap seperti $W$ pada layer linear.

**Contoh mini**: $q = (1, 0)$, $k_1 = (2, 1)$, $k_2 = (0, 3)$, $d_k = 2$:
$$\frac{q^\top k_1}{\sqrt{2}} = \frac{2}{1{,}4142} = 1{,}4142, \quad \frac{q^\top k_2}{\sqrt{2}} = 0$$
$$\alpha = \text{softmax}(1{,}4142;\; 0) = (0{,}8044;\; 0{,}1956)$$

> Materi lengkap ada pada topik *Attention Layers* dan pertemuan *Transformer*.

---

<!-- _class: divider -->

# Squeeze-and-Excitation (SE) Block

---

# SE Block (Hu, Shen & Sun, 2018)

*Gating* per **kanal** pada CNN. Untuk feature map $U \in \mathbb{R}^{C \times H \times W}$:

1. **Squeeze** — *global average pooling*: $z_c = \dfrac{1}{HW}\sum_{i,j} U_c(i, j)$
2. **Excitation** — MLP kecil dengan *bottleneck* rasio $r$:
$$s = \sigma\!\left(W_2\, \text{ReLU}(W_1 z)\right), \quad W_1 \in \mathbb{R}^{\frac{C}{r} \times C},\; W_2 \in \mathbb{R}^{C \times \frac{C}{r}}$$
3. **Scale** — $\tilde{U}_c = s_c \cdot U_c$ (setiap kanal dikalikan bobot 0–1)

- Jaringan belajar **kanal mana yang penting** untuk input tertentu.
- Tambahan parameter kecil ($2C^2/r$ per blok), peningkatan akurasi konsisten pada ImageNet; SENet memenangkan klasifikasi ILSVRC 2017.

---

<!-- _class: small -->

# Hitung Manual: SE Block ($C = 4$, $r = 2$, peta $2 \times 2$)

| Kanal | Feature map $U_c$ | Squeeze $z_c$ |
|---|---|---|
| 1 | [[1, 3], [2, 2]] | (1+3+2+2)/4 = **2,0** |
| 2 | [[0, 0], [1, 1]] | 2/4 = **0,5** |
| 3 | [[4, 4], [4, 4]] | 16/4 = **4,0** |
| 4 | [[−1, 1], [−3, 3]] | 0/4 = **0,0** |

$$W_1 = \begin{bmatrix} 0{,}5 & 0 & 0{,}25 & 0 \\ 0 & 1 & 0 & -1 \end{bmatrix} \Rightarrow W_1 z = \begin{bmatrix} 0{,}5(2) + 0{,}25(4) \\ 1(0{,}5) - 1(0) \end{bmatrix} = \begin{bmatrix} 2 \\ 0{,}5 \end{bmatrix} \xrightarrow{\text{ReLU}} \begin{bmatrix} 2 \\ 0{,}5 \end{bmatrix}$$

$$W_2 = \begin{bmatrix} 1 & 0 \\ 0 & 1 \\ 1 & -1 \\ -1 & 1 \end{bmatrix} \Rightarrow W_2 u = \begin{bmatrix} 2 \\ 0{,}5 \\ 1{,}5 \\ -1{,}5 \end{bmatrix} \xrightarrow{\sigma} s = \begin{bmatrix} 0{,}8808 \\ 0{,}6225 \\ 0{,}8176 \\ 0{,}1824 \end{bmatrix}$$

**Scale** kanal 1: $0{,}8808 \times$ [[1, 3], [2, 2]] = [[0,8808; 2,6424], [1,7616; 1,7616]]. Kanal 4 diredam menjadi 18% — dianggap kurang informatif untuk input ini.

---

<!-- _class: small -->

# PyTorch

```python
import torch, torch.nn as nn, torch.nn.functional as F

# 1) GLU bawaan: membagi dimensi terakhir menjadi dua
v = torch.tensor([2., -1., 0.5, 3., 0., -2.])
print(F.glu(v, dim=-1))            # tensor([ 1.9051, -0.5000,  0.0596])

# 2) SwiGLU feed-forward (gaya LLaMA, tanpa bias)
class SwiGLU(nn.Module):
    def __init__(self, d, d_ff):
        super().__init__()
        self.w = nn.Linear(d, d_ff, bias=False)
        self.v = nn.Linear(d, d_ff, bias=False)
        self.w2 = nn.Linear(d_ff, d, bias=False)
    def forward(self, x):
        return self.w2(F.silu(self.w(x)) * self.v(x))   # F.silu(u) = u * sigmoid(u) = Swish_1

# 3) Bilinear
bil = nn.Bilinear(2, 2, 1)          # weight: (1, 2, 2), bias: (1,)

# 4) Squeeze-and-Excitation
class SE(nn.Module):
    def __init__(self, C, r=16):
        super().__init__()
        self.fc = nn.Sequential(nn.Linear(C, C // r), nn.ReLU(), nn.Linear(C // r, C), nn.Sigmoid())
    def forward(self, U):                       # U: (N, C, H, W)
        s = self.fc(U.mean(dim=(2, 3)))          # squeeze + excitation -> (N, C)
        return U * s[:, :, None, None]           # scale per kanal
```

---

# Kapan Memakai & Hal yang Perlu Diperhatikan

| Situasi | Pilihan |
|---|---|
| Feed-forward pada Transformer/LLM | **SwiGLU** atau GEGLU |
| Sequence model berbasis konvolusi | **GLU** |
| CNN, ingin bobot kanal adaptif | **SE block** |
| Dua modalitas / input + konteks (mis. VQA, *conditioning*) | **Bilinear** (low-rank) atau gating oleh konteks |
| Jaringan sangat dalam tanpa skip connection | **Highway** (kini umumnya digantikan residual) |

**Perhatian**
- Perkalian dua sinyal dapat **memperbesar skala** aktivasi → perhatikan inisialisasi dan normalisasi.
- Gate sigmoid yang **jenuh** (≈ 0) memblokir gradien; inisialisasi bias gate dengan bijak (mis. bias *forget gate* LSTM positif, bias *transform gate* highway negatif).
- Bilinear penuh berparameter $O(d_1 d_2)$ per output — gunakan faktorisasi.

---

# Latihan

1. Hitung `GLU` untuk $v = (1, -2 \,|\, 0, 2)$.
2. Gate $y = a \cdot \sigma(b)$ dengan $a = 4$, $b = 0$. Hitung $y$, $\partial y/\partial a$, dan $\partial y/\partial b$.
3. Hitung $\text{Swish}_1(u)$ untuk $u = 0$ dan $u = 2$.
4. Layer bilinear: $x_1 = (2, 0)$, $x_2 = (1, 1)$, $A = \begin{bmatrix} 1 & -1 \\ 3 & 4 \end{bmatrix}$, $b = 0$. Hitung $y$.
5. Highway: $x = 2$, $H(x) = -1$, pra-aktivasi gate $= 0$. Hitung $y$.
6. SE block: squeeze menghasilkan $z = (1, 3)$; $W_1 = [1, -1]$ (1×2), $W_2 = [1, -1]^\top$ (2×1). Hitung $s$.

---

<!-- _class: small -->

# Kunci Jawaban

1. $a = (1, -2)$, $b = (0, 2)$, $\sigma(b) = (0{,}5;\; 0{,}8808)$ → $\text{GLU} = (\mathbf{0{,}5};\; \mathbf{-1{,}7616})$
2. $\sigma(0) = 0{,}5$ → $y = \mathbf{2}$; $\partial y/\partial a = \mathbf{0{,}5}$; $\partial y/\partial b = 4(0{,}5)(0{,}5) = \mathbf{1}$
3. $\text{Swish}(0) = 0 \times 0{,}5 = \mathbf{0}$; $\text{Swish}(2) = 2 \times 0{,}8808 = \mathbf{1{,}7616}$
4. $Ax_2 = (1 - 1;\; 3 + 4) = (0, 7)$; $y = 2(0) + 0(7) = \mathbf{0}$
5. $T = \sigma(0) = 0{,}5$ → $y = -1(0{,}5) + 2(0{,}5) = \mathbf{0{,}5}$
6. $W_1 z = 1 - 3 = -2 \xrightarrow{\text{ReLU}} 0$ → $W_2 \cdot 0 = (0, 0)$ → $s = (\mathbf{0{,}5};\; \mathbf{0{,}5})$. Catatan: ReLU yang mati membuat semua kanal mendapat bobot netral 0,5.

---

# Ringkasan

1. *Multiplicative layer* = layer yang **mengalikan dua sinyal terpelajari**, bukan sekadar menjumlahkan.
2. **Gate** $\sigma(\cdot) \odot (\cdot)$ mengatur aliran informasi **dan** gradien: $\partial y/\partial a = s$.
3. **GLU** (Dauphin dkk., 2017) dan **SwiGLU/GEGLU** (Shazeer, 2020) — standar FFN pada LLM modern.
4. **Highway**, **LSTM**, **GRU** memakai gate untuk interpolasi informasi lama dan baru.
5. **Bilinear** $x_1^\top A x_2$ menangkap interaksi pasangan fitur; *gating*, *hypernetwork*, dan *attention* adalah kasus khusus *multiplicative interactions* (Jayakumar dkk., 2020).
6. **SE block** = gating per kanal pada CNN (Hu dkk., 2018).

---

<!-- _class: small -->

# Referensi

1. Srivastava, R. K., Greff, K., & Schmidhuber, J. (2015). Training very deep networks. *NeurIPS*. (versi awal: Highway networks, arXiv:1505.00387)
2. Dauphin, Y. N., Fan, A., Auli, M., & Grangier, D. (2017). Language modeling with gated convolutional networks. *ICML*.
3. Hu, J., Shen, L., & Sun, G. (2018). Squeeze-and-excitation networks. *CVPR*.
4. Jayakumar, S. M., dkk. (2020). Multiplicative interactions and where to find them. *ICLR*.
5. Shazeer, N. (2020). GLU variants improve Transformer. *arXiv:2002.05202*.
6. Vaswani, A., dkk. (2017). Attention is all you need. *NeurIPS*.
7. Chowdhery, A., dkk. (2022). PaLM: Scaling language modeling with Pathways. *arXiv:2204.02311*.
8. Touvron, H., dkk. (2023). LLaMA: Open and efficient foundation language models. *arXiv:2302.13971*.
9. Hochreiter, S., & Schmidhuber, J. (1997). Long short-term memory. *Neural Computation*, 9(8), 1735–1780.
10. Zhang, A., Lipton, Z. C., Li, M., & Smola, A. J. (2023). *Dive into Deep Learning*. Cambridge University Press. https://d2l.ai
11. Dokumentasi PyTorch: `torch.nn.GLU`, `torch.nn.Bilinear`, `torch.nn.functional.silu`.

---

<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _header: '' -->

# Terima Kasih

### Berikutnya: **Implicit Layers**

Kerjakan latihan, lalu bandingkan FFN ReLU vs SwiGLU pada model kecil
