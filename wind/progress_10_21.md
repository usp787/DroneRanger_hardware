# Sim + wind: progress as of 2026-10-21

DroneRanger hardware group, CS 7980 capstone, Northeastern University (Silicon Valley).
This note covers the sim + wind direction, which started on 2026-10-19.

## Summary

- **Feasibility (10/19).** The pipeline is practical: real San Jose wind → simulator → scripted PX4 flight → comparison.
  San Jose wind data, a wind model checked against measurements, and an end-to-end laptop demo all ran. There is
  also a verified literature review with 89 references.
- **Stack decision (10/20).** We use Isaac Sim 5.1 + Pegasus Simulator 5.1 + PX4 SITL v1.14.3 on Explorer HPC, the
  stack the other DroneRanger team uses. This week's scope is the pipeline plus a wind publisher, smoke-tested with
  dummy wind only.
- **Explorer pipeline (10/20–10/21).** Three of the four pieces now work on an L40S GPU in the `sharing` partition:
  - Isaac Sim runs headless in Apptainer.
  - Pegasus and the wind publisher apply the correct wind force.
  - PX4 SITL connects to the simulator in lockstep and reports "Ready for takeoff!".
- **What failed, and its fix.** The first smoke test did not fly because the scripted-flight library (MAVSDK-Python)
  shipped an incompatible v4 API. That is fixed in code (pinned to `mavsdk<4`). It now needs a setup re-run and a
  smoke re-run.

## 1. Results

### 1.1 Feasibility and literature (10/19)

Details: [Wind_Sim_Feasibility.md](Wind_Sim_Feasibility.md); references: [references.md](references.md) / [references.bib](references.bib).

- **Literature.** 89 references: 47 journal articles, all resolved through LibKey, plus 12 conference papers, 4 standards and reports, and others. They are grouped into 7 themes.
- **Gap.** No public project replays *measured* wind time series into PX4 SITL or Isaac/Pegasus. Our pipeline fills that gap.
- **What the literature implies for the simulator:**
  - Drag must be computed from *airspeed*, not ground speed.
  - Airport wind cannot simply be scaled down to a garden among houses, because the 3–10 m band lies inside the urban roughness sublayer.
  - A hovering multirotor can estimate the wind it feels to about 0.3–0.5 m/s, and PX4's EKF2 can already do this from drag.

### 1.2 San Jose wind data (SJC airport, ASOS 1-minute)

218,107 one-minute records: Jul 1 – Oct 18 2026, plus Nov–Dec 2025 as the seasonal match for O1/O2.

| Flight hours 08–16 | Jul–Oct 2026 | Nov–Dec 2025 |
|---|---|---|
| Median 2-min mean wind, morning / afternoon | 1.5 / 4.6 m/s | 1.5 / 3.1 m/s |
| 90th-percentile 5-s gust, morning / afternoon | 4.6 / 8.7 m/s | 6.2 / 7.2 m/s |
| Minutes with mean ≤ 5 m/s **and** gust ≤ 8 m/s, morning / afternoon | 97 % / 52 % | 89 % / 82 % |
| Highest gust in flight hours | 15.9 m/s | 18.0 m/s (storm day) |

- **Mornings are much calmer**, because of the afternoon NW sea breeze.
- **Local effects dominate in winter.** Nearby stations correlate only at r = 0.42–0.56.
- **Gridded reanalysis wind reads about 35 % below SJC**, so it needs bias correction before use.

### 1.3 Turbulence model check

The standard MIL-F-8785C Dryden turbulence was compared with SJC's measured gusts over 1,200 windows of 15 minutes each. Its intensity must be raised to match them:
- by **×1.48** in Nov–Dec;
- by **×1.72** in Jul–Oct.

So "textbook" turbulence is too gentle even at the open airport. A garden among houses is gustier still.

### 1.4 End-to-end laptop demo (RotorPy, no PX4)

This flew an X500-like drone around an 8 m square patrol loop while replaying real SJC wind:

| Mean replayed wind at 5 m | 0 | 1.1 m/s | 1.9 m/s | 3.9 m/s | 7.9 m/s |
|---|---|---|---|---|---|
| Tracking RMSE | 0.02 m | 0.03 m | 0.05 m | 0.11 m | 0.26 m |
| Max tilt | 3.9° | 4.3° | 5.1° | 8.3° | 16.0° |

### 1.5 Isaac + Pegasus + PX4 pipeline on Explorer

Code: [isaac_pegasus/](isaac_pegasus/). Job logs on Explorer: `~/DroneRanger_hardware/runs/`.

| Date | Job | Partition | Result | Elapsed |
|---|---|---|---|---|
| 10/20 | setup 11265968 | short | **Failed.** Both images pulled (Isaac Sim 7.6 GB, PX4 toolchain 0.7 GB), but the PX4 build stopped at the version-header step: the shallow NuttX submodule has no tag | 1 h 01 m |
| 10/20 | setup 11267760 | short | **Completed.** Local NuttX tag created, PX4 v1.14.3 built, Pegasus v5.1.0 cloned, Python packages installed (including mavsdk 4.0.6, the cause of the next failure) | 13 m |
| 10/21 | check 11287550 | sharing (L40S, node d4042) | **`ISAAC_PEGASUS_OK`.** Isaac starts headless in 65 s. 498 physics steps = 2.00 s at 250 Hz. Drag force 2.49 N for 5 m/s wind (2.5 N expected) | 9.5 m |
| 10/21 | smoke 11288256 | sharing (L40S) | **Partial.** PX4 SITL connected to Pegasus over TCP 4567 in lockstep: "home set", "Ready for takeoff!", 35 MB ULog. The flight script crashed at start (MAVSDK v4 API), so no take-off, no wind phase and an empty sim log | 8.5 m |

