---
marp: true
theme: default
paginate: true
size: 16:9
math: mathjax
header: 'Building Blocks of Deep Learning · Adaptive Bias Layers'
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

# Adaptive Bias Layers
## Bias & Skala yang Dihasilkan dari Konteks: FiLM, AdaIN, adaLN, Attention Bias

### Minggu 0 — Deep Learning
**Sains Data ITERA · Ganjil 2026/2025**

---

# Capaian Pembelajaran & Agenda

> Mahasiswa mampu menjelaskan peran **bias** pada layer neural network, memahami bagaimana bias (dan skala) dapat **dihasilkan secara adaptif** dari input lain (kondisi), serta menghitung secara manual FiLM, AdaIN, dan bias posisi pada attention (ALiBi).

1. Catatan istilah: apa yang dimaksud "adaptive bias layer" di mata kuliah ini
2. Peran bias pada layer linear · bias yang redundan (BatchNorm)
3. **FiLM** — *Feature-wise Linear Modulation*
4. **Conditional BatchNorm** & **AdaIN**
5. **adaLN / adaLN-Zero** pada Diffusion Transformer
6. **Bias posisi pada attention**: relative position bias (T5) & **ALiBi**
7. Implementasi PyTorch · kesalahan umum · latihan

---

# Catatan Istilah

"**Adaptive Bias Layer**" **bukan** nama satu layer baku di literatur. Di mata kuliah ini istilah tersebut dipakai sebagai **payung** untuk layer yang:

> menambahkan **pergeseran (bias/shift)** — dan sering juga **skala** — yang **tidak tetap**, melainkan **dihitung dari input lain** (kondisi/konteks) atau dari **struktur input** (mis. jarak posisi).

| Layer biasa | Layer "adaptive bias" |
|---|---|
| $\mathbf{y} = W\mathbf{x} + \mathbf{b}$, $\mathbf{b}$ **konstan** setelah training | $\mathbf{y} = \boldsymbol{\gamma}(\mathbf{c}) \odot \mathbf{x} + \boldsymbol{\beta}(\mathbf{c})$, $\boldsymbol{\beta}$ **berubah** menurut kondisi $\mathbf{c}$ |
| Contoh: `nn.Linear`, `nn.Conv2d` | Contoh: FiLM, Conditional BN, AdaIN, adaLN, attention bias |

Nama-nama layer yang dibahas (FiLM, AdaIN, adaLN-Zero, ALiBi, dsb.) adalah nama resmi dari paper aslinya.

---

# Peran Bias pada Layer Linear

$$\mathbf{y} = W\mathbf{x} + \mathbf{b}$$

- Tanpa $\mathbf{b}$, hyperplane keputusan $W\mathbf{x} = 0$ **wajib melewati titik asal**.
- Bias menggeser fungsi aktivasi: neuron ReLU $\max(0, \mathbf{w}^\top\mathbf{x} + b)$ aktif ketika $\mathbf{w}^\top\mathbf{x} > -b$ → $b$ mengatur **ambang** aktivasi.

**Contoh**: $\mathbf{w} = [2, -1]$, $b = 0{,}5$, $\mathbf{x} = [1, 3]$
$$y = 2(1) + (-1)(3) + 0{,}5 = -0{,}5 \;\Rightarrow\; \text{ReLU}(y) = 0$$
Dengan $b = 1{,}5$: $y = 0{,}5$ → neuron **aktif**. Bias yang sama berlaku untuk semua input.

> Pertanyaan kunci topik ini: bagaimana jika **ambang/pergeseran** itu boleh berbeda untuk setiap **kondisi** (kelas, teks pertanyaan, gaya gambar, langkah waktu difusi)?

---

# Bias yang Redundan: Sebelum BatchNorm

Normalisasi mengurangi rata-rata → bias konstan **hilang**:
$$\text{BN}(z + b) = \frac{(z+b) - (\mu_z + b)}{\sigma_z} = \frac{z - \mu_z}{\sigma_z} = \text{BN}(z)$$

**Hitung manual**: $z = [1, 2, 3, 4]$ ($\mu = 2{,}5$, $\sigma = 1{,}118$)

| | $z$ | $z + 10$ |
|---|---|---|
| Setelah normalisasi | $[-1{,}342;\; -0{,}447;\; 0{,}447;\; 1{,}342]$ | $[-1{,}342;\; -0{,}447;\; 0{,}447;\; 1{,}342]$ |

