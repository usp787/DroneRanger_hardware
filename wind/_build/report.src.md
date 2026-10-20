# Simulation + wind for DroneRanger: is the pipeline practical?

*Feasibility check and literature review. Hardware group, CS 7980 capstone, Northeastern University (Silicon Valley). Prepared 2026-10-19. Every number below comes from data pulled on that day or from a source in the reference list; numbers that are my own estimates say so.*

## Summary

**Question.** Can we fly a scripted PX4 mission in a simulator (Isaac Sim, as in last semester's legacy repo, or another one) while replaying *real* San Jose wind, so that the sim tells us something useful about real outdoor flights?

**Verdict: yes, it is practical, and most of it already runs.** Every stage was either run on a laptop today or checked against the source code of the tools involved:

| Stage | What | Status (2026-10-19) |
|---|---|---|
| 1. Wind data | NOAA ASOS 1-minute wind at San Jose airport (SJC), free via the Iowa Environmental Mesonet | **Run.** 218,107 one-minute records pulled (Jul 1 – Oct 18 2026, plus Nov–Dec 2025 as the seasonal match for O1/O2) |
| 2. Wind model | Move airport wind (10 m, open terrain) to garden height and roughness, then add Dryden turbulence | **Run and checked** against 1,200 measured 15-minute windows |
| 3. Inject into a simulator | Isaac Sim + Pegasus, Gazebo (gz) + PX4 SITL, PX4 SIH or RotorPy | **Verified in source code** for all four; **run** in RotorPy |
| 4. Scripted flight | MAVSDK-Python or ROS 2 offboard (both used last semester), or PX4 Mission mode | Legacy code exists; **run** with RotorPy's own controller |
| 5. Compare with reality | PX4 log: tracking error, tilt, EKF2 wind estimate vs. measured wind | Planned; every PX4 topic and parameter it needs was confirmed |

What this means for the plan:
- **Last semester's script-controlled flight** used **MAVSDK-Python** first, then **ROS 2 offboard over uXRCE-DDS** (`px4_msgs`). The separate Isaac repo runs **Isaac Sim 5.1 + Pegasus Simulator 5.1 + PX4 SITL v1.14.3** [@yin2026; @ripzou2026isaac; @jacinto2024].
- **No simulator replays measured wind out of the box.** Each one needs a small adapter. In Pegasus it is a ~30-line custom drag class. In Gazebo it is a wind-message publisher plus one plugin line. RotorPy needed 10 lines, written and run today.
- **The recommended first platform is Gazebo (gz) + PX4 SITL.** It is what the hardware plan already uses for O0 rehearsal, it runs on the laptop, and it flies the same PX4 Mission mode used for O2. **Isaac Sim + Pegasus** is the second step, worth it when the camera matters too, but it needs a ≥ 16 GB RTX GPU (Explorer HPC or cloud). The laptop's RTX 4060 has 8 GB.
- **San Jose wind is strongly diurnal, and that is the main operational finding.** In Jul–Oct 2026, mornings (08–11) had a median 2-minute mean of 1.5 m/s. Afternoons (13–16) had 4.6 m/s, with 90th-percentile 5-second gusts of 8.7 m/s. In Nov–Dec 2025 the contrast was weaker, but storm days reached 11 m/s mean and 18 m/s gusts.
- **Standard turbulence models are too gentle for San Jose.** The MIL-F-8785C Dryden model needed its intensity raised by about ×1.5 (winter) to ×1.7 (summer–fall) to match measured SJC gustiness, even at the open airport. A garden among houses is gustier still.
- **The airport is not the garden.** Winter correlations between nearby stations were only r = 0.42–0.56. Gridded reanalysis read about 35 % lower than SJC. A cheap logging anemometer at the garden is needed to calibrate the transfer.

## 1. The legacy stack: what "script-controlled flight" meant last semester

| Period (Spring 2026) | Flight-control path | Simulator | Evidence |
|---|---|---|---|
| Weeks 2–8 | **MAVSDK-Python** offboard (`mavsdk.offboard`, `VelocityNedYaw`) on the Raspberry Pi over MAVLink | — | weekly reports, weeks 2 and 6 |
| Weeks 9–16 | **ROS 2 offboard** via **uXRCE-DDS** (`px4_msgs`: `OffboardControlMode`, `TrajectorySetpoint`, `VehicleCommand`) on the Jetson; flown outdoors in weeks 15–16 | Gazebo / Unity (legacy `DroneRanger` repo) | [@ling2026; @yin2026] |
| March 2026 (separate repo) | PX4 shell (`commander takeoff`); no autonomy code yet | **Isaac Sim 5.1 + Pegasus 5.1 + PX4 SITL v1.14.3** (MAVLink HIL on TCP 4560), ROS 2 Jazzy camera topics | [@ripzou2026isaac; @jacinto2024] |

Any of the three can script a flight in simulation. For O2, the most realistic choice is **PX4 Mission mode**, uploaded from the same QGroundControl plan that will be flown in the garden. MAVSDK or ROS 2 then only arm the drone, upload the plan and log. The sim then exercises the exact PX4 code path used outdoors.

## 2. Wind data for San Jose

**What exists.** San Jose's open-data portal has no wind datasets (a catalogue search for "wind" returned 0 results). The usable public sources are:

| Source | What | Resolution | Access | Used here |
|---|---|---|---|---|
| NOAA ASOS 1-minute (NCEI TD-6405) via the Iowa Environmental Mesonet [@iem1min; @ncei6405; @asos1998] | 2-minute average wind and the peak 5-second gust, every minute (hourly METAR omits most gusts) | 1 min, 1 kt | free CSV API; archive was current to 2026-10-18 | **yes, SJC (3.9 km from campus)** |
| ASOS/AWOS hourly METAR via IEM [@iemasos] | hourly mean wind, direction and gust (plus specials) | ~1 h, 1 kt | free CSV API | yes, for SJC, Reid-Hillview (RHV, 6.2 km), Moffett (NUQ), Palo Alto (PAO) |
| Open-Meteo historical API [@openmeteo] | gridded reanalysis/analysis wind and gusts at any point | hourly, 9–25 km grid | free, no key | yes, at the campus |
| CIMIS agricultural stations [@cimis] | hourly wind at 2 m (close to flight height) | hourly | free key | **no.** The San Jose station (#69) closed in 2002; the nearest active ones are 25–40 km away |
| Logging anemometer at the garden | the wind the drone actually meets | 1 s | buy (~tens of dollars) | **recommended** |

The download is scripted: `python wind/tools/fetch_wind.py --start 2026-07-01 --end 2026-10-18`. Raw CSVs go to the git-ignored `reference/08_wind_simulation/data/`.

**What the last few months looked like** (SJC, 10 m anemometer, flight hours 08–16 local; full tables in [data/sj_wind_summary.md](data/sj_wind_summary.md)):

![SJC wind by hour of day](figures/sjc_diurnal.png)

| SJC 1-minute data | Jul 1 – Oct 18, 2026 | Nov 1 – Dec 31, 2025 |
|---|---|---|
| Coverage | 87 % of minutes | 92 % of minutes |
| Median 2-min mean wind, morning 08–11 / afternoon 13–16 | 1.5 / 4.6 m/s | 1.5 / 3.1 m/s |
| 90th-percentile 5-s gust, morning / afternoon | 4.6 / 8.7 m/s | 6.2 / 7.2 m/s |
| Share of minutes with mean ≤ 5 m/s, morning / afternoon | 97 % / 52 % | 89 % / 82 % |
| Share of minutes with gust ≤ 8 m/s, morning / afternoon | 99 % / 81 % | 95 % / 94 % |
| Highest 5-s gust in flight hours | 15.9 m/s | 18.0 m/s (morning of a storm day) |
| Gust factor (5-s gust ÷ 2-min mean), median | 1.36 | 1.29 |
| Afternoon direction (mean ≥ 2 m/s) | NW 83 % | NW 55 % |

Two points matter for flight planning:
- In late summer and fall the afternoon northwest sea breeze dominates, so **morning slots are much calmer**. This confirms the earlier daily-data finding in `reference/07_california_silicon_valley/NOTES.md`.
- In November–December the average day is calmer but **storm days are windier**. The windiest 15-minute flight-hour window was 11.0 m/s mean with 16.5 m/s gusts (2025-11-13, 09:15). A go/no-go check on the day matters more than the season.

**How well does one station represent another place?** All comparisons below are hourly, during flight hours:

| SJC vs. | Jul–Oct 2026: r, speed ratio | Nov–Dec 2025: r, speed ratio |
|---|---|---|
| Reid-Hillview (RHV, 6 km, east San Jose) | 0.81, 0.82 | 0.56, 0.70 |
| Moffett (NUQ, 16 km) | 0.77, 1.20 | 0.42, 0.93 |
| Palo Alto (PAO, 24 km) | 0.76, 1.27 | 0.46, 1.05 |
| Open-Meteo grid point at the campus | 0.77, 0.63 | 0.49, 0.65 |

In the sea-breeze season the region moves together (r ≈ 0.8). In light winter winds, local effects dominate (r ≈ 0.4–0.6). The gridded model reads about a third lower than SJC, so model data can stand in for a station only after bias correction.

## 3. From airport wind to garden wind

`wind/tools/make_wind_profile.py` turns a chosen historical window into a time series the simulator replays (50 Hz, ENU, m/s):

1. **Mean wind.** It takes the SJC 1-minute vector series and interpolates it, so minute-scale lulls and gusts happen at their real times.
2. **Height and roughness transfer.** A log-law profile carries the airport wind (10 m, roughness length z₀ = 0.03 m) up to a 60 m blending height and back down over the rougher garden. This is the standard roughness-dependent method [@wieringa1986]. For 5 m altitude and a suburban z₀ = 0.5 m, the factor is **0.63**.
   - This is only a first-order estimate. Among houses, 3–10 m lies inside the roughness sublayer, where the log law is unreliable [@roth2000].
   - One measured garden/SJC ratio replaces it (`--height-factor`). The ratio can come from an on-site anemometer or from the drone's own wind estimate (Section 6.4).
3. **Turbulence.** Dryden spectra in the MIL-F-8785C low-altitude form [@milf8785c; @abichandani2020], scaled from the wind at 20 ft. Eddies are advected past the hovering drone at the mean wind speed, following Taylor's frozen-turbulence hypothesis [@taylor1938]. `--turb data` rescales the intensity so the synthetic per-minute 5-s gust factor matches the measured one in that window.

**Check against measurement.** `wind/tools/validate_turbulence.py` compares like with like: it simulates the anemometer itself (10 m, open terrain) for 1,200 random 15-minute flight-hour windows with mean ≥ 2 m/s, and compares the synthetic and measured gust factors:

| Period | Measured gust factor (median) | MIL-F-8785C synthetic | Turbulence scale needed: median (IQR) |
|---|---|---|---|
| Nov–Dec 2025 (600 windows) | 1.31 | 1.21 | **×1.48** (1.19–1.83) |
| Jul–Oct 2026 (600 windows) | 1.38 | 1.22 | **×1.72** (1.37–2.14) |
| by mean wind: 2–4 / 4–6 / ≥ 6 m/s | 1.38 / 1.31 / 1.29 | 1.20 / 1.22 / 1.22 | ×1.82 / ×1.40 / ×1.27 |

So textbook "light turbulence" understates San Jose gustiness even at the airport. Part of the excess in light wind comes from the 1-kt reporting resolution: 4 kt gusting 5 kt already reads as a gust factor of 1.25. A garden among houses at 5 m will be gustier than the airport. Neutral surface-layer scaling suggests turbulence intensity about 2.5 times higher (my estimate, from σᵤ ∝ 1/ln(z/z₀); the tool reports it as `surface_layer_TI_estimate`). In practice, sweep `--ti-scale` over 1.5–3 until on-site measurements narrow it.

## 4. Injecting wind into the simulators

All of the following was verified in source code at named tags (details and saved files in `reference/08_wind_simulation/NOTES.md`).

| Simulator | Built-in wind | How to replay a measured time series | PX4 | Runs on our laptop? |
|---|---|---|---|---|
| **Isaac Sim 5.1 + Pegasus 5.1** [@jacinto2024; @pegasussrc] | **None.** `LinearDrag` uses ground-relative body velocity. The PX4 backend's airspeed line says `# TODO - add wind here` | Subclass `Drag` with v_air = v − w(t) (~30 lines), set `MultirotorConfig.drag`. Or apply a force in a physics callback, as in the open Pegasus issue on wind [@pegasus132]. Standalone scripts with lockstep PX4 make replay deterministic | pinned to **v1.14.3** | **No** (needs RTX ≥ 16 GB); Explorer HPC L40/L40S/A6000 or cloud |
| **Gazebo (gz Harmonic) + PX4 SITL** [@px4gz; @gzwindeffects] | `windy` world (5, 2, 0 m/s) [@px4windy]. In PX4 v1.17 wind reaches the stock x500 only through **rotor drag** in the motor model [@gzmotormodel] (my estimate: ~1.3 N, a ~4° lean, at 5.4 m/s). PX4 `main` loads the WindEffects system since July 2026 [@px4pr28042] | Publish `gz.msgs.Wind` on `/world/<world>/wind` at ≤ physics rate. Add `<enable_wind>` on the x500 base link (an open PR does this [@px4pr130]) and set `time_for_rise` ≈ physics step. Better still, compute drag ourselves and apply it on `/world/<world>/wrench/persistent` (ApplyLinkWrench, already loaded in v1.17). WindEffects' force law is mass × gain × (v_wind − v_link): about 2 N per m/s on the x500 at default gain, so it needs calibrating | v1.17 stable; **same model family as our X500** | **Yes** (Linux, WSL2 or Docker) |
| **PX4 SIH** [@px4sihmain] | `SIH_WIND_N/E` parameters, changeable in flight; first-order drag (`SIH_KDV`); no vertical wind | Stream `PARAM_SET` from MAVSDK, or a small C++ patch to read a series | **main / v1.18-rc1 only**; not in v1.17.0 | Yes, headless and fastest |
| **RotorPy** [@folk2023rotorpy; @rotorpysrc] | Constant, sinusoid, Dryden, spatial "wind tunnel"; **air-relative** parasitic and rotor drag | `update(t, position)` class reading our CSV (**done**, 10 lines) | Optional HIL bridge (TCP 4560), but it sends no HIL_GPS, so Mission mode is unverified | **Yes**, pure Python |
| OmniDrones / Aerial Gym [@xu2024omnidrones; @kulkarni2025] | Random sinusoidal force (OmniDrones Track task) / random disturbance (Aerial Gym); not air-relative | Possible, but they are RL training environments | no | No (Isaac) |
| AirSim [@shah2018] | `simSetWind` (NED) | — | yes | archive announced; not recommended |

Two older options were rejected:
- **Gazebo Classic** has a mean + noise + one-gust wind plugin with no file input [@gzclassicwind], derived from RotorS [@furrer2016]. Gazebo Classic reached end of life on 2025-01-31 [@gzclassiceol].
- The only open tool found that loads measured wind into PX4 SITL is a Gazebo Classic plugin for a **static** CFD wind field [@wind3d]. **No public project replays measured wind time series into PX4 SITL or Isaac/Pegasus.** That gap makes this a reasonable small research contribution.

**Comparing sim with reality needs only standard PX4 features:**
- EKF2 can estimate wind on a multirotor from drag (`EKF2_DRAG_CTRL`, tuned with `EKF2_BCOEF_X/Y` and `EKF2_MCOEF`) and logs it in the `wind` topic [@px4ekf2]. That gives a sim-to-sim check (estimated vs. injected) and a real-flight wind record to replay afterwards.
- Wind failsafes exist: `COM_WIND_WARN` (v1.13+), `COM_WIND_MAX` (v1.14+) and `COM_WIND_MAX_ACT` (v1.15+). All are disabled by default [@px4commander]. The Pegasus stack's v1.14.3 has no `COM_WIND_MAX_ACT` and no `/fmu/out/wind` over DDS, although the wind estimate is still in the log.

## 5. End-to-end check on a laptop

To show that stages 1–4 connect, `wind/tools/rotorpy_wind_demo.py` flies an X500-like quadrotor in RotorPy. It flies three loops of an 8 m × 8 m garden square at 5 m altitude and 1 m/s, while replaying four real SJC windows produced by `make_wind_profile.py` (`--turb data`, or MIL × 1.5 when the window was too calm to calibrate).

The model uses the mass, inertia, motor constant and rotor-drag coefficient from PX4's own Gazebo x500. Mass is raised to 2.1 kg for the Jetson payload, and body drag is assumed. The controller is RotorPy's SE(3) controller with perfect state feedback, **not PX4**, so treat the numbers as a pipeline check, not an X500 prediction.

![RotorPy patrol loop under replayed SJC wind](figures/rotorpy_demo.png)

| Replayed window (SJC 10 m mean) | Wind at 5 m, mean / max | Tracking RMSE | Max error | Max tilt |
|---|---|---|---|---|
| no wind | 0 | 0.02 m | 0.04 m | 3.9° |
| 2025-11-30 09:15, median morning (1.5 m/s) | 1.1 / 1.5 m/s | 0.03 m | 0.06 m | 4.3° |
| 2025-12-05 13:15, median afternoon (2.9 m/s) | 1.9 / 3.2 m/s | 0.05 m | 0.11 m | 5.1° |
| 2025-11-07 15:30, 90th-percentile afternoon (5.6 m/s) | 3.9 / 5.1 m/s | 0.11 m | 0.19 m | 8.3° |
| 2025-11-13 09:15, windiest morning (11.0 m/s) | 7.9 / 11.1 m/s | 0.26 m | 0.37 m | 16.0° |

The chain works: error and tilt grow with the replayed wind, and no rotor saturated. A full 98-second flight took about one minute of CPU time. In PX4 the steady part of the error will be smaller, because the velocity loop has an integrator and SE(3) here does not. Gusts will still show.

Real flights will add something no simulator here models well: **estimation error** (GNSS without RTK, and barometer error from dynamic pressure in wind). That is why the comparison against real logs in stage 5 matters.

## 6. What the literature says about wind and small multirotors

The search covered seven themes. It added 51 peer-reviewed or primary sources to those already in the sim2real list, each verified as described in [references.md](references.md). The short version is below; the per-paper notes are in the reference list.

### 6.1 Wind and turbulence models

**The standard tool.** The workhorse is the Dryden/von Kármán spectral model in its military low-altitude form, valid from 10 ft to 1,000 ft [@milf8785c; @milhdbk1797]:
- Vertical gust intensity is 0.1 × the mean wind at 20 ft.
- Horizontal intensity and scale length grow with height through (0.177 + 0.000823h).
- The mean wind follows a log profile [@abichandani2020; @stull1988].

At 3–10 m this gives horizontal gusts of about 0.2 × the 20-ft wind, with scale lengths of roughly 20–70 m. Gust time series are made by shaping white noise with discrete filters [@beal1993]. A multirotor-specific review also provides Python Dryden code [@abichandani2020].

**Two limits matter here:**
- These models assume homogeneous, Gaussian turbulence at a single point.
- Measurements 4 m above ground show that small vehicles feel strong roll inputs from vertical gusts that vary across their own span, which a single uniform wind vector under-represents [@watkins2006].

Our own check (Section 3) adds a third limit: at San Jose airport the MIL intensity is about 1.5–1.7 times too low.

### 6.2 Low-altitude wind among houses and trees: why the airport is not the garden

**Built-up areas break the standard profile.** Over cities, a *roughness sublayer* reaches about 2.5–3 times the building height. Inside it, log-law scaling is unreliable [@roth2000]. With one- and two-storey houses, the whole 3–10 m patrol band lies inside that layer. Within and just above tree canopies, flow is dominated by large coherent sweeps and behaves like a mixing layer [@finnigan2000]. The roughness length and displacement height needed for any height correction can be estimated from building and tree geometry [@grimmond1999] and terrain type [@wieringa1993; @wieringa1986].

**Building effects are sharp and local:**
- Along a large-eddy-simulated flight path over a suburban building, in a 3 m/s reference wind, crossing the roof shear layer at 5 m/s changed the relative flow angle by about 20° and airspeed by about 50 % within 0.25 s [@mohamed2023].
- In an 8 kt wind, building wakes caused attitude excursions of up to 10° on a small unmanned helicopter [@galway2011].
- Urban wind is named as a key inhibitor of urban drone use [@watkins2020].

**The workable designs** treat the station wind as the *above-roof boundary condition* of a local flow model:
- CFD driven by the prevailing wind [@ware2016];
- a precomputed large-eddy-simulation database per site [@giersch2022];
- a learned local flow field from onboard range data [@folk2024];
- a station-to-CFD transfer that matched station records within 12 % in speed and 8 % in bearing [@gianfelice2022].

### 6.3 How multirotors respond to wind

**Drag depends on airspeed, not ground speed.** Rotor drag from blade flapping and induced drag is roughly linear in *air-relative* velocity [@mahony2012; @hoffmann2007]. A simulator must therefore compute drag from v − w, which RotorPy does and Pegasus's `LinearDrag` does not. Drag-aware feed-forward halves tracking error [@faessler2018]. A blade-element model with a learned residual is the next step up in fidelity [@bauersfeld2021].

**Measured magnitudes:**
- In NASA wind-tunnel tests of five commercial multicopters at about 6–24 m/s, a 1.5 kg 3DR Solo had about 0.8 lb (3.6 N) of mean drag at about 12 m/s [@russell2016].
- A wind-tunnel-based model predicted the station-keeping error spread within 7 % *along* the wind but only within 56 % *across* it [@bannwarth2019]. Simple sims get the mean response right and the cross-wind turbulence response poorly. That is a metric worth reporting in our sim-vs-real comparison.
- Power depends on airspeed, so holding position into a headwind costs endurance. A validated range/endurance model quantifies this [@bauersfeld2022].
- A public dataset of 209 outdoor quadrotor flights with an onboard anemometer can test drag and power models before we have X500 logs [@rodrigues2021].
- Ground effect matters only near take-off and landing, and must be separated from wind in low-altitude logs [@sanchezcuevas2017].

### 6.4 The drone as its own anemometer

A hovering multirotor's tilt and drag reveal the wind it feels. The inertial-only idea [@neumann2015] has since been validated against reference anemometers:

| Study | Speed error | Direction error | Setting |
|---|---|---|---|
| Palomaki et al. [@palomaki2017] | < 0.5 m/s | < 30° | 10 m, beside sonic anemometers |
| Simma et al. [@simma2020] | 0.26–0.29 m/s RMSE | 4–5° | autopilot logs only, 0–5 m/s wind |
| Wetz et al. [@wetz2021] | < 0.3 m/s RMS | < 8° | 76 flights against a 99 m tower |
| Crowe et al. [@crowe2020] | 0.61 m/s RMSE (LSTM) | — | learned from attitude data |

Other approaches:
- Richer motion models raise the estimation bandwidth [@gonzalezrocha2019].
- Telemetry-only drag calibration plus a Kalman filter runs onboard [@hattenberger2022].
- Propeller power and speed (ESC data) can separate aerodynamic from contact forces [@tomic2020].

**What this means for DroneRanger.** PX4 already implements drag fusion in EKF2 [@px4ekf2]. X500 hover segments in the garden should therefore give the wind the drone actually felt, to about 0.3–0.5 m/s. That gives the garden-to-SJC ratio needed in Section 3 without extra hardware. An anemometer remains the independent check. The statistics for comparing SITL and real PX4 logs are worked out in a recent PX4 testbed study [@kose2026].

### 6.5 Controllers that cope with wind

**Robust inner loops reject wind without an exact wind model:**
- Incremental nonlinear dynamic inversion (INDI) [@smeur2016] beat PID when flying in and out of a 10 m/s wind-tunnel jet [@smeur2018].
- INDI with flatness feed-forward tracked at up to 12.9 m/s with 6.6 cm RMS error and no aerodynamic model [@tal2021].
- Adding INDI and drag modelling cut tracking error by more than 78 % for both NMPC and flatness-based control [@sun2022].
- L1-adaptive NMPC cut error by more than 90 % under fan wind and unknown payloads [@hanover2022].
- An L1-augmented geometric controller is a natural adaptive baseline [@wu2025l1quad].
- Measured onboard wind can be fed straight into geometric control [@craig2020].

**Learning-based results:**
- Neural-Fly learned a wind representation and flew in a fan-array tunnel at up to 12.1 m/s [@oconnell2022], building on learned-residual aerodynamics [@shi2019].
- Meta-learning adaptive features in closed-loop simulation shows how a wind-randomised simulator can *train* adaptation [@richards2023].
- RL policies trained with random force disturbances transfer to real fan wind:
  - DATT: 34 % less error than adaptive NMPC [@huang2023datt];
  - the domain-randomised low-level policies of Molchanov et al. [@molchanov2019];
  - an extreme-adaptation controller [@zhang2025extreme];
  - a recent DRL-INDI preprint: 94.6 % vs 36.0 % success in ≤ 3.5 m/s gusts [@habel2026gustpilot].

**What this means for us.** Nearly all of this testing uses fans or wind tunnels at ≤ 12 m/s, not real atmospheric turbulence. To test robustness, a correct mean force plus plausible random disturbances is enough. The measured-wind replay is what lets us predict *a specific* outdoor flight. That makes it the new part of this work.

### 6.6 Wind in simulators: what others built

**Off-the-shelf support is basic** (Section 4 and [@dimmig2025]). RotorPy has the most complete built-in wind: Dryden, sinusoid and spatial profiles, with air-relative aerodynamics [@folk2023rotorpy].

**Closest existing work:**
- The nearest pipeline to ours is OpenStreetMap buildings → OpenFOAM CFD → a Gazebo plugin → PX4 SITL. It uses a *steady* CFD field, not measured time series [@kakavitsas2024].
- A Gazebo weather-plugin case study measured wind effects on a PX4 UAV with synthetic wind [@imamov2024].
- A CNN trained on CFD predicts 3D wind from sparse measurements. It works best well above the ground (> 50 m), unlike our band [@achermann2024].

**Validating against controllable wind** can use fan arrays:
- Caltech's Real Weather Wind Tunnel, used by Neural-Fly [@oconnell2022];
- an open-source low-cost multi-fan system giving 0.5–3.4 m/s steady wind and 0.125–0.5 Hz gusts, for small vehicles only [@olejnik2022].

### 6.7 Wind as an operational limit

- **Data semantics matter.** An hourly METAR wind is a 2-minute average at report time. A METAR gust is reported only when the peak exceeds the 10-minute lull by ≥ 10 kt, so most light-wind hours carry no gust. The 1-minute archive used here gives the peak 5-s gust of every minute [@asos1998].
- **Flyability.** Using hourly reanalysis wind at 100 m against manufacturer limits (median 10 m/s for common drones), global median flyability is 5.7 h/day, or 2.0 h/day in daylight [@gao2021]. Their 100 m wind overstates 3–10 m wind. Section 2 applies the same idea to SJC 1-minute data.
- **Go/no-go needs fine-scale data.** A weather-risk model for small drones argues that forecasts finer than 1 km are needed [@roseman2020]. An airport value is a starting point, not a backyard decision.
- **For DroneRanger** (my inference from the above, not a published limit): the physical envelope of a ~2 kg quadrotor is roughly 8–10 m/s mean wind. The first O1/O2 flights should keep a much lower operating limit, for example SJC mean ≤ 5 m/s and gust ≤ 8 m/s. Both limits together were met in 89 % (Nov–Dec 2025) and 97 % (Jul–Oct 2026) of morning minutes, but in only 52 % of Jul–Oct afternoon minutes. The SITL runs in Section 7 should refine it.

### 6.8 How much wind fidelity does the simulator need?

| Level | What is replayed | Good for | Evidence |
|---|---|---|---|
| 0 | Measured mean wind (1-min SJC × height factor) | along-wind offset, tilt, battery cost, failsafe logic | [@bannwarth2019; @bauersfeld2022] |
| 1 | + Dryden turbulence, intensity calibrated to measured gusts, drag from airspeed | gust response, controller robustness | Section 3; [@milf8785c; @faessler2018; @huang2023datt] |
| 2 | + spatial field around the house (CFD/LES/learned) | cross-wind errors and wakes near buildings and trees | [@mohamed2023; @kakavitsas2024; @giersch2022] |
| 3 | The wind EKF2 estimated in the real flight, replayed in SITL | like-for-like sim-vs-real comparison | [@wetz2021; @simma2020; @px4ekf2] |

Levels 0–1 are what this report builds. Level 3 comes free once real flights log `EKF2_DRAG_CTRL` wind. Level 2 is worth doing only if the cross-wind errors between sim and real demand it.

## 7. Recommended plan (fits the hardware scope and the O1/O2 dates)

This is an extension of the planned **O0 SITL rehearsal** and of the **weather gate**, not new algorithm work. It stays inside the hardware group's scope.

| When | Step | Output |
|---|---|---|
| Week of 10/19 | Bring up PX4 SITL + gz x500 (Docker or a Linux machine). Add a ~50-line gz-transport node that replays `make_wind_profile.py` CSVs. Calibrate the wind force against RotorPy's air-relative drag. Enable `EKF2_DRAG_CTRL` in SITL and check that the estimated wind converges to the injected wind | wind-replay node + SITL config in the repo |
| Week of 10/26 | Fly the **O2 Mission plan** in SITL under the four SJC scenarios, plus a `--ti-scale` sweep of 1.5–3. Record tracking error, tilt, battery draw and failsafe behaviour. Propose a go/no-go wind limit and the `COM_WIND_WARN` / `COM_WIND_MAX` values (the action parameter needs PX4 ≥ v1.15 on the Pixhawk) | wind limit for the flight checklist |
| O1 (early Nov) | Log a garden anemometer at about 2–5 m during flights. Pull SJC 1-minute data for the same minutes. Fit the garden/SJC height factor and turbulence scale | calibrated `--height-factor`, `--ti-scale` |
| O2 (mid–late Nov) | Replay each real flight's wind in SITL and compare the distributions of tracking and altitude error, sim vs. real (a *sim-to-real predictivity* check [@kadian2020]) | the sim-vs-real comparison table for the final report |
| Optional (with the algorithm group) | Port the same wind series into Isaac Sim + Pegasus with a `WindDrag` class on Explorer HPC, so camera-based work also sees wind | shared wind module |

## 8. Risks and open questions

- **GPU.** Isaac Sim needs an RTX GPU with ≥ 16 GB. The laptop has 8 GB. Explorer HPC's L40/L40S/A6000 nodes qualify but run without a local display. The legacy README also reports an Isaac Sim 5.1 release-candidate bug in standalone (scripted) mode. Re-test it on 5.1.0 final.
- **PX4 version skew.** Pegasus is pinned to PX4 v1.14.3. Gazebo wind is easiest on PX4 `main`. SIH wind needs v1.18. The Pixhawk's PX4 version should be checked, and the sim kept on the same version where possible.
- **Wind-force fidelity.** Gazebo's WindEffects is a mass-proportional linear law. Pegasus has only linear drag. Neither models rotor drag versus airspeed the way the literature does (Section 6). Prefer computing drag ourselves and applying a force.
- **Airport to garden.** The transfer factor and turbulence scale are estimates until on-site data exist. In light winter winds even stations 6 km apart disagree.
- **What sims leave out.** Building wakes, downwash, ground effect near take-off and landing, and sensor errors caused by wind. These need CFD or real data (Section 6).
- **Data latency.** The 1-minute archive is about a day behind. A live go/no-go check should use the current METAR or the on-site anemometer.

## 9. Files

| Path | What |
|---|---|
| `wind/tools/fetch_wind.py` | Downloads SJC 1-minute data, METAR for SJC/RHV/NUQ/PAO, and Open-Meteo |
| `wind/tools/wind_stats.py` | Flight-hour statistics → `wind/data/sj_wind_summary.md`, `sjc_1min_diurnal.csv` |
| `wind/tools/make_wind_profile.py` | Measured wind → replayable 50 Hz time series (+ JSON metadata) |
| `wind/tools/validate_turbulence.py` | Dryden/MIL turbulence vs. measured gusts → `wind/data/turbulence_validation.csv` |
| `wind/tools/rotorpy_wind_demo.py` | End-to-end replay in RotorPy → `wind/data/rotorpy_demo_results.csv` |
| `wind/tools/make_figures.py` | Figures in `wind/figures/` |
| `reference/08_wind_simulation/` | Local-only: raw data, generated profiles, saved docs and source files, open-access papers, `NOTES.md` |