Offline tests (no Isaac): **8/8 pass**. They cover the drag math, the trigger and schedule, CSV replay, a closed-loop
point-mass run through the checker (1.48 N push, 5.8° lean, 0.37 m drift, as predicted), and the empty-log case.

## 2. Issues found

| Issue | Cause | Fix | Status |
|---|---|---|---|
| PX4 build fails (`IndexError`) | Shallow clone, so the NuttX submodule has no `nuttx-X.Y.Z` tag | Setup creates the highest upstream tag name locally | **Fixed and verified** (setup 11267760) |
| Job logs outside the repo | Results went to `~/droneranger_runs` | Moved to `~/DroneRanger_hardware/runs/` (git-ignored) | **Done** |
| "ROS2 Bridge startup failed" | Isaac loads its ROS 2 bridge by default, without ROS 2 libraries on the path | None needed: ROS 2 is not used this week | Non-blocking |
| NGX errors | DLSS is unavailable headless | None needed | Non-blocking |
| Driver 545.23.08 on the L40S node, below the image's minimum of 570.169 | Explorer's node driver | Headless physics works anyway | Watch: may matter for camera rendering |
| Flight script `TypeError` at `System()` | `pip install mavsdk` pulled v4.0.6, which has a new API | Pin `mavsdk<4` in setup | **Fixed in code, needs re-run** |
| `pandas.errors.EmptyDataError` in the checker | Consequence of the above: no flight, so the log was still in its write buffer | The log now flushes ~2× per sim second; the checker reports FAIL instead of crashing; the job stops Isaac as soon as the flight script fails | **Fixed in code, needs re-run** |

## 3. Next steps

1. **Re-run the smoke test.**
   - Commit and push, then `git pull` on Explorer.
   - Run `bash wind/isaac_pegasus/explorer/submit.sh setup`. This takes a few minutes, because images and PX4 are already in place and it only downgrades mavsdk. The log should print `mavsdk 3.x`.
   - Run `bash wind/isaac_pegasus/explorer/submit.sh smoke`.
2. **If the smoke test fails again,** read `fly.log` (arming or take-off messages from PX4) and `px4.log`. Likely next suspects:
   - PX4 arming checks without RC (`--relax-link-failsafes` already sets `NAV_RCL_ACT` / `NAV_DLL_ACT` to 0);
   - the speed of lockstep simulation compared with the 60-minute job limit.
3. **Once it passes, replay real San Jose wind.**
   - Generate profiles with `wind/tools/make_wind_profile.py`.
   - Copy them to Explorer and run `submit.sh smoke csv:<profile>`.
4. **Check PX4's own wind estimate.** Enable `EKF2_DRAG_CTRL` in SITL and compare the logged `wind` topic with the injected wind (sim-to-sim validation).
5. **Before 2026-11-03** (the first Tuesday, when `/scratch` is purged), save what's needed from `/scratch/zha.j/droneranger_wind` (26 GB), or plan to re-run setup afterwards.

## 4. Future directions

- **GPU access (PI negotiation).**
  - Students reach RTX GPUs on Explorer only through `sharing`: 60 minutes, 1 GPU.
  - Longer runs, more scenarios or camera rendering would need a PI-owned partition, and possibly a newer node driver (≥ 570).
- **Simulation fidelity.**
  - Replace Pegasus' Iris drag coefficients `[0.50, 0.30, 0.0]` with values identified for the X500.
  - Add measured-gust-scaled turbulence: ×1.5–1.7 at the airport, more in the garden.
  - Consider a spatial wind field around the house only if sim-vs-real cross-wind errors call for it.
- **Alignment with the other team.** Share the container, and expose the wind on a ROS 2 topic (set `ROS_DISTRO` and the bridge library path to enable Isaac's ROS 2 bridge).
- **Real flights (when the team can fly).**
  - Log a garden anemometer alongside SJC to calibrate the airport-to-garden factor.
  - Record PX4's EKF2 wind estimate.
  - Replay each flight's wind in SITL and compare error distributions (sim-to-real predictivity).

## 5. Where things are

| Item | Location |
|---|---|
| Feasibility report, references | `wind/Wind_Sim_Feasibility.md`, `wind/references.md`, `wind/references.bib` |
| Wind data tools and results | `wind/tools/`, `wind/data/`, `wind/figures/` |
| Explorer pipeline (code, scripts, README) | `wind/isaac_pegasus/` |
| Explorer job logs and results | `~/DroneRanger_hardware/runs/` on Explorer (git-ignored) |
| Images, PX4 build, Pegasus, caches | `/scratch/zha.j/droneranger_wind/` on Explorer (purged monthly) |
| Raw data, saved docs, open-access papers | `reference/08_wind_simulation/` (local only, see its `NOTES.md`) |
