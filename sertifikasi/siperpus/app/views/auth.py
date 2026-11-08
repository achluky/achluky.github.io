from flask import Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from .. import repository as repo
from ..security import audit, catat_login_gagal, login_required, reset_login_gagal, terlalu_banyak_gagal

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        ip = request.remote_addr
        if terlalu_banyak_gagal(ip):
            audit("LOGIN_DIBLOKIR", f"ip={ip}")
            flash("Terlalu banyak percobaan gagal. Coba lagi beberapa menit lagi.", "error")
            return render_template("login.html"), 429

        username = request.form.get("username", "").strip()
        user = repo.get_user_by_username(username)
        if user is None or not check_password_hash(user["password_hash"], request.form.get("password", "")):
            catat_login_gagal(ip)
            audit("LOGIN_GAGAL", f"username={username}")
            # Pesan generik: tidak membocorkan apakah username terdaftar
            flash("Username atau password salah", "error")
            return render_template("login.html"), 401

        reset_login_gagal(ip)
        session.clear()  # cegah session fixation
        session.permanent = True
        session["user_id"] = user["id"]
        g.user = user
        audit("LOGIN", "berhasil")
        current_app.logger.info("Login: %s", username)
        tujuan = request.args.get("next", "")
        # Cegah open redirect: hanya path internal
        if not tujuan.startswith("/") or tujuan.startswith("//"):
            tujuan = url_for("katalog.dashboard")
        return redirect(tujuan)
    return render_template("login.html")


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    audit("LOGOUT")
    session.clear()
    return redirect(url_for("auth.login"))
