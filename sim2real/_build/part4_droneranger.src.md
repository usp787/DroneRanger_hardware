## 4. Question 3 — What DroneRanger can learn, and the challenges it is likely to meet

### 4.1 DroneRanger's simulation chain today

DroneRanger already runs four different simulation pipelines, and they do not share the same assumptions (Table 4). The CCWC paper's central claim is that one PX4–ROS 2 interface lets the same autonomy code run in SITL, HITL and flight, and that the architecture "enables reliable simulation-to-reality transfer" [@ling2026]. The evidence offered for that claim is qualitative: behaviours that work in Gazebo and Unity scenes and early hardware runs. No position errors, latency distributions or multi-run statistics were reported. The authors listed those as future work [@ling2026]. The Spring 2026 prototype then showed the gaps that simulation had hidden [@yin2026]:
- setpoints reported as "reached" while the vehicle was visibly offset;
- about 0.5 m of altitude error near 1 m above ground;
- invalid depth regions and spurious readings near 34 m;
- a port conflict on the flight-controller link;
- an arcing power connector.

**Table 4. DroneRanger's simulation pipelines and what each one assumes.**

| Pipeline | Simulator and autopilot | Sensing assumed | Scene | Status (Oct 2026) |
|---|---|---|---|---|
| CCWC architecture (Spring 2026) | Gazebo 11 and Unity with PX4 SITL; a PyBullet node publishes IMU/GPS/odometry with configurable noise | Unity RGB-D and GPS; a Boolean "obstacle within safe distance" flag | Unity village with an animated deer target | Qualitative demonstrations [@ling2026] |
| Hardware-group SITL twin (Fall 2026, O0) | Gazebo (gz) `gz_x500_depth` with PX4 SITL in lockstep; optional `windy` world | Ideal depth image, 640×480 at 30 Hz, clipped at 0.2–19.1 m, **no noise model**; X500 with a 2.0 kg body and generic motor constants, **no ground effect** | Empty or default worlds; the garden is not modelled | Planned rehearsal for every mission [@zha2026charter; @px4gz; @px4gzmodels] |
| RL training environment | Isaac Lab, three `TiledCamera` depth sensors; **a custom velocity–attitude–thrust PD controller instead of PX4** | Front and ±90° distances (73° FOV), capped at 10 m; ground hits removed with simulator ground truth; goal offset from simulator ground truth; 50 Hz decisions | Procedural obstacles, fixed altitude (2-D task) | DQN Stage 0/1 under development [@ripzou2026rl] |
| Isaac Sim + Pegasus | Isaac Sim 5.1 with Pegasus and PX4 SITL v1.14.3 over MAVLink HIL; ROS 2 Jazzy | RGB and depth 640×480 published on ROS 2 | "Rivermark" outdoor scene: buildings, roads, a parking lot | Infrastructure only, no policy connected [@ripzou2026isaac] |

Three observations follow. First, only the SITL twin and the Pegasus setup keep the real autopilot, PX4 [@meier2015], in the loop. The RL environment replaces PX4 with its own controller, so its transfer problem includes a control-stack gap that NavRL++-style perturbation studies treat as a separate factor [@xu2026navrlpp]. Second, every pipeline renders perfect geometry. None of them reproduces the OAK-D Lite's failure modes:
- a minimum range of about 0.35 m in the 480p mode;
- zero-valued invalid pixels;
- error that grows with the square of distance;
- one-pixel false matches that read as about 33 m [@luxonis2021; @keselman2017].

Third, none of the scenes is a household garden. The Rivermark scene is a parking lot and the Gazebo worlds are empty, so the environment distribution the policies and missions are tested on is not the deployment distribution.

### 4.2 Gap audit for the Fall 2026 platform

Table 5 applies the taxonomy of Section 1.1 to the real vehicle. It combines the project's own measurements and specifications with the evidence reviewed in Sections 2 and 3.

**Table 5. Sim-to-real gaps expected for DroneRanger, with evidence and responses.**

