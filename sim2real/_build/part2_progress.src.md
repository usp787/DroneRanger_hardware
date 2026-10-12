## 2. Question 1 — How far has sim-to-real transfer come?

### 2.1 Five phases in three decades

Sim-to-real research has moved through five overlapping phases (Table 1). Each phase answered the main failure of the one before it.

**Table 1. Phases of sim-to-real research.**

| Phase | Period | Core idea | Representative work | What it made possible |
|---|---|---|---|---|
| Naming the gap | 1992–2017 | Simulators are wrong in systematic ways; add noise and prefer behaviours that are known to transfer | [@brooks1992; @jakobi1995; @koos2013; @mouret2017] | The simulator is treated as a design choice, not a neutral test bed |
| Randomize | 2017–2020 | Train across many randomized simulators so that reality looks like one more sample | [@tobin2017; @sadeghi2017; @peng2018; @molchanov2019; @loquercio2020; @andrychowicz2020; @akkaya2019] | First zero-shot transfers of deep policies to arms, hands and drones |
| Identify and adapt | 2018–2022 | Fit the simulator, or a residual model, to real data; adapt online; distil privileged "teacher" policies | [@tan2018; @hwangbo2019; @chebotar2019; @ramos2019; @shi2019; @lee2020; @kumar2021; @oconnell2022] | Legged locomotion off-road; drones landing and flying in strong wind |
| Scale | 2021–2024 | GPU-parallel simulation makes thousands of randomized environments cheap | [@makoviychuk2021; @rudin2022; @mittal2023; @miki2022; @kaufmann2023; @song2023; @eschmann2024] | Training in minutes to hours; champion-level drone racing; locomotion in the wild |
| Reconstruct, differentiate, generate | 2023–2026 | Build the simulator from real data, differentiate through physics, and let foundation models design or replace parts of the simulator | [@mildenhall2022; @kerbl2023; @torne2024; @low2025; @zhang2025nmi; @ma2024dreureka; @maddukuri2025; @xu2026navrlpp; @aljalbout2026] | Zero-shot visual navigation in reconstructed scenes; automated design of randomization; system-level transfer studies |

### 2.2 The toolbox and its limits

**Randomize.** Domain randomization trains a model on a distribution of simulators wide enough that the real world falls inside it.
- *Visual randomization.* Tobin et al. trained an object detector only on images with non-realistic random textures. It localized real objects to about 1.5 cm, which was enough for grasping [@tobin2017]. Sadeghi and Levine flew a drone through real indoor corridors with a policy trained only on randomized synthetic images [@sadeghi2017].
- *Dynamics randomization.* Peng et al. randomized masses, friction, damping, controller gains and the action time step. The resulting pushing policy kept its performance on a real arm and tolerated significant calibration error [@peng2018].
- *Scaled-up randomization.* OpenAI combined both kinds of randomization at large scale for dexterous in-hand manipulation [@andrychowicz2020]. It later grew the randomization ranges automatically as the policy improved ("automatic domain randomization") [@akkaya2019].

For quadrotors, moderate randomization is usually best. About 20% around nominal values worked best for Molchanov et al. [@molchanov2019]. In racing, no randomization made real drones miss the gates, 10% gave the best real reward, and more randomization cost speed [@ferede2025].

The weaknesses are just as well documented. Initial guesses of the parameters and their variances are typically inaccurate, the methods need task-specific tuning, and robustness can come at the price of conservative behaviour [@muratore2022]. Valassakis et al. found that many published methods underplay the task-specific engineering they required. In their tests, simply injecting random forces worked as well as elaborate parameter randomization or recurrent adaptation [@valassakis2020].

