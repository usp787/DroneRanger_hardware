## 3. Question 2 — What are the latest challenges (2024–2026)?

The successes of Section 2 are real, but they cluster in well-instrumented settings. A 2026 view of the literature shows eleven challenges that are still open. They are ordered roughly by how directly they affect a small outdoor drone.

### 3.1 Perception is now the weakest link

Dynamics randomization and identification have made low-level control transfer fairly routine. Perception has not caught up.
- **The measured cost.** In NavRL++'s factorized study, perception failure caused the largest single drop in navigation success: more than 5 percentage points at every obstacle density. Input noise, latency and control mismatch each cost only about 1–3 points. All perturbations together cut success by more than 10 points, and by more than 15 in dense scenes, and they raised control effort about 2.5-fold [@xu2026navrlpp].
- **Lighting and blur.** A GPS-denied visual-servoing system on a Jetson and PX4 worked in simulation but failed in real flight because of lighting changes and motion blur [@wang2025ibvs].
- **Baked-in lighting.** Even photorealistic reconstructions couple lighting with geometry, which led Lv et al. to make Gaussian splats relightable [@lv2026].

Reconstructed scenes do not remove the problem. A 2026 policy trained in splat reconstructions of real clutter reached 90% success in simulation but 80% in reality. Most of its real failures came from foliage swaying in the propeller downwash, which the simulator did not model [@huang2026]. Another splat-trained gate-navigation policy fell from 9–10/10 successes in simulation to 6–7/10 on hardware [@chen2025gradnav].

Rendering realism is not the same as sensor realism. Probabilistic robotics has long modelled range sensors as a mixture: correct returns with noise, unexpected short readings, maximum-range failures and random outliers [@thrun2005]. The failure modes of real depth sensors, such as holes, minimum range, specular surfaces, thin structures and false matches [@keselman2017], are rarely modelled. Most simulators return perfect depth: PX4's Gazebo camera model does, and so does the idealized OAK-D sensor configuration shipped with Aerial Gym [@px4gzmodels; @kulkarni2025]. The 2026 Annual Review of the reality gap makes the same observation in general form. Simulated sensor models are often "simple Gaussian noise", and the authors group perception and sensing with dynamics, actuation and system design as the four sources of the gap [@aljalbout2026]. Visual fidelity does not always matter most, though. In contact-rich pushing, physics gaps mattered more than visual ones [@wei2025cotrain].

### 3.2 System-level gaps: latency, timing, control stacks and integration

The newest systematic studies find the gap spread across the whole autonomy stack, not inside the policy.
- **Latency.** NavRL++ measured input latency of up to about 100 ms and action latency of up to about 40 ms on its robots. It had to randomize both during fine-tuning. Performance held above 10 Hz control, degraded slightly at 5 Hz, and dropped sharply at 2 Hz [@xu2026navrlpp].
- **Decision rate.** Q-learning methods degrade as the decision period shrinks [@tallec2019]. In DroneRanger's own DQN, a 50 Hz decision rate prevented the policy from learning which way to turn, while 5 Hz worked [@zha2026ar].
- **Control stack.** When training replaces the autopilot with a simplified controller, the policy is tuned to a closed loop that does not exist on the vehicle. Cross-simulator or sim-to-sim checks are the recommended remedy [@xu2026navrlpp; @jacinto2024].
- **Integration.** Panerati et al. treat the vertical integration of heterogeneous hardware and software (autopilot, middleware, edge computer and network) as part of the reality gap [@panerati2026]. Delays, partial observability and system constraints also appear among the canonical challenges of real-world RL [@dulacarnold2021].

### 3.3 Physics that is still hard to model, especially outdoors

For multirotors the hard physics is aerodynamic. The first RL quadrotor controller to fly was trained in a deliberately simple simulator. Its authors named the gaps they had ignored: motor dynamics, ground effect, battery and weight changes, and wireless delay [@hwangbo2017]. Those effects are still the usual suspects.
- **Near the ground.** Ground effect is significant within about five rotor radii [@sanchezcuevas2017].
- **At speed and in wind.** Rotor drag and unsteady effects grow at speed [@bauersfeld2021], and wind is turbulent and site-specific [@oconnell2022].
- **Batteries.** Battery voltage sag changes the available thrust during a flight.

Learned residual models work well [@shi2019; @bauersfeld2021; @kaufmann2023], but they need flight data with accurate ground truth. That usually means motion capture or a wind tunnel [@oconnell2022]. Default autopilot simulators are optimistic too. In a 2026 comparison, real PX4 logs showed about ten times the vertical-acceleration variance of an untuned PX4 SITL run [@kose2026].

