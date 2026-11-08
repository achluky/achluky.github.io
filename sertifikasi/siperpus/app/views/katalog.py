from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from .. import algorithms as algo
from .. import repository as repo
from ..security import audit, login_required, role_required, wajib

bp = Blueprint("katalog", __name__)


@bp.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html", stat=repo.statistik_dashboard(),
                           aktif=repo.list_peminjaman_aktif()[:5])


@bp.route("/buku")
@login_required
def buku_list():
    keyword = request.args.get("q", "").strip()[:100]
    kategori_id = request.args.get("kategori", type=int)
    urut = request.args.get("urut", "judul")
    return render_template("buku_list.html", buku=repo.list_buku(keyword, kategori_id, urut),
                           kategori=repo.list_kategori(), q=keyword, kat=kategori_id, urut=urut)


@bp.route("/buku/<int:buku_id>")
@login_required
def buku_detail(buku_id):
    buku = repo.get_buku(buku_id) or abort(404)
    return render_template("buku_detail.html", buku=buku, rekomendasi=repo.rekomendasi_untuk(buku_id),
                           antrian=len(repo.antrian_reservasi(buku_id)), anggota=repo.list_anggota())


def _validasi_buku(form, buku_id=None):
    data = wajib(form, "isbn", "judul", "penulis", "kategori_id")
    if data is None:
        return None
    data["isbn"] = algo.normalisasi_isbn(data["isbn"])
    data["penerbit"] = form.get("penerbit", "").strip() or None
    try:
        data["kategori_id"] = int(data["kategori_id"])
        data["tahun"] = int(form.get("tahun") or 0) or None
        data["stok"] = int(form.get("stok") or 0)
    except ValueError:
        flash("Tahun, stok, dan kategori harus berupa angka", "error")
        return None
    if not algo.validasi_isbn13(data["isbn"]):
        flash("ISBN-13 tidak valid (checksum salah)", "error")
        return None
    if repo.isbn_sudah_ada(data["isbn"], buku_id):
        flash("ISBN sudah terdaftar", "error")
        return None
    if data["stok"] < 0:
        flash("Stok tidak boleh negatif", "error")
        return None
    return data


@bp.route("/buku/baru", methods=["GET", "POST"])
@bp.route("/buku/<int:buku_id>/edit", methods=["GET", "POST"])
@role_required("admin")
def buku_form(buku_id=None):
    buku = repo.get_buku(buku_id) if buku_id else None
    if buku_id and buku is None:
        abort(404)
    if request.method == "POST":
        data = _validasi_buku(request.form, buku_id)
        if data:
            bid = repo.simpan_buku(data, buku_id)
            audit("BUKU_UBAH" if buku_id else "BUKU_TAMBAH", f"id={bid} isbn={data['isbn']}")
            flash("Data buku tersimpan", "ok")
            return redirect(url_for("katalog.buku_detail", buku_id=bid))
        buku = request.form
    return render_template("buku_form.html", buku=buku, kategori=repo.list_kategori(), buku_id=buku_id)


@bp.route("/buku/<int:buku_id>/hapus", methods=["POST"])
@role_required("admin")
def buku_hapus(buku_id):
    try:
        repo.hapus_buku(buku_id)
        audit("BUKU_HAPUS", f"id={buku_id}")
        flash("Buku dihapus", "ok")
    except repo.AturanBisnisError as e:
        flash(str(e), "error")
        return redirect(url_for("katalog.buku_detail", buku_id=buku_id))
    return redirect(url_for("katalog.buku_list"))


@bp.route("/anggota", methods=["GET", "POST"])
@login_required
def anggota():
    if request.method == "POST":
        data = wajib(request.form, "no_anggota", "nama")
        if data:
            try:
                repo.tambah_anggota(data["no_anggota"], data["nama"],
                                    request.form.get("email", "").strip(), request.form.get("telepon", "").strip())
                audit("ANGGOTA_TAMBAH", data["no_anggota"])
                flash("Anggota ditambahkan", "ok")
            except repo.AturanBisnisError as e:
                flash(str(e), "error")
        return redirect(url_for("katalog.anggota"))
    return render_template("anggota.html", anggota=repo.list_anggota())
