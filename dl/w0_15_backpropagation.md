---
marp: true
theme: default
paginate: true
size: 16:9
math: mathjax
header: 'Building Blocks of Deep Learning · Backpropagation'
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

# Backpropagation
## Chain Rule · Computational Graph · Hitung Manual Langkah demi Langkah

### Minggu 0 — Deep Learning
**Sains Data ITERA · Ganjil 2026/2025**

---

# Capaian Pembelajaran & Agenda

> Mahasiswa mampu menurunkan dan menghitung secara manual gradien seluruh parameter jaringan saraf dengan **backpropagation**, memverifikasinya dengan *gradient check*, dan memahami cara kerja **autograd** di PyTorch.

1. Mengapa butuh backpropagation?
2. **Chain rule** & **computational graph**
3. Forward mode vs **reverse mode** differentiation
4. **Hitung manual** jaringan 2–2–1: forward, backward, update
5. Verifikasi: *finite-difference gradient check*
6. Bentuk matriks & kompleksitas
7. Vanishing / exploding gradient
8. Autograd PyTorch · jebakan umum · latihan

---

# Mengapa Butuh Backpropagation?

Gradient descent memerlukan $\nabla_\theta L$ untuk **semua** parameter: $\theta \leftarrow \theta - \eta \nabla_\theta L$.

| Cara menghitung gradien | Biaya untuk $p$ parameter | Masalah |
|---|---|---|
| Turunan simbolik manual | — | Tidak praktis untuk jutaan parameter |
| *Finite difference* $\frac{L(\theta + \epsilon e_j) - L(\theta - \epsilon e_j)}{2\epsilon}$ | $2p$ kali forward | GPT/ResNet: jutaan forward per langkah; galat numerik |
| **Backpropagation** (reverse-mode AD) | ≈ **1 forward + 1 backward** | Perlu menyimpan aktivasi (memori) |

**Backpropagation** = penerapan **chain rule** secara sistematis dari output ke input, menggunakan ulang hasil antara (*dynamic programming*). Dipopulerkan untuk neural network oleh Rumelhart, Hinton & Williams (1986).

> Backpropagation **hanya menghitung gradien**. Pembaruan parameter dilakukan oleh **optimizer** (SGD, Adam, ...).

---

# Chain Rule

Untuk fungsi komposisi $L = f(g(x))$:
$$\frac{dL}{dx} = \frac{dL}{dg}\cdot\frac{dg}{dx}$$

Jika satu variabel memengaruhi output melalui **beberapa jalur**, kontribusinya **dijumlahkan**:
$$z = f(u, v),\; u = u(x),\; v = v(x) \;\Rightarrow\; \frac{\partial z}{\partial x} = \frac{\partial z}{\partial u}\frac{\partial u}{\partial x} + \frac{\partial z}{\partial v}\frac{\partial v}{\partial x}$$

Notasi umum: **gradien hulu** (*upstream*) $\bar{u} = \partial L / \partial u$. Setiap operasi cukup tahu **turunan lokalnya**:
$$\bar{x} = \bar{u} \cdot \frac{\partial u}{\partial x} \qquad (\text{gradien hilir} = \text{gradien hulu} \times \text{gradien lokal})$$

---

# Computational Graph: Contoh Kecil

$f(a, b, c) = (a + b)\cdot c$ dengan $a = 2$, $b = -1$, $c = 3$. Definisikan $q = a + b$.

| Langkah | Forward | Backward (mulai $\bar f = \partial f/\partial f = 1$) |
|---|---|---|
| $q = a + b$ | $q = 1$ | $\bar{q} = \bar{f}\cdot \partial f/\partial q = 1 \cdot c = 3$ |
| $f = q \cdot c$ | $f = 3$ | $\bar{c} = \bar{f}\cdot q = 1$ |
| | | $\bar{a} = \bar{q} \cdot 1 = 3$, $\quad \bar{b} = \bar{q}\cdot 1 = 3$ |

**Pola gerbang** (*gate*) yang sering muncul:

