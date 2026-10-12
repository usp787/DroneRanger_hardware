"""Content of the brief (Canvas) literature review. Citations: [@key]; markup: <b>, <i>.

Entries are ('entry', (key, lead-in, paragraph)); the build script numbers them in order of first citation.
"""

TITLE = 'Sim-to-Real Transfer for DroneRanger: A Brief Literature Review'
AUTHOR = 'Jiarui Zha'
SUBJECT = 'Annotated literature review (IEEE style) on simulation-to-reality transfer for the DroneRanger UAV'
BYLINE = [
    'Jiarui Zha, zha.j@northeastern.edu',
    'CS 7980 Research Capstone, Northeastern University  ·  DroneRanger hardware group',
    'PI: Prof. Ilmi Yoon, NEURAI Lab  ·  October 11, 2026',
]

CONTENT = [
('h1', '1. Purpose'),
('p', 'DroneRanger is a low-cost autonomous drone being developed to patrol a household garden and, in the long run, '
      'to deter wildlife without contact. It is built on a Holybro X500 V2 airframe with PX4 on a Pixhawk 6C, an '
      'NVIDIA Jetson Orin Nano and an OAK-D Lite stereo camera. Its first paper claims that a single PX4–ROS 2 '
      'interface, shared by Gazebo, Unity and the real aircraft, “enables reliable simulation-to-reality '
      'transfer” [@ling2026]. The Spring 2026 prototype exposed what that interface had not been tested on '
      '[@yin2026]:'),
('bullets', ['about 0.5 m of altitude error near the ground;',
             'setpoints reported as reached while the drone was visibly offset;',
             'depth images with large invalid regions.']),
('p', 'This semester the hardware group will rehearse every mission in PX4 software-in-the-loop (SITL) simulation '
      'before flying it. The flight milestones are manual outdoor flight (O1) and then an autonomous Mission-mode '
      'patrol over the garden (O2). Meanwhile, the reinforcement-learning (RL) group trains a navigation policy in '
      'Isaac Lab. This brief asks one practical question of the literature: <i>where will DroneRanger’s '
      'simulators mislead it, and how can that gap be measured and narrowed?</i>'),

('h1', '2. Method'),
('p', 'I started from the project’s own reference library, then searched IEEE Xplore, the Science and Nature '
      'journals, arXiv and Google Scholar in October 2026. I kept peer-reviewed work that either addresses '
      'sim-to-real transfer directly or quantifies a gap that a small PX4 multirotor faces: ground effect, wind, '
      'sensing, model parameters, software testing and evaluation. Aerial robots and work from 2017–2026 were '
      'preferred. Journal articles were resolved through the Northeastern University Library’s LibKey service, '
      'and conference DOIs and the book were checked on Crossref.'),
('p', '<b>Citation management.</b> All entries are kept in a BibTeX file (references_brief.bib), which imports '
      'directly into Zotero, and are cited in IEEE style. A longer companion review covers {{N_COMPREHENSIVE}} '
      'sources.'),

('h1', '3. Annotated Sources'),
('h2', '3.1 Journal articles'),
('entry', ('aljalbout2026', 'The reality gap in robotics (Annu. Rev. Control Robot. Auton. Syst., 2026).',
   'This 2026 review is the most recent synthesis of the field. It traces the gap to four sources: dynamics; '
   'perception and sensing; actuation and control; and system design, which includes communication delay, '
   'control-frequency mismatch and privileged training signals. It also separates methods that <i>reduce</i> the gap '
   '(system identification, learned residuals, real-to-sim reconstruction) from methods that <i>overcome</i> it '
   '(randomization, adaptation, teacher–student training, modularity). <b>For DroneRanger:</b> all four sources '
   'are present. The X500 simulation model has no ground effect, and its depth camera has no noise. The RL '
   'environment replaces PX4 with a custom controller. Its policy decides at 50 Hz using ground truth that the '
   'real drone will not have, and it must eventually run over a serial link with real delays. The review is '
   'therefore a checklist for both the SITL twin and the RL hand-over.')),
('entry', ('kose2026', 'Sim-to-real discrepancies in PX4 flight logs (Sensors, 2026).',
   'The authors compared real PX4 flight logs with an untuned PX4 SITL simulation in Gazebo, both using the EKF2 '
   'estimator. Vertical-acceleration variance was about ten times larger in real flight (4.985 vs. 0.458), maximum '
   'tilt reached 72.1° instead of 24.0°, and GPS and magnetometer fluctuations appeared only in reality. The '
   'airframes and PX4 versions differed, which the authors flag as confounds. <b>For DroneRanger:</b> this is the '
   'closest published analogue to the hardware group’s SITL twin, with the same autopilot, simulator and '
   'estimator, and it shows that a default SITL model is optimistic. The twin must be tuned with the real X500’s '
   'parameters and noise before its predictions are trusted. Comparisons should use matched firmware versions.')),
('entry', ('kadian2020', 'Sim2Real predictivity (IEEE Robot. Autom. Lett., 2020).',
   'Nine navigation models were run both in a 3-D-scanned replica of a lab and on a real robot. The authors '
   'introduced the Sim-vs-Real Correlation Coefficient (SRCC) to measure how well simulated results predict real '
   'ones. The simulator used in a public challenge had an SRCC of only 0.18 for success, because agents exploited '
   'imperfect collision handling to slide along walls. Tuning the simulator raised the SRCC to 0.844. '
   '<b>For DroneRanger:</b> the CCWC paper asserts reliable transfer without any such measurement. Flying the same '
   'mission and parameter files in SITL and in the field, then comparing hover error, waypoint error and failsafe '
   'timing, turns that assertion into a number.')),
('entry', ('muratore2022', 'Robot learning from randomized simulations (Front. Robot. AI, 2022).',
   'This review organizes domain randomization into static, adaptive and adversarial variants. It concludes that '
   'policies trained with randomization are consistently more robust than policies trained on a single nominal '
   'model. It also warns that initial guesses of the simulator parameters and their variances are typically very '
   'inaccurate, and that the methods rarely work out of the box. <b>For DroneRanger:</b> the review gives a '
   'principled way to choose what to vary in Monte Carlo SITL runs: mass (the computer and camera add about '
   '0.37 kg), wind, GNSS bias and link delay. Its warning is a reason to ground those ranges in the hardware '
   'group\u2019s own flight logs first.')),
('entry', ('kaufmann2023', 'Champion-level drone racing (Nature, 2023).',
   'Swift, a quadrotor policy trained with deep RL, won 15 of 25 races against three world-champion pilots and set '
   'the fastest race time. Its simulator used an aerodynamic model fitted to flight data instead of randomizing the '
   'dynamics. After a few real runs recorded with motion capture, the team fitted residual models of two errors: '
   'drift in the visual–inertial odometry, using Gaussian processes, and unmodelled dynamics, using '
   'nearest-neighbour regression. They then fine-tuned the policy in the augmented simulator. <b>For '
   'DroneRanger:</b> a small amount of real data with independent ground truth made Swift’s simulator '
   'trustworthy. The equivalent here is to log every flight against rangefinder and ground-marker truth, and to '
   'feed the measured errors back into the SITL model.')),
('entry', ('loquercio2021', 'Learning high-speed flight in the wild (Sci. Robot., 2021).',
   'A quadrotor flew through forests, snow-covered terrain and ruins using a policy trained only in simulation. It '
   'transferred zero-shot: there were no crashes at 3 and 5 m/s, 8 of 10 runs succeeded at 7 m/s, and 60% '
   'succeeded at 10 m/s. Two choices made this possible. First, a privileged expert supervised a student that saw '
   'only onboard sensors. Second, the student’s training depth was computed by stereo matching on simulated '
   'image pairs, so it had the same kind of noise as the real stereo camera. <b>For DroneRanger:</b> its Gazebo and '
   'Isaac simulators render perfect depth. The OAK-D Lite, by contrast, returns invalid pixels below about 0.35 m '
   'and false far readings, so the depth interface given to the algorithm and RL groups should be simulated with '
   'these failure modes.')),
('entry', ('oconnell2022', 'Neural-Fly (Sci. Robot., 2022).',
   'Neural-Fly learned a wind-invariant representation of aerodynamic forces from 12 minutes of flight data and '
   'adapted only its output coefficients online. It outperformed nonlinear, INDI and L1-adaptive baselines in winds '
   'of up to 12.1 m/s. Its outdoor vehicle is close to DroneRanger in design: a Pixhawk running PX4 in Offboard mode '
   'under a companion computer, with GPS for position. <b>For DroneRanger:</b> wind is the largest dynamics gap '
   'that its default SITL worlds leave out. At San Jose airport, about one autumn day in five has a gust of 25 mph '
   'or more. Missions should therefore be rehearsed in PX4’s windy world, flights should have a gust go/no-go '
   'limit, and wind data should be logged for a later adaptive layer.')),
('entry', ('low2025', 'SOUS VIDE (IEEE Robot. Autom. Lett., 2025).',
   'SOUS VIDE built a drone simulator on a Gaussian-splatting reconstruction of a real scene, made from a '
   '2–3-minute hand-held video. A privileged, randomized expert controller was distilled into an onboard '
   'visuomotor policy with a rapid-adaptation module. In 105 hardware experiments the policy flew zero-shot and was '
   'robust to a 30% mass increase and to strong gusts; it failed only when the light fell below about 40% of the '
   'original level. It ran on the same companion computer as DroneRanger, a Jetson Orin Nano. <b>For '
   'DroneRanger:</b> it is the template for a future garden digital twin, which could replace the parking-lot scene '
   'now used in Isaac Sim. The twin is a static snapshot, though, and capture must stay inside the host property.')),

('h2', '3.2 Conference papers'),
('entry', ('ling2026', 'DroneRanger (IEEE CCWC, 2026).',
   'The project’s own paper presents the architecture under review. PX4 handles estimation and control, and '
   'ROS 2 handles mission logic. A Micro XRCE-DDS bridge exposes both through the same topics in Gazebo, in Unity '
   'and on the real aircraft. The architecture also includes a finite-state mission executive and depth-based '
   'avoidance. The paper validated behaviours qualitatively and listed latency audits, hardware-in-the-loop tests '
   'and multi-run statistics as future work. <b>For DroneRanger:</b> this review treats the paper’s transfer '
   'claim as the hypothesis this semester must test.')),
('entry', ('shi2019', 'Neural Lander (IEEE ICRA, 2019).',
   'Neural Lander learned the ground-effect force on a 1.47 kg quadrotor from flight data, using a spectrally '
   'normalized neural network. It added this force to a nonlinear controller with stability guarantees. Landing '
   'height error fell from 0.13 m to almost zero, and lateral drift fell by up to 90%. <b>For DroneRanger:</b> the '
   'Spring 2026 prototype had about 0.5 m of altitude error near 1 m above the ground, and the PX4 Gazebo X500 '
   'model has no ground-effect term at all. Near-ground altitude is therefore where SITL and flight will disagree '
   'first. The TFmini Plus rangefinder should be logged unfused, as independent truth, before it is fused into '
   'EKF2.')),
('entry', ('eschmann2024sysid', 'Data-driven system identification of quadrotors (IEEE/RSJ IROS, 2024).',
   'Eschmann et al. identified a quadrotor’s inertia, thrust curve, torque coefficient and motor delay from '
   'about one minute of ordinary flight data, without a thrust stand. They released a tool that reads PX4 ULog '
   'files. An RL policy trained in simulation on parameters from only 73 s of data then flew a 3.35 kg quadrotor '
   'outdoors in gusts of up to 8 m/s. <b>For DroneRanger:</b> this is the cheapest route from the real X500 to a '
   'calibrated Gazebo model. The logs of the first indoor hover tests can supply the thrust and motor-delay values '
   'that the default model only guesses.')),
('entry', ('timperley2018', 'Can simulation detect robotics bugs early? (IEEE ICST, 2018).',
   'Timperley et al. analysed 228 bug fixes in the ArduPilot autopilot. Only 10 of the bugs needed physical '
   'hardware to reproduce. Most could be triggered in software-in-the-loop simulation, provided the tests varied '
   'configurations and inputs, since configuration (81 bugs) and environment, such as wind (22 bugs), were the '
   'common triggers. <b>For DroneRanger:</b> this supports exercising every mission, parameter change and failsafe '
   'in PX4 SITL first (O0), with runs swept over parameter files and wind settings rather than run once. It also '
   'marks what SITL will miss: hardware faults and concurrency problems. Those need bench tests and staged field '
   'tests.')),

('h2', '3.3 Book'),
('entry', ('quan2017', 'Introduction to Multicopter Design and Control (Springer, 2017).',
   'This textbook models multicopters from first principles. It also devotes chapters to measuring what a '
   'simulator needs: propulsion-system modelling, the dynamic model and parameter measurement, sensor calibration '
   'and measurement models, Kalman filtering and state estimation, and health evaluation and failsafe design. '
   '<b>For DroneRanger:</b> it is the manual for the “identify before you randomize” step: weighing the '
   'roughly 2.1 kg aircraft, fitting thrust and motor time constants, and characterizing IMU, barometer and GNSS '
   'noise, so that the Gazebo X500 model matches the real vehicle.')),

('h1', '4. Synthesis for DroneRanger'),
('p', 'The sources agree on three points. First, transfer improves when the simulator is calibrated with a small '
      'amount of real data [@kaufmann2023; @shi2019; @eschmann2024sysid; @quan2017]. Second, the uncertainty that '
      'remains should be randomized [@muratore2022]. Third, transfer has to be measured rather than assumed '
      '[@kadian2020; @kose2026; @aljalbout2026]. Table 1 maps these lessons onto this semester.'),
('table', ('Table 1. Sim-to-real gaps for DroneRanger and the semester response.',
   [1.4, 0.95, 2.95, 1.7],
   ['Gap', 'Evidence', 'Response this semester', 'Measured by'],
   [['Ground effect and altitude', '[@shi2019; @kose2026]',
     'Log the TFmini Plus unfused as truth, then fuse it in EKF2; compare near-ground hover in SITL and in flight',
     'Hover altitude RMSE ≤ 0.15 m'],
    ['Model parameters', '[@eschmann2024sysid; @quan2017]',
     'Identify mass, thrust and motor delay from flight logs; update the Gazebo X500 model',
     'Hover throttle and step response, sim vs. real'],
    ['Wind', '[@oconnell2022]', 'Rehearse in the windy world; set a gust go/no-go limit; log wind',
     'Tracking error vs. gust'],
    ['Depth and GNSS sensing', '[@loquercio2021; @kaufmann2023]',
     'Model invalid depth and GNSS bias from logs; judge waypoints against surveyed markers',
     'Invalid-pixel fraction; waypoint error'],
    ['Software, timing and control stack', '[@timperley2018; @aljalbout2026]',
     'Run every mission and failsafe in SITL; bench-test the serial link; run the RL policy through PX4 SITL',
     'Faults caught before flight; latency distribution'],
    ['What to randomize', '[@muratore2022]', 'Monte Carlo SITL over wind, mass, GNSS bias and delay',
     'Geofence margin; mission success rate'],
    ['Evaluating the claim', '[@kadian2020; @ling2026]',
     'Pair every SITL run with a real run, with at least ten trials per metric', 'Sim–real difference per metric'],
    ['Garden scene (future)', '[@low2025]', 'Capture a splat twin of the host garden only', '—']])),
('p', 'For the hardware group, simulation stays the first gate: no mission flies until it has passed SITL. But '
      'simulation is not the final word. What this semester can claim is the measured difference between SITL and '
      'the garden, and narrowing that difference with real data is the platform’s contribution to the RL policy '
      'and, later, to learned deterrence.'),
]
