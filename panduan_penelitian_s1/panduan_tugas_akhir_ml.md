---
marp: true
theme: default
paginate: true
size: 16:9
math: mathjax
header: 'Panduan Tugas Akhir Penelitian Machine Learning & Deep Learning'
footer: 'Ahmad Luky Ramdani · Sains Data ITERA'
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
  section.lead blockquote { background: rgba(255,255,255,.12); color: #fff; border-left-color: #fff; }
  section.divider { background: #0f172a; color: #fff; justify-content: center; }
  section.divider h1 { color: #38bdf8; border: none; font-size: 2em; }
  section.divider p { color: #cbd5e1; }
  section.divider strong { color: #38bdf8; }
  section.lead em, section.lead blockquote strong { color: #fff; }
  section.small { font-size: 21px; }
  section.tiny { font-size: 18px; }
  section.two { column-count: 2; column-gap: 48px; }
  section.two h1 { column-span: all; }
  section.two blockquote { column-span: all; }
  section.two h3 ~ h3 { break-before: column; }
---

<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _header: '' -->
<!-- _footer: '' -->

# Panduan Tugas Akhir: Penelitian Machine Learning & Deep Learning

> Dari ide hingga sidang — menyusun skripsi yang **terukur, reproducible, dan dapat dipertanggungjawabkan**

Untuk Mahasiswa dengan Pembimbing · Ahmad Luky Ramdani · Program Studi Sains Data · ITERA

---

# Agenda

| # | Topik |
|---|-------|
| 0 | **Gambaran umum** — alur tugas akhir & karakter penelitian ML/DL |
| 1 | **Bab 1 Pendahuluan** — latar belakang, masalah, premis, hipotesis, tujuan, batasan |
| 2 | **Bab 2 Tinjauan Pustaka** — state of the art & *research gap* |
| 3 | **Bab 3 Metodologi** — data, model, eksperimen, evaluasi |
| 4 | **Bab 4 Hasil & Pembahasan** — menyajikan dan menafsirkan hasil |
| 5 | **Bab 5 Kesimpulan & Saran** |
| 6 | **Manajemen penelitian** — jadwal, bimbingan, tools, etika, checklist |

<br/>

> Contoh judul skripsi: **"Klasifikasi Penyakit Daun Padi Berbasis Citra Menggunakan Transfer Learning"**.

---

<!-- _class: divider -->

# 0. Gambaran Umum

Apa yang membuat skripsi ML/DL berbeda?

---

# Skripsi ML/DL = Penelitian Eksperimental

Skripsi ML/DL **bukan** "membuat aplikasi yang memakai model", melainkan **menjawab pertanyaan penelitian melalui eksperimen terkontrol**.

| Bukan ini | Melainkan ini |
|-----------|---------------|
| "Membangun sistem deteksi penyakit padi" | "Seberapa besar transfer learning meningkatkan F1 dibanding CNN dari awal pada data terbatas?" |
| Hanya melaporkan "akurasi 98%" | Membandingkan dengan **baseline**, menjelaskan **mengapa**, dan menguji **signifikansi** |
| Satu kali *training* | Beberapa *seed*, *cross-validation*, *ablation* |
| Kode di laptop pribadi | Kode, data, dan konfigurasi **berversi & dapat diulang** |

<br/>

> Kontribusi skripsi S1 tidak harus metode baru. Cukup: **penerapan yang tepat + perbandingan yang adil + analisis yang jujur** pada masalah/data yang relevan.

---

# Alur Besar Tugas Akhir

| Tahap | Keluaran | Bab |
|-------|----------|-----|
| 1. Eksplorasi topik & literatur | Daftar 20–40 paper, peta *research gap* | 1, 2 |
| 2. Proposal | Rumusan masalah, hipotesis, rancangan eksperimen | 1–3 |
| 3. Pengumpulan & persiapan data | Dataset berversi, laporan EDA | 3 |
| 4. Baseline | Model sederhana + angka acuan | 3, 4 |
| 5. Eksperimen utama | Hasil model usulan, tuning, ablation | 4 |
| 6. Analisis | Uji statistik, *error analysis*, interpretasi | 4 |
| 7. Penulisan & sidang | Naskah lengkap, slide, kode & data terarsip | 1–5 |

<br/>

> Tulis **sambil** bereksperimen — jangan menunggu semua eksperimen selesai baru menulis.

---

# Tipe Kontribusi yang Layak untuk S1

| Tipe | Contoh | Catatan |
|------|--------|---------|
| **Studi komparatif** | Membandingkan CNN, ResNet, EfficientNet, ViT pada citra daun padi | Paling umum; wajib adil (setting sama) |
| **Penerapan pada domain/data baru** | IndoBERT untuk ulasan aplikasi pemerintah daerah | Nilai pada **dataset & konteks lokal** |
| **Pembuatan dataset** | Korpus beranotasi bahasa Lampung | Wajib ukur kualitas anotasi (Cohen's κ) |
| **Modifikasi/perbaikan kecil** | Menambahkan *attention* atau augmentasi khusus | Butuh *ablation study* |
| **Analisis/interpretabilitas** | Mengapa model gagal pada kelas tertentu (Grad-CAM, SHAP) | Fokus pada *insight* |
| **Efisiensi** | Kuantisasi model agar jalan di HP petani | Ukur akurasi **dan** latensi/ukuran |

---

<!-- _class: divider -->

# Bab 1. Pendahuluan

Latar belakang · Rumusan masalah (masalah, premis, hipotesis) · Tujuan · Batasan

---

# Struktur Bab 1

| Subbab | Pertanyaan yang dijawab |
|--------|-------------------------|
| **A. Latar Belakang** | Mengapa masalah ini penting? Apa yang sudah dilakukan? Apa yang belum? |
|       | *(jangan ada kalimat atau opini pribadi, tapi harus berdasarkan paper)* |
| **B. Rumusan Masalah** | *di dalamnya terdapat masalah penelitian, premis dan hipotesis*|
| B.1 Masalah penelitian | Pertanyaan **spesifik** apa yang ingin dijawab? |
| B.2 Premis | Fakta/temuan terdahulu apa yang menjadi **pijakan**? *(bersumber dari paper)*|
| B.3 Hipotesis | **Dugaan sementara** apa yang akan diuji? |
| **C. Tujuan Penelitian** | Apa yang akan dihasilkan untuk menjawab masalah? |
| **D. Batasan Penelitian** | Apa yang **tidak** dicakup, dan mengapa? |

<br/>

> Bab 1 adalah "kontrak" penelitian: semua yang dijanjikan di sini **harus terjawab** di Bab 4 dan 5.

---

# A. Latar Belakang

1. **Konteks luas** — masalah nyata + data/angka. *"Padi adalah makanan pokok…; penyakit blas dan hawar daun menyebabkan kehilangan hasil hingga X% (sumber)."*
2. **Masalah praktis** — *"Identifikasi manual oleh penyuluh lambat dan jumlah penyuluh terbatas."*
3. **Peluang solusi** — *"Deep learning telah berhasil pada klasifikasi citra tanaman (Mohanty dkk., 2016)."*
4. **Celah (*gap*)** — *"Namun, sebagian besar studi memakai citra laboratorium berlatar seragam; kinerja pada citra lapangan dengan data terbatas belum banyak dikaji."*
5. **Usulan** — *"Penelitian ini mengkaji transfer learning untuk citra lapangan…"*

<br/>

> Setiap klaim di latar belakang **wajib bersitasi** (jurnal/data resmi), bukan opini.

---


# Kesalahan Umum di Latar Belakang

| ✗ Hindari | ✓ Lebih baik |
|-----------|--------------|
| "Di era revolusi industri 4.0 yang semakin canggih…" | Langsung ke masalah konkret + angka |
| "Deep learning adalah metode terbaik" | "Deep learning menunjukkan kinerja tinggi pada … (sitasi)" |
| Memilih metode dulu, mencari masalah belakangan | Masalah → kebutuhan → pemilihan metode yang beralasan |
| Tidak menyebut penelitian terdahulu | Ringkas 3–5 studi paling dekat + kelemahannya |
| *Gap* tidak jelas ("belum ada yang meneliti di ITERA") | *Gap* metodologis/data: kondisi data, bahasa, skala, metrik |
| Paragraf panjang tanpa alur | Satu paragraf = satu gagasan; ikuti pola corong |

<br/>

> Uji cepat: setelah membaca latar belakang, pembaca harus bisa menebak **rumusan masalah** Anda.

---

# B.1 Masalah Penelitian

Rumusan masalah ML/DL yang baik bersifat **spesifik, terukur, dan dapat dijawab dengan eksperimen**.

| ✗ Kabur/Bias | ✓ Spesifik & terukur |
|---------|----------------------|
| Bagaimana membuat sistem deteksi penyakit padi? | Bagaimana kinerja (F1-macro) transfer learning EfficientNet-B0 dibandingkan CNN yang dilatih dari awal pada citra lapangan daun padi? |
| Apakah deep learning akurat? | Bagaimana pengaruh augmentasi data terhadap kinerja model ketika jumlah data latih hanya 100 citra per kelas? |
| Bagaimana menerapkan BERT? | Kelas penyakit apa yang paling sering salah diklasifikasikan, dan apa penyebabnya? |

<br/>

> Rumus praktis: **[pengaruh/perbandingan] + [variabel/metode] + [metrik] + [kondisi data/konteks]**.

---

# B.2 Premis

**Premis** = pernyataan yang **sudah diterima kebenarannya** (didukung literatur/fakta), menjadi pijakan logis menuju hipotesis.

Contoh:

- **P1.** CNN yang dilatih pada ImageNet mempelajari fitur visual umum (tepi, tekstur, bentuk) yang dapat dipindahkan ke domain lain *(Yosinski dkk., 2014)*.
- **P2.** Transfer learning meningkatkan kinerja ketika data latih domain target terbatas *(Pan & Yang, 2010)*.
- **P3.** Gejala penyakit daun padi terutama dibedakan oleh **pola tekstur dan warna** bercak.
- **P4.** Dataset citra lapangan yang tersedia relatif kecil (< 1.000 citra per kelas).

> Premis bukan hipotesis: premis **tidak diuji** dalam penelitian Anda, tetapi **dikutip** dari bukti yang sudah ada.

---

# B.3 Hipotesis

Hipotesis = **dugaan yang dapat diuji** dan diturunkan dari premis. Dalam ML/DL nyatakan dalam **metrik** dan **pembanding**.

**Dari P1 + P2 + P4 →**

- **H₁:** Model EfficientNet-B0 dengan transfer learning menghasilkan F1-macro **lebih tinggi secara signifikan** dibanding CNN yang dilatih dari awal pada data citra lapangan daun padi.
- **H₀:** Tidak ada perbedaan F1-macro yang signifikan antara kedua pendekatan.

$$
H_0: \mu_{F1}^{\text{TL}} = \mu_{F1}^{\text{scratch}} \qquad H_1: \mu_{F1}^{\text{TL}} > \mu_{F1}^{\text{scratch}}
$$

<br/>

> Hipotesis menentukan **desain eksperimen**: apa yang dibandingkan, metrik apa, berapa kali diulang, dan uji statistik apa (dibahas di Bab 3).

---


# Keterkaitan Masalah → Premis → Hipotesis → Tujuan

| Masalah (B.1) | Premis (B.2) | Hipotesis (B.3) | Tujuan (C) | Dijawab di |
|---------------|--------------|-----------------|------------|------------|
| RM1: Bagaimana kinerja TL vs CNN dari awal? | P1, P2, P4 | H1: TL > scratch (F1-macro, signifikan) | T1: Mengukur & membandingkan F1-macro keduanya | Bab 4.2, uji Wilcoxon |
| RM2: Bagaimana pengaruh augmentasi pada data terbatas? | P2, P4 | H2: Augmentasi menaikkan F1 pada 100 citra/kelas | T2: Menganalisis efek augmentasi lewat ablation | Bab 4.3 |
| RM3: Kelas apa yang paling sulit & mengapa? | P3 | — (eksploratif) | T3: Menganalisis kesalahan dengan confusion matrix & Grad-CAM | Bab 4.4 |

<br/>

> Gunakan **tabel keterlacakan** seperti ini di catatan bimbingan. Setiap baris harus muncul lagi sebagai **satu poin kesimpulan** di Bab 5.

---

# C. Tujuan Penelitian

- Tujuan adalah **cermin** rumusan masalah: jumlahnya sama, urutannya sama.
- Gunakan kata kerja operasional: *mengukur, membandingkan, menganalisis, mengevaluasi, membangun*.

| Rumusan Masalah | Tujuan |
|-----------------|--------|
| Bagaimana kinerja TL dibanding CNN dari awal…? | **Membandingkan** F1-macro TL EfficientNet-B0 dan CNN dari awal… |
| Bagaimana pengaruh augmentasi…? | **Menganalisis** pengaruh augmentasi terhadap F1-macro… |
| Kelas apa yang paling sulit…? | **Mengidentifikasi** pola kesalahan klasifikasi beserta penyebabnya… |

<br/>

Opsional: **Manfaat penelitian** — teoretis (bukti empiris), praktis (alat bantu penyuluh), dan dataset/kode terbuka.

---

# D. Batasan Penelitian

Batasan membuat penelitian **dapat diselesaikan** dalam 1–2 semester dan menjelaskan **lingkup klaim**.

| Aspek | Contoh batasan |
|-------|----------------|
| **Data** | Citra dari dataset publik X + 300 citra lapangan Lampung Selatan; 4 kelas (blas, hawar, tungro, sehat) |
| **Tugas** | Klasifikasi citra tunggal; **tidak** termasuk deteksi lokasi bercak (object detection) atau tingkat keparahan |
| **Model** | CNN sederhana (baseline), ResNet-50, EfficientNet-B0; **tidak** membangun arsitektur baru |
| **Sumber daya** | Pelatihan dengan GPU Google Colab/Kaggle (T4, 16 GB) |
| **Evaluasi** | Offline pada test set; **tidak** diuji langsung oleh petani di lapangan |
| **Bahasa/wilayah** | (untuk NLP) teks berbahasa Indonesia dari platform X periode Jan–Jun 2026 |

> Batasan ≠ kelemahan yang ditutupi. Batasan **dipilih dengan alasan**; kelemahan yang ditemukan kemudian ditulis di Bab 5 (saran).

---

<!-- _class: divider -->

# Bab 2. Tinjauan Pustaka

State of the art · Landasan teori · Research gap

---

# Isi Bab 2

### 2.1 Penelitian Terkait (*state of the art*)
Studi terdahulu yang **paling dekat** dengan topik — dibandingkan secara kritis, bukan diringkas satu per satu.

### 2.2 Landasan Teori
Konsep yang **dipakai** di Bab 3: CNN, transfer learning, fungsi loss, optimizer, metrik evaluasi, uji statistik. Sertakan persamaan dan notasi yang konsisten.

<br/>

> Aturan praktis: **jangan** menulis teori yang tidak dipakai. Jika Bab 3 tidak memakai SVM, SVM tidak perlu dijelaskan panjang di Bab 2.

---

# Mencari Literatur yang Tepat

| Sumber | Kegunaan |
|--------|----------|
| **Google Scholar**, Semantic Scholar | Pencarian umum, jejak sitasi (*cited by*) |
| **Papers with Code** | Benchmark, kode, dataset, SOTA per tugas |
| **arXiv** | Preprint terbaru (cek apakah sudah terbit di jurnal/konferensi) |
| **IEEE Xplore, ScienceDirect, ACM DL, SpringerLink** | Jurnal & prosiding bereputasi |
| **SINTA, Garuda** | Penelitian berkonteks Indonesia |
| **Connected Papers, ResearchRabbit** | Peta keterkaitan paper |

<br/>

Strategi: mulai dari **1–2 survei/review terbaru** → telusuri referensinya (*backward*) dan yang mengutipnya (*forward*). Kelola dengan **Zotero/Mendeley** sejak hari pertama.

> Utamakan publikasi **5 tahun terakhir** + paper fondasional (mis. ResNet, Transformer). Hindari blog/Medium sebagai rujukan utama.

---

<!-- _class: tiny -->

# Matriks Literatur (*Literature Matrix*)

Bandingkan studi terdahulu dalam **satu tabel** — dari sini *research gap* terlihat. Kolom yang ditampilkan sesuaikan dengan fotmat prodi

| Penulis (tahun) | Data | Kondisi citra | Metode | Metrik | Hasil | Keterbatasan |
|-----------------|------|---------------|--------|--------|-------|--------------|
| Mohanty dkk. (2016) | PlantVillage, 54K citra, 38 kelas | Laboratorium, latar seragam | AlexNet, GoogLeNet (TL) | Akurasi | 99,35% | Turun drastis pada citra lapangan |
| Studi B (2021) | Daun padi, 5.932 citra | Campuran | VGG16, ResNet50 | Akurasi, F1 | F1 0,95 | Tanpa uji signifikansi; 1 kali run |
| Studi C (2023) | Daun padi lapangan, 1.200 citra | Lapangan | CNN custom | Akurasi | 88% | Tidak dibandingkan dengan TL |
| Studi D (2024) | Daun padi | Lapangan | ViT | F1 | 0,91 | Butuh data besar; biaya komputasi tinggi |
| **Penelitian ini** | Publik + 300 citra Lampung | **Lapangan, data terbatas** | **CNN vs ResNet vs EfficientNet** | **F1-macro, uji statistik** | — | — |

*Baris B–D adalah ilustrasi format; isi dengan paper nyata hasil penelusuran Anda.*

<br/>

> **Gap** yang muncul: data lapangan terbatas + perbandingan yang adil + uji signifikansi + analisis kesalahan.

---

# Menulis Penelitian Terkait secara Kritis

✗ **Gaya daftar** (sering ditemui):
> *"Mohanty (2016) melakukan penelitian … hasilnya 99%. Kemudian Studi B (2021) melakukan … hasilnya 95%. Selanjutnya Studi C …"*

✓ **Gaya sintesis** (dikelompokkan berdasarkan tema):
> *"Sebagian besar studi klasifikasi penyakit tanaman memperoleh akurasi di atas 95% (Mohanty dkk., 2016; B, 2021), namun dievaluasi pada citra berlatar seragam. Ketika diuji pada citra lapangan, kinerja menurun tajam (Mohanty dkk., 2016). Studi yang memakai citra lapangan (C, 2023) belum membandingkan dengan transfer learning, sementara pendekatan ViT (D, 2024) membutuhkan data besar…"*

> Paragraf yang baik **membandingkan, mengelompokkan, dan menilai** — lalu berakhir pada **celah** yang diisi penelitian Anda.

---

# Landasan Teori: Tulis yang Dipakai, dengan Notasi Konsisten

Contoh — fungsi loss *cross-entropy* untuk klasifikasi $K$ kelas:

$$
\mathcal{L} = -\frac{1}{N}\sum_{i=1}^{N}\sum_{k=1}^{K} y_{ik}\,\log \hat{y}_{ik}, \qquad \hat{y}_{ik} = \frac{e^{z_{ik}}}{\sum_{j=1}^{K} e^{z_{ij}}}
$$

Contoh — F1-macro (rata-rata F1 tiap kelas, adil untuk data tidak seimbang):

$$
\text{F1}_k = \frac{2\,P_k R_k}{P_k + R_k}, \qquad \text{F1}_{\text{macro}} = \frac{1}{K}\sum_{k=1}^{K}\text{F1}_k
$$

- Setiap simbol **didefinisikan** saat pertama muncul.
- Gambar arsitektur: buat ulang sendiri atau cantumkan sumber ("diadaptasi dari …").

---

<!-- _class: divider -->

# Bab 3. Metodologi Penelitian

Rancangan yang membuat hasil **valid dan dapat diulang**

---

<!-- _class: small -->

# Tahapan Penelitian (Diagram Alir)

| No | Tahap | Keluaran | Subbab |
|----|-------|----------|--------|
| 1 | Studi literatur & perumusan masalah | Hipotesis, rancangan eksperimen | 3.1 |
| 2 | Pengumpulan data | Dataset mentah + dokumentasi sumber & lisensi | 3.2 |
| 3 | Eksplorasi data (EDA) | Distribusi kelas, kualitas, contoh citra | 3.3 |
| 4 | Pra-pemrosesan & pembagian data | Train / validation / test **terkunci** | 3.4 |
| 5 | Pemodelan | Baseline + model usulan | 3.5 |
| 6 | Skenario eksperimen | Daftar run (perbandingan, tuning, ablation) | 3.6 |
| 7 | Evaluasi | Metrik + uji statistik + error analysis | 3.7 |
| 8 | Lingkungan & reproducibility | Spesifikasi HW/SW, seed, tracking | 3.8 |

<br/>

> Di naskah: gambarkan sebagai **flowchart**; setiap kotak dijelaskan dalam satu subbab. Pembaca lain harus bisa **mengulang** penelitian hanya dari Bab 3.

---

<!-- _class: small -->

# 3.2 Pengumpulan Data

| Hal | Yang wajib dijelaskan |
|-----|-----------------------|
| **Sumber** | Nama dataset publik + sitasi/URL, atau prosedur akuisisi sendiri (alat, lokasi, waktu) |
| **Lisensi & izin** | Lisensi dataset (CC-BY, dsb.), izin pengambilan data, persetujuan subjek (*informed consent*) bila melibatkan manusia |
| **Ukuran & struktur** | Jumlah sampel, kelas, resolusi/panjang teks, format |
| **Pelabelan** | Siapa pelabel (pakar? mahasiswa?), panduan anotasi, jumlah anotator |
| **Kualitas label** | Kesepakatan antar-anotator, mis. **Cohen's κ**: $\kappa = \dfrac{p_o - p_e}{1 - p_e}$ (κ > 0,6 cukup baik) |
| **Privasi** | Anonimisasi data pribadi (nama, NIK, wajah, nomor HP) |

> Data adalah **kontribusi besar** skripsi ML. Dokumentasikan dengan *datasheet* sederhana (Gebru dkk., 2021): motivasi, komposisi, proses pengumpulan, penggunaan yang disarankan.

---

<!-- _class: small -->

# 3.3 Exploratory Data Analysis (EDA)

Tujuan EDA di skripsi: **mengenali sifat data** yang memengaruhi pilihan metode.

- **Distribusi kelas** — seimbang atau tidak? → menentukan metrik (F1-macro, bukan akurasi) dan strategi (*class weight*, *oversampling*).
- **Kualitas data** — duplikat, citra blur/rusak, label salah, nilai hilang, *outlier*.
- **Karakteristik** — ukuran citra, panjang teks, korelasi fitur (tabular).
- **Potensi kebocoran** — citra yang sama/hampir sama di dua kelas atau dua split; foto beruntun dari daun yang sama.

| Kelas | Jumlah | % |
|-------|-------:|--:|
| Blas | 420 | 35,0 |
| Hawar daun | 360 | 30,0 |
| Tungro | 180 | 15,0 |
| Sehat | 240 | 20,0 |

*Contoh tabel distribusi (ilustrasi). Kelas tungro minoritas → perhatikan recall-nya.*

---

<!-- _class: small -->

# 3.4 Pembagian Data & Mencegah *Data Leakage*

**Aturan emas:** test set **disisihkan di awal**, tidak disentuh sampai evaluasi akhir.

| Skema | Kapan dipakai |
|-------|---------------|
| **Hold-out** 70/15/15 (stratified) | Data cukup besar (ribuan+) |
| **Stratified k-fold CV** (k = 5 atau 10) + test terpisah | Data kecil; ingin estimasi variansi |
| **Group split** (per daun/pasien/pengguna) | Ada beberapa sampel dari sumber yang sama |
| **Time-based split** | Data deret waktu / berurutan |

**Bentuk kebocoran yang sering terjadi:**
- Normalisasi/scaler/TF-IDF di-*fit* pada **seluruh** data sebelum split → *fit* hanya pada train.
- Augmentasi dilakukan **sebelum** split → duplikat hasil augmentasi bocor ke test.
- Foto beruntun dari **daun yang sama** tersebar di train dan test → gunakan *group split*.
- Memilih hyperparameter berdasarkan nilai **test** → gunakan validation.

> Kebocoran data adalah penyebab paling umum hasil "terlalu bagus untuk jadi kenyataan" (Kapoor & Narayanan, 2023).

---

# 3.4 Pra-pemrosesan: Tulis Secara Rinci & Berurutan

| Langkah | Citra (contoh) | Teks (contoh) | Tabular (contoh) |
|---------|----------------|---------------|------------------|
| Pembersihan | Hapus duplikat/blur | Hapus URL, emoji, duplikat | Tangani nilai hilang |
| Normalisasi | Resize 224×224, normalisasi mean/std ImageNet | *Case folding*, normalisasi slang | Standardisasi z-score |
| Representasi | Tensor RGB | Tokenisasi WordPiece (IndoBERT) | *One-hot* / *target encoding* |
| Augmentasi (train saja) | Flip, rotasi ±20°, *color jitter* | *Back-translation*, EDA | SMOTE (hanya di train fold) |

<br/>

> Tulis parameter **persis** (ukuran, rentang rotasi, probabilitas). "Dilakukan augmentasi" saja **tidak cukup** untuk direproduksi.

---

<!-- _class: small -->

# 3.5 Pemodelan: Baseline Itu Wajib

Tanpa baseline, angka "akurasi 95%" **tidak bermakna** — 95% dibanding apa?

| Tingkat | Contoh (citra) | Contoh (teks) | Fungsi |
|---------|----------------|---------------|--------|
| **Trivial** | Tebak kelas mayoritas | Tebak kelas mayoritas | Batas bawah (akurasi 35% pada contoh EDA) |
| **Klasik** | Fitur warna/tekstur (GLCM) + SVM/Random Forest | TF-IDF + Logistic Regression | Apakah DL memang diperlukan? |
| **DL sederhana** | CNN 3–4 layer dari awal | BiLSTM | Pembanding untuk transfer learning |
| **Usulan** | EfficientNet-B0 / ResNet-50 (TL) | IndoBERT *fine-tuning* | Model yang diuji hipotesisnya |
| **SOTA (opsional)** | ViT, ConvNeXt | XLM-R large | Posisi terhadap batas atas |

<br/>

> Jelaskan setiap model: arsitektur, jumlah parameter, bobot awal (*pretrained* dari mana), layer yang dibekukan/di-*fine-tune*, fungsi loss, optimizer.

---

<!-- _class: small -->

# 3.6 Skenario Eksperimen

Turunkan langsung dari hipotesis. **Ubah satu faktor pada satu waktu**; faktor lain dikunci.

| Skenario | Faktor yang diubah | Yang dikunci | Menjawab |
|----------|--------------------|--------------|----------|
| S1 — Perbandingan model | CNN-scratch vs ResNet-50 vs EfficientNet-B0 | Data split, augmentasi, epoch maks, early stopping | H1 / RM1 |
| S2 — Ukuran data | 25%, 50%, 100% data latih | Model terbaik S1 | RM1 (data terbatas) |
| S3 — Ablation augmentasi | Dengan vs tanpa augmentasi; jenis augmentasi | Model & data | H2 / RM2 |
| S4 — Tuning | lr ∈ {1e-4, 3e-4, 1e-3}, batch ∈ {16, 32} | Pada validation set saja | Konfigurasi akhir |

<br/>

- Setiap konfigurasi dijalankan dengan **≥ 3-5 seed** (atau 5-fold CV) → laporkan **mean ± std**.
- Hitung **anggaran komputasi**: 3 model × 5 seed × ±20 menit ≈ 5 jam GPU untuk S1 saja. Rencanakan!

---

<!-- _class: small -->

# 3.6 Tuning Hyperparameter yang Adil

| Prinsip | Penjelasan |
|---------|------------|
| **Anggaran sama** | Setiap model mendapat jumlah *trial* tuning yang setara — jangan tuning model usulan 50 kali tetapi baseline 1 kali |
| **Hanya di validation** | Test set tidak dipakai untuk memilih konfigurasi |
| **Ruang pencarian ditulis** | Cantumkan rentang/nilai yang dicoba + metode (grid, random, Bayesian/Optuna) |
| **Early stopping** | Pantau `val_loss`, *patience* mis. 10 epoch; simpan bobot terbaik |
| **Konfigurasi akhir dilaporkan** | Tabel hyperparameter final setiap model (lampiran) |

<br/>

```text
Ruang pencarian (contoh):
  learning_rate : log-uniform [1e-5, 1e-2]
  batch_size    : {16, 32, 64}
  dropout       : uniform [0.0, 0.5]
  optimizer     : {AdamW}, weight_decay = 1e-4
  metode        : Random search, 30 trial per model, metrik = val F1-macro
```

---

<!-- _class: small -->

# 3.7 Memilih Metrik Evaluasi

| Tugas | Metrik utama | Metrik pendukung |
|-------|--------------|------------------|
| Klasifikasi seimbang | Akurasi, F1-macro | Precision, recall per kelas, confusion matrix |
| Klasifikasi **tidak seimbang** | **F1-macro**, PR-AUC, *balanced accuracy* | Recall kelas minoritas |
| Diagnosis (biaya FN tinggi) | **Recall/sensitivity** | Specificity, ROC-AUC |
| Regresi | RMSE, MAE | $R^2$, plot residual |
| Deteksi objek | mAP@0,5, mAP@0,5:0,95 | Precision–recall per kelas |
| Segmentasi | IoU / Dice | Pixel accuracy |
| Generasi teks / ringkasan | ROUGE, BLEU, BERTScore | Evaluasi manusia |
| Clustering | Silhouette, ARI/NMI (bila ada label) | Interpretasi klaster |

<br/>

> Tetapkan **satu metrik utama sebelum eksperimen** (di proposal). Mengganti metrik setelah melihat hasil = *metric shopping*.
> Jika relevan, laporkan juga **efisiensi**: jumlah parameter, waktu inferensi, ukuran model.

---

<!-- _class: small -->

# 3.7 Uji Statistik: "Lebih Tinggi" Belum Tentu "Lebih Baik"

| Situasi | Uji yang disarankan |
|---------|---------------------|
| 2 model, skor dari k-fold/seed yang sama (berpasangan) | **Wilcoxon signed-rank** (non-parametrik) atau *paired t-test* |
| 2 model, satu test set, prediksi per sampel | **McNemar test** |
| ≥ 3 model pada beberapa fold/dataset | **Friedman** + post-hoc **Nemenyi** (Demšar, 2006) |
| Ketidakpastian satu metrik | **Bootstrap 95% CI** |

<br/>

Contoh hasil 5-fold (ilustrasi):

| Fold | 1 | 2 | 3 | 4 | 5 | Mean ± Std |
|------|---|---|---|---|---|-----------|
| CNN-scratch | 0,781 | 0,764 | 0,792 | 0,770 | 0,758 | 0,773 ± 0,014 |
| EfficientNet-B0 (TL) | 0,872 | 0,861 | 0,889 | 0,866 | 0,853 | 0,868 ± 0,014 |

<br/>

TL lebih tinggi di **kelima fold** → Wilcoxon satu sisi, $W^+ = 15$, $p = 1/2^5 = 0{,}031 < 0{,}05$ → **H₀ ditolak**.

> Catatan: dengan n = 5, nilai p terkecil yang mungkin adalah 0,031 — pertimbangkan 10-fold atau lebih banyak seed.

---

<!-- _class: small -->

# 3.8 Lingkungan & Reproducibility

| Komponen | Yang dicatat | Alat |
|----------|--------------|------|
| **Kode** | Repositori + *commit hash* untuk setiap hasil | Git, GitHub/GitLab |
| **Data** | Versi/hash dataset & berkas split | DVC, W&B Artifacts, simpan `split.csv` |
| **Konfigurasi** | Semua hyperparameter, termasuk seed | Berkas YAML, `wandb.config` |
| **Lingkungan** | Versi Python & library, CUDA, GPU | `requirements.txt` / `environment.yml`, Docker |
| **Eksperimen** | Metrik per epoch, artefak model, log | **Weights & Biases**, MLflow, TensorBoard |

<br/>

```python
import random, numpy as np, torch
def set_seed(seed: int = 42):
    random.seed(seed); np.random.seed(seed)
    torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
```

> Target minimal skripsi: orang lain dapat menjalankan `git clone` → `pip install -r requirements.txt` → `python train.py --config configs/s1_effnet.yaml` dan memperoleh hasil yang **mendekati** tabel di Bab 4.

---

<!-- _class: small -->

# Struktur Repositori yang Disarankan

```text
skripsi-padi/
├── README.md               # cara instalasi, menjalankan, dan mereproduksi tabel Bab 4
├── requirements.txt        # versi library terkunci
├── configs/                # satu YAML per skenario: s1_cnn.yaml, s1_effnet.yaml, ...
├── data/
│   ├── raw/                # TIDAK di-commit (gunakan DVC / tautan unduhan)
│   ├── processed/
│   └── splits/             # train.csv, val.csv, test.csv  → DI-COMMIT (kecil, penting)
├── notebooks/              # 01_eda.ipynb, 05_error_analysis.ipynb (eksplorasi saja)
├── src/
│   ├── data.py             # dataset, transform, augmentasi
│   ├── models.py           # definisi arsitektur
│   ├── train.py            # loop training + logging (wandb)
│   └── evaluate.py         # metrik, confusion matrix, uji statistik
├── results/                # tabel & gambar final untuk naskah
└── thesis/                 # naskah (LaTeX/Word) & slide sidang
```

> Notebook untuk **eksplorasi**; skrip `.py` + konfigurasi untuk **eksperimen resmi** yang hasilnya masuk naskah.

---

<!-- _class: divider -->

# Bab 4. Hasil dan Pembahasan

Hasil = **apa** yang terjadi · Pembahasan = **mengapa** dan **apa artinya**

---

# Struktur Bab 4

| Subbab | Isi |
|--------|-----|
| 4.1 Hasil eksplorasi & pra-pemrosesan data | Statistik akhir dataset, contoh hasil augmentasi |
| 4.2 Hasil skenario 1 — perbandingan model | Tabel utama + uji statistik → **jawab RM1/H1** |
| 4.3 Hasil skenario 2–3 — ukuran data & ablation | Grafik & tabel → **jawab RM2/H2** |
| 4.4 Analisis kesalahan & interpretabilitas | Confusion matrix, contoh salah, Grad-CAM → **jawab RM3** |
| 4.5 Pembahasan | Kaitkan dengan premis & penelitian terdahulu; keterbatasan |

<br/>

> Urutkan subbab **mengikuti rumusan masalah**, bukan mengikuti urutan Anda melakukan eksperimen.

---

<!-- _class: small -->

# Menyajikan Tabel Hasil Utama

**Tabel 4.2** Kinerja model pada test set (mean ± std dari 5 seed). **Tebal** = terbaik.

| Model | Param (juta) | Akurasi | F1-macro | Recall Tungro | Waktu inferensi (ms/citra) |
|-------|-------------:|--------:|---------:|--------------:|---------------------------:|
| Kelas mayoritas | — | 0,350 | 0,130 | 0,000 | — |
| GLCM + SVM | — | 0,712 ± 0,000 | 0,664 ± 0,000 | 0,51 | 3 |
| CNN-scratch | 1,2 | 0,801 ± 0,015 | 0,773 ± 0,014 | 0,62 | 4 |
| ResNet-50 (TL) | 23,5 | 0,889 ± 0,010 | 0,861 ± 0,012 | 0,78 | 18 |
| EfficientNet-B0 (TL) | 4,0 | **0,896 ± 0,009** | **0,868 ± 0,014** | **0,81** | 9 |

<br/>

*Angka ilustrasi.*

- Sertakan **baseline**, **variansi**, satuan, dan keterangan apakah dari validation atau test.
- Gunakan **angka penting yang konsisten** (3 desimal) dan desimal koma sesuai PUEBI bila naskah berbahasa Indonesia.

---

# Grafik yang Bercerita

| Pertanyaan | Grafik yang tepat |
|------------|-------------------|
| Apakah training stabil / overfitting? | **Learning curve** train vs val loss per epoch |
| Model mana lebih baik? | **Bar chart** dengan *error bar* (std atau 95% CI) |
| Bagaimana pengaruh ukuran data? | **Line chart** F1 vs % data latih per model |
| Kelas mana yang tertukar? | **Confusion matrix** (dinormalisasi per baris) |
| Trade-off kinerja vs biaya | **Scatter** F1 vs waktu inferensi / jumlah parameter |
| Ke mana model "melihat"? | **Grad-CAM** pada contoh benar & salah |

<br/>

> Setiap gambar: judul/keterangan lengkap, label sumbu + satuan, legenda, ukuran font terbaca, dan **dirujuk dan dibahas di teks** ("Gambar 4.3 menunjukkan…").

---

# Pembahasan: Dari Angka ke Makna

Pola **4 langkah** untuk setiap temuan:

1. **Nyatakan hasil** — *"EfficientNet-B0 mencapai F1-macro 0,868, lebih tinggi 0,095 dari CNN-scratch (Tabel 4.2); perbedaan signifikan (Wilcoxon, p = 0,031)."*
2. **Jelaskan mengapa** — *"Sejalan dengan P1–P2: fitur tekstur dari ImageNet dapat dipindahkan, sehingga model tidak perlu belajar dari 1.200 citra saja."*
3. **Bandingkan dengan literatur** — *"Hasil ini lebih rendah dari 99% pada Mohanty dkk. (2016) karena citra lapangan memiliki latar yang beragam, konsisten dengan penurunan kinerja yang juga mereka laporkan."*
4. **Implikasi & batasan** — *"Recall tungro (0,81) masih terendah; untuk penggunaan lapangan, kesalahan pada kelas ini perlu diwaspadai."*

> **Hipotesis harus dijawab eksplisit**: "H₁ **diterima**" atau "H₁ **tidak didukung** oleh data". Hasil negatif tetap kontribusi — laporkan dengan jujur.

---

<!-- _class: small -->

# Analisis Kesalahan (*Error Analysis*)

Nilai tambah besar skripsi: memahami **di mana dan mengapa** model gagal.

**Confusion matrix (dinormalisasi per baris, ilustrasi):**

| Aktual \ Prediksi | Blas | Hawar | Tungro | Sehat |
|-------------------|-----:|------:|-------:|------:|
| **Blas** | **0,91** | 0,06 | 0,02 | 0,01 |
| **Hawar** | 0,05 | **0,89** | 0,04 | 0,02 |
| **Tungro** | 0,03 | 0,11 | **0,81** | 0,05 |
| **Sehat** | 0,01 | 0,02 | 0,03 | **0,94** |

Langkah analisis:
1. Temukan pasangan kelas yang paling sering tertukar (**tungro → hawar**, 11%).
2. Ambil 20–30 contoh salah; kelompokkan penyebabnya: label keliru? citra buram? gejala mirip? pencahayaan?
3. Visualisasikan dengan **Grad-CAM**: apakah model melihat bercak, atau justru latar (tanah, tangan)?
4. Ubah temuan menjadi **saran** konkret (data tambahan kelas tungro, augmentasi warna, dsb.).

---

<!-- _class: small -->

# Ablation Study: Komponen Mana yang Berpengaruh?

**Tabel 4.4** Ablation pada EfficientNet-B0, 100 citra/kelas (val F1-macro, mean ± std, 5 seed — ilustrasi).

| Konfigurasi | Pretrained | Augmentasi | Class weight | F1-macro | Δ |
|-------------|:----------:|:----------:|:------------:|---------:|--:|
| Lengkap | ✓ | ✓ | ✓ | **0,842 ± 0,013** | — |
| − Pretrained | ✗ | ✓ | ✓ | 0,701 ± 0,021 | −0,141 |
| − Augmentasi | ✓ | ✗ | ✓ | 0,796 ± 0,018 | −0,046 |
| − Class weight | ✓ | ✓ | ✗ | 0,829 ± 0,012 | −0,013 |

<br/>

**Pembahasan:** bobot *pretrained* paling berpengaruh; augmentasi berpengaruh nyata pada data kecil (→ **H2 diterima** bila signifikan); *class weight* berpengaruh kecil.

> Ablation mengubah klaim "model kami bagus" menjadi "**komponen X** yang membuatnya bagus".

---

<!-- _class: divider -->

# Bab 5. Kesimpulan dan Saran

---

# Kesimpulan: Jawaban Langsung atas Rumusan Masalah

- Jumlah poin kesimpulan = jumlah rumusan masalah; **urutan sama**.
- Berisi **jawaban + angka kunci**, bukan ringkasan proses.
- **Tidak** memuat hal baru yang tidak dibahas di Bab 4.

<br/>

| ✗ Bukan kesimpulan | ✓ Kesimpulan |
|--------------------|--------------|
| "Penelitian ini telah berhasil membuat model deteksi penyakit padi menggunakan EfficientNet." | "1. Transfer learning EfficientNet-B0 menghasilkan F1-macro 0,868 ± 0,014, lebih tinggi secara signifikan dibanding CNN dari awal (0,773 ± 0,014; Wilcoxon p = 0,031), sehingga H₁ diterima." |
| "Augmentasi itu penting." | "2. Pada 100 citra/kelas, augmentasi meningkatkan F1-macro sebesar 0,046 …" |

---

# Saran: Konkret dan Berbasis Temuan

Saran yang baik **lahir dari keterbatasan dan hasil error analysis**, bukan daftar umum.

| ✗ Umum | ✓ Spesifik & beralasan |
|--------|------------------------|
| "Gunakan data yang lebih banyak." | "Tambah minimal 300 citra **tungro** lapangan karena 11% tungro salah diklasifikasikan sebagai hawar (Tabel 4.3)." |
| "Coba metode lain." | "Uji model deteksi objek (YOLO) agar bercak terlokalisasi, karena Grad-CAM menunjukkan model kadang memperhatikan latar." |
| "Kembangkan aplikasi." | "Evaluasi di lapangan bersama penyuluh untuk mengukur kinerja pada kamera HP berkualitas rendah." |

---

<!-- _class: divider -->

# 6. Manajemen Penelitian

Jadwal · Bimbingan · Tools · Etika · Checklist

---

<!-- _class: small -->

# Contoh Jadwal (2 Semester)

| Bulan | Kegiatan | Milestone bimbingan |
|-------|----------|---------------------|
| 1 | Eksplorasi topik, baca 20+ paper, matriks literatur | Topik & 3 kandidat rumusan masalah |
| 2 | Draf Bab 1–3, pilih dataset, EDA awal | **Seminar proposal** |
| 3 | Pipeline data + split terkunci + baseline | Tabel baseline |
| 4 | Eksperimen S1 (perbandingan model) | Hasil S1 + learning curves |
| 5 | Eksperimen S2–S4 (data, ablation, tuning) | Tabel ablation |
| 6 | Uji statistik, error analysis, Grad-CAM | Draf Bab 4 |
| 7 | Penulisan Bab 4–5, revisi Bab 1–3 | **Seminar hasil** |
| 8 | Revisi, cek plagiarisme, arsip kode & data, slide sidang | **Sidang** |

---

<!-- _class: small -->

# Tools yang Disarankan

| Kebutuhan | Tools |
|-----------|-------|
| Komputasi | Google Colab, Kaggle Notebooks (GPU gratis terbatas), server lab/prodi |
| Framework | PyTorch / TensorFlow-Keras, scikit-learn, HuggingFace Transformers, timm |
| Tracking eksperimen | **Weights & Biases**, MLflow, TensorBoard |
| Versi kode & data | Git + GitHub, DVC / W&B Artifacts |
| Anotasi data | Label Studio, CVAT, Roboflow |
| Uji statistik | `scipy.stats` (wilcoxon, friedmanchisquare), `scikit-posthocs`, `mlxtend` (McNemar) |
| Interpretabilitas | Grad-CAM (`pytorch-grad-cam`), SHAP, LIME |
| Referensi | Zotero / Mendeley (+ plugin Word/LaTeX) |
| Penulisan | LaTeX (Overleaf) atau Word dengan *styles* & *caption* otomatis |

---

<!-- _class: small -->

# Etika, Integritas, dan Penggunaan AI Generatif

| Aspek | Praktik yang benar |
|-------|--------------------|
| **Data pribadi** | Anonimisasi; patuhi UU PDP No. 27/2022; *informed consent* untuk data manusia |
| **Lisensi** | Patuhi lisensi dataset & model *pretrained*; cantumkan sitasi |
| **Bias & fairness** | Laporkan kinerja per subkelompok bila relevan (wilayah, gender, dialek) |
| **Integritas hasil** | Jangan memilih seed/fold terbaik saja; laporkan semua skenario termasuk yang gagal |
| **Plagiarisme** | Parafrase + sitasi; cek dengan Turnitin sesuai ketentuan prodi |
| **AI generatif** (ChatGPT, Claude, Copilot) | Boleh sebagai **alat bantu** (debug, perbaikan bahasa) sesuai kebijakan kampus; **ungkapkan penggunaannya**; Anda tetap **bertanggung jawab penuh** atas isi; **verifikasi** setiap sitasi — AI dapat mengarang referensi |

<br/>

> Anda harus dapat **menjelaskan setiap baris kode dan setiap kalimat** di naskah saat sidang.

---

<!-- _class: small -->

# 10 Kesalahan Paling Sering pada Skripsi ML/DL

| # | Kesalahan | Akibat |
|---|-----------|--------|
| 1 | Tidak ada baseline | Hasil tidak dapat dinilai |
| 2 | Data leakage (scaler/augmentasi sebelum split, duplikat) | Hasil terlalu optimistis |
| 3 | Memakai test set untuk tuning | Estimasi kinerja bias |
| 4 | Hanya akurasi pada data tidak seimbang | Kelas minoritas "hilang" |
| 5 | Satu kali run, tanpa variansi | Klaim tidak dapat dipercaya |
| 6 | Perbandingan tidak adil (tuning berbeda, data berbeda) | Kesimpulan keliru |
| 7 | Membandingkan angka dengan paper lain pada **dataset berbeda** | Perbandingan tidak sahih |
| 8 | Rumusan masalah tidak terjawab di kesimpulan | Inkonsistensi naskah |
| 9 | Kode/konfigurasi tidak tersimpan | Tidak dapat direproduksi saat revisi |
| 10 | Bab 2 berisi teori panjang yang tidak dipakai | Naskah tebal, isi tipis |

---

<!-- _class: tiny -->

# Checklist Sebelum Seminar Hasil / Sidang

### Naskah
- ✓ Setiap rumusan masalah → tujuan → subbab Bab 4 → poin kesimpulan saling terhubung
- ✓ Hipotesis dinyatakan diterima/ditolak secara eksplisit
- ✓ Matriks literatur & *research gap* jelas
- ✓ Semua gambar/tabel dirujuk dan dibahas di teks
- ✓ Notasi & istilah konsisten; daftar pustaka lengkap dan terverifikasi
- ✓ Lolos cek plagiarisme

### Eksperimen
- ✓ Test set tidak disentuh selama pengembangan
- ✓ Ada baseline trivial, klasik, dan DL sederhana
- ✓ Mean ± std dari ≥ 5 seed / k-fold; uji statistik
- ✓ Ablation & error analysis
- ✓ Repositori: README, `requirements.txt`, config, split, skrip untuk mereproduksi tabel
- ✓ Dataset & model terbaik terarsip (W&B/Drive/Zenodo)

> Simulasikan sidang: minta teman bertanya "**mengapa** memilih metode/metrik/split ini?" — pertanyaan *mengapa* adalah inti sidang.

---

<!-- _class: small -->

# Pertanyaan Sidang yang Sering Muncul

| Pertanyaan | Persiapan jawaban |
|------------|-------------------|
| Apa kontribusi penelitian Anda? | 1–2 kalimat yang merujuk *research gap* |
| Mengapa memakai model ini, bukan X? | Alasan dari literatur + bukti dari eksperimen pembanding |
| Mengapa memakai metrik ini? | Sifat data (tidak seimbang) & kebutuhan domain |
| Bagaimana memastikan tidak ada data leakage? | Prosedur split, *fit* pra-pemrosesan hanya di train, cek duplikat |
| Apakah perbedaan hasil signifikan? | Uji statistik + mean ± std |
| Mengapa model salah pada kelas tertentu? | Error analysis + Grad-CAM |
| Apakah model bisa dipakai di dunia nyata? | Batasan evaluasi + saran uji lapangan |
| Bagaimana jika data ditambah / domain berbeda? | Hasil skenario ukuran data + keterbatasan generalisasi |

---

# Ringkasan

1. Skripsi ML/DL adalah **penelitian eksperimental**: pertanyaan → hipotesis → eksperimen terkontrol → jawaban.
2. **Bab 1**: masalah spesifik, premis bersitasi, hipotesis yang dapat diuji, tujuan = cermin masalah, batasan yang beralasan.
3. **Bab 2**: matriks literatur dan sintesis kritis → *research gap*; teori hanya yang dipakai.
4. **Bab 3**: split dengan aturan yang jelas tanpa kebocoran, **baseline**, skenario yang adil, metrik yang tepat, uji statistik, reproducibility.
5. **Bab 4**: hasil → mengapa → bandingkan literatur → implikasi; ablation & error analysis.
6. **Bab 5**: jawaban langsung atas rumusan masalah + saran yang lahir dari temuan.

> *"Hasil yang baik bukan yang angkanya tertinggi, melainkan yang **jujur, dapat diulang, dan dapat dijelaskan**."*

---

<!-- _class: small -->

# Referensi

1. Demšar, J. (2006). Statistical comparisons of classifiers over multiple data sets. *JMLR*, 7, 1–30.
2. Dietterich, T. G. (1998). Approximate statistical tests for comparing supervised classification learning algorithms. *Neural Computation*, 10(7), 1895–1923.
3. Gebru, T., dkk. (2021). Datasheets for datasets. *Communications of the ACM*, 64(12), 86–92.
4. Kapoor, S., & Narayanan, A. (2023). Leakage and the reproducibility crisis in machine-learning-based science. *Patterns*, 4(9), 100804.
5. Lones, M. A. (2024). Avoiding common machine learning pitfalls. *Patterns*, 5(10). (versi arXiv: 2108.02497)
6. Mohanty, S. P., Hughes, D. P., & Salathé, M. (2016). Using deep learning for image-based plant disease detection. *Frontiers in Plant Science*, 7, 1419.
7. Pan, S. J., & Yang, Q. (2010). A survey on transfer learning. *IEEE TKDE*, 22(10), 1345–1359.
8. Pineau, J., dkk. (2021). Improving reproducibility in machine learning research. *JMLR*, 22(164), 1–20.
9. Selvaraju, R. R., dkk. (2017). Grad-CAM: Visual explanations from deep networks via gradient-based localization. *ICCV*.
10. Yosinski, J., Clune, J., Bengio, Y., & Lipson, H. (2014). How transferable are features in deep neural networks? *NeurIPS*.
11. Tan, M., & Le, Q. (2019). EfficientNet: Rethinking model scaling for convolutional neural networks. *ICML*.

---

<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _header: '' -->
<!-- _footer: '' -->

# Terima Kasih

> *Hasil yang baik bukan yang angkanya tertinggi, melainkan yang jujur, dapat diulang, dan dapat dijelaskan.*
