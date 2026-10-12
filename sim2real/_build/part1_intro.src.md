## 1. Introduction

### 1.1 What "sim-to-real" means

A controller, planner, perception model or whole mission is developed in simulation and then run on a physical robot. *Sim-to-real transfer* is the degree to which behaviour and performance carry over. The *reality gap* is everything that makes them differ. The term goes back to evolutionary robotics. Brooks warned in 1992 that programs evolved on simulated robots can fail on real ones, because simulated sensing and actuation differ from the real thing [@brooks1992]. Jakobi et al. then showed that the right amount of noise in a simulator could make evolved controllers for a small mobile robot transfer [@jakobi1995]. Twenty years later the same community still described the gap as the central obstacle to using simulators [@koos2013; @mouret2017].

Most of this literature concerns policies learned by reinforcement learning [@sutton2018; @kober2013]. The same gap affects any controller, estimator or mission that is tuned in simulation, including a scripted PX4 patrol.

This review uses a six-part taxonomy of the gap, which recurs in the surveys [@zhao2020; @hofer2021; @salvato2021; @choi2021]:

1. **Dynamics gap:** mass, inertia, actuator response, aerodynamics, contact and friction.
2. **Sensing and perception gap:** noise, bias, failure modes, rendering realism and lighting.
3. **Timing and latency gap:** delays, jitter, asynchronous sensors and discrete decision rates.
4. **Control-stack and software gap:** a different controller, middleware, coordinate frames or message versions in simulation than on the robot.
5. **Environment-distribution gap:** the scenes, weather and other agents that were simulated, as against those actually met.
6. **Evaluation gap:** metrics that are easy to compute in simulation (ground-truth state, collision checks) but not on the robot, so the gap itself goes unmeasured.

The first three are what most papers mean by the reality gap. The last three are less glamorous, but the DroneRanger record (Section 4) shows they matter as much on a capstone-scale platform.

### 1.2 Why it matters for DroneRanger

DroneRanger's first publication describes a simulation-guided architecture: PX4, ROS 2, Gazebo and Unity are bridged so that identical autonomy code runs in simulation and in flight. The paper states that the architecture "enables reliable simulation-to-reality transfer" for planning and avoidance [@ling2026]. In Fall 2026 the project has two threads.

- **Hardware group.** It must make the Spring 2026 prototype safe, measurable and outdoor-ready, ending with O1 (manual outdoor flight) and O2 (an autonomous PX4 Mission-mode patrol over a household garden). Every mission is rehearsed in PX4 SITL first (O0) [@zha2026charter].
- **RL group.** It is training a DQN navigation policy in Isaac Lab, and the hardware group has agreed to prepare the vehicle to receive it [@ripzou2026rl; @zha2026lit].

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