| Operasi | Gradien lokal | Perilaku backward |
|---|---|---|
| Penjumlahan $u = x + y$ | 1, 1 | **Mendistribusikan** gradien hulu apa adanya |
| Perkalian $u = x \cdot y$ | $y$, $x$ | **Menukar**: gradien ke $x$ dikali $y$ |
| $\max(x, y)$ / ReLU | 1 untuk yang terbesar, 0 lainnya | **Meneruskan** hanya ke cabang aktif |
| Percabangan (satu nilai dipakai 2×) | — | **Menjumlahkan** gradien dari semua cabang |

---

# Forward Mode vs Reverse Mode

Untuk $f: \mathbb{R}^n \rightarrow \mathbb{R}^m$, Jacobian $J \in \mathbb{R}^{m \times n}$:

| | Forward mode | **Reverse mode** (backpropagation) |
|---|---|---|
| Arah | Input → output | Output → input |
| Satu lintasan menghasilkan | Satu **kolom** $J$ (turunan semua output terhadap 1 input) | Satu **baris** $J$ (turunan 1 output terhadap semua input) |
| Lintasan untuk Jacobian penuh | $n$ | $m$ |
| Cocok jika | $n \ll m$ | $m \ll n$ |

Neural network: **input = jutaan parameter**, **output = 1 skalar loss** → $m = 1$ → reverse mode menghitung **seluruh gradien dalam satu lintasan backward** (Baydin dkk., 2018).

Biaya backward ≈ konstan kecil × biaya forward (Griewank & Walther, 2008). Imbalannya: semua nilai antara forward harus **disimpan** di memori.

---

# Jaringan Contoh untuk Hitung Manual (2–2–1)

$$z^{(1)} = W^{(1)}x + b^{(1)},\; h = \sigma(z^{(1)}),\; z^{(2)} = w^{(2)\top}h + b^{(2)},\; \hat{y} = \sigma(z^{(2)}),\; L = -[y\ln\hat{y} + (1-y)\ln(1-\hat{y})]$$

| Besaran | Nilai |
|---|---|
| Input $x$ | $[1{,}0;\; 0{,}5]$, target $y = 1$ |
| $W^{(1)}$ (baris = neuron tersembunyi) | $\begin{bmatrix} 0{,}2 & -0{,}4 \\ 0{,}5 & 0{,}1\end{bmatrix}$ |
| $b^{(1)}$ | $[0{,}1;\; -0{,}1]$ |
| $w^{(2)}$, $b^{(2)}$ | $[0{,}6;\; -0{,}3]$, $\;0{,}05$ |
| Aktivasi | Sigmoid $\sigma(z) = 1/(1 + e^{-z})$, $\;\sigma'(z) = \sigma(z)(1 - \sigma(z))$ |
| Loss | *Binary cross-entropy* (BCE) |
| Learning rate | $\eta = 0{,}5$ |

Jumlah parameter: $4 + 2 + 2 + 1 = 9$.

---

# Langkah 1: Forward Pass

| Besaran | Perhitungan | Nilai |
|---|---|---|
| $z^{(1)}_1$ | $0{,}2(1{,}0) + (-0{,}4)(0{,}5) + 0{,}1$ | **0,100000** |
| $z^{(1)}_2$ | $0{,}5(1{,}0) + 0{,}1(0{,}5) - 0{,}1$ | **0,450000** |
| $h_1$ | $\sigma(0{,}1)$ | **0,524979** |
| $h_2$ | $\sigma(0{,}45)$ | **0,610639** |
| $z^{(2)}$ | $0{,}6(0{,}524979) - 0{,}3(0{,}610639) + 0{,}05 = 0{,}314987 - 0{,}183192 + 0{,}05$ | **0,181796** |
| $\hat{y}$ | $\sigma(0{,}181796)$ | **0,545324** |
| $L$ | $-\ln(0{,}545324)$ | **0,606375** |

> Simpan **semua** nilai antara ($z^{(1)}, h, z^{(2)}, \hat{y}$) — semuanya dipakai lagi di backward.

---

# Langkah 2: Backward — Lapisan Output

**Gradien terhadap $z^{(2)}$** (dua jalur menuju hasil yang sama):

