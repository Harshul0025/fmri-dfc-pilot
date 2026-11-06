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


def load_timeseries(subject_id: str, cfg: dict | None = None) -> np.ndarray:
    """(T, n_rois) float32 array — contract C1."""
    return np.load(data_dir(cfg) / "timeseries" / f"sub-{subject_id}.npy")


def load_behaviour(cfg: dict | None = None) -> pd.DataFrame:
    return pd.read_csv(data_dir(cfg) / "behaviour.csv", dtype={"subject_id": str})


def load_metrics(kind: str, cfg: dict | None = None) -> pd.DataFrame:
    """kind = 'static' (C4) or 'dynamic' (C5)."""
    return pd.read_csv(results_dir(cfg) / kind / "metrics.csv", dtype={"subject_id": str})
