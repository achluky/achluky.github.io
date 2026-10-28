"""
Generate ilustrasi gambar untuk slide "Model Experimentation and Tracking".
Semua gambar adalah MOCKUP bergaya Weights & Biases (data sintetis), bukan screenshot asli.

    python make_figures.py      # output -> images/*.png
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle

OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)

plt.rcParams.update({
    "font.family": ["Helvetica Neue", "Arial Unicode MS"],
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#cbd5e1",
    "axes.labelcolor": "#334155",
    "xtick.color": "#64748b",
    "ytick.color": "#64748b",
    "axes.grid": True,
    "grid.color": "#eef2f6",
})

WB_DARK = "#1a1c1f"
WB_YELLOW = "#ffcc33"
INK = "#0f172a"
MUTED = "#64748b"
BORDER = "#e2e8f0"
RUN_COLORS = ["#e8590c", "#1c7ed6", "#2f9e44", "#ae3ec9", "#f59f00", "#0ca678"]

RUNS = [  # nama run, lr, batch, dropout, warna
    ("resnet18-lr1e-3", 1e-3, 64, 0.2),
    ("resnet18-lr3e-4", 3e-4, 64, 0.2),
    ("resnet18-lr1e-2", 1e-2, 64, 0.2),
    ("resnet50-lr3e-4", 3e-4, 32, 0.3),
    ("resnet18-noaug", 1e-3, 64, 0.0),
]
rng = np.random.default_rng(7)
EPOCHS = np.arange(1, 31)


def simulate(lr, dropout, i):
    """Kurva loss/acc sintetis yang perilakunya masuk akal per konfigurasi."""
    e = EPOCHS
    if lr >= 1e-2:  # lr terlalu besar -> osilasi
        tr = 1.2 * np.exp(-e / 12) + 0.35 + 0.12 * np.sin(e * 1.3)
        va = tr + 0.12 + 0.1 * np.sin(e * 1.1 + 1)
    elif dropout == 0.0:  # tanpa regularisasi -> overfitting
        tr = 1.6 * np.exp(-e / 5) + 0.03
        va = 1.5 * np.exp(-e / 5) + 0.30 + 0.018 * np.clip(e - 10, 0, None)
    else:
        speed = {1e-3: 5, 3e-4: 8}[lr] + (2 if i == 3 else 0)
        floor = {0: 0.20, 1: 0.24, 3: 0.17}[i]
        tr = 1.6 * np.exp(-e / speed) + floor - 0.06
        va = 1.5 * np.exp(-e / speed) + floor
    tr = tr + rng.normal(0, 0.012, e.size)
    va = va + rng.normal(0, 0.02, e.size)
    acc = np.clip(0.97 - 0.42 * va, 0, 1)
    return tr, va, acc


CURVES = [simulate(lr, d, i) for i, (_, lr, _, d) in enumerate(RUNS)]


def browser_frame(fig, url, title):
    """Header ala browser + top bar W&B."""
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0, 0.93, 1, 0.07])
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, color="#f1f5f9", transform=ax.transAxes))
    for k, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        ax.scatter([0.012 + k * 0.014], [0.5], s=90, color=c, transform=ax.transAxes)
    ax.add_patch(Rectangle((0.07, 0.2), 0.55, 0.6, color="white", transform=ax.transAxes))
    ax.text(0.08, 0.5, "" + url, va="center", fontsize=10, color=MUTED, transform=ax.transAxes)
    ax.text(0.99, 0.5, "Ilustrasi · data sintetis", va="center", ha="right", fontsize=9,
            color="#94a3b8", style="italic", transform=ax.transAxes)
    bar = fig.add_axes([0, 0.88, 1, 0.05])
    bar.axis("off")
    bar.add_patch(Rectangle((0, 0), 1, 1, color=WB_DARK, transform=bar.transAxes))
    bar.text(0.012, 0.5, "▮▮▮", color=WB_YELLOW, fontsize=11, va="center", fontweight="bold",
             transform=bar.transAxes)
    bar.text(0.045, 0.5, "Weights & Biases", color="white", fontsize=12, va="center",
             fontweight="bold", transform=bar.transAxes)
    bar.text(0.2, 0.5, title, color="#cbd5e1", fontsize=11, va="center", transform=bar.transAxes)


def runs_sidebar(fig, rect, highlight=None):
    ax = fig.add_axes(rect)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.add_patch(Rectangle((0, 0), 1, 1, color="#f8fafc"))
    ax.text(0.06, 0.95, "Runs (5)", fontsize=12, fontweight="bold", color=INK, va="top")
    ax.add_patch(FancyBboxPatch((0.06, 0.84), 0.88, 0.05, boxstyle="round,pad=0,rounding_size=0.02",
                                fc="white", ec=BORDER))
    ax.text(0.09, 0.865, "Search runs", fontsize=9, color="#94a3b8", va="center")
    for k, (name, *_ ) in enumerate(RUNS):
        y = 0.77 - k * 0.075
        if highlight is not None and k == highlight:
            ax.add_patch(Rectangle((0.02, y - 0.03), 0.96, 0.06, color="#fff3bf"))
        ax.text(0.06, y, "◉", fontsize=9, va="center", color=MUTED)
        ax.scatter([0.17], [y], s=110, color=RUN_COLORS[k], zorder=3)
        ax.text(0.22, y, name, fontsize=10, va="center", color=INK)
    ax.text(0.06, 0.32, "Group by: config.arch", fontsize=9, color=MUTED)
    ax.text(0.06, 0.27, "Filter: state = finished", fontsize=9, color=MUTED)


def fig_workspace():
    fig = plt.figure(figsize=(14, 7.6))
    browser_frame(fig, "wandb.ai/itera-ds/cifar10-classifier/workspace", "itera-ds / cifar10-classifier  ›  Workspace")
    runs_sidebar(fig, [0, 0, 0.2, 0.88], highlight=0)
    panels = [("train/loss", 0), ("val/loss", 1), ("val/accuracy", 2), ("learning_rate", None)]
    for p, (title, idx) in enumerate(panels):
        col, row = p % 2, p // 2
        ax = fig.add_axes([0.25 + col * 0.38, 0.5 - row * 0.43, 0.34, 0.31])
        for k, (name, lr, *_ ) in enumerate(RUNS):
            if idx is None:
                y = lr * (0.02 + 0.49 * (1 + np.cos(np.pi * EPOCHS / EPOCHS.max())))
            else:
                y = CURVES[k][idx]
            ax.plot(EPOCHS, y, color=RUN_COLORS[k], lw=2.2 if k == 0 else 1.6, alpha=1 if k == 0 else 0.85)
        ax.set_title(title, loc="left", fontsize=12, color=INK, fontweight="bold")
        ax.set_xlabel("epoch", fontsize=9)
        if idx is None:
            ax.set_yscale("log")
    fig.text(0.25, 0.86, "Charts  ·  4 panels", fontsize=10, color=MUTED, va="top")
    fig.savefig(OUT / "wandb_workspace.png", dpi=150)
    plt.close(fig)


def fig_runs_table():
    fig = plt.figure(figsize=(14, 6.2))
    browser_frame(fig, "wandb.ai/itera-ds/cifar10-classifier/table", "itera-ds / cifar10-classifier  ›  Runs Table")
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.83])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    cols = ["", "Name", "State", "arch", "lr", "batch_size", "dropout", "augment",
            "val/accuracy ▼", "val/loss", "Runtime", "git commit"]
    xs = [0.01, 0.04, 0.2, 0.28, 0.37, 0.44, 0.52, 0.6, 0.68, 0.78, 0.86, 0.93]
    ax.add_patch(Rectangle((0, 0.88), 1, 0.09, color="#f1f5f9"))
    for x, c in zip(xs, cols):
        ax.text(x, 0.925, c, fontsize=10.5, fontweight="bold", color=INK, va="center")
    rows = []
    for k, (name, lr, bs, d) in enumerate(RUNS):
        tr, va, acc = CURVES[k]
        rows.append((k, name, "finished", "resnet50" if "50" in name else "resnet18", f"{lr:.0e}", bs, d,
                     "✗" if "noaug" in name else "✓", acc.max(), va.min(),
                     f"{12 + 9 * (k == 3) + k}m {10 * k + 7}s", ["9e1b2c", "9e1b2c", "9e1b2c", "4fa71d", "c31e08"][k]))
    rows.sort(key=lambda r: -r[8])
    for j, r in enumerate(rows):
        y = 0.81 - j * 0.12
        if j == 0:
            ax.add_patch(Rectangle((0, y - 0.05), 1, 0.1, color="#fff9db"))
        ax.scatter([0.02], [y], s=120, color=RUN_COLORS[r[0]], zorder=3)
        vals = [r[1], "● " + r[2], r[3], r[4], r[5], r[6], r[7], f"{r[8]:.3f}", f"{r[9]:.3f}", r[10], r[11]]
        for x, v in zip(xs[1:], vals):
            color = "#2f9e44" if str(v).startswith("●") else INK
            weight = "bold" if (j == 0 and x in (0.68,)) else "normal"
            ax.text(x, y, str(v), fontsize=10.5, color=color, va="center", fontweight=weight,
                    family="Menlo" if x in (0.37, 0.93) else None)
        ax.plot([0, 1], [y - 0.06, y - 0.06], color=BORDER, lw=1)
    ax.text(0.01, 0.12, "★ Urutkan berdasarkan metrik utama, filter berdasarkan config, lalu pilih 2+ run → \"Compare\"",
            fontsize=11, color=MUTED, style="italic")
    fig.savefig(OUT / "wandb_runs_table.png", dpi=150)
    plt.close(fig)


def fig_sweep():
    fig = plt.figure(figsize=(14, 6.8))
    browser_frame(fig, "wandb.ai/itera-ds/cifar10-classifier/sweeps/k3j9x2", "Sweep: bayes-lr-dropout  ·  40 runs")
    # Parallel coordinates
    ax = fig.add_axes([0.04, 0.1, 0.58, 0.68])
    n = 40
    lr = 10 ** rng.uniform(-4.5, -1.5, n)
    bs = rng.choice([16, 32, 64, 128], n)
    do = rng.uniform(0, 0.5, n)
    wd = 10 ** rng.uniform(-6, -2, n)
    acc = (0.9 - 0.06 * (np.log10(lr) + 3) ** 2 - 0.25 * (do - 0.25) ** 2
           - 0.01 * np.abs(np.log2(bs) - 6) + rng.normal(0, 0.01, n))
    axes_vals = [np.log10(lr), np.log2(bs), do, np.log10(wd), acc]
    names = ["lr (log)", "batch_size", "dropout", "weight_decay", "val/accuracy"]
    norm = [(v - v.min()) / (v.max() - v.min()) for v in axes_vals]
    cmap = plt.get_cmap("plasma")
    a_n = norm[-1]
    for i in np.argsort(a_n):
        ax.plot(range(5), [nv[i] for nv in norm], color=cmap(a_n[i]), lw=1.4, alpha=0.8)
    for x in range(5):
        ax.axvline(x, color="#94a3b8", lw=1.2)
        ax.text(x, 1.06, names[x], ha="center", fontsize=11, fontweight="bold", color=INK)
        ax.text(x + 0.03, -0.04, f"{axes_vals[x].min():.2f}", fontsize=8, color=MUTED)
        ax.text(x + 0.03, 1.0, f"{axes_vals[x].max():.2f}", fontsize=8, color=MUTED)
    ax.set_xlim(-0.1, 4.4)
    ax.set_ylim(-0.08, 1.12)
    ax.axis("off")
    fig.text(0.04, 0.82, "Parallel Coordinates", fontsize=13, fontweight="bold", color=INK)
    # Parameter importance
    ax2 = fig.add_axes([0.72, 0.18, 0.25, 0.55])
    params = ["lr", "dropout", "batch_size", "weight_decay"]
    imp = [0.58, 0.24, 0.12, 0.06]
    corr = [-0.62, 0.21, -0.08, 0.03]
    ax2.barh(params[::-1], imp[::-1], color="#1c7ed6")
    for k, (p, c) in enumerate(zip(params[::-1], corr[::-1])):
        ax2.text(imp[::-1][k] + 0.02, k, f"corr {c:+.2f}", va="center", fontsize=9,
                 color="#e03131" if c < 0 else "#2f9e44")
    ax2.set_xlim(0, 0.85)
    ax2.set_axisbelow(True)
    ax2.set_xlabel("importance")
    ax2.grid(axis="y", visible=False)
    fig.text(0.72, 0.82, "Parameter Importance\nwrt val/accuracy", fontsize=13, fontweight="bold", color=INK, va="top")
    fig.savefig(OUT / "wandb_sweep.png", dpi=150)
    plt.close(fig)


def node(ax, x, y, w, h, title, sub, fc, ec):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.01,rounding_size=0.02",
                                fc=fc, ec=ec, lw=2))
    ax.text(x, y + 0.025, title, ha="center", va="center", fontsize=12, fontweight="bold", color=INK)
    ax.text(x, y - 0.035, sub, ha="center", va="center", fontsize=9.5, color=MUTED, family="Menlo")


def arrow(ax, x1, y1, x2, y2, label=None):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color="#475569", lw=1.8, mutation_scale=18))
    if label:
        dx, dy = (0.012, 0) if x1 == x2 else (0, 0.035)
        ax.text((x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, label, ha="left" if dx else "center", fontsize=9,
                color=MUTED, style="italic")


def fig_lineage():
    fig = plt.figure(figsize=(14, 6.2))
    browser_frame(fig, "wandb.ai/itera-ds/cifar10-classifier/artifacts/model/cifar10-resnet/v3/lineage",
                  "Artifacts  ›  cifar10-resnet:v3  ›  Lineage")
    ax = fig.add_axes([0.01, 0.02, 0.98, 0.84])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ds, run, art, rv = "#e7f5ff", "#fff9db", "#ebfbee", "#f3f0ff"
    node(ax, 0.09, 0.72, 0.15, 0.17, "cifar10-raw", "dataset:v0", ds, "#1c7ed6")
    node(ax, 0.29, 0.72, 0.15, 0.17, "preprocess", "run: wild-sun-3", run, "#f59f00")
    node(ax, 0.49, 0.72, 0.15, 0.17, "cifar10-split", "dataset:v2", ds, "#1c7ed6")
    node(ax, 0.49, 0.32, 0.15, 0.17, "train", "run: lr1e-3 (a3f9c1)", run, "#f59f00")
    node(ax, 0.69, 0.32, 0.15, 0.17, "cifar10-resnet", "model:v3", art, "#2f9e44")
    node(ax, 0.69, 0.72, 0.15, 0.17, "evaluate", "run: eval-test-7", run, "#f59f00")
    node(ax, 0.9, 0.32, 0.16, 0.17, "Registry", "@production", rv, "#7048e8")
    node(ax, 0.29, 0.32, 0.15, 0.17, "config + code", "git 9e1b2c · env", "#f8fafc", "#94a3b8")
    arrow(ax, 0.165, 0.72, 0.215, 0.72)
    arrow(ax, 0.365, 0.72, 0.415, 0.72)
    arrow(ax, 0.49, 0.635, 0.49, 0.405, "input")
    arrow(ax, 0.365, 0.32, 0.415, 0.32)
    arrow(ax, 0.565, 0.32, 0.615, 0.32)
    arrow(ax, 0.69, 0.405, 0.69, 0.635, "input")
    arrow(ax, 0.765, 0.32, 0.82, 0.32)
    ax.text(0.5, 0.08, "Setiap artifact tahu run mana yang membuatnya dan run mana yang memakainya → model di produksi dapat ditelusuri sampai ke data & kode.",
            ha="center", fontsize=11, color=MUTED, style="italic")
    fig.savefig(OUT / "wandb_lineage.png", dpi=150)
    plt.close(fig)


def fig_how_it_works():
    fig = plt.figure(figsize=(14, 4.6))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    node(ax, 0.1, 0.55, 0.15, 0.42, "train.py", "wandb.init()\nrun.log({...})", "#f8fafc", "#94a3b8")
    node(ax, 0.38, 0.55, 0.15, 0.42, "wandb SDK", "proses latar\n(buffer + sync)", "#fff9db", "#f59f00")
    node(ax, 0.64, 0.55, 0.13, 0.42, "W&B Server", "wandb.ai /\nself-hosted", "#e7f5ff", "#1c7ed6")
    for k, (t, c) in enumerate([("Workspace & Compare", "#ebfbee"), ("Sweeps", "#ebfbee"),
                                ("Artifacts & Registry", "#f3f0ff"), ("Reports", "#f3f0ff")]):
        y = 0.86 - k * 0.205
        ax.add_patch(FancyBboxPatch((0.79, y - 0.075), 0.19, 0.15, boxstyle="round,pad=0.005,rounding_size=0.02",
                                    fc=c, ec="#94a3b8", lw=1.5))
        ax.text(0.885, y, t, ha="center", va="center", fontsize=11.5, color=INK, fontweight="bold")
        arrow(ax, 0.71, 0.55, 0.79, y)
    arrow(ax, 0.18, 0.55, 0.3, 0.55, "metrics, config")
    arrow(ax, 0.46, 0.55, 0.57, 0.55, "HTTPS / offline sync")
    ax.text(0.1, 0.2, "Kode Anda", ha="center", fontsize=10, color=MUTED, style="italic")
    ax.text(0.38, 0.2, "+ otomatis: git commit, sistem,\nGPU/CPU, requirements", ha="center", fontsize=10,
            color=MUTED, style="italic", va="top")
    fig.savefig(OUT / "wandb_how_it_works.png", dpi=150)
    plt.close(fig)


def fig_learning_curves():
    fig, axs = plt.subplots(1, 4, figsize=(15, 3.9))
    e = np.linspace(1, 30, 60)
    cases = [
        ("✓ Good fit", 1.5 * np.exp(-e / 5) + 0.15, 1.5 * np.exp(-e / 5) + 0.25, "train ≈ val, keduanya turun"),
        ("! Overfitting", 1.5 * np.exp(-e / 5) + 0.03, 1.5 * np.exp(-e / 5) + 0.3 + 0.02 * np.clip(e - 9, 0, None),
         "val naik → early stopping /\nregularisasi / data lebih banyak"),
        ("! Underfitting", 0.4 * np.exp(-e / 4) + 0.9, 0.4 * np.exp(-e / 4) + 0.95,
         "loss tinggi & datar → model\nlebih besar / training lebih lama"),
        ("! LR terlalu besar", 0.8 * np.exp(-e / 10) + 0.5 + 0.2 * np.sin(e * 1.4),
         0.8 * np.exp(-e / 10) + 0.6 + 0.2 * np.sin(e * 1.4 + 0.6), "osilasi → turunkan lr /\nscheduler / warmup"),
    ]
    for ax, (t, tr, va, note) in zip(axs, cases):
        ax.plot(e, tr, color="#1c7ed6", lw=2.2, label="train")
        ax.plot(e, va, color="#e8590c", lw=2.2, label="val")
        ax.set_title(t, fontsize=13, fontweight="bold", color=INK, loc="left")
        ax.set_xlabel("epoch")
        ax.set_ylim(0, 2)
        ax.set_yticklabels([])
        ax.text(0.97, 0.95, note, transform=ax.transAxes, ha="right", va="top", fontsize=9.5, color=MUTED)
    axs[0].set_ylabel("loss")
    axs[0].legend(loc="lower left", frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "learning_curves.png", dpi=150)
    plt.close(fig)


def fig_experiment_cycle():
    fig = plt.figure(figsize=(14, 4.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    steps = [
        ("1. Hipotesis", "\"Augmentasi mixup\nmenaikkan F1 ≥ 2%\"", "#e7f5ff", "#1c7ed6"),
        ("2. Desain", "baseline, variabel,\nmetrik, seed", "#e7f5ff", "#1c7ed6"),
        ("3. Eksekusi + Log", "params, metrics,\nartifacts", "#fff9db", "#f59f00"),
        ("4. Analisis", "kurva, tabel,\nuji signifikansi", "#ebfbee", "#2f9e44"),
        ("5. Keputusan", "promote / iterate /\ndiscard", "#f3f0ff", "#7048e8"),
    ]
    for k, (t, s, fc, ec) in enumerate(steps):
        x = 0.1 + k * 0.2
        ax.add_patch(FancyBboxPatch((x - 0.08, 0.42), 0.16, 0.4, boxstyle="round,pad=0.005,rounding_size=0.03",
                                    fc=fc, ec=ec, lw=2))
        ax.text(x, 0.72, t, ha="center", fontsize=13, fontweight="bold", color=INK)
        ax.text(x, 0.56, s, ha="center", va="center", fontsize=10.5, color=MUTED)
        if k < 4:
            arrow(ax, x + 0.082, 0.62, x + 0.118, 0.62)
    ax.annotate("", xy=(0.1, 0.4), xytext=(0.9, 0.4),
                arrowprops=dict(arrowstyle="-|>", color="#475569", lw=1.8, mutation_scale=18,
                                connectionstyle="bar,fraction=-0.12"))
    ax.text(0.5, 0.12, "insight baru → hipotesis berikutnya", ha="center", fontsize=11, color=MUTED, style="italic")
    fig.savefig(OUT / "experiment_cycle.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    fig_workspace()
    fig_runs_table()
    fig_sweep()
    fig_lineage()
    fig_how_it_works()
    fig_learning_curves()
    fig_experiment_cycle()
    print("OK ->", sorted(p.name for p in OUT.glob("*.png")))
