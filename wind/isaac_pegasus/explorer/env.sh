# Settings shared by the Explorer scripts. Source it:  source wind/isaac_pegasus/explorer/env.sh
# Edit the block below; everything else is derived. Facts behind the defaults: ../README.md, "Explorer notes".

# ------------------------------------------------------------------------------------------------ edit
export DR_ROOT="${DR_ROOT:-/scratch/$USER/droneranger_wind}"    # work dir; /scratch is purged monthly
export DR_REPO="${DR_REPO:-$HOME/DroneRanger_hardware}"         # this repository on Explorer
export DR_RESULTS="${DR_RESULTS:-$DR_REPO/runs}"                # job logs + results (git-ignored), out of /scratch

# GPU. Isaac Sim needs RT cores: on Explorer the only RTX GPUs open to students are in `sharing` (PI-shared,
# 60 min per job, 1 GPU). The public `gpu` partition has one T4 node (RT cores, below Isaac's spec).
# A100 / H200 / V100 are not supported by Isaac Sim.
export DR_PARTITION="${DR_PARTITION:-sharing}"
export DR_GRES="${DR_GRES:-gpu:l40s:1}"                         # or gpu:l40:1, gpu:a6000:1, gpu:a5000:1, gpu:1
export DR_TIME="${DR_TIME:-00:55:00}"                           # keep under the partition limit
export DR_MEM="${DR_MEM:-48G}"                                  # Isaac Sim minimum is 32 GB
export DR_CPUS="${DR_CPUS:-8}"

export ISAAC_IMAGE="docker://nvcr.io/nvidia/isaac-sim:5.1.0"     # public, no NGC key; Ubuntu 24.04 based
export PX4_IMAGE="docker://px4io/px4-dev-base-jammy:2024-05-18" # Ubuntu 22.04 toolchain for PX4 v1.14
export PX4_TAG="v1.14.3"
export PEGASUS_TAG="v5.1.0"
export PX4_MODEL="gazebo-classic_iris"                          # airframe 10015, what Pegasus 5.1 expects

# ------------------------------------------------------------------------------------------------ derived
export ISAAC_SIF="$DR_ROOT/images/isaac-sim_5.1.0.sif"
export PX4_SIF="$DR_ROOT/images/px4-dev-base-jammy_2024-05-18.sif"
export PX4_DIR="$DR_ROOT/PX4-Autopilot"
export PEGASUS_DIR="$DR_ROOT/PegasusSimulator"
export PYUSER="$DR_ROOT/pyuser"                 # `pip install --user` target for Isaac's Python
export ISAAC_CACHE="$DR_ROOT/isaac_cache"       # Kit/shader caches: keeps the second start fast
export APPTAINER_CACHEDIR="$DR_ROOT/apptainer_cache"
export APPTAINER_TMPDIR="$DR_ROOT/apptainer_tmp"
export SIM_DIR="$DR_REPO/wind/isaac_pegasus/sim"

# Write the proxy variables (set by `module load explorer`) and our own variables to an env file, so that
# --cleanenv keeps host Python/conda settings out of the containers but internet access still works.
write_env_file() {   # write_env_file <file> [KEY=VALUE ...]
    local f="$1"; shift
    : > "$f"
    for v in http_proxy https_proxy ftp_proxy no_proxy HTTP_PROXY HTTPS_PROXY FTP_PROXY NO_PROXY; do
        [ -n "${!v:-}" ] && printf '%s=%s\n' "$v" "${!v}" >> "$f"
    done
    for kv in "$@"; do printf '%s\n' "$kv" >> "$f"; done
}

# isaac_exec <env-file> <command...>: run inside the Isaac Sim image with the GPU and writable caches.
# The image is read-only; Kit writes to the bound cache directories instead (layout from the 5.1.0 container
# docs plus the kit/cache and kit/data binds used by Apptainer recipes).
isaac_exec() {
    local envf="$1"; shift
    local c="$ISAAC_CACHE"
    mkdir -p "$c"/{home,kit_cache,kit_data,kit_logs,cache,computecache,logs,config,ovdata,ovpkg}
    apptainer exec --nv --cleanenv --env-file "$envf" \
        --home "$c/home" \
        --bind "$DR_ROOT" --bind "$DR_REPO" \
        --bind "$c/kit_cache:/isaac-sim/kit/cache" \
        --bind "$c/kit_data:/isaac-sim/kit/data" \
        --bind "$c/kit_logs:/isaac-sim/kit/logs" \
        --bind "$c/cache:/isaac-sim/.cache" \
        --bind "$c/computecache:/isaac-sim/.nv/ComputeCache" \
        --bind "$c/logs:/isaac-sim/.nvidia-omniverse/logs" \
        --bind "$c/config:/isaac-sim/.nvidia-omniverse/config" \
        --bind "$c/ovdata:/isaac-sim/.local/share/ov/data" \
        --bind "$c/ovpkg:/isaac-sim/.local/share/ov/pkg" \
        "$ISAAC_SIF" "$@"
}

isaac_env_vars() {   # variables every Isaac run needs
    echo "ACCEPT_EULA=Y" "PRIVACY_CONSENT=Y" "PYTHONUSERBASE=$PYUSER" \
         "PYTHONPATH=$PEGASUS_DIR/extensions/pegasus.simulator" \
         "PEGASUS_EXT_DIR=$PEGASUS_DIR/extensions/pegasus.simulator"
}