- Karena itu `nn.Conv2d(..., bias=False)` lazim dipakai sebelum `nn.BatchNorm2d`.
- Pergeseran yang **bermakna** dipindahkan ke parameter **$\beta$** (dan skala ke **$\gamma$**) milik normalisasi: $\text{BN}(z) = \gamma\,\hat{z} + \beta$.
- Ide "adaptive bias": jadikan $\gamma$ dan $\beta$ ini **fungsi dari kondisi**.

---

# FiLM: Feature-wise Linear Modulation (Perez dkk., 2018)

Untuk feature map $F \in \mathbb{R}^{C \times H \times W}$ dan input kondisi $\mathbf{c}$ (mis. embedding pertanyaan):
$$\boldsymbol{\gamma} = f(\mathbf{c}),\quad \boldsymbol{\beta} = h(\mathbf{c}),\qquad \text{FiLM}(F_{k,h,w}) = \gamma_k\, F_{k,h,w} + \beta_k$$

- $\gamma_k, \beta_k$ **per channel** $k$, sama untuk semua posisi spasial.
- $f, h$ biasanya layer linear/MLP kecil → **FiLM generator**; jaringan yang dimodulasi → **FiLM-ed network**.
- Aplikasi asli: *visual question answering* (CLEVR) — pertanyaan teks "menyetel" jaringan CNN gambar.

| Efek nilai | Interpretasi |
|---|---|
| $\gamma_k = 0$ | Channel $k$ **dimatikan** (seperti gerbang) |
| $\gamma_k < 0$ | Channel $k$ **dibalik tandanya** |
| $\beta_k$ besar | Geser ambang ReLU berikutnya → channel lebih/kurang aktif |

---

<!-- _class: small -->

# Hitung Manual FiLM (1): Hasilkan $\gamma$ dan $\beta$

FiLM generator linear: $\boldsymbol{\gamma} = W_\gamma\mathbf{c} + \mathbf{b}_\gamma$, $\boldsymbol{\beta} = W_\beta\mathbf{c} + \mathbf{b}_\beta$ dengan
$$W_\gamma = \begin{bmatrix} 0{,}5 & -1 \\ 1 & 0{,}5 \end{bmatrix},\; \mathbf{b}_\gamma = \begin{bmatrix}1\\1\end{bmatrix},\qquad W_\beta = \begin{bmatrix} 1 & 0 \\ -1 & 2 \end{bmatrix},\; \mathbf{b}_\beta = \begin{bmatrix}0\\0\end{bmatrix}$$

| Kondisi | $\boldsymbol{\gamma} = W_\gamma\mathbf{c} + \mathbf{b}_\gamma$ | $\boldsymbol{\beta} = W_\beta\mathbf{c}$ |
|---|---|---|
| $\mathbf{c}_A = [1, 0]$ | $[0{,}5 + 1;\; 1 + 1] = [1{,}5;\; 2]$ | $[1;\; -1]$ |
| $\mathbf{c}_B = [0, 1]$ | $[-1 + 1;\; 0{,}5 + 1] = [0;\; 1{,}5]$ | $[0;\; 2]$ |

Feature map 2 channel, masing-masing $2 \times 2$:
$$F_1 = \begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix}, \qquad F_2 = \begin{bmatrix} -1 & 0 \\ 2 & 1 \end{bmatrix}$$

---

# Hitung Manual FiLM (2): Terapkan Modulasi

**Kondisi A** ($\gamma = [1{,}5;\, 2]$, $\beta = [1;\, -1]$):
$$1{,}5 \begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix} + 1 = \begin{bmatrix} 2{,}5 & 4 \\ 5{,}5 & 7 \end{bmatrix},\qquad 2\begin{bmatrix} -1 & 0 \\ 2 & 1 \end{bmatrix} - 1 = \begin{bmatrix} -3 & -1 \\ 3 & 1 \end{bmatrix}$$

**Kondisi B** ($\gamma = [0;\, 1{,}5]$, $\beta = [0;\, 2]$):
$$0 \cdot F_1 + 0 = \begin{bmatrix} 0 & 0 \\ 0 & 0 \end{bmatrix},\qquad 1{,}5\begin{bmatrix} -1 & 0 \\ 2 & 1 \end{bmatrix} + 2 = \begin{bmatrix} 0{,}5 & 2 \\ 5 & 3{,}5 \end{bmatrix}$$

> Feature map **sama**, kondisi **berbeda** → keluaran sangat berbeda. Pada kondisi B, channel 1 **dimatikan total** ($\gamma_1 = 0$). Inilah inti "bias/skala adaptif": jaringan yang sama berperilaku berbeda sesuai konteks.

