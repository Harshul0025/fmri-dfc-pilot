# P3 — Dynamic Functional Connectivity & Brain States

**Effort: HIGH** (most methodological choices; heaviest compute).
**You consume:** C1, C2 · **You produce:** C5 (`results/dynamic/metrics.csv`) → see [CONTRACTS.md](../CONTRACTS.md)
**You depend on:** nothing while building. The synthetic data has hidden states built in, so you can check that your clustering finds them.

## Tasks
- [ ] `src/p3_dynamic/sliding_window.py`
  - windows of `dynamic.window_tr` TRs, step `dynamic.step_tr` (Hann or rectangular taper, choose one and document it)
  - (1200 − 60) / 5 + 1 ≈ 229 windows per subject
  - per window: correlation → Fisher z → keep the **upper triangle only** (19,900 values; saves memory)
  - save per subject: (n_windows, 19900) float32
- [ ] `fc_variability` per subject = mean over edges of the std across windows
- [ ] `src/p3_dynamic/states.py`
  - stack all subjects' windows → k-means (`sklearn`, `n_init=20`, seed from config)
  - laptop tip: 15 subjects × 229 × 19,900 is about 270 MB in float32. If it is slow, run PCA to ~50 components first, or cluster subsampled windows and then assign all windows
  - choose K: elbow + silhouette for K = 2..8 → justify the chosen K in the paper (update `config.yaml` and tell the group if it is not 4)
  - per subject: `state<k>_frac`, `state<k>_dwell` (mean run length), `n_transitions`
  - save `state_centroids.npy` (K, 200, 200) and `metrics.csv` (C5)
- [ ] Figures → `results/dynamic/figures/`
  - centroid matrix per state (sorted by Yeo network)
  - state time course for 3 example subjects
  - bar plot of fraction of time in each state (mean ± SD across subjects)
- [ ] **Robustness:** rerun with window = 40 and 90 TRs. Do the states look similar? (match centroids by correlation). Report this briefly.
- [ ] Write **Dynamic FC + Brain States** methods and results → `paper/sections/dynamic.md`.

## Pitfalls to mention in the paper
- Short windows give noisy FC; long windows hide the dynamics. That is why we test robustness.
- Head motion can create fake "states". Ask P1 for per-subject `mean_fd` and check whether state fractions correlate with motion.

## Definition of done
- C5 file pushed for real data, plus the K-selection plot, centroid figures and robustness note
