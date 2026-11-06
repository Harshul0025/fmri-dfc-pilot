"""Extract Schaefer-200 ROI time series → contract C1, plus per-subject QC info.

Real HCP (after download.py):
    python src/p1_data/extract_timeseries.py [--subject ID] [--delete-raw]
        reads  data/raw/<id>/<run>_Atlas_hp2000_clean.dtseries.nii   (CIFTI, default)
            or data/raw/<id>/<run>_hp2000_clean.nii.gz                (MNI volume)
        writes data/timeseries/sub-<id>.npy   (T, 200) float32, z-scored
               data/qc/sub-<id>.json          T, mean motion, bad ROIs
        Subjects already extracted are skipped (use --force to redo).

    CIFTI: mean over cortical grayordinates in each parcel of the Schaefer 2018
    fsLR-32k dlabel (official CBIG file, auto-downloaded to data/atlas/).
    Volume: nilearn NiftiLabelsMasker with the 2 mm MNI Schaefer atlas.
    Parcel order (1..200) is identical in both versions.

Demo (works without HCP access — nilearn's small public volumetric dataset):
    python src/p1_data/extract_timeseries.py --demo 4      → data_demo/
"""
import argparse
import json
import sys
import urllib.request
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from common.io import load_config  # noqa: E402

DLABEL_URL = (
    "https://raw.githubusercontent.com/ThomasYeoLab/CBIG/master/stable_projects/"
    "brain_parcellation/Schaefer2018_LocalGlobal/Parcellations/HCP/fslr32k/cifti/"
    "Schaefer2018_{n}Parcels_{k}Networks_order.dlabel.nii"
)


def zscore(ts):
    sd = ts.std(0, ddof=1)
    sd[sd == 0] = 1
    return ((ts - ts.mean(0)) / sd).astype(np.float32)


def bad_rois(ts):
    return [int(i) for i in np.where(~np.isfinite(ts).all(0) | (ts.std(0) == 0))[0]]


# ---------- CIFTI ----------
class CiftiParcellator:
    def __init__(self, cfg):
        import nibabel as nb

        n, k = cfg["atlas"]["n_rois"], cfg["atlas"]["yeo_networks"]
        path = REPO / "data" / "atlas" / f"Schaefer2018_{n}Parcels_{k}Networks_order.dlabel.nii"
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(DLABEL_URL.format(n=n, k=k), path)
        dl = nb.load(path)
        lab = dl.get_fdata()[0].astype(int)
        self.n = n
        # structure name -> {vertex index: parcel label}
        self.lookup = {}
        for name, slc, sub in dl.header.get_axis(1).iter_structures():
            self.lookup[name] = dict(zip(sub.vertex, lab[slc]))
        self.names = [dl.header.get_axis(0).label[0][i][0] for i in range(1, n + 1)]

    def __call__(self, path):
        import nibabel as nb

        img = nb.load(path)
        data = np.asarray(img.dataobj, dtype=np.float32)  # (T, grayordinates)
        labels = np.zeros(data.shape[1], dtype=int)
        for name, slc, sub in img.header.get_axis(1).iter_structures():
            if name in self.lookup and sub.vertex is not None:
                m = self.lookup[name]
                labels[slc] = [m.get(v, 0) for v in sub.vertex]
        ts = np.full((data.shape[0], self.n), np.nan, dtype=np.float32)
        for p in range(1, self.n + 1):
            idx = labels == p
            if idx.any():
                ts[:, p - 1] = data[:, idx].mean(1)
        return zscore(ts)


# ---------- volume ----------
class VolumeParcellator:
    def __init__(self, cfg):
        from nilearn import datasets
        from nilearn.maskers import NiftiLabelsMasker

        atlas = datasets.fetch_atlas_schaefer_2018(
            n_rois=cfg["atlas"]["n_rois"], yeo_networks=cfg["atlas"]["yeo_networks"], resolution_mm=2
        )
        self.n = cfg["atlas"]["n_rois"]
        self.masker = NiftiLabelsMasker(labels_img=atlas.maps, resampling_target="data",
                                        keep_masked_labels=True, verbose=0)

    def __call__(self, img):
        ts = self.masker.fit_transform(img).astype(np.float32)
        if ts.shape[1] != self.n:
            raise ValueError(f"expected {self.n} ROIs, got {ts.shape[1]}")
        return zscore(ts)


def save(out_root: Path, sid: str, ts, mean_motion, run, source):
    (out_root / "timeseries").mkdir(parents=True, exist_ok=True)
    (out_root / "qc").mkdir(parents=True, exist_ok=True)
    bad = bad_rois(ts)
    ts = np.nan_to_num(ts)
    np.save(out_root / "timeseries" / f"sub-{sid}.npy", ts)
    info = dict(subject_id=sid, run=run, source=source, n_timepoints=int(ts.shape[0]),
                mean_fd=None if mean_motion is None else round(float(mean_motion), 4),
                bad_rois=bad)
    (out_root / "qc" / f"sub-{sid}.json").write_text(json.dumps(info, indent=2))
    print(f"  sub-{sid}: T={ts.shape[0]}, motion={info['mean_fd']}, bad ROIs={len(bad)}", flush=True)


def run_hcp(cfg, subject, delete_raw, force):
    run = cfg["hcp"]["run"]
    raw = REPO / "data" / "raw"
    subs = [subject] if subject else (sorted(p.name for p in raw.iterdir() if p.is_dir()) if raw.exists() else [])
    if not subs:
        sys.exit("No subjects in data/raw/. Run download.py first (or use --demo).")
    parc = {}
    for sid in subs:
        if not force and (REPO / "data" / "timeseries" / f"sub-{sid}.npy").exists():
            print(f"  sub-{sid}: already extracted, skipped")
            continue
        cifti = raw / sid / f"{run}_Atlas_hp2000_clean.dtseries.nii"
        vol = raw / sid / f"{run}_hp2000_clean.nii.gz"
        img, kind = (cifti, "cifti") if cifti.exists() else (vol, "volume")
        if not img.exists():
            print(f"  sub-{sid}: no image file, skipped")
            continue
        if kind not in parc:
            parc[kind] = CiftiParcellator(cfg) if kind == "cifti" else VolumeParcellator(cfg)
        motion_f = raw / sid / "Movement_RelativeRMS_mean.txt"
        motion = float(motion_f.read_text().split()[0]) if motion_f.exists() else None
        try:
            ts = parc[kind](str(img))
        except Exception as e:  # keep going; QC marks it as failed
            print(f"  sub-{sid}: FAILED — {e}")
            continue
        save(REPO / "data", sid, ts, motion, run, kind)
        if delete_raw:
            img.unlink()


def run_demo(cfg, n):
    import pandas as pd
    from nilearn import datasets

    parc = VolumeParcellator(cfg)
    dev = datasets.fetch_development_fmri(n_subjects=n, reduce_confounds=False)
    for i, (img, conf) in enumerate(zip(dev.func, dev.confounds)):
        fd = pd.read_csv(conf, sep="\t")["framewise_displacement"].mean()
        save(REPO / "data_demo", f"demo{i + 1:02d}", parc(img), fd, "nilearn_development", "volume")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", type=int, metavar="N", help="use N subjects of nilearn's dev dataset")
    ap.add_argument("--subject")
    ap.add_argument("--delete-raw", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    cfg = load_config()
    if args.demo:
        run_demo(cfg, args.demo)
    else:
        run_hcp(cfg, args.subject, args.delete_raw, args.force)


if __name__ == "__main__":
    main()