Jumlah parameter generator di contoh: $W_\gamma, W_\beta$ ($2 \times 4$) + bias ($2 \times 2$) = **12**, bukan per-gambar.

---

# Conditional Batch Normalization (de Vries dkk., 2017)

Batch Normalization biasa: $\text{BN}(x) = \gamma\,\dfrac{x - \mu_B}{\sqrt{\sigma_B^2 + \epsilon}} + \beta$, dengan $\gamma, \beta$ **konstan** setelah training.

**Conditional BN** (CBN): kondisi $\mathbf{e}_q$ (embedding pertanyaan dari LSTM) memprediksi **perubahan**:
$$\hat{\gamma} = \gamma + \Delta\gamma(\mathbf{e}_q), \qquad \hat{\beta} = \beta + \Delta\beta(\mathbf{e}_q)$$

- $\Delta\gamma, \Delta\beta$ dihasilkan MLP kecil; $\gamma, \beta$ berasal dari ResNet **pretrained** yang dibekukan.
- Dengan inisialisasi $\Delta \approx 0$, jaringan mulai dari perilaku pretrained lalu belajar memodulasi.
- Dipakai juga pada GAN kondisional (bias & skala per kelas) — mis. BigGAN (Brock dkk., 2019).

FiLM dapat dipandang sebagai **generalisasi** CBN: modulasi $\gamma, \beta$ boleh diterapkan pada layer mana pun, tidak harus pada BN.

---

<!-- _class: small -->

# AdaIN: Adaptive Instance Normalization (Huang & Belongie, 2017)

Untuk *style transfer*: ganti statistik per channel konten $x$ dengan statistik gaya $y$:
$$\text{AdaIN}(x, y) = \sigma(y)\left(\frac{x - \mu(x)}{\sigma(x)}\right) + \mu(y)$$

- $\mu(\cdot), \sigma(\cdot)$ dihitung **per channel, per sampel** atas dimensi spasial.
- **Tidak ada parameter yang dipelajari**: skala = $\sigma(y)$, bias = $\mu(y)$ diambil langsung dari gambar gaya.

**Hitung manual** (satu channel, 4 piksel): konten $x = [1, 2, 3, 4]$, gaya $y = [10, 10, 14, 14]$

| Statistik | Konten | Gaya |
|---|---|---|
| $\mu$ | 2,5 | 12 |
| $\sigma$ | $\sqrt{1{,}25} = 1{,}118$ | 2 |

$$\text{AdaIN} = 2\cdot\frac{[1,2,3,4] - 2{,}5}{1{,}118} + 12 = [9{,}317;\; 11{,}106;\; 12{,}894;\; 14{,}683]$$

Hasil memiliki rata-rata **12** dan simpangan baku **2** (statistik gaya), tetapi **urutan/pola** nilai dari konten tetap terjaga.

---

# Dari AdaIN ke StyleGAN

**StyleGAN** (Karras dkk., 2019) memakai AdaIN sebagai mekanisme kendali:

1. *Mapping network* (MLP 8 layer) memetakan latent $\mathbf{z} \to \mathbf{w}$
2. Transformasi affine yang dipelajari: $\mathbf{w} \to (\mathbf{y}_s, \mathbf{y}_b)$ = **skala & bias per channel**
3. Di setiap resolusi: $\text{AdaIN}(\mathbf{x}_i, \mathbf{y}) = y_{s,i}\,\dfrac{x_i - \mu(x_i)}{\sigma(x_i)} + y_{b,i}$

- Skala & bias kini **dihasilkan** dari vektor gaya $\mathbf{w}$ — bentuk FiLM yang diterapkan setelah instance normalization.
- Pengaruh "gaya" pada resolusi rendah → pose/bentuk; resolusi tinggi → warna/tekstur.

---

# adaLN & adaLN-Zero pada Diffusion Transformer (Peebles & Xie, 2023)

Model difusi harus tahu **langkah waktu** $t$ dan **kelas** $y$. Pada **DiT**:

$$\mathbf{c} = \text{emb}(t) + \text{emb}(y) \;\xrightarrow{\text{MLP}}\; (\boldsymbol{\gamma}, \boldsymbol{\beta}, \boldsymbol{\alpha})$$

$$\text{adaLN}(\mathbf{h}) = \boldsymbol{\gamma} \odot \text{LayerNorm}(\mathbf{h}) + \boldsymbol{\beta}$$

