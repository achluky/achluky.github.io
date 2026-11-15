---
marp: true
theme: default
paginate: true
size: 16:9
math: mathjax
header: 'Building Blocks of Deep Learning · Recurrent Layers'
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

# Recurrent Layers
## RNN · BPTT · LSTM · GRU

### Minggu 0 — Deep Learning: Building Blocks
**Sains Data ITERA · Ganjil 2026/2025**

---

# Capaian Pembelajaran & Agenda

> Mahasiswa mampu menjelaskan cara kerja *recurrent layer*, menghitung secara manual *forward pass* RNN, LSTM, dan GRU, serta menjelaskan masalah *vanishing/exploding gradient* pada BPTT.

1. Motivasi: data sekuensial & keterbatasan layer *feed-forward*
2. **Vanilla RNN** — definisi, *unrolling*, *parameter sharing*
3. Hitung manual *forward pass* 3 langkah waktu
4. **Backpropagation Through Time** & *vanishing/exploding gradient*
5. *Gradient clipping*
6. **LSTM** & **GRU** — persamaan dan hitung manual satu langkah
7. Varian: *bidirectional*, *stacked*, pola input–output
8. PyTorch: bentuk tensor & jumlah parameter
9. RNN vs *attention*/Transformer · latihan

---

# Motivasi: Data Sekuensial

| Data | Urutan elemen | Contoh tugas |
|---|---|---|
| Teks | kata / token | analisis sentimen, terjemahan |
| Suara | frame sinyal | pengenalan ucapan |
| Deret waktu | nilai per waktu | prakiraan cuaca, harga, beban listrik |
| Sensor | pembacaan per detik | deteksi aktivitas manusia |
| Video | frame | klasifikasi aksi |

Kebutuhan:
1. **Panjang input bervariasi** — kalimat 5 kata vs 50 kata.
2. **Urutan bermakna** — "anjing menggigit orang" ≠ "orang menggigit anjing".
3. **Bobot yang sama** untuk pola yang sama di posisi berbeda.

> Layer linear biasa (MLP) menerima vektor berukuran **tetap** dan tidak memiliki "memori" urutan. *Recurrent layer* menambahkan **state tersembunyi** $h_t$ yang dibawa dari langkah ke langkah (Elman, 1990).

---

# Vanilla RNN: Definisi

Untuk input $x_1, x_2, \ldots, x_T$ dengan $x_t \in \mathbb{R}^{d}$ dan state $h_t \in \mathbb{R}^{H}$:

$$h_t = \tanh\left(W_{xh}\,x_t + W_{hh}\,h_{t-1} + b_h\right), \qquad h_0 = \mathbf{0}$$
$$\hat{y}_t = W_{hy}\,h_t + b_y$$

| Simbol | Ukuran | Arti |
|---|---|---|
| $W_{xh}$ | $H \times d$ | bobot input → state |
| $W_{hh}$ | $H \times H$ | bobot state lama → state baru (**rekurensi**) |
| $b_h$ | $H$ | bias |
| $W_{hy}$, $b_y$ | $q \times H$, $q$ | layer output |

- **Parameter sharing**: $W_{xh}, W_{hh}, b_h$ **sama** untuk semua $t$ → jumlah parameter tidak bergantung pada panjang $T$.
- $h_t$ adalah **ringkasan** seluruh riwayat $x_1, \ldots, x_t$.

---

# Unrolling: RNN = Jaringan Dalam dengan Bobot Bersama

| | $t = 1$ | $t = 2$ | $t = 3$ |
|---|---|---|---|
| Input | $x_1$ | $x_2$ | $x_3$ |
| State | $h_1 = \tanh(W_{xh}x_1 + W_{hh}h_0 + b)$ | $h_2 = \tanh(W_{xh}x_2 + W_{hh}h_1 + b)$ | $h_3 = \tanh(W_{xh}x_3 + W_{hh}h_2 + b)$ |
| Output | $\hat{y}_1$ | $\hat{y}_2$ | $\hat{y}_3$ |

$$h_0 \xrightarrow{W_{hh}} h_1 \xrightarrow{W_{hh}} h_2 \xrightarrow{W_{hh}} h_3$$

