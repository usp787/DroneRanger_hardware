#!/bin/bash
# Submit an Explorer job with the partition/GPU settings from env.sh.
#   bash submit.sh check              # stage A+B: GPU node + Isaac/Pegasus/WindDrag check (no PX4)
#   bash submit.sh smoke [wind-spec]  # stage C: full smoke test; wind-spec defaults to "smoke" (dummy profile)
# Override anything for one submission, e.g.:  DR_GRES=gpu:a6000:1 bash submit.sh check
set -euo pipefail
source "$(dirname "$(readlink -f "$0")")/env.sh"
case "${1:-}" in
    check) script=check_node.sbatch ;;
    smoke) script=run_smoke.sbatch ;;
    *) echo "usage: $0 check | smoke [wind-spec]"; exit 1 ;;
esac
shift
cd "$DR_RESULTS" 2>/dev/null || { mkdir -p "$DR_RESULTS"; cd "$DR_RESULTS"; }   # Slurm .out files land here
sbatch --partition="$DR_PARTITION" --gres="$DR_GRES" --time="$DR_TIME" --mem="$DR_MEM" \
    --cpus-per-task="$DR_CPUS" --export=ALL,DR_REPO="$DR_REPO",DR_ROOT="$DR_ROOT",DR_RESULTS="$DR_RESULTS" \
    "$DR_REPO/wind/isaac_pegasus/explorer/$script" "$@"
