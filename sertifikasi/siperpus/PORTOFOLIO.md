# Portofolio Sertifikasi Kompetensi — Database Programmer

**Project:** SIPERPUS — Sistem Informasi Perpustakaan berbasis Web (Flask + SQLite)
**Asesi:** Ahmad Luky Ramdani
**Versi project:** 1.1.0 · **Tanggal:** 28 Oktober 2026

> Dokumen ini memetakan **14 unit kompetensi** skema Database Programmer ke bukti nyata di dalam project.
> Elemen kompetensi di bawah merupakan ringkasan. Untuk asesmen resmi, cocokkan dengan teks KUK pada
> SKKNI No. 282 Tahun 2016 (kode J.620100.xxx) dan SKKNI No. 55 Tahun 2015 (kode J.62090.xxx).

---

## Ringkasan project

Perpustakaan kampus membutuhkan aplikasi untuk mengelola katalog buku, anggota, peminjaman/pengembalian beserta denda, reservasi buku yang stoknya habis, dan laporan. Aplikasi harus aman, dapat dipantau, dan dapat diperbarui tanpa kehilangan data.

| Aspek | Isi |
|---|---|
| Arsitektur | Flask (application factory + blueprint) → repository (SQL) → SQLite |
| Basis data | 7 tabel, 9 index, 3 trigger, 1 view, 2 migrasi berversi |
| Kode | ± 1.250 baris Python (tanpa test), 13 template |
| Pengujian | 33 test otomatis (pytest), coverage ± 78%, flake8 bersih |

## Matriks unit kompetensi → bukti

| No | Kode | Unit | Bukti utama |
|---|---|---|---|
| 1 | J.620100.001.01 | Menganalisis Tools | §1, `README.md` |
| 2 | J.620100.003.01 | Identifikasi Library/Komponen/Framework | §2, `requirements.txt` |
| 3 | J.620100.004.02 | Menggunakan Struktur Data | `app/algorithms.py`, `app/security.py`, `app/monitoring.py` |
| 4 | J.620100.007.01 | Implementasi Rancangan Entitas & Keterkaitan | `docs/ERD.md`, `migrations/001_*.sql` |
| 5 | J.620100.020.02 | Menggunakan SQL | `migrations/*.sql`, `app/repository.py` |
| 6 | J.620100.021.02 | Menerapkan Akses Basis Data | `app/db.py`, `app/repository.py` |
| 7 | J.620100.022.02 | Mengimplementasikan Algoritma Pemrograman | `app/algorithms.py`, `tests/test_algorithms.py` |
| 8 | J.620100.025.02 | Melakukan Debugging | `docs/LOG_DEBUGGING.md`, logging, test |
| 9 | J.620100.032.01 | Menerapkan Code Review | `docs/CODE_REVIEW.md`, `setup.cfg` |
| 10 | J.620100.042.01 | Konfigurasi Sesuai Environment | `config.py`, `.env.example`, `README.md` |
| 11 | J.620100.043.01 | Menganalisis Dampak Perubahan | `docs/ANALISIS_DAMPAK.md` |
| 12 | J.620100.045.01 | Pemantauan Resource Aplikasi | `app/monitoring.py`, `/admin/monitor`, `/health` |
| 13 | J.620100.047.01 | Melakukan Pembaharuan Perangkat Lunak | `app/migrate.py`, `migrations/`, `CHANGELOG.md` |
| 14 | J.62090.011.01 | Menerapkan Standar Keamanan Informasi | `app/security.py`, `views/auth.py` |

---

## 1. J.620100.001.01 — Menganalisis Tools

**Elemen:** (1) mengidentifikasi kebutuhan tools, (2) membandingkan & memilih tools sesuai kebutuhan.

**Kebutuhan:** aplikasi web CRUD skala kecil–menengah (± 5 petugas bersamaan), mudah dipasang di server kampus, mudah dipelajari tim.

