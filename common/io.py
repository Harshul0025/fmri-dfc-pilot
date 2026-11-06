"""Shared loaders that follow CONTRACTS.md. Import with: from common.io import ..."""
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

REPO = Path(__file__).resolve().parent.parent


def load_config() -> dict:
    with open(REPO / "config.yaml") as f:
        return yaml.safe_load(f)


def data_dir(cfg: dict | None = None) -> Path:
    cfg = cfg or load_config()
    return REPO / cfg["data_root"]


def results_dir(cfg: dict | None = None) -> Path:
    """results/ for real data, results_synthetic/ for fake data."""
    cfg = cfg or load_config()
    name = "results_synthetic" if cfg["data_root"] == "data_synthetic" else "results"
    return REPO / name


def load_subjects(cfg: dict | None = None, included_only: bool = True) -> pd.DataFrame:
    df = pd.read_csv(data_dir(cfg) / "subjects.csv", dtype={"subject_id": str})
    return df[df["included"]].reset_index(drop=True) if included_only else df


def global_signal_regression(ts: np.ndarray) -> np.ndarray:
    """Regress the mean signal over all ROIs out of every ROI, then re-z-score."""
    g = ts.mean(1, keepdims=True)
    g = (g - g.mean()) / g.std()
    resid = ts - g * ((g * ts).sum(0) / (g * g).sum())
    sd = resid.std(0, ddof=1)
    sd[sd == 0] = 1
    return ((resid - resid.mean(0)) / sd).astype(np.float32)


def load_timeseries(subject_id: str, cfg: dict | None = None) -> np.ndarray:
    """(T, n_rois) float32 array — contract C1.

    If config.yaml → preprocessing.global_signal_regression is true (default),
    the global signal is regressed out here, so every script gets the same data.
    """
    cfg = cfg or load_config()
    ts = np.load(data_dir(cfg) / "timeseries" / f"sub-{subject_id}.npy")
    if cfg.get("preprocessing", {}).get("global_signal_regression", False):
        ts = global_signal_regression(ts)
    return ts


def load_roi_labels() -> pd.DataFrame:
    """Schaefer-200 (7-network) labels: roi_index, label, hemisphere, network — contract C6."""
    return pd.read_csv(REPO / "common" / "schaefer200_7net_labels.csv")


def load_behaviour(cfg: dict | None = None) -> pd.DataFrame:
    return pd.read_csv(data_dir(cfg) / "behaviour.csv", dtype={"subject_id": str})


def load_metrics(kind: str, cfg: dict | None = None) -> pd.DataFrame:
    """kind = 'static' (C4) or 'dynamic' (C5)."""
    return pd.read_csv(results_dir(cfg) / kind / "metrics.csv", dtype={"subject_id": str})
