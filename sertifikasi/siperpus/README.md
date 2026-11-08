# SIPERPUS — Sistem Informasi Perpustakaan

Project portofolio **Sertifikasi Database Programmer** (Flask + SQLite).
Pemetaan lengkap unit kompetensi → bukti ada di [`PORTOFOLIO.md`](PORTOFOLIO.md); slide presentasi di [`presentasi.md`](presentasi.md) (Marp).

## Fitur
- Login berbasis role (**admin**, **petugas**), audit log
- Katalog buku (CRUD, validasi ISBN-13, pencarian, filter, urut), anggota
- Sirkulasi: peminjaman, pengembalian + denda otomatis, reservasi (antrian FIFO)
- Laporan SQL (JOIN, GROUP BY/HAVING, subquery, view), rekomendasi buku
- Monitor resource (`/admin/monitor`), health-check (`/health`)
- Migrasi skema berversi + backup otomatis

## Struktur
```
siperpus/
├── config.py               # konfigurasi per environment (dev/staging/prod/testing)
├── run.py                  # entry point WSGI
├── requirements.txt        # library + versi terkunci
├── app/
│   ├── __init__.py         # application factory, logging, error handler
│   ├── db.py               # koneksi, query, transaksi, perintah CLI
│   ├── migrate.py          # migrasi berversi + backup
│   ├── migrations/         # 001_skema_awal.sql, 002_reservasi_dan_audit.sql
│   ├── repository.py       # seluruh SQL aplikasi
│   ├── algorithms.py       # struktur data & algoritma
│   ├── security.py         # auth, role, CSRF, headers, rate limit, audit
│   ├── monitoring.py       # metrik request/query/memori/disk
│   ├── seed.py             # data contoh (non-production)
│   ├── views/              # blueprint: auth, katalog, sirkulasi, admin
│   ├── templates/  static/
├── tests/                  # 33 test (pytest)
└── docs/                   # ERD, log debugging, code review, analisis dampak
```

## Menjalankan (development)
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask --app run init-db          # migrasi + data contoh
flask --app run run --debug      # http://127.0.0.1:5000
```
Akun contoh: `admin / Admin#2026` dan `petugas / Petugas#2026` (khusus dev/staging).

## Test & kualitas kode
```bash
pytest -q --cov=app       # 33 passed
flake8                    # lint
pip-audit -r requirements.txt
```

## Environment
| | Development | Staging | Production |
|---|---|---|---|
| `APP_ENV` | development | staging | production |
| Database | `instance/perpus_dev.db` | `instance/perpus_staging.db` | `DATABASE_PATH` |
| DEBUG | ✅ | ❌ | ❌ |
| Log level | DEBUG | INFO | WARNING |
| Cookie `Secure` + HSTS | ❌ | ❌ | ✅ |
| `SECRET_KEY` | default boleh | wajib di `.env` | **wajib** (aplikasi menolak start) |
| Server | `flask run` | `gunicorn -w 2` | `gunicorn -w 4` di balik Nginx (HTTPS) |

## Prosedur pembaharuan (update) production
1. Baca `CHANGELOG.md` & `docs/ANALISIS_DAMPAK.md`; uji di **staging** terlebih dahulu.
2. `git fetch --tags && git checkout v1.1.0`
3. `pip install -r requirements.txt` (versi terkunci)
4. `APP_ENV=production flask --app run migrate` → backup otomatis `*.backup-<timestamp>.db` lalu migrasi.
5. Restart service: `sudo systemctl restart siperpus`
6. Verifikasi: `curl -f https://<host>/health` dan cek `/admin/monitor` (versi skema).
7. **Rollback**: hentikan service → kembalikan file backup → `git checkout v1.0.0` → start.

┌─────────┬──────────┬──────────────┬─────────────────────────────────────────────────────────┐
│  Role   │ Username │   Password   │                          Akses                          │
├─────────┼──────────┼──────────────┼─────────────────────────────────────────────────────────┤
│ Admin   │ admin    │ Admin#2026   │ Semua menu, termasuk Monitor dan Audit                  │
├─────────┼──────────┼──────────────┼─────────────────────────────────────────────────────────┤
│ Petugas │ petugas  │ Petugas#2026 │ Buku, Anggota, Sirkulasi, Laporan (Monitor ditolak 403) │
└─────────┴──────────┴──────────────┴─────────────────────────────────────────────────────────┘\


# 1. (sekali saja) virtualenv + dependensi
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. buat tabel (migrasi 001 & 002) + isi data contoh
APP_ENV=development flask --app run init-db

# 3. jalankan aplikasi
APP_ENV=development flask --app run run --debug
