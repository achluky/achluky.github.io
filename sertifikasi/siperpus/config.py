"""Konfigurasi aplikasi per environment.

Unit J.620100.042.01 - Melaksanakan Konfigurasi Perangkat Lunak Sesuai Environment
(Development, Staging, Production).

Environment dipilih lewat variabel APP_ENV (development | staging | production | testing).
Nilai rahasia (SECRET_KEY, DATABASE_PATH) dibaca dari environment variable / file .env,
tidak pernah ditulis langsung (hard-coded) untuk production.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
DEFAULT_SECRET = "dev-insecure-key-ganti-di-production"


def _load_dotenv(path=BASE_DIR / ".env"):
    """Loader .env sederhana (tanpa dependensi tambahan). Variabel OS tetap diutamakan."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()


class Config:
    APP_NAME = "SIPERPUS"
    VERSION = "1.1.0"
    SECRET_KEY = os.environ.get("SECRET_KEY", DEFAULT_SECRET)
    DATABASE = os.environ.get("DATABASE_PATH", str(INSTANCE_DIR / "perpus_dev.db"))
    DEBUG = False
    TESTING = False

    # Keamanan sesi (J.62090.011.01)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    PERMANENT_SESSION_LIFETIME = 30 * 60  # detik
    MAX_LOGIN_GAGAL = 5
    JEDA_LOGIN_GAGAL = 5 * 60  # detik

    # Logging & monitoring (J.620100.045.01)
    LOG_LEVEL = "INFO"
    LOG_FILE = str(INSTANCE_DIR / "app.log")
    SLOW_REQUEST_MS = 500
    SLOW_QUERY_MS = 100

    # Aturan bisnis
    LAMA_PINJAM_HARI = 7
    DENDA_PER_HARI = 1000
    DENDA_MAKSIMUM = 50000
    MAKS_PINJAM_AKTIF = 3


class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    SLOW_REQUEST_MS = 200


class StagingConfig(Config):
    DATABASE = os.environ.get("DATABASE_PATH", str(INSTANCE_DIR / "perpus_staging.db"))
    LOG_LEVEL = "INFO"


class ProductionConfig(Config):
    DATABASE = os.environ.get("DATABASE_PATH", str(INSTANCE_DIR / "perpus_prod.db"))
    LOG_LEVEL = "WARNING"
    SESSION_COOKIE_SECURE = True  # wajib HTTPS


class TestingConfig(Config):
    TESTING = True
    LOG_LEVEL = "DEBUG"
    LOG_FILE = None


CONFIGS = {
    "development": DevelopmentConfig,
    "staging": StagingConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
