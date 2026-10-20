# Isaac Sim 5.1 + Pegasus 5.1 + PX4 SITL v1.14.3 on Explorer, with a wind publisher

This week's scope (2026-10-20): get the stack the other DroneRanger team uses running headless on Northeastern's
Explorer cluster, add a wind publisher, and smoke-test it with **dummy wind**.
- Real San Jose wind (the CSVs from `wind/tools/make_wind_profile.py`) is a later week. The publisher already
  reads that format (`--wind csv:<file>`).
- Real flights are out of scope.

**Status.**
- **Tested locally:** the wind publisher, the drag model and the pass/fail checker (7 offline tests, including a
  closed-loop point-mass run).
- **Not yet run on Explorer:** everything that needs Isaac Sim, PX4 or Explorer. Those scripts were written against
  the Pegasus v5.1.0 source and the Isaac Sim 5.1.0 / Explorer documentation listed under "Explorer notes".

## How it fits together

```
 Slurm job on one RTX GPU node (all processes share the node's network)
 ┌──────────────────────────── Isaac Sim 5.1 container (Apptainer, headless) ────────────────────────────┐
 │ smoke_wind.py                                                                                           │
 │   World (physics 250 Hz) + local ground plane + Pegasus Iris                                            │
 │   MultirotorConfig.drag = WindDrag(WindPublisher(profile))   ← the wind publisher, keyed to sim time    │
 │     F_body = -D · (v_body − Rᵀ·w_world(t))                     logs state, wind and force → sim_log.csv  │
 │   PX4MavlinkBackend (lockstep, TCP 4560+i, px4_autolaunch = False)                                      │
 └───────────────────────────────────────────────▲──────────────────────────────────────────────────────────┘
                                                 │ MAVLink HIL (sensors ↔ motor commands)
 ┌──── PX4 SITL v1.14.3 (px4-dev-base-jammy container, airframe gazebo-classic_iris, instance i) ────┐
 └──────────────────────────────────────▲──────────────────────────────────────────────────────────────┘
                                        │ MAVLink UDP 14540+i
 fly_hover.py (MAVSDK-Python): arm → take off 3 m → Hold until the profile ends → land
 check_smoke.py: PASS/FAIL from sim_log.csv
```

## Files

| Path | What |
|---|---|
| `sim/wind_publisher.py` | Wind profiles: `none`, `constant:E,N[,U]`, `smoke` (dummy schedule), `csv:<path>`. The clock starts when the drone first climbs above the trigger height |
| `sim/wind_drag.py` | `WindDrag`: Pegasus `Drag` subclass using air-relative velocity; identical to `LinearDrag` with zero wind; writes the ground-truth log |
| `sim/check_isaac.py` | Stage B: Isaac headless + Pegasus import + `WindDrag` on a parked Iris (no PX4) |
| `sim/smoke_wind.py` | Stage C sim: Isaac + Pegasus + PX4 backend + wind publisher |
| `sim/fly_hover.py` | Stage C flight script (MAVSDK) |
| `sim/check_smoke.py` | Stage C pass/fail checks |
| `tests/test_wind_pipeline.py` | Offline tests: drag math, triggering, CSV replay, closed-loop point-mass run through the checker |
| `explorer/env.sh` | Paths, images, partition and GPU settings, container helpers. **Edit the top block** |
| `explorer/01_setup.sh` | One-time setup: pull images, build PX4 v1.14.3, clone Pegasus v5.1.0, install Python packages |
| `explorer/check_node.sbatch` | Stage A (GPU, driver, graphics libraries) + stage B |
| `explorer/run_smoke.sbatch` | Stage C, the full smoke test |
| `explorer/submit.sh` | `bash submit.sh check` or `bash submit.sh smoke [wind-spec]` with the settings from `env.sh` |

## Running it on Explorer

