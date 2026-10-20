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

Only this repository is needed on Explorer. `01_setup.sh` fetches PX4 and Pegasus itself, and the git-ignored
`reference/` library stays on the laptop.

```bash
ssh <username>@login.explorer.northeastern.edu
# 0. get the repo (public, so no GitHub login needed); later updates: cd ~/DroneRanger_hardware && git pull
git clone https://github.com/usp787/DroneRanger_hardware.git ~/DroneRanger_hardware
S=~/DroneRanger_hardware/wind/isaac_pegasus/explorer
# 1. one-time setup as a CPU batch job (about 20 GB in /scratch/$USER/droneranger_wind, up to 2 h)
bash $S/submit.sh setup
squeue -u $USER                                   # wait until it has finished
tail -20 ~/DroneRanger_hardware/runs/dr-setup-*.out        # should end with "setup done"
# 2. stage A+B on an RTX GPU in `sharing`
bash $S/submit.sh check
tail -40 ~/DroneRanger_hardware/runs/dr-isaac-check-*.out  # look for the driver line and ISAAC_PEGASUS_OK
# 3. stage C, the smoke test with the dummy wind profile
bash $S/submit.sh smoke
tail -30 ~/DroneRanger_hardware/runs/dr-wind-smoke-*.out   # PASS/FAIL table; logs in ~/DroneRanger_hardware/runs/smoke_<jobid>/
```

If the L40S queue is long, pick another RTX type for one submission: `DR_GRES=gpu:a6000:1 bash $S/submit.sh check`. The
alternatives are `gpu:l40:1`, `gpu:a5000:1` and `gpu:rtx6000:1`. Do not use plain `gpu:1`: `sharing` also holds V100, A100,
H100, H200 and AMD MI50 cards, which cannot run Isaac Sim. To copy results to the laptop:
`scp -r <username>@login.explorer.northeastern.edu:~/DroneRanger_hardware/runs .`

**Expected outputs:**
- Stage B prints `ISAAC_PEGASUS_OK`.
- Stage C ends with `SMOKE TEST PASSED` and copies the logs (including PX4 `.ulg` files) to `~/DroneRanger_hardware/runs/smoke_<jobid>/`.

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

## Decisions for this week (2026-10-20)

- **GPU:** the smoke test runs in `sharing`. A failure, or a finding that more GPU hours are needed, is an
  acceptable outcome; GPU access for later work will be negotiated with the PI.
- **ROS 2:** this week uses our own MAVSDK + MAVLink pipeline, with no ROS 2. Working with the other team (shared
  container, a ROS 2 wind topic) is possible future work.
- **Still unknown until stage A runs:** the driver and graphics stack on the RTX nodes. If the driver is below
  570.169 or the graphics libraries are missing, a Research Computing ticket is needed.
