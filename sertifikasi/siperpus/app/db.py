"""Lapisan akses basis data.

Unit J.620100.021.02 - Menerapkan Akses Basis Data:
- satu koneksi per request (disimpan di flask.g) dan ditutup otomatis,
- semua query memakai parameter binding (?) -> aman dari SQL injection,
- transaksi eksplisit BEGIN / COMMIT / ROLLBACK lewat context manager,
- foreign key constraint diaktifkan di setiap koneksi.
"""
import sqlite3
import time
from contextlib import contextmanager

import click
from flask import current_app, g


def connect(path):
    conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_db():
    if "db" not in g:
        g.db = connect(current_app.config["DATABASE"])
    return g.db


def close_db(exc=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def _timed(sql, params):
    from .monitoring import record_query

    start = time.perf_counter()
    cur = get_db().execute(sql, params)
    record_query(sql, (time.perf_counter() - start) * 1000)
    return cur


def query(sql, params=(), one=False):
    """SELECT -> list[sqlite3.Row] atau satu Row (one=True)."""
    rows = _timed(sql, params).fetchall()
    if one:
        return rows[0] if rows else None
    return rows


def execute(sql, params=()):
    """INSERT/UPDATE/DELETE -> lastrowid. Autocommit bila di luar transaction()."""
    return _timed(sql, params).lastrowid


@contextmanager
def transaction():
    """Blok atomik: semua perintah berhasil atau semuanya dibatalkan."""
    conn = get_db()
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        current_app.logger.warning("Transaksi di-rollback", exc_info=True)
        raise


@click.command("init-db")
@click.option("--seed/--no-seed", default=True, help="Isi data contoh")
def init_db_command(seed):
    """Menjalankan migrasi skema lalu (opsional) mengisi data contoh."""
    from .migrate import migrate
    from .seed import seed_data

    applied = migrate(current_app.config["DATABASE"])
    click.echo(f"Migrasi diterapkan: {applied or 'tidak ada (sudah terbaru)'}")
    if seed:
        seed_data()
        click.echo("Data contoh dimasukkan.")


@click.command("migrate")
def migrate_command():
    """Menerapkan migrasi yang belum dijalankan (dengan backup otomatis)."""
    from .migrate import migrate

    applied = migrate(current_app.config["DATABASE"])
    click.echo(f"Migrasi diterapkan: {applied or 'tidak ada (sudah terbaru)'}")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(migrate_command)
