"""
Hands-on — Preparing for Production: QA, Risk, Security & Compliance dengan MLflow
==================================================================================

Mata kuliah : Machine Learning Operations (MLOps) — Minggu 7
Kasus       : Deteksi tumor ganas (Breast Cancer Wisconsin) — LANJUTAN Hands-on 2 Minggu 6

Pertanyaan utama: model @challenger di MLflow Model Registry sudah "akurat",
tetapi apakah ia SIAP PRODUKSI?

Alur (sesuai slide):
    P0  Target          ambil model @challenger dari registry M6 (atau latih kandidat baru)
    P1  Lineage         run asal, git commit, data_md5, signature, requirements
    P2  Data QA         data contract (schema, range, null, duplikat), drift (PSI), leakage
    P3  Model QA        mlflow.models.evaluate + non-regresi vs champion + slice
                        + calibration + robustness + behavioral test (MFT/INV/DIR) + latency
    P4  Risk            risk tiering + risk register (likelihood x impact) terhubung ke hasil tes
    P5  Security        format serialisasi, scan opcode pickle, SHA-256 manifest (integritas),
                        dependensi ter-pin + pip-audit (opsional)
    P6  Compliance      scan PII, model card otomatis dari metadata MLflow, persetujuan manusia
    P7  Release gate    gate_report -> tag di model version -> promosi @champion / tolak / pending
    P8  Guarded serving model pembungkus (validasi input, cek integritas, human review)
                        diregistrasi sebagai "<model>-guarded" via Models from Code

Semua hasil tercatat di MLflow:
    * experiment "bc-production-readiness" -> 1 run per pemeriksaan (metrik + artefak per fase)
    * tag pada MODEL VERSION -> status QA/security/compliance, risk tier, approver (audit trail)

Setup:
    python -m venv .venv && source .venv/bin/activate
    pip install "mlflow>=3" scikit-learn pandas matplotlib requests
    pip install pip-audit                                         # opsional, untuk P5

Menjalankan (dari folder yang SAMA dengan mlflow.db Minggu 6, atau set MLFLOW_TRACKING_URI):
    # 0) Bila registry belum ada, jalankan Hands-on 2 Minggu 6 terlebih dahulu
    python ../model_xperimentation_and_tracking/hands_on_2_end_to_end.py

    # 1) Uji @challenger dari Minggu 6 (SVC)       -> REJECTED (recall & slice "tumor sedang")
    python hands_on_production_readiness.py
    # 2) Kandidat dengan threshold di-tuning (F2)  -> lulus uji teknis, PENDING approval
    python hands_on_production_readiness.py --new-candidate logreg-f2
    # 3) Persetujuan pemilik risiko                -> APPROVED, @champion + model -guarded (P8)
    python hands_on_production_readiness.py --approver "dr. Sari (Model Risk Committee)"
    # Lainnya
    python hands_on_production_readiness.py --new-candidate rf        # bandingkan kandidat lain
    python hands_on_production_readiness.py --demo-malicious-pickle   # demo deteksi pickle berbahaya
    python hands_on_production_readiness.py --rollback --reason "drift"  # kembalikan @champion lama
    mlflow ui --backend-store-uri sqlite:///mlflow.db

Diuji dengan: MLflow 3.17, scikit-learn 1.9 (butuh sklearn >= 1.5 untuk TunedThresholdClassifierCV).
Catatan: gate SENGAJA tidak mempromosikan model Tier 1 (kesehatan) tanpa --approver.
Itu bentuk "human oversight" yang diwajibkan regulasi untuk sistem berisiko tinggi.
"""

import argparse
import hashlib
import json
import os
import pickle
import pickletools
import shutil
import subprocess
import time
import warnings
from datetime import datetime, timezone

import matplotlib

matplotlib.use("Agg")
import mlflow
import numpy as np
import pandas as pd
import yaml
from mlflow import MlflowClient
from mlflow.models import infer_signature
from sklearn.calibration import CalibrationDisplay
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, fbeta_score, make_scorer, recall_score
from sklearn.model_selection import StratifiedKFold, TunedThresholdClassifierCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT_NAME = "bc-production-readiness"
MODEL_NAME = "bc-malignant-classifier"       # sama dengan Minggu 6
GUARDED_NAME = f"{MODEL_NAME}-guarded"
DATA_DIR = "data"
SEED = 42

# -----------------------------------------------------------------------------
# KEBIJAKAN RILIS — ditulis SEBELUM pengujian, disetujui pemilik risiko.
# Mengubah angka di sini = mengubah kebijakan (harus lewat review, bukan "biar lulus").
# -----------------------------------------------------------------------------
POLICY = {
    "min_test_recall": 0.93,          # optimizing metric (false negative mahal)
    "min_test_precision": 0.90,       # satisficing metric (sama dengan Minggu 6)
    "max_regression_vs_champion": 0.01,
    "min_slice_recall": 0.85,         # tidak boleh ada kelompok ukuran tumor yang "dikorbankan"
    "min_slice_support": 5,
    "max_flip_rate_noise_1pct": 0.02, # robustness
    "max_brier": 0.10,                # calibration (warning)
    "max_psi": 0.20,                  # drift train vs test (warning)
    "max_feature_target_corr": 0.95,  # indikasi leakage (blocker)
    "max_p95_latency_ms": 50,
    "max_model_size_mb": 50,
    "review_margin": 0.15,            # |skor - threshold| <= 0.15 -> zona abu-abu, dicek dokter
}

# Profil penggunaan model -> dasar risk tiering (P4)
USE_CASE = {
    "domain": "kesehatan",
    "decision": "rekomendasi skrining untuk dokter (bukan diagnosis final)",
    "affects_fundamental_rights": True,     # akses layanan kesehatan
    "fully_automated": False,               # dokter tetap memutuskan
    "personal_data": "data kesehatan (data pribadi spesifik, UU PDP Pasal 4)",
    "legal_basis": "persetujuan pasien + kepentingan layanan kesehatan; data latih: dataset publik teranonimisasi",
    "users": "dokter & radiolog rumah sakit mitra",
}

