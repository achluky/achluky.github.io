from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from .. import repository as repo
from ..security import audit, login_required

bp = Blueprint("sirkulasi", __name__, url_prefix="/sirkulasi")


@bp.route("/")
@login_required
def index():
    return render_template("sirkulasi.html", aktif=repo.list_peminjaman_aktif(), anggota=repo.list_anggota(),
                           buku=repo.list_buku(), reservasi=repo.list_reservasi())


@bp.route("/pinjam", methods=["POST"])
@login_required
def pinjam():
    anggota_id = request.form.get("anggota_id", type=int)
    buku_id = request.form.get("buku_id", type=int)
    if not anggota_id or not buku_id:
        flash("Pilih anggota dan buku", "error")
        return redirect(url_for("sirkulasi.index"))
    try:
        pid = repo.pinjam_buku(anggota_id, buku_id, g.user["id"])
        audit("PINJAM", f"peminjaman={pid} anggota={anggota_id} buku={buku_id}")
        flash("Peminjaman berhasil dicatat", "ok")
    except repo.AturanBisnisError as e:
        flash(str(e), "error")
    return redirect(url_for("sirkulasi.index"))


@bp.route("/kembali/<int:peminjaman_id>", methods=["POST"])
@login_required
def kembali(peminjaman_id):
    try:
        denda, berikutnya = repo.kembalikan_buku(peminjaman_id)
        audit("KEMBALI", f"peminjaman={peminjaman_id} denda={denda}")
        pesan = f"Buku dikembalikan. Denda: Rp{denda:,}".replace(",", ".")
        if berikutnya:
            pesan += f" — buku ini direservasi, hubungi anggota id {berikutnya}"
        flash(pesan, "ok")
    except repo.AturanBisnisError as e:
        flash(str(e), "error")
    return redirect(url_for("sirkulasi.index"))


@bp.route("/reservasi", methods=["POST"])
@login_required
def reservasi():
    anggota_id = request.form.get("anggota_id", type=int)
    buku_id = request.form.get("buku_id", type=int)
    try:
        posisi = repo.buat_reservasi(anggota_id, buku_id)
        audit("RESERVASI", f"anggota={anggota_id} buku={buku_id}")
        flash(f"Reservasi tercatat, posisi antrian ke-{posisi}", "ok")
    except repo.AturanBisnisError as e:
        flash(str(e), "error")
    return redirect(request.referrer or url_for("sirkulasi.index"))
