"""
Hands-on 2 — Studi Kasus End-to-End: Model Experimentation & Tracking dengan MLflow
====================================================================================

Mata kuliah : Machine Learning Operations (MLOps) — Minggu 6
Kasus       : Deteksi tumor ganas (Breast Cancer Wisconsin, scikit-learn)

Alur (sesuai slide):
    Skenario  Hipotesis & metrik ditetapkan SEBELUM eksperimen
    L1  Data            split tetap + hash data + mlflow.data (log_input)
    --  run_experiment  fungsi logging standar untuk semua run
    L2  Baseline        Dummy, LogReg tanpa / dengan scaling          (H1, H2)
    L3  Model selection 5 algoritma sederhana, kondisi identik
    L4  Tuning          GridSearchCV SVC + nested runs                (H3)
    L5  Analisis        pilih kandidat via mlflow.search_runs
    L6  Evaluasi final  test set disentuh SEKALI
    L7  Registry        @challenger -> quality gate -> @champion
    L8  Serving         load via models:/...@champion (+ REST opsional)
    L9  Reproduce       telusuri model produksi -> run, commit, data, environment

Setup:
    python -m venv .venv && source .venv/bin/activate
    pip install "mlflow>=3" scikit-learn pandas matplotlib requests   # diuji: MLflow 3.17, sklearn 1.9

Menjalankan (pilih salah satu):
    # (a) Tanpa server — semua tersimpan di ./mlflow.db dan ./mlruns
    python hands_on_2_end_to_end.py
    mlflow ui --backend-store-uri sqlite:///mlflow.db          # buka http://127.0.0.1:5000

    # (b) Dengan tracking server (seperti di slide)
    mlflow server --backend-store-uri sqlite:///mlflow.db \
                  --default-artifact-root ./mlartifacts --port 5000
    export MLFLOW_TRACKING_URI=http://127.0.0.1:5000
    python hands_on_2_end_to_end.py

Serving REST (L8, opsional, di terminal lain setelah script selesai):
    export MLFLOW_TRACKING_URI=<sama dengan di atas>
    mlflow models serve -m "models:/bc-malignant-classifier@champion" -p 5001 --env-manager local
    python hands_on_2_end_to_end.py --only-serve-test

Catatan: jalankan dari dalam repositori Git agar MLflow otomatis mencatat
`mlflow.source.git.commit`. Menjalankan ulang script akan membuat run baru;
quality gate (L7) akan MENOLAK versi baru bila tidak lebih baik dari champion.
"""

import argparse
import hashlib
import os
import warnings

import matplotlib

matplotlib.use("Agg")  # tanpa GUI: plot langsung disimpan sebagai artefak
import matplotlib.pyplot as plt
import mlflow
import pandas as pd
from mlflow import MlflowClient
from mlflow.models import infer_signature
from sklearn.datasets import load_breast_cancer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.exceptions import UndefinedMetricWarning
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import (
    GridSearchCV,
    StratifiedKFold,
    cross_val_predict,
    cross_validate,
    train_test_split,
)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

# Dummy classifier tidak pernah memprediksi kelas positif -> precision tak terdefinisi (diharapkan)
warnings.filterwarnings("ignore", category=UndefinedMetricWarning)

# =============================================================================
# SKENARIO — keputusan yang ditetapkan SEBELUM eksperimen dimulai
# =============================================================================
# Kelas positif     : 1 = malignant (label asli scikit-learn dibalik: 1 - target)
# Optimizing metric : Recall    — false negative (tumor ganas terlewat) sangat mahal
# Satisficing metric: Precision >= 0.90 — agar tidak membanjiri dokter dengan alarm palsu
# Protokol          : Train 80% (5-fold Stratified CV untuk seleksi) · Test 20% (sekali di akhir)
#
# Hipotesis:
#   H1: Model linear sederhana sudah jauh lebih baik dari baseline dummy.
#   H2: Standardisasi fitur meningkatkan recall model berbasis jarak/margin (LR, KNN, SVC).
#   H3: Tuning hyperparameter SVC meningkatkan recall tanpa melanggar precision >= 0.90.