$$\frac{\partial L}{\partial \hat{y}} = -\frac{y}{\hat{y}} + \frac{1-y}{1-\hat{y}} = -\frac{1}{0{,}545324} = -1{,}833771, \qquad \frac{\partial \hat{y}}{\partial z^{(2)}} = \hat{y}(1-\hat{y}) = 0{,}247946$$

$$\delta^{(2)} = \frac{\partial L}{\partial z^{(2)}} = -1{,}833771 \times 0{,}247946 = -0{,}454676 \;=\; \hat{y} - y \;\checkmark$$

> Sigmoid + BCE menghasilkan bentuk ringkas $\delta^{(2)} = \hat{y} - y$ (sama halnya softmax + cross-entropy).

| Parameter | Rumus | Nilai |
|---|---|---|
| $\partial L/\partial w^{(2)}_1$ | $\delta^{(2)} h_1 = -0{,}454676 \times 0{,}524979$ | **−0,238695** |
| $\partial L/\partial w^{(2)}_2$ | $\delta^{(2)} h_2 = -0{,}454676 \times 0{,}610639$ | **−0,277643** |
| $\partial L/\partial b^{(2)}$ | $\delta^{(2)}$ | **−0,454676** |

---

<!-- _class: small -->

# Langkah 3: Backward — Lapisan Tersembunyi

**Gradien mengalir ke $h$** (gerbang perkalian → dikali bobot):
$$\frac{\partial L}{\partial h_j} = \delta^{(2)} w^{(2)}_j: \quad \bar h_1 = -0{,}454676 \times 0{,}6 = -0{,}272805, \quad \bar h_2 = -0{,}454676 \times (-0{,}3) = 0{,}136403$$

**Melewati sigmoid**: $\delta^{(1)}_j = \bar h_j \cdot h_j(1 - h_j)$

| $j$ | $\bar h_j$ | $\sigma'(z^{(1)}_j) = h_j(1-h_j)$ | $\delta^{(1)}_j$ |
|---|---|---|---|
| 1 | −0,272805 | 0,524979 × 0,475021 = 0,249376 | **−0,068031** |
| 2 | 0,136403 | 0,610639 × 0,389361 = 0,237759 | **0,032431** |

**Gradien bobot**: $\partial L/\partial W^{(1)}_{jk} = \delta^{(1)}_j\, x_k$, $\;\partial L/\partial b^{(1)}_j = \delta^{(1)}_j$

| | $x_1 = 1{,}0$ | $x_2 = 0{,}5$ | bias |
|---|---|---|---|
| neuron 1 ($\delta = -0{,}068031$) | **−0,068031** | **−0,034016** | **−0,068031** |
| neuron 2 ($\delta = 0{,}032431$) | **0,032431** | **0,016215** | **0,032431** |

---

<!-- _class: small -->

# Langkah 4: Pembaruan Parameter (η = 0,5)

$\theta_\text{baru} = \theta - 0{,}5 \cdot \partial L/\partial\theta$

| Parameter | Lama | Gradien | Baru |
|---|---|---|---|
| $W^{(1)}_{11}$ | 0,2 | −0,068031 | 0,2 + 0,034016 = **0,234016** |
| $W^{(1)}_{12}$ | −0,4 | −0,034016 | **−0,382992** |
| $W^{(1)}_{21}$ | 0,5 | 0,032431 | **0,483785** |
| $W^{(1)}_{22}$ | 0,1 | 0,016215 | **0,091892** |
| $b^{(1)}_1$, $b^{(1)}_2$ | 0,1; −0,1 | −0,068031; 0,032431 | **0,134016; −0,116215** |
| $w^{(2)}_1$, $w^{(2)}_2$ | 0,6; −0,3 | −0,238695; −0,277643 | **0,719348; −0,161179** |
| $b^{(2)}$ | 0,05 | −0,454676 | **0,277338** |

Forward ulang dengan parameter baru: $\hat{y} = 0{,}545324 \rightarrow \mathbf{0{,}639146}$, $\;L = 0{,}606375 \rightarrow \mathbf{0{,}447623}$ ✓ loss turun.

> Perhatikan: $w^{(2)}_2$ naik (−0,3 → −0,161) karena $h_2$ aktif tetapi memberi kontribusi negatif ke output yang seharusnya lebih besar.

---

# Verifikasi: Gradient Check

