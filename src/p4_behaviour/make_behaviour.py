"""HCP unrestricted behavioural CSV → contract C3 (behaviour.csv) for our subjects.

    python src/p4_behaviour/make_behaviour.py path/to/unrestricted_behavioral.csv

Primary working-memory score: ListSort_Unadj (NIH Toolbox List Sorting Working
Memory test, unadjusted scale score). Why: it is a standard, validated WM measure,
it is measured outside the scanner (so it is independent of the fMRI session we
analyse), and it is in the unrestricted HCP file for almost every subject.
Alternative with --wm-column WM_Task_2bk_Acc (in-scanner 2-back accuracy).

Subjects come from {data_root}/subjects.csv (C2), included rows only.
Output: {data_root}/behaviour.csv with subject_id, wm_score, age_group, sex.
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from common.io import data_dir, load_config, load_subjects  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("behaviour_csv", help="HCP unrestricted behavioural CSV from BALSA")
    ap.add_argument("--wm-column", default="ListSort_Unadj")
    args = ap.parse_args()

    cfg = load_config()
    ids = load_subjects(cfg)["subject_id"]

    hcp = pd.read_csv(args.behaviour_csv, dtype={"Subject": str})
    need = ["Subject", args.wm_column, "Age", "Gender"]
    missing_cols = [c for c in need if c not in hcp.columns]
    if missing_cols:
        sys.exit(f"Columns not found in {args.behaviour_csv}: {missing_cols}")

    beh = hcp[need].rename(columns={"Subject": "subject_id", args.wm_column: "wm_score",
                                    "Age": "age_group", "Gender": "sex"})
    beh = beh[beh["subject_id"].isin(ids)].sort_values("subject_id")

    not_in_csv = sorted(set(ids) - set(beh["subject_id"]))
    no_score = beh.loc[beh["wm_score"].isna(), "subject_id"].tolist()
    beh = beh.dropna(subset=["wm_score"])

    out = data_dir(cfg) / "behaviour.csv"
    beh.to_csv(out, index=False)
    print(f"Wrote {len(beh)}/{len(ids)} subjects to {out} (wm_score = {args.wm_column})")
    if not_in_csv:
        print(f"  not in behavioural CSV: {not_in_csv}")
    if no_score:
        print(f"  missing {args.wm_column}: {no_score}  ← tell P1")
    print("IDs with a WM score:", " ".join(beh["subject_id"]))


if __name__ == "__main__":
    main()
