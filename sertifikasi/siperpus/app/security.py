"""Kontrol keamanan informasi.

Unit J.62090.011.01 - Menerapkan Standar-Standar Keamanan Informasi yang Berlaku
Acuan: OWASP Top 10 (2021) & ISO/IEC 27001:2022 Annex A.
  A01 Broken Access Control      -> login_required, role_required
  A02 Cryptographic Failures     -> hash password (scrypt/pbkdf2), cookie Secure/HttpOnly
  A03 Injection                  -> parameter binding (db.py), whitelist ORDER BY, autoescape Jinja2
  A05 Security Misconfiguration  -> security headers, secret wajib di production
  A07 Identification & Auth      -> pembatasan percobaan login, session timeout
  A09 Logging & Monitoring       -> audit_log
  CSRF                           -> token sinkron per sesi
"""
import hmac
import secrets
import time
from collections import defaultdict, deque
from functools import wraps

from flask import abort, current_app, flash, g, redirect, request, session, url_for

from .db import execute, query

# ip -> deque[timestamp gagal]  (struktur data untuk rate limiting)
_login_gagal = defaultdict(deque)


def init_app(app):
    app.before_request(_muat_user)
    app.before_request(_cek_csrf)
    app.after_request(_security_headers)
    app.context_processor(lambda: {"csrf_token": csrf_token, "user": g.get("user")})


# ------------------------------- Autentikasi -------------------------------
def _muat_user():
    g.user = None
    uid = session.get("user_id")
    if uid is not None:
        g.user = query("SELECT id, username, role FROM users WHERE id = ?", (uid,), one=True)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.get("user") is None:
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if g.user["role"] not in roles:
                audit("AKSES_DITOLAK", request.path)
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator


def terlalu_banyak_gagal(ip):
    cfg = current_app.config
    batas = time.time() - cfg["JEDA_LOGIN_GAGAL"]
    riwayat = _login_gagal[ip]
    while riwayat and riwayat[0] < batas:
        riwayat.popleft()
    return len(riwayat) >= cfg["MAX_LOGIN_GAGAL"]


def catat_login_gagal(ip):
    _login_gagal[ip].append(time.time())


def reset_login_gagal(ip):
    _login_gagal.pop(ip, None)


# ----------------------------------- CSRF ----------------------------------
def csrf_token():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_urlsafe(32)
    return session["_csrf"]


def _cek_csrf():
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        dikirim = request.form.get("_csrf") or request.headers.get("X-CSRF-Token", "")
        disimpan = session.get("_csrf", "")
        # BUG-02 (lihat docs/LOG_DEBUGGING.md): token kosong == token kosong dulu dianggap valid
        if not disimpan or not hmac.compare_digest(dikirim, disimpan):
            current_app.logger.warning("CSRF token tidak valid dari %s ke %s", request.remote_addr, request.path)
            abort(400, "CSRF token tidak valid")


# ----------------------------- Security headers ----------------------------
def _security_headers(resp):
    resp.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self'; img-src 'self' data:"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "same-origin"
    if current_app.config["SESSION_COOKIE_SECURE"]:
        resp.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return resp


# ------------------------------- Validasi input ----------------------------
def wajib(form, *fields):
    """Mengembalikan dict field -> nilai yang sudah di-strip, atau None (+flash) jika ada yang kosong."""
    data = {}
    for f in fields:
        nilai = (form.get(f) or "").strip()
        if not nilai:
            flash(f"Field '{f}' wajib diisi", "error")
            return None
        data[f] = nilai
    return data


# ---------------------------------- Audit ----------------------------------
def audit(aksi, detail=""):
    user = g.get("user")
    execute("INSERT INTO audit_log (user_id, aksi, detail, ip) VALUES (?, ?, ?, ?)",
            (user["id"] if user else None, aksi, detail[:500], request.remote_addr))
