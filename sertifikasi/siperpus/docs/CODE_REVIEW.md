# Code Review — SIPERPUS

> Unit **J.620100.032.01** – Menerapkan Code Review

## 1. Proses

1. Developer membuat branch fitur (`feature/reservasi`) → Pull Request ke `develop`.
2. **Pemeriksaan otomatis** wajib lulus sebelum direview manusia:
   `flake8` (gaya kode, `setup.cfg`), `pytest --cov=app` (test), `pip-audit` (kerentanan dependensi).
3. Reviewer memeriksa memakai checklist di bawah dan memberi komentar per baris.
4. Developer memperbaiki → reviewer memverifikasi → *approve* → merge.

## 2. Checklist review

| Aspek | Pertanyaan |
|---|---|
| Fungsionalitas | Apakah kode memenuhi kebutuhan & aturan bisnis (maks. pinjam, denda, stok)? |
| Basis data | Apakah query memakai parameter binding? Apakah operasi multi-langkah memakai transaksi? Apakah ada index untuk kolom filter/join? |
| Keamanan | Validasi input? Hak akses (role)? CSRF? Data sensitif tidak di-log? Pesan error tidak membocorkan detail? |
| Keterbacaan | Penamaan jelas & konsisten (Bahasa Indonesia untuk domain)? Fungsi ringkas, satu tanggung jawab? |
| Kinerja | Ada N+1 query? Kompleksitas algoritma wajar? |
| Test | Ada test untuk jalur sukses **dan** gagal? |
| Konfigurasi | Tidak ada nilai rahasia/hard-coded path; memakai `config.py`/`.env`? |

## 3. Rekaman review (PR #7 — fitur pencarian & laporan)

| # | File | Temuan | Tingkat | Tindak lanjut |
|---|---|---|---|---|
| R1 | `repository.py::list_buku` | Versi awal: `"... ORDER BY " + request.args["urut"]` → **SQL injection** pada ORDER BY (nama kolom tidak bisa di-bind). | Kritis | Diganti whitelist `URUTAN_BUKU`; test `test_sql_injection_pada_pencarian`. ✅ |
| R2 | `repository.py::list_buku` | Versi awal: `f"WHERE judul LIKE '%{q}%'"`. | Kritis | Diganti parameter bernama `:kw`. ✅ |
| R3 | `views/auth.py::login` | Pesan "username tidak ditemukan" vs "password salah" → *user enumeration*. | Tinggi | Pesan generik "Username atau password salah". ✅ |
| R4 | `views/auth.py::login` | Parameter `next` langsung dipakai `redirect()` → *open redirect*. | Sedang | Hanya path internal yang diterima. ✅ |
| R5 | `views/sirkulasi.py` | Laporan memanggil `get_buku()` dalam loop untuk tiap peminjaman (**N+1 query**). | Sedang | Diganti VIEW `v_peminjaman_aktif` (satu query JOIN). ✅ |
| R6 | `repository.py::pinjam_buku` | Cek batas pinjam & insert tidak atomik. | Tinggi | Dibungkus `transaction()` (lihat BUG-01). ✅ |
| R7 | `seed.py` | Password contoh bisa terbawa ke production. | Sedang | `seed_data()` menolak berjalan saat `ENV_NAME == "production"`. ✅ |
| R8 | `algorithms.py::hitung_denda` | Tidak ada batas maksimum denda. | Rendah | Parameter `maksimum` (`DENDA_MAKSIMUM`). ✅ |

## 4. Contoh komentar review (sebelum → sesudah)

```python
# SEBELUM (ditolak reviewer)
sql = f"SELECT * FROM buku WHERE judul LIKE '%{q}%' ORDER BY {urut}"

# SESUDAH (disetujui)
URUTAN_BUKU = {"judul": "b.judul", "tahun": "b.tahun DESC", ...}
sql += " ORDER BY " + URUTAN_BUKU.get(urut, URUTAN_BUKU["judul"])
query(sql, {"kw": f"%{keyword}%"})
```