# skops hanya memuat tipe yang ada di whitelist ini (selain tipe dasar sklearn/numpy).
# Menambah tipe = keputusan keamanan -> review, jangan asal salin pesan error.
SKOPS_TRUSTED = [
    "sklearn.tree._tree.Tree",                                   # rf, gb
    "sklearn._loss.loss.HalfBinomialLoss", "sklearn._loss.link.LogitLink",
    "sklearn._loss.link.Interval",                               # gb
    "sklearn.metrics._classification.fbeta_score", "sklearn.metrics._scorer._Scorer",
    "sklearn.metrics._scorer._CurveScorer", "sklearn.model_selection._split.StratifiedKFold",
    "sklearn.utils._metadata_requests.MetadataRequest",
    "sklearn.utils._metadata_requests.MethodMetadataRequest",   # logreg-f2 (threshold tuning)
]

DANGEROUS_GLOBALS = {"os", "posix", "nt", "subprocess", "sys", "socket", "shutil", "pty",
                     "importlib", "runpy", "webbrowser", "requests", "urllib"}
DANGEROUS_BUILTINS = {"eval", "exec", "compile", "open", "__import__", "getattr", "breakpoint"}


# =============================================================================
# Utilitas pencatatan hasil pemeriksaan
# severity "blocker" -> gagal = rilis diblokir; "warning" -> dicatat, tidak memblokir
# =============================================================================
CHECKS = []


def sha256_dir(path):
    """Hash setiap file artefak model (sama dengan guarded_model.sha256_dir)."""
    manifest = {}
    for root, _, files in os.walk(path):
        for name in sorted(files):
            full = os.path.join(root, name)
            with open(full, "rb") as f:
                manifest[os.path.relpath(full, path)] = hashlib.sha256(f.read()).hexdigest()
    return dict(sorted(manifest.items()))


def check(phase, name, passed, detail="", severity="blocker"):
    CHECKS.append({"phase": phase, "check": name, "passed": bool(passed),
                   "severity": severity, "detail": str(detail)})
    icon = "✓" if passed else ("✗" if severity == "blocker" else "⚠")
    print(f"  {icon} [{severity:<7}] {name:<38} {detail}")
    return passed


def phase_status(phase):
    rows = [c for c in CHECKS if c["phase"] == phase]
    if any(not c["passed"] and c["severity"] == "blocker" for c in rows):
        return "failed"
    return "passed_with_warnings" if any(not c["passed"] for c in rows) else "passed"


def setup_tracking():
    if not os.environ.get("MLFLOW_TRACKING_URI"):
        mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment(EXPERIMENT_NAME)
    print(f"[setup] tracking URI : {mlflow.get_tracking_uri()}")
    print(f"[setup] experiment   : {EXPERIMENT_NAME}")


def prepare_data():
    """Identik dengan L1 Minggu 6 -> data_md5 & test set harus SAMA persis."""
    df = load_breast_cancer(as_frame=True).frame
    df["target"] = 1 - df["target"]  # 1 = malignant
    data_md5 = hashlib.md5(pd.util.hash_pandas_object(df, index=True).values).hexdigest()
    train_df, test_df = train_test_split(df, test_size=0.2, stratify=df["target"],
                                         random_state=SEED)
    return train_df, test_df, data_md5


def score_of(model, X):
    """Skor kelas positif di (0, 1): predict_proba bila ada, jika tidak sigmoid(decision)."""
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)[:, 1]
    return 1.0 / (1.0 + np.exp(-model.decision_function(X)))


# =============================================================================
# P0 — TARGET: model mana yang akan diuji kesiapan produksinya?
# =============================================================================
def step_new_candidate(family, train_df, data_md5):
    """Latih kandidat baru (gaya Minggu 6) lalu daftarkan sebagai @challenger."""
    print(f"[P0] Melatih kandidat baru: {family}")
    clf = {"logreg": LogisticRegression(max_iter=5000),
           "logreg-f2": LogisticRegression(max_iter=5000),
           "rf": RandomForestClassifier(n_estimators=200, random_state=SEED),
           "gb": GradientBoostingClassifier(random_state=SEED)}[family]
    pipe = Pipeline([("scaler", StandardScaler()), ("clf", clf)])
    if family == "logreg-f2":
        # Skrining medis: false negative jauh lebih mahal -> geser decision threshold.
        # Threshold dipilih dengan CV di data LATIH (memaksimalkan F2 = recall dibobot 2x),
        # bukan dengan mengintip test set.
        pipe = TunedThresholdClassifierCV(
            pipe, scoring=make_scorer(fbeta_score, beta=2),
            cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED))
    X, y = train_df.drop(columns="target"), train_df["target"]

    mlflow.set_experiment("bc-malignant-detection")  # experiment training Minggu 6
    with mlflow.start_run(run_name=f"20-{family}-candidate-m7",
                          tags={"data_md5": data_md5, "split_seed": str(SEED),
                                "dataset": "sklearn-breast-cancer", "stage": "candidate-m7",
                                "model_family": family}) as run:
        mlflow.log_input(mlflow.data.from_pandas(train_df, source=f"{DATA_DIR}/train.csv",
                                                 name="bc-train", targets="target"),
                         context="training")
        mlflow.log_params({f"clf__{k}": v for k, v in clf.get_params().items()})
        pipe.fit(X, y)
        if hasattr(pipe, "best_threshold_"):
            mlflow.log_param("decision_threshold", round(float(pipe.best_threshold_), 4))
        info = mlflow.sklearn.log_model(
            pipe, name="model", signature=infer_signature(X, pipe.predict(X)),
            input_example=X.head(3),
            skops_trusted_types=SKOPS_TRUSTED,  # whitelist eksplisit, sudah di-review
        )
        mlflow.set_tag("model_uri", info.model_uri)
    mlflow.set_experiment(EXPERIMENT_NAME)

    client = MlflowClient()
    mv = mlflow.register_model(info.model_uri, MODEL_NAME)
    client.set_model_version_tag(MODEL_NAME, mv.version, "data_md5", data_md5)
    client.set_registered_model_alias(MODEL_NAME, "challenger", mv.version)
    print(f"  -> terdaftar sebagai {MODEL_NAME} v{mv.version} @challenger (run {run.info.run_id})")