**Identify.** The second family makes the simulator itself closer to reality.
- *Actuator and latency models.* Tan et al. moved quadruped gaits to hardware by adding an identified actuator model and simulated latency on top of randomization [@tan2018]. Hwangbo et al. replaced the analytic actuator model of ANYmal with a neural network trained on real data [@hwangbo2019].
- *Closed-loop calibration.* SimOpt and BayesSim close the loop: real rollouts update the randomization distribution itself [@chebotar2019; @ramos2019].
- *Aerodynamic residuals.* For multirotors, the residual is aerodynamic. Neural Lander learned the ground-effect force from flight data, which made near-ground control and landing stable [@shi2019]. NeuroBEM combined blade-element theory with a learned residual for agile flight [@bauersfeld2021].
- *Small quadrotors.* Gronauer et al. fitted thrust-to-weight, motor time constant and latency to about an hour of real flight data by Bayesian optimization (identified latency ≈18 ms). Low-level motor-command policies needed more simulator fidelity than attitude-rate policies, and policies trained with zero latency transferred worst [@gronauer2022]. A 2024 method identified inertia, thrust curve, torque coefficient and motor delay from about one minute of flight data, and its tool accepts PX4 ULog files. An RL policy trained only on the identified model then flew a 3.35 kg quadrotor outdoors in gusts up to 8 m/s [@eschmann2024sysid].
- *Residual models in Swift.* Swift's simulator used an aerodynamic model fitted to flight data, not dynamics randomization. Its champion-level racing policy then relied on residual models fitted to a handful of real runs recorded with motion capture. Gaussian processes modelled the drift of its visual–inertial odometry, and k-nearest-neighbour regression modelled residual accelerations. The policy was then fine-tuned in the augmented simulator [@kaufmann2023].

**Adapt.** Instead of one robust policy, the policy can infer the conditions it is in.
- *Image adaptation.* For perception, domain adaptation maps simulated or real images into a shared or canonical space [@bousmalis2018; @james2019].
- *Privileged teacher, sensor-only student.* For control, the most influential idea is "learning by cheating": a teacher policy with privileged simulator state is distilled into a student that sees only onboard sensors [@chen2020lbc]. This recipe produced quadrupeds that walk over challenging terrain and through the wild [@lee2020; @miki2022], and it trained Loquercio et al.'s high-speed forest-flight policy entirely in simulation [@loquercio2021].
- *Online adaptation.* Rapid Motor Adaptation estimates the dynamics online from recent history [@kumar2021]. Neural-Fly learns a wind-invariant representation from about 12 minutes of flight and adapts the last layer online [@oconnell2022]. A learned quadcopter controller with "extreme adaptation" infers a latent vehicle description from its sensor–action history. On hardware it handled a 3.7× mass difference, large changes in propeller constant, and motor failures [@zhang2025extreme].

**Abstract.** Transfer is easier when the policy consumes an intermediate representation that looks the same in simulation and reality.
- *Driving.* Müller et al. trained a driving policy on semantic segmentation instead of pixels and moved it to a real truck without real training data [@muller2018].
- *Acrobatics.* Deep Drone Acrobatics fed the policy feature tracks rather than images [@kaufmann2020].
- *Depth.* High-speed flight in the wild fed it depth computed by stereo matching on simulated image pairs, so the policy saw realistic stereo artefacts [@loquercio2021].

The price is that the abstraction must be computable onboard, and its own failures (missing depth, lost features) become the new gap.

**Scale.** GPU-parallel simulators changed what is affordable.
- *Physics on the GPU.* Isaac Gym moved physics and policy training onto one GPU [@makoviychuk2021]. Rudin et al. then trained quadruped locomotion in minutes with thousands of parallel robots [@rudin2022].
- *Frameworks.* Orbit and its successor Isaac Lab generalized this into a framework with rendered sensors [@mittal2023; @isaaclab2025]. Aerial counterparts include OmniDrones and Aerial Gym [@xu2024omnidrones; @kulkarni2025].
- *The 2025 generation.* MuJoCo Playground trains locomotion and manipulation policies in minutes on one GPU, and they transferred zero-shot to quadrupeds, humanoids and arms [@zakka2025]. ManiSkill3 combines GPU-parallel simulation with rendering at tens of thousands of frames per second [@tao2025]. Newer engines such as Genesis and Newton advertise very high throughput and better transfer, but those claims are so far reported by their developers, not independently validated [@genesis2024; @newton2025].
- *What it changed.* Scale makes heavy randomization and large hyper-parameter sweeps cheap. It does not by itself make the simulator more faithful. NavRL++ found that larger training scale improved convergence, but perception failures still dominated real-world degradation [@xu2026navrlpp].

