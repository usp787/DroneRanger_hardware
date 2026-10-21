#!/bin/bash -l
# One-time setup on Explorer: images, PX4 v1.14.3 build, Pegasus v5.1.0 and Python packages.
# Run it on a CPU compute node (pulls and the PX4 build are heavy):
#   bash ~/DroneRanger_hardware/wind/isaac_pegasus/explorer/submit.sh setup      # batch job (recommended)
# or interactively:
#   srun --partition=short --time=02:00:00 --cpus-per-task=8 --mem=32G --pty bash
#   bash ~/DroneRanger_hardware/wind/isaac_pegasus/explorer/01_setup.sh
# Re-running it skips what already exists. Needs about 20 GB in $DR_ROOT.
set -euo pipefail
source "${DR_REPO:-$HOME/DroneRanger_hardware}/wind/isaac_pegasus/explorer/env.sh"   # not $0: sbatch runs a copy
module load explorer 2>/dev/null || echo "note: 'module load explorer' failed; internet may need the proxy"

mkdir -p "$DR_ROOT"/{images,runs} "$APPTAINER_CACHEDIR" "$APPTAINER_TMPDIR" "$PYUSER" "$DR_RESULTS"
echo "== apptainer $(apptainer version)"

echo "== 1/4 container images"
[ -f "$ISAAC_SIF" ] || apptainer pull "$ISAAC_SIF" "$ISAAC_IMAGE"
[ -f "$PX4_SIF" ] || apptainer pull "$PX4_SIF" "$PX4_IMAGE"

echo "== 2/4 PX4 $PX4_TAG (SITL build inside the px4-dev container)"
if [ ! -d "$PX4_DIR" ]; then
    git clone --branch "$PX4_TAG" --depth 1 --recurse-submodules --shallow-submodules \
        https://github.com/PX4/PX4-Autopilot.git "$PX4_DIR"
fi
# PX4's version-header step (src/lib/version/px_update_git_header.py) lists the tags of the NuttX submodule and
# takes the highest nuttx-X.Y.Z; a shallow submodule has none, so the build fails with an IndexError. The value
# is only a version string, so recreate the highest upstream tag name locally instead of fetching history.
NUTTX="$PX4_DIR/platforms/nuttx/NuttX/nuttx"
if [ -e "$NUTTX/.git" ] && ! git -C "$NUTTX" tag | grep -qE '^nuttx-[0-9]+\.[0-9]+\.[0-9]+'; then
    NUTTX_TAG=$(git -C "$NUTTX" ls-remote --tags origin 'nuttx-*' \
        | sed -n 's#.*refs/tags/\(nuttx-[0-9]*\.[0-9]*\.[0-9]*\)$#\1#p' | sort -V | tail -1)
    git -C "$NUTTX" tag "${NUTTX_TAG:-nuttx-0.0.0}" HEAD
    echo "created local NuttX tag ${NUTTX_TAG:-nuttx-0.0.0} (needed by PX4's version header)"
fi
if [ ! -x "$PX4_DIR/build/px4_sitl_default/bin/px4" ]; then
    # `exec`, not `run`: the image's entrypoint script expects Docker. Plain build target; the `none`
    # target would also start PX4 afterwards.
    apptainer exec --cleanenv --bind "$DR_ROOT" --env "CCACHE_DIR=$DR_ROOT/ccache" "$PX4_SIF" \
        bash -c "cd '$PX4_DIR' && make px4_sitl_default -j${SLURM_CPUS_PER_TASK:-8}"
fi
ls -l "$PX4_DIR/build/px4_sitl_default/bin/px4"

echo "== 3/4 Pegasus $PEGASUS_TAG (used from PYTHONPATH; no 'pip install -e', which edits the read-only image)"
[ -d "$PEGASUS_DIR" ] || git clone --branch "$PEGASUS_TAG" --depth 1 \
    https://github.com/PegasusSimulator/PegasusSimulator.git "$PEGASUS_DIR"

echo "== 4/4 Python packages for Isaac's Python (into $PYUSER)"
ENVF="$DR_ROOT/setup.env"
write_env_file "$ENVF" $(isaac_env_vars)
# mavsdk<4: v4 (2026) replaced the gRPC-based API that fly_hover.py uses (System() raises TypeError in v4).
isaac_exec "$ENVF" /isaac-sim/python.sh -m pip install --user --no-warn-script-location \
    pymavlink pyyaml toml "mavsdk<4" pandas
isaac_exec "$ENVF" /isaac-sim/python.sh -c \
    "import numpy, scipy, pymavlink, yaml, toml, mavsdk, pandas; from importlib.metadata import version; \
print('python packages ok, mavsdk', version('mavsdk'))"

echo "== setup done. Next: bash $DR_REPO/wind/isaac_pegasus/explorer/submit.sh check"