- Setelah di-*unroll*, RNN dengan $T$ langkah = jaringan *feed-forward* sedalam $T$ layer yang **berbagi bobot**.
- Konsekuensi: gradien harus melewati $T$ perkalian dengan $W_{hh}$ → sumber masalah *vanishing/exploding gradient* (Bengio, Simard & Frasconi, 1994).

---

<!-- _class: divider -->

# Hitung Manual: Forward Pass RNN

---

# Soal: RNN dengan $d = 1$, $H = 2$

Barisan input $x = (1{,}0;\; 0{,}5;\; -1{,}0)$, $h_0 = (0, 0)^\top$.

$$W_{xh} = \begin{bmatrix} 0{,}5 \\ -0{,}3 \end{bmatrix}, \quad
W_{hh} = \begin{bmatrix} 0{,}1 & 0{,}2 \\ -0{,}1 & 0{,}3 \end{bmatrix}, \quad
b_h = \begin{bmatrix} 0 \\ 0{,}1 \end{bmatrix}, \quad
W_{hy} = \begin{bmatrix} 1 & -1 \end{bmatrix}, \; b_y = 0$$

Tugas *many-to-one*: hitung $h_1, h_2, h_3$ dan output akhir $\hat{y} = W_{hy}h_3$.

Langkah setiap $t$:
1. $W_{xh}x_t$
2. $W_{hh}h_{t-1}$
3. $a_t = W_{xh}x_t + W_{hh}h_{t-1} + b_h$
4. $h_t = \tanh(a_t)$ (elemen per elemen)

---

<!-- _class: small -->

# Langkah $t = 1$ dan $t = 2$

**$t = 1$**, $x_1 = 1$, $h_0 = 0$:

$$W_{xh}x_1 = \begin{bmatrix} 0{,}5 \\ -0{,}3 \end{bmatrix}, \;\; W_{hh}h_0 = \begin{bmatrix} 0 \\ 0 \end{bmatrix}, \;\; a_1 = \begin{bmatrix} 0{,}5 \\ -0{,}2 \end{bmatrix}, \;\; h_1 = \tanh(a_1) = \begin{bmatrix} 0{,}4621 \\ -0{,}1974 \end{bmatrix}$$

**$t = 2$**, $x_2 = 0{,}5$:

$$W_{xh}x_2 = \begin{bmatrix} 0{,}25 \\ -0{,}15 \end{bmatrix}$$

$$W_{hh}h_1 = \begin{bmatrix} 0{,}1(0{,}4621) + 0{,}2(-0{,}1974) \\ -0{,}1(0{,}4621) + 0{,}3(-0{,}1974) \end{bmatrix} = \begin{bmatrix} 0{,}0462 - 0{,}0395 \\ -0{,}0462 - 0{,}0592 \end{bmatrix} = \begin{bmatrix} 0{,}0067 \\ -0{,}1054 \end{bmatrix}$$

$$a_2 = \begin{bmatrix} 0{,}25 + 0{,}0067 + 0 \\ -0{,}15 - 0{,}1054 + 0{,}1 \end{bmatrix} = \begin{bmatrix} 0{,}2567 \\ -0{,}1554 \end{bmatrix}, \qquad h_2 = \begin{bmatrix} 0{,}2512 \\ -0{,}1542 \end{bmatrix}$$

---

<!-- _class: small -->

# Langkah $t = 3$ dan Output

**$t = 3$**, $x_3 = -1$:

$$W_{xh}x_3 = \begin{bmatrix} -0{,}5 \\ 0{,}3 \end{bmatrix}, \quad
W_{hh}h_2 = \begin{bmatrix} 0{,}1(0{,}2512) + 0{,}2(-0{,}1542) \\ -0{,}1(0{,}2512) + 0{,}3(-0{,}1542) \end{bmatrix} = \begin{bmatrix} -0{,}0057 \\ -0{,}0714 \end{bmatrix}$$

$$a_3 = \begin{bmatrix} -0{,}5 - 0{,}0057 \\ 0{,}3 - 0{,}0714 + 0{,}1 \end{bmatrix} = \begin{bmatrix} -0{,}5057 \\ 0{,}3286 \end{bmatrix}, \qquad h_3 = \begin{bmatrix} -0{,}4666 \\ 0{,}3173 \end{bmatrix}$$

**Output**: $\hat{y} = W_{hy}h_3 = 1(-0{,}4666) - 1(0{,}3173) = \mathbf{-0{,}7839}$

