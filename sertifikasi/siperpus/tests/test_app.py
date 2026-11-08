"""Integration test: akses basis data, SQL, keamanan, konfigurasi, monitoring."""
from datetime import date, timedelta

import pytest

from app import create_app
from app import repository as repo
from app.db import query
from config import DEFAULT_SECRET
from conftest import ambil_csrf


# ------------------------------ Konfigurasi (042) ------------------------------
def test_production_menolak_secret_default(monkeypatch):
    with pytest.raises(RuntimeError):
        create_app("production", {"SECRET_KEY": DEFAULT_SECRET})


def test_environment_berbeda_konfigurasi_berbeda(tmp_path):
    dev = create_app("development", {"DATABASE": str(tmp_path / "d.db"), "LOG_FILE": None})
    prod = create_app("production", {"SECRET_KEY": "x" * 32, "DATABASE": str(tmp_path / "p.db"), "LOG_FILE": None})
    assert dev.config["DEBUG"] is True and prod.config["DEBUG"] is False
    assert prod.config["SESSION_COOKIE_SECURE"] is True


# ------------------------------ Keamanan (J.62090.011.01) ----------------------
def test_halaman_wajib_login(client):
    resp = client.get("/buku")
    assert resp.status_code == 302 and "/login" in resp.headers["Location"]


def test_login_salah_dan_benar(login):
    assert login(password="salah").status_code == 401
    assert login().status_code == 302


def test_post_tanpa_csrf_ditolak(client):
    resp = client.post("/login", data={"username": "admin", "password": "Admin#2026"})
    assert resp.status_code == 400


def test_brute_force_diblokir(login):
    for _ in range(5):
        login(password="salah")
    assert login().status_code == 429  # password benar pun ditolak sementara


def test_petugas_tidak_boleh_akses_monitor(client, login):
    login("petugas", "Petugas#2026")
    assert client.get("/admin/monitor").status_code == 403


def test_security_headers(client):
    resp = client.get("/login")
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert "default-src 'self'" in resp.headers["Content-Security-Policy"]


def test_sql_injection_pada_pencarian(client, login):
    login()
    resp = client.get("/buku", query_string={"q": "' OR 1=1 --", "urut": "judul; DROP TABLE buku"})
    assert resp.status_code == 200
    assert "Tidak ada buku yang cocok" in resp.get_data(as_text=True)
    with client.application.app_context():
        assert query("SELECT COUNT(*) AS n FROM buku", one=True)["n"] == 8


def test_password_tersimpan_sebagai_hash(app):
    with app.app_context():
        h = repo.get_user_by_username("admin")["password_hash"]
    assert "Admin#2026" not in h and h.startswith(("scrypt:", "pbkdf2:"))


# --------------------------- Akses DB & SQL (020/021) ---------------------------
def test_pinjam_mengurangi_stok_via_trigger(app):
    with app.app_context():
        sebelum = repo.get_buku(3)["stok"]
        repo.pinjam_buku(anggota_id=4, buku_id=3, petugas_id=1)
        assert repo.get_buku(3)["stok"] == sebelum - 1


def test_stok_habis_ditolak_dan_rollback(app):
    with app.app_context():
        habis = query("SELECT id FROM buku WHERE stok = 0", one=True)["id"]
        jumlah = query("SELECT COUNT(*) AS n FROM peminjaman", one=True)["n"]
        with pytest.raises(repo.AturanBisnisError, match="Stok"):
            repo.pinjam_buku(4, habis, 1)
        assert query("SELECT COUNT(*) AS n FROM peminjaman", one=True)["n"] == jumlah


def test_batas_maksimal_pinjam(app):
    with app.app_context():
        for buku_id in (1, 2, 3):
            repo.pinjam_buku(4, buku_id, 1)
        with pytest.raises(repo.AturanBisnisError, match="Batas"):
            repo.pinjam_buku(4, 4, 1)


def test_kembali_terlambat_menghasilkan_denda(app):
    with app.app_context():
        hari_pinjam = date.today() - timedelta(days=10)
        pid = repo.pinjam_buku(4, 2, 1, hari_ini=hari_pinjam)
        denda, _ = repo.kembalikan_buku(pid)
        assert denda == 3 * app.config["DENDA_PER_HARI"]  # 10 - 7 hari
        with pytest.raises(repo.AturanBisnisError):
            repo.kembalikan_buku(pid)  # tidak bisa dikembalikan dua kali


def test_laporan_sql(app):
    with app.app_context():
        assert repo.buku_terpopuler()[0][0] == "Database System Concepts"
        assert {r["judul"] for r in repo.buku_tidak_pernah_dipinjam()} >= {"The Web Application Hacker's Handbook"}
        assert all(r["total_denda"] > 0 for r in repo.anggota_dengan_denda())


def test_alur_web_tambah_buku(client, login):
    login()
    token = ambil_csrf(client, "/buku/baru")
    data = {"isbn": "978-1-59327-584-6", "judul": "Black Hat Python", "penulis": "Justin Seitz",
            "penerbit": "No Starch", "tahun": "2014", "stok": "2", "kategori_id": "4", "_csrf": token}
    assert client.post("/buku/baru", data=data).status_code == 302
    resp = client.post("/buku/baru", data=data, follow_redirects=True)  # ISBN duplikat
    assert "ISBN sudah terdaftar" in resp.get_data(as_text=True)


# ------------------------------ Monitoring (045) -------------------------------
def test_health_dan_monitor(client, login):
    assert client.get("/health").get_json() == {"status": "ok", "db": "ok"}
    login()
    resp = client.get("/admin/monitor")
    assert resp.status_code == 200 and "X-Response-Time-ms" in resp.headers


# ------------------------------- Migrasi (047) ---------------------------------
def test_migrasi_tercatat_dan_idempoten(app):
    from app.migrate import migrate
    with app.app_context():
        versi = [r["versi"] for r in query("SELECT versi FROM schema_version ORDER BY versi")]
    assert versi == [1, 2]
    assert migrate(app.config["DATABASE"]) == []
