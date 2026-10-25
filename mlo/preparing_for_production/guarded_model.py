"""
GuardedModel —  wrapper model untuk serving yang lebih aman.
=========================================================================

Dipakai oleh hands_on_production_readiness.py (P8) dengan pola MLflow "Models from Code":
model wrapper TIDAK di-pickle, melainkan disimpan sebagai file kode sumber ini.
Keuntungannya: dapat dibaca/di-review manusia & tidak ada eksekusi kode tersembunyi saat load.

Guardrail yang diterapkan pada setiap request:
    1. Validasi input   : kolom lengkap, tidak ada null, nilai tidak negatif,
                          dan berada dalam rentang operasi model (operating envelope)
    2. Integritas model : SHA-256 artefak model dicek terhadap manifest saat load
    3. Human-in-the-loop: skor di "zona abu-abu" ditandai requires_review = True
    4. Output terbatas  : hanya label + skor dibulatkan (mempersulit model extraction)
"""

import hashlib
import json
import os

import mlflow
import numpy as np
import pandas as pd


def sha256_dir(path):
    """Hash setiap file di dalam folder artefak model (urut, path relatif)."""
    manifest = {}
    for root, _, files in os.walk(path):
        for name in sorted(files):
            full = os.path.join(root, name)
            with open(full, "rb") as f:
                manifest[os.path.relpath(full, path)] = hashlib.sha256(f.read()).hexdigest()
    return dict(sorted(manifest.items()))


class GuardedModel(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        with open(context.artifacts["contract"]) as f:
            self.contract = json.load(f)
        with open(context.artifacts["manifest"]) as f:
            expected = json.load(f)

        model_dir = context.artifacts["model"]
        if sha256_dir(model_dir) != expected:  # artefak berubah setelah gate -> tolak
            raise RuntimeError("Integritas model gagal: hash artefak tidak cocok dengan manifest")
        self.model = mlflow.sklearn.load_model(model_dir)
        # threshold milik model (TunedThresholdClassifierCV), default 0.5
        self.threshold = float(getattr(self.model, "best_threshold_", 0.5))

    def _score(self, X):
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(X)[:, 1]
        # SVC tanpa probability: ubah decision function ke (0, 1) dengan sigmoid
        return 1.0 / (1.0 + np.exp(-self.model.decision_function(X)))

    def _validate(self, df):
        """Kembalikan daftar alasan penolakan per baris ('' = valid)."""
        reasons = pd.Series("", index=df.index)
        missing = [c for c in self.contract["columns"] if c not in df.columns]
        if missing:
            return reasons.radd(f"kolom hilang: {missing[:3]}")

        X = df[self.contract["columns"]]
        tol = self.contract["range_tolerance"]
        for col, (lo, hi) in self.contract["ranges"].items():
            span = hi - lo
            v = X[col]
            reasons[v.isna()] += f"{col} null; "
            reasons[v < 0] += f"{col} negatif; "
            reasons[(v < lo - tol * span) | (v > hi + tol * span)] += f"{col} di luar rentang; "
        return reasons

    def predict(self, context, model_input, params=None):
        df = pd.DataFrame(model_input)
        reasons = self._validate(df)
        ok = reasons == ""

        out = pd.DataFrame({
            "prediction": -1,                 # -1 = tidak diprediksi (input ditolak)
            "score": np.nan,
            "requires_review": True,          # input ditolak -> wajib dicek manusia
            "status": np.where(ok, "ok", "rejected: " + reasons.str.rstrip("; ")),
        }, index=df.index)

        if ok.any():
            X = df.loc[ok, self.contract["columns"]]
            score = self._score(X)
            out.loc[ok, "prediction"] = self.model.predict(X).astype(int)
            out.loc[ok, "score"] = np.round(score, 2)        # dibulatkan
            out.loc[ok, "requires_review"] = (
                np.abs(score - self.threshold) <= self.contract["review_margin"])
        return out.reset_index(drop=True)


mlflow.models.set_model(GuardedModel())