| Kebutuhan | Alternatif | Dipilih | Alasan |
|---|---|---|---|
| Bahasa | Python, PHP, Java | **Python 3.11** | Sintaks ringkas, ekosistem test kuat |
| Framework web | Django, **Flask**, FastAPI | **Flask 3** | Ringan; SQL ditulis langsung (sesuai fokus *database programmer*), tidak terkunci ORM |
| DBMS | **SQLite**, MySQL, PostgreSQL | **SQLite** (dev/staging), siap migrasi ke PostgreSQL | Tanpa server, file tunggal, mendukung FK/trigger/view/partial index; beban tulis rendah |
| DB client | DB Browser for SQLite, DBeaver, CLI `sqlite3` | `sqlite3` CLI + DBeaver | `EXPLAIN QUERY PLAN`, inspeksi skema |
| Editor/IDE | VS Code, PyCharm | VS Code | Debugger Flask, ekstensi Python & SQLite |
| Version control | Git + GitHub | Git | Branch, PR untuk code review |
| Test | unittest, **pytest** | pytest + pytest-cov | Fixture, parametrisasi, coverage |
| Server produksi | `flask run`, **gunicorn**, uWSGI | gunicorn + Nginx | `flask run` tidak untuk production |

## 2. J.620100.003.01 — Identifikasi Library, Komponen, atau Framework

**Elemen:** (1) mengidentifikasi library/komponen yang dibutuhkan, (2) memastikan kompatibilitas & lisensi, (3) mendokumentasikan dependensi.

| Library | Versi | Fungsi di project | Lisensi |
|---|---|---|---|
| Flask | 3.0.3 | Routing, blueprint, session, Jinja2 | BSD-3 |
| Werkzeug | 3.0.6 | WSGI, `generate_password_hash`/`check_password_hash` | BSD-3 |
| sqlite3 | *stdlib* | Driver DB-API 2.0 | – |
| gunicorn | 23.0.0 | WSGI server staging/production | MIT |
| psutil | 6.1.0 | Memori & CPU proses (opsional, ada fallback) | BSD-3 |
| pytest / pytest-cov | 8.3.3 / 5.0.0 | Test & coverage | MIT |
| flake8 | 7.1.1 | Lint untuk code review | MIT |
| pip-audit | 2.7.3 | Pemindaian CVE dependensi | Apache-2.0 |

Komponen internal: `collections.deque`, `heapq`, `dataclasses`, `hmac`, `secrets`, `logging.handlers.RotatingFileHandler`.
Semua versi **dikunci** di `requirements.txt` agar dev/staging/production identik.

## 3. J.620100.004.02 — Menggunakan Struktur Data

**Elemen:** (1) mengidentifikasi konsep data & struktur data, (2) menerapkan struktur data dan aksesnya.

| Struktur data | Lokasi | Alasan pemilihan |
|---|---|---|
| `deque` (FIFO) | `AntrianReservasi` — `app/algorithms.py` | enqueue/dequeue O(1), urut kedatangan |
| `deque(maxlen=N)` (ring buffer) | `_requests`, `_queries` — `app/monitoring.py` | Memori tetap; data lama otomatis terbuang |
| `dict of deque` | `_login_gagal` — `app/security.py` | Riwayat gagal login per IP; buang entri kedaluwarsa dari depan |
| `dict of set` | `rekomendasi()` | Indeks buku → himpunan peminjam; irisan set untuk skor |
| Heap (`heapq.nlargest`) | `top_n()` | Top-N O(n log k) |
| `list` terurut | `binary_search()` | Pencarian O(log n) |
| `dict` (lookup table) | `URUTAN_BUKU` — `repository.py` | Whitelist kolom ORDER BY |
| `Counter` | `snapshot()` | Endpoint teramai |
| `dataclass` | `AntrianReservasi` | Struktur bertipe & ringkas |
| `sqlite3.Row` | `db.py` | Akses kolom by name `row["judul"]` |

## 4. J.620100.007.01 — Mengimplementasikan Rancangan Entitas dan Keterkaitan Antar Entitas

**Elemen:** (1) menerjemahkan ERD ke skema fisik, (2) menerapkan relasi & integritas referensial, (3) menerapkan normalisasi.