**adaLN-Zero** menambahkan skala gerbang $\boldsymbol{\alpha}$ sebelum koneksi residual:
$$\mathbf{x} \leftarrow \mathbf{x} + \boldsymbol{\alpha} \odot \text{Block}(\text{adaLN}(\mathbf{x}))$$

- MLP diinisialisasi agar $\boldsymbol{\alpha} = \mathbf{0}$ → di awal training setiap blok = **fungsi identitas** ($\mathbf{x} + 0 = \mathbf{x}$), membuat training jaringan dalam lebih stabil.
- Peebles & Xie melaporkan adaLN-Zero memberi FID terbaik dibanding *in-context conditioning* dan *cross-attention* pada eksperimen mereka.

---

<!-- _class: divider -->

# Bias pada Attention

Bias yang bergantung pada posisi relatif token

---

# Bias Posisi pada Skor Attention

Skor attention standar: $s_{ij} = \dfrac{\mathbf{q}_i^\top\mathbf{k}_j}{\sqrt{d_k}}$. Dapat ditambah **bias yang bergantung jarak** $i - j$:
$$s_{ij} = \frac{\mathbf{q}_i^\top\mathbf{k}_j}{\sqrt{d_k}} + b_{\,i-j}, \qquad \alpha_{ij} = \text{softmax}_j(s_{ij})$$

| Metode | Bias $b_{i-j}$ | Dipelajari? |
|---|---|---|
| **Relative position representations** (Shaw dkk., 2018) | Vektor embedding jarak relatif ditambahkan ke key/value | Ya |
| **T5 relative position bias** (Raffel dkk., 2020) | Satu **skalar** per *bucket* jarak per head, ditambahkan ke logit | Ya |
| **ALiBi** (Press dkk., 2022) | $-m \cdot (i - j)$, $m$ = *slope* tetap per head | **Tidak** (slope tetap) |

- Bias ini **adaptif terhadap struktur input**: nilainya ditentukan oleh jarak antar-token, bukan konstan.
- Keuntungan: model tidak perlu *positional embedding* absolut; ALiBi dirancang agar **generalisasi ke sekuens lebih panjang** dari saat training (*train short, test long*).

---

# Hitung Manual ALiBi (1): Matriks Bias

ALiBi dengan causal mask, 4 token, slope $m = 0{,}5$: $b_{ij} = -m\,(i - j)$ untuk $j \le i$

$$B = \begin{bmatrix} 0 & -\infty & -\infty & -\infty \\ -0{,}5 & 0 & -\infty & -\infty \\ -1 & -0{,}5 & 0 & -\infty \\ -1{,}5 & -1 & -0{,}5 & 0 \end{bmatrix}$$

- Semakin jauh token yang dilihat, semakin besar **penalti** → *recency bias* yang halus.
- Slope per head membentuk deret geometri. Untuk 8 head: $m \in \left\{\tfrac{1}{2}, \tfrac{1}{4}, \tfrac{1}{8}, \ldots, \tfrac{1}{256}\right\}$ (Press dkk., 2022).
- Head dengan slope kecil (mis. $1/256$) hampir tidak dipenalti → dapat melihat konteks jauh; slope besar → fokus lokal.

---

<!-- _class: small -->

# Hitung Manual ALiBi (2): Pengaruh pada Bobot Attention

Ambil baris token ke-4 (query $i = 4$). Skor $\mathbf{q}_4^\top\mathbf{k}_j/\sqrt{d_k}$ = $[3{,}0;\; 0{,}0;\; 1{,}0;\; 1{,}0]$

| | $j=1$ | $j=2$ | $j=3$ | $j=4$ |
|---|---|---|---|---|
| Skor | 3,0 | 0,0 | 1,0 | 1,0 |
| Bias ALiBi ($m = 0{,}5$) | −1,5 | −1,0 | −0,5 | 0 |
| Skor + bias | 1,5 | −1,0 | 0,5 | 1,0 |
| softmax tanpa bias | **0,757** | 0,038 | 0,102 | 0,102 |
| softmax dengan bias | **0,486** | 0,040 | 0,179 | 0,295 |

Perhitungan softmax dengan bias: $e^{1{,}5} = 4{,}482$, $e^{-1} = 0{,}368$, $e^{0{,}5} = 1{,}649$, $e^{1} = 2{,}718$; jumlah = $9{,}217$ → $4{,}482/9{,}217 = 0{,}486$, dst.

> Bobot pada token jauh ($j=1$) **turun** dari 0,757 ke 0,486; token terdekat ($j=4$) naik dari 0,102 ke 0,295.