def resolve_target(client, version):
    if version:
        return client.get_model_version(MODEL_NAME, str(version))
    try:
        return client.get_model_version_by_alias(MODEL_NAME, "challenger")
    except Exception:
        raise SystemExit(
            f"Model '{MODEL_NAME}@challenger' tidak ditemukan di {mlflow.get_tracking_uri()}.\n"
            "Jalankan dulu Hands-on 2 Minggu 6, atau pakai --new-candidate logreg.")


def get_champion(client):
    try:
        return client.get_model_version_by_alias(MODEL_NAME, "champion")
    except Exception:
        return None


# =============================================================================
# P1 — LINEAGE & REPRODUCIBILITY
# "Dari mana model ini berasal?" harus terjawab dari metadata, bukan ingatan.
# =============================================================================
def step_lineage(client, mv, model_dir, data_md5):
    print("[P1] Lineage & reproducibility")
    run = client.get_run(mv.run_id)
    tags = run.data.tags

    check("lineage", "Run training tercatat", run is not None, f"run_id={mv.run_id}")
    check("lineage", "data_md5 tercatat & cocok",
          tags.get("data_md5") == data_md5,
          f"tercatat={tags.get('data_md5', '-')[:10]}… sekarang={data_md5[:10]}…")
    commit = tags.get("mlflow.source.git.commit")
    check("lineage", "Git commit tercatat", commit is not None,
          commit[:10] if commit else "jalankan training dari dalam repo Git", severity="warning")

    with open(os.path.join(model_dir, "MLmodel")) as f:
        mlmodel = yaml.safe_load(f)
    check("lineage", "Signature (kontrak input/output)", "signature" in mlmodel,
          "ada" if "signature" in mlmodel else "tidak ada -> input tidak divalidasi saat serving")
    check("lineage", "Environment terdokumentasi",
          os.path.exists(os.path.join(model_dir, "requirements.txt")),
          "requirements.txt + conda.yaml + python_env.yaml")

    mlflow.log_dict({"model": f"{MODEL_NAME}/v{mv.version}", "training_run_id": mv.run_id,
                     "git_commit": commit, "data_md5": tags.get("data_md5"),
                     "params": run.data.params, "training_metrics": run.data.metrics},
                    "p1_lineage/lineage.json")
    return run, mlmodel


# =============================================================================
# P2 — DATA QA
# Data contract diturunkan dari data training -> juga dipakai guardrail serving (P8).
# =============================================================================
def build_contract(train_df):
    X = train_df.drop(columns="target")
    return {
        "columns": list(X.columns),
        "dtypes": {c: "float64" for c in X.columns},
        "ranges": {c: [float(X[c].min()), float(X[c].max())] for c in X.columns},
        "range_tolerance": 0.10,                    # 10% dari rentang: operating envelope
        "target_values": [0, 1],
        "positive_ratio": [0.20, 0.50],
        "review_margin": POLICY["review_margin"],
    }


def psi(expected, actual, bins=10):
    """Population Stability Index: < 0.1 stabil, 0.1–0.2 sedang, > 0.2 bergeser signifikan."""
    edges = np.unique(np.quantile(expected, np.linspace(0, 1, bins + 1)))
    edges[0], edges[-1] = -np.inf, np.inf
    e = np.histogram(expected, edges)[0] / len(expected) + 1e-6
    a = np.histogram(actual, edges)[0] / len(actual) + 1e-6
    return float(np.sum((a - e) * np.log(a / e)))


def step_data_qa(train_df, test_df, contract):
    print("[P2] Data QA")
    for name, df in [("train", train_df), ("test", test_df)]:
        X = df[contract["columns"]]
        missing = set(contract["columns"]) - set(df.columns)
        check("data_qa", f"[{name}] schema lengkap", not missing, f"{len(df.columns)} kolom")
        check("data_qa", f"[{name}] tipe numerik",
              all(pd.api.types.is_float_dtype(X[c]) for c in X), "float64")
        check("data_qa", f"[{name}] tanpa null", X.isna().sum().sum() == 0,
              f"null={int(X.isna().sum().sum())}")
        check("data_qa", f"[{name}] nilai tidak negatif", (X >= 0).all().all(),
              "ukuran fisik tumor >= 0")
        check("data_qa", f"[{name}] label valid",
              df["target"].isin(contract["target_values"]).all(), "{0, 1}")
        ratio = df["target"].mean()
        lo, hi = contract["positive_ratio"]
        check("data_qa", f"[{name}] proporsi malignant wajar", lo <= ratio <= hi, f"{ratio:.2%}")
        dup = int(df.duplicated().sum())
        check("data_qa", f"[{name}] tanpa duplikat", dup == 0, f"duplikat={dup}",
              severity="warning")

    overlap = len(pd.merge(train_df, test_df, how="inner"))
    check("data_qa", "Tidak ada baris train bocor ke test", overlap == 0, f"overlap={overlap}")

    corr = train_df.corr(numeric_only=True)["target"].drop("target").abs()
    check("data_qa", "Tidak ada fitur 'membocorkan' label",
          corr.max() < POLICY["max_feature_target_corr"],
          f"korelasi maks={corr.max():.2f} ({corr.idxmax()})")

    drift = {c: psi(train_df[c].values, test_df[c].values) for c in contract["columns"]}
    worst = max(drift, key=drift.get)
    check("data_qa", "Distribusi train vs test stabil (PSI)",
          drift[worst] < POLICY["max_psi"], f"PSI maks={drift[worst]:.3f} ({worst})",
          severity="warning")

    mlflow.log_dict(contract, "p2_data_qa/data_contract.json")
    mlflow.log_dict(drift, "p2_data_qa/psi_train_vs_test.json")
    mlflow.log_metric("data_psi_max", drift[worst])
    mlflow.log_metric("data_max_feature_target_corr", float(corr.max()))