- ERD, kardinalitas, kamus data & normalisasi 1NF–3NF: **`docs/ERD.md`**
- Implementasi: `app/migrations/001_skema_awal.sql`, `002_reservasi_dan_audit.sql`
- Relasi M:N `anggota ↔ buku` diwujudkan dengan entitas asosiatif `peminjaman` dan `reservasi`
- Integritas: PK, FK (`ON DELETE RESTRICT / CASCADE / SET NULL` sesuai makna bisnis), UNIQUE, CHECK, trigger

## 5. J.620100.020.02 — Menggunakan SQL

**Elemen:** (1) DDL — membuat/mengubah objek basis data, (2) DML — memanipulasi data, (3) query untuk menampilkan & menganalisis data.

| Kategori | Contoh & lokasi |
|---|---|
| DDL | `CREATE TABLE`, `CREATE INDEX`, `CREATE UNIQUE INDEX ... WHERE` (partial), `CREATE VIEW`, `CREATE TRIGGER` — `migrations/` |
| DML | `INSERT`, `UPDATE`, `DELETE` — `simpan_buku`, `kembalikan_buku`, `hapus_buku` |
| JOIN | `v_peminjaman_aktif` (4 tabel), `list_buku`, `list_audit` (LEFT JOIN) |
| Agregat + GROUP BY + HAVING | `anggota_dengan_denda()` |
| Subquery | korelasi di `list_anggota()`, `NOT EXISTS` di `buku_tidak_pernah_dipinjam()`, skalar di `statistik_dashboard()` |
| Fungsi tanggal | `strftime('%Y-%m', ...)`, `julianday()` |
| Transaksi | `BEGIN IMMEDIATE / COMMIT / ROLLBACK` |
| Optimasi | `EXPLAIN QUERY PLAN` → `SEARCH peminjaman USING INDEX idx_peminjaman_anggota (anggota_id=?)` |

```sql
-- Anggota dengan total denda >= batas
SELECT a.no_anggota, a.nama, COUNT(p.id) AS kali_terlambat, SUM(p.denda) AS total_denda
FROM anggota a JOIN peminjaman p ON p.anggota_id = a.id
WHERE p.denda > 0
GROUP BY a.id
HAVING SUM(p.denda) >= ?
ORDER BY total_denda DESC;
```

## 6. J.620100.021.02 — Menerapkan Akses Basis Data

**Elemen:** (1) menentukan cara akses basis data, (2) membuat koneksi & menjalankan perintah, (3) mengelola transaksi & error.

`app/db.py`:
- `get_db()` — satu koneksi per request di `flask.g`, ditutup di `teardown_appcontext`
- `PRAGMA foreign_keys = ON` di setiap koneksi
- `query()` / `execute()` — **parameter binding** (`?` dan `:nama`), dicatat waktunya untuk monitoring
- `transaction()` — context manager `BEGIN IMMEDIATE → COMMIT`, otomatis `ROLLBACK` bila ada exception
- Error DB diterjemahkan ke pesan bisnis: `sqlite3.IntegrityError` → `AturanBisnisError("Stok buku habis...")`

```python
with transaction():
    aktif = query("SELECT COUNT(*) AS n FROM peminjaman WHERE anggota_id = ? AND status = 'dipinjam'", (anggota_id,), one=True)["n"]
    if aktif >= cfg["MAKS_PINJAM_AKTIF"]:
        raise AturanBisnisError(...)          # -> ROLLBACK
    execute("INSERT INTO peminjaman (...) VALUES (?, ?, ?, ?, ?)", (...))
```

## 7. J.620100.022.02 — Mengimplementasikan Algoritma Pemrograman

**Elemen:** (1) menjelaskan varian & invarian, (2) membuat alur logika, (3) menerapkan teknik algoritma umum (sorting, searching), (4) menggunakan prosedur/fungsi, (5) mengidentifikasi kompleksitas algoritma.