EXPERIMENT_NAME = "bc-malignant-detection"
MODEL_NAME = "bc-malignant-classifier"
DATA_DIR = "data"
SEED = 42

MIN_PRECISION = 0.90  # satisficing metric
MARGIN = 0.005        # model baru harus lebih baik minimal sebesar ini dari champion

CV = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)  # fold identik untuk semua run
SCORING = ["recall", "precision", "f1", "roc_auc"]


def setup_tracking():
    """Pakai MLFLOW_TRACKING_URI bila di-set; jika tidak, simpan lokal di SQLite."""
    if not os.environ.get("MLFLOW_TRACKING_URI"):
        mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment(EXPERIMENT_NAME)
    print(f"[setup] tracking URI : {mlflow.get_tracking_uri()}")
    print(f"[setup] experiment   : {EXPERIMENT_NAME}")


# =============================================================================
# L1 — DATA: split tetap + versi data (hash)
# Prinsip: Versioning & Reproducibility — setiap run tahu persis data apa yang dipakai.
# =============================================================================
def prepare_data():
    df = load_breast_cancer(as_frame=True).frame
    df["target"] = 1 - df["target"]  # 1 = malignant (kelas positif)

    # Sidik jari data: berubah satu nilai pun -> hash berbeda
    data_md5 = hashlib.md5(pd.util.hash_pandas_object(df, index=True).values).hexdigest()

    train_df, test_df = train_test_split(
        df, test_size=0.2, stratify=df["target"], random_state=SEED
    )
    os.makedirs(DATA_DIR, exist_ok=True)
    train_df.to_csv(f"{DATA_DIR}/train.csv", index=False)
    test_df.to_csv(f"{DATA_DIR}/test.csv", index=False)  # test set: DIKUNCI sampai L6

    print(f"[L1] data_md5={data_md5} | train={len(train_df)} | test={len(test_df)} "
          f"| malignant ratio={df['target'].mean():.2%}")
    return df, train_df, test_df, data_md5


# Variabel global diisi di main() agar fungsi-fungsi di bawah sama persis dengan slide
X_train = y_train = X_test = y_test = None
train_df = test_df = train_ds = None
data_md5 = None
COMMON_TAGS = {}


# =============================================================================
# FUNGSI LOGGING STANDAR — dipakai SEMUA eksperimen
# Nama metrik & artefak konsisten -> mudah dibandingkan di MLflow UI.
# =============================================================================
def run_experiment(run_name, pipe, tags=None, note=""):
    with mlflow.start_run(run_name=run_name) as run:
        # (a) KONTEKS: tag, catatan hipotesis, versi data
        mlflow.set_tags({**COMMON_TAGS, "candidate": "true", **(tags or {})})
        mlflow.set_tag("mlflow.note.content", note)  # deskripsi run di UI
        mlflow.log_input(train_ds, context="training")

        # (b) PARAMETER: langkah pipeline + seluruh hyperparameter estimator
        mlflow.log_param("pipeline_steps", " -> ".join(pipe.named_steps))
        mlflow.log_params({f"clf__{k}": v for k, v in pipe[-1].get_params().items()})

        # (c) METRIK: mean & std dari 5-fold CV (bukan satu angka tunggal!)
        cv = cross_validate(pipe, X_train, y_train, cv=CV, scoring=SCORING)
        for m in SCORING:
            mlflow.log_metric(f"cv_{m}_mean", cv[f"test_{m}"].mean())
            mlflow.log_metric(f"cv_{m}_std", cv[f"test_{m}"].std())
        mlflow.log_metric("fit_time_s", cv["fit_time"].mean())

        # (d) ARTEFAK DIAGNOSTIK: prediksi out-of-fold (tanpa menyentuh test set)
        y_oof = cross_val_predict(pipe, X_train, y_train, cv=CV)
        disp = ConfusionMatrixDisplay.from_predictions(
            y_train, y_oof, display_labels=["benign", "malignant"]
        )
        mlflow.log_figure(disp.figure_, "plots/confusion_matrix_oof.png")
        plt.close(disp.figure_)
        mlflow.log_text(
            classification_report(y_train, y_oof, zero_division=0),
            "reports/classification_report_oof.txt",
        )

        # (e) MODEL: dilatih ulang di seluruh train set + signature & contoh input
        pipe.fit(X_train, y_train)
        signature = infer_signature(X_train, pipe.predict(X_train))
        info = mlflow.sklearn.log_model(
            pipe,
            name="model",
            signature=signature,
            input_example=X_train.head(3),
            skops_trusted_types=["sklearn.tree._tree.Tree"],  # utk DT/RF/GB (MLflow 3)
        )
        mlflow.set_tag("model_uri", info.model_uri)  # models:/m-... (MLflow 3)

        print(f"  - {run_name:<26} cv_recall={cv['test_recall'].mean():.3f}"
              f" ±{cv['test_recall'].std():.3f}  cv_precision={cv['test_precision'].mean():.3f}")
        return run.info.run_id