**Reconstruct.** The newest family builds the simulator from the real environment.
- *Scene representations.* Neural radiance fields and 3D Gaussian splatting reconstruct photorealistic, real-time renderable scenes from ordinary images [@mildenhall2022; @kerbl2023].
- *Drones.* SOUS VIDE built a drone simulator on a Gaussian-splat scene captured with a phone. It distilled an MPC expert with privileged information into an onboard visuomotor policy that transferred zero-shot, across 105 hardware experiments [@low2025]. Lv et al. made the splats relightable, so lighting can be randomized. Their monocular policy flew through real forests at up to 10 m/s [@lv2026].
- *Beyond drones.* The same idea spread quickly.
  - RialTo builds a digital twin from a real scan and uses RL in it to make real-world imitation policies robust. It reports robustness gains of more than 67% on eight manipulation tasks [@torne2024].
  - SplatSim reached 86.25% zero-shot real-world success with RGB policies trained only in a splat-rendered simulator, against 97.5% for policies trained on real data [@qureshi2025].
  - Vid2Sim turns a single monocular video into an interactive navigation environment. It improved real-world success by 68.3% over earlier simulation methods [@xie2025vid2sim].
  - PhysTwin fits physics to videos of deformable objects [@jiang2025phystwin].
  - Real-is-Sim keeps a twin synchronized with the real scene at 60 Hz, so the policy always acts on the simulated robot [@abouchakra2026].

**Differentiate and generate.** Two further directions reduce the cost of learning.
- *Differentiable physics.* Zhang et al. trained vision-based agile flight by back-propagating through a simple differentiable point-mass model. The policy used low-resolution depth and ran onboard a low-cost computer [@zhang2025nmi].
- *Model-based RL.* Dream to Fly learned racing from pixels with a world model, DreamerV3; real flights used rendered images in a hardware-in-the-loop setup [@romero2026].
- *Automated design.* Foundation models now automate parts of the sim-to-real recipe itself. Eureka used an LLM to write reward functions that beat human-engineered ones on 83% of 29 simulated tasks [@ma2024eureka]. DrEureka extended this to choosing domain-randomization ranges, improving a quadruped's forward velocity by 34% over human-designed settings [@ma2024dreureka].
- *Generated training images.* Generative image models can replace hand-built textures during training. LucidSim transferred a visual parkour policy zero-shot to a cheap RGB camera [@yu2025lucidsim].
- *Sim-and-real co-training.* Large generalist policies are increasingly trained on a mix of simulated and real data [@gr00t2025]. Maddukuri et al. found that simulation data raised real-world success by 38% on average, even with notable sim-real differences [@maddukuri2025].
- *World models.* Video world models are being tried as learned simulators and policy evaluators [@cosmos2025; @veo2025; @quevedo2026]. Their limits are discussed in Section 3.6.

### 2.3 Where transfer works best today

**Legged and humanoid robots** are the clearest success. A 2025 IJRR review describes the standard toolkit as system identification, domain randomization, domain adaptation and privileged teacher–student training [@ha2025].
- *Outdoor humanoid walking.* Radosavovic et al. deployed a transformer policy zero-shot on the Digit humanoid outdoors. They combined randomized dynamics, noise and delay with teacher–student training and adaptation from observation history [@radosavovic2024].
- *Soccer skills.* Haarnoja et al. transferred soccer skills to a small humanoid zero-shot. They credited "sufficiently high-frequency control, targeted dynamics randomization, and perturbations." The gap was still measurable: real and simulated walking speeds differed by 13%, and get-up times by 28% [@haarnoja2024].
- *Residual correction.* ASAP learned a residual "delta action" model from real rollouts and fine-tuned the policy in the corrected simulator. This cut tracking error more than system identification or randomization alone [@he2025asap].
- *Extreme motions.* OmniXtreme ran flips and breakdancing on a real humanoid by adding torque–speed envelopes, aggressive randomization and power-safety regularization [@wang2026omnixtreme].