On legged and humanoid robots, the analogous problem is actuator and contact modelling. Recent humanoid work shows how stubborn this is:
- **Residual alignment is costly.** ASAP needed real rollouts to fit its residual action model. A full-body model would need hundreds of motion clips, the method relied on motion capture, and two robots were damaged along the way [@he2025asap].
- **Power limits are missing from simulators.** In OmniXtreme, real failures on impulsive landings came from motor overcurrent, power limits and battery undervoltage. The authors note these "remain challenging to capture accurately in simulation" [@wang2026omnixtreme].
- **Unmodelled effects recur.** The legged-locomotion review lists motor heating, non-deterministic delays and policies that exploit simulator artefacts [@ha2025].
- **Correction needs per-task engineering.** An "unsupervised actuator net" learned corrective simulator torques from real data without torque sensing. It still needed a reference trajectory and engineering for each task [@fey2025].

Battery sag is the multirotor version of the same problem.

### 3.4 Dependence on privileged infrastructure

Many celebrated aerial results used motion capture: for state estimation during flight [@hwangbo2017; @molchanov2019; @song2023; @eschmann2024; @ferede2025; @chen2025simpleflight], or for collecting the real data that calibrated the simulator [@kaufmann2023]. Results "in the wild" replace motion capture with onboard visual–inertial odometry, which drifts. Benchmarked VIO also behaves differently in closed-loop flight than on datasets [@loquercio2021; @bednar2022]. Outdoors with GNSS alone, horizontal error of a metre or more is normal [@joubert2016; @holybrom10]. A 2025 survey of real-world deep RL concludes that, for quadrotors, most tests remain confined to controlled, obstacle-free indoor environments [@tang2025]. The gap between a lab arena and an open field is itself a sim-to-real gap. It is the one most capstone-scale projects meet first.

### 3.5 Digital twins: promise and limits

Real-to-sim reconstruction is the most active direction of 2024–2026. It is also not a finished solution:
- **Static scenes.** A splat or radiance field captures one moment. Vegetation grows and moves, lighting changes through the day and the season, and dynamic agents are absent [@low2025; @lv2026].
- **Geometry and physics.** Reconstructions are photometric. Collision geometry, materials and contact properties must be added, and errors there become dynamics gaps.
- **Capture cost.** SOUS VIDE used hand-held video [@low2025]. Lv et al.'s outdoor forest scenes used camera, LiDAR and RTK capture [@lv2026].
- **Moving vegetation.** Foliage moving in the propeller downwash caused most real failures of a splat-trained clutter-flight policy [@huang2026].

The 2024–2026 manipulation and navigation twins report the same limits:
- **RialTo** needs accurate depth sensing, which fails on thin, transparent or reflective objects. It is limited to quasi-static tasks and takes about two days per task [@torne2024].
- **SplatSim** handles rigid bodies only, so no cloth, liquids or plants [@qureshi2025].
- **Vid2Sim** environments are slow to build [@xie2025vid2sim].
- **PolaRiS** calls its system identification "relatively simplistic" [@jain2026polaris].
- **Real-is-Sim** breaks under prolonged occlusion [@abouchakra2026].

For a garden, the plants themselves are deformable objects that move in the wind.

### 3.6 Foundation models and generative simulation bring a new kind of gap

Generative models promise unlimited, diverse training and test data. Their gap is different in kind: physical *inconsistency*, rather than parameter error.
- **World-model developers' own caveats.** NVIDIA's Cosmos report says current world models "fall short as reliable simulators of the physical world". It cites missing object permanence, inaccurate contact dynamics and poor adherence to physics [@cosmos2025]. Genie 3 keeps generated worlds consistent for a few minutes [@genie3].
- **Realism is not physics.** Physical understanding in generative video models is "severely limited, and unrelated to visual realism" [@motamed2026]. Video models also tend to imitate the nearest training example rather than learn physical laws, so "scaling alone is insufficient" [@kang2025].
- **World models as evaluators.** These can work for ranking. A Veo-based simulator ranked eight policy checkpoints correctly against more than 1,600 real trials (Pearson 0.86), but it under-predicted absolute success and hallucinated during contact [@veo2025]. WorldGym reached a correlation of 0.78 with real success [@quevedo2026]. An interactive world simulator stayed stable for more than ten minutes, but policies scored slightly higher in it than in reality [@wang2026iws]. A third model, Ctrl-World [@guo2026ctrlworld], mis-ranked policies in PolaRiS's comparison [@jain2026polaris].
- **Co-training is fragile.** Maddukuri et al.'s best mix sampled 99% simulation data, and pushing it to 99.5–99.9% dropped success from 95% to 60% [@maddukuri2025]. Wei et al. found that gains plateau as simulation data grows, that real data sets the ceiling, and that perfectly rendered simulation can even hurt [@wei2025cotrain].
- **LLM-designed randomization is early.** DrEureka has no visual inputs and keeps its randomization fixed during training [@ma2024dreureka]. Surveys add hallucination, and the compute and latency cost of LLM calls, as new failure modes [@da2025]. DARPA's TIAMAT programme argues that most current techniques assume a small gap and high-fidelity simulators. It aims instead for "abstract-to-real" transfer from many low-fidelity simulators [@noorani2025].