```bash
# 0. on Explorer: get this repo into $HOME/DroneRanger_hardware (or set DR_REPO in env.sh)
# 1. one-time setup on a CPU node (about 20 GB in /scratch/$USER/droneranger_wind)
srun --partition=short --time=02:00:00 --cpus-per-task=8 --mem=32G --pty bash
bash ~/DroneRanger_hardware/wind/isaac_pegasus/explorer/01_setup.sh
exit
# 2. stage A+B on a GPU node; read the .out file in ~/droneranger_runs
bash ~/DroneRanger_hardware/wind/isaac_pegasus/explorer/submit.sh check
# 3. stage C, the smoke test with the dummy wind profile
bash ~/DroneRanger_hardware/wind/isaac_pegasus/explorer/submit.sh smoke
```

**Expected outputs:**
- Stage B prints `ISAAC_PEGASUS_OK`.
- Stage C ends with `SMOKE TEST PASSED` and copies the logs (including PX4 `.ulg` files) to `~/droneranger_runs/smoke_<jobid>/`.

The first Isaac start compiles shaders and can take 10 minutes or more. The caches in `isaac_cache/` make later
starts faster. That matters because `sharing` jobs are limited to 60 minutes.

### The dummy wind and what "pass" means

The schedule starts when the drone first passes 2.5 m on its way to a 3 m hover:

| Time after trigger | Wind (ENU, velocity of the air) |
|---|---|
| 0–15 s | calm (settle) |
| 15–35 s | 3 m/s toward +East (a wind from the west) |
| 35–50 s | calm (recover) |
| 50–80 s | 2 m/s toward +North ± 1.5 m/s sinusoid at 0.2 Hz |
| 80–90 s | calm, then land |