---

<!-- _class: small -->

# Implementasi PyTorch

```python
import torch, torch.nn as nn

class FiLM(nn.Module):
    """gamma, beta per channel dihasilkan dari vektor kondisi c."""
    def __init__(self, cond_dim, num_channels):
        super().__init__()
        self.to_gamma = nn.Linear(cond_dim, num_channels)
        self.to_beta  = nn.Linear(cond_dim, num_channels)
    def forward(self, F, c):                      # F: (N, C, H, W), c: (N, cond_dim)
        gamma = self.to_gamma(c)[:, :, None, None]
        beta  = self.to_beta(c)[:, :, None, None]
        return gamma * F + beta

film = FiLM(cond_dim=2, num_channels=2)
with torch.no_grad():                             # pakai bobot contoh slide
    film.to_gamma.weight.copy_(torch.tensor([[0.5, -1.], [1., 0.5]])); film.to_gamma.bias.fill_(1.)
    film.to_beta.weight.copy_(torch.tensor([[1., 0.], [-1., 2.]]));   film.to_beta.bias.zero_()
F = torch.tensor([[[[1., 2.], [3., 4.]], [[-1., 0.], [2., 1.]]]])
print(film(F, torch.tensor([[1., 0.]])))          # [[2.5,4],[5.5,7]] dan [[-3,-1],[3,1]]

def adain(x, y, eps=1e-5):                        # x, y: (N, C, H, W)
    mx, sx = x.mean((2, 3), keepdim=True), x.std((2, 3), keepdim=True, unbiased=False) + eps
    my, sy = y.mean((2, 3), keepdim=True), y.std((2, 3), keepdim=True, unbiased=False) + eps
    return sy * (x - mx) / sx + my

def alibi_bias(n, slope):                         # bias (n, n) untuk satu head, causal
    i = torch.arange(n)[:, None]; j = torch.arange(n)[None, :]
    return (-slope * (i - j)).float().masked_fill(j > i, float("-inf"))
```

---

# Kesalahan Umum

| Kesalahan | Akibat | Solusi |
|---|---|---|
| Bias `True` pada conv sebelum BN | Parameter mubazir (dihapus oleh normalisasi) | `bias=False` sebelum BN |
| Inisialisasi generator FiLM acak besar | $\gamma$ jauh dari 1 → aktivasi meledak/mati di awal training | Inisialisasi agar $\gamma \approx 1$, $\beta \approx 0$ (atau prediksi $\Delta\gamma$) |
| Lupa menambah sumbu spasial | *Broadcasting* salah: $(N, C)$ vs $(N, C, H, W)$ | `gamma[:, :, None, None]` |
| AdaIN memakai std **unbiased** vs **population** tidak konsisten | Nilai sedikit berbeda dari referensi | Tetapkan satu konvensi |
| Tanda bias ALiBi terbalik | Model justru memberi bobot lebih ke token jauh | Bias = $-m(i-j) \le 0$ |
| Menyamakan ALiBi dengan "bias yang dipelajari" | Salah konsep | Slope ALiBi **tetap**; bias T5 **dipelajari** |

---

# Latihan

1. Neuron ReLU dengan $\mathbf{w} = [1, 2]$ dan $\mathbf{x} = [-1, 0{,}5]$. Berapa nilai bias minimum agar neuron aktif ($> 0$)?
2. Tunjukkan secara numerik bahwa normalisasi (tanpa $\gamma,\beta$) dari $z = [2, 4, 6]$ dan $z + 5$ menghasilkan vektor yang sama.
3. Dengan FiLM generator pada slide, hitung $\boldsymbol{\gamma}, \boldsymbol{\beta}$ untuk $\mathbf{c} = [1, 1]$ dan keluaran FiLM untuk $F_1, F_2$ yang sama.
4. AdaIN: konten $x = [0, 2, 4, 6]$, gaya $y = [5, 5, 5, 9]$. Hitung keluarannya.
5. Tuliskan matriks bias ALiBi (causal) untuk 3 token dengan $m = 0{,}25$.
6. Mengapa adaLN-Zero menginisialisasi $\boldsymbol{\alpha} = 0$?

---

<!-- _class: small -->

# Kunci Jawaban

