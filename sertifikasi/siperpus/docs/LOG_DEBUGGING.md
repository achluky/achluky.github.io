# Log Debugging — SIPERPUS

> Unit **J.620100.025.02** – Melakukan Debugging

## Alat & teknik yang dipakai

| Teknik | Implementasi |
|---|---|
| Debug mode + interactive debugger | `DevelopmentConfig.DEBUG = True` (hanya di development) |
| Logging bertingkat | `_setup_logging()` di `app/__init__.py` — DEBUG (dev), INFO (staging), WARNING (production); file log berotasi `instance/app.log` |
| Breakpoint | `breakpoint()` / debugger VS Code (`launch.json` tipe *Python: Flask*) |
| Test otomatis sebagai pendeteksi regresi | `pytest -q` (33 test), `pytest --cov=app` |
| Inspeksi query | `record_query()` mencatat waktu tiap SQL, slow query ditampilkan di `/admin/monitor` |
| Inspeksi DB langsung | `sqlite3 instance/perpus_dev.db` → `.schema`, `EXPLAIN QUERY PLAN ...` |

## Catatan bug

### BUG-01 — Stok bisa negatif saat dua petugas meminjamkan eksemplar terakhir bersamaan
- **Gejala**: pada uji manual dengan dua tab browser, stok buku menjadi `-1`.
- **Reproduksi**: buku stok 1 → dua request `POST /sirkulasi/pinjam` dikirim hampir bersamaan.
- **Akar masalah**: pengecekan stok dilakukan di Python (`SELECT stok` lalu `INSERT`) di luar transaksi → *race condition* (check-then-act).
- **Perbaikan**:
  1. pengecekan dipindah ke trigger `trg_cek_stok` (atomik di DB),
  2. constraint `CHECK (stok >= 0)` sebagai pengaman terakhir,
  3. seluruh proses pinjam dibungkus `transaction()` dengan `BEGIN IMMEDIATE` (mengunci tulis).
- **Verifikasi**: `test_stok_habis_ditolak_dan_rollback` — peminjaman ditolak dan jumlah baris `peminjaman` tidak bertambah (rollback).

### BUG-02 — Validasi CSRF lolos ketika sesi belum memiliki token
- **Gejala**: `test_post_tanpa_csrf_ditolak` gagal → `assert 302 == 400` (login berhasil tanpa token).
- **Akar masalah**: `hmac.compare_digest("", session.get("_csrf", ""))` → string kosong dibandingkan string kosong bernilai **True**.
- **Perbaikan** (`app/security.py::_cek_csrf`): token yang tersimpan di sesi wajib tidak kosong.
  ```python
  disimpan = session.get("_csrf", "")
  if not disimpan or not hmac.compare_digest(dikirim, disimpan):
      abort(400)
  ```
- **Verifikasi**: seluruh test lulus (33 passed).
- **Pelajaran**: test negatif (*apa yang harus ditolak*) sama pentingnya dengan test positif.

### BUG-03 — Data test saling memengaruhi (test flaky)
- **Gejala**: `test_login_salah_dan_benar` lulus jika dijalankan sendiri, tetapi gagal (429) jika dijalankan setelah `test_brute_force_diblokir`.
- **Akar masalah**: penghitung login gagal `_login_gagal` adalah variabel modul (global) yang tetap ada antar-test.
- **Perbaikan**: fixture `app` di `tests/conftest.py` mengosongkan `security._login_gagal` sebelum tiap test.

### BUG-04 — Backup dibuat untuk database yang baru dibuat
- **Gejala**: `flask init-db` pada database kosong tetap menghasilkan file `*.backup-*.db`.
- **Akar masalah**: `versi_terpasang()` membuat tabel `schema_version` terlebih dahulu sehingga ukuran file > 0.
- **Perbaikan**: backup hanya dibuat jika sudah ada versi skema terpasang (`if sudah:` di `app/migrate.py`).

## Hasil akhir
```
$ pytest -q
.................................                    [100%]
33 passed
$ flake8
(tidak ada pelanggaran)
```
