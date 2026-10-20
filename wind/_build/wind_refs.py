"""Reference database for the wind feasibility report (single source of truth).

Every entry was checked on 2026-10-19:
  * journal articles: resolved through LibKey (Northeastern University Library); `libkey` holds the LibKey
    article id, the best link type and the open-access flag returned by LibKey;
  * conference papers, chapters, books and reports: DOI metadata checked on Crossref or the publisher;
  * preprints: checked on the arXiv API; documentation and software: the page or tagged source was opened.

Schema as in sim2real/_build/refs.py, plus
  reuse    True: take every bibliographic field from sim2real/_build/refs.py (same key)
  theme    T0-T7, see THEMES
  why      one or two sentences: what the source shows and why it matters here (shown in references.md)
"""

THEMES = {
    'T0': 'DroneRanger and wind data sources',
    'T1': 'atmospheric wind and turbulence models',
    'T2': 'low-altitude urban and suburban wind',
    'T3': 'multirotor aerodynamics in wind',
    'T4': 'wind estimation from multirotor motion',
    'T5': 'control and learning for wind rejection',
    'T6': 'simulators and wind injection',
    'T7': 'weather as an operational constraint',
}

ACC = '2026-10-19'

REFS = [
# ----------------------------------------------------------------------------------------- DroneRanger and data
dict(key='ling2026', reuse=True, theme='T0',
     why='The published DroneRanger framework (Gazebo/Unity + PX4 + ROS 2) that this work extends.'),
dict(key='yin2026', reuse=True, theme='T0',
     why='Spring 2026 handover: MAVSDK-Python, then ROS 2 offboard over uXRCE-DDS on the Jetson.'),
dict(key='ripzou2026isaac', reuse=True, theme='T0',
     why='Legacy Isaac Sim 5.1 + Pegasus 5.1 + PX4 v1.14.3 setup that the Isaac path would build on.'),
dict(key='iem1min', kind='D', authors=['Iowa Environmental Mesonet'], title='ASOS one minute data download',
     site='Iowa State University', url='https://mesonet.agron.iastate.edu/request/asos/1min.phtml', accessed=ACC,
     theme='T0', why='Free CSV access to NCEI ASOS 1-minute data; source of the 218k SJC records used here.'),
dict(key='ncei6405', kind='D', authors=['NOAA National Centers for Environmental Information'],
     title='ASOS surface 1-minute, page 1 data (TD-6405) format documentation', site='NCEI data archive',
     url='https://www.ncei.noaa.gov/pub/data/asos-onemin/td6405.txt', accessed=ACC, theme='T0',
     why='Defines the 1-minute fields: 2-minute average wind and the maximum 5-second average gust.'),
dict(key='iemasos', kind='D', authors=['Iowa Environmental Mesonet'], title='ASOS-AWOS-METAR data download',
     site='Iowa State University', url='https://mesonet.agron.iastate.edu/request/download.phtml', accessed=ACC,
     theme='T0', why='Hourly METAR for SJC, Reid-Hillview, Moffett and Palo Alto used for the station comparison.'),
dict(key='openmeteo', kind='D', authors=['Open-Meteo'], title='Historical weather API',
     site='Open-Meteo documentation', url='https://open-meteo.com/en/docs/historical-weather-api', accessed=ACC,
     theme='T0', why='Gridded reanalysis wind at any point (9-25 km grids); read ~35 % below SJC here.'),
dict(key='cimis', kind='D', authors=['California Department of Water Resources'],
     title='CIMIS station list (web API)', site='California Irrigation Management Information System',
     url='https://et.water.ca.gov/api/station', accessed=ACC, theme='T0',
     why='2 m agricultural wind stations; the San Jose station (#69) closed in 2002, nearest active 25-40 km.'),
dict(key='wieringa1986', kind='J', authors=['Wieringa, J.'],
     title='Roughness-dependent geographical interpolation of surface wind speed averages',
     venue='Q. J. R. Meteorol. Soc.', venue_full='Quarterly Journal of the Royal Meteorological Society',
     volume='112', number='473', pages='867--889', month=7, year=1986, doi='10.1002/qj.49711247316',
     libkey=(26687643, 'linkResolverOpenUrl', False), theme='T2',
     why='Standard method for moving station wind to a site of different roughness via a blending height; '
         'used for the airport-to-garden factor.'),
dict(key='taylor1938', kind='J', authors=['Taylor, G. I.'], title='The spectrum of turbulence',
     venue='Proc. R. Soc. Lond. A', venue_full='Proceedings of the Royal Society of London. Series A',
     volume='164', number='919', pages='476--490', month=2, year=1938, doi='10.1098/rspa.1938.0032',
     libkey=(35627245, 'linkResolverOpenUrl', False), theme='T1',
     why="Frozen-turbulence hypothesis: eddies advected at the mean wind, which lets Dryden spectra be used for "
         "a hovering drone."),

# ----------------------------------------------------------------------------------------- simulators, tools
dict(key='jacinto2024', reuse=True, theme='T6',
     why='Pegasus: Isaac Sim + PX4/ArduPilot via MAVLink HIL; the legacy Isaac stack.'),
dict(key='pegasussrc', kind='W', authors=['PegasusSimulator'], title='Pegasus Simulator',
     note='GitHub repository, tag v5.1.0', month=10, year=2025,
     url='https://github.com/PegasusSimulator/PegasusSimulator', theme='T6',
     why='Source check: LinearDrag uses ground-relative velocity, no wind model; Drag subclass is the hook.'),
dict(key='pegasus132', kind='D', authors=['BerkeCanGoktas'], title='How to add wind in headless scripts? (issue #132)',
     site='PegasusSimulator GitHub issues', url='https://github.com/PegasusSimulator/PegasusSimulator/issues/132',
     accessed=ACC, theme='T6', why='Open user request; workaround applies a force in a physics callback.'),
dict(key='px4gz', reuse=True, theme='T6', why='PX4 Gazebo (gz) SITL, including the x500 and world selection.'),
dict(key='px4windy', kind='D', authors=['PX4 Autopilot'], title='windy.sdf world',
     site='PX4-gazebo-models repository (main)',
     url='https://github.com/PX4/PX4-gazebo-models/blob/main/worlds/windy.sdf', accessed=ACC, theme='T6',
     why='Official windy world: constant 5, 2, 0 m/s wind, no plugins of its own.'),
dict(key='gzwindeffects', kind='D', authors=['Open Robotics'], title='WindEffects system (source)',
     site='gz-sim repository, branch gz-sim8',
     url='https://github.com/gazebosim/gz-sim/blob/gz-sim8/src/systems/wind_effects/WindEffects.cc',
     accessed=ACC, theme='T6',
     why='Force = mass x gain x (v_wind - v_link) on links with enable_wind; wind settable on /world/<w>/wind.'),
dict(key='gzmotormodel', kind='D', authors=['Open Robotics'], title='MulticopterMotorModel system (source)',
     site='gz-sim repository, branch gz-sim8',
     url='https://github.com/gazebosim/gz-sim/blob/gz-sim8/src/systems/multicopter_motor_model/'
         'MulticopterMotorModel.cc', accessed=ACC, theme='T6',
     why='Rotor drag uses body velocity minus wind: the only path by which wind reaches the stock x500.'),
dict(key='px4pr28042', kind='D', authors=['PX4 Autopilot'],
     title='fix(simulation): make wind affect the airspeed sensor in gz (pull request #28042)',
     site='PX4-Autopilot GitHub, merged 2026-07-22', url='https://github.com/PX4/PX4-Autopilot/pull/28042',
     accessed=ACC, theme='T6', why='Loads WindEffects in the PX4 gz server config on main; not in v1.17.0.'),
dict(key='px4pr130', kind='D', authors=['PX4 Autopilot'],
     title='feat: add real wind effect on multicopter-like models with WindEffects gz plugin (pull request #130)',
     site='PX4-gazebo-models GitHub, open', url='https://github.com/PX4/PX4-gazebo-models/pull/130',
     accessed=ACC, theme='T6', why='Adds enable_wind to the x500 base link; example gz.msgs.Wind command.'),
dict(key='px4sihmain', kind='D', authors=['PX4 Autopilot'], title='Simulation-in-hardware (SIH)',
     site='PX4 User Guide (main)', url='https://docs.px4.io/main/en/sim_sih/', accessed=ACC, theme='T6',
     why='SIH_WIND_N/E wind, changeable during flight (main and v1.18-rc1; not in v1.17.0).'),
dict(key='px4commander', kind='D', authors=['PX4 Autopilot'], title='Commander parameters (commander_params.c)',
     site='PX4-Autopilot repository, tag v1.17.0',
     url='https://github.com/PX4/PX4-Autopilot/blob/v1.17.0/src/modules/commander/commander_params.c',
     accessed=ACC, theme='T7',
     why='COM_WIND_WARN (v1.13+), COM_WIND_MAX (v1.14+), COM_WIND_MAX_ACT (v1.15+); all disabled by default.'),
dict(key='gzclassicwind', kind='D', authors=['PX4 Autopilot'], title='gazebo_wind_plugin.cpp',
     site='PX4-SITL_gazebo-classic repository (main)',
     url='https://github.com/PX4/PX4-SITL_gazebo-classic/blob/main/src/gazebo_wind_plugin.cpp', accessed=ACC,
     theme='T6', why='Mean + variance + one gust window + ramp; no wind-from-file input.'),
dict(key='gzclassiceol', kind='D', authors=['Open Robotics'], title='Gazebo Classic and Citadel end of life',
     site='Open Robotics Discourse', url='https://discourse.openrobotics.org/t/gazebo-classic-and-citadel-end-of-life/48152',
     accessed=ACC, theme='T6', why='Gazebo Classic end of life: 31 January 2025.'),
dict(key='rotorpysrc', kind='W', authors=['spencerfolk'], title='RotorPy',
     note='GitHub repository, PyPI release 3.0.0', month=9, year=2026,
     url='https://github.com/spencerfolk/rotorpy', theme='T6',
     why='MIT-licensed; air-relative aerodynamics, Dryden wind, optional PX4 HIL bridge; used for the demo.'),
dict(key='wind3d', kind='W', authors=['charlotte-visionlab'], title='px4_gazebo_wind3d',
     note='GitHub repository', year=2025, url='https://github.com/charlotte-visionlab/px4_gazebo_wind3d',
     theme='T6', why='Only open tool found that loads a (static, CFD) wind field into PX4 SITL; Gazebo Classic.'),
dict(key='furrer2016', reuse=True, theme='T6', why='RotorS: the Gazebo MAV framework whose wind plugin PX4 inherited.'),
dict(key='shah2018', reuse=True, theme='T6', why='AirSim: has a simSetWind API; the project is being archived.'),
dict(key='xu2024omnidrones', reuse=True, theme='T6',
     why='OmniDrones (Isaac): wind only as random sinusoidal forces in its tracking task.'),
dict(key='kulkarni2025', reuse=True, theme='T6',
     why='Aerial Gym: random force/torque disturbances, no air-relative wind.'),
dict(key='kadian2020', reuse=True, theme='T6',
     why='Sim-to-real predictivity: the right way to judge whether wind replay makes SITL predictive.'),
# ----------------------------------------------------------------------------------------- literature (LibKey-verified search, 2026-10-19)
# ----------------------------------------------------------------------------------------- T1 turbulence models
dict(key='milf8785c', kind='R', authors=['U.S. Department of Defense'],
     title='Military specification: Flying qualities of piloted airplanes', month=11, year=1980,
     address='Washington, DC, USA', institution='U.S. Department of Defense',
     rtype='Military specification MIL-F-8785C',
     url='https://everyspec.com/MIL-SPECS/MIL-SPECS-MIL-F/MIL-F-8785C_5295/', theme='T1',
     why='Source of the Dryden and von Karman turbulence forms later used by Simulink and RotorPy; its low-'
         'altitude model (Sec. 3.7.3, valid 10 ft < h < 1000 ft) sets sigma_w = 0.1*u20 (u20 = mean wind at 20'
         ' ft), gives horizontal intensities and scale lengths as functions of h through (0.177 + 0.000823h), '
         'and a log mean-wind profile scaled from 20 ft with z0 = 0.15 ft or 2.0 ft. Gives DroneRanger a '
         'citable recipe for turning an hourly mean wind into turbulence at 3-10 m (Notice 2, 1996, marks it '
         'inactive for new design).'),
dict(key='milhdbk1797', kind='R', authors=['U.S. Department of Defense'],
     title='Department of Defense handbook: Flying qualities of piloted aircraft', month=12, year=1997,
     address='Washington, DC, USA', institution='U.S. Department of Defense',
     rtype='Military handbook MIL-HDBK-1797',
     url='https://everyspec.com/MIL-HDBK/MIL-HDBK-1500-1799/MIL-HDBK-1797_NOTICE-1_39380/', theme='T1',
     why='Successor guidance to MIL-F-8785C whose Dryden/von Karman PSDs (tabulated by Abichandani et al.) and'
         ' scale-length choices are implemented, e.g., by the Simulink Dryden/von Karman wind blocks; '
         'cancelled by Notice 1 (24 Aug. 2004) and superseded by MIL-STD-1797A. Cite alongside MIL-F-8785C '
         'when stating which turbulence spectrum the DroneRanger wind plugin uses.'),
dict(key='beal1993', kind='J', authors=['Beal, T. R.'],
     title='Digital simulation of atmospheric turbulence for Dryden and von Karman models',
     venue='J. Guid. Control Dyn.', venue_full='Journal of Guidance, Control, and Dynamics', volume='16',
     number='1', pages='132--138', month=1, year=1993, doi='10.2514/3.11437',
     libkey=(45319520, 'linkResolverOpenUrl', False), theme='T1',
     why='Classic recipe for generating Dryden/von Karman gust time series by shaping white noise with '
         'discrete filters; this is the step DroneRanger needs to superimpose turbulence on a replayed ASOS '
         'hourly mean inside a fixed-step simulator.'),
dict(key='abichandani2020', kind='J',
     authors=['Abichandani, Pramod', 'Lobo, Deepan', 'Ford, Gabriel', 'Bucci, Donald', 'Kam, Moshe'],
     title='Wind measurement and simulation techniques in multi-rotor small unmanned aerial vehicles',
     venue='IEEE Access', venue_full='IEEE Access', volume='8', pages='54910--54927', month=3, year=2020,
     doi='10.1109/ACCESS.2020.2977693', libkey=(374333711, 'fullTextFile', True), theme='T1',
     why='Review of multirotor wind sensing (flow sensors, anemometers, tilt-angle methods) and wind '
         'simulation (PSD/Dryden-von Karman, discrete gusts, CFD, probabilistic models), with open-source '
         'Python Dryden code; the most direct starting point for the DroneRanger wind-injection module.'),
dict(key='watkins2006', kind='J',
     authors=['Watkins, Simon', 'Milbank, Juliette', 'Loxton, Benjamin J.', 'Melbourne, William H.'],
     title='Atmospheric winds and their implications for microair vehicles', venue='AIAA J.',
     venue_full='AIAA Journal', volume='44', number='11', pages='2591--2600', month=11, year=2006,
     doi='10.2514/1.22670', libkey=(45288380, 'linkResolverOpenUrl', False), theme='T1',
     why='Measured turbulence 4 m above ground with multi-hole probes 150 and 50 mm apart on a mast above a '
         'car: flow-pitch variation decays only slowly as span shrinks, so small vehicles see large roll '
         'inputs from vertical gusts. Argues that a single-point (uniform) wind vector, as in most simulators,'
         ' under-represents what a 3-10 m drone actually feels.'),
dict(key='stull1988', kind='B', authors=['Stull, Roland B.'],
     title='An Introduction to Boundary Layer Meteorology', year=1988, doi='10.1007/978-94-009-3027-8',
     publisher='Springer', address='Dordrecht, The Netherlands', isbn='978-90-277-2769-5', theme='T1',
     why='Standard text for the surface-layer log wind profile and roughness length used to translate a 10 m '
         'airport wind to other heights; DroneRanger should cite it when it extrapolates ASOS winds to 3-10 m '
         '(valid only above the roughness sublayer, see roth2000).'),

# ----------------------------------------------------------------------------------------- T2 urban and suburban wind
dict(key='watkins2020', kind='J',
     authors=['Watkins, S.', 'Burry, J.', 'Mohamed, A.', 'Marino, M.', 'Prudden, S.', 'Fisher, A.', 'Kloet, N.', 'Jakobi, T.'],
     et_al=True, title='Ten questions concerning the use of drones in urban environments', venue='Build. Environ.',
     venue_full='Building and Environment', volume='167', article_no='106458', month=1, year=2020,
     doi='10.1016/j.buildenv.2019.106458', libkey=(351723423, 'fullTextFile', False), theme='T2',
     why='Review naming inability to fly well in adverse weather (urban wind/turbulence) as a key inhibitor of'
         ' urban drone use, and comparing with how birds/insects cope; frames why a backyard among houses is a'
         ' harder wind environment than the open-field tests most papers use.'),
dict(key='mohamed2023', kind='J',
     authors=['Mohamed, Abdulghani', 'Marino, Matthew', 'Watkins, Simon', 'Jaworski, Justin', 'Jones, Anya'],
     title='Gusts encountered by flying vehicles in proximity to buildings', venue='Drones', venue_full='Drones',
     volume='7', number='1', article_no='22', year=2023, doi='10.3390/drones7010022',
     libkey=(541936308, 'fullTextFile', True), theme='T2',
     why='Reviews Dryden/von Karman and other gust models, then flies idealised trajectories through an LES '
         'field over a cuboid building in a suburban boundary layer (3 m/s reference wind at 10 m): crossing '
         'the roof shear layer at 5 m/s gives ~20 deg change in relative flow angle and ~50 % jump in airspeed'
         ' within 0.25 s. Shows building-induced gusts are spatial, sharp and not captured by isotropic '
         'models.'),
dict(key='galway2011', kind='J', authors=['Galway, David', 'Etele, J.', 'Fusina, Giovanni'],
     title='Modeling of urban wind field effects on unmanned rotorcraft flight', venue='J. Aircr.',
     venue_full='Journal of Aircraft', volume='48', number='5', pages='1613--1620', month=9, year=2011,
     doi='10.2514/1.C031325', libkey=(45318257, 'linkResolverOpenUrl', False), theme='T2',
     why='Builds a database of CFD building wakes and switches them on when the simulated rotorcraft enters a '
         'wake; for a Yamaha R-50 helicopter a light 8 kt (~4 m/s) wind already produced attitude excursions '
         'up to 10 deg. A low-cost template for adding house wakes to a DroneRanger sim without full-domain '
         'CFD.'),
dict(key='ware2016', kind='C', authors=['Ware, John', 'Roy, Nicholas'],
     title='An analysis of wind field estimation and exploitation for quadrotor flight in the urban canopy layer',
     venue='Proc. IEEE Int. Conf. Robot. Autom. (ICRA)',
     venue_full='2016 IEEE International Conference on Robotics and Automation (ICRA)', pages='1507--1514',
     year=2016, doi='10.1109/ICRA.2016.7487287', publisher='IEEE', address='Stockholm, Sweden', theme='T2',
     why='Drives a CFD solver with only the prevailing (above-canopy) wind speed and heading to predict the '
         'urban wind field, then plans minimum-energy quadrotor paths; wind-aware plans cut flight time, '
         'energy and over-airspeed failures across the MIT campus. Same idea as replaying ASOS as a boundary '
         'condition.'),
dict(key='giersch2022', kind='J',
     authors=['Giersch, Sebastian', 'El Guernaoui, Omar', 'Raasch, Siegfried', 'Sauer, Manuela', 'Palomar, Marta'],
     title='Atmospheric flow simulation strategies to assess turbulent wind conditions for safe drone operations'
           ' in urban environments', venue='J. Wind Eng. Ind. Aerodyn.',
     venue_full='Journal of Wind Engineering and Industrial Aerodynamics', volume='229', article_no='105136',
     month=10, year=2022, doi='10.1016/j.jweia.2022.105136', libkey=(533497874, 'fullTextFile', False), theme='T2',
     why='PALM large-eddy simulations resolving buildings down to metre scale argue that turbulence-resolving '
         'models are necessary to plan urban drone operations and recommend a pre-computed meteorological '
         'database per site; supports a precomputed-LES-lookup design over live CFD for DroneRanger. '
         '(Publisher open access, CC BY, although LibKey flags it as not OA.)'),
dict(key='folk2024', kind='J',
     authors=['Folk, Spencer', 'Melton, John', 'Margolis, Benjamin W. L.', 'Yim, Mark', 'Kumar, Vijay'],
     title='Learning local urban wind flow fields from range sensing', venue='IEEE Robot. Autom. Lett.',
     venue_full='IEEE Robotics and Automation Letters', volume='9', number='9', pages='7413--7420', month=9,
     year=2024, doi='10.1109/LRA.2024.3426209', libkey=(622312571, 'fullTextFile', False), theme='T2',
     why='A network trained on simulated winds through small random maps predicts the local flow around a '
         'robot from onboard range data plus sparse wind measurements, generalising to scenes with >200 '
         'buildings; points to a learned "house-wake" surrogate as a cheaper alternative to per-site CFD.'),
dict(key='wieringa1993', kind='J', authors=['Wieringa, Jon'],
     title='Representative roughness parameters for homogeneous terrain', venue='Boundary-Layer Meteorol.',
     venue_full='Boundary-Layer Meteorology', volume='63', number='4', pages='323--363', month=3, year=1993,
     doi='10.1007/BF00705357', libkey=(34762395, 'linkResolverOpenUrl', False), theme='T2',
     why='Critical review of measured roughness lengths for homogeneous terrain types; the standard source for'
         ' z0 of open, airport-like terrain when height-correcting a 10 m station wind. (Crossref spells the '
         'author "Wiernga".)'),
dict(key='grimmond1999', kind='J', authors=['Grimmond, C. S. B.', 'Oke, T. R.'],
     title='Aerodynamic properties of urban areas derived from analysis of surface form',
     venue='J. Appl. Meteorol.', venue_full='Journal of Applied Meteorology', volume='38', number='9',
     pages='1262--1292', month=9, year=1999, doi='10.1175/1520-0450(1999)038<1262:APOUAD>2.0.CO;2',
     libkey=(45506332, 'fullTextFile', False), theme='T2',
     why='Morphometric formulas for zero-plane displacement and roughness length from building/tree height and'
         ' density, tested on 11 North American sites, most of them residential suburbs; the paper to use for '
         'estimating z_d and z_0 of the San Jose garden neighbourhood before any log-law extrapolation.'),
dict(key='roth2000', kind='J', authors=['Roth, M.'], title='Review of atmospheric turbulence over cities',
     venue='Q. J. R. Meteorol. Soc.', venue_full='Quarterly Journal of the Royal Meteorological Society',
     volume='126', number='564', pages='941--990', month=4, year=2000, doi='10.1002/qj.49712656409',
     libkey=(26693282, 'linkResolverOpenUrl', False), theme='T2',
     why='Review of >50 urban turbulence studies: a roughness sublayer extends to about 2.5-3 times building '
         'height, and inside it standard surface-layer (log-law) methods are in doubt. With 1-2 storey houses '
         'the whole 3-10 m DroneRanger band lies inside this layer, so airport wind cannot simply be log-'
         'scaled down to the garden.'),
dict(key='finnigan2000', kind='J', authors=['Finnigan, John'], title='Turbulence in plant canopies',
     venue='Annu. Rev. Fluid Mech.', venue_full='Annual Review of Fluid Mechanics', volume='32', pages='519--571',
     year=2000, doi='10.1146/annurev.fluid.32.1.519', libkey=(47131720, 'fullTextFile', False), theme='T2',
     why='Within and just above vegetation the mean profile is inflected, turbulence is dominated by large '
         'coherent sweeps and behaves like a plane mixing layer rather than a boundary layer; relevant for '
         'flight beside garden trees, where Dryden assumptions (homogeneous, Gaussian) break down.'),

# ----------------------------------------------------------------------------------------- T3 multirotor aerodynamics
dict(key='bauersfeld2021', reuse=True, theme='T3',
     why='NeuroBEM: blade-element-momentum model plus learned residual for quadrotor aerodynamics; the higher-'
         'fidelity force model to swap in if linear drag under-predicts wind response in the sim.'),
dict(key='sanchezcuevas2017', reuse=True, theme='T3',
     why='Ground-effect characterisation for multirotors and its influence on control; matters only near take-'
         'off/landing, so it must be separated from wind when comparing low-altitude sim and real logs.'),
dict(key='mahony2012', kind='J', authors=['Mahony, Robert', 'Kumar, Vijay', 'Corke, Peter'],
     title='Multirotor aerial vehicles: Modeling, estimation, and control of quadrotor',
     venue='IEEE Robot. Autom. Mag.', venue_full='IEEE Robotics \\& Automation Magazine', volume='19', number='3',
     pages='20--32', month=9, year=2012, doi='10.1109/MRA.2012.2206474', libkey=(18873402, 'fullTextFile', False),
     theme='T3',
     why='Tutorial model of quadrotor dynamics including blade flapping and induced drag, which make the rotor'
         ' drag roughly linear in air-relative velocity; the term a simulator needs so that wind (not just '
         'ground velocity) produces force on the airframe.'),
dict(key='faessler2018', kind='J', authors=['Faessler, Matthias', 'Franchi, Antonio', 'Scaramuzza, Davide'],
     title='Differential flatness of quadrotor dynamics subject to rotor drag for accurate tracking of high-'
           'speed trajectories', venue='IEEE Robot. Autom. Lett.',
     venue_full='IEEE Robotics and Automation Letters', volume='3', number='2', pages='620--626', month=4,
     year=2018, doi='10.1109/LRA.2017.2776353', libkey=(164703614, 'fullTextFile', False), theme='T3',
     why='Shows the quadrotor with linear rotor drag stays differentially flat and that feed-forward drag '
         'compensation cuts RMS tracking error by 50 % from 0.5 m/s upward; gives the drag coefficients one '
         'should identify for the X500 so that sim wind produces realistic forces.'),
dict(key='hoffmann2007', kind='C',
     authors=['Hoffmann, Gabriel', 'Huang, Haomiao', 'Waslander, Steven', 'Tomlin, Claire'],
     title='Quadrotor helicopter flight dynamics and control: Theory and experiment',
     venue='Proc. AIAA Guid. Navig. Control Conf. Exhib.',
     venue_full='AIAA Guidance, Navigation and Control Conference and Exhibit', article_no='AIAA 2007-6461',
     month=8, year=2007, doi='10.2514/6.2007-6461', publisher='AIAA', address='Hilton Head, SC, USA', theme='T3',
     why='Analyses three aerodynamic effects away from hover (due to vehicle velocity, angle of attack and '
         'airframe design) that cause attitude moments and thrust variation, validated on a thrust stand and '
         'the STARMAC quadrotor; these airspeed-dependent terms are what a wind simulation must drive.'),
dict(key='russell2016', kind='C', authors=['Russell, Carl R.', 'Jung, Jaewoo', 'Willink, Gina', 'Glasner, Brett'],
     title='Wind tunnel and hover performance test results for multicopter UAS vehicles',
     venue='Proc. AHS Int. Annu. Forum',
     venue_full='American Helicopter Society (AHS) International Annual Forum and Technology Display', month=5,
     year=2016, publisher='American Helicopter Society International', address='West Palm Beach, FL, USA',
     url='https://ntrs.nasa.gov/citations/20160007399', theme='T3',
     why='NASA Ames 7x10 ft wind-tunnel data for five commercial multicopters (3DR Solo/Iris+, DJI Phantom 3, '
         'two octocopters) at 20-80 ft/s (~6-24 m/s) and pitch -40..+40 deg; e.g. Solo mean drag 0.8 lb at ~40'
         ' ft/s (12 m/s), with rotor-induced load peaks up to +/-10 lb. Gives order-of-magnitude drag and '
         'power vs. airspeed and attitude for ~1.3-1.5 kg quadrotors close to the X500 class.'),
dict(key='bannwarth2019', kind='J',
     authors=['Bannwarth, Jérémie X. J.', 'Chen, Z. Jeremy', 'Stol, Karl A.', 'MacDonald, Bruce A.', 'Richards, Peter J.'],
     title='Aerodynamic force modeling of multirotor unmanned aerial vehicles', venue='AIAA J.',
     venue_full='AIAA Journal', volume='57', number='3', pages='1250--1259', month=3, year=2019,
     doi='10.2514/1.J057165', libkey=(258048396, 'fullTextFile', False), theme='T3',
     why='Wind-tunnel-derived multirotor force model for station-keeping simulation in turbulent wind: '
         'simulated position-error spread matched experiment within 7 % along the wind but only within 56 % '
         'across it. Good evidence that simple sims get mean-wind response right but cross-wind turbulence '
         'response poorly -- a metric to report in DroneRanger sim-vs-real comparisons.'),
dict(key='bauersfeld2022', kind='J', authors=['Bauersfeld, Leonard', 'Scaramuzza, Davide'],
     title='Range, endurance, and optimal speed estimates for multicopters', venue='IEEE Robot. Autom. Lett.',
     venue_full='IEEE Robotics and Automation Letters', volume='7', number='2', pages='2953--2960', month=4,
     year=2022, doi='10.1109/LRA.2022.3145063', libkey=(515545995, 'fullTextFile', False), theme='T3',
     why='Combines a blade-element-momentum aerodynamic model with motor and gray-box battery models (cell '
         'voltage error 1.3 %), validated up to 65 km/h; because power depends on airspeed, the same model can'
         ' be used to estimate the endurance penalty of holding position against a headwind over the garden.'),
dict(key='rodrigues2021', kind='J',
     authors=['Rodrigues, Thiago A.', 'Patrikar, Jay', 'Choudhry, Arnav', 'Feldgoise, Jacob', 'Arcot, Vaibhav', 'Gahlaut, Aradhana', 'Lau, Sophia', 'Moon, Brady'],
     et_al=True,
     title='In-flight positional and energy use data set of a DJI Matrice 100 quadcopter for small package '
           'delivery', venue='Sci. Data', venue_full='Scientific Data', volume='8', number='1', article_no='155',
     month=6, year=2021, doi='10.1038/s41597-021-00930-x', libkey=(480855971, 'fullTextFile', True), theme='T3',
     why='209 outdoor flights (10 h 45 min, ~65 km) of a 3.7-4.2 kg quadrotor carrying an onboard ultrasonic '
         'anemometer, logging wind, IMU, GPS and power; a ready public dataset to test wind-drag and power '
         'models before DroneRanger collects its own X500 logs.'),

# ----------------------------------------------------------------------------------------- T4 wind estimation
dict(key='kose2026', reuse=True, theme='T4',
     why='Quantifies PX4 SITL vs real-flight ULog discrepancies (variance, distribution shift); the '
         "statistical template for DroneRanger's sim-with-wind vs real comparison."),
dict(key='px4ekf2', reuse=True, theme='T4',
     why='EKF2 can estimate N/E wind on multirotors by fusing drag specific forces (EKF2_DRAG_CTRL, ballistic '
         'coefficients EKF2_BCOEF_X/Y, momentum drag EKF2_MCOEF), tuned from a back-and-forth flight log; '
         'enabling it gives a logged wind estimate on every real flight.'),
dict(key='neumann2015', kind='J', authors=['Neumann, Patrick P.', 'Bartholmai, Matthias'],
     title='Real-time wind estimation on a micro unmanned aerial vehicle using its inertial measurement unit',
     venue='Sens. Actuators A, Phys.', venue_full='Sensors and Actuators A: Physical', volume='235',
     pages='300--310', month=11, year=2015, doi='10.1016/j.sna.2015.09.036',
     libkey=(56776033, 'fullTextFile', False), theme='T4',
     why='Early demonstration that a multirotor IMU (tilt needed to hold position) suffices to estimate wind '
         'speed and direction in real time; the basic tilt-to-wind mapping that DroneRanger can apply to hover'
         ' segments in its PX4 logs.'),
dict(key='palomaki2017', kind='J',
     authors=['Palomaki, Ross T.', 'Rose, Nathan T.', 'van den Bossche, Michael', 'Sherman, Thomas J.', 'De Wekker, Stephan F. J.'],
     title='Wind estimation in the lower atmosphere using multirotor aircraft', venue='J. Atmos. Ocean. Technol.',
     venue_full='Journal of Atmospheric and Oceanic Technology', volume='34', number='5', pages='1183--1191',
     month=5, year=2017, doi='10.1175/JTECH-D-16-0177.1', libkey=(91369601, 'fullTextFile', False), theme='T4',
     why='Multirotors hovering 10 m above ground next to sonic anemometers; attitude-based estimates gave '
         'typical errors <0.5 m/s in speed and <30 deg in direction. Directly supports flying the X500 at 3-10'
         ' m in the garden as its own anemometer to compare against ASOS.'),
dict(key='gonzalezrocha2019', kind='J',
     authors=['González-Rocha, Javier', 'Woolsey, Craig A.', 'Sultan, Cornel', 'De Wekker, Stephan F. J.'],
     title='Sensing wind from quadrotor motion', venue='J. Guid. Control Dyn.',
     venue_full='Journal of Guidance, Control, and Dynamics', volume='42', number='4', pages='836--852', month=4,
     year=2019, doi='10.2514/1.G003542', libkey=(274179633, 'linkResolverOpenUrl', False), theme='T4',
     why='Compares kinematic-particle, dynamic-particle and rigid-body motion models for wind estimation, '
         'identified from wind-tunnel and flight data and validated beside a 10 m sonic anemometer; bandwidth '
         'rises with model fidelity and the rigid-body model gives the best speed estimates.'),
dict(key='wetz2021', kind='J', authors=['Wetz, Tamino', 'Wildmann, Norman', 'Beyrich, Frank'],
     title='Distributed wind measurements with multiple quadrotor unmanned aerial vehicles in the atmospheric '
           'boundary layer', venue='Atmos. Meas. Tech.', venue_full='Atmospheric Measurement Techniques',
     volume='14', number='5', pages='3795--3814', month=5, year=2021, doi='10.5194/amt-14-3795-2021',
     libkey=(476597378, 'contentLocation', True), theme='T4',
     why='Drag-based wind retrieval from hovering quadrotors calibrated on 76 flights against a 99 m tower: '
         'RMS deviation <0.3 m/s in speed and <8 deg in direction, with short-timescale fluctuations agreeing '
         'with tower and lidar. Best published accuracy bound for the log-based wind DroneRanger can extract.'),
dict(key='tomic2020', kind='J',
     authors=['Tomić, Teodor', 'Lutz, Philipp', 'Schmid, Korbinian', 'Mathers, Andrew', 'Haddadin, Sami'],
     title='Simultaneous contact and aerodynamic force estimation (s-CAFE) for aerial robots',
     venue='Int. J. Robot. Res.', venue_full='The International Journal of Robotics Research', volume='39',
     number='6', pages='688--728', month=5, year=2020, doi='10.1177/0278364920904788',
     libkey=(377475599, 'fullTextFile', False), theme='T4',
     why='Separates aerodynamic from contact wrenches online and estimates airspeed from propeller power and '
         'speed (ESC data), with ground truth from autonomous flights in a 3D wind tunnel; a route to wind '
         'estimation if the X500 logs ESC RPM/current.'),
dict(key='simma2020', kind='J', authors=['Simma, Magdalena', 'Mjøen, Håvard', 'Boström, Tobias'],
     title='Measuring wind speed using the internal stabilization system of a quadrotor drone', venue='Drones',
     venue_full='Drones', volume='4', number='2', article_no='23', month=6, year=2020, doi='10.3390/drones4020023',
     libkey=(394115614, 'fullTextFile', True), theme='T4',
     why='Uses only autopilot log data plus static-thrust tests; hovering beside a 2D ultrasonic anemometer in'
         ' 0-5 m/s wind gave RMSE 0.26-0.29 m/s (speed) and 4.1-4.9 deg (direction). Closest published '
         'analogue to post-processing DroneRanger PX4 ULogs into the wind the drone actually felt.'),
dict(key='hattenberger2022', kind='J',
     authors=['Hattenberger, Gautier', 'Bronz, Murat', 'Condomines, Jean-Philippe'],
     title='Estimating wind using a quadrotor', venue='Int. J. Micro Air Veh.',
     venue_full='International Journal of Micro Air Vehicles', volume='14', article_no='17568293211070824',
     month=1, year=2022, doi='10.1177/17568293211070824', libkey=(514537284, 'fullTextFile', True), theme='T4',
     why='Calibrates a drag model by global optimisation from telemetry and runs a Kalman filter for online '
         'wind speed/direction using only standard navigation sensors, demonstrated onboard; essentially the '
         'calibrate-then-filter workflow PX4 EKF2 drag fusion expects.'),
dict(key='crowe2020', kind='J',
     authors=['Crowe, David', 'Pamula, Raghava', 'Cheung, Hing Yuet', 'De Wekker, Stephan F. J.'],
     title='Two supervised machine learning approaches for wind velocity estimation using multi-rotor copter '
           'attitude measurements', venue='Sensors', venue_full='Sensors', volume='20', number='19',
     article_no='5638', month=10, year=2020, doi='10.3390/s20195638', libkey=(414919174, 'fullTextFile', True),
     theme='T4',
     why='KNN and LSTM models map hovering-drone attitude to tower-measured wind; LSTM reached 0.61 m/s '
         'average RMSE with >=20 min of training data and beat linear regression in gusty conditions. A data-'
         'driven option if DroneRanger co-locates a cheap anemometer for a few calibration flights.'),

# ----------------------------------------------------------------------------------------- T5 control and learning in wind
dict(key='oconnell2022', reuse=True, theme='T5',
     why='Neural-Fly: DAIML-learned wind representation (12 min of data) plus composite adaptation; in '
         "Caltech's Real Weather Wind Tunnel fan array at up to 12.1 m/s it beat nonlinear and adaptive "
         'baselines. Benchmark wind range and the reference fan-array validation setup.'),
dict(key='shi2019', reuse=True, theme='T5',
     why='Neural Lander: learned residual aerodynamics (ground effect) inside a stable controller; the same '
         'residual-learning recipe can fit wind-drag residuals identified from DroneRanger PX4 logs.'),
dict(key='molchanov2019', reuse=True, theme='T5',
     why='Low-level RL quadrotor policies with domain randomisation that transfer to several real vehicles and'
         ' resist external disturbances; baseline recipe to which wind randomisation would be added.'),
dict(key='zhang2025extreme', reuse=True, theme='T5',
     why='Latent-adaptation RL controller (mass x3.7, propeller constant >100x, payloads, motor failure); wind'
         ' is not the focus, but it is a candidate adaptive baseline for wind-randomised training.'),
dict(key='smeur2016', kind='J', authors=['Smeur, Ewoud J. J.', 'Chu, Qiping', 'de Croon, Guido C. H. E.'],
     title='Adaptive incremental nonlinear dynamic inversion for attitude control of micro air vehicles',
     venue='J. Guid. Control Dyn.', venue_full='Journal of Guidance, Control, and Dynamics', volume='39',
     number='3', pages='450--461', month=3, year=2016, doi='10.2514/1.G001490',
     libkey=(57418683, 'linkResolverOpenUrl', False), theme='T5',
     why='Sensor-based INDI attitude control that needs only a control-effectiveness model (adapted online) '
         'and handles actuator/measurement delay; basis of the INDI disturbance-rejection line that PX4-class '
         'vehicles can use against gusts.'),
dict(key='smeur2018', kind='J', authors=['Smeur, E. J. J.', 'de Croon, G. C. H. E.', 'Chu, Q.'],
     title='Cascaded incremental nonlinear dynamic inversion for MAV disturbance rejection',
     venue='Control Eng. Pract.', venue_full='Control Engineering Practice', volume='73', pages='79--90', month=4,
     year=2018, doi='10.1016/j.conengprac.2018.01.003', libkey=(193452379, 'fullTextFile', False), theme='T5',
     why='Cascaded INDI (attitude + position) clearly outperformed PID when a quadrotor flew in and out of a '
         '10 m/s wind-tunnel exhaust, and also worked outdoors with standard GPS; a realistic sharp-gust test '
         'case to reproduce in simulation. (Publisher OA, CC BY-NC-ND, though LibKey flags it as not OA.)'),
dict(key='tal2021', kind='J', authors=['Tal, Ezra', 'Karaman, Sertac'],
     title='Accurate tracking of aggressive quadrotor trajectories using incremental nonlinear dynamic inversion'
           ' and differential flatness', venue='IEEE Trans. Control Syst. Technol.',
     venue_full='IEEE Transactions on Control Systems Technology', volume='29', number='3', pages='1203--1218',
     month=5, year=2021, doi='10.1109/TCST.2020.3001117', libkey=(394548683, 'fullTextFile', False), theme='T5',
     why='INDI + flatness feed-forward tracks up to 12.9 m/s and 2.1 g with 6.6 cm RMS error and needs no '
         'prior aerodynamic model, rejecting drag as a disturbance (also shown with an attached drag plate); '
         'evidence that a robust inner loop can make sim-vs-real wind mismatch less critical.'),
dict(key='richards2023', kind='J',
     authors=['Richards, Spencer M.', 'Azizan, Navid', 'Slotine, Jean-Jacques', 'Pavone, Marco'],
     title='Control-oriented meta-learning', venue='Int. J. Robot. Res.',
     venue_full='The International Journal of Robotics Research', volume='42', number='10', pages='777--797',
     month=9, year=2023, doi='10.1177/02783649231165085', libkey=(574627232, 'fullTextFile', False), theme='T5',
     why='Meta-learns adaptive-control features in closed-loop simulation with tracking error as the meta-'
         'objective, beating regression-oriented meta-learning for planar rotorcraft in wind; shows how a '
         'wind-randomised simulator can be used to train adaptation, not just to test it (simulation only).'),
dict(key='wu2025l1quad', kind='J',
     authors=['Wu, Zhuohuan', 'Cheng, Sheng', 'Zhao, Pan', 'Gahlawat, Aditya', 'Ackerman, Kasey A.', 'Lakshmanan, Arun', 'Yang, Chengyu', 'Yu, Jiahao'],
     et_al=True,
     title='L1Quad: L1 adaptive augmentation of geometric control for agile quadrotors with performance '
           'guarantees', venue='IEEE Trans. Control Syst. Technol.',
     venue_full='IEEE Transactions on Control Systems Technology', volume='33', number='2', pages='597--612',
     month=3, year=2025, doi='10.1109/TCST.2024.3521182', libkey=(639561486, 'fullTextFile', False), theme='T5',
     why='L1 adaptive augmentation of an SE(3) geometric controller with uniformly bounded transients, tested '
         'on 11 uncertainty types (sloshing payloads, damaged/mixed propellers, etc.); L1 adaptive estimation '
         'is also the disturbance observer DATT uses against fan wind, so this is a natural adaptive baseline.'),
dict(key='hanover2022', kind='J',
     authors=['Hanover, Drew', 'Foehn, Philipp', 'Sun, Sihao', 'Kaufmann, Elia', 'Scaramuzza, Davide'],
     title='Performance, precision, and payloads: Adaptive nonlinear MPC for quadrotors',
     venue='IEEE Robot. Autom. Lett.', venue_full='IEEE Robotics and Automation Letters', volume='7', number='2',
     pages='690--697', month=4, year=2022, doi='10.1109/LRA.2021.3131690',
     libkey=(508338861, 'fullTextFile', False), theme='T5',
     why='L1-NMPC learns model errors online: >90 % tracking-error reduction over plain NMPC under large '
         'unknown disturbances (fan wind, unmodelled payloads) with identical gains, and ~50 % better tracking'
         ' on racing trajectories up to 70 km/h.'),
dict(key='sun2022', kind='J',
     authors=['Sun, Sihao', 'Romero, Angel', 'Foehn, Philipp', 'Kaufmann, Elia', 'Scaramuzza, Davide'],
     title='A comparative study of nonlinear MPC and differential-flatness-based control for quadrotor agile '
           'flight', venue='IEEE Trans. Robot.', venue_full='IEEE Transactions on Robotics', volume='38',
     number='6', pages='3357--3373', month=12, year=2022, doi='10.1109/TRO.2022.3177279',
     libkey=(528045932, 'fullTextFile', False), theme='T5',
     why='Up to 20 m/s, both NMPC and DFBC gain >78 % tracking-error reduction from adding an INDI inner loop '
         'and an aerodynamic drag model; quantifies how much aerodynamic modelling matters when transferring '
         'controllers from sim to real.'),
dict(key='craig2020', kind='J', authors=['Craig, William', 'Yeo, Derrick', 'Paley, Derek A.'],
     title='Geometric attitude and position control of a quadrotor in wind', venue='J. Guid. Control Dyn.',
     venue_full='Journal of Guidance, Control, and Dynamics', volume='43', number='5', pages='870--883', month=5,
     year=2020, doi='10.2514/1.G004710', libkey=(368606308, 'linkResolverOpenUrl', False), theme='T5',
     why='Feeds onboard flow-probe wind measurements into SE(3) feedback linearisation using models of blade-'
         'flapping moment and rotor induced + body drag, with variable gains for thrust saturation; shows the '
         'benefit of measured (not estimated) wind and the aerodynamic terms a wind sim must include.'),
dict(key='huang2023datt', kind='C',
     authors=['Huang, Kevin', 'Rana, Rwik', 'Spitzer, Alexander', 'Shi, Guanya', 'Boots, Byron'],
     title='DATT: Deep adaptive trajectory tracking for quadrotor control',
     venue='Proc. Conf. Robot Learn. (CoRL)', venue_full='Proceedings of The 7th Conference on Robot Learning',
     series='Proc. Mach. Learn. Res.', volume='229', pages='326--340', month=12, year=2023, publisher='PMLR',
     url='https://proceedings.mlr.press/v229/huang23a.html', theme='T5',
     why='RL policy trained only with a random-walk force disturbance in sim, augmented on hardware by an L1 '
         'disturbance estimator, outperforms adaptive NMPC in unsteady fan wind with a drag plate (34 % less '
         'error in the hardest case, <3.2 ms inference). Suggests coarse force randomisation + online '
         'adaptation can stand in for a high-fidelity wind model.'),
dict(key='habel2026gustpilot', kind='P',
     authors=['Habel, Amir Atef', 'Khan, Roohan Ahmed', 'Mehboob, Fawad', 'Fortin, Clement', 'Tsetserukou, Dzmitry'],
     title='GustPilot: A hierarchical DRL-INDI framework for wind-resilient quadrotor navigation', month=3,
     year=2026, arxiv='2603.19966', url='https://arxiv.org/abs/2603.19966', theme='T5',
     why='DRL velocity planner trained with fan-jet domain randomisation over an INDI tracker; on a 50 g '
         'Crazyflie in ducted-fan wind (up to ~7 m/s at the fan, 3.5 m/s disturbances) it reached 94.6 % '
         'success vs 36.0 % for DRL-PID and up to 50 % lower RMSE (80 flights). Recent example of wind-'
         'randomised RL transferring to real wind; preprint, not peer reviewed.'),

# ----------------------------------------------------------------------------------------- T6 wind in simulators
dict(key='dimmig2025', reuse=True, theme='T6',
     why='Systematic comparison of aerial-robot simulators; use it to justify the Gazebo vs Isaac/Pegasus '
         'choice for wind work.'),
dict(key='folk2023rotorpy', kind='P', authors=['Folk, Spencer', 'Paulos, James', 'Kumar, Vijay'],
     title='RotorPy: A Python-based multirotor simulator with aerodynamics for education and research', month=6,
     year=2023, arxiv='2306.04485', url='https://arxiv.org/abs/2306.04485', theme='T6',
     why='Pure-Python 6-DoF multirotor sim with aerodynamic wrenches, actuator limits, sensors and wind as an '
         'extra state (step, sinusoid and Dryden profiles), benchmarked against Crazyflie data and used to '
         'design a UKF wind estimator. Contributed paper at the ICRA 2023 UAV-simulator workshop; PX4 docs '
         'list it as a community-supported simulator. Fast sandbox for prototyping ASOS-driven wind before '
         'porting to Gazebo/Isaac.'),
dict(key='kakavitsas2024', kind='C',
     authors=['Kakavitsas, Nicholas', 'Willis, Andrew', 'Jacobik, Ryan', 'Uddin, Mesbah', 'Wolek, Artur'],
     title='Quadrotor flight simulation in a CFD-generated urban wind field',
     venue='Proc. IEEE Aerosp. Conf. (AERO)', venue_full='2024 IEEE Aerospace Conference', pages='1--8', month=3,
     year=2024, doi='10.1109/AERO58975.2024.10521032', publisher='IEEE', address='Big Sky, MT, USA', theme='T6',
     why='OpenStreetMap buildings -> OpenFOAM steady 3D wind field -> Gazebo plugin interpolating the field at'
         ' runtime -> PX4 SITL, compared with and without wind over a campus. The closest existing pipeline to'
         " DroneRanger's plan; ASOS would supply the inflow boundary condition."),
dict(key='imamov2024', kind='C',
     authors=['Imamov, Niyaz', 'Abbyasov, Bulat', 'Tsoy, Tatyana', 'Martínez-García, Edgar A.', 'Magid, Evgeni'],
     title='Evaluation of a weather plugin in Gazebo: A case-study of a wind influence on PX4-based UAV '
           'performance', venue='Proc. Int. Conf. Interactive Collab. Robot. (ICR)',
     venue_full='Interactive Collaborative Robotics (ICR 2024)', pages='344--356', year=2024,
     doi='10.1007/978-3-031-71360-6_26', publisher='Springer', theme='T6',
     why='Case study of a Gazebo wind/weather plugin flown with PX4 (per its title and repository record: wind'
         ' resistance, tilt and velocity evaluated); a direct precedent for the Gazebo branch of the '
         'DroneRanger plan (full text not checked).'),
dict(key='achermann2024', kind='J',
     authors=['Achermann, Florian', 'Stastny, Thomas', 'Danciu, Bogdan', 'Kolobov, Andrey', 'Chung, Jen Jen', 'Siegwart, Roland', 'Lawrance, Nicholas'],
     title='WindSeer: Real-time volumetric wind prediction over complex terrain aboard a small uncrewed aerial '
           'vehicle', venue='Nat. Commun.', venue_full='Nature Communications', volume='15', number='1',
     article_no='3507', month=4, year=2024, doi='10.1038/s41467-024-47778-4',
     libkey=(613998673, 'fullTextFile', True), theme='T6',
     why='CNN trained purely on 7361 CFD runs predicts time-averaged 3D wind from a few noisy measurements, '
         'validated on weather-station and in-flight drone wind; errors are largest near the ground and in lee'
         ' zones, and the authors note typical sUAV altitudes above 50 m -- unlike the DroneRanger 3-10 m '
         'band.'),
dict(key='olejnik2022', kind='C',
     authors=['Olejnik, Diana A.', 'Wang, Sunyi', 'Dupeyroux, Julien', 'Stroobants, Stein', 'Karasek, Matej', 'De Wagter, Christophe', 'de Croon, Guido'],
     title='An experimental study of wind resistance and power consumption in MAVs with a low-speed multi-fan '
           'wind system', venue='Proc. IEEE Int. Conf. Robot. Autom. (ICRA)',
     venue_full='2022 International Conference on Robotics and Automation (ICRA)', pages='2989--2994', year=2022,
     doi='10.1109/ICRA46639.2022.9811834', publisher='IEEE', address='Philadelphia, PA, USA', theme='T6',
     why='Open-source low-cost multi-fan wind generator: steady 0.5-3.4 m/s and periodic gusts (1.3-3.4 m/s at'
         ' 0.5/0.25/0.125 Hz) used to log attitude and power of a Crazyflie and a flapping-wing MAV; a cheap '
         'way to create repeatable gusts for validating a wind sim indoors (small vehicles only).'),
dict(key='gianfelice2022', kind='J', authors=['Gianfelice, Michael', 'Aboshosha, Haitham', 'Ghazal, Tarek'],
     title='Real-time wind predictions for safe drone flights in Toronto', venue='Results Eng.',
     venue_full='Results in Engineering', volume='15', article_no='100534', month=9, year=2022,
     doi='10.1016/j.rineng.2022.100534', libkey=(594255656, 'fullTextFile', True), theme='T6',
     why='Couples zone-wise CFD of downtown Toronto with historical/real-time meteorological station data; '
         'CFD-transferred speed and bearing were within 12 % and 8 % RMSE of station records for 85 % of '
         'samples. Demonstrates the "met-station wind -> CFD transfer -> local wind" chain DroneRanger needs '
         'for ASOS replay.'),

# ----------------------------------------------------------------------------------------- T7 operational constraints
dict(key='gao2021', kind='J',
     authors=['Gao, Mozhou', 'Hugenholtz, Chris H.', 'Fox, Thomas A.', 'Kucharczyk, Maja', 'Barchyn, Thomas E.', 'Nesbit, Paul R.'],
     title='Weather constraints on global drone flyability', venue='Sci. Rep.', venue_full='Scientific Reports',
     volume='11', number='1', article_no='12092', month=6, year=2021, doi='10.1038/s41598-021-91325-w',
     libkey=(479081776, 'fullTextFile', True), theme='T7',
     why='10 years of hourly ERA5 reanalysis (100 m wind, 0.25 deg grid) vs manufacturer limits: "common" '
         'drones (max wind 10 m/s, no rain) have median global flyability 5.7 h/day (2.0 h/day in daylight); '
         'raising the wind limit to 15 m/s gives the largest gains. Template for a San Jose ASOS-based '
         'flyability analysis (an Author Correction exists: doi 10.1038/s41598-021-00537-7).'),
dict(key='roseman2020', kind='J', authors=['Roseman, Christopher A.', 'Argrow, Brian M.'],
     title='Weather hazard risk quantification for sUAS safety risk management', venue='J. Atmos. Ocean. Technol.',
     venue_full='Journal of Atmospheric and Oceanic Technology', volume='37', number='7', pages='1251--1268',
     month=7, year=2020, doi='10.1175/JTECH-D-20-0009.1', libkey=(401428647, 'fullTextFile', False), theme='T7',
     why='Bayesian-network sUAS Weather Risk Model combining forecast weather (HRRR), population and structure'
         ' density following FAA safety-risk guidance, demonstrated over Boulder; argues fine-scale (<1 km) '
         'forecasts are needed -- coarse airport/forecast wind is not enough for go/no-go at a backyard.'),
dict(key='asos1998', kind='R',
     authors=['National Oceanic and Atmospheric Administration', 'Department of Defense', 'Federal Aviation Administration', 'United States Navy'],
     title="Automated Surface Observing System (ASOS) user's guide", month=3, year=1998,
     institution='National Oceanic and Atmospheric Administration', rtype='User guide',
     url='https://www.weather.gov/media/asos/aum-toc.pdf', theme='T7',
     why='Defines the observations: 2-min average wind from a sensor nominally at 10 m; the gust is the highest '
         '5-s average of 1-s samples. In METAR a gust is reported only when it exceeds the 10-min lull by >= 10 kt '
         '(minimum 14 kt), so most light-wind San Jose hours carry no gust; the 1-minute archive, used here, '
         'gives the peak 5-s gust of every minute.'),
]
