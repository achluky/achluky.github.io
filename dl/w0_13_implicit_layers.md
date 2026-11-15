---
marp: true
theme: default
paginate: true
size: 16:9
math: mathjax
header: 'Building Blocks of Deep Learning · Implicit Layers'
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

# Implicit Layers
## Fixed-Point (DEQ) · Neural ODE · Optimization Layers

### Minggu 0 — Deep Learning: Building Blocks
**Sains Data ITERA · Ganjil 2026/2025**

---

# Capaian Pembelajaran & Agenda

> Mahasiswa mampu membedakan layer **eksplisit** dan **implisit**, menghitung manual solusi *fixed point* dan gradiennya dengan **teorema fungsi implisit**, serta menjelaskan Deep Equilibrium Models, Neural ODE, dan *optimization layers*.

1. Layer eksplisit vs implisit
2. **Fixed-point layer**: iterasi, syarat konvergensi, metode Newton
3. **Teorema fungsi implisit** (IFT) — gradien tanpa menyimpan iterasi
4. Hitung manual: $z = \tanh(wz + x)$, gradien IFT vs beda hingga
5. **Deep Equilibrium Models** (DEQ): kedalaman "tak hingga", memori $O(1)$
6. **Neural ODE**: ResNet sebagai metode Euler, hitung manual Euler
7. **Optimization layers** (OptNet): ReLU sebagai solusi optimasi
8. Implementasi PyTorch · kelebihan & keterbatasan · latihan

---

# Eksplisit vs Implisit

**Layer eksplisit** — output dihitung langsung dengan rumus:
$$z = f(x;\theta) \qquad \text{contoh: } z = \text{ReLU}(Wx + b)$$

**Layer implisit** — output didefinisikan sebagai solusi suatu **kondisi**:
$$\text{temukan } z^\star \text{ sehingga } g(x, z^\star; \theta) = 0$$

| Jenis layer implisit | Kondisi yang dipenuhi output |
|---|---|
| **Fixed-point / equilibrium** | $z^\star = f(z^\star, x)$ → $g = z - f(z, x) = 0$ |
| **ODE** | $z(T)$ adalah solusi $\dfrac{dz}{dt} = f(z, t)$ dengan $z(0) = x$ |
| **Optimasi** | $z^\star = \arg\min_z\, E(z, x)$ → $\nabla_z E = 0$ (+ KKT) |

> Ide kunci (Kolter, Duvenaud & Johnson, 2020): pisahkan **apa** yang dihitung (kondisi) dari **bagaimana** menghitungnya (solver). Gradien bisa diperoleh dari kondisinya saja — tanpa *backprop* melalui langkah-langkah solver.

---

<!-- _class: divider -->

# Fixed-Point Layer

---

# Contoh Skalar: $z = \tanh(wz + x)$

Layer: diberikan $x$ dan parameter $w$, output $z^\star$ memenuhi
$$z^\star = \tanh(w z^\star + x)$$
$z^\star$ muncul di **kedua sisi** → tidak ada rumus tertutup; harus diselesaikan secara numerik.

**Iterasi fixed-point**: $z^{(k+1)} = \tanh(w z^{(k)} + x)$, mulai dari $z^{(0)} = 0$.

**Syarat konvergensi** (teorema Banach): $f$ merupakan **kontraksi**, yaitu $\left|\dfrac{\partial f}{\partial z}\right| < 1$ di sekitar solusi:
$$\frac{\partial f}{\partial z} = w\,(1 - \tanh^2(wz + x)) = w\,(1 - z^2), \qquad |w| < 1 \Rightarrow \text{kontraksi}$$

Pada DEQ berdimensi tinggi: $\dfrac{\partial f}{\partial z}$ adalah matriks Jacobian; kontraksi ⇔ normanya < 1.

---

<!-- _class: small -->

# Hitung Manual: Iterasi Fixed-Point ($w = 0{,}5$, $x = 1$)

| $k$ | $z^{(k-1)}$ | $wz^{(k-1)} + x$ | $z^{(k)} = \tanh(\cdot)$ | $\lvert z^{(k)} - z^{(k-1)}\rvert$ |
|---|---|---|---|---|
| 1 | 0,000000 | 1,000000 | 0,761594 | 0,761594 |
| 2 | 0,761594 | 1,380797 | 0,881130 | 0,119535 |
| 3 | 0,881130 | 1,440565 | 0,893811 | 0,012682 |
| 4 | 0,893811 | 1,446906 | 0,895079 | 0,001268 |
| 5 | 0,895079 | 1,447540 | 0,895205 | 0,000126 |
| 6 | 0,895205 | 1,447603 | 0,895218 | 0,000013 |
| 7 | 0,895218 | 1,447609 | 0,895219 | 0,000001 |