**Manipulation** transfers well for rigid objects and quasi-static tasks, from in-hand reorientation [@andrychowicz2020] to splat-rendered RGB policies [@qureshi2025], and sim-and-real co-training has become a practical recipe for vision-based policies [@maddukuri2025; @wei2025cotrain]. Deformable, transparent and contact-rich cases remain hard (Section 3).

**Navigation** transfers when the policy consumes geometry (depth, LiDAR or occupancy) rather than raw pixels, and when the simulated scenes resemble the deployment scenes [@kadian2020; @xie2025vid2sim; @xu2026navrlpp]. Aerial navigation follows the same pattern (Section 2.4).

### 2.4 Aerial robots: from motion-capture arenas to forests

Multirotors have been a proving ground for sim-to-real, because their rigid-body dynamics are simple to simulate. Their aerodynamics, batteries and sensors are not. Table 2 lists the milestones most relevant to DroneRanger.

**Table 2. Selected aerial sim-to-real milestones.**

| Year | Work | Task | Main transfer technique | State / sensing in the real tests |
|---|---|---|---|---|
| 2017 | Hwangbo et al. [@hwangbo2017] | Low-level control | Conservative policy optimization in a deliberately simple simulator; recovered from upside-down hand throws | Motion capture + onboard IMU |
| 2017 | CAD2RL [@sadeghi2017] | Indoor collision-free flight | Visual randomization; no real images | Monocular camera on a consumer drone; no motion capture |
| 2019 | Sim-to-(multi)-real [@molchanov2019] | Low-level control on several airframes | Dynamics randomization | Motion capture |
| 2019 | Neural Lander [@shi2019] | Near-ground control and landing | Learned ground-effect residual (landing height error 0.13 m → ≈0) | Motion capture |
| 2020 | Deep drone racing [@loquercio2020] | Gate detection for racing | Visual randomization | Onboard camera + VIO |
| 2020 | Deep drone acrobatics [@kaufmann2020] | Acrobatic manoeuvres | Abstraction (feature tracks), privileged expert | Onboard camera + IMU |
| 2021 | High-speed flight in the wild [@loquercio2021] | Forest flight | Privileged expert, simulated stereo depth | Onboard stereo + VIO |
| 2022 | Neural-Fly [@oconnell2022] | Flight in winds up to 12.1 m/s | Learned representation + online adaptation | Pixhawk/PX4 in Offboard mode with a companion computer; motion capture indoors, GPS outdoors |
| 2023 | Swift [@kaufmann2023] | Racing against human champions | Residual perception and dynamics models fitted to real data | Onboard VIO and gate detection; motion capture used for data collection |
| 2023 | Song et al. [@song2023] | Racing near the physical limit | RL vs. optimal control, dynamics randomization | Motion capture |
| 2024 | Learning to fly in seconds [@eschmann2024] | Low-level control | Fast training (18 s), action history, asymmetric critic | Motion capture |
| 2024 | End-to-end time-optimal flight [@ferede2024] | Racing, motor level | Residual thrust/moment model from flight data | Motion capture; larger sim–real gap than a policy over an inner-loop controller |
| 2024 | Kulkarni and Alexis [@kulkarni2024] | Collision-free navigation | Depth → collision-encoding latent → RL, with latency and noise randomization | Onboard depth + VIO, Jetson Orin NX |
| 2025 | SimpleFlight [@chen2025simpleflight] | Low-level control | Five factors: input choice, time-aware critic, smoothness reward, system identification + selective randomization, large batches | Motion capture |
| 2025 | NavRL [@xu2025navrl] | Safe flight among moving obstacles | Isaac Sim PPO with velocity commands + velocity-obstacle shield | Onboard RGB-D, LiDAR-inertial odometry, Jetson Orin NX |
| 2025 | Differentiable physics [@zhang2025nmi] | Agile vision-based flight | Back-propagation through a simple point-mass model | Onboard 16×12 depth on a US$21 computer |
| 2025 | SOUS VIDE [@low2025] | Visual navigation | Gaussian-splat digital twin + distillation + adaptive low-level module | Onboard Jetson Orin Nano; camera, optical flow, IMU |
| 2025 | GRaD-Nav [@chen2025gradnav] | Visual gate navigation | Splats + differentiable dynamics + runtime adaptation | Onboard Orin Nano; 6–7/10 real vs. 9–10/10 simulated |
| 2026 | Zhang et al. [@zhang2026shield] | High-speed flight in clutter and forest | RL + physics-informed reward + safety filter | Onboard depth camera (100×60 input) |
| 2026 | Huang et al. [@huang2026] | Clutter flight, monocular RGB | Splat scenes + randomization + adversarial domain adaptation | Onboard Orin NX; 80% real vs. 90% simulated success |
| 2026 | Lv et al. [@lv2026] | Forest flight, monocular | Relightable Gaussian splatting; twilight success 3/10 → 8/10 with relighting | PX4, Jetson Orin NX, RGB, GNSS–IMU EKF |
| 2026 | Dream to Fly [@romero2026] | Racing from pixels | Model-based RL (DreamerV3) | Hardware-in-the-loop with rendered images: tests dynamics, not visual transfer |
| 2026 | NavRL++ [@xu2026navrlpp] | Navigation (aerial and legged) | Factorized perturbation study + perturbation-aware fine-tuning | Onboard RGB-D + LiDAR |
| 2026 | Ranjbar Divkoti and Aguiar [@divkoti2026] | Dynamic obstacle avoidance with three range sensors | PPO with a behaviour grid map | Small quadrotor with three range sensors |

