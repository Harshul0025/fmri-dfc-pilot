# Data Contracts

These formats are how we hand work to each other. If your output matches this, the next person's code works without talking to you.
**Do not change a contract without posting in the group and updating this file.**

All paths are relative to `data_root` (from `config.yaml`): `data_synthetic/` while building, `data/` for real.
`subject_id` is always a **string** (HCP IDs like `"100307"`).

---

## C1 — ROI time series  (P1 → P2, P3)

`{data_root}/timeseries/sub-<subject_id>.npy`

- NumPy array, `float32`, shape **(T, 200)** — rows = time points, columns = Schaefer-200 ROIs (in atlas order, 7-network version).
- Each column z-scored (mean 0, std 1).
- HCP rest run: T = 1200, TR = 0.72 s.
- Files on disk are **without** global signal regression. `common/io.py:load_timeseries()` applies GSR when `preprocessing.global_signal_regression: true` in `config.yaml` (default). Always load through it.

## C2 — Subject list  (P1 → everyone)

`{data_root}/subjects.csv`

| column | type | meaning |
|---|---|---|
| subject_id | str | HCP ID |
| run | str | e.g. `rfMRI_REST1_LR` |
| n_timepoints | int | T after QC |
| mean_fd | float | mean relative head motion (HCP `Movement_RelativeRMS_mean`, mm) |
| included | bool | passes QC |
| exclusion_reason | str | empty if included |

Everyone analyses **only rows with `included == True`**.

## C3 — Behaviour  (P4 → P4, optional for others)

`{data_root}/behaviour.csv`

| column | type | meaning |
|---|---|---|
| subject_id | str | HCP ID |
| wm_score | float | primary working-memory measure (see P4 plan) |
| age_group | str | HCP age bracket, e.g. `26-30` |
| sex | str | `M`/`F` |

## C4 — Static metrics  (P2 → P4)

`results/static/metrics.csv` — one row per subject

| column | meaning |
|---|---|
| subject_id | |
| mean_fc | mean Fisher-z FC over all ROI pairs |
| mean_strength | mean node strength (thresholded graph) |
| mean_clustering | mean clustering coefficient |
| global_efficiency | global efficiency |
| density | edge density after threshold |

Also: `results/static/sub-<id>_fc.npy` — (200, 200) Fisher-z matrix (git-ignored, regenerable).

## C5 — Dynamic metrics  (P3 → P4)

`results/dynamic/metrics.csv` — one row per subject

| column | meaning |
|---|---|
| subject_id | |
| fc_variability | mean over edges of std of FC across windows |
| n_transitions | number of state switches |
| state<k>_frac | fraction of windows in state k (k = 1..K) |
| state<k>_dwell | mean consecutive windows spent in state k |

K comes from `config.yaml` (`dynamic.n_states`).
Also: `results/dynamic/state_centroids.npy` — (K, 200, 200).

## C6 — ROI labels  (shared, committed)

`common/schaefer200_7net_labels.csv` — load with `common.io.load_roi_labels()`

| column | meaning |
|---|---|
| roi_index | 0–199, same as the column index in C1 |
| label | Schaefer name, e.g. `7Networks_LH_Vis_1` |
| hemisphere | `LH` / `RH` |
| network | `Vis`, `SomMot`, `DorsAttn`, `SalVentAttn`, `Limbic`, `Cont`, `Default` |

---

Results folders are **always** `results/` (not under data_root). Metrics computed on synthetic data go to `results_synthetic/` — the helper `common/io.py:results_dir()` handles this automatically.