# =============================================================================
# P3 — MODEL QA
# =============================================================================
def step_model_qa(client, mv, champion, test_df, contract):
    print("[P3] Model QA")
    model_uri = f"models:/{MODEL_NAME}/{mv.version}"
    model = mlflow.sklearn.load_model(model_uri)
    X_test, y_test = test_df[contract["columns"]], test_df["target"]
    y_pred = model.predict(X_test)
    score = score_of(model, X_test)

    # (a) Evaluasi standar MLflow: metrik + confusion matrix + ROC/PR curve sebagai artefak
    result = mlflow.models.evaluate(
        model_uri, data=test_df, targets="target", model_type="classifier",
        evaluators="default", evaluator_config={"log_model_explainability": False},
    )
    recall, precision = result.metrics["recall_score"], result.metrics["precision_score"]
    check("model_qa", "Recall test >= kebijakan", recall >= POLICY["min_test_recall"],
          f"{recall:.3f} (min {POLICY['min_test_recall']})")
    check("model_qa", "Precision test >= kebijakan", precision >= POLICY["min_test_precision"],
          f"{precision:.3f} (min {POLICY['min_test_precision']})")

    # (b) Non-regresi terhadap champion (dievaluasi pada test set yang SAMA)
    if champion and champion.version != mv.version:
        champ = mlflow.sklearn.load_model(f"models:/{MODEL_NAME}/{champion.version}")
        champ_recall = recall_score(y_test, champ.predict(X_test))
        check("model_qa", "Tidak lebih buruk dari champion",
              recall >= champ_recall - POLICY["max_regression_vs_champion"],
              f"challenger={recall:.3f} champion v{champion.version}={champ_recall:.3f}")
        mlflow.log_metric("champion_recall", champ_recall)
    else:
        check("model_qa", "Tidak lebih buruk dari champion", True,
              "tidak ada champion lain (model ini sendiri/pertama)", severity="warning")

    # (c) Slice-based evaluation: performa per kelompok ukuran tumor
    size = pd.qcut(test_df["mean radius"], 3, labels=["kecil", "sedang", "besar"])
    rows = []
    for s in size.cat.categories:
        m = (size == s).values
        pos = int(y_test[m].sum())
        r = recall_score(y_test[m], y_pred[m]) if pos else float("nan")
        rows.append({"slice": f"tumor_{s}", "n": int(m.sum()), "n_malignant": pos, "recall": r})
        if pos >= POLICY["min_slice_support"]:
            check("model_qa", f"Recall slice tumor_{s}", r >= POLICY["min_slice_recall"],
                  f"{r:.3f} (n_malignant={pos})")
            mlflow.log_metric(f"slice_recall_tumor_{s}", r)
        else:
            check("model_qa", f"Recall slice tumor_{s}", False,
                  f"support terlalu kecil (n_malignant={pos}) -> butuh data tambahan",
                  severity="warning")
    mlflow.log_table(pd.DataFrame(rows), "p3_model_qa/slice_metrics.json")

    # (d) Calibration: bisakah skor dibaca sebagai probabilitas?
    brier = brier_score_loss(y_test, score)
    check("model_qa", "Kalibrasi (Brier score)", brier <= POLICY["max_brier"],
          f"{brier:.3f}" + ("" if hasattr(model, "predict_proba") else " (skor dari sigmoid)"),
          severity="warning")
    disp = CalibrationDisplay.from_predictions(y_test, score, n_bins=5)
    mlflow.log_figure(disp.figure_, "p3_model_qa/calibration_curve.png")
    mlflow.log_metric("brier_score", brier)

    # (e) Robustness: noise kecil (1% std fitur) tidak boleh mengubah banyak prediksi
    rng = np.random.default_rng(SEED)
    std = X_test.std()
    for pct in [0.01, 0.05]:
        noisy = X_test + rng.normal(0, 1, X_test.shape) * (pct * std.values)
        flip = float((model.predict(noisy.clip(lower=0)) != y_pred).mean())
        mlflow.log_metric(f"flip_rate_noise_{int(pct * 100)}pct", flip)
        if pct == 0.01:
            check("model_qa", "Robust terhadap noise 1%",
                  flip <= POLICY["max_flip_rate_noise_1pct"], f"flip rate={flip:.2%}")
        else:
            print(f"    (info) flip rate noise 5% = {flip:.2%}")

    # (f) Behavioral testing ala CheckList
    malignant = test_df[test_df["target"] == 1]
    extreme = malignant.nlargest(5, "worst area")[contract["columns"]]
    check("model_qa", "MFT: tumor sangat besar -> malignant",
          (model.predict(extreme) == 1).all(), "5 kasus paling ekstrem")

    shuffled = X_test.sample(frac=1.0, random_state=SEED)
    inv_batch = (pd.Series(model.predict(shuffled), index=shuffled.index)
                 .sort_index().values == pd.Series(y_pred, index=X_test.index).sort_index().values)
    check("model_qa", "INV: urutan/batch tidak memengaruhi hasil", inv_batch.all(),
          "prediksi batch acak == batch asli")

    pyfunc = mlflow.pyfunc.load_model(model_uri)
    reordered = X_test[X_test.columns[::-1]]           # kolom dibalik urutannya
    same = (np.asarray(pyfunc.predict(reordered)) == y_pred).all()
    check("model_qa", "INV: urutan kolom (via signature)", same,
          "pyfunc menyusun ulang kolom berdasarkan nama")

    benign = test_df[test_df["target"] == 0][contract["columns"]]
    bigger = benign.copy()
    for c in ["worst area", "worst radius", "worst concave points"]:
        bigger[c] *= 1.2
    dir_ok = float((score_of(model, bigger) >= score_of(model, benign) - 1e-9).mean())
    check("model_qa", "DIR: tumor membesar -> skor tidak turun", dir_ok >= 0.90,
          f"{dir_ok:.0%} kasus konsisten (min 90%)")

    # (g) Efisiensi: latensi 1 request & ukuran artefak
    row = X_test.head(1)
    lat = []
    for _ in range(200):
        t0 = time.perf_counter()
        pyfunc.predict(row)
        lat.append((time.perf_counter() - t0) * 1000)
    p95 = float(np.percentile(lat, 95))
    check("model_qa", "Latensi p95 (1 baris, pyfunc)", p95 <= POLICY["max_p95_latency_ms"],
          f"{p95:.1f} ms (maks {POLICY['max_p95_latency_ms']})")
    mlflow.log_metrics({"latency_p50_ms": float(np.percentile(lat, 50)), "latency_p95_ms": p95,
                        "test_recall": recall, "test_precision": precision})
    return {"recall": recall, "precision": precision, "brier": brier, "slices": rows}