| Gap | In simulation | On the real vehicle | Evidence and remedy from the literature | When |
|---|---|---|---|---|
| Vertical dynamics near the ground | No ground-effect term in the X500 model; ideal barometer; default SITL under-represents real vertical-acceleration variance about tenfold [@kose2026] | ~0.5 m altitude error near 1 m AGL in Spring 2026; ground effect matters up to ~5 rotor radii (≈0.64 m for 10-inch props); barometer dips from downwash | Learned ground-effect residuals made near-ground control stable [@shi2019]; fuse a rangefinder and use PX4's barometer ground-effect compensation [@sanchezcuevas2017; @px4ekf2] | O0–O1 |
| Mass, thrust and battery | 2.0 kg body, generic motor constant and 12.5 ms motor time constant [@px4gzmodels] | Estimated all-up weight ≈2.1 kg with the Jetson and camera, hover throttle ≈55%, thrust-to-weight ≈2.5 falling as the 4S pack sags (estimates) | Identify the dynamics from logs before randomizing. About one minute of flight data can be enough, and a tool that reads PX4 ULogs exists [@eschmann2024sysid; @gronauer2022; @quan2017]. Then randomize only the residual uncertainty, by about 10–20% [@molchanov2019; @ferede2025] | O0 |
| Wind | Calm unless the `windy` world is used | At San Jose airport, 18–21% of autumn days have a gust ≥25 mph | Wind is the classic outdoor gap; learned adaptation needs only minutes of real data [@oconnell2022]; gust models and randomization in SITL [@beard2012] | O1–O2 |
| GNSS and compass | Small, uncorrelated sensor noise | M10 receiver specified at 2.0 m CEP; multipath near houses and trees; magnetic interference from power wiring | Treat GNSS error as slowly varying bias, not white noise [@beard2012]; GNSS-only hover stayed within 1.05 m (95%) vs. 0.35 m with RTK [@joubert2016; @holybrom10] | O1–O2 |
| Depth perception | Noise-free depth (Gazebo, Isaac) | Invalid pixels, minimum range ≈0.35 m, false far readings, noise ∝ z²; rangefinder outputs 0 on unreliable returns | Perception failure was the largest single degradation factor in NavRL++ [@xu2026navrlpp]. Simulate the sensor's failure modes, not only its geometry [@loquercio2021; @keselman2017]. Even Aerial Gym's OAK-D model is idealized [@kulkarni2025] | O2 interface; future |
| Timing and latency | PX4 and Gazebo in lockstep; RL decisions at 50 Hz | USB-TTL serial link, XRCE-DDS agent, Jetson load, 30 Hz depth | Randomize input and action delays (0–100 ms and 0–40 ms in NavRL++) [@xu2026navrlpp; @tan2018; @peng2018]; decide at 5–10 Hz [@tallec2019; @zha2026ar] | O0 bench, RL |
| Control stack | Custom PD controller (RL env); policy acts at velocity level | PX4 cascaded control, Offboard heartbeat and failover semantics, Mission-mode smoothing [@px4offboard] | Keep PX4's inner loops, and let the policy send velocity setpoints, which transfer more easily than motor commands [@gronauer2022; @ferede2024; @xu2025navrl]. Validate sim-to-sim in PX4 SITL first [@jacinto2024; @xu2026navrlpp; @px4sih] | RL hand-over |
| Scene and appearance | Parking lot or empty world | Lawn, flower beds, fences, thin branches, changing light and season | Digital twins from phone video [@low2025]; relightable splats for lighting [@lv2026]. Scenes are static and must be re-captured, and foliage moving in downwash defeated a splat-trained policy [@huang2026] | Future |
| Software integration | One interface by design | NED/FRD vs ENU/FLU frames, QoS mismatches, PX4 v1.16+ versioned topics, port conflicts | Vertical integration is part of the gap [@panerati2026]. Stage the testing SIL→HIL→field [@jiang2025]. Simulation reproduces most, but not all, autopilot bugs [@timperley2018], and replaying real logs in SITL builds realistic tests [@khatiri2023] | O0 |
| Evaluation | Ground-truth state available | Only the EKF2 estimate onboard | Sim metrics can fail to predict real ones (SRCC 0.18) until the simulator is tuned (0.844) [@kadian2020]; measure against independent truth | O0–O2 |
| Other agents (wildlife) | Scripted deer in Unity | Animal reactions depend on species, altitude and approach | Reaction thresholds vary widely [@bennitt2019; @mulero2017]; herding models need parameters measured on live animals [@paranjape2018]; rehearse in simulation, validate in the field [@schiano2022] | Future |

### 4.3 Lessons for DroneRanger

**L1. Make "sim-to-real" a measured quantity.** The literature that succeeded quantified its gap; the CCWC paper did not. For DroneRanger, every O0 mission file and PX4 parameter file should be run in SITL and then flown unchanged. Both runs should be scored on the same metrics against independent truth. Kadian et al. show why this matters: their simulator ranked methods in a way that did not hold on the robot until simulator parameters were corrected [@kadian2020]. A pre-registered sim-vs-real comparison table is the cheapest credible replacement for the phrase "reliable sim-to-real transfer".