# =============================================================================
# L2 — BASELINE: seberapa buruk "tanpa model"? (H1, H2)
# =============================================================================
def step_baseline():
    print("[L2] Baseline")
    run_experiment(
        "00-dummy-most-frequent",
        Pipeline([("clf", DummyClassifier(strategy="most_frequent"))]),
        tags={"stage": "baseline", "model_family": "dummy"},
        note="Batas bawah: selalu menebak kelas mayoritas (benign).",
    )
    run_experiment(
        "01-logreg-noscale",
        Pipeline([("clf", LogisticRegression(max_iter=5000))]),
        tags={"stage": "baseline", "model_family": "logreg"},
        note="H1: model linear tanpa preprocessing.",
    )
    # Controlled experiment: dibanding 01, HANYA scaling yang berubah
    run_experiment(
        "02-logreg-scaled",
        Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression(max_iter=5000))]),
        tags={"stage": "baseline", "model_family": "logreg"},
        note="H2: hanya menambah StandardScaler, variabel lain tetap.",
    )


# =============================================================================
# L3 — MODEL SELECTION: bandingkan algoritma sederhana
# Kontrol: fold CV sama, preprocessing sama, data sama -> perbedaan hanya dari algoritma.
# =============================================================================
def step_model_selection():
    print("[L3] Model selection")
    candidates = {
        "knn": KNeighborsClassifier(n_neighbors=5),
        "tree": DecisionTreeClassifier(max_depth=5, random_state=SEED),
        "rf": RandomForestClassifier(n_estimators=200, random_state=SEED),
        "gb": GradientBoostingClassifier(random_state=SEED),
        "svc": SVC(kernel="rbf", random_state=SEED),
    }
    for i, (family, clf) in enumerate(candidates.items(), start=3):
        pipe = Pipeline([("scaler", StandardScaler()), ("clf", clf)])
        run_experiment(
            f"{i:02d}-{family}-default",
            pipe,
            tags={"stage": "model-selection", "model_family": family},
            note="Hyperparameter default; preprocessing identik untuk semua.",
        )


