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
- [x] **Day 1:** Create account (BALSA — ConnectomeDB is retired)
- [ ] Sign HCP-YA Data Use Terms on BALSA → project "HCP-Young Adult 2025" → "Get/Reset AWS S3 access" → save as `[hcp]` profile in `~/.aws/credentials`
- [ ] Pick 20 candidate subjects from HCP S1200 who have `rfMRI_REST1_LR` (extra buffer for QC drop-outs). Coordinate with P4 that they also have the working-memory score.
- [ ] Download **only** per subject:
  - `MNINonLinear/Results/rfMRI_REST1_LR/rfMRI_REST1_LR_hp2000_clean.nii.gz` (ICA-FIX cleaned, MNI volume)
  - `MNINonLinear/Results/rfMRI_REST1_LR/Movement_RelativeRMS_mean.txt` (motion, for QC)
- [x] Write `src/p1_data/download.py` (aws cli / boto3, takes a subject list file).
- [x] Write `src/p1_data/extract_timeseries.py`:
  - `nilearn.datasets.fetch_atlas_schaefer_2018(n_rois=200, yeo_networks=7, resolution_mm=2)`
  - `NiftiLabelsMasker(labels_img=..., standardize="zscore_sample")` → `(1200, 200)` array
  - save as `data/timeseries/sub-<id>.npy` (float32)
- [x] Write `src/p1_data/qc.py` → builds `data/subjects.csv`:
  - exclude if mean motion > `qc.max_mean_fd` or T < `qc.min_timepoints` or any ROI is all-zero/NaN
  - fill `exclusion_reason`
- [x] Sanity plots: one carpet plot + one ROI time series per subject → `results/qc/`.
- [ ] Delete raw `.nii.gz` after extraction if disk is tight (the `.npy` files are only ~1 MB each).
- [ ] Write the **Data & Preprocessing** methods paragraph (draft done — fill numbers after real run) (dataset, run, atlas, QC rules, final N) → `paper/sections/methods_data.md`.

## Status
Code done. Real run in progress: CIFTI files, 15 subjects, one at a time (`bash src/p1_data/run_pipeline.sh 15`, log in `data/pipeline.log`). S3 → India gives only ~0.25 MB/s, so ~33 min per subject.
Why CIFTI instead of the MNI volume: 440 MB vs 1 GB per subject, and it is HCP's recommended space. Same Schaefer parcel order, so the C1 contract is unchanged.

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
