---
marp: true
theme: default
paginate: true
size: 16:9
header: 'MLOps — Model Experimentation & Tracking'
footer: 'Sains Data · ITERA · Minggu 6'
style: |
  :root {
    --primary: #1e3a8a;
    --accent: #0ea5e9;
    --warn: #dc2626;
    --ok: #16a34a;
    --muted: #64748b;
  }
  section {
    font-family: 'Inter', 'Segoe UI', 'Helvetica Neue', sans-serif;
    font-size: 25px;
    padding: 60px 70px;
    color: #0f172a;
    background: #ffffff;
  }
  h1 { color: var(--primary); font-size: 1.6em; border-bottom: 3px solid var(--accent); padding-bottom: 6px; }
  h2 { color: var(--primary); font-size: 1.25em; }
  h3 { color: var(--accent); font-size: 1.0em; margin-bottom: 4px; }
  strong { color: var(--primary); }
  em { color: var(--muted); }
  table { font-size: 0.78em; margin: 0 auto; }
  th { background: var(--primary); color: #fff; }
  code { font-size: 0.9em; }
  pre { font-size: 0.68em; line-height: 1.35; border-radius: 8px; }
  blockquote { border-left: 5px solid var(--accent); background: #f0f9ff; padding: 8px 18px; color: #0f172a; font-style: normal; }
  header, footer { color: var(--muted); font-size: 0.55em; }
  section.lead { background: linear-gradient(135deg, #1e3a8a 0%, #0ea5e9 100%); color: #fff; justify-content: center; }
  section.lead h1 { color: #fff; border: none; font-size: 2.1em; }
  section.lead h2, section.lead h3, section.lead strong, section.lead p { color: #e0f2fe; }
  section.divider { background: #0f172a; color: #fff; justify-content: center; }
  section.divider h1 { color: #38bdf8; border: none; font-size: 2em; }
  section.divider p { color: #cbd5e1; }
  section.small { font-size: 21px; }
  section.tiny { font-size: 18px; }
---

<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _header: '' -->
<!-- _footer: '' -->

# Model Experimentation and Tracking in Machine Learning

## Dari "notebook yang berantakan" menuju eksperimen yang **reproducible**, terukur

Ahmad Luky Ramdani · Program Studi Sains Data · ITERA

---

<!-- _class: divider -->

# 1. Motivasi

Mengapa kita butuh *experiment tracking*?

---

# ML Itu Eksperimental, Bukan Deterministik

Software tradisional: **requirement → kode → hasil yang dapat diprediksi**.
Machine learning: **hipotesis → eksperimen → evaluasi → ulangi** (puluhan hingga ribuan kali).

Satu proyek deep learning biasa melibatkan variasi pada:

- **Arsitektur**: ResNet-18 vs ResNet-50 vs ViT, jumlah layer, dropout
- **Hyperparameter**: learning rate, batch size, optimizer, scheduler, weight decay
- **Data**: versi dataset, split, augmentasi, preprocessing, sampling
- **Environment**: versi library, CUDA, GPU, random seed

> Dengan 5 learning rate × 3 batch size × 3 arsitektur × 2 augmentasi = **90 run**. Tanpa pencatatan sistematis, tidak mungkin diingat mana yang terbaik — apalagi *mengapa*.

---

# Gejala Tim Tanpa Experiment Tracking

- 📁 `model_final.pkl`, `model_final_v2.pkl`, `model_final_FIX_benar.pkl`
- 📓 Notebook dengan cell yang dijalankan tidak berurutan → hasil tidak bisa diulang
- 📊 Spreadsheet manual yang tidak sinkron dengan kode yang sebenarnya dijalankan
- ❓ "Akurasi 94% itu dari data versi mana? Hyperparameter-nya apa? Commit yang mana?"
- 🔁 Eksperimen yang sama diulang karena lupa sudah pernah dicoba
- 🚫 Model di produksi bermasalah, tetapi **tidak bisa ditelusuri asalnya** (*no lineage*)

> **Reproducibility crisis**: banyak hasil ML (riset maupun industri) tidak dapat direproduksi, bahkan oleh pembuatnya sendiri.

---

# The real cost of not tracking

| Masalah | Dampak |
|---------|--------|
| Hasil tidak reproducible | Tidak bisa memverifikasi klaim performa; *rework* |
| Tidak ada perbandingan objektif | Keputusan model berdasarkan "feeling" |
| Pengetahuan hilang saat anggota tim keluar | *Bus factor* = 1 |
| Tidak ada audit trail | Gagal memenuhi regulasi (mis. sektor keuangan, kesehatan, EU AI Act) |
| Eksperimen duplikat | Pemborosan GPU-hours dan biaya cloud |
| Debugging produksi sulit | Tidak tahu data/kode apa yang menghasilkan model |

---

<!-- _class: divider -->

# 2. Experiment Tracking dalam ML

---

# MLOps Principles (ml-ops.org)

Prinsip inti MLOps yang saling terkait:

| Prinsip | Kaitan dengan Experiment Tracking |
|---------|-----------------------------------|
| **Iterative-Incremental Development** | Eksperimen adalah unit iterasi dalam fase *Model Development* |
| **Automation** | Logging otomatis, hyperparameter search otomatis |
| **Continuous X** (CI/CD/CT/CM) | Continuous Training menghasilkan run baru yang harus terlacak |
| **Versioning** | Versi data, kode, dan model untuk setiap run |
| **Experiments Tracking** | Prinsip eksplisit: catat setiap eksperimen beserta konteksnya |
| **Testing** | Validasi model dan data sebelum dipromosikan |
| **Monitoring** | Bandingkan metrik produksi dengan metrik eksperimen |
| **Reproducibility** | Tujuan akhir: hasil identik dari input identik |

---

# Tiga Fase MLOps & Posisi Eksperimen

```
 ┌───────────────────┐    ┌─────────────────────────────┐    ┌───────────────────────┐
 │  1. DESIGN        │    │  2. MODEL DEVELOPMENT       │    │  3. OPERATIONS        │
 │                   │    │   (Experimentation)         │    │                       │
 │ • Requirement     │──▶ │ • Data engineering          │──▶ │ • CI/CD pipeline      │
 │ • Use-case        │    │ • ML model engineering      │    │ • Serving / Deploy    │
 │ • Data available? │    │ • Model testing & validasi  │    │ • Monitoring          │
 │                   │    │ ★ EXPERIMENT TRACKING ★    │    │ • Triggering retrain  │
 └───────────────────┘    └─────────────────────────────┘    └───────────────────────┘
          ▲                              │                               │
          └──────────── feedback loop ◀──┴──────── drift / degradasi ◀──┘
```

Experiment tracking adalah **jembatan** antara *development* dan *operations*: model yang di-deploy harus dapat ditelusuri ke **run eksperimen** yang menghasilkannya.

---

# Mengapa ML Butuh Lebih dari Git?

Software tradisional: **Code** → versi cukup dengan Git.
Machine learning: **Code + Data + Model + Config + Environment**.

```
           Software 1.0                    Software 2.0 (ML)
      ┌──────────────────┐          ┌──────────────────────────────┐
      │      CODE        │          │  CODE   ─┐                   │
      │        │         │          │  DATA   ─┼──▶ TRAINING ──▶ MODEL
      │        ▼         │          │  PARAMS ─┤     (stokastik)   │
      │    PROGRAM       │          │  ENV    ─┘                   │
      └──────────────────┘          └──────────────────────────────┘
       versi: git commit             versi: git + data hash + run id
                                            + model version
```

> Model adalah **fungsi dari data**. Mengubah satu baris data dapat mengubah model, meskipun kode tidak berubah sama sekali.

---

<!-- _class: divider -->

# 3. Anatomi Eksperimen

Istilah dan konsep dasar

---

# Terminologi Kunci

| Istilah | Definisi | Contoh |
|---------|----------|--------|
| **Experiment** | Kumpulan run untuk satu pertanyaan/tujuan | `churn-prediction`, `cifar10-classifier` |
| **Run** | Satu kali eksekusi kode training | `run_id = a3f9c1…` |
| **Parameters** | Input konfigurasi (statis per run) | `lr=0.001`, `batch_size=64` |
| **Metrics** | Hasil terukur, bisa per *step/epoch* | `val_loss`, `f1`, `auc` |
| **Artifacts** | File keluaran | model `.pt`, confusion matrix, plot, log |
| **Tags / Metadata** | Label bebas untuk pencarian | `author`, `git_commit`, `stage=baseline` |
| **Lineage** | Jejak asal-usul model | data v3 + commit `9e1b` → run X → model v7 |

---

# Apa yang Harus Dilacak? (The "Full Context")

| Kategori | Item | Mengapa penting |
|----------|------|-----------------|
| **Code** | Git commit hash, branch, *diff* yang belum di-commit | Kode yang tepat yang dijalankan |
| **Data** | Versi/hash dataset, split, skema, statistik | Model = f(data) |
| **Hyperparameters** | lr, epochs, optimizer, arsitektur, seed | Menjelaskan perbedaan hasil |
| **Environment** | `requirements.txt`, Docker image, versi CUDA/cuDNN | Library berbeda → hasil berbeda |
| **Metrics** | Training & validation curves, metrik test akhir | Dasar perbandingan |
| **Artifacts** | Bobot model, plot, prediksi, *feature importance* | Bukti & deliverable |
| **System** | GPU/CPU, memori, durasi, biaya | Efisiensi dan kapasitas |
| **Context** | Siapa, kapan, hipotesis, catatan | Pengetahuan tim |

---

# Siklus Sebuah Eksperimen

```
   ┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐
   │ 1.HIPOTESIS│──▶│ 2. DESAIN  │──▶│ 3. EKSEKUSI│──▶│ 4. ANALISIS│──▶│ 5. KEPUTUSAN│
   │            │   │            │   │  + LOGGING │   │ & KOMPARASI│   │            │
   │"Augmentasi │   │ baseline,  │   │ params,    │   │ kurva,     │   │ promote /  │
   │ mixup naik │   │ variabel,  │   │ metrics,   │   │ tabel,     │   │ iterate /  │
   │ F1 ≥ 2%"   │   │ metrik,    │   │ artifacts  │   │ uji        │   │ discard    │
   │            │   │ seed       │   │            │   │ signifikan │   │            │
   └────────────┘   └────────────┘   └────────────┘   └────────────┘   └─────┬──────┘
         ▲                                                                   │
         └────────────────────────── insight baru ───────────────────────────┘
```

> Eksperimen yang baik dimulai dari **hipotesis yang dapat diuji**, bukan dari "coba-coba saja".

---

<!-- _class: divider -->

# 4. Experimentation in Deep Learning

Merancang eksperimen yang valid

---

# Prinsip Desain Eksperimen

1. **Mulai dari baseline** — model sederhana (mis. logistic regression, ResNet-18 pretrained) sebagai titik acuan.
2. **Ubah satu hal pada satu waktu** — agar efek dapat diatribusikan (*controlled experiment*).
3. **Tetapkan metrik utama sebelum mulai** — hindari *metric shopping* setelah melihat hasil.
4. **Kunci data split** — train / validation / test tetap dan berversi; **test set hanya disentuh di akhir**.
5. **Kendalikan keacakan** — set seed; jalankan beberapa seed untuk mengukur variansi.
6. **Catat hipotesis & kesimpulan** — termasuk eksperimen yang **gagal** (negative results juga pengetahuan).

---

# Sumber Non-Determinisme di Deep Learning

| Sumber | Contoh | Mitigasi |
|--------|--------|----------|
| Inisialisasi bobot | Random init | `torch.manual_seed(42)` |
| Data shuffling | `DataLoader(shuffle=True)` | Seed + `worker_init_fn`, `generator` |
| Augmentasi acak | RandomCrop, Mixup | Seed pada library augmentasi |
| Dropout | Mask acak | Seed global |
| Operasi GPU | cuDNN autotune, atomic add | `torch.backends.cudnn.deterministic=True`, `torch.use_deterministic_algorithms(True)` |
| Hardware/library | Versi CUDA berbeda | Lock environment (Docker) |

```python
import random, numpy as np, torch
def set_seed(seed: int = 42):
    random.seed(seed); np.random.seed(seed)
    torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
```

---

# Variansi: Satu Run Tidak Cukup

Dua konfigurasi, masing-masing 5 seed:

| Konfigurasi | Seed 1 | Seed 2 | Seed 3 | Seed 4 | Seed 5 | **Mean ± Std** |
|-------------|--------|--------|--------|--------|--------|----------------|
| A (lr=1e-3) | 91.2 | 90.4 | 92.0 | 90.8 | 91.5 | **91.18 ± 0.61** |
| B (lr=3e-4) | 92.1 | 89.7 | 91.0 | 92.4 | 90.3 | **91.10 ± 1.15** |

- Jika hanya melihat seed 4 → "B lebih baik". Ternyata **tidak berbeda signifikan**.
- Laporkan **mean ± std** atau *confidence interval*; gunakan uji statistik (t-test, bootstrap) untuk klaim perbaikan.
- Experiment tracker memudahkan agregasi ini dengan **tag/grouping** per konfigurasi.

---

# Strategi Hyperparameter Search

| Strategi | Cara kerja | Kelebihan | Kekurangan |
|----------|-----------|-----------|------------|
| **Manual** | Intuisi peneliti | Murah untuk awal | Bias, tidak sistematis |
| **Grid Search** | Semua kombinasi | Lengkap, sederhana | Eksponensial (*curse of dimensionality*) |
| **Random Search** | Sampel acak | Lebih efisien dari grid (Bergstra & Bengio, 2012) | Tidak belajar dari run sebelumnya |
| **Bayesian Opt.** (Optuna/TPE) | Model surrogate memilih titik berikutnya | Efisien sampel | Lebih kompleks |
| **Early-stopping based** (Hyperband/ASHA) | Hentikan run yang jelek lebih awal | Hemat komputasi | Butuh metrik intermediate |

> Setiap trial = **satu run** di tracker. Gunakan **nested runs** (parent = sweep, child = trial) agar terorganisir.

---

# Ablation Study

Tujuan: mengukur **kontribusi tiap komponen** dengan menghapusnya satu per satu.

| Run | Pretrained | Augmentasi | Label Smoothing | Scheduler | Val F1 |
|-----|:---------:|:----------:|:---------------:|:---------:|-------:|
| Full model | ✅ | ✅ | ✅ | ✅ | **0.884** |
| − Pretrained | ❌ | ✅ | ✅ | ✅ | 0.802 |
| − Augmentasi | ✅ | ❌ | ✅ | ✅ | 0.851 |
| − Label smoothing | ✅ | ✅ | ❌ | ✅ | 0.879 |
| − Scheduler | ✅ | ✅ | ✅ | ❌ | 0.866 |

**Insight**: pretrained weights paling berpengaruh (−8.2 poin); label smoothing hampir tidak berpengaruh → kandidat untuk disederhanakan.

> Tanpa tracker, tabel seperti ini harus dirakit manual dari log yang tercecer.

---

<!-- _class: divider -->

# 5. Tracking Metrics

Apa, kapan, dan bagaimana mengukur

---

# Jenis Metrik yang Dilacak

| Level | Contoh metrik | Granularitas |
|-------|---------------|--------------|
| **Training dynamics** | train/val loss, accuracy, learning rate, gradient norm | per step / epoch |
| **Model quality (offline)** | Accuracy, Precision, Recall, F1, ROC-AUC, RMSE, mAP, BLEU | per run (akhir) |
| **Per-segment / fairness** | F1 per kelas, per wilayah, per gender | per run |
| **Efisiensi** | Waktu training, latency inferensi, ukuran model, FLOPs | per run |
| **System** | GPU utilization, memori GPU, throughput (samples/s) | time-series |
| **Business (online)** | CTR, konversi, revenue — via A/B test | produksi |

> **Offline metric ≠ online metric.** Model dengan AUC tertinggi belum tentu memberi dampak bisnis terbesar; tracking harus menghubungkan keduanya.

---

# Membaca Learning Curves

```
 loss                                     loss
  │╲                                       │╲
  │ ╲   val                                │ ╲        ╱‾‾ val  ← divergen
  │  ╲___________                          │  ╲______╱
  │   ╲__________ train                    │   ╲________________ train
  │                                        │
  └──────────────────▶ epoch               └──────────────────▶ epoch
     ✅ Good fit                               ⚠️ Overfitting → early stopping /
                                                  regularisasi / data lebih banyak

 loss                                     loss
  │‾‾‾‾‾‾‾‾‾‾‾‾‾ val                       │ ╱╲  ╱╲ ╱╲
  │‾‾‾‾‾‾‾‾‾‾‾‾ train                      │╱  ╲╱  ╲╱  ╲╱  ← osilasi
  │                                        │
  └──────────────────▶ epoch               └──────────────────▶ epoch
     ⚠️ Underfitting → model lebih besar,      ⚠️ LR terlalu besar → turunkan lr,
        training lebih lama                       gunakan scheduler / warmup
```

Logging **per step** (bukan hanya nilai akhir) memungkinkan diagnosis seperti ini.

---

# Memilih Metrik yang Tepat

- **Satu metrik utama (*optimizing metric*)** untuk menentukan "terbaik", mis. `val_f1_macro`.
- **Metrik pembatas (*satisficing metrics*)** sebagai syarat minimum, mis. `latency_p95 < 100 ms`, `model_size < 50 MB`.
- Sesuaikan dengan masalah:
  - Data **imbalanced** → F1, PR-AUC, *balanced accuracy* (bukan accuracy).
  - Biaya FN ≫ FP (deteksi penyakit) → **Recall** / *sensitivity*.
  - Ranking/rekomendasi → NDCG, MAP@k.
- Selalu log **metrik pada data validasi**, dan metrik **test** hanya untuk kandidat final.

> "Kebocoran" test set via pemilihan model berulang = *overfitting to the test set*.

---

# Pitfalls dalam Tracking Metrics

| Pitfall | Contoh | Solusi |
|---------|--------|--------|
| **Data leakage** | Normalisasi dihitung pada seluruh data sebelum split | Fit preprocessing hanya pada train; log pipeline sebagai artifact |
| **Cherry-picking** | Melaporkan seed/epoch terbaik saja | Log semua run; laporkan mean ± std |
| **Metrik tidak konsisten** | `f1` macro di run A, weighted di run B | Nama metrik eksplisit: `val_f1_macro` |
| **Split berbeda** | Random split ulang di tiap run | Version & hash data split |
| **Hanya log nilai akhir** | Tidak tahu kapan overfitting mulai | Log per step/epoch |
| **Lupa metrik sistem** | Model akurat tapi 10× lebih lambat | Log latency & resource |

---

<!-- _class: divider -->

# 6. Model Versioning

Data · Code · Model · Registry

---

# Tiga Pilar Versioning

| Pilar | Tools | Yang di-versi |
|-------|-------|---------------|
| **Code** | Git, GitHub/GitLab | Script training, preprocessing, konfigurasi |
| **Data** | DVC, LakeFS, Delta Lake, Pachyderm | Dataset mentah, fitur, split |
| **Model** | MLflow Model Registry, W&B Artifacts, DVC | Bobot, signature, metadata, stage |

**Run eksperimen** adalah simpul yang mengikat ketiganya:

```
  git commit 9e1b2c  ─┐
  data  md5:7fa3…    ─┼──▶  run_id a3f9c1  ──▶  model "fraud-detector" v7  ──▶  production
  config.yaml        ─┘      (metrics, artifacts, env)
```

> Dengan *lineage* ini, setiap prediksi di produksi dapat ditelusuri kembali ke data dan kode asalnya.

---

# Data Versioning dengan DVC

DVC menyimpan **pointer kecil** (`.dvc` file berisi hash) di Git; data aslinya di remote storage (S3, GCS, GDrive, dsb).

```bash
git init && dvc init
dvc remote add -d storage s3://my-bucket/dvc-store

dvc add data/train.csv              # buat data/train.csv.dvc (berisi md5 hash)
git add data/train.csv.dvc .gitignore
git commit -m "data: train v1"
dvc push                            # upload data ke remote

# ... data diperbarui ...
dvc add data/train.csv && git commit -am "data: train v2" && dvc push

git checkout <commit_v1> && dvc checkout   # kembali ke data v1 secara persis
```

Log hash data ke experiment tracker: `mlflow.log_param("data_md5", md5)` → setiap run terhubung ke versi data.

---

# Model Versioning & Model Registry

**Model Registry** = repositori terpusat untuk model dengan versi, metadata, dan status siklus hidup.

| Konsep | Penjelasan |
|--------|------------|
| **Registered model** | Nama logis, mis. `fraud-detector` |
| **Version** | Bertambah otomatis: v1, v2, v3 … — tiap versi menunjuk ke satu run |
| **Alias** (MLflow ≥ 2.9) | Pointer yang dapat dipindah: `@champion`, `@challenger` |
| **Stage** (legacy) | `None → Staging → Production → Archived` |
| **Signature** | Skema input/output model |
| **Lineage** | Run, dataset, commit, author |

```
 v5 (Archived)   v6  ◀── @champion (melayani produksi)
                 v7  ◀── @challenger (shadow / A-B test)
                 v8  (baru diregistrasi, menunggu validasi)
```

**Rollback** = memindahkan alias `@champion` kembali ke versi sebelumnya — cepat dan aman.

---

# Semantic Versioning untuk Model (Opsional)

Konvensi yang sering dipakai tim:

| Perubahan | Contoh | Versi |
|-----------|--------|-------|
| **MAJOR** — skema input/output berubah (breaking) | Tambah fitur wajib baru | `2.0.0` |
| **MINOR** — retrain dengan data/arsitektur baru, API sama | Retrain bulanan, ganti backbone | `1.3.0` |
| **PATCH** — perbaikan kecil tanpa perubahan perilaku berarti | Ubah threshold, fix preprocessing bug | `1.3.1` |

Simpan versi semantik sebagai **tag** di registry, berdampingan dengan versi numerik otomatis.

---

# Tingkat Reproducibility

| Level | Yang dijamin | Kebutuhan |
|-------|--------------|-----------|
| **L0 — Tidak ada** | "Works on my machine" | — |
| **L1 — Code** | Kode yang sama | Git commit |
| **L2 — Code + Config** | Hyperparameter sama | Tracker (params) |
| **L3 — + Data** | Data identik | DVC / data hash |
| **L4 — + Environment** | Library & OS identik | Docker / conda lock |
| **L5 — Bit-exact** | Hasil numerik identik | Seed + deterministic ops + hardware sama |

> Target realistis kebanyakan tim: **L4**, dengan L5 untuk kebutuhan audit tertentu.

---

<!-- _class: divider -->

# 7. Tools for Experiment Tracking

---

# Evolusi Cara Tracking

| Generasi | Cara | Masalah |
|----------|------|---------|
| **1. Manual** | Catatan kertas, nama file, spreadsheet | Error-prone, tidak scalable, tidak sinkron dengan kode |
| **2. Logging lokal** | `print`, CSV, TensorBoard per folder | Sulit dibandingkan lintas run & lintas orang |
| **3. Experiment tracker** | MLflow, W&B, Neptune, Comet | Terpusat, dapat di-query, visual, kolaboratif |
| **4. Platform terintegrasi** | Tracker + registry + pipeline + monitoring (Vertex AI, SageMaker, Databricks, Snowflake ML) | Lebih kompleks, potensi *vendor lock-in* |

---

<!-- _class: small -->

# Lanskap Tools

| Tool | Lisensi / Hosting | Kekuatan | Catatan |
|------|-------------------|----------|---------|
| **MLflow** | Open source (Apache 2.0), self-host / managed | Tracking + Models + Registry; framework-agnostic; de facto standar | UI lebih sederhana |
| **Weights & Biases** | SaaS (free tier akademik), self-host enterprise | Visualisasi kaya, Sweeps, Reports, kolaborasi | Data di cloud vendor |
| **Neptune.ai** | SaaS | Metadata store fleksibel, skala besar | Komersial |
| **Comet ML** | SaaS / on-prem | Experiment + production monitoring | Komersial |
| **ClearML** | Open source + SaaS | Tracking + orchestration + data mgmt | Setup lebih berat |
| **DVC / DVC Experiments** | Open source | Git-native, versioning data & eksperimen | Visualisasi via VS Code / Studio |
| **TensorBoard** | Open source | Visualisasi training DL | Bukan tracker lengkap; tanpa registry |
| **Aim** | Open source | Ringan, UI cepat untuk banyak run | Ekosistem lebih kecil |

---

# Kriteria Memilih Tool

1. **Integrasi framework** — PyTorch, TensorFlow/Keras, scikit-learn, XGBoost, HuggingFace?
2. **Hosting & data governance** — boleh data/metadata keluar dari infrastruktur sendiri?
3. **Skalabilitas** — ribuan run, metrik per step, artifact besar?
4. **Kolaborasi** — multi-user, akses kontrol, reports/dashboard?
5. **Model registry & deployment** — terhubung ke CI/CD dan serving?
6. **Biaya & lisensi** — open source vs SaaS per-seat.
7. **API & query** — bisa mencari run secara programatik (mis. "run dengan F1 > 0.9")?

> Untuk perkuliahan & tim kecil: **MLflow (self-host)** atau **W&B (free academic)** adalah titik awal yang baik.

---

# Referensi

1. ml-ops.org — *MLOps Principles*. https://ml-ops.org/content/mlops-principles
2. S. Soni — *A Practical Guide to Experiment Tracking in MLOps*, Medium. https://medium.com/@sachinsoni600517/a-practical-guide-to-experiment-tracking-in-mlops-14777cfc3724
3. Diametral — *MLOps: Why Data and Model Experiment Tracking is Important*. https://diametral.com/en/articles/mlops-why-data-and-model-experiment-tracking-is-important
4. B. Wilson — *DevOps & MLOps* (LinkedIn post). https://www.linkedin.com/posts/bibinwilson_devops-mlops-share-7484966746697895936-ex0x/
5. Snowflake — *Experiment Tracking*. https://www.snowflake.com/en/artificial-intelligence/machine-learning/model-evaluation/experiment-tracking/


---

# Referensi

6. trail-ml — *First Steps in Experiment Tracking*. https://www.trail-ml.com/blog/first-steps-experiment-tracking
7. Nazmi — *MLOps Experiment Tracking with MLflow*. https://nazmi.tech/blog/mlops-experiment-tracking-with-mlflow
8. MLflow Documentation. https://mlflow.org/docs/latest/
9. Google Cloud — *MLOps: Continuous delivery and automation pipelines in machine learning*.
10. Bergstra, J. & Bengio, Y. (2012). *Random Search for Hyper-Parameter Optimization*. JMLR 13.

---

<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _header: '' -->
<!-- _footer: '' -->

# Terima Kasih

### Diskusi & Tanya Jawab

> *"If you can't reproduce it, you can't trust it — and you can't ship it."*


---

# Form Pengumpulan Tugas
### Link Google Form
https://forms.gle/CKYGBesLJgCbwjJt7