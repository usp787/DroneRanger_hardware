# Sim-to-Real Transfer for Aerial Robots and What It Means for DroneRanger: A Comprehensive Literature Review

*Jiarui Zha (zha.j@northeastern.edu), DroneRanger hardware group, CS 7980 Research Capstone, Northeastern University (Silicon Valley). PI: Prof. Ilmi Yoon, NEURAI Lab. Version 1.0, 2026-10-11.*

*Companion files: [references.md](references.md) (reference list with access links), [references.bib](references.bib) (BibTeX), and the brief Canvas version [DroneRanger_Sim2Real_Literature_Review_Brief.docx](DroneRanger_Sim2Real_Literature_Review_Brief.docx).*

---

## Executive summary

**Q1. How far has sim-to-real come?**
- **Transfer is now routine where the physics can be modelled.** It used to fail by default. Today it works for tasks whose physics can be modelled or randomized: legged and humanoid locomotion, low-level quadrotor control and drone racing [[1]](#ref-1)–[[3]](#ref-3).
- **The recipe that works has four parts:**
  - calibrate the simulator with a little real data [[3]](#ref-3), [[4]](#ref-4);
  - randomize what remains uncertain [[5]](#ref-5), [[6]](#ref-6);
  - keep the policy's inputs similar in simulation and reality [[7]](#ref-7), [[8]](#ref-8);
  - train at GPU scale [[9]](#ref-9).
- **New tools since 2023.** Real-to-sim digital twins [[10]](#ref-10), [[11]](#ref-11), differentiable physics [[12]](#ref-12) and foundation-model tools [[13]](#ref-13), [[14]](#ref-14) have joined the recipe. Transfer is also increasingly *measured*, not just asserted [[15]](#ref-15), [[16]](#ref-16).
- **Drones in the wild.** Drones now fly learned policies through forests and clutter with onboard sensing [[7]](#ref-7), [[17]](#ref-17), [[18]](#ref-18). Many headline results still rely on motion capture.

**Q2. What are the latest challenges?**
- **Perception** is now the largest single source of degradation, and recent systems also show gaps in **latency, timing and the control stack** [[19]](#ref-19), [[20]](#ref-20).
- **Hard-to-model physics** persists: aerodynamics, actuator limits and battery limits [[21]](#ref-21), [[22]](#ref-22).
- **The newest tools have clear limits.** Digital twins are static and mostly rigid [[23]](#ref-23). World models are not yet physically consistent [[24]](#ref-24), [[25]](#ref-25). Co-training saturates [[26]](#ref-26).
- **Evaluation and safety assurance lag behind.** Real trials are few, correlations are setup-specific, and safety filters inherit estimation errors [[27]](#ref-27), [[28]](#ref-28).

**Q3. What does this mean for DroneRanger?**
- **Four pipelines, none measured.** DroneRanger runs four simulation pipelines with different assumptions (Table 4). None models the OAK-D Lite's depth failures, the X500's ground effect or the real serial-link timing. Wind exists only as an uncalibrated `windy` world, and the RL environment replaces PX4 with its own controller. The CCWC claim of "reliable sim-to-real transfer" has not yet been measured [[29]](#ref-29).
- **Calibrate, then randomize.** First identify the vehicle from logs: mass, hover thrust, motor constants and sensor noise [[30]](#ref-30)–[[32]](#ref-32). Then randomize wind, mass, GNSS bias and delay in Monte Carlo SITL runs.
- **Keep the real stack in the loop.** Progress from SITL to simulation-in-hardware, then the bench, then the field [[33]](#ref-33), [[34]](#ref-34). Validate any RL policy sim-to-sim in PX4 SITL before it touches hardware [[19]](#ref-19).
- **Make transfer a number.** Pair every SITL run with a real run against independent ground truth. The semester should then end with measured sim-vs-real differences and, across conditions, a rank correlation [[15]](#ref-15).
- **Expect these risks this semester.** Each one has a mitigation in Table 6:
  - waypoint offsets at the scale of GNSS error;
  - altitude errors near the ground;
  - wind;
  - compass interference;
  - link jitter;
  - battery sag;
  - very few flight opportunities.

---

## 1. Introduction

### 1.1 What "sim-to-real" means

A controller, planner, perception model or whole mission is developed in simulation and then run on a physical robot. *Sim-to-real transfer* is the degree to which behaviour and performance carry over. The *reality gap* is everything that makes them differ. The term goes back to evolutionary robotics. Brooks warned in 1992 that programs evolved on simulated robots can fail on real ones, because simulated sensing and actuation differ from the real thing [[35]](#ref-35). Jakobi et al. then showed that the right amount of noise in a simulator could make evolved controllers for a small mobile robot transfer [[36]](#ref-36). Twenty years later the same community still described the gap as the central obstacle to using simulators [[37]](#ref-37), [[38]](#ref-38).

Most of this literature concerns policies learned by reinforcement learning [[39]](#ref-39), [[40]](#ref-40). The same gap affects any controller, estimator or mission that is tuned in simulation, including a scripted PX4 patrol.

This review uses a six-part taxonomy of the gap, which recurs in the surveys [[41]](#ref-41)–[[44]](#ref-44):

1. **Dynamics gap:** mass, inertia, actuator response, aerodynamics, contact and friction.
2. **Sensing and perception gap:** noise, bias, failure modes, rendering realism and lighting.
3. **Timing and latency gap:** delays, jitter, asynchronous sensors and discrete decision rates.
4. **Control-stack and software gap:** a different controller, middleware, coordinate frames or message versions in simulation than on the robot.
5. **Environment-distribution gap:** the scenes, weather and other agents that were simulated, as against those actually met.
6. **Evaluation gap:** metrics that are easy to compute in simulation (ground-truth state, collision checks) but not on the robot, so the gap itself goes unmeasured.

The first three are what most papers mean by the reality gap. The last three are less glamorous, but the DroneRanger record (Section 4) shows they matter as much on a capstone-scale platform.

### 1.2 Why it matters for DroneRanger

DroneRanger's first publication describes a simulation-guided architecture: PX4, ROS 2, Gazebo and Unity are bridged so that identical autonomy code runs in simulation and in flight. The paper states that the architecture "enables reliable simulation-to-reality transfer" for planning and avoidance [[29]](#ref-29). In Fall 2026 the project has two threads.

- **Hardware group.** It must make the Spring 2026 prototype safe, measurable and outdoor-ready, ending with O1 (manual outdoor flight) and O2 (an autonomous PX4 Mission-mode patrol over a household garden). Every mission is rehearsed in PX4 SITL first (O0) [[45]](#ref-45).
- **RL group.** It is training a DQN navigation policy in Isaac Lab, and the hardware group has agreed to prepare the vehicle to receive it [[46]](#ref-46), [[47]](#ref-47).

Both threads depend on simulation predicting reality. This review asks how far that assumption can be trusted.

### 1.3 Questions and method

The review answers three questions:

- **Q1.** What progress has sim-to-real transfer made, overall and for aerial robots in particular? (Section 2)
- **Q2.** What are the latest open challenges, as of 2024–2026? (Section 3)
- **Q3.** What can DroneRanger learn from this literature, and which sim-to-real challenges is it likely to meet this semester? (Section 4)

This is a narrative review, not a systematic one. Sources came from three places:
- the project's local libraries: `../reference/`, about 100 papers and documents on state estimation, the PX4–ROS 2 stack, perception and safety; and `../../LEGACY_reference_papers/`, 67 papers on learned navigation, simulators and wildlife deterrence;
- the project's own documents: the CCWC paper, the Spring 2026 handover, the hardware charter, the October 6 literature review, and the RL and Isaac repositories;
- new searches made on 2026-10-11 for 2024–2026 work, using IEEE Xplore, arXiv, publisher sites and Google Scholar.

Peer-reviewed sources were preferred. Preprints are included where they are the newest evidence, and they are labelled as preprints in the reference list. Every journal article was resolved through LibKey (Northeastern University Library). LibKey does not index conference papers, book chapters or books, so their DOIs and metadata were checked on Crossref, PMLR or arXiv. Vendor documentation is cited for system behaviour (PX4, Luxonis, NVIDIA), not for research claims. Quantitative claims are taken from the cited papers' own abstracts or results; where a number comes from this project's estimates, the text says so.

## 2. Question 1 — How far has sim-to-real transfer come?

### 2.1 Five phases in three decades

Sim-to-real research has moved through five overlapping phases (Table 1). Each phase answered the main failure of the one before it.

**Table 1. Phases of sim-to-real research.**

| Phase | Period | Core idea | Representative work | What it made possible |
|---|---|---|---|---|
| Naming the gap | 1992–2017 | Simulators are wrong in systematic ways; add noise and prefer behaviours that are known to transfer | [[35]](#ref-35)–[[38]](#ref-38) | The simulator is treated as a design choice, not a neutral test bed |
| Randomize | 2017–2020 | Train across many randomized simulators so that reality looks like one more sample | [[5]](#ref-5), [[48]](#ref-48)–[[53]](#ref-53) | First zero-shot transfers of deep policies to arms, hands and drones |
| Identify and adapt | 2018–2022 | Fit the simulator, or a residual model, to real data; adapt online; distil privileged "teacher" policies | [[4]](#ref-4), [[21]](#ref-21), [[54]](#ref-54)–[[59]](#ref-59) | Legged locomotion off-road; drones landing and flying in strong wind |
| Scale | 2021–2024 | GPU-parallel simulation makes thousands of randomized environments cheap | [[2]](#ref-2), [[3]](#ref-3), [[9]](#ref-9), [[60]](#ref-60)–[[63]](#ref-63) | Training in minutes to hours; champion-level drone racing; locomotion in the wild |
| Reconstruct, differentiate, generate | 2023–2026 | Build the simulator from real data, differentiate through physics, and let foundation models design or replace parts of the simulator | [[10]](#ref-10)–[[14]](#ref-14), [[19]](#ref-19), [[20]](#ref-20), [[64]](#ref-64), [[65]](#ref-65) | Zero-shot visual navigation in reconstructed scenes; automated design of randomization; system-level transfer studies |

### 2.2 The toolbox and its limits

**Randomize.** Domain randomization trains a model on a distribution of simulators wide enough that the real world falls inside it.
- *Visual randomization.* Tobin et al. trained an object detector only on images with non-realistic random textures. It localized real objects to about 1.5 cm, which was enough for grasping [[48]](#ref-48). Sadeghi and Levine flew a drone through real indoor corridors with a policy trained only on randomized synthetic images [[49]](#ref-49).
- *Dynamics randomization.* Peng et al. randomized masses, friction, damping, controller gains and the action time step. The resulting pushing policy kept its performance on a real arm and tolerated significant calibration error [[5]](#ref-5).
- *Scaled-up randomization.* OpenAI combined both kinds of randomization at large scale for dexterous in-hand manipulation [[52]](#ref-52). It later grew the randomization ranges automatically as the policy improved ("automatic domain randomization") [[53]](#ref-53).

For quadrotors, moderate randomization is usually best. About 20% around nominal values worked best for Molchanov et al. [[50]](#ref-50). In racing, no randomization made real drones miss the gates, 10% gave the best real reward, and more randomization cost speed [[66]](#ref-66).

The weaknesses are just as well documented. Initial guesses of the parameters and their variances are typically inaccurate, the methods need task-specific tuning, and robustness can come at the price of conservative behaviour [[6]](#ref-6). Valassakis et al. found that many published methods underplay the task-specific engineering they required. In their tests, simply injecting random forces worked as well as elaborate parameter randomization or recurrent adaptation [[67]](#ref-67).

**Identify.** The second family makes the simulator itself closer to reality.
- *Actuator and latency models.* Tan et al. moved quadruped gaits to hardware by adding an identified actuator model and simulated latency on top of randomization [[4]](#ref-4). Hwangbo et al. replaced the analytic actuator model of ANYmal with a neural network trained on real data [[54]](#ref-54).
- *Closed-loop calibration.* SimOpt and BayesSim close the loop: real rollouts update the randomization distribution itself [[55]](#ref-55), [[56]](#ref-56).
- *Aerodynamic residuals.* For multirotors, the residual is aerodynamic. Neural Lander learned the ground-effect force from flight data, which made near-ground control and landing stable [[57]](#ref-57). NeuroBEM combined blade-element theory with a learned residual for agile flight [[68]](#ref-68).
- *Small quadrotors.* Gronauer et al. fitted thrust-to-weight, motor time constant and latency to about an hour of real flight data by Bayesian optimization (identified latency ≈18 ms). Low-level motor-command policies needed more simulator fidelity than attitude-rate policies, and policies trained with zero latency transferred worst [[30]](#ref-30). A 2024 method identified inertia, thrust curve, torque coefficient and motor delay from about one minute of flight data, and its tool accepts PX4 ULog files. An RL policy trained only on the identified model then flew a 3.35 kg quadrotor outdoors in gusts up to 8 m/s [[31]](#ref-31).
- *Residual models in Swift.* Swift's simulator used an aerodynamic model fitted to flight data, not dynamics randomization. Its champion-level racing policy then relied on residual models fitted to a handful of real runs recorded with motion capture. Gaussian processes modelled the drift of its visual–inertial odometry, and k-nearest-neighbour regression modelled residual accelerations. The policy was then fine-tuned in the augmented simulator [[3]](#ref-3).

**Adapt.** Instead of one robust policy, the policy can infer the conditions it is in.
- *Image adaptation.* For perception, domain adaptation maps simulated or real images into a shared or canonical space [[69]](#ref-69), [[70]](#ref-70).
- *Privileged teacher, sensor-only student.* For control, the most influential idea is "learning by cheating": a teacher policy with privileged simulator state is distilled into a student that sees only onboard sensors [[8]](#ref-8). This recipe produced quadrupeds that walk over challenging terrain and through the wild [[58]](#ref-58), [[62]](#ref-62), and it trained Loquercio et al.'s high-speed forest-flight policy entirely in simulation [[7]](#ref-7).
- *Online adaptation.* Rapid Motor Adaptation estimates the dynamics online from recent history [[59]](#ref-59). Neural-Fly learns a wind-invariant representation from about 12 minutes of flight and adapts the last layer online [[21]](#ref-21). A learned quadcopter controller with "extreme adaptation" infers a latent vehicle description from its sensor–action history. On hardware it handled a 3.7× mass difference, large changes in propeller constant, and motor failures [[71]](#ref-71).

**Abstract.** Transfer is easier when the policy consumes an intermediate representation that looks the same in simulation and reality.
- *Driving.* Müller et al. trained a driving policy on semantic segmentation instead of pixels and moved it to a real truck without real training data [[72]](#ref-72).
- *Acrobatics.* Deep Drone Acrobatics fed the policy feature tracks rather than images [[73]](#ref-73).
- *Depth.* High-speed flight in the wild fed it depth computed by stereo matching on simulated image pairs, so the policy saw realistic stereo artefacts [[7]](#ref-7).

The price is that the abstraction must be computable onboard, and its own failures (missing depth, lost features) become the new gap.

**Scale.** GPU-parallel simulators changed what is affordable.
- *Physics on the GPU.* Isaac Gym moved physics and policy training onto one GPU [[60]](#ref-60). Rudin et al. then trained quadruped locomotion in minutes with thousands of parallel robots [[9]](#ref-9).
- *Frameworks.* Orbit and its successor Isaac Lab generalized this into a framework with rendered sensors [[61]](#ref-61), [[74]](#ref-74). Aerial counterparts include OmniDrones and Aerial Gym [[75]](#ref-75), [[76]](#ref-76).
- *The 2025 generation.* MuJoCo Playground trains locomotion and manipulation policies in minutes on one GPU, and they transferred zero-shot to quadrupeds, humanoids and arms [[77]](#ref-77). ManiSkill3 combines GPU-parallel simulation with rendering at tens of thousands of frames per second [[78]](#ref-78). Newer engines such as Genesis and Newton advertise very high throughput and better transfer, but those claims are so far reported by their developers, not independently validated [[79]](#ref-79), [[80]](#ref-80).
- *What it changed.* Scale makes heavy randomization and large hyper-parameter sweeps cheap. It does not by itself make the simulator more faithful. NavRL++ found that larger training scale improved convergence, but perception failures still dominated real-world degradation [[19]](#ref-19).

**Reconstruct.** The newest family builds the simulator from the real environment.
- *Scene representations.* Neural radiance fields and 3D Gaussian splatting reconstruct photorealistic, real-time renderable scenes from ordinary images [[64]](#ref-64), [[65]](#ref-65).
- *Drones.* SOUS VIDE built a drone simulator on a Gaussian-splat scene captured with a phone. It distilled an MPC expert with privileged information into an onboard visuomotor policy that transferred zero-shot, across 105 hardware experiments [[10]](#ref-10). Lv et al. made the splats relightable, so lighting can be randomized. Their monocular policy flew through real forests at up to 10 m/s [[18]](#ref-18).
- *Beyond drones.* The same idea spread quickly.
  - RialTo builds a digital twin from a real scan and uses RL in it to make real-world imitation policies robust. It reports robustness gains of more than 67% on eight manipulation tasks [[11]](#ref-11).
  - SplatSim reached 86.25% zero-shot real-world success with RGB policies trained only in a splat-rendered simulator, against 97.5% for policies trained on real data [[23]](#ref-23).
  - Vid2Sim turns a single monocular video into an interactive navigation environment. It improved real-world success by 68.3% over earlier simulation methods [[81]](#ref-81).
  - PhysTwin fits physics to videos of deformable objects [[82]](#ref-82).
  - Real-is-Sim keeps a twin synchronized with the real scene at 60 Hz, so the policy always acts on the simulated robot [[83]](#ref-83).

**Differentiate and generate.** Two further directions reduce the cost of learning.
- *Differentiable physics.* Zhang et al. trained vision-based agile flight by back-propagating through a simple differentiable point-mass model. The policy used low-resolution depth and ran onboard a low-cost computer [[12]](#ref-12).
- *Model-based RL.* Dream to Fly learned racing from pixels with a world model, DreamerV3; real flights used rendered images in a hardware-in-the-loop setup [[84]](#ref-84).
- *Automated design.* Foundation models now automate parts of the sim-to-real recipe itself. Eureka used an LLM to write reward functions that beat human-engineered ones on 83% of 29 simulated tasks [[85]](#ref-85). DrEureka extended this to choosing domain-randomization ranges, improving a quadruped's forward velocity by 34% over human-designed settings [[13]](#ref-13).
- *Generated training images.* Generative image models can replace hand-built textures during training. LucidSim transferred a visual parkour policy zero-shot to a cheap RGB camera [[86]](#ref-86).
- *Sim-and-real co-training.* Large generalist policies are increasingly trained on a mix of simulated and real data [[87]](#ref-87). Maddukuri et al. found that simulation data raised real-world success by 38% on average, even with notable sim-real differences [[14]](#ref-14).
- *World models.* Video world models are being tried as learned simulators and policy evaluators [[24]](#ref-24), [[88]](#ref-88), [[89]](#ref-89). Their limits are discussed in Section 3.6.

### 2.3 Where transfer works best today

**Legged and humanoid robots** are the clearest success. A 2025 IJRR review describes the standard toolkit as system identification, domain randomization, domain adaptation and privileged teacher–student training [[1]](#ref-1).
- *Outdoor humanoid walking.* Radosavovic et al. deployed a transformer policy zero-shot on the Digit humanoid outdoors. They combined randomized dynamics, noise and delay with teacher–student training and adaptation from observation history [[90]](#ref-90).
- *Soccer skills.* Haarnoja et al. transferred soccer skills to a small humanoid zero-shot. They credited "sufficiently high-frequency control, targeted dynamics randomization, and perturbations." The gap was still measurable: real and simulated walking speeds differed by 13%, and get-up times by 28% [[91]](#ref-91).
- *Residual correction.* ASAP learned a residual "delta action" model from real rollouts and fine-tuned the policy in the corrected simulator. This cut tracking error more than system identification or randomization alone [[92]](#ref-92).
- *Extreme motions.* OmniXtreme ran flips and breakdancing on a real humanoid by adding torque–speed envelopes, aggressive randomization and power-safety regularization [[22]](#ref-22).

**Manipulation** transfers well for rigid objects and quasi-static tasks, from in-hand reorientation [[52]](#ref-52) to splat-rendered RGB policies [[23]](#ref-23), and sim-and-real co-training has become a practical recipe for vision-based policies [[14]](#ref-14), [[26]](#ref-26). Deformable, transparent and contact-rich cases remain hard (Section 3).

**Navigation** transfers when the policy consumes geometry (depth, LiDAR or occupancy) rather than raw pixels, and when the simulated scenes resemble the deployment scenes [[15]](#ref-15), [[19]](#ref-19), [[81]](#ref-81). Aerial navigation follows the same pattern (Section 2.4).

### 2.4 Aerial robots: from motion-capture arenas to forests

Multirotors have been a proving ground for sim-to-real, because their rigid-body dynamics are simple to simulate. Their aerodynamics, batteries and sensors are not. Table 2 lists the milestones most relevant to DroneRanger.

**Table 2. Selected aerial sim-to-real milestones.**

| Year | Work | Task | Main transfer technique | State / sensing in the real tests |
|---|---|---|---|---|
| 2017 | Hwangbo et al. [[93]](#ref-93) | Low-level control | Conservative policy optimization in a deliberately simple simulator; recovered from upside-down hand throws | Motion capture + onboard IMU |
| 2017 | CAD2RL [[49]](#ref-49) | Indoor collision-free flight | Visual randomization; no real images | Monocular camera on a consumer drone; no motion capture |
| 2019 | Sim-to-(multi)-real [[50]](#ref-50) | Low-level control on several airframes | Dynamics randomization | Motion capture |
| 2019 | Neural Lander [[57]](#ref-57) | Near-ground control and landing | Learned ground-effect residual (landing height error 0.13 m → ≈0) | Motion capture |
| 2020 | Deep drone racing [[51]](#ref-51) | Gate detection for racing | Visual randomization | Onboard camera + VIO |
| 2020 | Deep drone acrobatics [[73]](#ref-73) | Acrobatic manoeuvres | Abstraction (feature tracks), privileged expert | Onboard camera + IMU |
| 2021 | High-speed flight in the wild [[7]](#ref-7) | Forest flight | Privileged expert, simulated stereo depth | Onboard stereo + VIO |
| 2022 | Neural-Fly [[21]](#ref-21) | Flight in winds up to 12.1 m/s | Learned representation + online adaptation | Pixhawk/PX4 in Offboard mode with a companion computer; motion capture indoors, GPS outdoors |
| 2023 | Swift [[3]](#ref-3) | Racing against human champions | Residual perception and dynamics models fitted to real data | Onboard VIO and gate detection; motion capture used for data collection |
| 2023 | Song et al. [[63]](#ref-63) | Racing near the physical limit | RL vs. optimal control, dynamics randomization | Motion capture |
| 2024 | Learning to fly in seconds [[2]](#ref-2) | Low-level control | Fast training (18 s), action history, asymmetric critic | Motion capture |
| 2024 | End-to-end time-optimal flight [[94]](#ref-94) | Racing, motor level | Residual thrust/moment model from flight data | Motion capture; larger sim–real gap than a policy over an inner-loop controller |
| 2024 | Kulkarni and Alexis [[95]](#ref-95) | Collision-free navigation | Depth → collision-encoding latent → RL, with latency and noise randomization | Onboard depth + VIO, Jetson Orin NX |
| 2025 | SimpleFlight [[96]](#ref-96) | Low-level control | Five factors: input choice, time-aware critic, smoothness reward, system identification + selective randomization, large batches | Motion capture |
| 2025 | NavRL [[97]](#ref-97) | Safe flight among moving obstacles | Isaac Sim PPO with velocity commands + velocity-obstacle shield | Onboard RGB-D, LiDAR-inertial odometry, Jetson Orin NX |
| 2025 | Differentiable physics [[12]](#ref-12) | Agile vision-based flight | Back-propagation through a simple point-mass model | Onboard 16×12 depth on a US$21 computer |
| 2025 | SOUS VIDE [[10]](#ref-10) | Visual navigation | Gaussian-splat digital twin + distillation + adaptive low-level module | Onboard Jetson Orin Nano; camera, optical flow, IMU |
| 2025 | GRaD-Nav [[98]](#ref-98) | Visual gate navigation | Splats + differentiable dynamics + runtime adaptation | Onboard Orin Nano; 6–7/10 real vs. 9–10/10 simulated |
| 2026 | Zhang et al. [[17]](#ref-17) | High-speed flight in clutter and forest | RL + physics-informed reward + safety filter | Onboard depth camera (100×60 input) |
| 2026 | Huang et al. [[99]](#ref-99) | Clutter flight, monocular RGB | Splat scenes + randomization + adversarial domain adaptation | Onboard Orin NX; 80% real vs. 90% simulated success |
| 2026 | Lv et al. [[18]](#ref-18) | Forest flight, monocular | Relightable Gaussian splatting; twilight success 3/10 → 8/10 with relighting | PX4, Jetson Orin NX, RGB, GNSS–IMU EKF |
| 2026 | Dream to Fly [[84]](#ref-84) | Racing from pixels | Model-based RL (DreamerV3) | Hardware-in-the-loop with rendered images: tests dynamics, not visual transfer |
| 2026 | NavRL++ [[19]](#ref-19) | Navigation (aerial and legged) | Factorized perturbation study + perturbation-aware fine-tuning | Onboard RGB-D + LiDAR |
| 2026 | Ranjbar Divkoti and Aguiar [[100]](#ref-100) | Dynamic obstacle avoidance with three range sensors | PPO with a behaviour grid map | Small quadrotor with three range sensors |

Two trends stand out. The first is a move from motion-capture arenas to onboard sensing. Low-level and agile results still mostly rely on external state estimation [[2]](#ref-2), [[50]](#ref-50), [[66]](#ref-66), [[96]](#ref-96). A 2025 review of real-world deep RL notes that "for quadrotors, most tests remain confined to controlled, obstacle-free indoor environments" [[101]](#ref-101). Navigation results since 2021 increasingly rely on onboard VIO, depth and LiDAR [[7]](#ref-7), [[95]](#ref-95), [[97]](#ref-97). The second is a move from one technique to a recipe. The strongest recent systems combine several techniques: identification, randomization, abstraction, a privileged teacher, a safety layer, and some real data. The surveys of drone racing [[102]](#ref-102) and of RL for real robots [[103]](#ref-103), [[104]](#ref-104) make the same point. The engineering of the whole system decides transfer, not any single algorithm.

The level at which the policy acts also matters. Low-level motor-command policies need more simulator fidelity than attitude-rate or velocity policies [[30]](#ref-30). An end-to-end motor-level racing policy lost most of its simulated advantage on the real drone, while a policy running over an inner-loop controller transferred more consistently [[94]](#ref-94). NavRL chose velocity commands specifically for transferability [[97]](#ref-97).

Simulators followed the same arc:
- Gazebo with RotorS ran the real autopilot against simulated dynamics [[105]](#ref-105), [[106]](#ref-106).
- AirSim and Flightmare added photorealism and fast rendering [[107]](#ref-107), [[108]](#ref-108). Gym-pybullet-drones offered a lightweight learning environment [[109]](#ref-109).
- Pegasus connected Isaac Sim to PX4 [[110]](#ref-110). Aerial-autonomy-stack runs a full PX4/ArduPilot, ROS 2 and edge-compute stack more than 20 times faster than real time. Its authors explicitly count the vertical integration of heterogeneous hardware and software as part of the "simulation-to-reality gap" [[111]](#ref-111).
- A 2025 survey of 44 aerial simulators notes that transfer remains hard where unmodelled effects dominate: agile flight, close-proximity flight and aerial manipulation [[112]](#ref-112).

### 2.5 Simulation for testing, not only for training

Sim-to-real is not only about learned policies. Two lines of work bear directly on DroneRanger's SITL-first plan.
- **Simulation-based testing of autopilot software.**
  - Timperley et al. studied 228 ArduPilot bug fixes. Only 10 needed physical hardware, so most bugs were reproducible in software-in-the-loop simulation, provided the tests swept configurations and inputs. Configuration (81 bugs) and environment, such as wind (22 bugs), mattered most [[113]](#ref-113).
  - Khatiri et al. reconstructed real PX4 flights in PX4 SITL/Gazebo and generated riskier neighbouring test cases. Repeated runs of the same simulation already differed noticeably, so simulator non-determinism alone limits replication [[114]](#ref-114).
  - Kose et al. compared real PX4 flight logs with default, untuned PX4 SITL in Gazebo. Vertical-acceleration variance was about ten times larger in reality (4.985 vs. 0.458), and maximum tilt was 72.1° vs. 24.0°. GPS and magnetometer fluctuations appeared only in reality. Airframes, PX4 versions and mission scales also differed, which confounds the comparison [[115]](#ref-115).
- **Staged validation pipelines.** Jiang et al. lay out software-in-the-loop, hardware-in-the-loop, controlled real-world and in-field stages for PX4-class drones [[34]](#ref-34).

Measuring transfer has also become a research topic in its own right.
- **The SRCC metric.** Kadian et al. defined the Sim-vs-Real Correlation Coefficient (SRCC): the correlation between methods' simulated and real performance. The simulator used in a navigation challenge had an SRCC of only 0.18 for success, because agents had learned to exploit imperfect collision handling and "slide" along walls. Tuning simulator parameters raised the SRCC to 0.844 [[15]](#ref-15).
- **Predictivity as a design target.** SIMPLER narrowed control and visual gaps without building full digital twins. Over more than 1,500 paired evaluations, its "visual matching" setup reached a Pearson correlation of 0.924 between simulated and real success rates [[116]](#ref-116). PolaRiS builds a splat environment from a 2–5 minute video scan and reaches an average correlation of about 0.9 with real performance [[16]](#ref-16).
- **Few real trials.** Two 2026 papers address DroneRanger's situation directly. One treats real-world performance estimation as a betting problem, to get more out of each real trial [[27]](#ref-27). RoboGauge showed that evaluating policies in a second simulator predicted real command tracking better than evaluating them in the training simulator: an error of 0.0558 against real data, vs. 0.0883 [[117]](#ref-117).
- **Factorized perturbations.** NavRL++ injected each perturbation separately: sensor noise, perception failure, input and action latency, and control-response mismatch. This measured how much each one costs [[19]](#ref-19).

### 2.6 Answer to Q1

In three decades, sim-to-real moved from "controllers built in simulation rarely work on robots" to routine zero-shot transfer for tasks whose physics can be modelled or randomized. The clearest successes are:
- legged and humanoid locomotion [[1]](#ref-1), [[90]](#ref-90);
- low-level quadrotor control [[2]](#ref-2), [[50]](#ref-50), [[93]](#ref-93);
- drone racing [[3]](#ref-3), [[63]](#ref-63).

Rigid-object manipulation [[23]](#ref-23), [[52]](#ref-52) and geometry-based navigation [[19]](#ref-19), [[97]](#ref-97) follow. The successful recipes share four ingredients:
1. a simulator calibrated by system identification, or by residual models fitted to a small amount of real data [[3]](#ref-3), [[4]](#ref-4), [[54]](#ref-54), [[92]](#ref-92);
2. randomization of whatever is still uncertain, including timing [[5]](#ref-5), [[6]](#ref-6);
3. inputs that look the same in simulation and in reality, through abstraction or privileged teacher–student training [[7]](#ref-7), [[8]](#ref-8), [[72]](#ref-72);
4. GPU-parallel training at scale [[9]](#ref-9), [[60]](#ref-60).

Since 2023 the field has added digital twins reconstructed from real images [[10]](#ref-10), [[11]](#ref-11), differentiable physics [[12]](#ref-12) and foundation-model tools [[13]](#ref-13), [[14]](#ref-14). It has also started to *measure* transfer, using correlations between simulated and real outcomes [[15]](#ref-15), [[16]](#ref-16), [[116]](#ref-116). For aerial robots the frontier has moved from motion-capture arenas to flight through forests and clutter at 7–10 m/s with onboard sensing [[7]](#ref-7), [[17]](#ref-17), [[18]](#ref-18). Many headline results still depend on motion capture, either for state or for calibration data [[3]](#ref-3), [[63]](#ref-63).

## 3. Question 2 — What are the latest challenges (2024–2026)?

The successes of Section 2 are real, but they cluster in well-instrumented settings. A 2026 view of the literature shows eleven challenges that are still open. They are ordered roughly by how directly they affect a small outdoor drone.

### 3.1 Perception is now the weakest link

Dynamics randomization and identification have made low-level control transfer fairly routine. Perception has not caught up.
- **The measured cost.** In NavRL++'s factorized study, perception failure caused the largest single drop in navigation success: more than 5 percentage points at every obstacle density. Input noise, latency and control mismatch each cost only about 1–3 points. All perturbations together cut success by more than 10 points, and by more than 15 in dense scenes, and they raised control effort about 2.5-fold [[19]](#ref-19).
- **Lighting and blur.** A GPS-denied visual-servoing system on a Jetson and PX4 worked in simulation but failed in real flight because of lighting changes and motion blur [[118]](#ref-118).
- **Baked-in lighting.** Even photorealistic reconstructions couple lighting with geometry, which led Lv et al. to make Gaussian splats relightable [[18]](#ref-18).

Reconstructed scenes do not remove the problem. A 2026 policy trained in splat reconstructions of real clutter reached 90% success in simulation but 80% in reality. Most of its real failures came from foliage swaying in the propeller downwash, which the simulator did not model [[99]](#ref-99). Another splat-trained gate-navigation policy fell from 9–10/10 successes in simulation to 6–7/10 on hardware [[98]](#ref-98).

Rendering realism is not the same as sensor realism. Probabilistic robotics has long modelled range sensors as a mixture: correct returns with noise, unexpected short readings, maximum-range failures and random outliers [[119]](#ref-119). The failure modes of real depth sensors, such as holes, minimum range, specular surfaces, thin structures and false matches [[120]](#ref-120), are rarely modelled. Most simulators return perfect depth: PX4's Gazebo camera model does, and so does the idealized OAK-D sensor configuration shipped with Aerial Gym [[76]](#ref-76), [[121]](#ref-121). The 2026 Annual Review of the reality gap makes the same observation in general form. Simulated sensor models are often "simple Gaussian noise", and the authors group perception and sensing with dynamics, actuation and system design as the four sources of the gap [[20]](#ref-20). Visual fidelity does not always matter most, though. In contact-rich pushing, physics gaps mattered more than visual ones [[26]](#ref-26).

### 3.2 System-level gaps: latency, timing, control stacks and integration

The newest systematic studies find the gap spread across the whole autonomy stack, not inside the policy.
- **Latency.** NavRL++ measured input latency of up to about 100 ms and action latency of up to about 40 ms on its robots. It had to randomize both during fine-tuning. Performance held above 10 Hz control, degraded slightly at 5 Hz, and dropped sharply at 2 Hz [[19]](#ref-19).
- **Decision rate.** Q-learning methods degrade as the decision period shrinks [[122]](#ref-122). In DroneRanger's own DQN, a 50 Hz decision rate prevented the policy from learning which way to turn, while 5 Hz worked [[123]](#ref-123).
- **Control stack.** When training replaces the autopilot with a simplified controller, the policy is tuned to a closed loop that does not exist on the vehicle. Cross-simulator or sim-to-sim checks are the recommended remedy [[19]](#ref-19), [[110]](#ref-110).
- **Integration.** Panerati et al. treat the vertical integration of heterogeneous hardware and software (autopilot, middleware, edge computer and network) as part of the reality gap [[111]](#ref-111). Delays, partial observability and system constraints also appear among the canonical challenges of real-world RL [[104]](#ref-104).

### 3.3 Physics that is still hard to model, especially outdoors

For multirotors the hard physics is aerodynamic. The first RL quadrotor controller to fly was trained in a deliberately simple simulator. Its authors named the gaps they had ignored: motor dynamics, ground effect, battery and weight changes, and wireless delay [[93]](#ref-93). Those effects are still the usual suspects.
- **Near the ground.** Ground effect is significant within about five rotor radii [[124]](#ref-124).
- **At speed and in wind.** Rotor drag and unsteady effects grow at speed [[68]](#ref-68), and wind is turbulent and site-specific [[21]](#ref-21).
- **Batteries.** Battery voltage sag changes the available thrust during a flight.

Learned residual models work well [[3]](#ref-3), [[57]](#ref-57), [[68]](#ref-68), but they need flight data with accurate ground truth. That usually means motion capture or a wind tunnel [[21]](#ref-21). Default autopilot simulators are optimistic too. In a 2026 comparison, real PX4 logs showed about ten times the vertical-acceleration variance of an untuned PX4 SITL run [[115]](#ref-115).

On legged and humanoid robots, the analogous problem is actuator and contact modelling. Recent humanoid work shows how stubborn this is:
- **Residual alignment is costly.** ASAP needed real rollouts to fit its residual action model. A full-body model would need hundreds of motion clips, the method relied on motion capture, and two robots were damaged along the way [[92]](#ref-92).
- **Power limits are missing from simulators.** In OmniXtreme, real failures on impulsive landings came from motor overcurrent, power limits and battery undervoltage. The authors note these "remain challenging to capture accurately in simulation" [[22]](#ref-22).
- **Unmodelled effects recur.** The legged-locomotion review lists motor heating, non-deterministic delays and policies that exploit simulator artefacts [[1]](#ref-1).
- **Correction needs per-task engineering.** An "unsupervised actuator net" learned corrective simulator torques from real data without torque sensing. It still needed a reference trajectory and engineering for each task [[125]](#ref-125).

Battery sag is the multirotor version of the same problem.

### 3.4 Dependence on privileged infrastructure

Many celebrated aerial results used motion capture: for state estimation during flight [[2]](#ref-2), [[50]](#ref-50), [[63]](#ref-63), [[66]](#ref-66), [[93]](#ref-93), [[96]](#ref-96), or for collecting the real data that calibrated the simulator [[3]](#ref-3). Results "in the wild" replace motion capture with onboard visual–inertial odometry, which drifts. Benchmarked VIO also behaves differently in closed-loop flight than on datasets [[7]](#ref-7), [[126]](#ref-126). Outdoors with GNSS alone, horizontal error of a metre or more is normal [[127]](#ref-127), [[128]](#ref-128). A 2025 survey of real-world deep RL concludes that, for quadrotors, most tests remain confined to controlled, obstacle-free indoor environments [[101]](#ref-101). The gap between a lab arena and an open field is itself a sim-to-real gap. It is the one most capstone-scale projects meet first.

### 3.5 Digital twins: promise and limits

Real-to-sim reconstruction is the most active direction of 2024–2026. It is also not a finished solution:
- **Static scenes.** A splat or radiance field captures one moment. Vegetation grows and moves, lighting changes through the day and the season, and dynamic agents are absent [[10]](#ref-10), [[18]](#ref-18).
- **Geometry and physics.** Reconstructions are photometric. Collision geometry, materials and contact properties must be added, and errors there become dynamics gaps.
- **Capture cost.** SOUS VIDE used hand-held video [[10]](#ref-10). Lv et al.'s outdoor forest scenes used camera, LiDAR and RTK capture [[18]](#ref-18).
- **Moving vegetation.** Foliage moving in the propeller downwash caused most real failures of a splat-trained clutter-flight policy [[99]](#ref-99).

The 2024–2026 manipulation and navigation twins report the same limits:
- **RialTo** needs accurate depth sensing, which fails on thin, transparent or reflective objects. It is limited to quasi-static tasks and takes about two days per task [[11]](#ref-11).
- **SplatSim** handles rigid bodies only, so no cloth, liquids or plants [[23]](#ref-23).
- **Vid2Sim** environments are slow to build [[81]](#ref-81).
- **PolaRiS** calls its system identification "relatively simplistic" [[16]](#ref-16).
- **Real-is-Sim** breaks under prolonged occlusion [[83]](#ref-83).

For a garden, the plants themselves are deformable objects that move in the wind.

### 3.6 Foundation models and generative simulation bring a new kind of gap

Generative models promise unlimited, diverse training and test data. Their gap is different in kind: physical *inconsistency*, rather than parameter error.
- **World-model developers' own caveats.** NVIDIA's Cosmos report says current world models "fall short as reliable simulators of the physical world". It cites missing object permanence, inaccurate contact dynamics and poor adherence to physics [[24]](#ref-24). Genie 3 keeps generated worlds consistent for a few minutes [[129]](#ref-129).
- **Realism is not physics.** Physical understanding in generative video models is "severely limited, and unrelated to visual realism" [[25]](#ref-25). Video models also tend to imitate the nearest training example rather than learn physical laws, so "scaling alone is insufficient" [[130]](#ref-130).
- **World models as evaluators.** These can work for ranking. A Veo-based simulator ranked eight policy checkpoints correctly against more than 1,600 real trials (Pearson 0.86), but it under-predicted absolute success and hallucinated during contact [[88]](#ref-88). WorldGym reached a correlation of 0.78 with real success [[89]](#ref-89). An interactive world simulator stayed stable for more than ten minutes, but policies scored slightly higher in it than in reality [[131]](#ref-131). A third model, Ctrl-World [[132]](#ref-132), mis-ranked policies in PolaRiS's comparison [[16]](#ref-16).
- **Co-training is fragile.** Maddukuri et al.'s best mix sampled 99% simulation data, and pushing it to 99.5–99.9% dropped success from 95% to 60% [[14]](#ref-14). Wei et al. found that gains plateau as simulation data grows, that real data sets the ceiling, and that perfectly rendered simulation can even hurt [[26]](#ref-26).
- **LLM-designed randomization is early.** DrEureka has no visual inputs and keeps its randomization fixed during training [[13]](#ref-13). Surveys add hallucination, and the compute and latency cost of LLM calls, as new failure modes [[133]](#ref-133). DARPA's TIAMAT programme argues that most current techniques assume a small gap and high-fidelity simulators. It aims instead for "abstract-to-real" transfer from many low-fidelity simulators [[134]](#ref-134).

For a semester-scale drone project, these tools are worth watching, not yet worth depending on.

### 3.7 Robustness versus performance, and choosing what to randomize

Domain randomization trades nominal performance for robustness. Randomized policies are consistently more robust than nominal ones, but the initial parameter guesses and variances are typically inaccurate [[6]](#ref-6). In quadrotor racing, wider ranges bought robustness at the cost of speed [[66]](#ref-66). Adaptive methods tune the ranges with real data [[55]](#ref-55), [[56]](#ref-56). Their price is the real data that the method is supposed to save. Valassakis et al. found that, once engineering effort is accounted for, simple random force injection matched elaborate methods [[67]](#ref-67). There is still no principled, task-independent rule for choosing ranges.

### 3.8 Evaluation and reproducibility

Sim-to-real claims are hard to compare:
- **Few trials.** Real-world trials are few and costly.
- **Unreported effort.** Engineering effort and task-specific tuning are often left out [[67]](#ref-67).
- **Simulation does not predict reality.** Simulated benchmarks may not predict real performance. Kadian et al.'s SRCC of 0.18 for an unmodified simulator is the cautionary example [[15]](#ref-15). Since 2024, sim-to-real correlation has been reported more often [[16]](#ref-16), [[116]](#ref-116). Correlations are setup-specific, though, and standard simulated benchmarks can correlate poorly with reality [[16]](#ref-16). The 2026 Annual Review lists the metrics now in use: SRCC, offline replay error, image-fidelity scores, and success and reward. It also lists calibrating the gap, so that simulation can be trusted for evaluation, as an open problem [[20]](#ref-20).

Choi et al. call for community-curated libraries of *validated* models and for simulation grand challenges. Among the field's nine barriers they list that "uncertainty is marginally handled" and that "model calibration can be tedious" [[44]](#ref-44).

### 3.9 Safety assurance of simulation-trained behaviour

A learned policy has no guarantee outside its training distribution, and the reality gap is exactly such a shift. The standard response is to wrap the policy in a filter:
- shields that override unsafe actions [[135]](#ref-135);
- control-barrier-function filters [[136]](#ref-136);
- velocity-obstacle or projection-based safety layers in recent aerial RL [[17]](#ref-17), [[97]](#ref-97).

These filters themselves depend on a model and on state estimates. A safety layer is only as good as the perception and estimation beneath it [[28]](#ref-28). Certification of learned flight control is still an open question.

### 3.10 Compute, tooling and the people cost of simulation

Photorealistic simulation has hardware requirements. NVIDIA states that Isaac Sim does not support GPUs without RT cores, such as the A100 and H100 [[137]](#ref-137). Simulators also differ widely in physics fidelity and features [[138]](#ref-138). Choi et al. note that building and maintaining a simulation platform takes broad multidisciplinary expertise and sustained software-development commitment [[44]](#ref-44). For a student team that turns over every semester, this "people gap" is real: versions drift, and undocumented simulator settings are lost.

### 3.11 Modelling other agents: people and animals

Simulating the humans or animals a robot interacts with is listed by Choi et al. as a barrier of its own [[44]](#ref-44). For wildlife the evidence is thin and variable:
- **Reactions vary.** Mammal reactions to drones depend on species, altitude and approach [[139]](#ref-139). A systematic review found that target-oriented flight provokes the strongest reactions [[140]](#ref-140).
- **Models need field data.** Herding models need interaction parameters measured with live birds [[141]](#ref-141).
- **Synthetic animals are only a start.** Simulated animals can train detectors [[142]](#ref-142). An RL deterrence supervisor trained against virtual deer has been proposed, but not yet evaluated [[143]](#ref-143).

A deterrence policy trained against simulated animals will face a behavioural reality gap that no physics engine can close.

### 3.12 Summary

**Table 3. Open sim-to-real challenges in 2026 and their relevance to DroneRanger.**

| Challenge | Status in 2026 | Most promising direction | Relevance to DroneRanger |
|---|---|---|---|
| Perception gap | Largest single factor in recent studies | Sensor-failure models, real-to-sim scenes, abstraction | High (depth interface, RL inputs) |
| Latency, timing, control stack | Recognized; handled by randomization and sim-to-sim checks | Measured delay models; real autopilot in the loop | High (serial link, custom RL controller) |
| Hard-to-model aerodynamics | Residual learning works with good ground truth | Small real datasets, online adaptation | High (ground effect, wind) |
| Infrastructure dependence | Many agile results still need motion capture | Onboard VIO/GNSS/RTK with measured error | High (garden, GNSS only) |
| Digital twins | Rapid progress; static and lighting-baked | Relightable, re-capturable splats with geometry | Medium (future garden twin) |
| Foundation and generative models | Emerging; physical consistency unproven | Co-training with real data; LLM-designed randomization | Low this semester |
| Randomization design | Heuristic | Adaptive methods with real data | Medium (Monte Carlo SITL) |
| Evaluation and reproducibility | Weak; few standard real benchmarks | Paired sim/real protocols, SRCC | High (CCWC claim) |
| Safety assurance | Filters and shields common; guarantees limited | Shields on top of validated estimation | High (any learned policy) |
| Other agents | Behaviour models unvalidated | Field-calibrated agent models | Future (deterrence) |

### 3.13 Answer to Q2

In 2026 the remaining gap lies less inside the policy than in the system around it:
- perception and sensor failure modes [[19]](#ref-19), [[20]](#ref-20);
- latency, decision rate and control-stack mismatch [[19]](#ref-19), [[111]](#ref-111);
- hard-to-model physics: aerodynamics, and actuator, power and battery limits [[21]](#ref-21), [[22]](#ref-22);
- the motion-capture and lab infrastructure that many successes quietly depend on.

The newest tools help but have limits. Digital twins are powerful but static and mostly rigid [[10]](#ref-10), [[23]](#ref-23). Generative world models are not yet physically consistent [[24]](#ref-24), [[25]](#ref-25). Co-training and LLM-designed randomization help, but they saturate or remain narrow [[13]](#ref-13), [[26]](#ref-26).

Evaluation is the weakest link. Sim–real predictivity is setup-specific, real trials are few, and engineering effort is under-reported [[15]](#ref-15), [[27]](#ref-27), [[67]](#ref-67). Safety filters help, but they inherit the errors of the models and estimates beneath them [[28]](#ref-28).

Every one of these challenges appears, at small scale, in DroneRanger (Section 4).

## 4. Question 3 — What DroneRanger can learn, and the challenges it is likely to meet

### 4.1 DroneRanger's simulation chain today

DroneRanger already runs four different simulation pipelines, and they do not share the same assumptions (Table 4). The CCWC paper's central claim is that one PX4–ROS 2 interface lets the same autonomy code run in SITL, HITL and flight, and that the architecture "enables reliable simulation-to-reality transfer" [[29]](#ref-29). The evidence offered for that claim is qualitative: behaviours that work in Gazebo and Unity scenes and early hardware runs. No position errors, latency distributions or multi-run statistics were reported. The authors listed those as future work [[29]](#ref-29). The Spring 2026 prototype then showed the gaps that simulation had hidden [[144]](#ref-144):
- setpoints reported as "reached" while the vehicle was visibly offset;
- about 0.5 m of altitude error near 1 m above ground;
- invalid depth regions and spurious readings near 34 m;
- a port conflict on the flight-controller link;
- an arcing power connector.

**Table 4. DroneRanger's simulation pipelines and what each one assumes.**

| Pipeline | Simulator and autopilot | Sensing assumed | Scene | Status (Oct 2026) |
|---|---|---|---|---|
| CCWC architecture (Spring 2026) | Gazebo 11 and Unity with PX4 SITL; a PyBullet node publishes IMU/GPS/odometry with configurable noise | Unity RGB-D and GPS; a Boolean "obstacle within safe distance" flag | Unity village with an animated deer target | Qualitative demonstrations [[29]](#ref-29) |
| Hardware-group SITL twin (Fall 2026, O0) | Gazebo (gz) `gz_x500_depth` with PX4 SITL in lockstep; optional `windy` world | Ideal depth image, 640×480 at 30 Hz, clipped at 0.2–19.1 m, **no noise model**; X500 with a 2.0 kg body and generic motor constants, **no ground effect** | Empty or default worlds; the garden is not modelled | Planned rehearsal for every mission [[45]](#ref-45), [[121]](#ref-121), [[145]](#ref-145) |
| RL training environment | Isaac Lab, three `TiledCamera` depth sensors; **a custom velocity–attitude–thrust PD controller instead of PX4** | Front and ±90° distances (73° FOV), capped at 10 m; ground hits removed with simulator ground truth; goal offset from simulator ground truth; 50 Hz decisions | Procedural obstacles, fixed altitude (2-D task) | DQN Stage 0/1 under development [[46]](#ref-46) |
| Isaac Sim + Pegasus | Isaac Sim 5.1 with Pegasus and PX4 SITL v1.14.3 over MAVLink HIL; ROS 2 Jazzy | RGB and depth 640×480 published on ROS 2 | "Rivermark" outdoor scene: buildings, roads, a parking lot | Infrastructure only, no policy connected [[146]](#ref-146) |

Three observations follow. First, only the SITL twin and the Pegasus setup keep the real autopilot, PX4 [[147]](#ref-147), in the loop. The RL environment replaces PX4 with its own controller, so its transfer problem includes a control-stack gap that NavRL++-style perturbation studies treat as a separate factor [[19]](#ref-19). Second, every pipeline renders perfect geometry. None of them reproduces the OAK-D Lite's failure modes:
- a minimum range of about 0.35 m in the 480p mode;
- zero-valued invalid pixels;
- error that grows with the square of distance;
- one-pixel false matches that read as about 33 m [[120]](#ref-120), [[148]](#ref-148).

Third, none of the scenes is a household garden. The Rivermark scene is a parking lot and the Gazebo worlds are empty, so the environment distribution the policies and missions are tested on is not the deployment distribution.

### 4.2 Gap audit for the Fall 2026 platform

Table 5 applies the taxonomy of Section 1.1 to the real vehicle. It combines the project's own measurements and specifications with the evidence reviewed in Sections 2 and 3.

**Table 5. Sim-to-real gaps expected for DroneRanger, with evidence and responses.**

| Gap | In simulation | On the real vehicle | Evidence and remedy from the literature | When |
|---|---|---|---|---|
| Vertical dynamics near the ground | No ground-effect term in the X500 model; ideal barometer; default SITL under-represents real vertical-acceleration variance about tenfold [[115]](#ref-115) | ~0.5 m altitude error near 1 m AGL in Spring 2026; ground effect matters up to ~5 rotor radii (≈0.64 m for 10-inch props); barometer dips from downwash | Learned ground-effect residuals made near-ground control stable [[57]](#ref-57); fuse a rangefinder and use PX4's barometer ground-effect compensation [[124]](#ref-124), [[149]](#ref-149) | O0–O1 |
| Mass, thrust and battery | 2.0 kg body, generic motor constant and 12.5 ms motor time constant [[121]](#ref-121) | Estimated all-up weight ≈2.1 kg with the Jetson and camera, hover throttle ≈55%, thrust-to-weight ≈2.5 falling as the 4S pack sags (estimates) | Identify the dynamics from logs before randomizing. About one minute of flight data can be enough, and a tool that reads PX4 ULogs exists [[30]](#ref-30)–[[32]](#ref-32). Then randomize only the residual uncertainty, by about 10–20% [[50]](#ref-50), [[66]](#ref-66) | O0 |
| Wind | Calm unless the `windy` world is used | At San Jose airport, 18–21% of autumn days have a gust ≥25 mph | Wind is the classic outdoor gap; learned adaptation needs only minutes of real data [[21]](#ref-21); gust models and randomization in SITL [[150]](#ref-150) | O1–O2 |
| GNSS and compass | Small, uncorrelated sensor noise | M10 receiver specified at 2.0 m CEP; multipath near houses and trees; magnetic interference from power wiring | Treat GNSS error as slowly varying bias, not white noise [[150]](#ref-150); GNSS-only hover stayed within 1.05 m (95%) vs. 0.35 m with RTK [[127]](#ref-127), [[128]](#ref-128) | O1–O2 |
| Depth perception | Noise-free depth (Gazebo, Isaac) | Invalid pixels, minimum range ≈0.35 m, false far readings, noise ∝ z²; rangefinder outputs 0 on unreliable returns | Perception failure was the largest single degradation factor in NavRL++ [[19]](#ref-19). Simulate the sensor's failure modes, not only its geometry [[7]](#ref-7), [[120]](#ref-120). Even Aerial Gym's OAK-D model is idealized [[76]](#ref-76) | O2 interface; future |
| Timing and latency | PX4 and Gazebo in lockstep; RL decisions at 50 Hz | USB-TTL serial link, XRCE-DDS agent, Jetson load, 30 Hz depth | Randomize input and action delays (0–100 ms and 0–40 ms in NavRL++) [[4]](#ref-4), [[5]](#ref-5), [[19]](#ref-19); decide at 5–10 Hz [[122]](#ref-122), [[123]](#ref-123) | O0 bench, RL |
| Control stack | Custom PD controller (RL env); policy acts at velocity level | PX4 cascaded control, Offboard heartbeat and failover semantics, Mission-mode smoothing [[151]](#ref-151) | Keep PX4's inner loops, and let the policy send velocity setpoints, which transfer more easily than motor commands [[30]](#ref-30), [[94]](#ref-94), [[97]](#ref-97). Validate sim-to-sim in PX4 SITL first [[19]](#ref-19), [[33]](#ref-33), [[110]](#ref-110) | RL hand-over |
| Scene and appearance | Parking lot or empty world | Lawn, flower beds, fences, thin branches, changing light and season | Digital twins from phone video [[10]](#ref-10); relightable splats for lighting [[18]](#ref-18). Scenes are static and must be re-captured, and foliage moving in downwash defeated a splat-trained policy [[99]](#ref-99) | Future |
| Software integration | One interface by design | NED/FRD vs ENU/FLU frames, QoS mismatches, PX4 v1.16+ versioned topics, port conflicts | Vertical integration is part of the gap [[111]](#ref-111). Stage the testing SIL→HIL→field [[34]](#ref-34). Simulation reproduces most, but not all, autopilot bugs [[113]](#ref-113), and replaying real logs in SITL builds realistic tests [[114]](#ref-114) | O0 |
| Evaluation | Ground-truth state available | Only the EKF2 estimate onboard | Sim metrics can fail to predict real ones (SRCC 0.18) until the simulator is tuned (0.844) [[15]](#ref-15); measure against independent truth | O0–O2 |
| Other agents (wildlife) | Scripted deer in Unity | Animal reactions depend on species, altitude and approach | Reaction thresholds vary widely [[139]](#ref-139), [[140]](#ref-140); herding models need parameters measured on live animals [[141]](#ref-141); rehearse in simulation, validate in the field [[152]](#ref-152) | Future |

### 4.3 Lessons for DroneRanger

**L1. Make "sim-to-real" a measured quantity.** The literature that succeeded quantified its gap; the CCWC paper did not. For DroneRanger, every O0 mission file and PX4 parameter file should be run in SITL and then flown unchanged. Both runs should be scored on the same metrics against independent truth. Kadian et al. show why this matters: their simulator ranked methods in a way that did not hold on the robot until simulator parameters were corrected [[15]](#ref-15). A pre-registered sim-vs-real comparison table is the cheapest credible replacement for the phrase "reliable sim-to-real transfer".

**L2. Calibrate before randomizing.** System identification came before randomization in the most reliable transfers, from legged robots (actuator models, measured latency) [[4]](#ref-4), [[54]](#ref-54) to drone racing (residual models fitted to real data) [[3]](#ref-3). Gronauer et al. showed the same for small quadrotors: fitting the motor time constant and latency to real flight data made zero-shot transfer work [[30]](#ref-30). Eschmann et al. identified a quadrotor's thrust curve, inertia and motor delay from about one minute of flight data, with a tool that reads PX4 ULog files directly [[31]](#ref-31). The hardware group's equivalent is concrete:
- weigh the aircraft;
- let PX4's hover-thrust estimator converge and copy the value into the Gazebo model;
- fit the motor time constant and thrust coefficient from a step test in the logs;
- measure IMU, barometer and GNSS noise at rest and in hover.

Quan's textbook gives the parameter-measurement and sensor-model procedures for multicopters [[32]](#ref-32). Its companion practice book turns them into Pixhawk-based experiments, from dynamic modelling and sensor calibration to failsafe-logic design [[153]](#ref-153).

**L3. Randomize what remains uncertain, and test the mission, not only the policy.** Domain randomization is usually discussed for learned policies [[5]](#ref-5), [[6]](#ref-6), [[48]](#ref-48), but the same idea hardens a scripted Mission-mode patrol. Moderate ranges, about 10–20% around identified values, worked best for quadrotors; wider ranges cost performance [[50]](#ref-50), [[66]](#ref-66). Monte Carlo SITL runs should vary wind (`windy` world), mass (±10–20%), GNSS bias, magnetometer offset and link delay. Their output is the distribution of geofence margin, waypoint error and battery use, not a single pass/fail.

**L4. Keep the real stack in the loop for as long as possible.** Every simplified component in the loop is a new gap. The ladder goes from PX4 SITL with the flight parameter file, to simulation-in-hardware (SIH) on the Pixhawk with the Jetson and serial link attached [[33]](#ref-33), to propeller-off bench tests, and then to tethered or low-altitude flight. This is the staged pipeline of Jiang et al. [[34]](#ref-34) and the original CCWC plan [[29]](#ref-29). For the RL policy, a sim-to-sim step (Isaac Lab controller → PX4 SITL through Pegasus or Gazebo) exposes the controller gap before any hardware is involved [[19]](#ref-19), [[110]](#ref-110). RoboGauge found that a second simulator predicted real performance better than the training simulator [[117]](#ref-117). The policy should command velocities and leave the inner loops to PX4. That is the level at which learned aerial policies have transferred most reliably [[30]](#ref-30), [[94]](#ref-94), [[97]](#ref-97). Neural-Fly's outdoor tests used the same hardware split as DroneRanger: a Pixhawk running PX4 in Offboard mode, under a companion computer that ran the learned controller at 50 Hz [[21]](#ref-21).

**L5. Choose abstractions that transfer, and define what "invalid" means.** Policies that consume depth or other intermediate representations transfer better than policies that consume raw pixels [[7]](#ref-7), [[72]](#ref-72), [[73]](#ref-73). The CCWC warning grid is such an abstraction [[29]](#ref-29). It must still encode invalid depth as "unknown", never as "far", because the closest obstacles are exactly the ones a stereo camera cannot measure. The RL observation should carry the same convention, plus the yaw rate and speed that make it Markov.

**L6. Put safety outside the parts that are least validated.** Learned or simulation-tuned behaviour should sit under an independent supervisor: the PX4 geofence and failsafes, an RC kill switch, and for any learned policy a shield or barrier-function filter [[28]](#ref-28), [[135]](#ref-135), [[136]](#ref-136). Recent aerial RL systems use exactly this pattern [[17]](#ref-17), [[97]](#ref-97).

**L7. Treat each real flight as data for the simulator.** Swift fitted its residual models to a handful of real runs; its dynamics residual used fewer than a thousand samples [[3]](#ref-3). Neural-Fly learned its wind representation from about 12 minutes of flight [[21]](#ref-21). Every DroneRanger flight should therefore log:
- the ULog;
- a rosbag of the depth stream and odometry;
- the parameter file;
- the wind reading;
- the ground-truth references (ground markers, or RTK if funded).

**L8. Plan the garden digital twin as future work, with its limits in view.** Gaussian-splatting twins built from a few minutes of phone video now train visual policies that transfer zero-shot [[10]](#ref-10), and relighting addresses part of the appearance gap [[18]](#ref-18). A splat is still a static snapshot. Lawns grow, leaves move in wind, and light changes through the day and the season, so the twin must be re-captured and validated. Capture must also stay inside the host property, for the same privacy reasons that constrain the camera in flight [[47]](#ref-47).

**L9. Do not over-claim.** Many celebrated sim-to-real results depend on motion capture, controlled arenas or extensive engineering [[3]](#ref-3), [[67]](#ref-67). Statements about DroneRanger should name the conditions under which transfer was measured: site, wind, lighting, number of trials and the source of truth.

### 4.4 Challenges the project is likely to meet this semester

**Table 6. Sim-to-real risk register for O0–O2 (likelihood/impact: H high, M medium, L low).**

| # | Challenge | L/I | Early warning | Mitigation |
|---|---|---|---|---|
| R1 | SITL missions are perfect, but outdoor waypoints miss by metres | H/M | Estimate says "reached" while the aircraft is visibly off the marker | Judge success against surveyed markers; set tolerances above the GNSS error; RTK if funded [[127]](#ref-127) |
| R2 | Altitude hold, take-off and landing behave differently near the ground | H/M | Barometer dips at take-off/landing; climb-back on landing | TFmini Plus fused in EKF2; ground-effect compensation; log the rangefinder unfused first [[124]](#ref-124), [[149]](#ref-149) |
| R3 | Wind degrades tracking and battery life beyond SITL predictions | M/H | Larger tilt and throttle in logs; shorter flights | Rehearse in the `windy` world; gust go/no-go limit; morning slots |
| R4 | Compass interference or GNSS multipath near the house | M/H | EKF2 innovation warnings; yaw drift; position jumps | GPS mast; compass calibration with the payload powered; site survey before O2 |
| R5 | Link latency, jitter or drop-outs absent in lockstep SITL | M/M | XRCE-DDS gaps; Offboard heartbeat warnings | SIH bench test with the real link; latency audit [[154]](#ref-154); heartbeat monitoring |
| R6 | Battery sag shortens flights and reduces control margin | M/M | Voltage under load; hover throttle creeping up | Conservative failsafes; plan 8–10 min flights; log energy per lap |
| R7 | Outdoor depth artifacts (low-texture lawn, sky, thin branches, glare, foliage moving in downwash [[99]](#ref-99)) | M/L for O2 | High invalid-pixel fraction; false near or far readings | Characterize the depth interface; invalid means unknown; not on the O2 critical path |
| R8 | Few real flights (approval lead time, rain, short days) | H/H | Calendar slips; cancelled test days | Pre-written test cards; maximize data per flight (L7); December buffer |
| R9 | Version drift between the simulated and the real stack | M/M | Topics present in SITL but silent on the vehicle | Pin PX4, `px4_msgs` and JetPack versions; one parameter file for both [[155]](#ref-155) |
| R10 | RL policy hand-over fails on PX4 | H/M | Oscillation or overshoot in PX4 SITL | Interface control document; sim-to-sim in PX4 SITL; shadow mode only this semester [[19]](#ref-19) |
| R11 | Compute limits block photorealistic simulation | M/L | Isaac Sim will not render on the H200 or the 8 GB laptop GPU | Gazebo SITL for the hardware group; RTX-class nodes for camera-based RL [[137]](#ref-137) |

### 4.5 A sim-vs-real validation protocol for O0–O2

**Table 7. Paired sim/real measurements that turn transfer into numbers.**

| Metric | SITL procedure | Real procedure | Truth source | Report |
|---|---|---|---|---|
| Hover hold, 60 s at 2 m | Calm and `windy` worlds | Calm morning, then ≤15 mph | TFmini (height); ground markers or RTK (horizontal) | RMSE per axis, sim vs. real, ≥10 trials |
| Altitude step 1 m → 3 m | Same parameter file | Same | TFmini | Rise time, overshoot, settling |
| Waypoint loop (≥4 waypoints + RTL) | Same mission file, Monte Carlo over wind, mass and GNSS bias | Garden (O2) | Surveyed markers | Cross-track error, lap time, energy per lap, geofence margin |
| Failsafes (RC loss, geofence, low battery, Offboard loss) | All triggered in SITL | Triggered in the field where safe | Logged mode transitions | Trigger latency and behaviour, 100% verified |
| Link timing | Not represented in lockstep | Jetson ↔ Pixhawk over TELEM2 | Offset/skew estimator [[154]](#ref-154) | Latency and jitter distribution |
| Depth interface | Gazebo ideal depth | OAK-D Lite at 1, 2 and 3 m targets, sun and shade | Tape measure | Invalid-pixel fraction, bias and spread |

If several conditions are flown, for example calm vs. windy or two gain sets, the rank correlation between sim and real outcomes is a direct, small-sample version of Kadian et al.'s Sim-vs-Real Correlation Coefficient [[15]](#ref-15).

## 5. Conclusion

The sim-to-real literature has moved from treating simulation as a substitute for reality to treating it as an instrument. A simulator is useful when three things are true [[20]](#ref-20), [[44]](#ref-44):
- it has been calibrated against the real system;
- its remaining uncertainty is randomized;
- its predictions are checked against measurements.

DroneRanger's architecture already has the hardest piece: one interface that runs unchanged in simulation and in flight [[29]](#ref-29). What it lacks is the instrumentation that would let it *show* transfer:
- a calibrated X500 model;
- sensor models with realistic failure modes;
- a timing model of the Jetson–Pixhawk link;
- paired sim and real measurements against independent truth.

These are hardware-group deliverables this semester. They are also the foundation that the RL group's policy and, later, learned wildlife deterrence will need [[47]](#ref-47). The practical rule for the semester: no mission flies without passing SITL first, and no SITL result is reported without its real-world counterpart.

### Limitations of this review

- **Not systematic.** This is a narrative review: the search was wide but not exhaustive.
- **Preprints.** Several of the most relevant 2025–2026 works are preprints; they are labelled as such.
- **Vendor claims.** Claims about simulators such as Genesis and Newton come from their developers and have not been independently validated.
- **Estimated project figures.** DroneRanger numbers taken from project notes (all-up weight, hover throttle, wind statistics) are estimates until measured on the vehicle.

## References

*IEEE style, numbered in order of first citation. Journal articles were resolved through LibKey (Northeastern University Library); conference papers, chapters and books were checked against Crossref, PMLR or arXiv. Access links, peer-review status and BibTeX are in [references.md](references.md) and [references.bib](references.bib).*

<a id="ref-1"></a>[1] S. Ha, J. Lee, M. van de Panne, Z. Xie, W. Yu, and M. Khadiv, “Learning-based legged locomotion: State of the art and future perspectives,” *Int. J. Robot. Res.*, vol. 44, no. 8, pp. 1396–1427, Jul. 2025, doi: 10.1177/02783649241312698.  
<a id="ref-2"></a>[2] J. Eschmann, D. Albani, and G. Loianno, “Learning to fly in seconds,” *IEEE Robot. Autom. Lett.*, vol. 9, no. 7, pp. 6336–6343, Jul. 2024, doi: 10.1109/LRA.2024.3396025.  
<a id="ref-3"></a>[3] E. Kaufmann, L. Bauersfeld, A. Loquercio, M. Müller, V. Koltun, and D. Scaramuzza, “Champion-level drone racing using deep reinforcement learning,” *Nature*, vol. 620, no. 7976, pp. 982–987, Aug. 2023, doi: 10.1038/s41586-023-06419-4.  
<a id="ref-4"></a>[4] J. Tan *et al.*, “Sim-to-real: Learning agile locomotion for quadruped robots,” in *Proc. Robot.: Sci. Syst. (RSS)*, 2018, doi: 10.15607/RSS.2018.XIV.010.  
<a id="ref-5"></a>[5] X. B. Peng, M. Andrychowicz, W. Zaremba, and P. Abbeel, “Sim-to-real transfer of robotic control with dynamics randomization,” in *Proc. IEEE Int. Conf. Robot. Autom. (ICRA)*, 2018, pp. 3803–3810, doi: 10.1109/ICRA.2018.8460528.  
<a id="ref-6"></a>[6] F. Muratore, F. Ramos, G. Turk, W. Yu, M. Gienger, and J. Peters, “Robot learning from randomized simulations: A review,” *Front. Robot. AI*, vol. 9, Art. no. 799893, Apr. 2022, doi: 10.3389/frobt.2022.799893.  
<a id="ref-7"></a>[7] A. Loquercio, E. Kaufmann, R. Ranftl, M. Müller, V. Koltun, and D. Scaramuzza, “Learning high-speed flight in the wild,” *Sci. Robot.*, vol. 6, no. 59, Art. no. eabg5810, Oct. 2021, doi: 10.1126/scirobotics.abg5810.  
<a id="ref-8"></a>[8] D. Chen, B. Zhou, V. Koltun, and P. Krähenbühl, “Learning by cheating,” in *Proc. Conf. Robot Learn. (CoRL)*, ser. Proc. Mach. Learn. Res., vol. 100, 2020, pp. 66–75. [Online]. Available: https://proceedings.mlr.press/v100/chen20a.html  
<a id="ref-9"></a>[9] N. Rudin, D. Hoeller, P. Reist, and M. Hutter, “Learning to walk in minutes using massively parallel deep reinforcement learning,” in *Proc. Conf. Robot Learn. (CoRL)*, ser. Proc. Mach. Learn. Res., vol. 164, 2022, pp. 91–100. [Online]. Available: https://proceedings.mlr.press/v164/rudin22a.html  
<a id="ref-10"></a>[10] J. Low, M. Adang, J. Yu, K. Nagami, and M. Schwager, “SOUS VIDE: Cooking visual drone navigation policies in a Gaussian splatting vacuum,” *IEEE Robot. Autom. Lett.*, vol. 10, no. 5, pp. 5122–5129, May 2025, doi: 10.1109/LRA.2025.3553785.  
<a id="ref-11"></a>[11] M. Torne Villasevil *et al.*, “Reconciling reality through simulation: A real-to-sim-to-real approach for robust manipulation,” in *Proc. Robot.: Sci. Syst. (RSS)*, 2024, doi: 10.15607/RSS.2024.XX.015.  
<a id="ref-12"></a>[12] Y. Zhang, Y. Hu, Y. Song, D. Zou, and W. Lin, “Learning vision-based agile flight via differentiable physics,” *Nat. Mach. Intell.*, vol. 7, no. 6, pp. 954–966, Jun. 2025, doi: 10.1038/s42256-025-01048-0.  
<a id="ref-13"></a>[13] Y. J. Ma *et al.*, “DrEureka: Language model guided sim-to-real transfer,” in *Proc. Robot.: Sci. Syst. (RSS)*, 2024, doi: 10.15607/RSS.2024.XX.094.  
<a id="ref-14"></a>[14] A. Maddukuri *et al.*, “Sim-and-real co-training: A simple recipe for vision-based robotic manipulation,” in *Proc. Robot.: Sci. Syst. (RSS)*, 2025, doi: 10.15607/RSS.2025.XXI.109.  
<a id="ref-15"></a>[15] A. Kadian *et al.*, “Sim2Real predictivity: Does evaluation in simulation predict real-world performance?” *IEEE Robot. Autom. Lett.*, vol. 5, no. 4, pp. 6670–6677, Oct. 2020, doi: 10.1109/LRA.2020.3013848.  
<a id="ref-16"></a>[16] A. Jain *et al.*, “PolaRiS: Scalable real-to-sim evaluations for generalist robot policies,” in *Proc. Robot.: Sci. Syst. (RSS)*, 2026, doi: 10.15607/RSS.2026.XXII.062.  
<a id="ref-17"></a>[17] J. Zhang *et al.*, “High-speed vision-based flight in clutter with safety-shielded reinforcement learning,” *IEEE Robot. Autom. Lett.*, vol. 11, no. 8, pp. 9559–9566, Aug. 2026, doi: 10.1109/LRA.2026.3703580.  
<a id="ref-18"></a>[18] Z. Lv, Y. Qian, C. Sang, H. Liu, D. Zou, and M. Yang, “Zero-shot UAV navigation in forests via relightable 3D Gaussian splatting,” Feb. 2026, arXiv:2602.07101.  
<a id="ref-19"></a>[19] Z. Xu, H. Jin, and K. Shimada, “NavRL++: A system-level framework for improving sim-to-real transfer in reinforcement learning-based robot navigation,” May 2026, arXiv:2605.15559.  
<a id="ref-20"></a>[20] E. Aljalbout *et al.*, “The reality gap in robotics: Challenges, solutions, and best practices,” *Annu. Rev. Control Robot. Auton. Syst.*, vol. 9, no. 1, pp. 403–432, May 2026, doi: 10.1146/annurev-control-031924-100130.  
<a id="ref-21"></a>[21] M. O'Connell *et al.*, “Neural-Fly enables rapid learning for agile flight in strong winds,” *Sci. Robot.*, vol. 7, no. 66, Art. no. eabm6597, May 2022, doi: 10.1126/scirobotics.abm6597.  
<a id="ref-22"></a>[22] Y. Wang *et al.*, “OmniXtreme: Breaking the generality barrier in high-dynamic humanoid control,” in *Proc. Robot.: Sci. Syst. (RSS)*, 2026, doi: 10.15607/RSS.2026.XXII.031.  
<a id="ref-23"></a>[23] M. N. Qureshi, S. Garg, F. Yandun, D. Held, G. Kantor, and A. Silwal, “SplatSim: Zero-shot sim2real transfer of RGB manipulation policies using Gaussian splatting,” in *Proc. IEEE Int. Conf. Robot. Autom. (ICRA)*, 2025, pp. 6502–6509, doi: 10.1109/ICRA55743.2025.11128339.  
<a id="ref-24"></a>[24] N. Agarwal *et al.*, “Cosmos world foundation model platform for physical AI,” Jan. 2025, arXiv:2501.03575.  
<a id="ref-25"></a>[25] S. Motamed, L. Culp, K. Swersky, P. Jaini, and R. Geirhos, “Do generative video models understand physical principles?” in *Proc. IEEE/CVF Winter Conf. Appl. Comput. Vis. (WACV)*, 2026, pp. 948–958, doi: 10.1109/WACV61042.2026.00099.  
<a id="ref-26"></a>[26] A. Wei, A. Agarwal, B. Chen, R. Bosworth, N. Pfaff, and R. Tedrake, “Empirical analysis of sim-and-real cotraining of diffusion policies for planar pushing from pixels,” in *Proc. IEEE/RSJ Int. Conf. Intell. Robots Syst. (IROS)*, 2025, pp. 5625–5632, doi: 10.1109/IROS60139.2025.11246304.  
<a id="ref-27"></a>[27] Y. Chen, Z. Mahboob, and B. Weng, “Betting for sim-to-real performance evaluation,” in *Proc. Robot.: Sci. Syst. (RSS)*, 2026, doi: 10.15607/RSS.2026.XXII.090.  
<a id="ref-28"></a>[28] L. Brunke *et al.*, “Safe learning in robotics: From learning-based control to safe reinforcement learning,” *Annu. Rev. Control Robot. Auton. Syst.*, vol. 5, pp. 411–444, May 2022, doi: 10.1146/annurev-control-042920-020211.  
<a id="ref-29"></a>[29] Z. Ling *et al.*, “DroneRanger: Simulation-guided UAV framework for autonomous wildlife deterrence,” in *Proc. IEEE 16th Annu. Comput. Commun. Workshop Conf. (CCWC)*, 2026, pp. 1221–1227, doi: 10.1109/CCWC67433.2026.11393823.  
<a id="ref-30"></a>[30] S. Gronauer, M. Kissel, L. Sacchetto, M. Korte, and K. Diepold, “Using simulation optimization to improve zero-shot policy transfer of quadrotors,” in *Proc. IEEE/RSJ Int. Conf. Intell. Robots Syst. (IROS)*, 2022, pp. 10170–10176, doi: 10.1109/IROS47612.2022.9981229.  
<a id="ref-31"></a>[31] J. Eschmann, D. Albani, and G. Loianno, “Data-driven system identification of quadrotors subject to motor delays,” in *Proc. IEEE/RSJ Int. Conf. Intell. Robots Syst. (IROS)*, 2024, pp. 8095–8102, doi: 10.1109/IROS58592.2024.10801441.  
<a id="ref-32"></a>[32] Q. Quan, *Introduction to Multicopter Design and Control*. Singapore: Springer, 2017, doi: 10.1007/978-981-10-3382-7.  
<a id="ref-33"></a>[33] PX4 Autopilot, “SIH on flight controller hardware,” *PX4 User Guide (main)*. Accessed: Sep. 27, 2026. [Online]. Available: https://docs.px4.io/main/en/sim_sih/hardware.html  
<a id="ref-34"></a>[34] Y. Jiang *et al.*, “A step-by-step guide to creating a robust autonomous drone testing pipeline,” Jun. 2025, arXiv:2506.11400.  
<a id="ref-35"></a>[35] R. A. Brooks, “Artificial life and real robots,” in *Toward a Practice of Autonomous Systems: Proc. 1st Eur. Conf. Artificial Life*, F. J. Varela and P. Bourgine, Eds. Cambridge, MA, USA: MIT Press, 1992, pp. 3–10.  
<a id="ref-36"></a>[36] N. Jakobi, P. Husbands, and I. Harvey, “Noise and the reality gap: The use of simulation in evolutionary robotics,” in *Advances in Artificial Life (ECAL 1995)*, ser. Lecture Notes in Computer Science, vol. 929. Berlin, Germany: Springer, 1995, pp. 704–720, doi: 10.1007/3-540-59496-5_337.  
<a id="ref-37"></a>[37] S. Koos, J.-B. Mouret, and S. Doncieux, “The transferability approach: Crossing the reality gap in evolutionary robotics,” *IEEE Trans. Evol. Comput.*, vol. 17, no. 1, pp. 122–145, Feb. 2013, doi: 10.1109/TEVC.2012.2185849.  
<a id="ref-38"></a>[38] J.-B. Mouret and K. Chatzilygeroudis, “20 years of reality gap: A few thoughts about simulators in evolutionary robotics,” in *Proc. Genet. Evol. Comput. Conf. Companion (GECCO)*, 2017, pp. 1121–1124, doi: 10.1145/3067695.3082052.  
<a id="ref-39"></a>[39] R. S. Sutton and A. G. Barto, *Reinforcement Learning: An Introduction*, 2nd ed. Cambridge, MA, USA: MIT Press, 2018.  
<a id="ref-40"></a>[40] J. Kober, J. A. Bagnell, and J. Peters, “Reinforcement learning in robotics: A survey,” *Int. J. Robot. Res.*, vol. 32, no. 11, pp. 1238–1274, Sep. 2013, doi: 10.1177/0278364913495721.  
<a id="ref-41"></a>[41] W. Zhao, J. Peña Queralta, and T. Westerlund, “Sim-to-real transfer in deep reinforcement learning for robotics: A survey,” in *Proc. IEEE Symp. Ser. Comput. Intell. (SSCI)*, 2020, pp. 737–744, doi: 10.1109/SSCI47803.2020.9308468.  
<a id="ref-42"></a>[42] S. Höfer *et al.*, “Sim2Real in robotics and automation: Applications and challenges,” *IEEE Trans. Autom. Sci. Eng.*, vol. 18, no. 2, pp. 398–400, Apr. 2021, doi: 10.1109/TASE.2021.3064065.  
<a id="ref-43"></a>[43] E. Salvato, G. Fenu, E. Medvet, and F. A. Pellegrino, “Crossing the reality gap: A survey on sim-to-real transferability of robot controllers in reinforcement learning,” *IEEE Access*, vol. 9, pp. 153171–153187, 2021, doi: 10.1109/ACCESS.2021.3126658.  
<a id="ref-44"></a>[44] H. Choi *et al.*, “On the use of simulation in robotics: Opportunities, challenges, and suggestions for moving forward,” *Proc. Natl. Acad. Sci. USA*, vol. 118, no. 1, Art. no. e1907856118, Jan. 2021, doi: 10.1073/pnas.1907856118.  
<a id="ref-45"></a>[45] J. Zha, “Project charter: DroneRanger hardware,” CS 7980 Research Capstone, Northeastern Univ., San Jose, CA, USA, Project charter, Sep. 2026.  
<a id="ref-46"></a>[46] RipZou, “Drone-Ranger-RL,” GitHub repository, commit aa9c597, Sep. 2026. [Online]. Available: https://github.com/RipZou/Drone-Ranger-RL  
<a id="ref-47"></a>[47] J. Zha, “From simulation-guided autonomy to a field-ready platform: A literature review for DroneRanger, Fall 2026,” CS 7980 Research Capstone, Northeastern Univ., San Jose, CA, USA, Course report, Oct. 2026.  
<a id="ref-48"></a>[48] J. Tobin, R. Fong, A. Ray, J. Schneider, W. Zaremba, and P. Abbeel, “Domain randomization for transferring deep neural networks from simulation to the real world,” in *Proc. IEEE/RSJ Int. Conf. Intell. Robots Syst. (IROS)*, 2017, pp. 23–30, doi: 10.1109/IROS.2017.8202133.  
<a id="ref-49"></a>[49] F. Sadeghi and S. Levine, “CAD2RL: Real single-image flight without a single real image,” in *Proc. Robot.: Sci. Syst. (RSS)*, 2017, doi: 10.15607/RSS.2017.XIII.034.  
<a id="ref-50"></a>[50] A. Molchanov, T. Chen, W. Hönig, J. A. Preiss, N. Ayanian, and G. S. Sukhatme, “Sim-to-(multi)-real: Transfer of low-level robust control policies to multiple quadrotors,” in *Proc. IEEE/RSJ Int. Conf. Intell. Robots Syst. (IROS)*, 2019, pp. 59–66, doi: 10.1109/IROS40897.2019.8967695.  
<a id="ref-51"></a>[51] A. Loquercio, E. Kaufmann, R. Ranftl, A. Dosovitskiy, V. Koltun, and D. Scaramuzza, “Deep drone racing: From simulation to reality with domain randomization,” *IEEE Trans. Robot.*, vol. 36, no. 1, pp. 1–14, Feb. 2020, doi: 10.1109/TRO.2019.2942989.  
<a id="ref-52"></a>[52] M. Andrychowicz *et al.*, “Learning dexterous in-hand manipulation,” *Int. J. Robot. Res.*, vol. 39, no. 1, pp. 3–20, Jan. 2020, doi: 10.1177/0278364919887447.  
<a id="ref-53"></a>[53] I. Akkaya *et al.*, “Solving Rubik's cube with a robot hand,” Oct. 2019, arXiv:1910.07113.  
<a id="ref-54"></a>[54] J. Hwangbo *et al.*, “Learning agile and dynamic motor skills for legged robots,” *Sci. Robot.*, vol. 4, no. 26, Art. no. eaau5872, Jan. 2019, doi: 10.1126/scirobotics.aau5872.  
<a id="ref-55"></a>[55] Y. Chebotar *et al.*, “Closing the sim-to-real loop: Adapting simulation randomization with real world experience,” in *Proc. IEEE Int. Conf. Robot. Autom. (ICRA)*, 2019, pp. 8973–8979, doi: 10.1109/ICRA.2019.8793789.  
<a id="ref-56"></a>[56] F. Ramos, R. Possas, and D. Fox, “BayesSim: Adaptive domain randomization via probabilistic inference for robotics simulators,” in *Proc. Robot.: Sci. Syst. (RSS)*, 2019, doi: 10.15607/RSS.2019.XV.029.  
<a id="ref-57"></a>[57] G. Shi *et al.*, “Neural Lander: Stable drone landing control using learned dynamics,” in *Proc. IEEE Int. Conf. Robot. Autom. (ICRA)*, 2019, pp. 9784–9790, doi: 10.1109/ICRA.2019.8794351.  
<a id="ref-58"></a>[58] J. Lee, J. Hwangbo, L. Wellhausen, V. Koltun, and M. Hutter, “Learning quadrupedal locomotion over challenging terrain,” *Sci. Robot.*, vol. 5, no. 47, Art. no. eabc5986, Oct. 2020, doi: 10.1126/scirobotics.abc5986.  
<a id="ref-59"></a>[59] A. Kumar, Z. Fu, D. Pathak, and J. Malik, “RMA: Rapid motor adaptation for legged robots,” in *Proc. Robot.: Sci. Syst. (RSS)*, 2021, doi: 10.15607/RSS.2021.XVII.011.  
<a id="ref-60"></a>[60] V. Makoviychuk *et al.*, “Isaac Gym: High performance GPU-based physics simulation for robot learning,” Aug. 2021, arXiv:2108.10470. NeurIPS 2021 Datasets and Benchmarks Track.  
<a id="ref-61"></a>[61] M. Mittal *et al.*, “Orbit: A unified simulation framework for interactive robot learning environments,” *IEEE Robot. Autom. Lett.*, vol. 8, no. 6, pp. 3740–3747, Jun. 2023, doi: 10.1109/LRA.2023.3270034.  
<a id="ref-62"></a>[62] T. Miki, J. Lee, J. Hwangbo, L. Wellhausen, V. Koltun, and M. Hutter, “Learning robust perceptive locomotion for quadrupedal robots in the wild,” *Sci. Robot.*, vol. 7, no. 62, Art. no. eabk2822, Jan. 2022, doi: 10.1126/scirobotics.abk2822.  
<a id="ref-63"></a>[63] Y. Song, A. Romero, M. Müller, V. Koltun, and D. Scaramuzza, “Reaching the limit in autonomous racing: Optimal control versus reinforcement learning,” *Sci. Robot.*, vol. 8, no. 82, Art. no. eadg1462, Sep. 2023, doi: 10.1126/scirobotics.adg1462.  
<a id="ref-64"></a>[64] B. Mildenhall, P. P. Srinivasan, M. Tancik, J. T. Barron, R. Ramamoorthi, and R. Ng, “NeRF: Representing scenes as neural radiance fields for view synthesis,” *Commun. ACM*, vol. 65, no. 1, pp. 99–106, Jan. 2022, doi: 10.1145/3503250.  
<a id="ref-65"></a>[65] B. Kerbl, G. Kopanas, T. Leimkühler, and G. Drettakis, “3D Gaussian splatting for real-time radiance field rendering,” *ACM Trans. Graph.*, vol. 42, no. 4, Art. no. 139, Aug. 2023, doi: 10.1145/3592433.  
<a id="ref-66"></a>[66] R. Ferede, T. Blaha, E. Lucassen, C. De Wagter, and G. C. H. E. de Croon, “One net to rule them all: Domain randomization in quadcopter racing across different platforms,” in *Proc. IEEE Int. Conf. Robot. Autom. (ICRA)*, 2025, pp. 6357–6363, doi: 10.1109/ICRA55743.2025.11128790.  
<a id="ref-67"></a>[67] E. Valassakis, Z. Ding, and E. Johns, “Crossing the gap: A deep dive into zero-shot sim-to-real transfer for dynamics,” in *Proc. IEEE/RSJ Int. Conf. Intell. Robots Syst. (IROS)*, 2020, pp. 5372–5379, doi: 10.1109/IROS45743.2020.9341617.  
<a id="ref-68"></a>[68] L. Bauersfeld, E. Kaufmann, P. Foehn, S. Sun, and D. Scaramuzza, “NeuroBEM: Hybrid aerodynamic quadrotor model,” in *Proc. Robot.: Sci. Syst. (RSS)*, 2021, doi: 10.15607/RSS.2021.XVII.042.  
<a id="ref-69"></a>[69] K. Bousmalis *et al.*, “Using simulation and domain adaptation to improve efficiency of deep robotic grasping,” in *Proc. IEEE Int. Conf. Robot. Autom. (ICRA)*, 2018, pp. 4243–4250, doi: 10.1109/ICRA.2018.8460875.  
<a id="ref-70"></a>[70] S. James *et al.*, “Sim-to-real via sim-to-sim: Data-efficient robotic grasping via randomized-to-canonical adaptation networks,” in *Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR)*, 2019, pp. 12619–12629, doi: 10.1109/CVPR.2019.01291.  
<a id="ref-71"></a>[71] D. Zhang, A. Loquercio, J. Tang, T.-H. Wang, J. Malik, and M. W. Mueller, “A learning-based quadcopter controller with extreme adaptation,” *IEEE Trans. Robot.*, vol. 41, pp. 3948–3964, 2025, doi: 10.1109/TRO.2025.3577037.  
<a id="ref-72"></a>[72] M. Müller, A. Dosovitskiy, B. Ghanem, and V. Koltun, “Driving policy transfer via modularity and abstraction,” in *Proc. Conf. Robot Learn. (CoRL)*, ser. Proc. Mach. Learn. Res., vol. 87, 2018, pp. 1–15. [Online]. Available: https://proceedings.mlr.press/v87/mueller18a.html  
<a id="ref-73"></a>[73] E. Kaufmann, A. Loquercio, R. Ranftl, M. Müller, V. Koltun, and D. Scaramuzza, “Deep drone acrobatics,” in *Proc. Robot.: Sci. Syst. (RSS)*, 2020, doi: 10.15607/RSS.2020.XVI.040.  
<a id="ref-74"></a>[74] M. Mittal *et al.*, “Isaac Lab: A GPU-accelerated simulation framework for multi-modal robot learning,” Nov. 2025, arXiv:2511.04831.  
<a id="ref-75"></a>[75] B. Xu, F. Gao, C. Yu, R. Zhang, Y. Wu, and Y. Wang, “OmniDrones: An efficient and flexible platform for reinforcement learning in drone control,” *IEEE Robot. Autom. Lett.*, vol. 9, no. 3, pp. 2838–2844, Mar. 2024, doi: 10.1109/LRA.2024.3356168.  
<a id="ref-76"></a>[76] M. Kulkarni, W. Rehberg, and K. Alexis, “Aerial Gym Simulator: A framework for highly parallelized simulation of aerial robots,” *IEEE Robot. Autom. Lett.*, vol. 10, no. 4, pp. 4093–4100, Apr. 2025, doi: 10.1109/LRA.2025.3548507.  
<a id="ref-77"></a>[77] K. Zakka *et al.*, “Demonstrating MuJoCo Playground,” in *Proc. Robot.: Sci. Syst. (RSS)*, 2025, doi: 10.15607/RSS.2025.XXI.020.  
<a id="ref-78"></a>[78] S. Tao *et al.*, “Demonstrating GPU parallelized robot simulation and rendering for generalizable embodied AI with ManiSkill3,” in *Proc. Robot.: Sci. Syst. (RSS)*, 2025, doi: 10.15607/RSS.2025.XXI.021.  
<a id="ref-79"></a>[79] Genesis Authors, “Genesis: A generative and universal physics engine for robotics and beyond,” GitHub repository, Dec. 2024. [Online]. Available: https://github.com/Genesis-Embodied-AI/Genesis  
<a id="ref-80"></a>[80] Linux Foundation, “Linux Foundation announces contribution of Newton by Disney Research, Google DeepMind, and NVIDIA to accelerate open robot learning,” *Press release (Sep. 29, 2025)*. Accessed: Oct. 11, 2026. [Online]. Available: https://www.linuxfoundation.org/press/linux-foundation-announces-contribution-of-newton-by-disney-research-google-deepmind-and-nvidia-to-accelerate-open-robot-learning  
<a id="ref-81"></a>[81] Z. Xie, Z. Liu, Z. Peng, W. Wu, and B. Zhou, “Vid2Sim: Realistic and interactive simulation from video for urban navigation,” in *Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR)*, 2025, pp. 1581–1591, doi: 10.1109/CVPR52734.2025.00155.  
<a id="ref-82"></a>[82] H. Jiang, H.-Y. Hsu, K. Zhang, H.-N. Yu, S. Wang, and Y. Li, “PhysTwin: Physics-informed reconstruction and simulation of deformable objects from videos,” in *Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV)*, 2025, pp. 7219–7230, doi: 10.1109/ICCV51701.2025.00678.  
<a id="ref-83"></a>[83] J. Abou-Chakra *et al.*, “Real-is-Sim: Bridging the sim-to-real gap with a dynamic digital twin,” in *Proc. IEEE Int. Conf. Robot. Autom. (ICRA)*, 2026, pp. 20542–20549, doi: 10.1109/ICRA57385.2026.11697400.  
<a id="ref-84"></a>[84] A. Romero, A. Shenai, I. Geles, E. Aljalbout, and D. Scaramuzza, “Dream to fly: Model-based reinforcement learning for vision-based drone flight,” in *Proc. IEEE Int. Conf. Robot. Autom. (ICRA)*, 2026, pp. 15983–15990, doi: 10.1109/ICRA57385.2026.11695931.  
<a id="ref-85"></a>[85] Y. J. Ma *et al.*, “Eureka: Human-level reward design via coding large language models,” in *Proc. Int. Conf. Learn. Represent. (ICLR)*, 2024. [Online]. Available: https://openreview.net/forum?id=IEduRUO55F  
<a id="ref-86"></a>[86] A. Yu, G. Yang, R. Choi, Y. Ravan, J. Leonard, and P. Isola, “Learning visual parkour from generated images,” in *Proc. Conf. Robot Learn. (CoRL)*, ser. Proc. Mach. Learn. Res., vol. 270, 2025, pp. 2500–2516. [Online]. Available: https://proceedings.mlr.press/v270/yu25b.html  
<a id="ref-87"></a>[87] J. Bjorck *et al.*, “GR00T N1: An open foundation model for generalist humanoid robots,” Mar. 2025, arXiv:2503.14734.  
<a id="ref-88"></a>[88] K. Choromanski *et al.*, “Evaluating Gemini Robotics policies in a Veo world simulator,” Dec. 2025, arXiv:2512.10675.  
<a id="ref-89"></a>[89] J. Quevedo, A. K. Sharma, Y. Sun, V. Suryavanshi, P. Liang, and S. Yang, “WorldGym: World model as an environment for policy evaluation,” in *Proc. Int. Conf. Learn. Represent. (ICLR)*, 2026. [Online]. Available: https://openreview.net/forum?id=hidBHy1CAw  
<a id="ref-90"></a>[90] I. Radosavovic, T. Xiao, B. Zhang, T. Darrell, J. Malik, and K. Sreenath, “Real-world humanoid locomotion with reinforcement learning,” *Sci. Robot.*, vol. 9, no. 89, Art. no. eadi9579, Apr. 2024, doi: 10.1126/scirobotics.adi9579.  
<a id="ref-91"></a>[91] T. Haarnoja *et al.*, “Learning agile soccer skills for a bipedal robot with deep reinforcement learning,” *Sci. Robot.*, vol. 9, no. 89, Art. no. eadi8022, Apr. 2024, doi: 10.1126/scirobotics.adi8022.  
<a id="ref-92"></a>[92] T. He *et al.*, “ASAP: Aligning simulation and real-world physics for learning agile humanoid whole-body skills,” in *Proc. Robot.: Sci. Syst. (RSS)*, 2025, doi: 10.15607/RSS.2025.XXI.066.  
<a id="ref-93"></a>[93] J. Hwangbo, I. Sa, R. Siegwart, and M. Hutter, “Control of a quadrotor with reinforcement learning,” *IEEE Robot. Autom. Lett.*, vol. 2, no. 4, pp. 2096–2103, Oct. 2017, doi: 10.1109/LRA.2017.2720851.  
<a id="ref-94"></a>[94] R. Ferede, C. De Wagter, D. Izzo, and G. C. H. E. de Croon, “End-to-end reinforcement learning for time-optimal quadcopter flight,” in *Proc. IEEE Int. Conf. Robot. Autom. (ICRA)*, 2024, pp. 6172–6177, doi: 10.1109/ICRA57147.2024.10611665.  
<a id="ref-95"></a>[95] M. Kulkarni and K. Alexis, “Reinforcement learning for collision-free flight exploiting deep collision encoding,” in *Proc. IEEE Int. Conf. Robot. Autom. (ICRA)*, 2024, pp. 15781–15788, doi: 10.1109/ICRA57147.2024.10610287.  
<a id="ref-96"></a>[96] J. Chen *et al.*, “What matters in learning a zero-shot sim-to-real RL policy for quadrotor control? A comprehensive study,” *IEEE Robot. Autom. Lett.*, vol. 10, no. 7, pp. 7134–7141, Jul. 2025, doi: 10.1109/LRA.2025.3575011.  
<a id="ref-97"></a>[97] Z. Xu, X. Han, H. Shen, H. Jin, and K. Shimada, “NavRL: Learning safe flight in dynamic environments,” *IEEE Robot. Autom. Lett.*, vol. 10, no. 4, pp. 3668–3675, Apr. 2025, doi: 10.1109/LRA.2025.3546069.  
<a id="ref-98"></a>[98] Q. Chen, J. Sun, N. Gao, J. Low, T. Chen, and M. Schwager, “GRaD-Nav: Efficiently learning visual drone navigation with Gaussian radiance fields and differentiable dynamics,” in *Proc. IEEE/RSJ Int. Conf. Intell. Robots Syst. (IROS)*, 2025, pp. 7941–7948, doi: 10.1109/IROS60139.2025.11247514.  
<a id="ref-99"></a>[99] X. Huang, J. Li, T. Wu, X. Zhou, Z. Han, and F. Gao, “Flying in clutter on monocular RGB by learning in 3D radiance fields with domain adaptation,” *IEEE Robot. Autom. Lett.*, vol. 11, no. 4, pp. 5127–5134, Apr. 2026, doi: 10.1109/LRA.2026.3666383.  
<a id="ref-100"></a>[100] M. R. Ranjbar Divkoti and A. P. Aguiar, “Learning-based dynamic obstacle avoidance for a UAV using only three range sensors,” Sep. 2026, arXiv:2609.14426.  
<a id="ref-101"></a>[101] C. Tang, B. Abbatematteo, J. Hu, R. Chandra, R. Martín-Martín, and P. Stone, “Deep reinforcement learning for robotics: A survey of real-world successes,” *Annu. Rev. Control Robot. Auton. Syst.*, vol. 8, no. 1, pp. 153–188, May 2025, doi: 10.1146/annurev-control-030323-022510.  
<a id="ref-102"></a>[102] D. Hanover *et al.*, “Autonomous drone racing: A survey,” *IEEE Trans. Robot.*, vol. 40, pp. 3044–3067, 2024, doi: 10.1109/TRO.2024.3400838.  
<a id="ref-103"></a>[103] J. Ibarz, J. Tan, C. Finn, M. Kalakrishnan, P. Pastor, and S. Levine, “How to train your robot with deep reinforcement learning: Lessons we have learned,” *Int. J. Robot. Res.*, vol. 40, no. 4–5, pp. 698–721, Apr. 2021, doi: 10.1177/0278364920987859.  
<a id="ref-104"></a>[104] G. Dulac-Arnold *et al.*, “Challenges of real-world reinforcement learning: Definitions, benchmarks and analysis,” *Mach. Learn.*, vol. 110, no. 9, pp. 2419–2468, Sep. 2021, doi: 10.1007/s10994-021-05961-4.  
<a id="ref-105"></a>[105] N. Koenig and A. Howard, “Design and use paradigms for Gazebo, an open-source multi-robot simulator,” in *Proc. IEEE/RSJ Int. Conf. Intell. Robots Syst. (IROS)*, 2004, pp. 2149–2154, doi: 10.1109/IROS.2004.1389727.  
<a id="ref-106"></a>[106] F. Furrer, M. Burri, M. Achtelik, and R. Siegwart, “RotorS—A modular Gazebo MAV simulator framework,” in *Robot Operating System (ROS): The Complete Reference (Volume 1)*, A. Koubaa, Ed., ser. Studies in Computational Intelligence, vol. 625. Cham, Switzerland: Springer, 2016, pp. 595–625, doi: 10.1007/978-3-319-26054-9_23.  
<a id="ref-107"></a>[107] S. Shah, D. Dey, C. Lovett, and A. Kapoor, “AirSim: High-fidelity visual and physical simulation for autonomous vehicles,” in *Field and Service Robotics*, ser. Springer Proceedings in Advanced Robotics, vol. 5. Cham, Switzerland: Springer, 2018, pp. 621–635, doi: 10.1007/978-3-319-67361-5_40.  
<a id="ref-108"></a>[108] Y. Song, S. Naji, E. Kaufmann, A. Loquercio, and D. Scaramuzza, “Flightmare: A flexible quadrotor simulator,” in *Proc. Conf. Robot Learn. (CoRL)*, ser. Proc. Mach. Learn. Res., vol. 155, 2021, pp. 1147–1157. [Online]. Available: https://proceedings.mlr.press/v155/song21a.html  
<a id="ref-109"></a>[109] J. Panerati, H. Zheng, S. Zhou, J. Xu, A. Prorok, and A. P. Schoellig, “Learning to fly—A gym environment with PyBullet physics for reinforcement learning of multi-agent quadcopter control,” in *Proc. IEEE/RSJ Int. Conf. Intell. Robots Syst. (IROS)*, 2021, pp. 7512–7519, doi: 10.1109/IROS51168.2021.9635857.  
<a id="ref-110"></a>[110] M. Jacinto *et al.*, “Pegasus Simulator: An Isaac Sim framework for multiple aerial vehicles simulation,” in *Proc. Int. Conf. Unmanned Aircraft Syst. (ICUAS)*, 2024, pp. 917–922, doi: 10.1109/ICUAS60882.2024.10556959.  
<a id="ref-111"></a>[111] J. Panerati, S. Sajjadi, S. Soleymanpour, V. Mehta, and I. Mantegh, “aerial-autonomy-stack—A faster-than-real-time, autopilot-agnostic, ROS2 framework to simulate and deploy perception-based drones,” Feb. 2026, arXiv:2602.07264.  
<a id="ref-112"></a>[112] C. A. Dimmig *et al.*, “Survey of simulators for aerial robots: An overview and in-depth systematic comparisons,” *IEEE Robot. Autom. Mag.*, vol. 32, no. 2, pp. 153–166, Jun. 2025, doi: 10.1109/MRA.2024.3433171.  
<a id="ref-113"></a>[113] C. S. Timperley, A. Afzal, D. S. Katz, J. M. Hernandez, and C. Le Goues, “Crashing simulated planes is cheap: Can simulation detect robotics bugs early?” in *Proc. IEEE Int. Conf. Softw. Testing, Verification Validation (ICST)*, 2018, pp. 331–342, doi: 10.1109/ICST.2018.00040.  
<a id="ref-114"></a>[114] S. Khatiri, S. Panichella, and P. Tonella, “Simulation-based test case generation for unmanned aerial vehicles in the neighborhood of real flights,” in *Proc. IEEE Conf. Softw. Testing, Verification Validation (ICST)*, 2023, pp. 281–292, doi: 10.1109/ICST57152.2023.00034.  
<a id="ref-115"></a>[115] K. Kose, J. Wing, N. A. Kose, C. Guadarrama-Trejo, A. Sowers, and A. Rasheed, “A UAV testbed for diagnosing hardware vulnerabilities: Quantifying sim-to-real discrepancies in PX4 flight logs,” *Sensors*, vol. 26, no. 10, Art. no. 3188, May 2026, doi: 10.3390/s26103188.  
<a id="ref-116"></a>[116] X. Li *et al.*, “Evaluating real-world robot manipulation policies in simulation,” in *Proc. Conf. Robot Learn. (CoRL)*, ser. Proc. Mach. Learn. Res., vol. 270, 2025, pp. 3705–3728. [Online]. Available: https://proceedings.mlr.press/v270/li25c.html  
<a id="ref-117"></a>[117] T. Wu *et al.*, “Toward reliable sim-to-real predictability for MoE-based robust quadrupedal locomotion,” in *Proc. Robot.: Sci. Syst. (RSS)*, 2026, doi: 10.15607/RSS.2026.XXII.156.  
<a id="ref-118"></a>[118] X. Wang, Y. R. Tan, W. Leong, S. Huang, R. Teo, and C. Xiang, “GPS denied IBVS-based navigation and collision avoidance of UAV using a low-cost RGB camera,” Sep. 2025, arXiv:2509.17435.  
<a id="ref-119"></a>[119] S. Thrun, W. Burgard, and D. Fox, *Probabilistic Robotics*. Cambridge, MA, USA: MIT Press, 2005.  
<a id="ref-120"></a>[120] L. Keselman, J. I. Woodfill, A. Grunnet-Jepsen, and A. Bhowmik, “Intel RealSense stereoscopic depth cameras,” in *Proc. IEEE Conf. Comput. Vis. Pattern Recognit. Workshops (CVPRW)*, 2017, pp. 1267–1276, doi: 10.1109/CVPRW.2017.167.  
<a id="ref-121"></a>[121] PX4 Autopilot, “OakD-Lite camera model (model.sdf),” *PX4-gazebo-models repository*. Accessed: Sep. 27, 2026. [Online]. Available: https://github.com/PX4/PX4-gazebo-models  
<a id="ref-122"></a>[122] C. Tallec, L. Blier, and Y. Ollivier, “Making deep Q-learning methods robust to time discretization,” in *Proc. Int. Conf. Mach. Learn. (ICML)*, ser. Proc. Mach. Learn. Res., vol. 97, 2019, pp. 6096–6104. [Online]. Available: https://proceedings.mlr.press/v97/tallec19a.html  
<a id="ref-123"></a>[123] J. Zha, “Action-repeat check for the DroneRanger DQN navigation policy,” Northeastern Univ., San Jose, CA, USA, Internal experiment report, Sep. 2026.  
<a id="ref-124"></a>[124] P. Sanchez-Cuevas, G. Heredia, and A. Ollero, “Characterization of the aerodynamic ground effect and its influence in multirotor control,” *Int. J. Aerosp. Eng.*, vol. 2017, Art. no. 1823056, 2017, doi: 10.1155/2017/1823056.  
<a id="ref-125"></a>[125] N. Fey, G. B. Margolis, M. Peticco, and P. Agrawal, “Bridging the sim-to-real gap for athletic loco-manipulation,” in *Proc. Robot.: Sci. Syst. (RSS)*, 2025, doi: 10.15607/RSS.2025.XXI.125.  
<a id="ref-126"></a>[126] J. Bednář, M. Petrlík, K. C. T. Vivaldini, and M. Saska, “Deployment of reliable visual inertial odometry approaches for unmanned aerial vehicles in real-world environment,” in *Proc. Int. Conf. Unmanned Aircraft Syst. (ICUAS)*, 2022, pp. 167–176, doi: 10.1109/ICUAS54217.2022.9836067.  
<a id="ref-127"></a>[127] N. Joubert *et al.*, “Towards a drone cinematographer: Guiding quadrotor cameras using visual composition principles,” Oct. 2016, arXiv:1610.01691.  
<a id="ref-128"></a>[128] Holybro, “M10 GPS,” *Product specification*. Accessed: Sep. 27, 2026. [Online]. Available: https://holybro.com/products/m10-gps  
<a id="ref-129"></a>[129] J. Parker-Holder and S. Fruchter, “Genie 3: A new frontier for world models,” *Google DeepMind Blog (Aug. 5, 2025)*. Accessed: Oct. 11, 2026. [Online]. Available: https://deepmind.google/discover/blog/genie-3-a-new-frontier-for-world-models/  
<a id="ref-130"></a>[130] B. Kang *et al.*, “How far is video generation from world model: A physical law perspective,” in *Proc. Int. Conf. Mach. Learn. (ICML)*, ser. Proc. Mach. Learn. Res., vol. 267, 2025, pp. 28991–29017. [Online]. Available: https://proceedings.mlr.press/v267/kang25g.html  
<a id="ref-131"></a>[131] Y. Wang *et al.*, “Interactive world simulator for robot policy training and evaluation,” in *Proc. Robot.: Sci. Syst. (RSS)*, 2026, doi: 10.15607/RSS.2026.XXII.018.  
<a id="ref-132"></a>[132] Y. Guo, L. X. Shi, J. Chen, and C. Finn, “Ctrl-World: A controllable generative world model for robot manipulation,” in *Proc. Int. Conf. Learn. Represent. (ICLR)*, 2026. [Online]. Available: https://openreview.net/forum?id=748bHL2BAv  
<a id="ref-133"></a>[133] L. Da, J. Turnau, T. P. Kutralingam, A. Velasquez, P. Shakarian, and H. Wei, “A survey of sim-to-real methods in RL: Progress, prospects and challenges with foundation models,” Mar. 2025, arXiv:2502.13187.  
<a id="ref-134"></a>[134] E. Noorani, Z. Serlin, B. Price, and A. Velasquez, “From abstraction to reality: DARPA's vision for robust sim-to-real autonomy,” *AI Mag.*, vol. 46, no. 2, Art. no. e70015, Jun. 2025, doi: 10.1002/aaai.70015.  
<a id="ref-135"></a>[135] M. Alshiekh, R. Bloem, R. Ehlers, B. Könighofer, S. Niekum, and U. Topcu, “Safe reinforcement learning via shielding,” in *Proc. AAAI Conf. Artif. Intell.*, 2018, doi: 10.1609/aaai.v32i1.11797.  
<a id="ref-136"></a>[136] A. D. Ames, S. Coogan, M. Egerstedt, G. Notomista, K. Sreenath, and P. Tabuada, “Control barrier functions: Theory and applications,” in *Proc. Eur. Control Conf. (ECC)*, 2019, pp. 3420–3431, doi: 10.23919/ECC.2019.8796030.  
<a id="ref-137"></a>[137] NVIDIA, “Isaac Sim requirements,” *Isaac Sim Documentation (5.1)*. Accessed: Sep. 22, 2026. [Online]. Available: https://docs.isaacsim.omniverse.nvidia.com/5.1.0/installation/requirements.html  
<a id="ref-138"></a>[138] J. Collins, S. Chand, A. Vanderkop, and D. Howard, “A review of physics simulators for robotic applications,” *IEEE Access*, vol. 9, pp. 51416–51431, 2021, doi: 10.1109/ACCESS.2021.3068769.  
<a id="ref-139"></a>[139] E. Bennitt, H. L. A. Bartlam-Brooks, T. Y. Hubel, and A. M. Wilson, “Terrestrial mammalian wildlife responses to unmanned aerial systems approaches,” *Sci. Rep.*, vol. 9, Art. no. 2142, Feb. 2019, doi: 10.1038/s41598-019-38610-x.  
<a id="ref-140"></a>[140] M. Mulero-Pázmány, S. Jenni-Eiermann, N. Strebel, T. Sattler, J. J. Negro, and Z. Tablado, “Unmanned aircraft systems as a new source of disturbance for wildlife: A systematic review,” *PLoS ONE*, vol. 12, no. 6, Art. no. e0178448, Jun. 2017, doi: 10.1371/journal.pone.0178448.  
<a id="ref-141"></a>[141] A. A. Paranjape, S.-J. Chung, K. Kim, and D. H. Shim, “Robotic herding of a flock of birds using an unmanned aerial vehicle,” *IEEE Trans. Robot.*, vol. 34, no. 4, pp. 901–915, Aug. 2018, doi: 10.1109/TRO.2018.2853610.  
<a id="ref-142"></a>[142] E. Bondi *et al.*, “AirSim-W: A simulation environment for wildlife conservation with UAVs,” in *Proc. 1st ACM SIGCAS Conf. Comput. Sustain. Soc. (COMPASS)*, 2018, pp. 1–12, doi: 10.1145/3209811.3209880.  
<a id="ref-143"></a>[143] E. Temesgen *et al.*, “Geofenced unmanned aerial robotic defender for deer detection and deterrence (GUARD),” May 2025, arXiv:2505.10770. IEEE ICRA 2025 Workshop on Novel Approaches for Precision Agriculture and Forestry with Autonomous Robots.  
<a id="ref-144"></a>[144] R. Yin, “Drone project technical handover: PX4 / ROS 2 / OAK-D Lite autonomous flight and obstacle-aware planning system,” NEURAI Lab, Northeastern Univ., San Jose, CA, USA, Internal tech. rep., 2026.  
<a id="ref-145"></a>[145] PX4 Autopilot, “Gazebo simulation,” *PX4 User Guide (main)*. Accessed: Sep. 27, 2026. [Online]. Available: https://docs.px4.io/main/en/sim_gazebo_gz/  
<a id="ref-146"></a>[146] RipZou, “DroneRangerIssac,” GitHub repository, commit 5acbe7b, Mar. 2026. [Online]. Available: https://github.com/RipZou/DroneRangerIssac  
<a id="ref-147"></a>[147] L. Meier, D. Honegger, and M. Pollefeys, “PX4: A node-based multithreaded open source robotics framework for deeply embedded platforms,” in *Proc. IEEE Int. Conf. Robot. Autom. (ICRA)*, 2015, pp. 6235–6240, doi: 10.1109/ICRA.2015.7140074.  
<a id="ref-148"></a>[148] Luxonis, “OAK-D Lite hardware documentation and datasheet,” *Luxonis Docs*. Accessed: Sep. 27, 2026. [Online]. Available: https://docs.luxonis.com/hardware/products/OAK-D%20Lite  
<a id="ref-149"></a>[149] PX4 Autopilot, “Using PX4's navigation filter (EKF2),” *PX4 User Guide (v1.17)*. Accessed: Sep. 27, 2026. [Online]. Available: https://docs.px4.io/v1.17/en/advanced_config/tuning_the_ecl_ekf.html  
<a id="ref-150"></a>[150] R. W. Beard and T. W. McLain, *Small Unmanned Aircraft: Theory and Practice*. Princeton, NJ, USA: Princeton Univ. Press, 2012, doi: 10.1515/9781400840601.  
<a id="ref-151"></a>[151] PX4 Autopilot, “Offboard mode,” *PX4 User Guide (v1.17)*. Accessed: Sep. 27, 2026. [Online]. Available: https://docs.px4.io/v1.17/en/flight_modes/offboard.html  
<a id="ref-152"></a>[152] F. Schiano, D. Natter, D. Zambrano, and D. Floreano, “Autonomous detection and deterrence of pigeons on buildings by drones,” *IEEE Access*, vol. 10, pp. 1745–1755, 2022, doi: 10.1109/ACCESS.2021.3137031.  
<a id="ref-153"></a>[153] Q. Quan, X. Dai, and S. Wang, *Multicopter Design and Control Practice: A Series Experiments Based on MATLAB and Pixhawk*. Singapore: Springer, 2020, doi: 10.1007/978-981-15-3138-5.  
<a id="ref-154"></a>[154] J. L. S. Cotta, D. Agar, I. R. Bertaska, J. P. Inness, and H. Gutierrez, “Latency reduction and packet synchronization in low-resource devices connected by DDS networks in autonomous UAVs,” *Sensors*, vol. 23, no. 22, Art. no. 9269, Nov. 2023, doi: 10.3390/s23229269.  
<a id="ref-155"></a>[155] PX4 Autopilot, “ROS 2 user guide and message translation node,” *PX4 User Guide (main)*. Accessed: Sep. 27, 2026. [Online]. Available: https://docs.px4.io/main/en/ros2/  