| $t$ | $x_t$ | $a_t$ | $h_t$ |
|---|---|---|---|
| 1 | 1,0 | (0,5000; −0,2000) | (0,4621; −0,1974) |
| 2 | 0,5 | (0,2567; −0,1554) | (0,2512; −0,1542) |
| 3 | −1,0 | (−0,5057; 0,3286) | (−0,4666; 0,3173) |

> Perhatikan $h_2$ bergantung pada $x_1$ melalui $h_1$: inilah **memori** RNN.

---

<!-- _class: divider -->

# Backpropagation Through Time (BPTT)

---

# BPTT: Gradien Mengalir Mundur Melalui Waktu

Loss total $\mathcal{L} = \sum_t \ell_t(\hat{y}_t, y_t)$. Karena $W_{hh}$ dipakai di semua langkah:

$$\frac{\partial \mathcal{L}}{\partial W_{hh}} = \sum_{t=1}^{T} \frac{\partial \mathcal{L}}{\partial h_t}\,\frac{\partial h_t}{\partial W_{hh}}\Big|_{\text{lokal}}$$

Gradien dari langkah $T$ ke langkah $k$ memuat **perkalian Jacobian**:

$$\frac{\partial h_T}{\partial h_k} = \prod_{t=k+1}^{T} \frac{\partial h_t}{\partial h_{t-1}} = \prod_{t=k+1}^{T} \text{diag}\!\left(1 - h_t^2\right) W_{hh}$$

- Jika norma tiap faktor **< 1** → hasil kali menuju 0: **vanishing gradient** (dependensi jangka panjang tidak terpelajari).
- Jika norma tiap faktor **> 1** → hasil kali meledak: **exploding gradient** (training tidak stabil, NaN).

Analisis: Bengio, Simard & Frasconi (1994); Pascanu, Mikolov & Bengio (2013).

---

<!-- _class: small -->

# Hitung Manual: Perkalian Faktor pada RNN Skalar

RNN skalar $h_t = \tanh(w\,h_{t-1} + 0{,}1)$, $h_0 = 0$. Faktor tiap langkah: $\dfrac{\partial h_t}{\partial h_{t-1}} = w\,(1 - h_t^2)$.

| $t$ | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | $\prod$ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| $w = 0{,}5$ | 0,495 | 0,489 | 0,485 | 0,483 | 0,482 | 0,482 | 0,481 | 0,481 | 0,481 | 0,481 | **0,0007** |
| $w = 1{,}5$ | 1,485 | 1,410 | 1,216 | 0,891 | 0,578 | 0,402 | 0,334 | 0,312 | 0,305 | 0,303 | **0,0051** |

Batas atas kasar (faktor konstan) untuk $T = 20$ langkah:

$$0{,}5^{20} \approx 9{,}5 \times 10^{-7} \qquad\qquad 1{,}5^{20} \approx 3325$$

**Pengamatan**
- $w = 0{,}5$: setiap langkah mengalikan gradien dengan ≈ 0,48 → setelah 10 langkah tinggal 0,07%.
- $w = 1{,}5$: awalnya faktor > 1 (gradien membesar), tetapi $h_t$ lalu **saturasi** (mendekati 1) sehingga $1 - h_t^2$ kecil → tetap mengecil. Dengan tanh, *vanishing* lebih sering terjadi daripada *exploding*.
- *Exploding* terjadi bila faktor > 1 bertahan, mis. aktivasi kecil dengan $\lVert W_{hh}\rVert$ besar, atau RNN linear ($h_t = w h_{t-1}$, $w > 1$).

---

# Gradient Clipping (Pascanu dkk., 2013)

Solusi sederhana untuk *exploding gradient*: jika norma gradien melebihi ambang $\tau$, skalakan ulang:

$$g \leftarrow \begin{cases} g & \lVert g\rVert \le \tau \\[4pt] \dfrac{\tau}{\lVert g\rVert}\, g & \lVert g\rVert > \tau \end{cases}$$

**Hitung manual**: $g = (3, 4)$, $\tau = 1$.
$$\lVert g\rVert = \sqrt{3^2 + 4^2} = 5 > 1 \;\Rightarrow\; g \leftarrow \frac{1}{5}(3, 4) = (0{,}6;\; 0{,}8)$$