1. $\mathbf{w}^\top\mathbf{x} = -1 + 1 = 0$ → perlu $b > 0$ (bias positif sekecil apa pun)
2. $z$: $\mu = 4$, $\sigma = 1{,}633$ → $[-1{,}225;\; 0;\; 1{,}225]$; $z + 5 = [7, 9, 11]$: $\mu = 9$, $\sigma = 1{,}633$ → $[-1{,}225;\; 0;\; 1{,}225]$ ✓ sama
3. $\boldsymbol{\gamma} = [0{,}5 - 1 + 1;\; 1 + 0{,}5 + 1] = [0{,}5;\; 2{,}5]$, $\boldsymbol{\beta} = [1;\; -1 + 2] = [1;\; 1]$ → channel 1: $0{,}5F_1 + 1 = \begin{bmatrix}1{,}5 & 2\\ 2{,}5 & 3\end{bmatrix}$; channel 2: $2{,}5F_2 + 1 = \begin{bmatrix}-1{,}5 & 1\\ 6 & 3{,}5\end{bmatrix}$
4. $\mu(x) = 3$, $\sigma(x) = \sqrt{5} = 2{,}236$; $\mu(y) = 6$, $\sigma(y) = \sqrt{3} = 1{,}732$ → $1{,}732 \cdot \frac{[-3, -1, 1, 3]}{2{,}236} + 6 = [3{,}676;\; 5{,}225;\; 6{,}775;\; 8{,}324]$
5. $\begin{bmatrix} 0 & -\infty & -\infty \\ -0{,}25 & 0 & -\infty \\ -0{,}5 & -0{,}25 & 0 \end{bmatrix}$
6. Agar di awal training setiap blok bertindak sebagai **identitas** ($\mathbf{x} + 0 \cdot \text{Block} = \mathbf{x}$) → sinyal & gradien mengalir lancar lewat jalur residual; modulasi dipelajari bertahap

---

# Ringkasan

1. "Adaptive bias layer" = payung untuk layer dengan **pergeseran (dan skala) yang dihitung dari konteks**, bukan konstanta tetap.
2. Bias biasa menggeser ambang aktivasi; bias sebelum normalisasi **redundan** → peran pindah ke $\gamma, \beta$.
3. **FiLM**: $\gamma(\mathbf{c}) \odot F + \beta(\mathbf{c})$ per channel — kondisi "menyetel" jaringan.
4. **Conditional BN** memprediksi $\Delta\gamma, \Delta\beta$; **AdaIN** memakai $\sigma(y), \mu(y)$ gambar gaya tanpa parameter.
5. **adaLN-Zero** (DiT): $\gamma, \beta, \alpha$ dari timestep + kelas; $\alpha = 0$ di awal → blok identitas.
6. **Bias posisi attention**: T5 (skalar dipelajari per bucket) dan **ALiBi** (penalti linear $-m(i-j)$, slope tetap).

---

<!-- _class: small -->

# Referensi

1. Perez, E., Strub, F., de Vries, H., Dumoulin, V., & Courville, A. (2018). FiLM: Visual reasoning with a general conditioning layer. *AAAI*.
2. de Vries, H., Strub, F., Mary, J., Larochelle, H., Pietquin, O., & Courville, A. (2017). Modulating early visual processing by language. *NeurIPS*.
3. Huang, X., & Belongie, S. (2017). Arbitrary style transfer in real-time with adaptive instance normalization. *ICCV*.
4. Karras, T., Laine, S., & Aila, T. (2019). A style-based generator architecture for generative adversarial networks. *CVPR*.
5. Peebles, W., & Xie, S. (2023). Scalable diffusion models with transformers. *ICCV*.
6. Brock, A., Donahue, J., & Simonyan, K. (2019). Large scale GAN training for high fidelity natural image synthesis. *ICLR*.
7. Ioffe, S., & Szegedy, C. (2015). Batch normalization: Accelerating deep network training by reducing internal covariate shift. *ICML*.
8. Shaw, P., Uszkoreit, J., & Vaswani, A. (2018). Self-attention with relative position representations. *NAACL*.
9. Raffel, C., dkk. (2020). Exploring the limits of transfer learning with a unified text-to-text transformer. *Journal of Machine Learning Research*, 21(140).
10. Press, O., Smith, N. A., & Lewis, M. (2022). Train short, test long: Attention with linear biases enables input length extrapolation. *ICLR*.
11. Dumoulin, V., dkk. (2018). Feature-wise transformations. *Distill*. https://distill.pub/2018/feature-wise-transformations
12. Prince, S. J. D. (2023). *Understanding Deep Learning*. MIT Press.

---

<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _header: '' -->

# Terima Kasih

### Topik berikutnya: **Pooling Layers**
