# P4 — Behaviour, Statistics & Paper Lead  ·  Owner: **Harshul** (Claude Code)

**Effort: MEDIUM coding + HIGH writing.** The workload grows in the final week, so front-load the writing.
**You consume:** C2, C4, C5 · **You produce:** C3 (`behaviour.csv`), the stats, and the assembled paper
**You depend on:** nothing while building. `common/synthetic.py` already gives you fake C4/C5 metrics with a planted weak effect, so your whole stats pipeline can be finished before anyone else is done.

## Tasks — behaviour (week 1)
- [ ] Download the HCP **unrestricted behavioural CSV** from BALSA (balsa.wustl.edu, HCP-Young Adult project; ConnectomeDB is retired).
- [ ] Choose the primary working-memory score. Suggested: `ListSort_Unadj` (NIH Toolbox List Sorting WM). Alternative: `WM_Task_2bk_Acc`. Decide, then document why.
- [ ] `src/p4_behaviour/make_behaviour.py` → `data/behaviour.csv` in C3 format, only for P1's subject list.
- [ ] Send P1 the IDs that **have** the WM score, so P1 doesn't download subjects without behaviour data.

## Tasks — stats (week 1–2, on synthetic data)
- [ ] `src/p4_behaviour/associations.py`
  - merge C4 + C5 + C3 on `subject_id`, keep included subjects only
  - for each metric vs `wm_score`: Pearson r **and** Spearman ρ, p-value, 95% CI (bootstrap, 5,000 resamples)
  - FDR correction (Benjamini–Hochberg) across all metrics tested
  - scatterplot grid with regression line → `results/stats/figures/`
  - results table → `results/stats/associations.csv`
  - control check: correlate `mean_fd` with WM and with the key metrics (is motion driving anything?)
- [ ] Descriptives table: N, age groups, sex, WM mean ± SD, mean FD.

## Tasks — paper (start in week 1, not at the end)
- [ ] `paper/manuscript.md` skeleton: Abstract, Intro, Methods, Results, Discussion, Limitations, References
- [ ] Write the **Intro** + related work now (static vs dynamic FC, brain states, HCP). Collect 10–15 references.
- [ ] Merge everyone's section files from `paper/sections/` and keep a consistent voice.
- [ ] Discussion + Limitations: stay cautious. Write "preliminary/exploratory association", not "predicts". No clinical claims. Mention the small N.
- [ ] Final checklist from the docx §6: N after QC, effect sizes + CIs, all parameters (atlas, window, step, K, threshold, software versions).

## Definition of done
- Stats rerun on real C4/C5 with one command
- Full manuscript draft with figures from P1–P3
