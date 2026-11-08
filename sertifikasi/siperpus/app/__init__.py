"""Application factory SIPERPUS."""
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask, render_template

from config import CONFIGS, DEFAULT_SECRET


def create_app(env=None, overrides=None):
    env = env or os.environ.get("APP_ENV", "development")
    if env not in CONFIGS:
        raise ValueError(f"APP_ENV tidak dikenal: {env}")

    app = Flask(__name__)
    app.config.from_object(CONFIGS[env])
    app.config["ENV_NAME"] = env
    if overrides:
        app.config.update(overrides)

    # Production tidak boleh berjalan dengan secret bawaan (J.620100.042.01 & J.62090.011.01)
    if env == "production" and app.config["SECRET_KEY"] == DEFAULT_SECRET:
        raise RuntimeError("SECRET_KEY wajib di-set lewat environment untuk production")

    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    _setup_logging(app)

    from . import db, monitoring, security
    from .views import admin, auth, katalog, sirkulasi

    db.init_app(app)
    security.init_app(app)
    monitoring.init_app(app)

    for bp in (auth.bp, katalog.bp, sirkulasi.bp, admin.bp):
        app.register_blueprint(bp)

    pesan_error = {400: "Permintaan tidak valid", 403: "Anda tidak memiliki hak akses",
                   404: "Halaman tidak ditemukan", 405: "Metode tidak diizinkan"}

    def client_error(e):
        return render_template("error.html", kode=e.code, pesan=pesan_error[e.code]), e.code

    for kode in pesan_error:
        app.register_error_handler(kode, client_error)

    @app.errorhandler(500)
    def server_error(e):
        # Detail error hanya masuk log, tidak ditampilkan ke pengguna (J.62090.011.01)
        app.logger.exception("Internal server error: %s", e)
        return render_template("error.html", kode=500, pesan="Terjadi kesalahan pada server"), 500

    app.logger.info("SIPERPUS v%s berjalan pada environment '%s'", app.config["VERSION"], env)
    return app


def _setup_logging(app):
    """Logging terstruktur untuk debugging (J.620100.025.02) & pemantauan (J.620100.045.01)."""
    level = getattr(logging, app.config["LOG_LEVEL"])
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    app.logger.setLevel(level)
    if app.config.get("LOG_FILE"):
        Path(app.config["LOG_FILE"]).parent.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(app.config["LOG_FILE"], maxBytes=1_000_000, backupCount=3)
        handler.setFormatter(fmt)
        handler.setLevel(level)
        app.logger.addHandler(handler)
