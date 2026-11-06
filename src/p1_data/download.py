"""Download only the files we need from the HCP open-access S3 bucket.

Per subject:
    MNINonLinear/Results/<run>/<run>_Atlas_hp2000_clean.dtseries.nii  (default, CIFTI, ≈440 MB)
      or <run>_hp2000_clean.nii.gz with --format volume               (MNI volume, ≈1 GB)
    MNINonLinear/Results/<run>/Movement_RelativeRMS_mean.txt (mean frame-to-frame motion, mm)
Both are ICA-FIX cleaned. CIFTI is the default: half the size (S3 → India is slow,
~0.3 MB/s) and HCP's recommended grayordinate space.

Credentials (ConnectomeDB is retired; keys now come from BALSA, since Apr 2026):
    1. Log in at https://balsa.wustl.edu and sign the HCP-YA Data Use Terms
    2. Open the "HCP-Young Adult 2025" project → "Get/Reset AWS S3 access"
    3. Store the keys as a named profile (S3 serves the 2017 S1200 release, which we use):
    ~/.aws/credentials
        [hcp]
        aws_access_key_id = ...
        aws_secret_access_key = ...

Usage (from repo root):
    python src/p1_data/download.py                 # all IDs in candidates.txt
    python src/p1_data/download.py --limit 1       # try one subject first
    python src/p1_data/download.py --subject 100307 # one specific subject
    python src/p1_data/download.py --profile hcp --dry-run
"""
import argparse
import sys
from pathlib import Path

import boto3
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from common.io import load_config  # noqa: E402

BUCKET = "hcp-openaccess"
PREFIX = "HCP_1200"


def read_ids(path: Path) -> list[str]:
    return [ln.strip() for ln in path.read_text().splitlines()
            if ln.strip() and not ln.startswith("#")]


def files_for(sid: str, run: str, fmt: str = "cifti") -> list[str]:
    base = f"{PREFIX}/{sid}/MNINonLinear/Results/{run}"
    img = f"{run}_Atlas_hp2000_clean.dtseries.nii" if fmt == "cifti" else f"{run}_hp2000_clean.nii.gz"
    return [f"{base}/Movement_RelativeRMS_mean.txt", f"{base}/{img}"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", default=str(REPO / "src/p1_data/candidates.txt"))
    ap.add_argument("--profile", default="hcp")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--subject", help="download just this subject ID")
    ap.add_argument("--format", choices=["cifti", "volume"], default="cifti")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cfg = load_config()
    run = cfg["hcp"]["run"]
    raw = REPO / "data" / "raw"
    ids = [args.subject] if args.subject else read_ids(Path(args.ids))[: args.limit]

    try:
        s3 = boto3.Session(profile_name=args.profile).client("s3")
    except ProfileNotFound:
        sys.exit(f"AWS profile '{args.profile}' not found. Get keys from BALSA — see the docstring at the top of this file.")

    failed = []
    for i, sid in enumerate(ids, 1):
        for key in files_for(sid, run, args.format):
            dest = raw / sid / Path(key).name
            if dest.exists() or (REPO / "data" / "timeseries" / f"sub-{sid}.npy").exists():
                print(f"[{i}/{len(ids)}] {sid}: {dest.name} already present")
                continue
            if args.dry_run:
                print(f"[{i}/{len(ids)}] would download s3://{BUCKET}/{key}")
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            tmp = dest.with_suffix(dest.suffix + ".part")
            try:
                print(f"[{i}/{len(ids)}] {sid}: downloading {dest.name} ...", flush=True)
                s3.download_file(BUCKET, key, str(tmp))
                tmp.rename(dest)
            except NoCredentialsError:
                sys.exit("No AWS credentials. See the docstring at the top of this file.")
            except ClientError as e:
                tmp.unlink(missing_ok=True)
                print(f"    FAILED ({e.response['Error'].get('Code')}): {key}")
                failed.append(sid)

    if failed:
        sys.stderr.write(f"FAILED: {sorted(set(failed))}\n")
        print(f"\nFailed subjects (check access / availability): {sorted(set(failed))}")
    print("Done.")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