Bandingkan gradien backprop dengan **beda hingga terpusat** (*central difference*):
$$\frac{\partial L}{\partial \theta_j} \approx \frac{L(\theta + \epsilon e_j) - L(\theta - \epsilon e_j)}{2\epsilon}, \qquad \epsilon = 10^{-4}$$

| Parameter | Backpropagation | Finite difference | Selisih |
|---|---|---|---|
| $W^{(1)}_{11}$ | −0,0680312 | −0,0680312 | < $10^{-8}$ |
| $w^{(2)}_1$ | −0,2386953 | −0,2386953 | < $10^{-8}$ |

Ukuran relatif yang lazim: $\dfrac{\lVert g_\text{bp} - g_\text{fd} \rVert}{\lVert g_\text{bp} \rVert + \lVert g_\text{fd} \rVert}$ — sekitar $10^{-7}$ ke bawah biasanya menandakan implementasi benar (dengan presisi float64).

> Gradient check **sangat lambat** ($2p$ forward) → hanya untuk *debugging* lapisan buatan sendiri, bukan saat training.

---

# Bentuk Matriks (Vektorisasi)

Untuk jaringan $L$ lapisan: $z^{(l)} = W^{(l)} a^{(l-1)} + b^{(l)}$, $\;a^{(l)} = \phi(z^{(l)})$, $\;a^{(0)} = x$.

