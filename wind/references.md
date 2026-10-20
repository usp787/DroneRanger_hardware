# Wind + drone reference list

89 references, numbered as in [Wind_Sim_Feasibility.md](Wind_Sim_Feasibility.md) (IEEE style, order of first citation). Breakdown: 47 journal articles, 17 documentation pages, 12 conference papers, 4 reports and standards, 4 software repositories, 2 preprints, 2 book chapters, 1 book. 19 entries are shared with [../sim2real/references.md](../sim2real/references.md) and keep the same citation keys.

- **Verification (2026-10-19).** Every journal article was resolved through LibKey (Northeastern University Library): 📄 opens the library PDF, 🔗 *View Article* the article page, 🔗 *Access Options* the library link resolver (sign-in may be required). Conference papers, chapters, books and reports were checked on Crossref or the publisher; preprints on arXiv.
- **Peer review.** *Preprint* entries had not completed peer review when checked; *Documentation* entries describe software behaviour, not research results.
- **Themes.** **T0** DroneRanger and wind data sources; **T1** atmospheric wind and turbulence models; **T2** low-altitude urban and suburban wind; **T3** multirotor aerodynamics in wind; **T4** wind estimation from multirotor motion; **T5** control and learning for wind rejection; **T6** simulators and wind injection; **T7** weather as an operational constraint.
- **Citation manager.** Import [references.bib](references.bib) into Zotero with *File → Import…* (e.g. into a *DroneRanger wind* collection) and pick the IEEE style.
- **Local copies.** Open-access PDFs and saved documentation pages are in the git-ignored `reference/08_wind_simulation/` folder (see its `NOTES.md`).

**[1]** R. Yin, “Drone project technical handover: PX4 / ROS 2 / OAK-D Lite autonomous flight and obstacle-aware planning system,” NEURAI Lab, Northeastern Univ., San Jose, CA, USA, Internal tech. rep., 2026.  
*Report or standard* · T0 · `yin2026` · no DOI  
Spring 2026 handover: MAVSDK-Python, then ROS 2 offboard over uXRCE-DDS on the Jetson.