Arah gradien **tetap**, hanya panjang langkahnya yang dibatasi.

```python
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)  # setelah loss.backward()
```

> *Clipping* mengatasi *exploding*, tetapi **tidak** mengatasi *vanishing*. Untuk itu dibutuhkan arsitektur ber-*gate*: **LSTM** dan **GRU**.

---

<!-- _class: divider -->

# LSTM & GRU

Arsitektur ber-*gate* untuk dependensi jangka panjang

---

# LSTM (Hochreiter & Schmidhuber, 1997; *forget gate*: Gers dkk., 2000)

State terdiri dari **cell state** $c_t$ (memori jangka panjang) dan **hidden state** $h_t$:

$$\begin{aligned}
f_t &= \sigma(W_f x_t + U_f h_{t-1} + b_f) && \text{forget gate}\\
i_t &= \sigma(W_i x_t + U_i h_{t-1} + b_i) && \text{input gate}\\
o_t &= \sigma(W_o x_t + U_o h_{t-1} + b_o) && \text{output gate}\\
g_t &= \tanh(W_g x_t + U_g h_{t-1} + b_g) && \text{kandidat memori}\\
c_t &= f_t \odot c_{t-1} + i_t \odot g_t && \text{update memori (aditif!)}\\
h_t &= o_t \odot \tanh(c_t)
\end{aligned}$$

**Mengapa mengatasi vanishing?** $\dfrac{\partial c_t}{\partial c_{t-1}} = f_t$ (lewat jalur langsung). Jika $f_t \approx 1$, gradien mengalir hampir tanpa peluruhan sepanjang banyak langkah — jalur ini dikenal sebagai *constant error carousel*.

---

<!-- _class: small -->

# Hitung Manual: Satu Langkah LSTM (skalar)

Diketahui $x_t = 1$, $h_{t-1} = 0{,}5$, $c_{t-1} = 1$, semua bias 0.

| Gate | $W$ | $U$ | Pra-aktivasi $Wx + Uh$ | Aktivasi |
|---|---|---|---|---|
| $f$ | 0,5 | 0,4 | 0,5 + 0,2 = 0,70 | $\sigma(0{,}70) = 0{,}6682$ |
| $i$ | 0,6 | −0,2 | 0,6 − 0,1 = 0,50 | $\sigma(0{,}50) = 0{,}6225$ |
| $o$ | −0,3 | 0,8 | −0,3 + 0,4 = 0,10 | $\sigma(0{,}10) = 0{,}5250$ |
| $g$ | 1,0 | 0,5 | 1,0 + 0,25 = 1,25 | $\tanh(1{,}25) = 0{,}8483$ |

$$c_t = f\,c_{t-1} + i\,g = 0{,}6682(1) + 0{,}6225(0{,}8483) = 0{,}6682 + 0{,}5280 = \mathbf{1{,}1962}$$
$$h_t = o\,\tanh(c_t) = 0{,}5250 \times \tanh(1{,}1962) = 0{,}5250 \times 0{,}8325 = \mathbf{0{,}4370}$$

**Interpretasi**: 67% memori lama dipertahankan ($f$), 62% kandidat baru ditambahkan ($i$), dan 52% isi memori dikeluarkan sebagai $h_t$ ($o$).

---

# GRU (Cho dkk., 2014)

Versi ringkas: **2 gate**, tanpa cell state terpisah.

$$\begin{aligned}
r_t &= \sigma(W_r x_t + U_r h_{t-1} + b_r) && \text{reset gate}\\
z_t &= \sigma(W_z x_t + U_z h_{t-1} + b_z) && \text{update gate}\\
\tilde{h}_t &= \tanh\!\left(W_h x_t + r_t \odot (U_h h_{t-1}) + b_h\right) && \text{kandidat}\\
h_t &= (1 - z_t) \odot \tilde{h}_t + z_t \odot h_{t-1}
\end{aligned}$$

- $z_t \approx 1$ → state lama **disalin** (memori panjang); $z_t \approx 0$ → diganti kandidat baru.
- $r_t \approx 0$ → kandidat "melupakan" state lama (cocok saat awal frasa baru).
- Rumus kandidat di atas mengikuti implementasi PyTorch ($r_t$ dikalikan **setelah** $U_h h_{t-1}$); makalah Cho dkk. menulis $U_h(r_t \odot h_{t-1})$. Keduanya setara untuk kasus skalar tanpa bias.