**L2. Calibrate before randomizing.** System identification came before randomization in the most reliable transfers, from legged robots (actuator models, measured latency) [@tan2018; @hwangbo2019] to drone racing (residual models fitted to real data) [@kaufmann2023]. Gronauer et al. showed the same for small quadrotors: fitting the motor time constant and latency to real flight data made zero-shot transfer work [@gronauer2022]. Eschmann et al. identified a quadrotor's thrust curve, inertia and motor delay from about one minute of flight data, with a tool that reads PX4 ULog files directly [@eschmann2024sysid]. The hardware group's equivalent is concrete:
- weigh the aircraft;
- let PX4's hover-thrust estimator converge and copy the value into the Gazebo model;
- fit the motor time constant and thrust coefficient from a step test in the logs;
- measure IMU, barometer and GNSS noise at rest and in hover.

Quan's textbook gives the parameter-measurement and sensor-model procedures for multicopters [@quan2017]. Its companion practice book turns them into Pixhawk-based experiments, from dynamic modelling and sensor calibration to failsafe-logic design [@quan2020].

**L3. Randomize what remains uncertain, and test the mission, not only the policy.** Domain randomization is usually discussed for learned policies [@tobin2017; @peng2018; @muratore2022], but the same idea hardens a scripted Mission-mode patrol. Moderate ranges, about 10–20% around identified values, worked best for quadrotors; wider ranges cost performance [@molchanov2019; @ferede2025]. Monte Carlo SITL runs should vary wind (`windy` world), mass (±10–20%), GNSS bias, magnetometer offset and link delay. Their output is the distribution of geofence margin, waypoint error and battery use, not a single pass/fail.

**L4. Keep the real stack in the loop for as long as possible.** Every simplified component in the loop is a new gap. The ladder goes from PX4 SITL with the flight parameter file, to simulation-in-hardware (SIH) on the Pixhawk with the Jetson and serial link attached [@px4sih], to propeller-off bench tests, and then to tethered or low-altitude flight. This is the staged pipeline of Jiang et al. [@jiang2025] and the original CCWC plan [@ling2026]. For the RL policy, a sim-to-sim step (Isaac Lab controller → PX4 SITL through Pegasus or Gazebo) exposes the controller gap before any hardware is involved [@jacinto2024; @xu2026navrlpp]. RoboGauge found that a second simulator predicted real performance better than the training simulator [@wu2026robogauge]. The policy should command velocities and leave the inner loops to PX4. That is the level at which learned aerial policies have transferred most reliably [@gronauer2022; @ferede2024; @xu2025navrl]. Neural-Fly's outdoor tests used the same hardware split as DroneRanger: a Pixhawk running PX4 in Offboard mode, under a companion computer that ran the learned controller at 50 Hz [@oconnell2022].

**L5. Choose abstractions that transfer, and define what "invalid" means.** Policies that consume depth or other intermediate representations transfer better than policies that consume raw pixels [@muller2018; @loquercio2021; @kaufmann2020]. The CCWC warning grid is such an abstraction [@ling2026]. It must still encode invalid depth as "unknown", never as "far", because the closest obstacles are exactly the ones a stereo camera cannot measure. The RL observation should carry the same convention, plus the yaw rate and speed that make it Markov.

**L6. Put safety outside the parts that are least validated.** Learned or simulation-tuned behaviour should sit under an independent supervisor: the PX4 geofence and failsafes, an RC kill switch, and for any learned policy a shield or barrier-function filter [@alshiekh2018; @ames2019; @brunke2022]. Recent aerial RL systems use exactly this pattern [@xu2025navrl; @zhang2026shield].

**L7. Treat each real flight as data for the simulator.** Swift fitted its residual models to a handful of real runs; its dynamics residual used fewer than a thousand samples [@kaufmann2023]. Neural-Fly learned its wind representation from about 12 minutes of flight [@oconnell2022]. Every DroneRanger flight should therefore log:
- the ULog;
- a rosbag of the depth stream and odometry;
- the parameter file;
- the wind reading;
- the ground-truth references (ground markers, or RTK if funded).

**L8. Plan the garden digital twin as future work, with its limits in view.** Gaussian-splatting twins built from a few minutes of phone video now train visual policies that transfer zero-shot [@low2025], and relighting addresses part of the appearance gap [@lv2026]. A splat is still a static snapshot. Lawns grow, leaves move in wind, and light changes through the day and the season, so the twin must be re-captured and validated. Capture must also stay inside the host property, for the same privacy reasons that constrain the camera in flight [@zha2026lit].

