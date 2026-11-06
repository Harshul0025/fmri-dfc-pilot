# Agent instructions (Codex & Claude Code)

Project: exploratory fMRI pilot, static + dynamic functional connectivity vs working memory, on 10–20 HCP subjects. See README.md.

## Rules
1. **Read `CONTRACTS.md` first.** Every output file must match its contract exactly (paths, shapes, column names). Never change a contract on your own.
2. **Stay in your folder.** P1 → `src/p1_data/`, P2 → `src/p2_static/` (+ `common/plotting.py`), P3 → `src/p3_dynamic/`, P4 → `src/p4_behaviour/` + `paper/`. Do not edit another person's folder, `common/io.py`, `common/synthetic.py` or `config.yaml` without being asked.
3. **Load data only through `common/io.py`** (`load_config`, `load_subjects`, `load_timeseries`, `load_metrics`, `results_dir`). Never hard-code `data/` or `data_synthetic/`; the switch is `data_root` in `config.yaml`.
4. **Read parameters from `config.yaml`**, never hard-code them (window length, K, thresholds, seeds).
5. **Test on synthetic data:** `python common/synthetic.py` first, then run your script from the repo root.
6. **Never commit data**: no `data/`, `.nii.gz` or `.npy` files. HCP terms forbid redistribution.
7. Scripts must run from the repo root as `python src/pX_.../script.py`. Add `sys.path.insert(0, <repo root>)` to import `common`.
8. Tick the checkbox in your `plans/PX_*.md` when a task is done.
9. Language for results: "exploratory association", never "predicts". Small N.