For a semester-scale drone project, these tools are worth watching, not yet worth depending on.

### 3.7 Robustness versus performance, and choosing what to randomize

Domain randomization trades nominal performance for robustness. Randomized policies are consistently more robust than nominal ones, but the initial parameter guesses and variances are typically inaccurate [@muratore2022]. In quadrotor racing, wider ranges bought robustness at the cost of speed [@ferede2025]. Adaptive methods tune the ranges with real data [@chebotar2019; @ramos2019]. Their price is the real data that the method is supposed to save. Valassakis et al. found that, once engineering effort is accounted for, simple random force injection matched elaborate methods [@valassakis2020]. There is still no principled, task-independent rule for choosing ranges.

### 3.8 Evaluation and reproducibility

Sim-to-real claims are hard to compare:
- **Few trials.** Real-world trials are few and costly.
- **Unreported effort.** Engineering effort and task-specific tuning are often left out [@valassakis2020].
- **Simulation does not predict reality.** Simulated benchmarks may not predict real performance. Kadian et al.'s SRCC of 0.18 for an unmodified simulator is the cautionary example [@kadian2020]. Since 2024, sim-to-real correlation has been reported more often [@li2025simpler; @jain2026polaris]. Correlations are setup-specific, though, and standard simulated benchmarks can correlate poorly with reality [@jain2026polaris]. The 2026 Annual Review lists the metrics now in use: SRCC, offline replay error, image-fidelity scores, and success and reward. It also lists calibrating the gap, so that simulation can be trusted for evaluation, as an open problem [@aljalbout2026].

Choi et al. call for community-curated libraries of *validated* models and for simulation grand challenges. Among the field's nine barriers they list that "uncertainty is marginally handled" and that "model calibration can be tedious" [@choi2021].

### 3.9 Safety assurance of simulation-trained behaviour

A learned policy has no guarantee outside its training distribution, and the reality gap is exactly such a shift. The standard response is to wrap the policy in a filter:
- shields that override unsafe actions [@alshiekh2018];
- control-barrier-function filters [@ames2019];
- velocity-obstacle or projection-based safety layers in recent aerial RL [@xu2025navrl; @zhang2026shield].

These filters themselves depend on a model and on state estimates. A safety layer is only as good as the perception and estimation beneath it [@brunke2022]. Certification of learned flight control is still an open question.

### 3.10 Compute, tooling and the people cost of simulation

Photorealistic simulation has hardware requirements. NVIDIA states that Isaac Sim does not support GPUs without RT cores, such as the A100 and H100 [@nvidiaisaac]. Simulators also differ widely in physics fidelity and features [@collins2021]. Choi et al. note that building and maintaining a simulation platform takes broad multidisciplinary expertise and sustained software-development commitment [@choi2021]. For a student team that turns over every semester, this "people gap" is real: versions drift, and undocumented simulator settings are lost.

### 3.11 Modelling other agents: people and animals

Simulating the humans or animals a robot interacts with is listed by Choi et al. as a barrier of its own [@choi2021]. For wildlife the evidence is thin and variable:
- **Reactions vary.** Mammal reactions to drones depend on species, altitude and approach [@bennitt2019]. A systematic review found that target-oriented flight provokes the strongest reactions [@mulero2017].
- **Models need field data.** Herding models need interaction parameters measured with live birds [@paranjape2018].
- **Synthetic animals are only a start.** Simulated animals can train detectors [@bondi2018]. An RL deterrence supervisor trained against virtual deer has been proposed, but not yet evaluated [@temesgen2025].

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
- perception and sensor failure modes [@xu2026navrlpp; @aljalbout2026];
- latency, decision rate and control-stack mismatch [@xu2026navrlpp; @panerati2026];
- hard-to-model physics: aerodynamics, and actuator, power and battery limits [@oconnell2022; @wang2026omnixtreme];
- the motion-capture and lab infrastructure that many successes quietly depend on.

The newest tools help but have limits. Digital twins are powerful but static and mostly rigid [@low2025; @qureshi2025]. Generative world models are not yet physically consistent [@cosmos2025; @motamed2026]. Co-training and LLM-designed randomization help, but they saturate or remain narrow [@wei2025cotrain; @ma2024dreureka].

Evaluation is the weakest link. Sim–real predictivity is setup-specific, real trials are few, and engineering effort is under-reported [@kadian2020; @valassakis2020; @chen2026betting]. Safety filters help, but they inherit the errors of the models and estimates beneath them [@brunke2022].

Every one of these challenges appears, at small scale, in DroneRanger (Section 4).
