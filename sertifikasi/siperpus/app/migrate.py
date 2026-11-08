"""Migrasi skema berversi.

Unit J.620100.047.01 - Melakukan Pembaharuan Perangkat Lunak:
- setiap perubahan skema = satu file migrations/NNN_nama.sql,
- versi yang sudah diterapkan dicatat di tabel schema_version,
- database di-backup sebelum migrasi; migrasi gagal -> ROLLBACK.
"""
import re
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).parent / "migrations"
NAMA_FILE = re.compile(r"^(\d{3})_[a-z0-9_]+\.sql$")


def daftar_migrasi():
    files = [f for f in MIGRATIONS_DIR.iterdir() if NAMA_FILE.match(f.name)]
    return sorted((int(NAMA_FILE.match(f.name).group(1)), f) for f in files)


def versi_terpasang(conn):
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_version ("
        " versi INTEGER PRIMARY KEY, nama TEXT NOT NULL,"
        " diterapkan_pada TEXT NOT NULL DEFAULT (datetime('now')))"
    )
    return {row[0] for row in conn.execute("SELECT versi FROM schema_version")}


def backup(db_path):
    src = Path(db_path)
    if not src.exists() or src.stat().st_size == 0:
        return None
    dst = src.with_name(f"{src.stem}.backup-{datetime.now():%Y%m%d%H%M%S}{src.suffix}")
    shutil.copy2(src, dst)
    return dst


def migrate(db_path):
    conn = sqlite3.connect(db_path, isolation_level=None)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        sudah = versi_terpasang(conn)
        pending = [(v, f) for v, f in daftar_migrasi() if v not in sudah]
        if not pending:
            return []
        if sudah:  # database lama -> backup dulu sebelum diubah
            backup(db_path)
        applied = []
        for versi, file in pending:
            script = file.read_text()
            try:
                conn.executescript(
                    "BEGIN;\n" + script +
                    f"\nINSERT INTO schema_version (versi, nama) VALUES ({versi}, '{file.stem}');\nCOMMIT;"
                )
            except sqlite3.Error as exc:
                if conn.in_transaction:
                    conn.execute("ROLLBACK")
                raise RuntimeError(f"Migrasi {file.name} gagal: {exc}") from exc
            applied.append(file.name)
        return applied
    finally:
        conn.close()