| Algoritma | Fungsi | Kompleksitas | Dipakai di |
|---|---|---|---|
| Checksum ISBN-13 | `validasi_isbn13` | O(n) | Form buku |
| Perhitungan denda (percabangan, batas maks.) | `hitung_denda` | O(1) | Pengembalian |
| Binary search | `binary_search` | O(log n) | Cek ISBN duplikat |
| Merge sort (stabil) | `merge_sort` | O(n log n) | Utilitas pengurutan |
| Top-N heap | `top_n` | O(n log k) | Laporan buku terpopuler |
| Rekomendasi irisan himpunan | `rekomendasi` | O(m + b) | Detail buku |
| Antrian FIFO | `AntrianReservasi` | O(1) | Reservasi |

Invarian & varian dituliskan pada docstring `binary_search` dan `validasi_isbn13`. Diuji oleh 15 kasus di `tests/test_algorithms.py` (termasuk kasus batas: list kosong, ISBN 12 digit, denda melebihi maksimum).

## 8. J.620100.025.02 — Melakukan Debugging

**Elemen:** (1) mempersiapkan kode & tools debugging, (2) melakukan debugging, (3) memperbaiki kode dan memverifikasi.

- Tools: debug mode (dev saja), logging bertingkat + file log berotasi, `breakpoint()`, test otomatis, `EXPLAIN QUERY PLAN`, log slow query
- Catatan 4 bug lengkap (gejala → reproduksi → akar masalah → perbaikan → verifikasi): **`docs/LOG_DEBUGGING.md`**
  - BUG-01 race condition stok negatif → trigger + `BEGIN IMMEDIATE`
  - BUG-02 CSRF lolos dengan token kosong → ditemukan oleh test
  - BUG-03 test flaky karena state global
  - BUG-04 backup tidak perlu pada DB baru

## 9. J.620100.032.01 — Menerapkan Code Review

**Elemen:** (1) menyiapkan standar & checklist review, (2) melakukan review, (3) menindaklanjuti hasil review.

- Standar otomatis: `flake8` (`setup.cfg`), `pytest`, `pip-audit`
- Checklist & rekaman review 8 temuan (SQL injection ORDER BY, user enumeration, open redirect, N+1 query, transaksi non-atomik, dll.) beserta tindak lanjutnya: **`docs/CODE_REVIEW.md`**

## 10. J.620100.042.01 — Konfigurasi Perangkat Lunak Sesuai Environment

**Elemen:** (1) mengidentifikasi kebutuhan konfigurasi tiap environment, (2) menerapkan konfigurasi, (3) memverifikasi konfigurasi.

- `config.py`: kelas `DevelopmentConfig`, `StagingConfig`, `ProductionConfig`, `TestingConfig`; dipilih via `APP_ENV`
- Rahasia dari environment / `.env` (`.env.example` disediakan; `.env` di-`.gitignore`)
- **Fail-safe**: production menolak berjalan dengan `SECRET_KEY` bawaan (`create_app`)
- Verifikasi otomatis: `test_production_menolak_secret_default`, `test_environment_berbeda_konfigurasi_berbeda`
- Tabel perbandingan environment & cara menjalankan: `README.md`

## 11. J.620100.043.01 — Menganalisis Dampak Perubahan Terhadap Aplikasi

**Elemen:** (1) mengidentifikasi perubahan, (2) menganalisis komponen terdampak & risikonya, (3) melaporkan rekomendasi.

**`docs/ANALISIS_DAMPAK.md`** — CR-002 (reservasi + audit log) v1.0.0 → v1.1.0: komponen terdampak per lapisan (DB, repository, view, test), matriks dampak (fungsional, data, kinerja, keamanan, downtime), risiko & mitigasi, rencana rollback, rekomendasi rilis *minor version*.

## 12. J.620100.045.01 — Melakukan Pemantauan Resource yang Digunakan Aplikasi

**Elemen:** (1) mengidentifikasi resource yang perlu dipantau, (2) melakukan pemantauan, (3) melaporkan & menindaklanjuti hasil.