Two trends stand out. The first is a move from motion-capture arenas to onboard sensing. Low-level and agile results still mostly rely on external state estimation [@molchanov2019; @eschmann2024; @ferede2025; @chen2025simpleflight]. A 2025 review of real-world deep RL notes that "for quadrotors, most tests remain confined to controlled, obstacle-free indoor environments" [@tang2025]. Navigation results since 2021 increasingly rely on onboard VIO, depth and LiDAR [@loquercio2021; @kulkarni2024; @xu2025navrl]. The second is a move from one technique to a recipe. The strongest recent systems combine several techniques: identification, randomization, abstraction, a privileged teacher, a safety layer, and some real data. The surveys of drone racing [@hanover2024] and of RL for real robots [@ibarz2021; @dulacarnold2021] make the same point. The engineering of the whole system decides transfer, not any single algorithm.

The level at which the policy acts also matters. Low-level motor-command policies need more simulator fidelity than attitude-rate or velocity policies [@gronauer2022]. An end-to-end motor-level racing policy lost most of its simulated advantage on the real drone, while a policy running over an inner-loop controller transferred more consistently [@ferede2024]. NavRL chose velocity commands specifically for transferability [@xu2025navrl].

Simulators followed the same arc:
- Gazebo with RotorS ran the real autopilot against simulated dynamics [@koenig2004; @furrer2016].
- AirSim and Flightmare added photorealism and fast rendering [@shah2018; @song2021flightmare]. Gym-pybullet-drones offered a lightweight learning environment [@panerati2021].
- Pegasus connected Isaac Sim to PX4 [@jacinto2024]. Aerial-autonomy-stack runs a full PX4/ArduPilot, ROS 2 and edge-compute stack more than 20 times faster than real time. Its authors explicitly count the vertical integration of heterogeneous hardware and software as part of the "simulation-to-reality gap" [@panerati2026].
- A 2025 survey of 44 aerial simulators notes that transfer remains hard where unmodelled effects dominate: agile flight, close-proximity flight and aerial manipulation [@dimmig2025].

### 2.5 Simulation for testing, not only for training

