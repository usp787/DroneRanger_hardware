#!/bin/bash -l
#SBATCH --job-name=dr-wind-smoke
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --output=%x-%j.out
# Partition, GPU, time, memory and CPUs come from env.sh via submit.sh:  bash submit.sh smoke [wind-spec]
#
# Stage C: Isaac Sim 5.1 + Pegasus 5.1 (smoke_wind.py) <-TCP 4560+i-> PX4 SITL v1.14.3 (own container)
#          <-UDP 14540+i-> MAVSDK script (fly_hover.py); then check_smoke.py on the ground-truth log.
# All three processes share the node's network (Apptainer default), so they talk over localhost.
set -uo pipefail
source "${DR_REPO:-$HOME/DroneRanger_hardware}/wind/isaac_pegasus/explorer/env.sh"
module load explorer 2>/dev/null || true
WIND="${1:-smoke}"
JOB="${SLURM_JOB_ID:-manual}"
RUN_DIR="$DR_ROOT/runs/smoke_$JOB"
INST=$(( 1 + ${SLURM_JOB_ID:-0} % 50 ))   # PX4 instance: unique ports and lock files on a shared node
mkdir -p "$RUN_DIR"/{px4_rootfs,tmp}
echo "run dir $RUN_DIR | wind $WIND | PX4 instance $INST (TCP $((4560 + INST)), UDP $((14540 + INST)))"
nvidia-smi --query-gpu=name,driver_version --format=csv,noheader

ENVF="$RUN_DIR/isaac.env"
write_env_file "$ENVF" $(isaac_env_vars)
LOCALF="$RUN_DIR/local.env"                     # flight script + checker: localhost only, no proxy
write_env_file --offline "$LOCALF" $(isaac_env_vars)
PIDS=()
cleanup() { for p in "${PIDS[@]}"; do kill "$p" 2>/dev/null; done; }
trap cleanup EXIT

echo "== 1/4 Isaac Sim + Pegasus (wind publisher: $WIND)"
isaac_exec "$ENVF" /isaac-sim/python.sh "$SIM_DIR/smoke_wind.py" \
    --px4-dir "$PX4_DIR" --instance "$INST" --px4-model "$PX4_MODEL" \
    --wind "$WIND" --log "$RUN_DIR/sim_log.csv" > "$RUN_DIR/isaac.log" 2>&1 &
ISAAC_PID=$!; PIDS+=("$ISAAC_PID")

echo "== 2/4 PX4 SITL $PX4_TAG (waits until Pegasus accepts the TCP connection)"
apptainer exec --cleanenv --bind "$DR_ROOT" --bind "$RUN_DIR/tmp:/tmp" \
    --env "PX4_SIM_MODEL=$PX4_MODEL" "$PX4_SIF" bash -c \
    "cd '$RUN_DIR/px4_rootfs' && '$PX4_DIR/build/px4_sitl_default/bin/px4' '$PX4_DIR/ROMFS/px4fmu_common' \
     -s '$PX4_DIR/ROMFS/px4fmu_common/init.d-posix/rcS' -i $INST -d" > "$RUN_DIR/px4.log" 2>&1 &
PIDS+=("$!")

echo "== 3/4 MAVSDK flight: arm, take off to 3 m, hold until the wind profile ends, land"
isaac_exec "$LOCALF" /isaac-sim/python.sh "$SIM_DIR/fly_hover.py" --url "udpin://0.0.0.0:$((14540 + INST))" \
    --done-file "$RUN_DIR/sim_log.csv.done" --log "$RUN_DIR/px4_telemetry.csv" --relax-link-failsafes \
    > "$RUN_DIR/fly.log" 2>&1
FLY=$?
echo "fly_hover exit $FLY"; tail -15 "$RUN_DIR/fly.log"

if [ "$FLY" -ne 0 ]; then
    echo "flight script failed: stopping the sim now (it would wait for a take-off that never comes)"
    kill -INT "$ISAAC_PID" 2>/dev/null; sleep 20
else
    for _ in $(seq 1 60); do kill -0 "$ISAAC_PID" 2>/dev/null || break; sleep 5; done   # let the sim exit
fi
grep "smoke_wind" "$RUN_DIR/isaac.log" | tail -10

echo "== 4/4 checks"
isaac_exec "$LOCALF" /isaac-sim/python.sh "$SIM_DIR/check_smoke.py" "$RUN_DIR/sim_log.csv"
CHECK=$?

OUT="$DR_RESULTS/smoke_$JOB"
mkdir -p "$OUT"
cp "$RUN_DIR"/{sim_log.csv,sim_log.csv.done,sim_log.csv.summary.json,px4_telemetry.csv,fly.log,isaac.log,px4.log} \
    "$OUT/" 2>/dev/null
cp -r "$RUN_DIR/px4_rootfs/log" "$OUT/px4_ulog" 2>/dev/null
echo "results copied to $OUT (the PX4 .ulg files are in px4_ulog/)"
exit $CHECK