# =============================================================================
# P4 — RISK: tiering + risk register yang TERHUBUNG ke hasil pengujian
# =============================================================================
def risk_tier(use_case):
    if use_case["affects_fundamental_rights"] or use_case["domain"] in {"kesehatan", "kredit", "rekrutmen"}:
        return "Tier 1 (tinggi)"
    return "Tier 2 (sedang)" if use_case["personal_data"] else "Tier 3 (rendah)"


def step_risk():
    print("[P4] Risk assessment")
    tier = risk_tier(USE_CASE)
    print(f"  Risk tier: {tier} — {USE_CASE['domain']}, {USE_CASE['decision']}")

    def ok(*names):  # kontrol dianggap efektif bila semua pemeriksaan terkait lulus
        rel = [c for c in CHECKS if any(n in c["check"] for n in names)]
        return bool(rel) and all(c["passed"] for c in rel)

    register = [
        ("R1", "Tumor ganas terlewat (false negative)", 3, 5,
         "Recall >= kebijakan, human review zona abu-abu", ok("Recall test")),
        ("R2", "Performa buruk pada kelompok tumor tertentu", 3, 4,
         "Uji per slice ukuran tumor", ok("Recall slice")),
        ("R3", "Data produksi di luar rentang data latih", 4, 4,
         "Data contract + guardrail serving (P8)", ok("schema", "negatif")),
        ("R4", "Model/artefak dimodifikasi pihak tak berwenang", 2, 5,
         "SHA-256 manifest + format aman", ok("Integritas", "Format serialisasi", "pickle")),
        ("R5", "Library dengan kerentanan (CVE)", 3, 3,
         "Dependensi ter-pin + pip-audit", ok("Dependensi")),
        ("R6", "Skor disalahartikan sebagai diagnosis final", 3, 5,
         "Model card (intended use) + keputusan tetap di tangan dokter", ok("otomatis penuh")),
        ("R7", "Kebocoran data pasien", 2, 5,
         "Scan PII, output dibulatkan, tanpa logging data mentah", ok("PII")),
    ]
    rows = []
    for rid, risk, L, I, mitigation, effective in register:
        residual = L * I if not effective else max(1, (L - 2)) * I
        rows.append({"id": rid, "risiko": risk, "L": L, "I": I, "skor_inheren": L * I,
                     "mitigasi": mitigation, "kontrol_efektif": effective,
                     "skor_residual": residual})
    df = pd.DataFrame(rows)
    print(df[["id", "risiko", "skor_inheren", "kontrol_efektif", "skor_residual"]]
          .to_string(index=False))
    mlflow.log_table(df, "p4_risk/risk_register.json")
    mlflow.log_dict({"tier": tier, "use_case": USE_CASE}, "p4_risk/risk_tier.json")
    mlflow.log_metric("risk_residual_max", int(df["skor_residual"].max()))
    high = df[df["skor_residual"] >= 15]
    check("risk", "Tidak ada risiko residual tinggi (>=15)", high.empty,
          "semua risiko termitigasi" if high.empty else f"{list(high['id'])}")
    return tier, df


# =============================================================================
# P5 — SECURITY
# =============================================================================
def scan_pickle(path):
    """Pindai opcode pickle TANPA memuatnya. Kembalikan daftar import berbahaya."""
    findings, strings = [], []
    with open(path, "rb") as f:
        for op, arg, _ in pickletools.genops(f):
            if op.name in {"SHORT_BINUNICODE", "BINUNICODE", "UNICODE", "BINUNICODE8"}:
                strings.append(arg)
            elif op.name in {"GLOBAL", "INST"}:
                module, name = arg.split(" ", 1)
                findings.append((module, name))
            elif op.name == "STACK_GLOBAL" and len(strings) >= 2:
                findings.append((strings[-2], strings[-1]))
    return [f"{m}.{n}" for m, n in findings
            if m.split(".")[0] in DANGEROUS_GLOBALS
            or (m == "builtins" and n in DANGEROUS_BUILTINS)]