Sim-to-real is not only about learned policies. Two lines of work bear directly on DroneRanger's SITL-first plan.
- **Simulation-based testing of autopilot software.**
  - Timperley et al. studied 228 ArduPilot bug fixes. Only 10 needed physical hardware, so most bugs were reproducible in software-in-the-loop simulation, provided the tests swept configurations and inputs. Configuration (81 bugs) and environment, such as wind (22 bugs), mattered most [@timperley2018].
  - Khatiri et al. reconstructed real PX4 flights in PX4 SITL/Gazebo and generated riskier neighbouring test cases. Repeated runs of the same simulation already differed noticeably, so simulator non-determinism alone limits replication [@khatiri2023].
  - Kose et al. compared real PX4 flight logs with default, untuned PX4 SITL in Gazebo. Vertical-acceleration variance was about ten times larger in reality (4.985 vs. 0.458), and maximum tilt was 72.1° vs. 24.0°. GPS and magnetometer fluctuations appeared only in reality. Airframes, PX4 versions and mission scales also differed, which confounds the comparison [@kose2026].
- **Staged validation pipelines.** Jiang et al. lay out software-in-the-loop, hardware-in-the-loop, controlled real-world and in-field stages for PX4-class drones [@jiang2025].

Measuring transfer has also become a research topic in its own right.
- **The SRCC metric.** Kadian et al. defined the Sim-vs-Real Correlation Coefficient (SRCC): the correlation between methods' simulated and real performance. The simulator used in a navigation challenge had an SRCC of only 0.18 for success, because agents had learned to exploit imperfect collision handling and "slide" along walls. Tuning simulator parameters raised the SRCC to 0.844 [@kadian2020].
- **Predictivity as a design target.** SIMPLER narrowed control and visual gaps without building full digital twins. Over more than 1,500 paired evaluations, its "visual matching" setup reached a Pearson correlation of 0.924 between simulated and real success rates [@li2025simpler]. PolaRiS builds a splat environment from a 2–5 minute video scan and reaches an average correlation of about 0.9 with real performance [@jain2026polaris].
- **Few real trials.** Two 2026 papers address DroneRanger's situation directly. One treats real-world performance estimation as a betting problem, to get more out of each real trial [@chen2026betting]. RoboGauge showed that evaluating policies in a second simulator predicted real command tracking better than evaluating them in the training simulator: an error of 0.0558 against real data, vs. 0.0883 [@wu2026robogauge].
- **Factorized perturbations.** NavRL++ injected each perturbation separately: sensor noise, perception failure, input and action latency, and control-response mismatch. This measured how much each one costs [@xu2026navrlpp].

### 2.6 Answer to Q1

In three decades, sim-to-real moved from "controllers built in simulation rarely work on robots" to routine zero-shot transfer for tasks whose physics can be modelled or randomized. The clearest successes are:
- legged and humanoid locomotion [@ha2025; @radosavovic2024];
- low-level quadrotor control [@hwangbo2017; @molchanov2019; @eschmann2024];
- drone racing [@kaufmann2023; @song2023].

Rigid-object manipulation [@andrychowicz2020; @qureshi2025] and geometry-based navigation [@xu2025navrl; @xu2026navrlpp] follow. The successful recipes share four ingredients:
1. a simulator calibrated by system identification, or by residual models fitted to a small amount of real data [@tan2018; @hwangbo2019; @kaufmann2023; @he2025asap];
2. randomization of whatever is still uncertain, including timing [@peng2018; @muratore2022];
3. inputs that look the same in simulation and in reality, through abstraction or privileged teacher–student training [@muller2018; @chen2020lbc; @loquercio2021];
4. GPU-parallel training at scale [@makoviychuk2021; @rudin2022].

Since 2023 the field has added digital twins reconstructed from real images [@low2025; @torne2024], differentiable physics [@zhang2025nmi] and foundation-model tools [@ma2024dreureka; @maddukuri2025]. It has also started to *measure* transfer, using correlations between simulated and real outcomes [@kadian2020; @li2025simpler; @jain2026polaris]. For aerial robots the frontier has moved from motion-capture arenas to flight through forests and clutter at 7–10 m/s with onboard sensing [@loquercio2021; @zhang2026shield; @lv2026]. Many headline results still depend on motion capture, either for state or for calibration data [@kaufmann2023; @song2023].
