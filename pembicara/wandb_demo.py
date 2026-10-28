"""
Hands-on: Experiment Tracking dengan Weights & Biases (W&B)
Dataset: sklearn digits (8x8 angka tulisan tangan) · Model: MLPClassifier · CPU saja

Persiapan:
    pip install wandb scikit-learn matplotlib
    wandb login                      # tempel API key dari https://wandb.ai/authorize
    # tanpa akun / tanpa internet:  export WANDB_MODE=offline  (lalu `wandb sync wandb/offline-run-*`)

Jalankan:
    python wandb_demo.py                         # 1 run dengan konfigurasi default
    python wandb_demo.py --lr 0.01 --hidden 32   # run lain, untuk dibandingkan
    python wandb_demo.py --sweep --count 15      # hyperparameter sweep (Bayesian)
"""
import argparse
import random
import warnings

import joblib
import numpy as np
import wandb
from sklearn.datasets import load_digits
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import accuracy_score, f1_score, log_loss
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore", category=ConvergenceWarning)

PROJECT = "digits-experiment-tracking"
DEFAULTS = dict(lr=1e-3, hidden=64, alpha=1e-4, batch_size=64, epochs=40, seed=42)


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)


def load_data(seed):
    X, y = load_digits(return_X_y=True)
    # split DIKUNCI dengan random_state tetap -> setiap run memakai data yang sama
    X_tmp, X_test, y_tmp, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=0)
    X_train, X_val, y_train, y_val = train_test_split(X_tmp, y_tmp, test_size=0.2, stratify=y_tmp, random_state=0)
    scaler = StandardScaler().fit(X_train)  # fit hanya di train -> tidak ada data leakage
    return [scaler.transform(a) for a in (X_train, X_val, X_test)], (y_train, y_val, y_test)


def train(config=None):
    with wandb.init(project=PROJECT, config=config, job_type="train",
                    tags=["mlp", "digits"], notes="Hands-on W&B") as run:
        cfg = run.config  # pada sweep, nilai diisi oleh W&B
        set_seed(cfg.seed)
        (X_train, X_val, X_test), (y_train, y_val, y_test) = load_data(cfg.seed)
        classes = np.unique(y_train)

        model = MLPClassifier(hidden_layer_sizes=(cfg.hidden,), alpha=cfg.alpha,
                              learning_rate_init=cfg.lr, batch_size=cfg.batch_size,
                              max_iter=1, warm_start=True, random_state=cfg.seed)

        best_val_acc, best_epoch = 0.0, 0
        for epoch in range(1, cfg.epochs + 1):
            model.partial_fit(X_train, y_train, classes=classes)
            metrics = {
                "epoch": epoch,
                "train/loss": log_loss(y_train, model.predict_proba(X_train), labels=classes),
                "train/accuracy": accuracy_score(y_train, model.predict(X_train)),
                "val/loss": log_loss(y_val, model.predict_proba(X_val), labels=classes),
                "val/accuracy": accuracy_score(y_val, model.predict(X_val)),
            }
            run.log(metrics)  # dicatat per epoch -> muncul sebagai kurva di dashboard
            if metrics["val/accuracy"] > best_val_acc:
                best_val_acc, best_epoch = metrics["val/accuracy"], epoch
                joblib.dump(model, "model.joblib")

        # Ringkasan run (kolom di Runs Table)
        best = joblib.load("model.joblib")
        y_pred = best.predict(X_val)
        run.summary["best_val_accuracy"] = best_val_acc
        run.summary["best_epoch"] = best_epoch
        run.summary["val/f1_macro"] = f1_score(y_val, y_pred, average="macro")

        # Visualisasi: confusion matrix + tabel prediksi yang salah
        run.log({"val/confusion_matrix": wandb.plot.confusion_matrix(
            y_true=y_val.tolist(), preds=y_pred.tolist(), class_names=[str(c) for c in classes])})
        wrong = np.where(y_pred != y_val)[0][:20]
        table = wandb.Table(columns=["image", "label", "prediksi"])
        for i in wrong:
            table.add_data(wandb.Image(X_val[i].reshape(8, 8)), int(y_val[i]), int(y_pred[i]))
        run.log({"val/salah_prediksi": table})

        # Versioning model sebagai Artifact (otomatis v0, v1, v2, ...)
        art = wandb.Artifact("digits-mlp", type="model",
                             metadata={"val_accuracy": best_val_acc, **dict(cfg)})
        art.add_file("model.joblib")
        run.log_artifact(art, aliases=["latest", f"epoch-{best_epoch}"])


SWEEP_CONFIG = {
    "method": "bayes",  # grid | random | bayes
    "metric": {"name": "best_val_accuracy", "goal": "maximize"},
    "parameters": {
        "lr": {"distribution": "log_uniform_values", "min": 1e-4, "max": 1e-1},
        "hidden": {"values": [16, 32, 64, 128]},
        "alpha": {"distribution": "log_uniform_values", "min": 1e-6, "max": 1e-2},
        "batch_size": {"values": [32, 64, 128]},
        "epochs": {"value": 40},
        "seed": {"value": 42},
    },
    "early_terminate": {"type": "hyperband", "min_iter": 5},
}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    for k, v in DEFAULTS.items():
        p.add_argument(f"--{k.replace('_', '-')}", dest=k, type=type(v), default=v)
    p.add_argument("--sweep", action="store_true")
    p.add_argument("--count", type=int, default=15)
    args = p.parse_args()

    if args.sweep:
        sweep_id = wandb.sweep(SWEEP_CONFIG, project=PROJECT)
        wandb.agent(sweep_id, function=train, count=args.count)
    else:
        train({k: getattr(args, k) for k in DEFAULTS})