def step_security(client, mv, model_dir, mlmodel):
    print("[P5] Security")
    # (a) Format serialisasi: skops (whitelist tipe) lebih aman daripada pickle/cloudpickle
    sk = mlmodel.get("flavors", {}).get("sklearn", {})
    fmt = sk.get("serialization_format", "unknown")
    check("security", "Format serialisasi aman", fmt == "skops",
          f"{fmt}" + ("" if fmt == "skops" else " -> dapat mengeksekusi kode saat load"),
          severity="warning")

    # (b) Scan semua file pickle di artefak model
    bad = {}
    for root, _, files in os.walk(model_dir):
        for name in files:
            if name.endswith((".pkl", ".pickle", ".joblib")):
                hits = scan_pickle(os.path.join(root, name))
                if hits:
                    bad[name] = hits
    check("security", "Tidak ada import berbahaya di pickle", not bad,
          "bersih" if not bad else json.dumps(bad))

    # (c) Integritas: SHA-256 manifest. Pertama kali -> disimpan; berikutnya -> dibandingkan
    manifest = sha256_dir(model_dir)
    digest = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    recorded = mv.tags.get("artifact_sha256")
    if recorded is None:
        client.set_model_version_tag(MODEL_NAME, mv.version, "artifact_sha256", digest)
        check("security", "Integritas artefak (SHA-256)", True,
              f"baseline disimpan {digest[:12]}…")
    else:
        check("security", "Integritas artefak (SHA-256)", recorded == digest,
              f"tercatat={recorded[:12]}… sekarang={digest[:12]}…")
    mlflow.log_dict(manifest, "p5_security/artifact_manifest.json")

    # (d) Dependensi: harus ter-pin & bebas CVE yang diketahui
    req_path = os.path.join(model_dir, "requirements.txt")
    reqs = [r.strip() for r in open(req_path) if r.strip() and not r.startswith("#")]
    unpinned = [r for r in reqs if "==" not in r]
    check("security", "Dependensi ter-pin (==)", not unpinned,
          f"{len(reqs)} paket" + (f", belum ter-pin: {unpinned}" if unpinned else ""),
          severity="warning")
    if shutil.which("pip-audit"):
        proc = subprocess.run(["pip-audit", "-r", req_path, "--format", "json"],
                              capture_output=True, text=True)
        try:
            vulns = [(d["name"], v["id"]) for d in json.loads(proc.stdout)["dependencies"]
                     for v in d.get("vulns", [])]
            check("security", "Dependensi tanpa CVE (pip-audit)", not vulns,
                  f"{len(vulns)} kerentanan" + (f": {vulns[:3]}" if vulns else ""))
            mlflow.log_text(proc.stdout, "p5_security/pip_audit.json")
        except (json.JSONDecodeError, KeyError):
            check("security", "Dependensi tanpa CVE (pip-audit)", False,
                  "pip-audit gagal dijalankan (cek koneksi internet)", severity="warning")
    else:
        check("security", "Dependensi tanpa CVE (pip-audit)", False,
              "pip-audit belum terpasang: pip install pip-audit", severity="warning")
    return manifest


class _Payload:
    """Objek berbahaya untuk DEMO. Perintahnya tidak berbahaya & file ini TIDAK pernah di-load."""
    def __reduce__(self):
        return (os.system, ("echo 'kode penyerang dijalankan!'",))


def demo_malicious_pickle():
    print("[P5-demo] Deteksi pickle berbahaya (tanpa memuatnya)")
    path = "model_dari_internet.pkl"
    with open(path, "wb") as f:
        pickle.dump({"weights": [0.1, 0.2], "trap": _Payload()}, f)
    hits = scan_pickle(path)
    print(f"  file      : {path}")
    print(f"  temuan    : {hits}")
    print("  kesimpulan: " + ("JANGAN di-load! pickle.load() akan menjalankan perintah shell."
                              if hits else "tidak ditemukan import berbahaya"))
    os.remove(path)


# =============================================================================
# P6 — COMPLIANCE
# =============================================================================
PII_PATTERNS = ["nama", "name", "nik", "ktp", "email", "phone", "telepon", "hp", "alamat",
                "address", "tanggal_lahir", "birth", "dob", "rekam_medis", "patient_id"]


def step_compliance_data(train_df):
    """P6a — dijalankan SEBELUM P4 karena risk register membutuhkan hasilnya."""
    print("[P6a] Compliance — data & penggunaan")
    cols = [c.lower().replace(" ", "_") for c in train_df.columns]
    pii = [c for c in cols if any(p in c.split("_") for p in PII_PATTERNS)]
    check("compliance", "Tidak ada kolom PII langsung", not pii, f"temuan={pii}")
    check("compliance", "Dasar pemrosesan data tercatat", bool(USE_CASE["legal_basis"]),
          "UU PDP: " + USE_CASE["legal_basis"][:45] + "…")
    check("compliance", "Keputusan tidak otomatis penuh", not USE_CASE["fully_automated"],
          "dokter tetap pengambil keputusan (human-in-the-loop)")