**L9. Do not over-claim.** Many celebrated sim-to-real results depend on motion capture, controlled arenas or extensive engineering [@kaufmann2023; @valassakis2020]. Statements about DroneRanger should name the conditions under which transfer was measured: site, wind, lighting, number of trials and the source of truth.

### 4.4 Challenges the project is likely to meet this semester

**Table 6. Sim-to-real risk register for O0–O2 (likelihood/impact: H high, M medium, L low).**

| # | Challenge | L/I | Early warning | Mitigation |
|---|---|---|---|---|
| R1 | SITL missions are perfect, but outdoor waypoints miss by metres | H/M | Estimate says "reached" while the aircraft is visibly off the marker | Judge success against surveyed markers; set tolerances above the GNSS error; RTK if funded [@joubert2016] |
| R2 | Altitude hold, take-off and landing behave differently near the ground | H/M | Barometer dips at take-off/landing; climb-back on landing | TFmini Plus fused in EKF2; ground-effect compensation; log the rangefinder unfused first [@px4ekf2; @sanchezcuevas2017] |
| R3 | Wind degrades tracking and battery life beyond SITL predictions | M/H | Larger tilt and throttle in logs; shorter flights | Rehearse in the `windy` world; gust go/no-go limit; morning slots |
| R4 | Compass interference or GNSS multipath near the house | M/H | EKF2 innovation warnings; yaw drift; position jumps | GPS mast; compass calibration with the payload powered; site survey before O2 |
| R5 | Link latency, jitter or drop-outs absent in lockstep SITL | M/M | XRCE-DDS gaps; Offboard heartbeat warnings | SIH bench test with the real link; latency audit [@cotta2023]; heartbeat monitoring |
| R6 | Battery sag shortens flights and reduces control margin | M/M | Voltage under load; hover throttle creeping up | Conservative failsafes; plan 8–10 min flights; log energy per lap |
| R7 | Outdoor depth artifacts (low-texture lawn, sky, thin branches, glare, foliage moving in downwash [@huang2026]) | M/L for O2 | High invalid-pixel fraction; false near or far readings | Characterize the depth interface; invalid means unknown; not on the O2 critical path |
| R8 | Few real flights (approval lead time, rain, short days) | H/H | Calendar slips; cancelled test days | Pre-written test cards; maximize data per flight (L7); December buffer |
| R9 | Version drift between the simulated and the real stack | M/M | Topics present in SITL but silent on the vehicle | Pin PX4, `px4_msgs` and JetPack versions; one parameter file for both [@px4ros2] |
| R10 | RL policy hand-over fails on PX4 | H/M | Oscillation or overshoot in PX4 SITL | Interface control document; sim-to-sim in PX4 SITL; shadow mode only this semester [@xu2026navrlpp] |
| R11 | Compute limits block photorealistic simulation | M/L | Isaac Sim will not render on the H200 or the 8 GB laptop GPU | Gazebo SITL for the hardware group; RTX-class nodes for camera-based RL [@nvidiaisaac] |

### 4.5 A sim-vs-real validation protocol for O0–O2

**Table 7. Paired sim/real measurements that turn transfer into numbers.**

| Metric | SITL procedure | Real procedure | Truth source | Report |
|---|---|---|---|---|
| Hover hold, 60 s at 2 m | Calm and `windy` worlds | Calm morning, then ≤15 mph | TFmini (height); ground markers or RTK (horizontal) | RMSE per axis, sim vs. real, ≥10 trials |
| Altitude step 1 m → 3 m | Same parameter file | Same | TFmini | Rise time, overshoot, settling |
| Waypoint loop (≥4 waypoints + RTL) | Same mission file, Monte Carlo over wind, mass and GNSS bias | Garden (O2) | Surveyed markers | Cross-track error, lap time, energy per lap, geofence margin |
| Failsafes (RC loss, geofence, low battery, Offboard loss) | All triggered in SITL | Triggered in the field where safe | Logged mode transitions | Trigger latency and behaviour, 100% verified |
| Link timing | Not represented in lockstep | Jetson ↔ Pixhawk over TELEM2 | Offset/skew estimator [@cotta2023] | Latency and jitter distribution |
| Depth interface | Gazebo ideal depth | OAK-D Lite at 1, 2 and 3 m targets, sun and shade | Tape measure | Invalid-pixel fraction, bias and spread |

If several conditions are flown, for example calm vs. windy or two gain sets, the rank correlation between sim and real outcomes is a direct, small-sample version of Kadian et al.'s Sim-vs-Real Correlation Coefficient [@kadian2020].