$$\delta^{(L)} = \nabla_{a^{(L)}}\mathcal{L} \odot \phi'(z^{(L)}) \qquad (\text{untuk sigmoid + BCE: } \delta^{(L)} = \hat{y} - y)$$
$$\boxed{\delta^{(l)} = \left(W^{(l+1)\top}\delta^{(l+1)}\right) \odot \phi'(z^{(l)})}$$
$$\frac{\partial \mathcal{L}}{\partial W^{(l)}} = \delta^{(l)}\, a^{(l-1)\top}, \qquad \frac{\partial \mathcal{L}}{\partial b^{(l)}} = \delta^{(l)}$$

Cek dengan contoh: $W^{(2)\top}\delta^{(2)} = [0{,}6;\,-0{,}3](-0{,}454676) = [-0{,}272805;\; 0{,}136403]$, lalu $\odot\,[0{,}249376;\; 0{,}237759] = [-0{,}068031;\; 0{,}032431]$ ✓

Untuk mini-batch $B$ contoh, $a^{(l-1)}$ menjadi matriks dan gradien bobot = **jumlah/rata-rata** atas batch → operasi perkalian matriks yang efisien di GPU.

---

# Vanishing & Exploding Gradient

Dari rekursi $\delta^{(l)} = (W^{(l+1)\top}\delta^{(l+1)}) \odot \phi'(z^{(l)})$, gradien di lapisan awal adalah **hasil kali** banyak faktor:

- Sigmoid: $\sigma'(z) \le 0{,}25$ → melewati 10 lapisan: faktor $\le 0{,}25^{10} \approx 9{,}5 \times 10^{-7}$ → **vanishing**
- Bobot besar ($\lVert W \rVert > 1$ berulang) → gradien membesar eksponensial → **exploding** (sering pada RNN)

| Masalah | Solusi yang umum |
|---|---|
| Vanishing | ReLU & variannya; inisialisasi He/Xavier; **residual connection**; normalisasi (BatchNorm/LayerNorm); LSTM/GRU pada RNN |
| Exploding | **Gradient clipping** (mis. norma ≤ 1); inisialisasi yang tepat; learning rate lebih kecil |

> Hampir setiap "building block" modern (ReLU, residual, normalization) dirancang agar **gradien mengalir dengan baik** selama backpropagation.

---

<!-- _class: small -->

# Autograd di PyTorch

```python
import torch
x  = torch.tensor([1.0, 0.5]); y = torch.tensor(1.0)
W1 = torch.tensor([[0.2, -0.4], [0.5, 0.1]], requires_grad=True)
b1 = torch.tensor([0.1, -0.1], requires_grad=True)
w2 = torch.tensor([0.6, -0.3], requires_grad=True)
b2 = torch.tensor(0.05, requires_grad=True)

h     = torch.sigmoid(W1 @ x + b1)                 # forward: graf komputasi direkam
y_hat = torch.sigmoid(w2 @ h + b2)
loss  = torch.nn.functional.binary_cross_entropy(y_hat, y)
loss.backward()                                    # reverse-mode AD
print(loss.item())   # ~0.606375
print(W1.grad)       # ~[[-0.0680, -0.0340], [ 0.0324,  0.0162]]
print(w2.grad, b2.grad)  # ~[-0.2387, -0.2776]  -0.4547
```

| Fungsi | Peran |
|---|---|
| `requires_grad=True` | Tandai tensor yang gradiennya dibutuhkan |
| `loss.backward()` | Menjalankan backpropagation dari skalar `loss` |
| `.grad` | Tempat gradien disimpan — **diakumulasi** (ditambahkan), bukan ditimpa |
| `optimizer.zero_grad()` | Mengosongkan `.grad` sebelum iterasi berikutnya |
| `torch.no_grad()` | Mematikan perekaman graf (evaluasi/inferensi) → hemat memori |

---

# Jebakan Umum

| Jebakan | Akibat | Solusi |
|---|---|---|
| Lupa `zero_grad()` | Gradien bertumpuk antar-iterasi | Panggil setiap iterasi |
| Memanggil `.backward()` dua kali pada graf yang sama | Error: graf sudah dibebaskan | `retain_graph=True` jika memang perlu |
| Operasi *in-place* pada tensor yang dibutuhkan backward | Error / gradien salah | Hindari `x += ...` pada tensor tersebut |
| `.item()`, `.numpy()`, `.detach()` di tengah perhitungan loss | Graf terputus, gradien = None | Pertahankan operasi dalam tensor |
| Sigmoid lalu `BCELoss` terpisah | Tidak stabil secara numerik untuk logit ekstrem | Gunakan `BCEWithLogitsLoss` pada logit |
| Inferensi tanpa `no_grad()` | Memori membengkak | `with torch.no_grad():` |

---

# Latihan

Jaringan 1–1–1: $z_1 = w_1 x + b_1$, $h = \text{ReLU}(z_1)$, $\hat{y} = w_2 h + b_2$, loss $L = \tfrac{1}{2}(\hat{y} - y)^2$.

Nilai: $x = 2$, $y = 3$, $w_1 = 0{,}5$, $b_1 = 0$, $w_2 = 1{,}5$, $b_2 = 0{,}5$, $\eta = 0{,}1$.

1. Hitung forward pass: $z_1$, $h$, $\hat{y}$, $L$.
2. Hitung $\partial L/\partial \hat{y}$, $\partial L/\partial w_2$, $\partial L/\partial b_2$.
3. Hitung $\partial L/\partial h$, $\partial L/\partial z_1$, $\partial L/\partial w_1$, $\partial L/\partial b_1$.
4. Lakukan satu langkah gradient descent dan hitung loss baru.
5. Apa yang terjadi pada $\partial L/\partial w_1$ jika $w_1 = -0{,}5$? Jelaskan kaitannya dengan "dying ReLU".
6. Pada $f(a,b,c) = (a \cdot b) + c$ dengan $a = 3$, $b = -2$, $c = 4$: hitung $\bar a, \bar b, \bar c$.

---

<!-- _class: small -->

# Kunci Jawaban Latihan

1. $z_1 = 0{,}5 \cdot 2 + 0 = 1$; $h = \text{ReLU}(1) = 1$; $\hat{y} = 1{,}5 \cdot 1 + 0{,}5 = 2$; $L = \tfrac{1}{2}(2 - 3)^2 = \mathbf{0{,}5}$
2. $\partial L/\partial \hat{y} = \hat{y} - y = -1$; $\partial L/\partial w_2 = -1 \cdot h = \mathbf{-1}$; $\partial L/\partial b_2 = \mathbf{-1}$
3. $\partial L/\partial h = -1 \cdot w_2 = -1{,}5$; ReLU'(1) = 1 → $\partial L/\partial z_1 = -1{,}5$; $\partial L/\partial w_1 = -1{,}5 \cdot x = \mathbf{-3}$; $\partial L/\partial b_1 = \mathbf{-1{,}5}$
4. $w_1 = 0{,}5 + 0{,}3 = 0{,}8$; $b_1 = 0 + 0{,}15 = 0{,}15$; $w_2 = 1{,}5 + 0{,}1 = 1{,}6$; $b_2 = 0{,}5 + 0{,}1 = 0{,}6$
   Forward ulang: $z_1 = 0{,}8 \cdot 2 + 0{,}15 = 1{,}75$; $h = 1{,}75$; $\hat{y} = 1{,}6 \cdot 1{,}75 + 0{,}6 = 3{,}4$; $L = \tfrac{1}{2}(0{,}4)^2 = \mathbf{0{,}08}$
5. $z_1 = -1 < 0$ → ReLU'$= 0$ → $\partial L/\partial w_1 = \partial L/\partial b_1 = 0$: neuron tidak belajar. Jika $z_1 < 0$ untuk **semua** data, neuron "mati" permanen (*dying ReLU*).
6. $q = ab = -6$, $f = q + c = -2$. Gerbang penjumlahan: $\bar q = 1$, $\bar c = \mathbf{1}$; gerbang perkalian: $\bar a = \bar q \cdot b = \mathbf{-2}$, $\bar b = \bar q \cdot a = \mathbf{3}$

---

# Ringkasan

1. Backpropagation = **chain rule** yang diterapkan dari output ke input pada **computational graph**.
2. Setiap operasi cukup mengetahui **gradien lokal**; gradien hilir = gradien hulu × gradien lokal; cabang → **dijumlahkan**.
3. **Reverse mode** cocok untuk banyak parameter → satu skalar loss: biaya ≈ beberapa kali forward, tetapi perlu memori untuk aktivasi.
4. Rumus inti: $\delta^{(l)} = (W^{(l+1)\top}\delta^{(l+1)}) \odot \phi'(z^{(l)})$, $\;\partial\mathcal{L}/\partial W^{(l)} = \delta^{(l)} a^{(l-1)\top}$.
5. Sigmoid/softmax + cross-entropy → $\delta = \hat{y} - y$.
6. Selalu bisa diverifikasi dengan **gradient check**.
7. Hasil kali turunan menyebabkan **vanishing/exploding gradient** → motivasi ReLU, residual, normalisasi, clipping.

---

<!-- _class: small -->

# Referensi

1. Baydin, A. G., Pearlmutter, B. A., Radul, A. A., & Siskind, J. M. (2018). Automatic differentiation in machine learning: A survey. *JMLR*, 18(153), 1–43.
2. Bishop, C. M., & Bishop, H. (2024). *Deep Learning: Foundations and Concepts*, Bab 8 (Backpropagation). Springer.
3. Glorot, X., & Bengio, Y. (2010). Understanding the difficulty of training deep feedforward neural networks. *AISTATS*.
4. Goodfellow, I., Bengio, Y., & Courville, A. (2016). *Deep Learning*, §6.5 (Back-Propagation and Other Differentiation Algorithms). MIT Press.
5. Griewank, A., & Walther, A. (2008). *Evaluating Derivatives: Principles and Techniques of Algorithmic Differentiation* (2nd ed.). SIAM.
6. Paszke, A., dkk. (2019). PyTorch: An imperative style, high-performance deep learning library. *NeurIPS*.
7. Pascanu, R., Mikolov, T., & Bengio, Y. (2013). On the difficulty of training recurrent neural networks. *ICML*.
8. Prince, S. J. D. (2023). *Understanding Deep Learning*, Bab 7 (Gradients and Initialization). MIT Press.
9. Rumelhart, D. E., Hinton, G. E., & Williams, R. J. (1986). Learning representations by back-propagating errors. *Nature*, 323, 533–536.
10. Zhang, A., Lipton, Z. C., Li, M., & Smola, A. J. (2023). *Dive into Deep Learning*, §5.3 (Forward Propagation, Backward Propagation, and Computational Graphs). Cambridge University Press.

---

<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _header: '' -->

# Terima Kasih

### Berikutnya: **Embedding Layers** — merepresentasikan simbol sebagai vektor

Kerjakan latihan dan verifikasi dengan `loss.backward()`