| | Vanilla RNN | GRU | LSTM |
|---|---|---|---|
| Gate | 0 | 2 | 3 |
| State | $h$ | $h$ | $h, c$ |
| Parameter (relatif) | 1× | 3× | 4× |

---

<!-- _class: small -->

# Hitung Manual: Satu Langkah GRU (skalar)

Diketahui $x_t = 1$, $h_{t-1} = 0{,}5$, bias 0; $W_r = 0{,}5$, $U_r = 0{,}5$; $W_z = -0{,}4$, $U_z = 0{,}6$; $W_h = 1{,}0$, $U_h = 0{,}8$.

| Langkah | Perhitungan | Hasil |
|---|---|---|
| Reset | $r = \sigma(0{,}5 \cdot 1 + 0{,}5 \cdot 0{,}5) = \sigma(0{,}75)$ | 0,6792 |
| Update | $z = \sigma(-0{,}4 \cdot 1 + 0{,}6 \cdot 0{,}5) = \sigma(-0{,}10)$ | 0,4750 |
| Kandidat | $\tilde{h} = \tanh(1{,}0 \cdot 1 + 0{,}6792 \times 0{,}8 \times 0{,}5) = \tanh(1{,}2717)$ | 0,8543 |
| State baru | $h_t = (1 - 0{,}4750)(0{,}8543) + 0{,}4750(0{,}5)$ | **0,6860** |

Rincian baris terakhir: $0{,}5250 \times 0{,}8543 = 0{,}4485$ dan $0{,}4750 \times 0{,}5 = 0{,}2375$; jumlah $= 0{,}6860$.

> $h_t$ merupakan **interpolasi** antara state lama (0,5) dan kandidat (0,8543) dengan bobot $z_t$. Interpolasi ini membuat $\partial h_t / \partial h_{t-1}$ memiliki komponen $z_t$ secara langsung, sehingga gradien tidak mudah hilang.

---

<!-- _class: divider -->

# Varian & Implementasi

---

# Pola Input–Output & Varian Arsitektur

| Pola | Input → Output | Contoh |
|---|---|---|
| **Many-to-one** | barisan → satu label (pakai $h_T$) | klasifikasi sentimen |
| **One-to-many** | satu vektor → barisan | *image captioning* |
| **Many-to-many (sinkron)** | output di setiap $t$ | POS tagging, NER |
| **Many-to-many (encoder–decoder)** | barisan → barisan beda panjang | terjemahan mesin (Cho dkk., 2014) |

**Bidirectional RNN** (Schuster & Paliwal, 1997): dua RNN, maju ($\overrightarrow{h}_t$) dan mundur ($\overleftarrow{h}_t$); output $[\overrightarrow{h}_t; \overleftarrow{h}_t]$ berukuran $2H$. Cocok saat seluruh barisan tersedia (NER), **tidak** untuk prediksi *real-time*.

**Stacked (deep) RNN**: output $h_t^{(l)}$ layer $l$ menjadi input layer $l+1$. Umumnya 2–4 layer; *dropout* antar-layer.

---

<!-- _class: small -->

# PyTorch: Bentuk Tensor (verifikasi hitung manual)

```python
import torch, torch.nn as nn

rnn = nn.RNN(input_size=1, hidden_size=2, batch_first=True)   # default batch_first=False
with torch.no_grad():
    rnn.weight_ih_l0.copy_(torch.tensor([[0.5], [-0.3]]))
    rnn.weight_hh_l0.copy_(torch.tensor([[0.1, 0.2], [-0.1, 0.3]]))
    rnn.bias_ih_l0.copy_(torch.tensor([0.0, 0.1]))
    rnn.bias_hh_l0.zero_()                         # PyTorch memakai DUA bias: b_ih + b_hh

x = torch.tensor([[[1.0], [0.5], [-1.0]]])         # (N=1, L=3, H_in=1) karena batch_first=True
out, h_n = rnn(x)
print(out.shape, h_n.shape)    # torch.Size([1, 3, 2]) torch.Size([1, 1, 2])
print(h_n)                     # ≈ [[[-0.4666, 0.3173]]]  -> sama dengan h_3 hitung manual
```

