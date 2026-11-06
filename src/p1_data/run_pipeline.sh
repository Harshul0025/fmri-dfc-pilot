#!/usr/bin/env bash
# Download + extract one subject at a time, then QC. Safe to stop and rerun:
# finished subjects are skipped.
#   bash src/p1_data/run_pipeline.sh        # first 15 candidates
#   bash src/p1_data/run_pipeline.sh 20     # first 20
set -u
cd "$(dirname "$0")/../.."
PY=${PY:-.venv/bin/python}
N=${1:-15}
ids=$(grep -v '^#' src/p1_data/candidates.txt | grep -v '^\s*$' | head -n "$N")
i=0
for sid in $ids; do
  i=$((i+1)); echo "=== [$i/$N] $sid  $(date +%H:%M) ==="
  $PY -u src/p1_data/download.py --subject "$sid" && \
  $PY -u src/p1_data/extract_timeseries.py --subject "$sid" --delete-raw
done
$PY -u src/p1_data/qc.py
