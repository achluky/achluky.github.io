from flask import Blueprint, jsonify, render_template

from .. import repository as repo
from ..db import query
from ..monitoring import snapshot
from ..security import login_required, role_required

bp = Blueprint("admin", __name__)


@bp.route("/laporan")
@login_required
def laporan():
    return render_template("laporan.html", populer=repo.buku_terpopuler(), denda=repo.anggota_dengan_denda(),
                           per_bulan=repo.peminjaman_per_bulan(), tidak_dipinjam=repo.buku_tidak_pernah_dipinjam())


@bp.route("/admin/monitor")
@role_required("admin")
def monitor():
    versi = query("SELECT versi, nama, diterapkan_pada FROM schema_version ORDER BY versi")
    return render_template("monitor.html", m=snapshot(), versi=versi)


@bp.route("/admin/audit")
@role_required("admin")
def audit_log():
    return render_template("audit.html", log=repo.list_audit())


@bp.route("/health")
def health():
    """Health-check publik: hanya status, tanpa detail sensitif."""
    try:
        query("SELECT 1", one=True)
        return jsonify(status="ok", db="ok"), 200
    except Exception:
        return jsonify(status="error", db="down"), 503