# =============================================================================
# L4 — HYPERPARAMETER TUNING dengan nested runs (H3)
# Parent run = ringkasan sweep + model terbaik; child run = satu trial.
# Alternatif singkat: mlflow.sklearn.autolog() (child run otomatis, atur max_tuning_runs).
# =============================================================================
def step_tuning():
    print("[L4] Tuning SVC dengan GridSearchCV (nested runs)")
    pipe = Pipeline([("scaler", StandardScaler()), ("clf", SVC(kernel="rbf", random_state=SEED))])
    grid = {"clf__C": [0.1, 1, 10, 100], "clf__gamma": ["scale", 0.01, 0.001]}  # 12 kombinasi
    gs = GridSearchCV(pipe, grid, cv=CV, scoring=SCORING, refit="recall", n_jobs=-1)

    with mlflow.start_run(
        run_name="10-svc-gridsearch",
        tags={**COMMON_TAGS, "stage": "tuning", "model_family": "svc", "candidate": "true"},
    ):
        mlflow.set_tag("mlflow.note.content", "H3: tuning C x gamma pada SVC RBF.")
        mlflow.log_input(train_ds, context="training")
        mlflow.log_dict(grid, "search_space.json")  # ruang pencarian = artefak
        gs.fit(X_train, y_train)
        res = gs.cv_results_

        for i, params in enumerate(res["params"]):  # 1 trial = 1 child run
            with mlflow.start_run(run_name=f"svc-trial-{i:02d}", nested=True):
                mlflow.set_tag("stage", "tuning-trial")
                mlflow.log_params(params)
                mlflow.log_metrics({f"cv_{m}_mean": res[f"mean_test_{m}"][i] for m in SCORING})
                mlflow.log_metrics({f"cv_{m}_std": res[f"std_test_{m}"][i] for m in SCORING})

        # Parent = ringkasan trial terbaik (nama metrik sama dgn run lain -> bisa dibandingkan)
        b = gs.best_index_
        mlflow.log_params(gs.best_params_)
        mlflow.log_metrics({f"cv_{m}_mean": res[f"mean_test_{m}"][b] for m in SCORING})
        mlflow.log_metrics({f"cv_{m}_std": res[f"std_test_{m}"][b] for m in SCORING})
        info = mlflow.sklearn.log_model(
            gs.best_estimator_,
            name="model",
            signature=infer_signature(X_train, gs.best_estimator_.predict(X_train)),
            input_example=X_train.head(3),
        )
        mlflow.set_tag("model_uri", info.model_uri)

    print(f"  - best params={gs.best_params_}  cv_recall={res['mean_test_recall'][b]:.3f}"
          f" ±{res['std_test_recall'][b]:.3f}")


# =============================================================================
# L5 — ANALISIS PROGRAMATIK: pilih kandidat terbaik
# Seleksi model = aturan tertulis di kode (bisa dijalankan ulang di Continuous Training).
# =============================================================================
def step_select_best():
    print("[L5] Seleksi kandidat via mlflow.search_runs")
    runs = mlflow.search_runs(
        experiment_names=[EXPERIMENT_NAME],
        filter_string=(
            "tags.candidate = 'true' "                     # hanya run yang punya model
            f"and metrics.cv_precision_mean >= {MIN_PRECISION}"  # satisficing metric
        ),
        order_by=["metrics.cv_recall_mean DESC",           # optimizing metric
                  "metrics.cv_f1_mean DESC"],              # tie-breaker
    )
    cols = ["tags.mlflow.runName", "tags.model_family",
            "metrics.cv_recall_mean", "metrics.cv_recall_std", "metrics.cv_precision_mean"]
    print(runs[cols].head(5).to_string(index=False))

    best_run_id = runs.iloc[0]["run_id"]
    best_model_uri = runs.iloc[0]["tags.model_uri"]  # models:/m-...
    print(f"  -> Kandidat terpilih: {runs.iloc[0]['tags.mlflow.runName']} ({best_run_id})")
    return best_run_id, best_model_uri


def summarize_hypotheses():
    """Ringkas H1–H3 langsung dari data yang tercatat di MLflow (bukan dari ingatan)."""
    runs = mlflow.search_runs(experiment_names=[EXPERIMENT_NAME],
                              filter_string="tags.candidate = 'true'",
                              order_by=["attributes.start_time DESC"])
    latest = runs.drop_duplicates("tags.mlflow.runName").set_index("tags.mlflow.runName")

    def r(name, stat="mean"):
        return latest.loc[name, f"metrics.cv_recall_{stat}"]

    print("[Hipotesis]")
    print(f"  H1 dummy -> logreg      : {r('00-dummy-most-frequent'):.3f} -> {r('01-logreg-noscale'):.3f}")
    print(f"  H2 logreg tanpa/dgn scale: {r('01-logreg-noscale'):.3f} -> {r('02-logreg-scaled'):.3f}")
    gain = r("10-svc-gridsearch") - r("07-svc-default")
    std = r("10-svc-gridsearch", "std")
    print(f"  H3 svc default -> tuned  : {r('07-svc-default'):.3f} -> {r('10-svc-gridsearch'):.3f}"
          f" (gain {gain:+.3f}, std {std:.3f})"
          + ("  ⚠ gain < std: belum tentu signifikan" if abs(gain) < std else ""))


