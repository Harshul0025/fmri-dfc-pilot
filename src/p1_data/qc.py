"""Apply QC rules → contract C2 (subjects.csv) + sanity plots.

    python src/p1_data/qc.py            # real: data/qc/*.json → data/subjects.csv
    python src/p1_data/qc.py --demo     # demo: data_demo/ (min-timepoints rule skipped,
                                        #   since the demo scans are short)

Rules (from config.yaml → qc):
    mean motion > max_mean_fd          → "high motion"
    T < min_timepoints                 → "too few timepoints"
    any ROI all-NaN / flat             → "bad ROI signal"
    listed in candidates but no output → "missing / extraction failed"

Plots → results/qc/ (or results_demo/qc/): carpet plot + 3 ROI traces per subject,
and a motion bar chart with the threshold line.
"""
import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from common.io import load_config  # noqa: E402
from download import read_ids  # noqa: E402


def reasons_for(info, q, check_length):
    r = []
    if info["mean_fd"] is None:
        r.append("motion file missing")
    elif info["mean_fd"] > q["max_mean_fd"]:
        r.append("high motion")
    if check_length and info["n_timepoints"] < q["min_timepoints"]:
        r.append("too few timepoints")
    if info["bad_rois"]:
        r.append(f"bad ROI signal ({len(info['bad_rois'])} ROIs)")
    return r


def plot_subject(ts, sid, out):
    fig, (a, b) = plt.subplots(2, 1, figsize=(9, 5), height_ratios=[2, 1], sharex=True)
    a.imshow(ts.T, aspect="auto", cmap="gray", vmin=-2, vmax=2, interpolation="nearest")
    a.set_ylabel("ROI")
    a.set_title(f"sub-{sid}: carpet plot (z-scored)")
    for roi in (0, 100, 199):
        b.plot(ts[:, roi], lw=0.6, label=f"ROI {roi + 1}")
    b.set_xlabel("time point (TR)")
    b.legend(fontsize=7, loc="upper right")
    fig.tight_layout()
    fig.savefig(out / f"sub-{sid}_carpet.png", dpi=110)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()

    cfg = load_config()
    q = cfg["qc"]
    root = REPO / ("data_demo" if args.demo else "data")
    figs = REPO / ("results_demo" if args.demo else "results") / "qc"
    figs.mkdir(parents=True, exist_ok=True)

    rows = []
    for f in sorted((root / "qc").glob("sub-*.json")):
        info = json.loads(f.read_text())
        r = reasons_for(info, q, check_length=not args.demo)
        rows.append(dict(subject_id=info["subject_id"], run=info["run"],
                         n_timepoints=info["n_timepoints"], mean_fd=info["mean_fd"],
                         included=not r, exclusion_reason="; ".join(r)))
        plot_subject(np.load(root / "timeseries" / f"sub-{info['subject_id']}.npy"),
                     info["subject_id"], figs)

    if not args.demo:  # candidates that never produced output
        done = {r["subject_id"] for r in rows}
        for sid in read_ids(REPO / "src/p1_data/candidates.txt"):
            if sid not in done:
                rows.append(dict(subject_id=sid, run=cfg["hcp"]["run"], n_timepoints=0,
                                 mean_fd=None, included=False,
                                 exclusion_reason="missing / extraction failed"))

    df = pd.DataFrame(rows).sort_values("subject_id")
    df.to_csv(root / "subjects.csv", index=False)

    d = df.dropna(subset=["mean_fd"])
    fig, ax = plt.subplots(figsize=(max(5, 0.35 * len(d)), 3))
    ax.bar(d["subject_id"], d["mean_fd"], color=np.where(d["included"], "#4C78A8", "#E45756"))
    ax.axhline(q["max_mean_fd"], ls="--", c="k", lw=1, label=f"threshold {q['max_mean_fd']} mm")
    ax.set_ylabel("mean motion (mm)")
    ax.tick_params(axis="x", rotation=90, labelsize=7)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(figs / "motion.png", dpi=110)
    plt.close(fig)

    n_in = int(df["included"].sum())
    print(df.to_string(index=False))
    print(f"\nIncluded: {n_in}/{len(df)}  →  {root / 'subjects.csv'}")
    if not args.demo and n_in < 10:
        print("WARNING: fewer than 10 included subjects — download more candidates.")


if __name__ == "__main__":
    main()