| Argumen / output | Bentuk (`batch_first=False`) |
|---|---|
| input | $(L, N, H_{in})$ |
| output | $(L, N, D \cdot H_{out})$, $D = 2$ jika bidirectional |
| `h_n` | $(D \cdot \text{num\_layers}, N, H_{out})$ |
| LSTM | mengembalikan `output, (h_n, c_n)` |

Urutan blok bobot: LSTM `(i, f, g, o)`, GRU `(r, z, n)`.

---

# Jumlah Parameter

Per layer, input berdimensi $d$, hidden $H$ (PyTorch memakai dua vektor bias):

$$\text{RNN} = H d + H^2 + 2H, \qquad \text{GRU} = 3 \times \text{RNN}, \qquad \text{LSTM} = 4 \times \text{RNN}$$

**Contoh** $d = 10$, $H = 20$:

| Layer | Perhitungan | Parameter |
|---|---|---|
| `nn.RNN` | $20 \cdot 10 + 20^2 + 2 \cdot 20 = 200 + 400 + 40$ | **640** |
| `nn.GRU` | $3 \times 640$ | **1.920** |
| `nn.LSTM` | $4 \times 640$ | **2.560** |

> Parameter **tidak** bergantung pada panjang barisan $T$ — konsekuensi langsung dari *parameter sharing*.

---

# RNN vs Attention / Transformer

| Aspek | RNN / LSTM / GRU | Self-attention (Transformer) |
|---|---|---|
| Pemrosesan | **Berurutan** ($h_t$ menunggu $h_{t-1}$) | **Paralel** di semua posisi |
| Jarak dependensi | Gradien melewati $O(T)$ langkah | Setiap posisi terhubung langsung, $O(1)$ langkah |
| Biaya per layer | $O(T \cdot H^2)$ | $O(T^2 \cdot H)$ |
| Memori saat inferensi | State konstan $O(H)$ | KV-cache tumbuh $O(T)$ |
| Cocok untuk | Streaming, perangkat kecil, deret waktu pendek | Teks panjang, data besar, pra-latih |

> Transformer menggantikan RNN di sebagian besar NLP, tetapi gagasan **state rekuren** kembali hidup pada model modern berbasis *state space* dan RNN linear yang dapat dilatih paralel. Prinsip *gating* dari LSTM/GRU juga dipakai luas (lihat materi *Multiplicative Layers*).

---

<!-- _class: small -->

# Kesalahan Umum

| Kesalahan | Akibat | Solusi |
|---|---|---|
| Lupa `batch_first=True` padahal data `(N, L, d)` | Dimensi waktu dan batch tertukar, tanpa error | Periksa bentuk tensor; konsisten |
| Tidak me-reset $h_0$ antar-barisan independen | Informasi bocor antar-sampel | Biarkan `h0=None` (nol) atau `detach()` pada *truncated BPTT* |
| Barisan beda panjang dengan *padding* nol tanpa masking | State terkontaminasi token *pad* | `pack_padded_sequence` |
| Tidak memakai *gradient clipping* | Loss melonjak / NaN | `clip_grad_norm_` (mis. 1,0–5,0) |
| Memakai output $t$ terakhir pada barisan ber-*padding* | Mengambil state setelah *padding* | Ambil `h_n` dari sequence yang di-*pack* |
| Bidirectional untuk prediksi masa depan | *Data leakage* dari masa depan | Gunakan RNN satu arah |

---

# Latihan

1. RNN skalar $h_t = \tanh(0{,}8\,h_{t-1} + 0{,}5\,x_t)$, $h_0 = 0$, $x = (1, -1)$. Hitung $h_1$ dan $h_2$.
2. Untuk soal 1, hitung $\dfrac{\partial h_2}{\partial h_1}$.
3. LSTM skalar dengan $f = 0{,}9$, $i = 0{,}2$, $g = -0{,}5$, $o = 0{,}7$, $c_{t-1} = 2$. Hitung $c_t$ dan $h_t$.
4. GRU skalar dengan $z = 0{,}8$, $\tilde{h} = -0{,}6$, $h_{t-1} = 0{,}4$. Hitung $h_t$.
5. Gradien $g = (6, -8)$ dengan $\tau = 5$. Hitung gradien setelah *clipping*.
6. Hitung jumlah parameter `nn.LSTM(input_size=8, hidden_size=16)`.

