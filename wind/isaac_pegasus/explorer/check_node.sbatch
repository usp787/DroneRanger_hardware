#!/bin/bash -l
#SBATCH --job-name=dr-isaac-check
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --output=%x-%j.out
# Partition, GPU, time, memory and CPUs come from env.sh via submit.sh:  bash submit.sh check
#
# Stage A: can this GPU node run Isaac Sim 5.1 in Apptainer? (GPU model, driver, graphics/Vulkan libraries)
# Stage B: does Isaac Sim start headless, import Pegasus and apply WindDrag? (check_isaac.py, no PX4)
set -uo pipefail
source "${DR_REPO:-$HOME/DroneRanger_hardware}/wind/isaac_pegasus/explorer/env.sh"
module load explorer 2>/dev/null || true
RUN_DIR="$DR_ROOT/runs/check_${SLURM_JOB_ID:-manual}"
mkdir -p "$RUN_DIR"
echo "run dir: $RUN_DIR"

echo "== A1 GPU and driver on $(hostname)"
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv
DRV=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1)
ver_ge() { [ "$(printf '%s\n%s\n' "$2" "$1" | sort -V | head -1)" = "$2" ]; }
ver_ge "$DRV" 570.169 && echo "driver $DRV >= 570.169 (container minimum)" \
    || echo "WARNING: driver $DRV < 570.169, the image's MIN_DRIVER_VERSION"
ver_ge "$DRV" 580.65.06 || echo "note: Isaac Sim 5.1.0 was tested on 580.65.06"

echo "== A2 host graphics/Vulkan userspace (a compute-only driver install cannot render)"
for f in /usr/share/vulkan/icd.d/nvidia_icd.json /etc/vulkan/icd.d/nvidia_icd.json /usr/share/nvidia/nvoptix.bin; do
    [ -e "$f" ] && echo "found   $f" || echo "missing $f"
done
for lib in libGLX_nvidia.so.0 libnvidia-glvkspirv libnvidia-rtcore libnvoptix libnvidia-gpucomp; do
    ldconfig -p | grep -q "$lib" && echo "found   $lib" || echo "missing $lib"
done

echo "== A3 apptainer $(apptainer version); libraries --nv binds into the container"
ENVF="$RUN_DIR/isaac.env"
write_env_file "$ENVF" $(isaac_env_vars)
isaac_exec "$ENVF" bash -c 'nvidia-smi -L; ls /.singularity.d/libs | grep -E "GLX_nvidia|rtcore|glvkspirv|nvoptix|gpucomp" || echo "no graphics libs bound"; cat /etc/vulkan/icd.d/nvidia_icd.json 2>/dev/null | head -5'

echo "== B  Isaac Sim headless + Pegasus + WindDrag (first start compiles shaders: can take 10+ min)"
SECONDS=0
isaac_exec "$ENVF" /isaac-sim/python.sh "$SIM_DIR/check_isaac.py" --log "$RUN_DIR/check_isaac.csv" \
    > "$RUN_DIR/check_isaac.log" 2>&1
STATUS=$?
grep -E "check_isaac|ISAAC_PEGASUS|Error|error:|Traceback|ModuleNotFound|vkCreateInstance" "$RUN_DIR/check_isaac.log" | tail -40
echo "stage B exit $STATUS after ${SECONDS} s; full log: $RUN_DIR/check_isaac.log"
echo "Kit logs: $ISAAC_CACHE/logs and $ISAAC_CACHE/home (search for 'Failed to resolve extension dependencies')"
mkdir -p "$DR_RESULTS/check_${SLURM_JOB_ID:-manual}"
cp "$RUN_DIR"/check_isaac.{log,csv} "$DR_RESULTS/check_${SLURM_JOB_ID:-manual}/" 2>/dev/null || true
exit $STATUS