**[2]** RipZou, “DroneRangerIssac,” GitHub repository, commit 5acbe7b, Mar. 2026. [Online]. Available: https://github.com/RipZou/DroneRangerIssac  
*Software repository* · T0 · `ripzou2026isaac` · [link](https://github.com/RipZou/DroneRangerIssac)  
Legacy Isaac Sim 5.1 + Pegasus 5.1 + PX4 v1.14.3 setup that the Isaac path would build on.

**[3]** M. Jacinto *et al.*, “Pegasus Simulator: An Isaac Sim framework for multiple aerial vehicles simulation,” in *Proc. Int. Conf. Unmanned Aircraft Syst. (ICUAS)*, 2024, pp. 917–922, doi: 10.1109/ICUAS60882.2024.10556959.  
*Conference paper* · T6 · `jacinto2024` · [doi:10.1109/ICUAS60882.2024.10556959](https://doi.org/10.1109/ICUAS60882.2024.10556959)  
Pegasus: Isaac Sim + PX4/ArduPilot via MAVLink HIL; the legacy Isaac stack.

**[4]** Z. Ling *et al.*, “DroneRanger: Simulation-guided UAV framework for autonomous wildlife deterrence,” in *Proc. IEEE 16th Annu. Comput. Commun. Workshop Conf. (CCWC)*, 2026, pp. 1221–1227, doi: 10.1109/CCWC67433.2026.11393823.  
*Conference paper* · T0 · `ling2026` · [doi:10.1109/CCWC67433.2026.11393823](https://doi.org/10.1109/CCWC67433.2026.11393823)  
The published DroneRanger framework (Gazebo/Unity + PX4 + ROS 2) that this work extends.

**[5]** Iowa Environmental Mesonet, “ASOS one minute data download,” *Iowa State University*. Accessed: Oct. 19, 2026. [Online]. Available: https://mesonet.agron.iastate.edu/request/asos/1min.phtml  
*Documentation* · T0 · `iem1min` · [link](https://mesonet.agron.iastate.edu/request/asos/1min.phtml)  
Free CSV access to NCEI ASOS 1-minute data; source of the 218k SJC records used here.

**[6]** NOAA National Centers for Environmental Information, “ASOS surface 1-minute, page 1 data (TD-6405) format documentation,” *NCEI data archive*. Accessed: Oct. 19, 2026. [Online]. Available: https://www.ncei.noaa.gov/pub/data/asos-onemin/td6405.txt  
*Documentation* · T0 · `ncei6405` · [link](https://www.ncei.noaa.gov/pub/data/asos-onemin/td6405.txt)  
Defines the 1-minute fields: 2-minute average wind and the maximum 5-second average gust.

**[7]** National Oceanic and Atmospheric Administration, Department of Defense, Federal Aviation Administration, and United States Navy, “Automated Surface Observing System (ASOS) user's guide,” National Oceanic and Atmospheric Administration, User guide, Mar. 1998. [Online]. Available: https://www.weather.gov/media/asos/aum-toc.pdf  
*Report or standard* · T7 · `asos1998` · [link](https://www.weather.gov/media/asos/aum-toc.pdf)  
Defines the observations: 2-min average wind from a sensor nominally at 10 m; the gust is the highest 5-s average of 1-s samples. In METAR a gust is reported only when it exceeds the 10-min lull by >= 10 kt (minimum 14 kt), so most light-wind San Jose hours carry no gust; the 1-minute archive, used here, gives the peak 5-s gust of every minute.

**[8]** Iowa Environmental Mesonet, “ASOS-AWOS-METAR data download,” *Iowa State University*. Accessed: Oct. 19, 2026. [Online]. Available: https://mesonet.agron.iastate.edu/request/download.phtml  
*Documentation* · T0 · `iemasos` · [link](https://mesonet.agron.iastate.edu/request/download.phtml)  
Hourly METAR for SJC, Reid-Hillview, Moffett and Palo Alto used for the station comparison.

**[9]** Open-Meteo, “Historical weather API,” *Open-Meteo documentation*. Accessed: Oct. 19, 2026. [Online]. Available: https://open-meteo.com/en/docs/historical-weather-api  
*Documentation* · T0 · `openmeteo` · [link](https://open-meteo.com/en/docs/historical-weather-api)  
Gridded reanalysis wind at any point (9-25 km grids); read ~35 % below SJC here.

**[10]** California Department of Water Resources, “CIMIS station list (web API),” *California Irrigation Management Information System*. Accessed: Oct. 19, 2026. [Online]. Available: https://et.water.ca.gov/api/station  
*Documentation* · T0 · `cimis` · [link](https://et.water.ca.gov/api/station)  
2 m agricultural wind stations; the San Jose station (#69) closed in 2002, nearest active 25-40 km.

**[11]** J. Wieringa, “Roughness-dependent geographical interpolation of surface wind speed averages,” *Q. J. R. Meteorol. Soc.*, vol. 112, no. 473, pp. 867–889, Jul. 1986, doi: 10.1002/qj.49711247316.  
*Journal article* · T2 · `wieringa1986` · [🔗 **Access Options**](https://libkey.io/libraries/545/10.1002/qj.49711247316) · [doi:10.1002/qj.49711247316](https://doi.org/10.1002/qj.49711247316)  
Standard method for moving station wind to a site of different roughness via a blending height; used for the airport-to-garden factor.

**[12]** M. Roth, “Review of atmospheric turbulence over cities,” *Q. J. R. Meteorol. Soc.*, vol. 126, no. 564, pp. 941–990, Apr. 2000, doi: 10.1002/qj.49712656409.  
*Journal article* · T2 · `roth2000` · [🔗 **Access Options**](https://libkey.io/libraries/545/10.1002/qj.49712656409) · [doi:10.1002/qj.49712656409](https://doi.org/10.1002/qj.49712656409)  
Review of >50 urban turbulence studies: a roughness sublayer extends to about 2.5-3 times building height, and inside it standard surface-layer (log-law) methods are in doubt. With 1-2 storey houses the whole 3-10 m DroneRanger band lies inside this layer, so airport wind cannot simply be log-scaled down to the garden.

**[13]** U.S. Department of Defense, “Military specification: Flying qualities of piloted airplanes,” U.S. Department of Defense, Washington, DC, USA, Military specification MIL-F-8785C, Nov. 1980.  
*Report or standard* · T1 · `milf8785c` · [link](https://everyspec.com/MIL-SPECS/MIL-SPECS-MIL-F/MIL-F-8785C_5295/)  
Source of the Dryden and von Karman turbulence forms later used by Simulink and RotorPy; its low-altitude model (Sec. 3.7.3, valid 10 ft < h < 1000 ft) sets sigma_w = 0.1*u20 (u20 = mean wind at 20 ft), gives horizontal intensities and scale lengths as functions of h through (0.177 + 0.000823h), and a log mean-wind profile scaled from 20 ft with z0 = 0.15 ft or 2.0 ft. Gives DroneRanger a citable recipe for turning an hourly mean wind into turbulence at 3-10 m (Notice 2, 1996, marks it inactive for new design).

**[14]** P. Abichandani, D. Lobo, G. Ford, D. Bucci, and M. Kam, “Wind measurement and simulation techniques in multi-rotor small unmanned aerial vehicles,” *IEEE Access*, vol. 8, pp. 54910–54927, Mar. 2020, doi: 10.1109/ACCESS.2020.2977693.  
*Journal article* · T1 · `abichandani2020` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/374333711/full-text-file?utm_source=api_4212&allow_speedbump=true) (Open Access) · [doi:10.1109/ACCESS.2020.2977693](https://doi.org/10.1109/ACCESS.2020.2977693)  
Review of multirotor wind sensing (flow sensors, anemometers, tilt-angle methods) and wind simulation (PSD/Dryden-von Karman, discrete gusts, CFD, probabilistic models), with open-source Python Dryden code; the most direct starting point for the DroneRanger wind-injection module.

**[15]** G. I. Taylor, “The spectrum of turbulence,” *Proc. R. Soc. Lond. A*, vol. 164, no. 919, pp. 476–490, Feb. 1938, doi: 10.1098/rspa.1938.0032.  
*Journal article* · T1 · `taylor1938` · [🔗 **Access Options**](https://libkey.io/libraries/545/10.1098/rspa.1938.0032) · [doi:10.1098/rspa.1938.0032](https://doi.org/10.1098/rspa.1938.0032)  
Frozen-turbulence hypothesis: eddies advected at the mean wind, which lets Dryden spectra be used for a hovering drone.

**[16]** PegasusSimulator, “Pegasus Simulator,” GitHub repository, tag v5.1.0, Oct. 2025. [Online]. Available: https://github.com/PegasusSimulator/PegasusSimulator  
*Software repository* · T6 · `pegasussrc` · [link](https://github.com/PegasusSimulator/PegasusSimulator)  
Source check: LinearDrag uses ground-relative velocity, no wind model; Drag subclass is the hook.

**[17]** BerkeCanGoktas, “How to add wind in headless scripts? (issue #132),” *PegasusSimulator GitHub issues*. Accessed: Oct. 19, 2026. [Online]. Available: https://github.com/PegasusSimulator/PegasusSimulator/issues/132  
*Documentation* · T6 · `pegasus132` · [link](https://github.com/PegasusSimulator/PegasusSimulator/issues/132)  
Open user request; workaround applies a force in a physics callback.

**[18]** PX4 Autopilot, “Gazebo simulation,” *PX4 User Guide (main)*. Accessed: Sep. 27, 2026. [Online]. Available: https://docs.px4.io/main/en/sim_gazebo_gz/  
*Documentation* · T6 · `px4gz` · [link](https://docs.px4.io/main/en/sim_gazebo_gz/)  
PX4 Gazebo (gz) SITL, including the x500 and world selection.

**[19]** Open Robotics, “WindEffects system (source),” *gz-sim repository, branch gz-sim8*. Accessed: Oct. 19, 2026. [Online]. Available: https://github.com/gazebosim/gz-sim/blob/gz-sim8/src/systems/wind_effects/WindEffects.cc  
*Documentation* · T6 · `gzwindeffects` · [link](https://github.com/gazebosim/gz-sim/blob/gz-sim8/src/systems/wind_effects/WindEffects.cc)  
Force = mass x gain x (v_wind - v_link) on links with enable_wind; wind settable on /world/<w>/wind.

**[20]** PX4 Autopilot, “windy.sdf world,” *PX4-gazebo-models repository (main)*. Accessed: Oct. 19, 2026. [Online]. Available: https://github.com/PX4/PX4-gazebo-models/blob/main/worlds/windy.sdf  
*Documentation* · T6 · `px4windy` · [link](https://github.com/PX4/PX4-gazebo-models/blob/main/worlds/windy.sdf)  
Official windy world: constant 5, 2, 0 m/s wind, no plugins of its own.

**[21]** Open Robotics, “MulticopterMotorModel system (source),” *gz-sim repository, branch gz-sim8*. Accessed: Oct. 19, 2026. [Online]. Available: https://github.com/gazebosim/gz-sim/blob/gz-sim8/src/systems/multicopter_motor_model/MulticopterMotorModel.cc  
*Documentation* · T6 · `gzmotormodel` · [link](https://github.com/gazebosim/gz-sim/blob/gz-sim8/src/systems/multicopter_motor_model/MulticopterMotorModel.cc)  
Rotor drag uses body velocity minus wind: the only path by which wind reaches the stock x500.

**[22]** PX4 Autopilot, “fix(simulation): make wind affect the airspeed sensor in gz (pull request #28042),” *PX4-Autopilot GitHub, merged 2026-07-22*. Accessed: Oct. 19, 2026. [Online]. Available: https://github.com/PX4/PX4-Autopilot/pull/28042  
*Documentation* · T6 · `px4pr28042` · [link](https://github.com/PX4/PX4-Autopilot/pull/28042)  
Loads WindEffects in the PX4 gz server config on main; not in v1.17.0.

**[23]** PX4 Autopilot, “feat: add real wind effect on multicopter-like models with WindEffects gz plugin (pull request #130),” *PX4-gazebo-models GitHub, open*. Accessed: Oct. 19, 2026. [Online]. Available: https://github.com/PX4/PX4-gazebo-models/pull/130  
*Documentation* · T6 · `px4pr130` · [link](https://github.com/PX4/PX4-gazebo-models/pull/130)  
Adds enable_wind to the x500 base link; example gz.msgs.Wind command.

**[24]** PX4 Autopilot, “Simulation-in-hardware (SIH),” *PX4 User Guide (main)*. Accessed: Oct. 19, 2026. [Online]. Available: https://docs.px4.io/main/en/sim_sih/  
*Documentation* · T6 · `px4sihmain` · [link](https://docs.px4.io/main/en/sim_sih/)  
SIH_WIND_N/E wind, changeable during flight (main and v1.18-rc1; not in v1.17.0).

**[25]** S. Folk, J. Paulos, and V. Kumar, “RotorPy: A Python-based multirotor simulator with aerodynamics for education and research,” Jun. 2023, arXiv:2306.04485.  
*Preprint (not peer reviewed)* · T6 · `folk2023rotorpy` · [arXiv:2306.04485](https://arxiv.org/abs/2306.04485) · [link](https://arxiv.org/abs/2306.04485)  
Pure-Python 6-DoF multirotor sim with aerodynamic wrenches, actuator limits, sensors and wind as an extra state (step, sinusoid and Dryden profiles), benchmarked against Crazyflie data and used to design a UKF wind estimator. Contributed paper at the ICRA 2023 UAV-simulator workshop; PX4 docs list it as a community-supported simulator. Fast sandbox for prototyping ASOS-driven wind before porting to Gazebo/Isaac.

**[26]** spencerfolk, “RotorPy,” GitHub repository, PyPI release 3.0.0, Sep. 2026. [Online]. Available: https://github.com/spencerfolk/rotorpy  
*Software repository* · T6 · `rotorpysrc` · [link](https://github.com/spencerfolk/rotorpy)  
MIT-licensed; air-relative aerodynamics, Dryden wind, optional PX4 HIL bridge; used for the demo.

**[27]** B. Xu, F. Gao, C. Yu, R. Zhang, Y. Wu, and Y. Wang, “OmniDrones: An efficient and flexible platform for reinforcement learning in drone control,” *IEEE Robot. Autom. Lett.*, vol. 9, no. 3, pp. 2838–2844, Mar. 2024, doi: 10.1109/LRA.2024.3356168.  
*Journal article* · T6 · `xu2024omnidrones` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/602259224/full-text-file?utm_source=api_4212&allow_speedbump=true) · [doi:10.1109/LRA.2024.3356168](https://doi.org/10.1109/LRA.2024.3356168)  
OmniDrones (Isaac): wind only as random sinusoidal forces in its tracking task.

**[28]** M. Kulkarni, W. Rehberg, and K. Alexis, “Aerial Gym Simulator: A framework for highly parallelized simulation of aerial robots,” *IEEE Robot. Autom. Lett.*, vol. 10, no. 4, pp. 4093–4100, Apr. 2025, doi: 10.1109/LRA.2025.3548507.  
*Journal article* · T6 · `kulkarni2025` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/655687250/full-text-file?utm_source=api_4212&allow_speedbump=true) · [doi:10.1109/LRA.2025.3548507](https://doi.org/10.1109/LRA.2025.3548507)  
Aerial Gym: random force/torque disturbances, no air-relative wind.

**[29]** S. Shah, D. Dey, C. Lovett, and A. Kapoor, “AirSim: High-fidelity visual and physical simulation for autonomous vehicles,” in *Field and Service Robotics*, ser. Springer Proceedings in Advanced Robotics, vol. 5. Cham, Switzerland: Springer, 2018, pp. 621–635, doi: 10.1007/978-3-319-67361-5_40.  
*Book chapter* · T6 · `shah2018` · [doi:10.1007/978-3-319-67361-5_40](https://doi.org/10.1007/978-3-319-67361-5_40)  
AirSim: has a simSetWind API; the project is being archived.

**[30]** PX4 Autopilot, “gazebo_wind_plugin.cpp,” *PX4-SITL_gazebo-classic repository (main)*. Accessed: Oct. 19, 2026. [Online]. Available: https://github.com/PX4/PX4-SITL_gazebo-classic/blob/main/src/gazebo_wind_plugin.cpp  
*Documentation* · T6 · `gzclassicwind` · [link](https://github.com/PX4/PX4-SITL_gazebo-classic/blob/main/src/gazebo_wind_plugin.cpp)  
Mean + variance + one gust window + ramp; no wind-from-file input.

**[31]** F. Furrer, M. Burri, M. Achtelik, and R. Siegwart, “RotorS—A modular Gazebo MAV simulator framework,” in *Robot Operating System (ROS): The Complete Reference (Volume 1)*, A. Koubaa, Ed., ser. Studies in Computational Intelligence, vol. 625. Cham, Switzerland: Springer, 2016, pp. 595–625, doi: 10.1007/978-3-319-26054-9_23.  
*Book chapter* · T6 · `furrer2016` · [doi:10.1007/978-3-319-26054-9_23](https://doi.org/10.1007/978-3-319-26054-9_23)  
RotorS: the Gazebo MAV framework whose wind plugin PX4 inherited.

**[32]** Open Robotics, “Gazebo Classic and Citadel end of life,” *Open Robotics Discourse*. Accessed: Oct. 19, 2026. [Online]. Available: https://discourse.openrobotics.org/t/gazebo-classic-and-citadel-end-of-life/48152  
*Documentation* · T6 · `gzclassiceol` · [link](https://discourse.openrobotics.org/t/gazebo-classic-and-citadel-end-of-life/48152)  
Gazebo Classic end of life: 31 January 2025.

**[33]** charlotte-visionlab, “px4_gazebo_wind3d,” GitHub repository, 2025. [Online]. Available: https://github.com/charlotte-visionlab/px4_gazebo_wind3d  
*Software repository* · T6 · `wind3d` · [link](https://github.com/charlotte-visionlab/px4_gazebo_wind3d)  
Only open tool found that loads a (static, CFD) wind field into PX4 SITL; Gazebo Classic.

**[34]** PX4 Autopilot, “Using PX4's navigation filter (EKF2),” *PX4 User Guide (v1.17)*. Accessed: Sep. 27, 2026. [Online]. Available: https://docs.px4.io/v1.17/en/advanced_config/tuning_the_ecl_ekf.html  
*Documentation* · T4 · `px4ekf2` · [link](https://docs.px4.io/v1.17/en/advanced_config/tuning_the_ecl_ekf.html)  
EKF2 can estimate N/E wind on multirotors by fusing drag specific forces (EKF2_DRAG_CTRL, ballistic coefficients EKF2_BCOEF_X/Y, momentum drag EKF2_MCOEF), tuned from a back-and-forth flight log; enabling it gives a logged wind estimate on every real flight.

**[35]** PX4 Autopilot, “Commander parameters (commander_params.c),” *PX4-Autopilot repository, tag v1.17.0*. Accessed: Oct. 19, 2026. [Online]. Available: https://github.com/PX4/PX4-Autopilot/blob/v1.17.0/src/modules/commander/commander_params.c  
*Documentation* · T7 · `px4commander` · [link](https://github.com/PX4/PX4-Autopilot/blob/v1.17.0/src/modules/commander/commander_params.c)  
COM_WIND_WARN (v1.13+), COM_WIND_MAX (v1.14+), COM_WIND_MAX_ACT (v1.15+); all disabled by default.

**[36]** U.S. Department of Defense, “Department of Defense handbook: Flying qualities of piloted aircraft,” U.S. Department of Defense, Washington, DC, USA, Military handbook MIL-HDBK-1797, Dec. 1997.  
*Report or standard* · T1 · `milhdbk1797` · [link](https://everyspec.com/MIL-HDBK/MIL-HDBK-1500-1799/MIL-HDBK-1797_NOTICE-1_39380/)  
Successor guidance to MIL-F-8785C whose Dryden/von Karman PSDs (tabulated by Abichandani et al.) and scale-length choices are implemented, e.g., by the Simulink Dryden/von Karman wind blocks; cancelled by Notice 1 (24 Aug. 2004) and superseded by MIL-STD-1797A. Cite alongside MIL-F-8785C when stating which turbulence spectrum the DroneRanger wind plugin uses.

**[37]** R. B. Stull, *An Introduction to Boundary Layer Meteorology*. Dordrecht, The Netherlands: Springer, 1988, doi: 10.1007/978-94-009-3027-8.  
*Book* · T1 · `stull1988` · [doi:10.1007/978-94-009-3027-8](https://doi.org/10.1007/978-94-009-3027-8)  
Standard text for the surface-layer log wind profile and roughness length used to translate a 10 m airport wind to other heights; DroneRanger should cite it when it extrapolates ASOS winds to 3-10 m (valid only above the roughness sublayer, see roth2000).

**[38]** T. R. Beal, “Digital simulation of atmospheric turbulence for Dryden and von Karman models,” *J. Guid. Control Dyn.*, vol. 16, no. 1, pp. 132–138, Jan. 1993, doi: 10.2514/3.11437.  
*Journal article* · T1 · `beal1993` · [🔗 **Access Options**](https://libkey.io/libraries/545/10.2514/3.11437) · [doi:10.2514/3.11437](https://doi.org/10.2514/3.11437)  
Classic recipe for generating Dryden/von Karman gust time series by shaping white noise with discrete filters; this is the step DroneRanger needs to superimpose turbulence on a replayed ASOS hourly mean inside a fixed-step simulator.

**[39]** S. Watkins, J. Milbank, B. J. Loxton, and W. H. Melbourne, “Atmospheric winds and their implications for microair vehicles,” *AIAA J.*, vol. 44, no. 11, pp. 2591–2600, Nov. 2006, doi: 10.2514/1.22670.  
*Journal article* · T1 · `watkins2006` · [🔗 **Access Options**](https://libkey.io/libraries/545/10.2514/1.22670) · [doi:10.2514/1.22670](https://doi.org/10.2514/1.22670)  
Measured turbulence 4 m above ground with multi-hole probes 150 and 50 mm apart on a mast above a car: flow-pitch variation decays only slowly as span shrinks, so small vehicles see large roll inputs from vertical gusts. Argues that a single-point (uniform) wind vector, as in most simulators, under-represents what a 3-10 m drone actually feels.

**[40]** J. Finnigan, “Turbulence in plant canopies,” *Annu. Rev. Fluid Mech.*, vol. 32, pp. 519–571, 2000, doi: 10.1146/annurev.fluid.32.1.519.  
*Journal article* · T2 · `finnigan2000` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/47131720/full-text-file?utm_source=api_4212&allow_speedbump=true) · [doi:10.1146/annurev.fluid.32.1.519](https://doi.org/10.1146/annurev.fluid.32.1.519)  
Within and just above vegetation the mean profile is inflected, turbulence is dominated by large coherent sweeps and behaves like a plane mixing layer rather than a boundary layer; relevant for flight beside garden trees, where Dryden assumptions (homogeneous, Gaussian) break down.

**[41]** C. S. B. Grimmond and T. R. Oke, “Aerodynamic properties of urban areas derived from analysis of surface form,” *J. Appl. Meteorol.*, vol. 38, no. 9, pp. 1262–1292, Sep. 1999, doi: 10.1175/1520-0450(1999)038<1262:APOUAD>2.0.CO;2.  
*Journal article* · T2 · `grimmond1999` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/45506332/full-text-file?utm_source=api_4212&allow_speedbump=true) · [doi:10.1175/1520-0450(1999)038<1262:APOUAD>2.0.CO;2](https://doi.org/10.1175/1520-0450(1999)038<1262:APOUAD>2.0.CO;2)  
Morphometric formulas for zero-plane displacement and roughness length from building/tree height and density, tested on 11 North American sites, most of them residential suburbs; the paper to use for estimating z_d and z_0 of the San Jose garden neighbourhood before any log-law extrapolation.

**[42]** J. Wieringa, “Representative roughness parameters for homogeneous terrain,” *Boundary-Layer Meteorol.*, vol. 63, no. 4, pp. 323–363, Mar. 1993, doi: 10.1007/BF00705357.  
*Journal article* · T2 · `wieringa1993` · [🔗 **Access Options**](https://libkey.io/libraries/545/10.1007/BF00705357) · [doi:10.1007/BF00705357](https://doi.org/10.1007/BF00705357)  
Critical review of measured roughness lengths for homogeneous terrain types; the standard source for z0 of open, airport-like terrain when height-correcting a 10 m station wind. (Crossref spells the author "Wiernga".)

**[43]** A. Mohamed, M. Marino, S. Watkins, J. Jaworski, and A. Jones, “Gusts encountered by flying vehicles in proximity to buildings,” *Drones*, vol. 7, no. 1, Art. no. 22, 2023, doi: 10.3390/drones7010022.  
*Journal article* · T2 · `mohamed2023` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/541936308/full-text-file?utm_source=api_4212&allow_speedbump=true) (Open Access) · [doi:10.3390/drones7010022](https://doi.org/10.3390/drones7010022)  
Reviews Dryden/von Karman and other gust models, then flies idealised trajectories through an LES field over a cuboid building in a suburban boundary layer (3 m/s reference wind at 10 m): crossing the roof shear layer at 5 m/s gives ~20 deg change in relative flow angle and ~50 % jump in airspeed within 0.25 s. Shows building-induced gusts are spatial, sharp and not captured by isotropic models.

**[44]** D. Galway, J. Etele, and G. Fusina, “Modeling of urban wind field effects on unmanned rotorcraft flight,” *J. Aircr.*, vol. 48, no. 5, pp. 1613–1620, Sep. 2011, doi: 10.2514/1.C031325.  
*Journal article* · T2 · `galway2011` · [🔗 **Access Options**](https://libkey.io/libraries/545/10.2514/1.C031325) · [doi:10.2514/1.C031325](https://doi.org/10.2514/1.C031325)  
Builds a database of CFD building wakes and switches them on when the simulated rotorcraft enters a wake; for a Yamaha R-50 helicopter a light 8 kt (~4 m/s) wind already produced attitude excursions up to 10 deg. A low-cost template for adding house wakes to a DroneRanger sim without full-domain CFD.

**[45]** S. Watkins *et al.*, “Ten questions concerning the use of drones in urban environments,” *Build. Environ.*, vol. 167, Art. no. 106458, Jan. 2020, doi: 10.1016/j.buildenv.2019.106458.  
*Journal article* · T2 · `watkins2020` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/351723423/full-text-file?utm_source=api_4212&allow_speedbump=true) · [doi:10.1016/j.buildenv.2019.106458](https://doi.org/10.1016/j.buildenv.2019.106458)  
Review naming inability to fly well in adverse weather (urban wind/turbulence) as a key inhibitor of urban drone use, and comparing with how birds/insects cope; frames why a backyard among houses is a harder wind environment than the open-field tests most papers use.

**[46]** J. Ware and N. Roy, “An analysis of wind field estimation and exploitation for quadrotor flight in the urban canopy layer,” in *Proc. IEEE Int. Conf. Robot. Autom. (ICRA)*, 2016, pp. 1507–1514, doi: 10.1109/ICRA.2016.7487287.  
*Conference paper* · T2 · `ware2016` · [doi:10.1109/ICRA.2016.7487287](https://doi.org/10.1109/ICRA.2016.7487287)  
Drives a CFD solver with only the prevailing (above-canopy) wind speed and heading to predict the urban wind field, then plans minimum-energy quadrotor paths; wind-aware plans cut flight time, energy and over-airspeed failures across the MIT campus. Same idea as replaying ASOS as a boundary condition.

**[47]** S. Giersch, O. El Guernaoui, S. Raasch, M. Sauer, and M. Palomar, “Atmospheric flow simulation strategies to assess turbulent wind conditions for safe drone operations in urban environments,” *J. Wind Eng. Ind. Aerodyn.*, vol. 229, Art. no. 105136, Oct. 2022, doi: 10.1016/j.jweia.2022.105136.  
*Journal article* · T2 · `giersch2022` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/533497874/full-text-file?utm_source=api_4212&allow_speedbump=true) · [doi:10.1016/j.jweia.2022.105136](https://doi.org/10.1016/j.jweia.2022.105136)  
PALM large-eddy simulations resolving buildings down to metre scale argue that turbulence-resolving models are necessary to plan urban drone operations and recommend a pre-computed meteorological database per site; supports a precomputed-LES-lookup design over live CFD for DroneRanger. (Publisher open access, CC BY, although LibKey flags it as not OA.)

**[48]** S. Folk, J. Melton, B. W. L. Margolis, M. Yim, and V. Kumar, “Learning local urban wind flow fields from range sensing,” *IEEE Robot. Autom. Lett.*, vol. 9, no. 9, pp. 7413–7420, Sep. 2024, doi: 10.1109/LRA.2024.3426209.  
*Journal article* · T2 · `folk2024` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/622312571/full-text-file?utm_source=api_4212&allow_speedbump=true) · [doi:10.1109/LRA.2024.3426209](https://doi.org/10.1109/LRA.2024.3426209)  
A network trained on simulated winds through small random maps predicts the local flow around a robot from onboard range data plus sparse wind measurements, generalising to scenes with >200 buildings; points to a learned "house-wake" surrogate as a cheaper alternative to per-site CFD.

**[49]** M. Gianfelice, H. Aboshosha, and T. Ghazal, “Real-time wind predictions for safe drone flights in Toronto,” *Results Eng.*, vol. 15, Art. no. 100534, Sep. 2022, doi: 10.1016/j.rineng.2022.100534.  
*Journal article* · T6 · `gianfelice2022` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/594255656/full-text-file?utm_source=api_4212&allow_speedbump=true) (Open Access) · [doi:10.1016/j.rineng.2022.100534](https://doi.org/10.1016/j.rineng.2022.100534)  
Couples zone-wise CFD of downtown Toronto with historical/real-time meteorological station data; CFD-transferred speed and bearing were within 12 % and 8 % RMSE of station records for 85 % of samples. Demonstrates the "met-station wind -> CFD transfer -> local wind" chain DroneRanger needs for ASOS replay.

**[50]** R. Mahony, V. Kumar, and P. Corke, “Multirotor aerial vehicles: Modeling, estimation, and control of quadrotor,” *IEEE Robot. Autom. Mag.*, vol. 19, no. 3, pp. 20–32, Sep. 2012, doi: 10.1109/MRA.2012.2206474.  
*Journal article* · T3 · `mahony2012` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/18873402/full-text-file?utm_source=api_4212&allow_speedbump=true) · [doi:10.1109/MRA.2012.2206474](https://doi.org/10.1109/MRA.2012.2206474)  
Tutorial model of quadrotor dynamics including blade flapping and induced drag, which make the rotor drag roughly linear in air-relative velocity; the term a simulator needs so that wind (not just ground velocity) produces force on the airframe.

**[51]** G. Hoffmann, H. Huang, S. Waslander, and C. Tomlin, “Quadrotor helicopter flight dynamics and control: Theory and experiment,” in *Proc. AIAA Guid. Navig. Control Conf. Exhib.*, 2007, Art. no. AIAA 2007-6461, doi: 10.2514/6.2007-6461.  
*Conference paper* · T3 · `hoffmann2007` · [doi:10.2514/6.2007-6461](https://doi.org/10.2514/6.2007-6461)  
Analyses three aerodynamic effects away from hover (due to vehicle velocity, angle of attack and airframe design) that cause attitude moments and thrust variation, validated on a thrust stand and the STARMAC quadrotor; these airspeed-dependent terms are what a wind simulation must drive.

**[52]** M. Faessler, A. Franchi, and D. Scaramuzza, “Differential flatness of quadrotor dynamics subject to rotor drag for accurate tracking of high-speed trajectories,” *IEEE Robot. Autom. Lett.*, vol. 3, no. 2, pp. 620–626, Apr. 2018, doi: 10.1109/LRA.2017.2776353.  
*Journal article* · T3 · `faessler2018` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/164703614/full-text-file?utm_source=api_4212&allow_speedbump=true) · [doi:10.1109/LRA.2017.2776353](https://doi.org/10.1109/LRA.2017.2776353)  
Shows the quadrotor with linear rotor drag stays differentially flat and that feed-forward drag compensation cuts RMS tracking error by 50 % from 0.5 m/s upward; gives the drag coefficients one should identify for the X500 so that sim wind produces realistic forces.

**[53]** L. Bauersfeld, E. Kaufmann, P. Foehn, S. Sun, and D. Scaramuzza, “NeuroBEM: Hybrid aerodynamic quadrotor model,” in *Proc. Robot.: Sci. Syst. (RSS)*, 2021, doi: 10.15607/RSS.2021.XVII.042.  
*Conference paper* · T3 · `bauersfeld2021` · [doi:10.15607/RSS.2021.XVII.042](https://doi.org/10.15607/RSS.2021.XVII.042)  
NeuroBEM: blade-element-momentum model plus learned residual for quadrotor aerodynamics; the higher-fidelity force model to swap in if linear drag under-predicts wind response in the sim.

**[54]** C. R. Russell, J. Jung, G. Willink, and B. Glasner, “Wind tunnel and hover performance test results for multicopter UAS vehicles,” in *Proc. AHS Int. Annu. Forum*, 2016. [Online]. Available: https://ntrs.nasa.gov/citations/20160007399  
*Conference paper* · T3 · `russell2016` · [link](https://ntrs.nasa.gov/citations/20160007399)  
NASA Ames 7x10 ft wind-tunnel data for five commercial multicopters (3DR Solo/Iris+, DJI Phantom 3, two octocopters) at 20-80 ft/s (~6-24 m/s) and pitch -40..+40 deg; e.g. Solo mean drag 0.8 lb at ~40 ft/s (12 m/s), with rotor-induced load peaks up to +/-10 lb. Gives order-of-magnitude drag and power vs. airspeed and attitude for ~1.3-1.5 kg quadrotors close to the X500 class.

**[55]** J. X. J. Bannwarth, Z. J. Chen, K. A. Stol, B. A. MacDonald, and P. J. Richards, “Aerodynamic force modeling of multirotor unmanned aerial vehicles,” *AIAA J.*, vol. 57, no. 3, pp. 1250–1259, Mar. 2019, doi: 10.2514/1.J057165.  
*Journal article* · T3 · `bannwarth2019` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/258048396/full-text-file?utm_source=api_4212&allow_speedbump=true) · [doi:10.2514/1.J057165](https://doi.org/10.2514/1.J057165)  
Wind-tunnel-derived multirotor force model for station-keeping simulation in turbulent wind: simulated position-error spread matched experiment within 7 % along the wind but only within 56 % across it. Good evidence that simple sims get mean-wind response right but cross-wind turbulence response poorly -- a metric to report in DroneRanger sim-vs-real comparisons.

**[56]** L. Bauersfeld and D. Scaramuzza, “Range, endurance, and optimal speed estimates for multicopters,” *IEEE Robot. Autom. Lett.*, vol. 7, no. 2, pp. 2953–2960, Apr. 2022, doi: 10.1109/LRA.2022.3145063.  
*Journal article* · T3 · `bauersfeld2022` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/515545995/full-text-file?utm_source=api_4212&allow_speedbump=true) · [doi:10.1109/LRA.2022.3145063](https://doi.org/10.1109/LRA.2022.3145063)  
Combines a blade-element-momentum aerodynamic model with motor and gray-box battery models (cell voltage error 1.3 %), validated up to 65 km/h; because power depends on airspeed, the same model can be used to estimate the endurance penalty of holding position against a headwind over the garden.

**[57]** T. A. Rodrigues *et al.*, “In-flight positional and energy use data set of a DJI Matrice 100 quadcopter for small package delivery,” *Sci. Data*, vol. 8, no. 1, Art. no. 155, Jun. 2021, doi: 10.1038/s41597-021-00930-x.  
*Journal article* · T3 · `rodrigues2021` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/480855971/full-text-file?utm_source=api_4212&allow_speedbump=true) (Open Access) · [doi:10.1038/s41597-021-00930-x](https://doi.org/10.1038/s41597-021-00930-x)  
209 outdoor flights (10 h 45 min, ~65 km) of a 3.7-4.2 kg quadrotor carrying an onboard ultrasonic anemometer, logging wind, IMU, GPS and power; a ready public dataset to test wind-drag and power models before DroneRanger collects its own X500 logs.

**[58]** P. Sanchez-Cuevas, G. Heredia, and A. Ollero, “Characterization of the aerodynamic ground effect and its influence in multirotor control,” *Int. J. Aerosp. Eng.*, vol. 2017, Art. no. 1823056, 2017, doi: 10.1155/2017/1823056.  
*Journal article* · T3 · `sanchezcuevas2017` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/147762318/full-text-file?utm_source=api_4212&allow_speedbump=true) (Open Access) · [doi:10.1155/2017/1823056](https://doi.org/10.1155/2017/1823056)  
Ground-effect characterisation for multirotors and its influence on control; matters only near take-off/landing, so it must be separated from wind when comparing low-altitude sim and real logs.

**[59]** P. P. Neumann and M. Bartholmai, “Real-time wind estimation on a micro unmanned aerial vehicle using its inertial measurement unit,” *Sens. Actuators A, Phys.*, vol. 235, pp. 300–310, Nov. 2015, doi: 10.1016/j.sna.2015.09.036.  
*Journal article* · T4 · `neumann2015` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/56776033/full-text-file?utm_source=api_4212&allow_speedbump=true) · [doi:10.1016/j.sna.2015.09.036](https://doi.org/10.1016/j.sna.2015.09.036)  
Early demonstration that a multirotor IMU (tilt needed to hold position) suffices to estimate wind speed and direction in real time; the basic tilt-to-wind mapping that DroneRanger can apply to hover segments in its PX4 logs.

**[60]** R. T. Palomaki, N. T. Rose, M. van den Bossche, T. J. Sherman, and S. F. J. De Wekker, “Wind estimation in the lower atmosphere using multirotor aircraft,” *J. Atmos. Ocean. Technol.*, vol. 34, no. 5, pp. 1183–1191, May 2017, doi: 10.1175/JTECH-D-16-0177.1.  
*Journal article* · T4 · `palomaki2017` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/91369601/full-text-file?utm_source=api_4212&allow_speedbump=true) · [doi:10.1175/JTECH-D-16-0177.1](https://doi.org/10.1175/JTECH-D-16-0177.1)  
Multirotors hovering 10 m above ground next to sonic anemometers; attitude-based estimates gave typical errors <0.5 m/s in speed and <30 deg in direction. Directly supports flying the X500 at 3-10 m in the garden as its own anemometer to compare against ASOS.

**[61]** M. Simma, H. Mjøen, and T. Boström, “Measuring wind speed using the internal stabilization system of a quadrotor drone,” *Drones*, vol. 4, no. 2, Art. no. 23, Jun. 2020, doi: 10.3390/drones4020023.  
*Journal article* · T4 · `simma2020` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/394115614/full-text-file?utm_source=api_4212&allow_speedbump=true) (Open Access) · [doi:10.3390/drones4020023](https://doi.org/10.3390/drones4020023)  
Uses only autopilot log data plus static-thrust tests; hovering beside a 2D ultrasonic anemometer in 0-5 m/s wind gave RMSE 0.26-0.29 m/s (speed) and 4.1-4.9 deg (direction). Closest published analogue to post-processing DroneRanger PX4 ULogs into the wind the drone actually felt.

**[62]** T. Wetz, N. Wildmann, and F. Beyrich, “Distributed wind measurements with multiple quadrotor unmanned aerial vehicles in the atmospheric boundary layer,” *Atmos. Meas. Tech.*, vol. 14, no. 5, pp. 3795–3814, May 2021, doi: 10.5194/amt-14-3795-2021.  
*Journal article* · T4 · `wetz2021` · [🔗 **View Article**](https://libkey.io/libraries/545/articles/476597378/content-location?utm_source=api_4212&allow_speedbump=true) (Open Access) · [doi:10.5194/amt-14-3795-2021](https://doi.org/10.5194/amt-14-3795-2021)  
Drag-based wind retrieval from hovering quadrotors calibrated on 76 flights against a 99 m tower: RMS deviation <0.3 m/s in speed and <8 deg in direction, with short-timescale fluctuations agreeing with tower and lidar. Best published accuracy bound for the log-based wind DroneRanger can extract.

**[63]** D. Crowe, R. Pamula, H. Y. Cheung, and S. F. J. De Wekker, “Two supervised machine learning approaches for wind velocity estimation using multi-rotor copter attitude measurements,” *Sensors*, vol. 20, no. 19, Art. no. 5638, Oct. 2020, doi: 10.3390/s20195638.  
*Journal article* · T4 · `crowe2020` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/414919174/full-text-file?utm_source=api_4212&allow_speedbump=true) (Open Access) · [doi:10.3390/s20195638](https://doi.org/10.3390/s20195638)  
KNN and LSTM models map hovering-drone attitude to tower-measured wind; LSTM reached 0.61 m/s average RMSE with >=20 min of training data and beat linear regression in gusty conditions. A data-driven option if DroneRanger co-locates a cheap anemometer for a few calibration flights.

**[64]** J. González-Rocha, C. A. Woolsey, C. Sultan, and S. F. J. De Wekker, “Sensing wind from quadrotor motion,” *J. Guid. Control Dyn.*, vol. 42, no. 4, pp. 836–852, Apr. 2019, doi: 10.2514/1.G003542.  
*Journal article* · T4 · `gonzalezrocha2019` · [🔗 **Access Options**](https://libkey.io/libraries/545/10.2514/1.G003542) · [doi:10.2514/1.G003542](https://doi.org/10.2514/1.G003542)  
Compares kinematic-particle, dynamic-particle and rigid-body motion models for wind estimation, identified from wind-tunnel and flight data and validated beside a 10 m sonic anemometer; bandwidth rises with model fidelity and the rigid-body model gives the best speed estimates.

**[65]** G. Hattenberger, M. Bronz, and J.-P. Condomines, “Estimating wind using a quadrotor,” *Int. J. Micro Air Veh.*, vol. 14, Art. no. 17568293211070824, Jan. 2022, doi: 10.1177/17568293211070824.  
*Journal article* · T4 · `hattenberger2022` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/514537284/full-text-file?utm_source=api_4212&allow_speedbump=true) (Open Access) · [doi:10.1177/17568293211070824](https://doi.org/10.1177/17568293211070824)  
Calibrates a drag model by global optimisation from telemetry and runs a Kalman filter for online wind speed/direction using only standard navigation sensors, demonstrated onboard; essentially the calibrate-then-filter workflow PX4 EKF2 drag fusion expects.

**[66]** T. Tomić, P. Lutz, K. Schmid, A. Mathers, and S. Haddadin, “Simultaneous contact and aerodynamic force estimation (s-CAFE) for aerial robots,” *Int. J. Robot. Res.*, vol. 39, no. 6, pp. 688–728, May 2020, doi: 10.1177/0278364920904788.  
*Journal article* · T4 · `tomic2020` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/377475599/full-text-file?utm_source=api_4212&allow_speedbump=true) · [doi:10.1177/0278364920904788](https://doi.org/10.1177/0278364920904788)  
Separates aerodynamic from contact wrenches online and estimates airspeed from propeller power and speed (ESC data), with ground truth from autonomous flights in a 3D wind tunnel; a route to wind estimation if the X500 logs ESC RPM/current.

**[67]** K. Kose, J. Wing, N. A. Kose, C. Guadarrama-Trejo, A. Sowers, and A. Rasheed, “A UAV testbed for diagnosing hardware vulnerabilities: Quantifying sim-to-real discrepancies in PX4 flight logs,” *Sensors*, vol. 26, no. 10, Art. no. 3188, May 2026, doi: 10.3390/s26103188.  
*Journal article* · T4 · `kose2026` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/710408988/full-text-file?utm_source=api_4212&allow_speedbump=true) (Open Access) · [doi:10.3390/s26103188](https://doi.org/10.3390/s26103188)  
Quantifies PX4 SITL vs real-flight ULog discrepancies (variance, distribution shift); the statistical template for DroneRanger's sim-with-wind vs real comparison.

**[68]** E. J. J. Smeur, Q. Chu, and G. C. H. E. de Croon, “Adaptive incremental nonlinear dynamic inversion for attitude control of micro air vehicles,” *J. Guid. Control Dyn.*, vol. 39, no. 3, pp. 450–461, Mar. 2016, doi: 10.2514/1.G001490.  
*Journal article* · T5 · `smeur2016` · [🔗 **Access Options**](https://libkey.io/libraries/545/10.2514/1.G001490) · [doi:10.2514/1.G001490](https://doi.org/10.2514/1.G001490)  
Sensor-based INDI attitude control that needs only a control-effectiveness model (adapted online) and handles actuator/measurement delay; basis of the INDI disturbance-rejection line that PX4-class vehicles can use against gusts.

**[69]** E. J. J. Smeur, G. C. H. E. de Croon, and Q. Chu, “Cascaded incremental nonlinear dynamic inversion for MAV disturbance rejection,” *Control Eng. Pract.*, vol. 73, pp. 79–90, Apr. 2018, doi: 10.1016/j.conengprac.2018.01.003.  
*Journal article* · T5 · `smeur2018` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/193452379/full-text-file?utm_source=api_4212&allow_speedbump=true) · [doi:10.1016/j.conengprac.2018.01.003](https://doi.org/10.1016/j.conengprac.2018.01.003)  
Cascaded INDI (attitude + position) clearly outperformed PID when a quadrotor flew in and out of a 10 m/s wind-tunnel exhaust, and also worked outdoors with standard GPS; a realistic sharp-gust test case to reproduce in simulation. (Publisher OA, CC BY-NC-ND, though LibKey flags it as not OA.)

**[70]** E. Tal and S. Karaman, “Accurate tracking of aggressive quadrotor trajectories using incremental nonlinear dynamic inversion and differential flatness,” *IEEE Trans. Control Syst. Technol.*, vol. 29, no. 3, pp. 1203–1218, May 2021, doi: 10.1109/TCST.2020.3001117.  
*Journal article* · T5 · `tal2021` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/394548683/full-text-file?utm_source=api_4212&allow_speedbump=true) · [doi:10.1109/TCST.2020.3001117](https://doi.org/10.1109/TCST.2020.3001117)  
INDI + flatness feed-forward tracks up to 12.9 m/s and 2.1 g with 6.6 cm RMS error and needs no prior aerodynamic model, rejecting drag as a disturbance (also shown with an attached drag plate); evidence that a robust inner loop can make sim-vs-real wind mismatch less critical.

**[71]** S. Sun, A. Romero, P. Foehn, E. Kaufmann, and D. Scaramuzza, “A comparative study of nonlinear MPC and differential-flatness-based control for quadrotor agile flight,” *IEEE Trans. Robot.*, vol. 38, no. 6, pp. 3357–3373, Dec. 2022, doi: 10.1109/TRO.2022.3177279.  
*Journal article* · T5 · `sun2022` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/528045932/full-text-file?utm_source=api_4212&allow_speedbump=true) · [doi:10.1109/TRO.2022.3177279](https://doi.org/10.1109/TRO.2022.3177279)  
Up to 20 m/s, both NMPC and DFBC gain >78 % tracking-error reduction from adding an INDI inner loop and an aerodynamic drag model; quantifies how much aerodynamic modelling matters when transferring controllers from sim to real.

**[72]** D. Hanover, P. Foehn, S. Sun, E. Kaufmann, and D. Scaramuzza, “Performance, precision, and payloads: Adaptive nonlinear MPC for quadrotors,” *IEEE Robot. Autom. Lett.*, vol. 7, no. 2, pp. 690–697, Apr. 2022, doi: 10.1109/LRA.2021.3131690.  
*Journal article* · T5 · `hanover2022` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/508338861/full-text-file?utm_source=api_4212&allow_speedbump=true) · [doi:10.1109/LRA.2021.3131690](https://doi.org/10.1109/LRA.2021.3131690)  
L1-NMPC learns model errors online: >90 % tracking-error reduction over plain NMPC under large unknown disturbances (fan wind, unmodelled payloads) with identical gains, and ~50 % better tracking on racing trajectories up to 70 km/h.

**[73]** Z. Wu *et al.*, “L1Quad: L1 adaptive augmentation of geometric control for agile quadrotors with performance guarantees,” *IEEE Trans. Control Syst. Technol.*, vol. 33, no. 2, pp. 597–612, Mar. 2025, doi: 10.1109/TCST.2024.3521182.  
*Journal article* · T5 · `wu2025l1quad` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/639561486/full-text-file?utm_source=api_4212&allow_speedbump=true) · [doi:10.1109/TCST.2024.3521182](https://doi.org/10.1109/TCST.2024.3521182)  
L1 adaptive augmentation of an SE(3) geometric controller with uniformly bounded transients, tested on 11 uncertainty types (sloshing payloads, damaged/mixed propellers, etc.); L1 adaptive estimation is also the disturbance observer DATT uses against fan wind, so this is a natural adaptive baseline.

**[74]** W. Craig, D. Yeo, and D. A. Paley, “Geometric attitude and position control of a quadrotor in wind,” *J. Guid. Control Dyn.*, vol. 43, no. 5, pp. 870–883, May 2020, doi: 10.2514/1.G004710.  
*Journal article* · T5 · `craig2020` · [🔗 **Access Options**](https://libkey.io/libraries/545/10.2514/1.G004710) · [doi:10.2514/1.G004710](https://doi.org/10.2514/1.G004710)  
Feeds onboard flow-probe wind measurements into SE(3) feedback linearisation using models of blade-flapping moment and rotor induced + body drag, with variable gains for thrust saturation; shows the benefit of measured (not estimated) wind and the aerodynamic terms a wind sim must include.

**[75]** M. O'Connell *et al.*, “Neural-Fly enables rapid learning for agile flight in strong winds,” *Sci. Robot.*, vol. 7, no. 66, Art. no. eabm6597, May 2022, doi: 10.1126/scirobotics.abm6597.  
*Journal article* · T5 · `oconnell2022` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/598435673/full-text-file?utm_source=api_4212&allow_speedbump=true) · [doi:10.1126/scirobotics.abm6597](https://doi.org/10.1126/scirobotics.abm6597)  
Neural-Fly: DAIML-learned wind representation (12 min of data) plus composite adaptation; in Caltech's Real Weather Wind Tunnel fan array at up to 12.1 m/s it beat nonlinear and adaptive baselines. Benchmark wind range and the reference fan-array validation setup.

**[76]** G. Shi *et al.*, “Neural Lander: Stable drone landing control using learned dynamics,” in *Proc. IEEE Int. Conf. Robot. Autom. (ICRA)*, 2019, pp. 9784–9790, doi: 10.1109/ICRA.2019.8794351.  
*Conference paper* · T5 · `shi2019` · [doi:10.1109/ICRA.2019.8794351](https://doi.org/10.1109/ICRA.2019.8794351)  
Neural Lander: learned residual aerodynamics (ground effect) inside a stable controller; the same residual-learning recipe can fit wind-drag residuals identified from DroneRanger PX4 logs.

**[77]** S. M. Richards, N. Azizan, J.-J. Slotine, and M. Pavone, “Control-oriented meta-learning,” *Int. J. Robot. Res.*, vol. 42, no. 10, pp. 777–797, Sep. 2023, doi: 10.1177/02783649231165085.  
*Journal article* · T5 · `richards2023` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/574627232/full-text-file?utm_source=api_4212&allow_speedbump=true) · [doi:10.1177/02783649231165085](https://doi.org/10.1177/02783649231165085)  
Meta-learns adaptive-control features in closed-loop simulation with tracking error as the meta-objective, beating regression-oriented meta-learning for planar rotorcraft in wind; shows how a wind-randomised simulator can be used to train adaptation, not just to test it (simulation only).

**[78]** K. Huang, R. Rana, A. Spitzer, G. Shi, and B. Boots, “DATT: Deep adaptive trajectory tracking for quadrotor control,” in *Proc. Conf. Robot Learn. (CoRL)*, ser. Proc. Mach. Learn. Res., vol. 229, 2023, pp. 326–340. [Online]. Available: https://proceedings.mlr.press/v229/huang23a.html  
*Conference paper* · T5 · `huang2023datt` · [link](https://proceedings.mlr.press/v229/huang23a.html)  
RL policy trained only with a random-walk force disturbance in sim, augmented on hardware by an L1 disturbance estimator, outperforms adaptive NMPC in unsteady fan wind with a drag plate (34 % less error in the hardest case, <3.2 ms inference). Suggests coarse force randomisation + online adaptation can stand in for a high-fidelity wind model.

**[79]** A. Molchanov, T. Chen, W. Hönig, J. A. Preiss, N. Ayanian, and G. S. Sukhatme, “Sim-to-(multi)-real: Transfer of low-level robust control policies to multiple quadrotors,” in *Proc. IEEE/RSJ Int. Conf. Intell. Robots Syst. (IROS)*, 2019, pp. 59–66, doi: 10.1109/IROS40897.2019.8967695.  
*Conference paper* · T5 · `molchanov2019` · [doi:10.1109/IROS40897.2019.8967695](https://doi.org/10.1109/IROS40897.2019.8967695)  
Low-level RL quadrotor policies with domain randomisation that transfer to several real vehicles and resist external disturbances; baseline recipe to which wind randomisation would be added.

**[80]** D. Zhang, A. Loquercio, J. Tang, T.-H. Wang, J. Malik, and M. W. Mueller, “A learning-based quadcopter controller with extreme adaptation,” *IEEE Trans. Robot.*, vol. 41, pp. 3948–3964, 2025, doi: 10.1109/TRO.2025.3577037.  
*Journal article* · T5 · `zhang2025extreme` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/665612268/full-text-file?utm_source=api_4212&allow_speedbump=true) · [doi:10.1109/TRO.2025.3577037](https://doi.org/10.1109/TRO.2025.3577037)  
Latent-adaptation RL controller (mass x3.7, propeller constant >100x, payloads, motor failure); wind is not the focus, but it is a candidate adaptive baseline for wind-randomised training.

**[81]** A. A. Habel, R. A. Khan, F. Mehboob, C. Fortin, and D. Tsetserukou, “GustPilot: A hierarchical DRL-INDI framework for wind-resilient quadrotor navigation,” Mar. 2026, arXiv:2603.19966.  
*Preprint (not peer reviewed)* · T5 · `habel2026gustpilot` · [arXiv:2603.19966](https://arxiv.org/abs/2603.19966) · [link](https://arxiv.org/abs/2603.19966)  
DRL velocity planner trained with fan-jet domain randomisation over an INDI tracker; on a 50 g Crazyflie in ducted-fan wind (up to ~7 m/s at the fan, 3.5 m/s disturbances) it reached 94.6 % success vs 36.0 % for DRL-PID and up to 50 % lower RMSE (80 flights). Recent example of wind-randomised RL transferring to real wind; preprint, not peer reviewed.

**[82]** C. A. Dimmig *et al.*, “Survey of simulators for aerial robots: An overview and in-depth systematic comparisons,” *IEEE Robot. Autom. Mag.*, vol. 32, no. 2, pp. 153–166, Jun. 2025, doi: 10.1109/MRA.2024.3433171.  
*Journal article* · T6 · `dimmig2025` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/627072390/full-text-file?utm_source=api_4212&allow_speedbump=true) · [doi:10.1109/MRA.2024.3433171](https://doi.org/10.1109/MRA.2024.3433171)  
Systematic comparison of aerial-robot simulators; use it to justify the Gazebo vs Isaac/Pegasus choice for wind work.

**[83]** N. Kakavitsas, A. Willis, R. Jacobik, M. Uddin, and A. Wolek, “Quadrotor flight simulation in a CFD-generated urban wind field,” in *Proc. IEEE Aerosp. Conf. (AERO)*, 2024, pp. 1–8, doi: 10.1109/AERO58975.2024.10521032.  
*Conference paper* · T6 · `kakavitsas2024` · [doi:10.1109/AERO58975.2024.10521032](https://doi.org/10.1109/AERO58975.2024.10521032)  
OpenStreetMap buildings -> OpenFOAM steady 3D wind field -> Gazebo plugin interpolating the field at runtime -> PX4 SITL, compared with and without wind over a campus. The closest existing pipeline to DroneRanger's plan; ASOS would supply the inflow boundary condition.

**[84]** N. Imamov, B. Abbyasov, T. Tsoy, E. A. Martínez-García, and E. Magid, “Evaluation of a weather plugin in Gazebo: A case-study of a wind influence on PX4-based UAV performance,” in *Proc. Int. Conf. Interactive Collab. Robot. (ICR)*, 2024, pp. 344–356, doi: 10.1007/978-3-031-71360-6_26.  
*Conference paper* · T6 · `imamov2024` · [doi:10.1007/978-3-031-71360-6_26](https://doi.org/10.1007/978-3-031-71360-6_26)  
Case study of a Gazebo wind/weather plugin flown with PX4 (per its title and repository record: wind resistance, tilt and velocity evaluated); a direct precedent for the Gazebo branch of the DroneRanger plan (full text not checked).

**[85]** F. Achermann *et al.*, “WindSeer: Real-time volumetric wind prediction over complex terrain aboard a small uncrewed aerial vehicle,” *Nat. Commun.*, vol. 15, no. 1, Art. no. 3507, Apr. 2024, doi: 10.1038/s41467-024-47778-4.  
*Journal article* · T6 · `achermann2024` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/613998673/full-text-file?utm_source=api_4212&allow_speedbump=true) (Open Access) · [doi:10.1038/s41467-024-47778-4](https://doi.org/10.1038/s41467-024-47778-4)  
CNN trained purely on 7361 CFD runs predicts time-averaged 3D wind from a few noisy measurements, validated on weather-station and in-flight drone wind; errors are largest near the ground and in lee zones, and the authors note typical sUAV altitudes above 50 m -- unlike the DroneRanger 3-10 m band.

**[86]** D. A. Olejnik *et al.*, “An experimental study of wind resistance and power consumption in MAVs with a low-speed multi-fan wind system,” in *Proc. IEEE Int. Conf. Robot. Autom. (ICRA)*, 2022, pp. 2989–2994, doi: 10.1109/ICRA46639.2022.9811834.  
*Conference paper* · T6 · `olejnik2022` · [doi:10.1109/ICRA46639.2022.9811834](https://doi.org/10.1109/ICRA46639.2022.9811834)  
Open-source low-cost multi-fan wind generator: steady 0.5-3.4 m/s and periodic gusts (1.3-3.4 m/s at 0.5/0.25/0.125 Hz) used to log attitude and power of a Crazyflie and a flapping-wing MAV; a cheap way to create repeatable gusts for validating a wind sim indoors (small vehicles only).

**[87]** M. Gao, C. H. Hugenholtz, T. A. Fox, M. Kucharczyk, T. E. Barchyn, and P. R. Nesbit, “Weather constraints on global drone flyability,” *Sci. Rep.*, vol. 11, no. 1, Art. no. 12092, Jun. 2021, doi: 10.1038/s41598-021-91325-w.  
*Journal article* · T7 · `gao2021` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/479081776/full-text-file?utm_source=api_4212&allow_speedbump=true) (Open Access) · [doi:10.1038/s41598-021-91325-w](https://doi.org/10.1038/s41598-021-91325-w)  
10 years of hourly ERA5 reanalysis (100 m wind, 0.25 deg grid) vs manufacturer limits: "common" drones (max wind 10 m/s, no rain) have median global flyability 5.7 h/day (2.0 h/day in daylight); raising the wind limit to 15 m/s gives the largest gains. Template for a San Jose ASOS-based flyability analysis (an Author Correction exists: doi 10.1038/s41598-021-00537-7).

**[88]** C. A. Roseman and B. M. Argrow, “Weather hazard risk quantification for sUAS safety risk management,” *J. Atmos. Ocean. Technol.*, vol. 37, no. 7, pp. 1251–1268, Jul. 2020, doi: 10.1175/JTECH-D-20-0009.1.  
*Journal article* · T7 · `roseman2020` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/401428647/full-text-file?utm_source=api_4212&allow_speedbump=true) · [doi:10.1175/JTECH-D-20-0009.1](https://doi.org/10.1175/JTECH-D-20-0009.1)  
Bayesian-network sUAS Weather Risk Model combining forecast weather (HRRR), population and structure density following FAA safety-risk guidance, demonstrated over Boulder; argues fine-scale (<1 km) forecasts are needed -- coarse airport/forecast wind is not enough for go/no-go at a backyard.

**[89]** A. Kadian *et al.*, “Sim2Real predictivity: Does evaluation in simulation predict real-world performance?” *IEEE Robot. Autom. Lett.*, vol. 5, no. 4, pp. 6670–6677, Oct. 2020, doi: 10.1109/LRA.2020.3013848.  
*Journal article* · T6 · `kadian2020` · [📄 **Download PDF**](https://libkey.io/libraries/545/articles/403516120/full-text-file?utm_source=api_4212&allow_speedbump=true) · [doi:10.1109/LRA.2020.3013848](https://doi.org/10.1109/LRA.2020.3013848)  
Sim-to-real predictivity: the right way to judge whether wind replay makes SITL predictive.