# =============================================================================
# L6 — EVALUASI FINAL di test set (HANYA SEKALI)
# Jika test_recall jauh di bawah cv_recall_mean -> overfitting pada proses seleksi;
# JANGAN kembali men-tuning berdasarkan test set.
# =============================================================================
def step_final_evaluation(best_run_id, best_model_uri):
    print("[L6] Evaluasi final di test set")
    model = mlflow.sklearn.load_model(best_model_uri)
    y_pred = model.predict(X_test)
    score = (model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba")
             else model.decision_function(X_test))

    test_metrics = {
        "test_recall": recall_score(y_test, y_pred),
        "test_precision": precision_score(y_test, y_pred),
        "test_f1": f1_score(y_test, y_pred),
        "test_roc_auc": roc_auc_score(y_test, score),
    }

    with mlflow.start_run(run_id=best_run_id):  # tambahkan ke run yang SAMA
        mlflow.log_metrics(test_metrics)
        mlflow.log_input(
            mlflow.data.from_pandas(test_df, source=f"{DATA_DIR}/test.csv",
                                    name="bc-test", targets="target"),
            context="testing",
        )
        disp = ConfusionMatrixDisplay.from_predictions(
            y_test, y_pred, display_labels=["benign", "malignant"]
        )
        mlflow.log_figure(disp.figure_, "plots/confusion_matrix_test.png")
        plt.close(disp.figure_)
        mlflow.set_tag("test_evaluated", "true")

    print("  " + "  ".join(f"{k}={v:.3f}" for k, v in test_metrics.items()))
    return test_metrics


# =============================================================================
# L7 — MODEL REGISTRY + QUALITY GATE otomatis
# Gate hanya adil bila champion & challenger diuji pada test set yang sama (cek data_md5).
# Rollback: client.set_registered_model_alias(MODEL_NAME, "champion", <versi_lama>)
# =============================================================================
def step_register(best_model_uri, test_metrics):
    print("[L7] Registry + quality gate")
    client = MlflowClient()

    mv = mlflow.register_model(best_model_uri, MODEL_NAME)  # -> versi baru
    client.update_model_version(
        MODEL_NAME, mv.version,
        description=(f"Dipilih otomatis: max cv_recall dgn precision>={MIN_PRECISION}. "
                     f"data_md5={data_md5}"),
    )
    client.set_model_version_tag(MODEL_NAME, mv.version, "data_md5", data_md5)
    client.set_registered_model_alias(MODEL_NAME, "challenger", mv.version)

    def champion_recall():
        try:
            champ = client.get_model_version_by_alias(MODEL_NAME, "champion")
            return client.get_run(champ.run_id).data.metrics["test_recall"]
        except Exception:  # belum ada champion
            return -1.0

    current = champion_recall()
    passed = (test_metrics["test_precision"] >= MIN_PRECISION
              and test_metrics["test_recall"] >= current + MARGIN)

    client.set_model_version_tag(MODEL_NAME, mv.version, "validation_status",
                                 "approved" if passed else "rejected")
    if passed:
        client.set_registered_model_alias(MODEL_NAME, "champion", mv.version)  # promosi
        print(f"  -> v{mv.version} APPROVED dan menjadi @champion")
    else:
        print(f"  -> v{mv.version} REJECTED (champion test_recall={current:.3f}); "
              f"@champion tidak berubah")
    return mv.version


# =============================================================================
# L8 — SERVING model dari registry (berdasarkan ALIAS, bukan path/nomor versi)
# =============================================================================
def step_serving_local():
    print("[L8] Load @champion via pyfunc (batch scoring)")
    model = mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}@champion")
    preds = model.predict(X_test.head(5))  # input divalidasi terhadap signature
    print(f"  prediksi 5 sampel test : {pd.Series(preds).tolist()}  (1 = malignant)")
    print(f"  label sebenarnya       : {y_test.head(5).tolist()}")


