#!/bin/bash
# Submit an Explorer job with the settings from env.sh. Slurm .out files land in $DR_RESULTS.
#   bash submit.sh setup              # one-time setup on a CPU node (`short`, 2 h): images, PX4 build, Pegasus
#   bash submit.sh check              # stage A+B: GPU node + Isaac/Pegasus/WindDrag check (no PX4)
#   bash submit.sh smoke [wind-spec]  # stage C: full smoke test; wind-spec defaults to "smoke" (dummy profile)
# Override anything for one submission, e.g.:  DR_GRES=gpu:a6000:1 bash submit.sh check
set -euo pipefail
source "$(dirname "$(readlink -f "$0")")/env.sh"
mode="${1:-}"
[ $# -gt 0 ] && shift
mkdir -p "$DR_RESULTS"
cd "$DR_RESULTS"
EXPORT="ALL,DR_REPO=$DR_REPO,DR_ROOT=$DR_ROOT,DR_RESULTS=$DR_RESULTS"
case "$mode" in
    setup)
        sbatch --job-name=dr-setup --partition=short --time=02:00:00 --cpus-per-task=8 --mem=32G \
            --output=%x-%j.out --export="$EXPORT" "$DR_REPO/wind/isaac_pegasus/explorer/01_setup.sh" ;;
    check | smoke)
        script=$([ "$mode" = check ] && echo check_node.sbatch || echo run_smoke.sbatch)
        sbatch --partition="$DR_PARTITION" --gres="$DR_GRES" --time="$DR_TIME" --mem="$DR_MEM" \
            --cpus-per-task="$DR_CPUS" --export="$EXPORT" "$DR_REPO/wind/isaac_pegasus/explorer/$script" "$@" ;;
    *) echo "usage: $0 setup | check | smoke [wind-spec]"; exit 1 ;;
esac