---

<!-- _class: small -->

# Kunci Jawaban

1. $h_1 = \tanh(0 + 0{,}5) = \mathbf{0{,}4621}$; $h_2 = \tanh(0{,}8 \times 0{,}4621 - 0{,}5) = \tanh(-0{,}1303) = \mathbf{-0{,}1296}$
2. $\dfrac{\partial h_2}{\partial h_1} = 0{,}8\,(1 - h_2^2) = 0{,}8\,(1 - 0{,}0168) = \mathbf{0{,}7866}$
3. $c_t = 0{,}9 \times 2 + 0{,}2 \times (-0{,}5) = 1{,}8 - 0{,}1 = \mathbf{1{,}7}$; $h_t = 0{,}7 \tanh(1{,}7) = 0{,}7 \times 0{,}9354 = \mathbf{0{,}6548}$
4. $h_t = (1 - 0{,}8)(-0{,}6) + 0{,}8(0{,}4) = -0{,}12 + 0{,}32 = \mathbf{0{,}20}$
5. $\lVert g\rVert = 10 > 5$ → $g \leftarrow \tfrac{5}{10}(6, -8) = \mathbf{(3, -4)}$
6. RNN dasar $= 16 \cdot 8 + 16^2 + 2 \cdot 16 = 128 + 256 + 32 = 416$; LSTM $= 4 \times 416 = \mathbf{1.664}$

---

# Ringkasan

1. *Recurrent layer* memproses barisan dengan **state tersembunyi** $h_t = \tanh(W_{xh}x_t + W_{hh}h_{t-1} + b)$ dan **bobot bersama** di semua langkah.
2. *Unrolling* mengubah RNN menjadi jaringan dalam; **BPTT** mengalikan Jacobian sepanjang waktu → **vanishing/exploding gradient**.
3. **Gradient clipping** mengatasi *exploding*; **LSTM** (cell state aditif + 3 gate) dan **GRU** (2 gate, interpolasi) mengatasi *vanishing*.
4. Varian: *bidirectional*, *stacked*, *encoder–decoder*.
5. PyTorch: perhatikan `batch_first`, dua bias, dan urutan blok bobot gate.
6. Transformer unggul untuk paralelisme dan dependensi jauh; RNN tetap relevan untuk *streaming* dan memori konstan.

---

<!-- _class: small -->

# Referensi

1. Elman, J. L. (1990). Finding structure in time. *Cognitive Science*, 14(2), 179–211.
2. Bengio, Y., Simard, P., & Frasconi, P. (1994). Learning long-term dependencies with gradient descent is difficult. *IEEE Transactions on Neural Networks*, 5(2), 157–166.
3. Hochreiter, S., & Schmidhuber, J. (1997). Long short-term memory. *Neural Computation*, 9(8), 1735–1780.
4. Schuster, M., & Paliwal, K. K. (1997). Bidirectional recurrent neural networks. *IEEE Transactions on Signal Processing*, 45(11), 2673–2681.
5. Gers, F. A., Schmidhuber, J., & Cummins, F. (2000). Learning to forget: Continual prediction with LSTM. *Neural Computation*, 12(10), 2451–2471.
6. Pascanu, R., Mikolov, T., & Bengio, Y. (2013). On the difficulty of training recurrent neural networks. *ICML*.
7. Cho, K., dkk. (2014). Learning phrase representations using RNN encoder–decoder for statistical machine translation. *EMNLP*.
8. Goodfellow, I., Bengio, Y., & Courville, A. (2016). *Deep Learning*, Bab 10: Sequence Modeling. MIT Press.
9. Zhang, A., Lipton, Z. C., Li, M., & Smola, A. J. (2023). *Dive into Deep Learning*, Bab 9–10. Cambridge University Press. https://d2l.ai
10. Dokumentasi PyTorch: `torch.nn.RNN`, `torch.nn.LSTM`, `torch.nn.GRU`. https://pytorch.org/docs/stable/nn.html

---

<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _header: '' -->

# Terima Kasih

### Berikutnya: **Multiplicative Layers**

Kerjakan latihan hitung manual, lalu verifikasi dengan `torch.nn.RNN`, `LSTM`, dan `GRU`