def step_serving_rest(url="http://127.0.0.1:5001/invocations"):
    """Butuh server: mlflow models serve -m "models:/bc-malignant-classifier@champion" -p 5001 --env-manager local"""
    import requests

    print(f"[L8] Request ke REST endpoint {url}")
    payload = {"dataframe_split": X_test.head(3).to_dict(orient="split")}
    try:
        r = requests.post(url, json=payload, timeout=10)
        print(f"  status={r.status_code} response={r.json()}")  # {"predictions": [0, 1, 0]}
    except requests.exceptions.ConnectionError:
        print("  server belum berjalan. Jalankan dulu:\n"
              f'  mlflow models serve -m "models:/{MODEL_NAME}@champion" -p 5001 --env-manager local')


# =============================================================================
# L9 — REPRODUCE: dari model di produksi kembali ke asal-usulnya (lineage)
# git checkout <commit> + data dgn hash sama + environment sama + random_state tetap
# -> hasil identik.
# =============================================================================
def step_reproduce():
    print("[L9] Lineage model @champion")
    client = MlflowClient()
    champ = client.get_model_version_by_alias(MODEL_NAME, "champion")
    run = client.get_run(champ.run_id)

    print(f"  Model      : {MODEL_NAME} v{champ.version}")
    print(f"  Run        : {run.info.run_name} {run.info.run_id}")
    print(f"  Git commit : {run.data.tags.get('mlflow.source.git.commit', '(bukan repo git)')}")
    print(f"  Data md5   : {run.data.tags['data_md5']}")
    print(f"  Params     : {{{', '.join(f'{k}={v}' for k, v in run.data.params.items() if k.startswith('clf__'))}}}")
    print(f"  Metrics    : {{{', '.join(f'{k}={v:.3f}' for k, v in sorted(run.data.metrics.items()))}}}")

    # 1) Pastikan data saat ini identik dengan data training
    assert data_md5 == run.data.tags["data_md5"], "Data berbeda -> hasil tidak akan sama!"
    print("  ✓ data_md5 cocok dengan data training champion")

    # 2) Unduh artefak (model, requirements.txt) untuk audit
    path = mlflow.artifacts.download_artifacts(artifact_uri=f"models:/{MODEL_NAME}@champion")
    with open(os.path.join(path, "requirements.txt")) as f:
        print("  requirements.txt:\n    " + f.read().strip().replace("\n", "\n    "))


# =============================================================================
# MAIN
# =============================================================================
def main():
    global X_train, y_train, X_test, y_test, train_df, test_df, train_ds, data_md5, COMMON_TAGS

    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--only-serve-test", action="store_true",
                        help="hanya kirim request ke REST endpoint (L8) lalu keluar")
    args = parser.parse_args()

    setup_tracking()

    # L1 — Data
    _, train_df, test_df, data_md5 = prepare_data()
    X_train, y_train = train_df.drop(columns="target"), train_df["target"]
    X_test, y_test = test_df.drop(columns="target"), test_df["target"]
    # Objek Dataset MLflow -> tampil di tab "Datasets" pada setiap run
    train_ds = mlflow.data.from_pandas(train_df, source=f"{DATA_DIR}/train.csv",
                                       name="bc-train", targets="target")
    COMMON_TAGS = {"data_md5": data_md5, "split_seed": str(SEED),
                   "dataset": "sklearn-breast-cancer"}

    if args.only_serve_test:
        step_serving_rest()
        return

    step_baseline()                                              # L2
    step_model_selection()                                       # L3
    step_tuning()                                                # L4
    best_run_id, best_model_uri = step_select_best()             # L5
    summarize_hypotheses()
    test_metrics = step_final_evaluation(best_run_id, best_model_uri)  # L6
    step_register(best_model_uri, test_metrics)                  # L7
    step_serving_local()                                         # L8
    step_serving_rest()
    step_reproduce()                                             # L9

    print("\nSelesai. Buka MLflow UI untuk membandingkan run, melihat artefak, dan registry.")


if __name__ == "__main__":
    main()
