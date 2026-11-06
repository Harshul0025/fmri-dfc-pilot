# P2 — Static Functional Connectivity & Network Analysis  ·  Owner: **Vishesh** (Codex)

**Effort: MEDIUM** (most straightforward methods; well-documented libraries).
**You consume:** C1, C2 · **You produce:** C4 (`results/static/metrics.csv`) → see [CONTRACTS.md](../CONTRACTS.md)
**You depend on:** nothing while building (use `data_synthetic/`). Real run needs P1's data.

Because this role is the lightest, P2 also owns the **shared figure style** and **reproducibility** (see the last section).

## Codex tips
- Codex reads `AGENTS.md` automatically. Give it one task at a time, e.g. *"Implement src/p2_static/compute_fc.py per plans/P2_static_network.md and CONTRACTS.md C1/C4; run it on the synthetic data."*
- Every task below has an exact input/output, so you can check each one by running it: the output file must match C4 in CONTRACTS.md.

## Tasks
- [ ] `src/p2_static/compute_fc.py`
  - for each included subject: Pearson correlation of the (T, 200) series → (200, 200)
  - Fisher z (`np.arctanh`, clip the diagonal first) → save `sub-<id>_fc.npy`
  - group-average matrix (average in z-space, then `tanh` back to r for display)
- [ ] Figures → `results/static/figures/`
  - group FC heatmap with ROIs sorted by Yeo network (labels come from the Schaefer atlas)
  - 2–3 example single-subject matrices
  - histogram of edge strengths
- [ ] `src/p2_static/network_metrics.py` (use `networkx` or `bctpy`)
  - keep the top `static.threshold_density` edges (proportional threshold), weighted, positive only
  - per subject: mean node strength, mean clustering coefficient, global efficiency, density
  - write `results/static/metrics.csv` in C4 format (this overwrites the synthetic placeholder)
- [ ] **Sensitivity check:** rerun the metrics at each `static.sensitivity_densities` value and save a small table showing whether subject rankings hold (Spearman between densities). The paper must report this.
- [ ] Network-level summary: mean within- vs between-network FC for the 7 Yeo networks (7×7 matrix figure).
- [ ] Write **Static FC + Network** methods and results paragraphs → `paper/sections/static.md`.

## Extra ownership (balances workload)
- [ ] `common/plotting.py`: one shared matplotlib style (font sizes, colormap `RdBu_r` centred at 0, figure size) that everyone imports.
- [ ] Keep `requirements.txt` pinned (`pip freeze`) and record software versions for the paper.

## Definition of done
- Scripts run end to end with `python src/p2_static/compute_fc.py && python src/p2_static/network_metrics.py`
- C4 file pushed for real data, plus figures and the sensitivity table
