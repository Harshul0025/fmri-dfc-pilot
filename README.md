# fMRI Dynamic Connectivity Pilot

Exploratory pilot: static + dynamic functional connectivity, brain states, and their association with working memory, using 10–20 HCP Young Adult resting-state scans.

Full study design: `fMRI_Pilot_Research_Paper_Draft_Bullet_Points.docx`

## Team

| Role | Owner | Plan | Code folder |
|---|---|---|---|
| P1 — Data & QC | _name_ | [plans/P1_data.md](plans/P1_data.md) | `src/p1_data/` |
| P2 — Static FC & Network | _name_ | [plans/P2_static_network.md](plans/P2_static_network.md) | `src/p2_static/` |
| P3 — Dynamic FC & Brain States | _name_ | [plans/P3_dynamic_states.md](plans/P3_dynamic_states.md) | `src/p3_dynamic/` |
| P4 — Behaviour, Stats & Paper | _name_ | [plans/P4_behaviour_paper.md](plans/P4_behaviour_paper.md) | `src/p4_behaviour/`, `paper/` |

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
