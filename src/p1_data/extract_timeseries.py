"""Extract Schaefer-200 ROI time series → contract C1, plus per-subject QC info.

Real HCP (after download.py):
    python src/p1_data/extract_timeseries.py
        reads  data/raw/<id>/<run>_hp2000_clean.nii.gz
        writes data/timeseries/sub-<id>.npy   (T, 200) float32, z-scored
               data/qc/sub-<id>.json          T, mean motion, bad ROIs

Demo (works today, no HCP access needed — nilearn's small public dataset):
    python src/p1_data/extract_timeseries.py --demo 4
        same pipeline, writes into data_demo/ instead of data/

Options:
    --delete-raw   remove each .nii.gz after successful extraction (saves ~1 GB/subject)
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from common.io import load_config  # noqa: E402


def get_masker(cfg):
    from nilearn import datasets
    from nilearn.maskers import NiftiLabelsMasker

    atlas = datasets.fetch_atlas_schaefer_2018(
        n_rois=cfg["atlas"]["n_rois"], yeo_networks=cfg["atlas"]["yeo_networks"], resolution_mm=2
    )
    masker = NiftiLabelsMasker(
        labels_img=atlas.maps,
        standardize="zscore_sample",
        resampling_target="data",
        keep_masked_labels=True,  # keeps all 200 columns even if an ROI has no voxels
        verbose=0,
    )
    return masker, atlas


def extract_one(masker, img, n_rois):
    ts = masker.fit_transform(img).astype(np.float32)
    if ts.shape[1] != n_rois:
        raise ValueError(f"expected {n_rois} ROIs, got {ts.shape[1]}")
    bad = [int(i) for i in np.where(~np.isfinite(ts).all(0) | (ts.std(0) == 0))[0]]
    return ts, bad


def save(out_root: Path, sid: str, ts, bad, mean_motion, run):
    (out_root / "timeseries").mkdir(parents=True, exist_ok=True)
    (out_root / "qc").mkdir(parents=True, exist_ok=True)
    np.save(out_root / "timeseries" / f"sub-{sid}.npy", ts)
    info = dict(subject_id=sid, run=run, n_timepoints=int(ts.shape[0]),
                mean_fd=None if mean_motion is None else round(float(mean_motion), 4),
                bad_rois=bad)
    (out_root / "qc" / f"sub-{sid}.json").write_text(json.dumps(info, indent=2))
    print(f"  sub-{sid}: T={ts.shape[0]}, motion={info['mean_fd']}, bad ROIs={len(bad)}")


def run_hcp(cfg, masker, delete_raw):
    run = cfg["hcp"]["run"]
    raw = REPO / "data" / "raw"
    subs = sorted(p.name for p in raw.iterdir() if p.is_dir()) if raw.exists() else []
    if not subs:
        sys.exit("No subjects in data/raw/. Run download.py first (or use --demo).")
    for sid in subs:
        img = raw / sid / f"{run}_hp2000_clean.nii.gz"
        if not img.exists():
            print(f"  sub-{sid}: missing {img.name}, skipped")
            continue
        motion_f = raw / sid / "Movement_RelativeRMS_mean.txt"
        motion = float(motion_f.read_text().split()[0]) if motion_f.exists() else None
        try:
            ts, bad = extract_one(masker, str(img), cfg["atlas"]["n_rois"])
        except Exception as e:  # keep going; QC will mark it missing
            print(f"  sub-{sid}: FAILED — {e}")
            continue
        save(REPO / "data", sid, ts, bad, motion, run)
        if delete_raw:
            img.unlink()


def run_demo(cfg, masker, n):
    from nilearn import datasets
    import pandas as pd

    dev = datasets.fetch_development_fmri(n_subjects=n, reduce_confounds=False)
    for i, (img, conf) in enumerate(zip(dev.func, dev.confounds)):
        sid = f"demo{i + 1:02d}"
        fd = pd.read_csv(conf, sep="\t")["framewise_displacement"].mean()
        ts, bad = extract_one(masker, img, cfg["atlas"]["n_rois"])
        save(REPO / "data_demo", sid, ts, bad, fd, "nilearn_development")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", type=int, metavar="N", help="use N subjects of nilearn's dev dataset")
    ap.add_argument("--delete-raw", action="store_true")
    args = ap.parse_args()

    cfg = load_config()
    masker, _ = get_masker(cfg)
    if args.demo:
        run_demo(cfg, masker, args.demo)
    else:
        run_hcp(cfg, masker, args.delete_raw)


if __name__ == "__main__":
    main()
