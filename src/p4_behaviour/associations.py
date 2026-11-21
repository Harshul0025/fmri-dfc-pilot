"""Brain–behaviour stats: do the connectivity metrics (C4 + C5) relate to working memory (C3)?

    python src/p4_behaviour/associations.py

Steps:
  1. Merge subjects (C2) + behaviour (C3) + static metrics (C4) + dynamic metrics (C5).
  2. For every metric vs wm_score:
       - partial Spearman controlling for head motion (mean_fd)  ← main test
       - plain Spearman and Pearson                              ← extra, for comparison
       - 95% bootstrap confidence interval for the main test
  3. FDR correction (Benjamini–Hochberg) because we test many metrics.
  4. Motion check: is mean_fd itself related to WM or to the metrics?
  5. Descriptives table + scatterplots.

Outputs go to results/stats/ (or results_synthetic/stats/ on fake data).
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from common.io import (load_behaviour, load_config, load_metrics,  # noqa: E402
                       load_subjects, results_dir)


def partial_spearman(x, y, z):
    """Spearman correlation of x and y after removing the effect of z (motion).

    Ranks first (that makes it Spearman), then the standard partial-correlation
    formula. p-value uses n - 3 degrees of freedom (one extra lost for z).
    """
    r_xy = stats.spearmanr(x, y)[0]
    r_xz = stats.spearmanr(x, z)[0]
    r_yz = stats.spearmanr(y, z)[0]
    r = (r_xy - r_xz * r_yz) / np.sqrt((1 - r_xz ** 2) * (1 - r_yz ** 2))
    df = len(x) - 3
    t = r * np.sqrt(df / (1 - r ** 2))
    p = 2 * stats.t.sf(abs(t), df)
    return r, p


def bootstrap_ci(x, y, z, seed, n_boot=5000):
    """95% CI: resample subjects with replacement 5,000 times, recompute r each time."""
    rng = np.random.default_rng(seed)
    n = len(x)
    rs = []
    for _ in range(n_boot):
        i = rng.integers(0, n, n)
        rs.append(partial_spearman(x[i], y[i], z[i])[0])
    return np.nanpercentile(rs, [2.5, 97.5])


def main():
    cfg = load_config()
    seed = cfg["dynamic"]["random_seed"]
    out = results_dir(cfg) / "stats"
    (out / "figures").mkdir(parents=True, exist_ok=True)

    # ---- 1. merge everything on subject_id ----
    static = load_metrics("static", cfg)
    dynamic = load_metrics("dynamic", cfg)
    df = (load_subjects(cfg)[["subject_id", "mean_fd"]]       # included subjects only
          .merge(load_behaviour(cfg), on="subject_id")
          .merge(static, on="subject_id")
          .merge(dynamic, on="subject_id"))

    # metrics = every column from C4/C5 except subject_id; skip columns that are the
    # same for everyone (e.g. density is fixed by the threshold), nothing to correlate
    metrics = [c for c in list(static.columns[1:]) + list(dynamic.columns[1:])
               if df[c].nunique() > 1]

    wm = df["wm_score"].to_numpy(float)
    fd = df["mean_fd"].to_numpy(float)

    # ---- 2. correlations ----
    rows = []
    for m in metrics:
        x = df[m].to_numpy(float)
        r, p = partial_spearman(x, wm, fd)
        lo, hi = bootstrap_ci(x, wm, fd, seed)
        rows.append(dict(
            metric=m,
            source="static" if m in static.columns else "dynamic",
            n=len(x),
            partial_rho=r, partial_p=p, ci_low=lo, ci_high=hi,
            spearman_rho=stats.spearmanr(x, wm)[0], spearman_p=stats.spearmanr(x, wm)[1],
            pearson_r=stats.pearsonr(x, wm)[0], pearson_p=stats.pearsonr(x, wm)[1],
        ))
    res = pd.DataFrame(rows)

    # ---- 3. FDR correction across all metrics (on the main test) ----
    res["partial_q"] = stats.false_discovery_control(res["partial_p"], method="bh")
    res = res.sort_values("partial_p")
    res.round(4).to_csv(out / "associations.csv", index=False)

    # ---- 4. motion check ----
    motion = pd.DataFrame(
        [dict(variable=v, rho_with_mean_fd=stats.spearmanr(fd, df[v])[0],
              p=stats.spearmanr(fd, df[v])[1]) for v in ["wm_score"] + metrics])
    motion.round(4).to_csv(out / "motion_check.csv", index=False)

    # ---- 5a. descriptives ----
    desc = pd.DataFrame([
        ("N", len(df)),
        ("Female / Male", f"{(df.sex == 'F').sum()} / {(df.sex == 'M').sum()}"),
        ("Age groups", ", ".join(f"{g}: {n}" for g, n in df.age_group.value_counts().sort_index().items())),
        ("WM score mean ± SD", f"{wm.mean():.1f} ± {wm.std(ddof=1):.1f}"),
        ("Mean FD (mm) mean ± SD", f"{fd.mean():.3f} ± {fd.std(ddof=1):.3f}"),
    ], columns=["measure", "value"])
    desc.to_csv(out / "descriptives.csv", index=False)

    # ---- 5b. scatterplots: one small plot per metric ----
    ncol = 4
    nrow = int(np.ceil(len(res) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(3.3 * ncol, 3 * nrow), squeeze=False)
    for ax, row in zip(axes.flat, res.itertuples()):
        x = df[row.metric]
        ax.scatter(x, wm, s=20)
        slope, intercept = np.polyfit(x, wm, 1)          # straight-line fit, just for the eye
        ax.plot(np.sort(x), intercept + slope * np.sort(x), color="red")
        ax.set_xlabel(row.metric)
        ax.set_ylabel("WM score")
        ax.set_title(f"ρ = {row.partial_rho:.2f}, p = {row.partial_p:.3f}, q = {row.partial_q:.2f}",
                     fontsize=9)
    for ax in axes.flat[len(res):]:
        ax.axis("off")
    fig.suptitle(f"Metrics vs working memory (N = {len(df)}, partial ρ controls for motion)")
    fig.tight_layout()
    fig.savefig(out / "figures" / "scatter_grid.png", dpi=150)

    print(desc.to_string(index=False), "\n")
    print(res[["metric", "partial_rho", "partial_p", "partial_q", "spearman_rho", "pearson_r"]]
          .round(3).to_string(index=False))
    print(f"\nSaved to {out}")


if __name__ == "__main__":
    main()
