"""Pemantauan resource aplikasi.

Unit J.620100.045.01 - Melakukan Pemantauan Resource Yang Digunakan Aplikasi
- waktu respons tiap request (rata-rata, p95, request lambat),
- waktu eksekusi query + log slow query,
- memori & CPU proses (psutil bila tersedia, fallback modul `resource`),
- ukuran file database & disk,
- endpoint /health untuk health-check (load balancer / uptime monitor).
"""
import os
import platform
import shutil
import time
from collections import Counter, deque

from flask import current_app, g, request

_mulai = time.time()
_requests = deque(maxlen=1000)   # (endpoint, status, ms)
_queries = deque(maxlen=1000)    # (sql, ms)
_slow_queries = deque(maxlen=50)

try:
    import psutil
except ImportError:  # psutil opsional
    psutil = None


def init_app(app):
    app.before_request(_mulai_timer)
    app.after_request(_catat_request)


def _mulai_timer():
    g._t0 = time.perf_counter()


def _catat_request(resp):
    if "_t0" not in g:
        return resp
    ms = (time.perf_counter() - g._t0) * 1000
    _requests.append((request.endpoint or request.path, resp.status_code, ms))
    resp.headers["X-Response-Time-ms"] = f"{ms:.1f}"
    if ms > current_app.config["SLOW_REQUEST_MS"]:
        current_app.logger.warning("Request lambat %.1f ms: %s %s", ms, request.method, request.path)
    return resp


def record_query(sql, ms):
    _queries.append((sql, ms))
    try:
        batas = current_app.config["SLOW_QUERY_MS"]
    except RuntimeError:
        return
    if ms > batas:
        ringkas = " ".join(sql.split())[:200]
        _slow_queries.append((time.strftime("%H:%M:%S"), ringkas, round(ms, 1)))
        current_app.logger.warning("Slow query %.1f ms: %s", ms, ringkas)


def _persentil(nilai, p):
    if not nilai:
        return 0.0
    urut = sorted(nilai)
    return urut[min(len(urut) - 1, int(round(p / 100 * (len(urut) - 1))))]


def _memori_proses_mb():
    if psutil:
        return psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
    import resource
    maxrss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # Linux: KB, macOS: byte
    return maxrss / 1024 / 1024 if platform.system() == "Darwin" else maxrss / 1024


def snapshot():
    db_path = current_app.config["DATABASE"]
    waktu = [ms for _, _, ms in _requests]
    q_waktu = [ms for _, ms in _queries]
    disk = shutil.disk_usage(os.path.dirname(os.path.abspath(db_path)))
    per_endpoint = Counter(ep for ep, _, _ in _requests)
    error = sum(1 for _, s, _ in _requests if s >= 500)
    return {
        "versi": current_app.config["VERSION"],
        "environment": current_app.config["ENV_NAME"],
        "uptime_detik": int(time.time() - _mulai),
        "pid": os.getpid(),
        "memori_mb": round(_memori_proses_mb(), 1),
        "cpu_persen": psutil.Process(os.getpid()).cpu_percent(interval=0.1) if psutil else None,
        "db_mb": round(os.path.getsize(db_path) / 1024 / 1024, 3) if os.path.exists(db_path) else 0,
        "disk_bebas_gb": round(disk.free / 1024 ** 3, 1),
        "disk_terpakai_persen": round(disk.used / disk.total * 100, 1),
        "jumlah_request": len(waktu),
        "error_5xx": error,
        "rata_ms": round(sum(waktu) / len(waktu), 1) if waktu else 0,
        "p95_ms": round(_persentil(waktu, 95), 1),
        "jumlah_query": len(q_waktu),
        "rata_query_ms": round(sum(q_waktu) / len(q_waktu), 2) if q_waktu else 0,
        "endpoint_teramai": per_endpoint.most_common(5),
        "slow_queries": list(_slow_queries)[-10:],
    }