| Resource | Cara pantau | Lokasi |
|---|---|---|
| Waktu respons (rata-rata, p95) | `before_request`/`after_request`, header `X-Response-Time-ms` | `monitoring.py` |
| Request lambat | log WARNING bila > `SLOW_REQUEST_MS` | `_catat_request` |
| Waktu query & slow query | `record_query()` dari `db._timed` | `/admin/monitor` |
| Memori & CPU proses | `psutil` (fallback `resource.getrusage`) | `_memori_proses_mb` |
| Ukuran database & disk | `os.path.getsize`, `shutil.disk_usage` | `snapshot()` |
| Error 5xx | dihitung dari status response | `snapshot()` |
| Ketersediaan | `GET /health` → 200 / 503 | `views/admin.py` |

Tindak lanjut hasil pantau: kueri peminjaman per anggota terdeteksi full-scan → ditambah `idx_peminjaman_anggota` (dibuktikan dengan `EXPLAIN QUERY PLAN`).

## 13. J.620100.047.01 — Melakukan Pembaharuan Perangkat Lunak

**Elemen:** (1) mengidentifikasi kebutuhan pembaharuan, (2) melakukan pembaharuan sesuai prosedur, (3) memverifikasi & mendokumentasikan pembaharuan.

- Migrasi berversi `app/migrations/NNN_*.sql` + tabel `schema_version`
- `flask --app run migrate`: deteksi migrasi tertunda → **backup otomatis** → jalankan dalam transaksi → ROLLBACK bila gagal; idempoten (`test_migrasi_tercatat_dan_idempoten`)
- Versi aplikasi semantik (`Config.VERSION = "1.1.0"`), ditampilkan di footer & monitor
- `CHANGELOG.md`, prosedur update & rollback production di `README.md`
- Pembaharuan dependensi: `pip-audit` → versi baru dikunci di `requirements.txt`

## 14. J.62090.011.01 — Menerapkan Standar-Standar Keamanan Informasi yang Berlaku

**Elemen:** (1) mengidentifikasi standar keamanan yang berlaku, (2) menerapkan kontrol keamanan, (3) memverifikasi penerapan.

Acuan: **OWASP Top 10 (2021)**, **ISO/IEC 27001:2022 Annex A**, UU No. 27 Tahun 2022 tentang Pelindungan Data Pribadi (data anggota).

| Risiko / kontrol | Penerapan | Verifikasi (test) |
|---|---|---|
| A01 Broken Access Control | `login_required`, `role_required("admin")` | `test_halaman_wajib_login`, `test_petugas_tidak_boleh_akses_monitor` |
| A02 Cryptographic Failures | Hash password (scrypt), cookie `HttpOnly`, `SameSite`, `Secure` + HSTS di production | `test_password_tersimpan_sebagai_hash` |
| A03 Injection | Parameter binding, whitelist ORDER BY, autoescape Jinja2 | `test_sql_injection_pada_pencarian` |
| A05 Security Misconfiguration | Security headers (CSP, X-Frame-Options, nosniff), debug mati di production, pesan error generik | `test_security_headers` |
| A07 Identification & Authentication | Batas 5× gagal / 5 menit, `session.clear()` saat login, timeout sesi 30 menit, pesan login generik | `test_brute_force_diblokir` |
| A09 Logging & Monitoring (ISO A.8.15) | Tabel `audit_log` + halaman audit | – |
| CSRF | Token per sesi, `hmac.compare_digest` | `test_post_tanpa_csrf_ditolak` |
| Open redirect | Parameter `next` hanya path internal | – |
| Keamanan rantai pasok | Versi terkunci + `pip-audit` | – |

---

## Lampiran — Bukti eksekusi

```text
$ flask --app run init-db
Migrasi diterapkan: ['001_skema_awal.sql', '002_reservasi_dan_audit.sql']
Data contoh dimasukkan.

$ pytest -q
.................................                                        [100%]
33 passed

$ flake8
(tidak ada pelanggaran)

sqlite> EXPLAIN QUERY PLAN SELECT COUNT(*) FROM peminjaman WHERE anggota_id=1 AND status='dipinjam';
`--SEARCH peminjaman USING INDEX idx_peminjaman_anggota (anggota_id=?)
```
