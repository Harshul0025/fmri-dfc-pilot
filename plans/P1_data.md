# P1 — Data & Quality Control  ·  Owner: **Vedansh** (Claude Code)

**Effort: HIGHEST** (slow external steps + biggest risk). Start on day 1.
**You produce:** C1 (time series) + C2 (subjects.csv) → see [CONTRACTS.md](../CONTRACTS.md)
**You depend on:** nobody.
**Who waits for you:** P2 and P3 for the *real* run only. They build on synthetic data meanwhile, so you are not blocking anyone day to day.

## Why this is the heaviest role
- HCP access needs an account + accepting data use terms; approval / AWS credentials can take a few days. **Apply on day 1.**
- One preprocessed rest run is roughly 1 GB per subject → 15–20 GB for 20 subjects. Check disk space and wifi.
- File format and atlas matching is the most fiddly debugging in the project.

## Tasks
- [ ] **Day 1:** Create ConnectomeDB account, accept Open Access terms, get AWS S3 credentials for the `hcp-openaccess` bucket.
- [ ] Pick 20 candidate subjects from HCP S1200 who have `rfMRI_REST1_LR` (extra buffer for QC drop-outs). Coordinate with P4 that they also have the working-memory score.
- [ ] Download **only** per subject:
  - `MNINonLinear/Results/rfMRI_REST1_LR/rfMRI_REST1_LR_hp2000_clean.nii.gz` (ICA-FIX cleaned, MNI volume)
  - `MNINonLinear/Results/rfMRI_REST1_LR/Movement_RelativeRMS_mean.txt` (motion, for QC)
- [ ] Write `src/p1_data/download.py` (aws cli / boto3, takes a subject list file).
- [ ] Write `src/p1_data/extract_timeseries.py`:
  - `nilearn.datasets.fetch_atlas_schaefer_2018(n_rois=200, yeo_networks=7, resolution_mm=2)`
  - `NiftiLabelsMasker(labels_img=..., standardize="zscore_sample")` → `(1200, 200)` array
  - save as `data/timeseries/sub-<id>.npy` (float32)
- [ ] Write `src/p1_data/qc.py` → builds `data/subjects.csv`:
  - exclude if mean motion > `qc.max_mean_fd` or T < `qc.min_timepoints` or any ROI is all-zero/NaN
  - fill `exclusion_reason`
- [ ] Sanity plots: one carpet plot + one ROI time series per subject → `results/qc/`.
- [ ] Delete raw `.nii.gz` after extraction if disk is tight (the `.npy` files are only ~1 MB each).
- [ ] Write the **Data & Preprocessing** methods paragraph (dataset, run, atlas, QC rules, final N) → `paper/sections/methods_data.md`.

## Tip: start before HCP access comes through
Run your extraction code on nilearn's small built-in dataset (`nilearn.datasets.fetch_development_fmri(n_subjects=2)`). Same code, real fMRI, works today.

## Repo admin (weeks 3–4, balances your load)
- [ ] Protect `main` on GitHub (require a PR); review and merge everyone's PRs.
- [ ] Motion confound check across the project: correlate `mean_fd` with P2/P3 metrics and send the table to Harshul.
- [ ] Final reproducibility test: fresh clone → `pip install -r requirements.txt` → run every script in order → same numbers. Write `RUN_ALL.md` with the exact command sequence.

## Definition of done
- `data/timeseries/` has ≥10 included subjects in C1 format
- `data/subjects.csv` matches C2
- Group message posted: "real data ready, N = __"

Real data must be shared **privately** (Drive link to the group), never committed to git.
