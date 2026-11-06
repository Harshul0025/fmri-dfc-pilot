# fMRI Dynamic Connectivity Pilot

Exploratory pilot: static + dynamic functional connectivity, brain states, and their association with working memory, using 10–20 HCP Young Adult resting-state scans.

Full study design: `fMRI_Pilot_Research_Paper_Draft_Bullet_Points.docx`

## 📍 Current status — 6 Nov 2026

| Person | Done | Next (step by step) |
|---|---|---|
| **Vedansh (P1)** | ✅ Real data: 15/15 subjects, all pass QC. Zip shared privately. Motion check done → GSR switch added | Review & merge PRs → motion check on P3 metrics → final reproducibility run (week 3–4) |
| **Vishesh (P2)** | ✅ All P2 code on synthetic data (branch `p2-vishesh`); verified by Vedansh that it runs on real data | 1. Unzip real data, `data_root: data` · 2. Pull `main` (gets GSR) · 3. Rerun 3 scripts · 4. Update `paper/sections/static.md` with real numbers · 5. One no-GSR sensitivity run · 6. Open PR |
| **Vishal (P3)** | ⏳ Not pushed yet | 1. Build on synthetic data (all of P3 plan) · 2. Switch to real data · 3. Push C5 metrics + figures · 4. Write `paper/sections/dynamic.md` |
| **Harshul (P4)** | ⏳ Not pushed yet | 1. BALSA account → behavioural CSV → `behaviour.csv` for our 15 IDs · 2. Stats pipeline on synthetic metrics · 3. Paper skeleton + intro · 4. Real stats once P2/P3 metrics arrive |

**Key decision (6 Nov): global signal regression (GSR) is ON by default.** Without it, head motion drove whole-brain FC (QC-FC: 55% of edges motion-related; mean FC vs motion ρ = 0.65, p = 0.01). With GSR: 13% of edges, and the static graph metrics no longer correlate significantly with motion. GSR is applied inside `common/io.py:load_timeseries()`, so no one changes their code. Run once with `global_signal_regression: false` as a sensitivity check. P4 must still use motion (`mean_fd`) as a covariate.

**Real data** = `hcp_timeseries_15subj_FINAL.zip` (private, from Vedansh). Unzip in repo root → `data/`; set `data_root: data` locally (don't commit that line).

## Team

| Role | Owner | AI tool | Plan | Code folder | Branch |
|---|---|---|---|---|---|
| P1 — Data & QC + repo admin | **Vedansh** | Claude Code | [plans/P1_data.md](plans/P1_data.md) | `src/p1_data/` | `p1-vedansh` |
| P2 — Static FC & Network | **Vishesh** | Codex | [plans/P2_static_network.md](plans/P2_static_network.md) | `src/p2_static/`, `common/plotting.py` | `p2-vishesh` |
| P3 — Dynamic FC & Brain States | **Vishal** | Claude Code | [plans/P3_dynamic_states.md](plans/P3_dynamic_states.md) | `src/p3_dynamic/` | `p3-vishal` |
| P4 — Behaviour, Stats & Paper | **Harshul** | Claude Code | [plans/P4_behaviour_paper.md](plans/P4_behaviour_paper.md) | `src/p4_behaviour/`, `paper/` | `p4-harshul` |

### Why this split is equal
Total effort is about the same for each person; it just peaks at different times:

| Week | Vedansh (P1) | Vishesh (P2) | Vishal (P3) | Harshul (P4) |
|---|---|---|---|---|
| 1 | **Heavy** — HCP access, download, extraction | Medium — FC + figures on synthetic | Medium — sliding windows on synthetic | Medium — behaviour CSV, stats pipeline, intro |
| 2 | Medium — QC, motion checks, hand off data | Medium — network metrics + sensitivity | **Heavy** — k-means, K selection, robustness | Medium — related work, methods skeleton |
| 3 | Medium — review & merge PRs, confound checks | Light — rerun on real data, write section | Medium — rerun on real data, write section | **Heavy** — real stats + assemble paper |
| 4 | Medium — reproducibility run, final review | Light — figure polish, review | Light — review | **Heavy** — discussion, final draft |

- **Vishesh (Codex)** gets P2: clearly specified, standard numpy/networkx code with no open-ended research decisions. A solid medium-sized task, plus the shared plot style.
- **Claude users** get the roles with more open-ended debugging and judgement (HCP download/atlas issues, choosing K, writing the paper).
- **Vedansh** is also repo admin: reviews and merges PRs and does the final "fresh clone → full rerun" reproducibility check.

### Working with your AI
`CLAUDE.md` (Claude Code) and `AGENTS.md` (Codex) are already in the repo, so the AI knows the rules automatically. To start, open the repo and say:
> Read CONTRACTS.md and plans/PX_....md. Implement the first unchecked task in src/pX_.../ and test it on the synthetic data.

Tick the checkboxes in your plan file as you finish tasks, so everyone can see progress on GitHub.

## How we work independently (Diwali-proof)

1. **Contracts first.** Every hand-off between people is a file with a fixed format — see [CONTRACTS.md](CONTRACTS.md). Nobody changes a contract without telling the group.
2. **Fake data from day 1.** `python common/synthetic.py` creates realistic fake data in exactly the contract format inside `data_synthetic/`. Everyone builds and tests their code on it — no waiting for anyone.
3. **One switch to go real.** When real data exists, change `data_root` in `config.yaml` from `data_synthetic` to `data` and rerun your scripts. Nothing else changes.
4. **Own folder, own branch.** Work only in your `src/pX_*/` folder on branch `pX-<name>`; merge to `main` via pull request. This avoids merge conflicts.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python common/synthetic.py      # creates data_synthetic/
```

## Timeline

| Phase | When | What | Needs others? |
|---|---|---|---|
| 0. Kickoff | Day 1 (30-min call) | Read CONTRACTS.md, fill names, agree on config.yaml | Yes — only meeting required |
| 1. Build | Week 1–2 | Each person builds their pipeline on synthetic data | **No** |
| 2. Real data | When P1 pushes `data/` | P2 & P3 rerun on real data → push metrics | Only P1's output |
| 3. Integrate | After P2+P3 push metrics | P4 reruns stats on real metrics; everyone sends figures + methods text | Only files |
| 4. Paper | Final week | P4 assembles; everyone reviews their section | Async review |

## Repo layout

```
config.yaml          shared parameters (atlas, window length, k, paths)
CONTRACTS.md         file formats between people  ← read this first
common/              shared helpers (loading, synthetic data)
src/pX_*/            each person's code
plans/               each person's task plan
data/                REAL data (git-ignored — never commit HCP data)
data_synthetic/      fake data (git-ignored, regenerate any time)
results/             outputs (metrics CSVs are committed, big .npy files are not)
paper/               manuscript drafts and final figures
```

> HCP data use terms forbid redistributing the data. `data/` is git-ignored — keep it that way.
