# Sim-to-Real Transfer for Aerial Robots and What It Means for DroneRanger: A Comprehensive Literature Review

*Jiarui Zha (zha.j@northeastern.edu), DroneRanger hardware group, CS 7980 Research Capstone, Northeastern University (Silicon Valley). PI: Prof. Ilmi Yoon, NEURAI Lab. Version 1.0, 2026-10-11.*

*Companion files: [references.md](references.md) (reference list with access links), [references.bib](references.bib) (BibTeX), and the brief Canvas version [DroneRanger_Sim2Real_Literature_Review_Brief.docx](DroneRanger_Sim2Real_Literature_Review_Brief.docx).*

---

## Executive summary

**Q1. How far has sim-to-real come?**
- **Transfer is now routine where the physics can be modelled.** It used to fail by default. Today it works for tasks whose physics can be modelled or randomized: legged and humanoid locomotion, low-level quadrotor control and drone racing [@ha2025; @eschmann2024; @kaufmann2023].
- **The recipe that works has four parts:**
  - calibrate the simulator with a little real data [@tan2018; @kaufmann2023];
  - randomize what remains uncertain [@peng2018; @muratore2022];
  - keep the policy's inputs similar in simulation and reality [@loquercio2021; @chen2020lbc];
  - train at GPU scale [@rudin2022].
- **New tools since 2023.** Real-to-sim digital twins [@low2025; @torne2024], differentiable physics [@zhang2025nmi] and foundation-model tools [@ma2024dreureka; @maddukuri2025] have joined the recipe. Transfer is also increasingly *measured*, not just asserted [@kadian2020; @jain2026polaris].
- **Drones in the wild.** Drones now fly learned policies through forests and clutter with onboard sensing [@loquercio2021; @zhang2026shield; @lv2026]. Many headline results still rely on motion capture.

**Q2. What are the latest challenges?**
- **Perception** is now the largest single source of degradation, and recent systems also show gaps in **latency, timing and the control stack** [@xu2026navrlpp; @aljalbout2026].
- **Hard-to-model physics** persists: aerodynamics, actuator limits and battery limits [@oconnell2022; @wang2026omnixtreme].
- **The newest tools have clear limits.** Digital twins are static and mostly rigid [@qureshi2025]. World models are not yet physically consistent [@cosmos2025; @motamed2026]. Co-training saturates [@wei2025cotrain].
- **Evaluation and safety assurance lag behind.** Real trials are few, correlations are setup-specific, and safety filters inherit estimation errors [@chen2026betting; @brunke2022].

**Q3. What does this mean for DroneRanger?**
- **Four pipelines, none measured.** DroneRanger runs four simulation pipelines with different assumptions (Table 4). None models the OAK-D Lite's depth failures, the X500's ground effect or the real serial-link timing. Wind exists only as an uncalibrated `windy` world, and the RL environment replaces PX4 with its own controller. The CCWC claim of "reliable sim-to-real transfer" has not yet been measured [@ling2026].
- **Calibrate, then randomize.** First identify the vehicle from logs: mass, hover thrust, motor constants and sensor noise [@gronauer2022; @eschmann2024sysid; @quan2017]. Then randomize wind, mass, GNSS bias and delay in Monte Carlo SITL runs.
- **Keep the real stack in the loop.** Progress from SITL to simulation-in-hardware, then the bench, then the field [@px4sih; @jiang2025]. Validate any RL policy sim-to-sim in PX4 SITL before it touches hardware [@xu2026navrlpp].
- **Make transfer a number.** Pair every SITL run with a real run against independent ground truth. The semester should then end with measured sim-vs-real differences and, across conditions, a rank correlation [@kadian2020].
- **Expect these risks this semester.** Each one has a mitigation in Table 6:
  - waypoint offsets at the scale of GNSS error;
  - altitude errors near the ground;
  - wind;
  - compass interference;
  - link jitter;
  - battery sag;
  - very few flight opportunities.

---