def step_compliance(mv, run, tier, qa, risk_df, train_df, approver):
    print("[P6b] Compliance — dokumentasi & persetujuan")

    slices = "\n".join(f"| {s['slice']} | {s['n']} | {s['n_malignant']} | {s['recall']:.3f} |"
                       for s in qa["slices"])
    risks = "\n".join(f"| {r.id} | {r.risiko} | {r.skor_inheren} | {r.mitigasi} | {r.skor_residual} |"
                      for r in risk_df.itertuples())
    card = f"""# Model Card — {MODEL_NAME} v{mv.version}

## Detail Model
- Training run: `{mv.run_id}` ({run.info.run_name})
- Git commit: `{run.data.tags.get('mlflow.source.git.commit', 'tidak tercatat')}`
- Parameter: {', '.join(f'{k}={v}' for k, v in run.data.params.items() if k.startswith('clf__') and k.count('__') == 1) or '-'}
- Dibuat otomatis oleh pipeline readiness: {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC}

## Intended Use
{USE_CASE['decision']}. Pengguna: {USE_CASE['users']}.

## Out-of-Scope
- Diagnosis final tanpa pemeriksaan dokter / histopatologi
- Data dari alat atau protokol pengukuran yang berbeda dari data latih
- Penggunaan pada pasien di luar rentang data latih (ditolak oleh guardrail serving)

## Data Training
Breast Cancer Wisconsin (Diagnostic), {len(train_df)} baris latih, data_md5 `{run.data.tags.get('data_md5')}`.
Kategori data: {USE_CASE['personal_data']}. Dasar pemrosesan: {USE_CASE['legal_basis']}.

## Metrik (test set beku)
- Recall: {qa['recall']:.3f} · Precision: {qa['precision']:.3f} · Brier: {qa['brier']:.3f}

| Slice | n | n_malignant | Recall |
|---|---|---|---|
{slices}

## Fairness
Atribut demografis (usia, etnis) tidak tersedia di dataset -> fairness antar kelompok pasien
BELUM dapat diuji. Uji per ukuran tumor dipakai sebagai proxy subgroup.

## Keterbatasan
- Dataset kecil (569 sampel) dari satu institusi; generalisasi ke populasi Indonesia belum divalidasi
- Kalibrasi skor perlu dipantau; skor dalam ±{POLICY['review_margin']} dari threshold wajib direview dokter

## Risiko & Mitigasi ({tier})
| ID | Risiko | Skor inheren | Mitigasi | Skor residual |
|---|---|---|---|---|
{risks}

## Persetujuan
{f'Disetujui oleh: {approver}' if approver else 'BELUM DISETUJUI — menunggu Model Risk Committee'}
"""
    mlflow.log_text(card, "p6_compliance/model_card.md")
    required = ["Intended Use", "Out-of-Scope", "Data Training", "Metrik", "Fairness",
                "Keterbatasan", "Risiko & Mitigasi", "Persetujuan"]
    missing = [s for s in required if f"## {s}" not in card]
    check("compliance", "Model card lengkap", not missing, f"{len(required)} bagian wajib")

    needs_human = tier.startswith("Tier 1")
    check("compliance", "Persetujuan manusia (human oversight)",
          approver is not None or not needs_human,
          f"approver={approver}" if approver else "Tier 1 wajib --approver", severity="approval")
    return card


# =============================================================================
# P7 — RELEASE GATE: keputusan + audit trail di Model Registry
# =============================================================================
def step_release_gate(client, mv, champion, tier, approver, gate_run_id):
    print("[P7] Release gate")
    blockers = [c for c in CHECKS if not c["passed"] and c["severity"] == "blocker"]
    pending = [c for c in CHECKS if not c["passed"] and c["severity"] == "approval"]
    warnings_ = [c for c in CHECKS if not c["passed"] and c["severity"] == "warning"]
    decision = "rejected" if blockers else ("pending_approval" if pending else "approved")

    report = {"model": MODEL_NAME, "version": mv.version, "decision": decision,
              "risk_tier": tier, "approver": approver, "policy": POLICY,
              "timestamp": datetime.now(timezone.utc).isoformat(),
              "summary": {"total": len(CHECKS), "blockers_failed": len(blockers),
                          "warnings": len(warnings_)},
              "checks": CHECKS}
    mlflow.log_dict(report, "p7_gate/gate_report.json")
    mlflow.log_table(pd.DataFrame(CHECKS), "p7_gate/checks.json")
    mlflow.set_tags({"model_name": MODEL_NAME, "model_version": mv.version,
                     "gate_decision": decision, "risk_tier": tier})

    # Audit trail pada model version: siapa, kapan, berdasarkan bukti apa
    vtags = {"readiness_gate": decision, "gate_run_id": gate_run_id, "risk_tier": tier,
             "qa_status": phase_status("model_qa"), "data_qa_status": phase_status("data_qa"),
             "security_status": phase_status("security"),
             "compliance_status": phase_status("compliance"),
             "gate_checked_at": report["timestamp"]}
    if approver:
        vtags["approved_by"] = approver
    for k, v in vtags.items():
        client.set_model_version_tag(MODEL_NAME, mv.version, k, str(v))

    print(f"  total={len(CHECKS)} blocker gagal={len(blockers)} warning={len(warnings_)}")
    for c in blockers + pending:
        print(f"    - {c['check']}: {c['detail']}")

    if decision == "approved":
        if champion and champion.version != mv.version:
            client.set_registered_model_alias(MODEL_NAME, "previous-champion", champion.version)
        client.set_registered_model_alias(MODEL_NAME, "champion", mv.version)
        print(f"  ==> APPROVED: v{mv.version} menjadi @champion"
              + (f" (rollback ke v{champion.version} via @previous-champion)"
                 if champion and champion.version != mv.version else ""))
    elif decision == "pending_approval":
        print(f"  ==> PENDING: v{mv.version} lulus semua uji teknis, menunggu persetujuan manusia."
              "\n      Jalankan ulang dengan --approver \"<nama & jabatan>\"")
    else:
        print(f"  ==> REJECTED: v{mv.version} TIDAK dipromosikan. Lihat p7_gate/gate_report.json")
        if champion and champion.version == mv.version:
            print(f"      Perhatian: v{mv.version} SUDAH @champion (gate Minggu 6 hanya mengecek recall)."
                  "\n      Latih kandidat pengganti: --new-candidate logreg|rf|gb")
    return decision