`check_smoke.py` requires all of the following:
- The wind clock started, the logged wind equals the profile, and the whole profile was simulated.
- In the step, the drag force points east (≈ 0.5 N/(m/s) × 3 m/s ≈ 1.5 N with Pegasus' default coefficients and the nose east).
- PX4 tilts the thrust axis west by more than 1°.
- The drone is pushed downwind at the step onset.
- It holds within 0.5 m during the step and recovers within 0.3 m afterwards.
- The force follows the gusts (correlation > 0.5).
- Nothing diverges: horizontal error < 2 m and altitude error < 1 m.

The offline point-mass stand-in gives 1.48 N, a 5.8° lean and a 0.37 m push. PX4 will differ, but should have the same signs.

## Design choices (change them if the other team prefers otherwise)

- **The wind publisher runs inside the simulation and is keyed to simulation time.** PX4 runs in lockstep, so a
  replay is deterministic, and nothing extra must run on Explorer.
  - A ROS 2 topic (for example `/drone/wind`, `geometry_msgs/Vector3Stamped`) can be added on top later if the other team wants to see or set the wind from ROS 2.
  - We would then have to decide whether ROS time or sim time drives the wind.
- **Air-relative linear drag** with Pegasus' own coefficients `[0.50, 0.30, 0.0]`. The literature favours drag
  computed from airspeed (`../Wind_Sim_Feasibility.md`, Section 6.3). The coefficients for our X500 are still to be identified.
- **Pegasus is used from `PYTHONPATH`.** Its `setup.py` patches `apps/isaacsim.exp.base.kit` inside the Isaac
  tree, which is read-only in a SIF. That patch only serves Pegasus' People module (`isaacsim.replicator.agent.core`),
  which we don't import. The scripts enable the two deprecated extensions Pegasus imports
  (`omni.isaac.core`, `omni.isaac.dynamic_control`).
- **PX4 runs in its own container** (`px4_autolaunch = False`) with a job-specific instance number. A shared
  8-GPU node may host another user's PX4, and PX4 hard-codes `/tmp` lock files and fixed base ports. Each job
  therefore gets a private `/tmp` and ports 4560+i / 14540+i.
- **A local ground plane, not an NVIDIA environment.** Pegasus' environments load from NVIDIA's asset server
  (S3). Compute nodes reach the internet only through the `explorer` module's proxy.
- **The PX4 origin is the NU Silicon Valley campus** (37.3377, −121.8898), ready for San Jose wind data.

## Explorer notes (verified 2026-10-20; copies in `reference/08_wind_simulation/docs/hpc_*.md`, `isaacsim51_*.md`)

- **GPUs.** Isaac Sim needs RT cores; A100, H100, H200 and V100 are not supported.
  - On Explorer the RTX GPUs (L40S, L40, A6000, A5000, Quadro RTX 6000) are all PI-owned.
  - Students can reach them only through the `sharing` partition: **60 minutes per job, 1 GPU, 2 running jobs**. Preemption is not documented.
  - The public `gpu` partition (8 h) has one T4 node. A T4 has RT cores but is below Isaac Sim's minimum (RTX 4080 class, 16 GB). NVIDIA's own 5.1.0 GCP guide still lists a T4 VM.
- **Driver.**
  - The Isaac Sim 5.1.0 image sets `MIN_DRIVER_VERSION=570.169`, and it was tested on 580.65.06.
  - Explorer does not publish its node driver versions. Stage A prints them.
  - The node also needs the graphics/Vulkan userspace libraries, not just a compute install.
- **Containers.**
  - Apptainer is on every node (no module). Isaac Sim 5.x cannot run natively on Rocky 9 (glibc 2.34; 5.x needs ≥ 2.35).
  - `nvcr.io/nvidia/isaac-sim:5.1.0` is public (no NGC key). Its base is Ubuntu 24.04 and its user is `isaac-sim`.
  - NVIDIA does not officially support Isaac Sim under Apptainer, but NVIDIA's Isaac Lab cluster guide and community recipes run it.
- **Storage.** `/scratch` holds 20 TB but is **purged on the first Tuesday of every month**, so results are copied to `$HOME` (75 GB). `/projects` needs a PI.
- **Other.**
  - Compute nodes reach the internet through the HTTP proxy that `module load explorer` sets.
  - IdleBot cancels jobs whose GPU is idle for an hour.
  - You cannot SSH into GPU nodes.

## Troubleshooting

- **`ISAAC_PEGASUS_FAILED` or a `ModuleNotFoundError: omni.kit.usd` / `omni.isaac.dynamic_control` error.**
  Search the Kit log (`isaac_cache/logs`, `isaac_cache/home/.nvidia-omniverse/logs`) for "Failed to resolve extension dependencies". The legacy README's "rc.19 standalone bug" is the 5.1.0 release itself; the usual cause is an extension that did not load.
- **`vkCreateInstance failed` or a segmentation fault at start.** The node lacks graphics/Vulkan driver libraries, or Apptainer is older than 1.4 (which binds the ICD and OptiX files). See stage A's output.
- **`Read-only file system` under `/isaac-sim/...`.** Add that path as another bind in `isaac_exec` (`env.sh`). Alternatively, pass `--portable-root <writable dir>` through `smoke_wind.py`; unknown arguments go to Kit.
- **PX4 never connects.** Check `px4.log` for "Waiting for simulator to accept connection on TCP port 4560+i", and check that `isaac.log` shows the vehicle being created.
- **MAVSDK cannot arm.** `--relax-link-failsafes` already sets `NAV_RCL_ACT=0` and `NAV_DLL_ACT=0`; read the `[px4]` status texts in `fly.log`.
- **The job hits 60 minutes.** Run `check` first so the shader cache is warm before `smoke`.

## Open questions for this week

1. **GPU access.** Is `sharing` (60-minute jobs) enough for now, or should we ask the PI (or the other team's PI) for their partition? A T4 job on `gpu` is the fallback test.
2. **Driver and graphics stack on the RTX nodes.** Stage A answers this. If the driver is below 570.169 or the graphics libraries are missing, a Research Computing ticket is needed.
3. **Does the other team already have an Isaac container or allocation on Explorer?** If so, reuse their image, partition and paths instead of `01_setup.sh`.
4. **Should the wind be visible on ROS 2** for the other team (see Design choices)?