$$z^\star \approx \mathbf{0{,}895219}$$

Galat turun ≈ 10× setiap iterasi — sesuai faktor kontraksi $w(1 - z^{\star 2}) = 0{,}5 \times 0{,}1986 = 0{,}0993$ (konvergensi **linear**).

---

# Solver Lebih Cepat: Metode Newton

Selesaikan $g(z) = z - \tanh(wz + x) = 0$ dengan
$$z^{(k+1)} = z^{(k)} - \frac{g(z^{(k)})}{g'(z^{(k)})}, \qquad g'(z) = 1 - w\,(1 - \tanh^2(wz + x))$$

| $k$ | $z^{(k)}$ |
|---|---|
| 0 | 0 |
| 1 | 0,964028 |
| 2 | 0,895443 |
| 3 | 0,8952191987 |
| 4 | 0,8952191962 |

Langkah 1: $g(0) = -\tanh(1) = -0{,}7616$; $g'(0) = 1 - 0{,}5(1 - 0{,}58) = 0{,}79$ → $z^{(1)} = 0 + 0{,}7616/0{,}79 = 0{,}9640$.

Konvergensi **kuadratik** (jumlah digit benar ≈ berlipat dua). Dalam dimensi tinggi, menghitung Jacobian penuh mahal → DEQ memakai **Broyden** (aproksimasi Jacobian) atau **Anderson acceleration**.

---

<!-- _class: divider -->

# Gradien via Teorema Fungsi Implisit

---

# Teorema Fungsi Implisit (IFT)

Jika $g(x, z^\star(\theta); \theta) = 0$ untuk semua $\theta$ di sekitar titik tersebut dan $\partial g / \partial z$ invertibel, maka turunkan kedua sisi terhadap $\theta$:

$$\frac{\partial g}{\partial \theta} + \frac{\partial g}{\partial z}\,\frac{dz^\star}{d\theta} = 0 \quad\Longrightarrow\quad \boxed{\frac{dz^\star}{d\theta} = -\left(\frac{\partial g}{\partial z}\right)^{-1}\frac{\partial g}{\partial \theta}}$$

Untuk fixed point $g = z - f(z, x; \theta)$:
$$\frac{dz^\star}{d\theta} = \left(I - \frac{\partial f}{\partial z}\right)^{-1}\frac{\partial f}{\partial \theta}\Bigg|_{z = z^\star}$$

**Konsekuensi penting**
- Gradien hanya bergantung pada **titik solusi** $z^\star$ — bukan pada berapa iterasi atau solver apa yang dipakai.
- Tidak perlu menyimpan iterasi untuk *backprop* → memori **konstan**.
- Dalam praktik tidak menghitung invers; selesaikan sistem linear $\left(I - \frac{\partial f}{\partial z}\right)^{\!\top} u = \frac{\partial \mathcal{L}}{\partial z^\star}$ (juga bisa dengan iterasi fixed-point).

---

<!-- _class: small -->

# Hitung Manual: Gradien IFT untuk $z = \tanh(wz + x)$

$g(z, w, x) = z - \tanh(wz + x)$. Di solusi, $\tanh(wz^\star + x) = z^\star$, sehingga $1 - \tanh^2(\cdot) = 1 - z^{\star 2}$.

$$\frac{\partial g}{\partial z} = 1 - w(1 - z^{\star 2}), \qquad \frac{\partial g}{\partial w} = -(1 - z^{\star 2})\,z^\star, \qquad \frac{\partial g}{\partial x} = -(1 - z^{\star 2})$$

Dengan $z^\star = 0{,}895219$: $1 - z^{\star 2} = 0{,}198583$, $\;\partial g/\partial z = 1 - 0{,}5(0{,}198583) = 0{,}900709$.

$$\frac{dz^\star}{dw} = \frac{(1 - z^{\star 2})\,z^\star}{1 - w(1 - z^{\star 2})} = \frac{0{,}198583 \times 0{,}895219}{0{,}900709} = \mathbf{0{,}197372}$$
$$\frac{dz^\star}{dx} = \frac{1 - z^{\star 2}}{1 - w(1 - z^{\star 2})} = \frac{0{,}198583}{0{,}900709} = \mathbf{0{,}220474}$$

**Cek dengan beda hingga** (selesaikan ulang fixed point pada $w \pm 10^{-5}$ dan $x \pm 10^{-5}$):

| Turunan | IFT | Beda hingga terpusat |
|---|---|---|
| $dz^\star/dw$ | 0,197372 | 0,197372 |
| $dz^\star/dx$ | 0,220474 | 0,220474 |

---

# Backprop Unrolled vs IFT

| | *Unrolled* (backprop melalui $K$ iterasi) | **IFT (implicit differentiation)** |
|---|---|---|
| Memori | $O(K)$ — simpan semua $z^{(k)}$ | $O(1)$ — cukup $z^\star$ |
| Gradien | Turunan dari **prosedur** iterasi (terpotong di $K$) | Turunan **eksak** dari solusi (bila $z^\star$ akurat) |
| Ketergantungan solver | Ya | Tidak — solver bebas diganti |
| Biaya backward | $K$ langkah | Satu sistem linear |

> Untuk contoh skalar, *backward* IFT hanya butuh **satu pembagian**; *unrolled* butuh menyimpan dan mundur melalui 7+ iterasi.

---

<!-- _class: divider -->

# Deep Equilibrium Models (DEQ)

---

# DEQ (Bai, Kolter & Koltun, 2019)

Observasi: jaringan dalam dengan **bobot sama di setiap layer** (*weight-tied*),
$$z^{[i+1]} = f_\theta(z^{[i]}, x), \quad i = 0, 1, \ldots, L-1$$
sering **konvergen** ke titik tetap saat $L \to \infty$. DEQ langsung mencari titik tersebut:

$$z^\star = f_\theta(z^\star, x) \qquad \text{(setara jaringan sedalam tak hingga)}$$

| Tahap | Cara |
|---|---|
| Forward | Solver akar (Broyden / Anderson) untuk $g_\theta(z) = f_\theta(z, x) - z = 0$ |
| Backward | IFT: selesaikan $\left(I - J_{f}\right)^{\!\top} u = \dfrac{\partial \mathcal{L}}{\partial z^\star}$, lalu $\dfrac{\partial \mathcal{L}}{\partial \theta} = u^\top \dfrac{\partial f}{\partial \theta}$ |
| Memori | **Konstan** terhadap "kedalaman" |

- Bai dkk. (2019) menerapkan DEQ pada *language modeling* dengan $f_\theta$ berupa sel Transformer/TrellisNet dan mencapai kinerja kompetitif dengan memori jauh lebih kecil.
- Keterbatasan: waktu forward bisa lebih lama dan bervariasi; kestabilan (kontraksi) tidak dijamin otomatis.

---

<!-- _class: divider -->

# Neural ODE

---

# Dari ResNet ke Neural ODE (Chen dkk., 2018)

Blok residual: $h_{t+1} = h_t + f(h_t, \theta_t)$

Metode **Euler** untuk ODE $\dfrac{dh}{dt} = f(h, t, \theta)$ dengan langkah $\Delta t$:
$$h(t + \Delta t) = h(t) + \Delta t \cdot f(h(t), t, \theta)$$

→ ResNet = Euler dengan $\Delta t = 1$. **Neural ODE**: jadikan dinamika kontinu dan biarkan *ODE solver* (adaptif) menghitung
$$h(T) = h(0) + \int_0^T f(h(t), t, \theta)\,dt$$

- Output didefinisikan **implisit** sebagai solusi ODE.
- Gradien dihitung dengan **metode adjoint**: selesaikan ODE lain mundur dalam waktu → memori $O(1)$ terhadap jumlah langkah solver.
- Aplikasi: deret waktu tak beraturan, *continuous normalizing flows*.

---

<!-- _class: small -->

# Hitung Manual: Metode Euler

ODE $\dfrac{dz}{dt} = a z$ dengan $a = -1$, $z(0) = 1$. Solusi eksak $z(1) = e^{-1} = 0{,}367879$.

**Euler, $\Delta t = 0{,}25$ (4 langkah)**: $z_{k+1} = z_k + \Delta t \cdot a z_k = z_k(1 - 0{,}25) = 0{,}75\,z_k$

| Langkah | $t$ | $z_k$ | $f = -z_k$ | $z_{k+1} = z_k + 0{,}25 f$ |
|---|---|---|---|---|
| 1 | 0,00 | 1,000000 | −1,000000 | 0,750000 |
| 2 | 0,25 | 0,750000 | −0,750000 | 0,562500 |
| 3 | 0,50 | 0,562500 | −0,562500 | 0,421875 |
| 4 | 0,75 | 0,421875 | −0,421875 | **0,316406** |

| Langkah $\Delta t$ | Jumlah langkah ("layer") | $z(1)$ | Galat |
|---|---|---|---|
| 0,25 | 4 | 0,316406 | 0,051473 |
| 0,10 | 10 | 0,348678 | 0,019201 |
| eksak | — | 0,367879 | 0 |

> Lebih banyak langkah = "jaringan lebih dalam" = lebih akurat. Solver adaptif memilih jumlah langkah otomatis sesuai toleransi galat.

---

<!-- _class: divider -->

# Optimization Layers

---

# Optimization Layer: Output = Solusi Masalah Optimasi

$$z^\star(x) = \arg\min_z\; E(z, x) \quad \text{s.t. kendala}$$

**OptNet** (Amos & Kolter, 2017): layer berupa *quadratic program*
$$z^\star = \arg\min_z\; \tfrac{1}{2} z^\top Q z + q^\top z \quad \text{s.t. } Az = b,\; Gz \le h$$
dengan $Q, q, A, b, G, h$ dapat bergantung pada input/parameter. Gradien diperoleh dengan **diferensiasi implisit kondisi KKT**.

**Contoh: ReLU adalah optimization layer!**
$$\text{ReLU}(x) = \arg\min_{z \ge 0}\; \tfrac{1}{2}\lVert z - x\rVert^2 \quad \text{(proyeksi ke orthant non-negatif)}$$

Untuk $x = (-2;\; 0{,}5;\; 3)$: titik terdekat dengan $z \ge 0$ adalah $z^\star = (0;\; 0{,}5;\; 3)$ — persis $\text{ReLU}(x)$.

Contoh lain: **softmax** = solusi $\arg\max_{p \in \Delta}\; p^\top x + H(p)$ (dengan $H$ entropi). Aplikasi OptNet: menyelesaikan Sudoku dari contoh.

---

<!-- _class: small -->

# PyTorch: Layer Fixed-Point dengan Backward IFT

```python
import torch

class FixedPointTanh(torch.autograd.Function):
    """z* = tanh(w z* + x); forward iteratif, backward dengan IFT (tanpa menyimpan iterasi)."""
    @staticmethod
    def forward(ctx, x, w):
        with torch.no_grad():
            z = torch.zeros_like(x)
            for _ in range(100):
                z = torch.tanh(w * z + x)
        ctx.save_for_backward(z, w)
        return z

    @staticmethod
    def backward(ctx, grad_z):
        z, w = ctx.saved_tensors
        s = 1 - z**2                         # turunan tanh di titik solusi
        denom = 1 - w * s                    # dg/dz
        return grad_z * s / denom, grad_z * s * z / denom   # dL/dx, dL/dw

x = torch.tensor(1.0, requires_grad=True)
w = torch.tensor(0.5, requires_grad=True)
z = FixedPointTanh.apply(x, w)
z.backward()
print(z.item(), x.grad.item(), w.grad.item())   # 0.895219  0.220474  0.197372
```

Pustaka nyata: tutorial dan kode di **implicit-layers-tutorial.org**; `torchdiffeq` (Neural ODE); `cvxpylayers` (optimization layers).

---

# Kelebihan, Keterbatasan & Kesalahan Umum

| Kelebihan | Keterbatasan |
|---|---|
| Memori konstan terhadap kedalaman / langkah solver | Waktu forward bisa panjang dan tidak tetap |
| Representasi ringkas (satu blok bobot) | Solusi bisa **tidak ada / tidak unik** |
| Solver dapat diganti tanpa mengubah gradien | Gradien IFT akurat hanya jika solusi akurat |
| Menyatukan model dengan pengetahuan domain (ODE, kendala) | Training dapat tidak stabil bila tidak kontraktif |

**Kesalahan umum**
- Menghentikan solver terlalu dini lalu memakai IFT → gradien salah.
- Tidak menjaga kontraksi (mis. norma bobot terlalu besar) → iterasi divergen.
- Lupa bahwa $\partial g/\partial z$ harus invertibel — di dekat titik singular gradien meledak.

---

# Latihan

1. Layer fixed-point $z = 0{,}5\,z + x$ (linear). Tentukan $z^\star$ secara analitik untuk $x = 2$ dan lakukan 3 iterasi mulai $z^{(0)} = 0$.
2. Untuk soal 1, hitung $dz^\star/dx$ dengan IFT dan cocokkan dengan rumus analitik.
3. Apakah iterasi $z^{(k+1)} = 2 z^{(k)} + 1$ konvergen? Jelaskan dengan syarat kontraksi.
4. Euler untuk $dz/dt = -2z$, $z(0) = 1$, $\Delta t = 0{,}5$, dua langkah. Bandingkan dengan $e^{-2}$.
5. Hitung $\arg\min_{z \ge 0} \tfrac{1}{2}(z - x)^2$ untuk $x = -0{,}7$ dan $x = 1{,}3$.
6. Mengapa memori DEQ tidak bertambah saat jumlah iterasi forward bertambah?

---

<!-- _class: small -->

# Kunci Jawaban

1. $z^\star = 0{,}5 z^\star + 2 \Rightarrow 0{,}5 z^\star = 2 \Rightarrow z^\star = \mathbf{4}$. Iterasi: $z^{(1)} = 2$, $z^{(2)} = 3$, $z^{(3)} = 3{,}5$ (galat menyusut ½ tiap langkah).
2. $g = z - 0{,}5z - x$: $\partial g/\partial z = 0{,}5$, $\partial g/\partial x = -1$ → $dz^\star/dx = -(-1)/0{,}5 = \mathbf{2}$. Analitik $z^\star = 2x$ → turunan 2 ✓.
3. **Tidak**: $|\partial f/\partial z| = 2 > 1$ (bukan kontraksi); dari $z^{(0)} = 0$: 1, 3, 7, 15, … divergen, padahal titik tetap $z^\star = -1$ ada.
4. $z_{k+1} = z_k(1 - 2 \cdot 0{,}5) = 0$ → $z_1 = 0$, $z_2 = \mathbf{0}$; eksak $e^{-2} = 0{,}1353$. Langkah terlalu besar → galat besar (batas stabilitas Euler).
5. $x = -0{,}7 \Rightarrow z^\star = \mathbf{0}$; $x = 1{,}3 \Rightarrow z^\star = \mathbf{1{,}3}$ (= ReLU).
6. Forward dijalankan tanpa graf komputasi (`no_grad`); backward hanya memerlukan $z^\star$ dan Jacobian di titik itu (IFT), bukan riwayat iterasi.

---

# Ringkasan

1. Layer **implisit** mendefinisikan output sebagai solusi kondisi $g(x, z^\star) = 0$ — fixed point, ODE, atau optimasi.
2. Forward memakai **solver** (fixed-point, Newton, Broyden/Anderson, ODE solver, QP solver).
3. **Teorema fungsi implisit**: $\dfrac{dz^\star}{d\theta} = -\left(\dfrac{\partial g}{\partial z}\right)^{-1}\dfrac{\partial g}{\partial \theta}$ — gradien eksak, memori $O(1)$, bebas solver.
4. **DEQ** = jaringan *weight-tied* sedalam tak hingga; **Neural ODE** = ResNet kontinu; **OptNet** = layer berupa QP (ReLU dan softmax adalah contoh sederhana).
5. Syarat praktis: kontraksi / stabilitas, solver cukup akurat, $\partial g/\partial z$ invertibel.

---

<!-- _class: small -->

# Referensi

1. Amos, B., & Kolter, J. Z. (2017). OptNet: Differentiable optimization as a layer in neural networks. *ICML*.
2. Chen, R. T. Q., Rubanova, Y., Bettencourt, J., & Duvenaud, D. (2018). Neural ordinary differential equations. *NeurIPS*.
3. Bai, S., Kolter, J. Z., & Koltun, V. (2019). Deep equilibrium models. *NeurIPS*.
4. Kolter, Z., Duvenaud, D., & Johnson, M. (2020). *Deep Implicit Layers — Neural ODEs, Deep Equilibrium Models, and Beyond*. NeurIPS 2020 Tutorial. http://implicit-layers-tutorial.org
5. Agrawal, A., Amos, B., Barratt, S., Boyd, S., Diamond, S., & Kolter, J. Z. (2019). Differentiable convex optimization layers. *NeurIPS*. (pustaka `cvxpylayers`)
6. He, K., Zhang, X., Ren, S., & Sun, J. (2016). Deep residual learning for image recognition. *CVPR*.
7. Prince, S. J. D. (2023). *Understanding Deep Learning*. MIT Press. https://udlbook.github.io/udlbook/
8. Burden, R. L., & Faires, J. D. *Numerical Analysis*. Brooks/Cole. (iterasi fixed-point, Newton, Euler)

---

<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _header: '' -->

# Terima Kasih

### Berikutnya: **Gradient Descent & Backpropagation**

Kerjakan latihan, lalu jalankan `FixedPointTanh` dan bandingkan dengan backprop *unrolled*
