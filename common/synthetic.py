"""Generate fake data in the exact CONTRACTS.md format so everyone can work without waiting.

Run from repo root:  python common/synthetic.py

Creates data_synthetic/ (C1, C2, C3) and results_synthetic/ (C4, C5 placeholders),
so P4 can build stats before P2/P3 finish. P2/P3 will overwrite the placeholders
with their own real outputs once their code works.

The time series switch between a few hidden connectivity states, so P3's clustering
has something real to find, and wm_score is weakly linked to time in state 1.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common.io import REPO, load_config  # noqa: E402


def make_state_covs(rng, n_states, n_rois, n_blocks=7):
    """Each state = a different set of 'networks' that are strongly coupled."""
    covs = []
    for _ in range(n_states):
        labels = rng.integers(0, n_blocks, n_rois)
        strength = rng.uniform(0.2, 0.7, n_blocks)
        cov = np.eye(n_rois)
        for b in range(n_blocks):
            idx = np.where(labels == b)[0]
            cov[np.ix_(idx, idx)] += strength[b]
        covs.append(np.linalg.cholesky(cov + 1e-6 * np.eye(n_rois)))
    return covs


def simulate_subject(rng, chols, T, n_rois, mean_dwell=80):
    """Markov-switching between states; returns (T, n_rois) and state sequence."""
    k = len(chols)
    seq = np.empty(T, dtype=int)
    s = rng.integers(k)
    for t in range(T):
        if rng.random() < 1.0 / mean_dwell:
            s = rng.integers(k)
        seq[t] = s
    noise = rng.standard_normal((T, n_rois))
    ts = np.stack([chols[seq[t]] @ noise[t] for t in range(T)])
    # mild temporal smoothing to look BOLD-ish
    kernel = np.array([0.25, 0.5, 0.25])
    ts = np.apply_along_axis(lambda c: np.convolve(c, kernel, mode="same"), 0, ts)
    ts = (ts - ts.mean(0)) / ts.std(0)
    return ts.astype(np.float32), seq


def main():
    cfg = load_config()
    rng = np.random.default_rng(cfg["synthetic"]["seed"])
    n_sub = cfg["synthetic"]["n_subjects"]
    n_rois = cfg["atlas"]["n_rois"]
    T = cfg["hcp"]["n_timepoints"]
    K = cfg["dynamic"]["n_states"]

    out = REPO / "data_synthetic"
    (out / "timeseries").mkdir(parents=True, exist_ok=True)
    chols = make_state_covs(rng, K, n_rois)

    ids = [str(100000 + 1000 * i + rng.integers(0, 999)) for i in range(n_sub)]
    subj_rows, beh_rows, frac1 = [], [], []
    for sid in ids:
        ts, seq = simulate_subject(rng, chols, T, n_rois)
        np.save(out / "timeseries" / f"sub-{sid}.npy", ts)
        fd = float(rng.gamma(2.0, 0.06))
        ok = fd <= cfg["qc"]["max_mean_fd"]
        subj_rows.append(dict(subject_id=sid, run=cfg["hcp"]["run"], n_timepoints=T,
                              mean_fd=round(fd, 3), included=ok,
                              exclusion_reason="" if ok else "high motion"))
        f1 = float((seq == 0).mean())
        frac1.append(f1)
        beh_rows.append(dict(subject_id=sid,
                             wm_score=round(100 + 25 * f1 + rng.normal(0, 8), 1),
                             age_group=rng.choice(["22-25", "26-30", "31-35"]),
                             sex=rng.choice(["M", "F"])))
    pd.DataFrame(subj_rows).to_csv(out / "subjects.csv", index=False)
    pd.DataFrame(beh_rows).to_csv(out / "behaviour.csv", index=False)

    # Placeholder metrics (C4, C5) so P4 can start immediately.
    res = REPO / "results_synthetic"
    (res / "static").mkdir(parents=True, exist_ok=True)
    (res / "dynamic").mkdir(parents=True, exist_ok=True)
    pd.DataFrame(dict(
        subject_id=ids,
        mean_fc=rng.normal(0.3, 0.05, n_sub).round(3),
        mean_strength=rng.normal(25, 3, n_sub).round(2),
        mean_clustering=rng.normal(0.45, 0.04, n_sub).round(3),
        global_efficiency=rng.normal(0.5, 0.03, n_sub).round(3),
        density=cfg["static"]["threshold_density"],
    )).to_csv(res / "static" / "metrics.csv", index=False)
    dyn = dict(subject_id=ids,
               fc_variability=rng.normal(0.2, 0.02, n_sub).round(3),
               n_transitions=rng.integers(5, 30, n_sub))
    fr = rng.dirichlet(np.ones(K), n_sub)
    fr[:, 0] = frac1
    fr = fr / fr.sum(1, keepdims=True)
    for k in range(K):
        dyn[f"state{k + 1}_frac"] = fr[:, k].round(3)
        dyn[f"state{k + 1}_dwell"] = rng.uniform(3, 20, n_sub).round(1)
    pd.DataFrame(dyn).to_csv(res / "dynamic" / "metrics.csv", index=False)

    n_ok = sum(r["included"] for r in subj_rows)
    print(f"Synthetic data: {n_sub} subjects ({n_ok} pass QC), T={T}, ROIs={n_rois}, states={K}")
    print(f"  -> {out}\n  -> {res} (placeholder metrics; P2/P3 overwrite)")


if __name__ == "__main__":
    main()
