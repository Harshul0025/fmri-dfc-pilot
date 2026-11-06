"""Pick candidate subjects from the HCP unrestricted behavioural CSV.

Keeps subjects with a complete resting-state session and a working-memory score,
then writes the first N (sorted by ID, for reproducibility) to candidates.txt.

Usage (from repo root):
    python src/p1_data/select_subjects.py path/to/unrestricted_behavioral.csv --n 20
"""
import argparse
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("behaviour_csv")
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--wm-column", default="ListSort_Unadj")
    args = ap.parse_args()

    df = pd.read_csv(args.behaviour_csv, dtype={"Subject": str})
    keep = df[df["3T_RS-fMRI_PctCompl"] == 100]
    keep = keep[keep[args.wm_column].notna()].sort_values("Subject")
    ids = keep["Subject"].head(args.n).tolist()

    out = HERE / "candidates.txt"
    header = f"# Selected by select_subjects.py: full rest session + non-missing {args.wm_column}\n"
    out.write_text(header + "\n".join(ids) + "\n")
    print(f"{len(keep)} eligible subjects; wrote {len(ids)} to {out}")


if __name__ == "__main__":
    main()