def rollback(client, reason):
    print("[Rollback]")
    try:
        prev = client.get_model_version_by_alias(MODEL_NAME, "previous-champion")
    except Exception:
        raise SystemExit("Alias @previous-champion tidak ada -> tidak ada versi untuk rollback.")
    cur = get_champion(client)
    client.set_registered_model_alias(MODEL_NAME, "champion", prev.version)
    if cur:
        client.set_model_version_tag(MODEL_NAME, cur.version, "rolled_back_at",
                                     datetime.now(timezone.utc).isoformat())
        client.set_model_version_tag(MODEL_NAME, cur.version, "rollback_reason", reason)
    print(f"  @champion: v{cur.version if cur else '-'} -> v{prev.version} (alasan: {reason})")
    if prev.tags.get("readiness_gate") != "approved":
        print(f"  ⚠ v{prev.version} belum/tidak lulus readiness gate "
              f"({prev.tags.get('readiness_gate', 'belum diuji')}) -> rollback hanya solusi darurat")

    # Endpoint serving memakai model -guarded -> ikut dikembalikan ke pembungkus versi lama
    try:
        guarded = [v for v in client.search_model_versions(f"name='{GUARDED_NAME}'")
                   if v.tags.get("base_model_version") == str(prev.version)]
    except Exception:
        guarded = []
    if guarded:
        gv = max(guarded, key=lambda v: int(v.version))
        client.set_registered_model_alias(GUARDED_NAME, "champion", gv.version)
        print(f"  {GUARDED_NAME}@champion -> v{gv.version} (membungkus v{prev.version})")
    else:
        try:
            client.delete_registered_model_alias(GUARDED_NAME, "champion")
        except Exception:
            pass
        print(f"  {GUARDED_NAME}: belum ada pembungkus untuk v{prev.version} -> alias dihapus."
              f"\n  Jalankan gate untuk v{prev.version} agar endpoint aman tersedia kembali.")


# =============================================================================
# P8 — GUARDED SERVING (Models from Code, tanpa pickle untuk wrapper)
# =============================================================================
def step_guarded_serving(client, mv, model_dir, contract, manifest, test_df):
    print("[P8] Guarded serving")
    os.makedirs("guard", exist_ok=True)
    with open("guard/contract.json", "w") as f:
        json.dump(contract, f)
    with open("guard/manifest.json", "w") as f:
        json.dump(manifest, f)

    X = test_df[contract["columns"]]
    example = X.head(2)
    with mlflow.start_run(run_name=f"guarded-v{mv.version}", nested=True):
        info = mlflow.pyfunc.log_model(
            name="guarded_model",
            python_model=os.path.join(HERE, "guarded_model.py"),   # Models from Code
            code_paths=[os.path.join(HERE, "guarded_model.py")],
            artifacts={"model": model_dir, "contract": "guard/contract.json",
                       "manifest": "guard/manifest.json"},
            input_example=example,
            registered_model_name=GUARDED_NAME,
        )
        mlflow.set_tag("base_model", f"{MODEL_NAME}/v{mv.version}")
    gv = info.registered_model_version
    client.set_registered_model_alias(GUARDED_NAME, "champion", gv)
    client.set_model_version_tag(GUARDED_NAME, gv, "base_model_version", mv.version)
    print(f"  -> {GUARDED_NAME} v{gv} @champion (membungkus {MODEL_NAME} v{mv.version})")

    guarded = mlflow.pyfunc.load_model(f"models:/{GUARDED_NAME}@champion")
    demo = X.head(4).copy().reset_index(drop=True)
    demo.loc[1, "mean radius"] = -3.0              # nilai mustahil
    demo.loc[2, "worst area"] = 99999.0            # jauh di luar rentang data latih
    demo.loc[3, "mean texture"] = np.nan           # data tidak lengkap
    out = guarded.predict(demo)
    print(out.to_string())


# =============================================================================
# MAIN
# =============================================================================
def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("--model-version", help="versi yang diuji (default: alias @challenger)")
    p.add_argument("--new-candidate", choices=["logreg", "logreg-f2", "rf", "gb"],
                   help="latih & daftarkan kandidat baru sebagai @challenger terlebih dahulu")
    p.add_argument("--approver", help="nama & jabatan pemberi persetujuan (wajib untuk Tier 1)")
    p.add_argument("--rollback", action="store_true", help="kembalikan @champion ke versi sebelumnya")
    p.add_argument("--reason", default="insiden produksi", help="alasan rollback (audit trail)")
    p.add_argument("--demo-malicious-pickle", action="store_true")
    p.add_argument("--skip-serving", action="store_true", help="lewati P8")
    args = p.parse_args()

    setup_tracking()
    client = MlflowClient()

    if args.demo_malicious_pickle:
        demo_malicious_pickle()
        return
    if args.rollback:
        rollback(client, args.reason)
        return

    train_df, test_df, data_md5 = prepare_data()
    if args.new_candidate:
        step_new_candidate(args.new_candidate, train_df, data_md5)

    mv = resolve_target(client, args.model_version)                     # P0
    champion = get_champion(client)
    print(f"[P0] Target: {MODEL_NAME} v{mv.version} | champion saat ini: "
          f"{f'v{champion.version}' if champion else '-'}")
    model_dir = mlflow.artifacts.download_artifacts(f"models:/{MODEL_NAME}/{mv.version}")

    with mlflow.start_run(run_name=f"readiness-v{mv.version}") as gate_run:
        mlflow.set_tag("mlflow.note.content",
                       f"Production readiness check untuk {MODEL_NAME} v{mv.version}")
        mlflow.log_dict(POLICY, "policy.json")
        run, mlmodel = step_lineage(client, mv, model_dir, data_md5)           # P1
        contract = build_contract(train_df)
        step_data_qa(train_df, test_df, contract)                              # P2
        qa = step_model_qa(client, mv, champion, test_df, contract)            # P3
        manifest = step_security(client, mv, model_dir, mlmodel)               # P5
        step_compliance_data(train_df)                                         # P6a
        tier, risk_df = step_risk()                  # P4: dinilai SETELAH bukti kontrol tersedia
        step_compliance(mv, run, tier, qa, risk_df, train_df, args.approver)   # P6b
        decision = step_release_gate(client, mv, champion, tier, args.approver,
                                     gate_run.info.run_id)                     # P7
        if decision == "approved" and not args.skip_serving:
            step_guarded_serving(client, mv, model_dir, contract, manifest, test_df)  # P8

    print(f"\nSelesai. Keputusan: {decision.upper()}. "
          f"Buka MLflow UI -> experiment '{EXPERIMENT_NAME}' & tab Models.")


if __name__ == "__main__":
    main()
