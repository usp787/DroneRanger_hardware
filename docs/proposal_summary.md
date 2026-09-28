# Drone Ranger — Proposal Planning Summary (Hardware Group)

*v3, 2026-09-27. Updated for the Silicon Valley campus, O1 + O2 scope, and 9/28–12/25 dates. The charter draft
is `Project Charter - Drone Ranger Hardware.docx`; its General Project Information table is left for you to fill.
Tags such as `[04]` point to `reference/` topic folders (local, git-ignored); each folder's `NOTES.md` holds the
evidence and URLs.*

---

## 0. Decisions

| Item | Decision |
|---|---|
| Group | **Hardware group**. Planning and mapping algorithms belong to the algorithm group |
| Campus | **NU Silicon Valley** (San Jose, CA) |
| Sponsor | A Northeastern PI |
| "Patrol" | Waypoint patrol of a **household garden** (outdoor) |
| Duration | **09/28/2026 – 12/25/2026** (one Fall semester, ~12.5 weeks) |
| Committed outcome | Fix and integrate the previous issues and parts, then **O1** (manual outdoor flight) + **O2** (autonomous PX4 Mission-mode garden patrol) |
| Dropped | O3 (ROS 2 offboard autonomy outdoors) and world-frame mapping |
| Open, negotiable with the PI | Budget; UAS Review Board application; garden location |

**Story:**

> Make the Drone Ranger platform safe, reliable, measurable and outdoor-ready, and prove it with an approved
> autonomous garden-patrol flight.

```
 Planning / mapping / avoidance algorithms            <- algorithm group
 ───────────────────────────────────────────────────── interface: clean depth + TF (handed over)
 Sensors: TFmini, GNSS/compass mast, Remote ID, [RTK]  <- hardware
 PX4 config: ports, EKF2 fusion, failsafes, geofence  <- hardware
 Platform safety: power rebuild, RC kill, approvals   <- hardware (first)
 Test infrastructure: SITL twin, launch, log analysis <- hardware
```

---

## 1. Scope check
**Right-sized.** Dropping O3 and the world map removes about 3 person-weeks. The remaining ~10–12 person-weeks
fit the 12.5 weeks for one person, with some buffer.

| Work package | Person-weeks (est.) |
|---|---|
| Audit (versions, parameter file, old logs, code archive) | 0.5 |
| Power rebuild + electrical tests | 1 |
| RC kill switch + PX4 failsafes/geofence + SITL failsafe tests | 1 |
| Serial link fix (FTDI cable, port map, `px4_msgs` match) | 0.5–1 |
| Sensors: TFmini + EKF2, GPS mast + compass recalibration, Remote ID, [RTK] | 1.5–2 |
| Depth/TF interface handover to the algorithm group | 0.5 |
| SITL twin + launch file + log-analysis scripts | 1.5–2 |
| Tests: indoor regression → O1 → O2 | 2 |
| Compliance paperwork (runs in parallel; takes **≥3 weeks** of calendar time) | 0.5 |
| Metrics, report, handover | 1–1.5 |

**Main risks:**
- **Paperwork lead time:** UAS Review Board approval, homeowner permission, and a Part 107 pilot.
- **The garden's airspace**, which depends on its address.
- **Short afternoons and rain later in the season:** sunset is 16:50 in early December, and the rainy season
  starts in November.

---

## 2. Where the project stands
**Spring 2026 history** (weekly reports, `[00]`):
- **Hardware:** migrated from a Raspberry Pi to a **Jetson Orin Nano 8 GB**. The Jetson's own UART failed, so a
  USB-TTL adapter is used.
- **Software:** moved from MAVSDK to uXRCE-DDS.
- **Flights:** outdoor test flights happened; the tilt-at-takeoff bug was fixed; offboard hover works.
- **Problems found:** **~0.5 m altitude error**, and the **DC plug arced on the carbon frame**.
- **Owned but unused:** a **TFmini Plus LiDAR**, and a free **Orin Nano "Super"** upgrade.

| Handover issue | Root cause (research) | Fix (hardware group) | Ref |
|---|---|---|---|
| Setpoint "reached" but drone offset | The script checks against PX4's *estimate*. Outdoor horizontal position is GNSS-only (~1–2 m) | Measure against surveyed ground markers; GPS mast + compass recalibration; RTK if funded | 01, 06 |
| Altitude error ~0.5 m | Baro/GNSS height, prop wash | Install the TFmini Plus (TELEM3 `SENS_TFMINI_CFG=103`, JST-GH adapter) and fuse it in EKF2 | 01 |
| MAVLink/XRCE port conflict | Likely a leftover `MAV_2_CONFIG` on TELEM2 *(hypothesis)* | Radio on TELEM1, Jetson XRCE on TELEM2; FTDI cable | 02 |
| Depth zeros / 34 m | 1-px disparity false matches; DepthAI v3 reversed the confidence-threshold meaning | depthai-ros v3 ROBOTICS preset + filters; documented handover to the algorithm group | 03 |
| RViz shows nothing | QoS mismatch / missing TF | Fix QoS; publish the TF tree | 02 |
| Power arcing / fire | Exposed barrel metal touching conductive carbon fiber | Fuse at the source, protected 12 V BEC, molded 5.5×2.5 mm pigtail, insulating plate | 04 |
| No sim / launch / plots | — | `make px4_sitl gz_x500_depth`, one launch file, ULog → Flight Review | 02 |

**Issues the handover doesn't mention:**
- **No RC kill switch** in the inventory.
- **Unsafe PX4 defaults** (low battery = warning only, geofence off).
- **PX4 v1.16+ `_v1` topic names.**
- **Hover time ~11–13 min** with the payload. `[02][04]`

---

## 3. Outdoor flying near San Jose (`[07]`, federal detail in `[04]`)

**Bottom line:** no California, San Jose or Santa Clara County *permit* is needed to fly over a consenting
homeowner's garden. The binding constraints are **federal rules, NU approval and privacy**. *(Not legal advice;
confirm with the UAS Review Board.)*

### 3.1 Compliance checklist (H = hard requirement)
- **Federal:**
  - [H] FAA registration ($5), with the number on the aircraft.
  - [H] A **Remote ID broadcast module** (FAA DOC-accepted, ~$40). Not needed inside a FRIA.
  - [H] A **Part 107** remote pilot in command. Students may fly under their direct supervision.
  - [H] VLOS, and **no flight over non-participants**: neighbors, people on the street.
  - [H] **LAANC before each flight if the garden is in controlled airspace.**
  - [H] Check TFRs on the day: Levi's/Stanford game days, wildfire TFRs.
- **California:**
  - [H] **Civil Code §1708.8:** it is illegal to enter "the airspace above the land of another" to capture images
    of private activity (up to 3× damages plus fines). Stay inside the lot and don't image neighbors.
  - [H] No viewing into windows (PC §647(j)).
  - [H] No audio recording (PC §632). The OAK-D Lite has no microphone.
  - [H] Land if an emergency response or wildfire is nearby (PC §402).
  - The new AB 2113 (no drones within 400 ft of ticketed events) takes effect **2027-01-01**, after this semester.
- **Local:**
  - San Jose has no drone ordinance. Parks need a designated area (SJMC 13.44.160).
  - County parks need a permit.
  - **City of Santa Clara (Ord. 2080):** no take-off within 2 mi of Levi's events, plus limits over schools and
    critical sites. **Los Gatos** and **Morgan Hill** have their own strict codes.
- **Northeastern:**
  - [H] **UAS Review Board approval**: an NU-employee applicant, **≥3 weeks** ahead.
  - [H] **Written homeowner permission** attached to the application.
  - [H] **No imaging of any other private property** without that owner's permission.
  - [H] Faculty supervision.
- **Good practice:**
  - notify the neighbors;
  - point the camera nadir or inward; a PX4 geofence inside the lot line;
  - morning flights (≈1 day in 5 has gusts ≥25 mph at SJC);
  - consider an anti-collision strobe for twilight flights.

### 3.2 Airspace (FAA UAS Facility Map, 2026-09-03; re-check the exact address)
| Area | LAANC ceiling |
|---|---|
| NU SV campus (4 N 2nd St, downtown) | 100 ft (SJC Class C). **Don't fly at campus**: leased building, no flight space |
| Willow Glen, Rose Garden, Berryessa, Milpitas, Santa Clara, Campbell | 200–400 ft (LAANC) |
| East San Jose near Reid-Hillview; north Sunnyvale near Moffett | **0 ft**, manual authorization only |
| Mountain View / Palo Alto | Moffett/Palo Alto airports are not LAANC-enabled, so manual authorization |
| Almaden, Cambrian, Blossom Valley, Los Gatos, Saratoga, Cupertino, Fremont, Morgan Hill, Gilroy | **No grid: Class G / E extension, no authorization needed** |

### 3.3 Test ladder and sites
| Step | What | Where |
|---|---|---|
| O0 | SITL rehearsal of the garden mission; indoor regression | Lab / laptop |
| **O1** | Manual/Position-mode outdoor flight: compass, GNSS, RC kill, RTL, geofence, battery failsafe | **SCCMAS AMA field, Morgan Hill** (Class G + FRIA, multirotors allowed; needs AMA membership and the club's OK for a university flight), **or** the garden itself if it is in Class G |
| **O2** | Autonomous **PX4 Mission-mode** waypoint loop (≥4 waypoints + RTL) over the garden | The household garden (homeowner permission; geofence inside the lot line) |

**Season** (San Jose):
- **Daylight:** sunset 18:10 on Oct 31, then 17:09 after DST ends (Nov 1), down to 16:50 in early December.
- **Rain:** Oct 0.5 in → Nov 1.3 in → Dec 2.3 in.
- **Target windows:** O1 early November, O2 mid to late November, with December as buffer.

---

## 4. The charter draft
The draft (`Project Charter - Drone Ranger Hardware.docx`) follows this plan, one short paragraph per box:
- **Problem:** the safety, reliability and positioning gaps, plus no approved outdoor flight. [1-6]
- **Purpose:** harden the platform, ending in an autonomous garden patrol. [5-8], [14-16]
- **Business case:** security drone market 13–20%/yr; a ~$10k residential system and $15–25k enterprise drones
  vs our ~$1.5k in parts. [9-12]
- **Goals/Methods/Metrics:**
  - 0 electrical incidents and 0 link drops;
  - 100% of failsafes verified;
  - altitude RMSE ≤ 0.15 m (from 0.5 m);
  - waypoint error measured (≤ 0.3 m with RTK);
  - ≥1 autonomous outdoor patrol loop;
  - ≥10 min flight time.
- **Deliverables:** platform; configuration and test toolkit; outdoor flight package; evaluation report and
  handover.
- **Scope:**
  - *In:* hardware, PX4 configuration, SITL, O1/O2 under NU, FAA and California rules.
  - *Out:* algorithms, O3, flights beyond visual line of sight, at night or over people, multi-drone, RL, imaging
    neighbors.
- **Schedule:** DMAIC rows, 09/28 → 12/25, with the UAS Review Board filing in the Define phase.
- **References:** 16 IEEE entries. Market figures are cited as vendor estimates.

**You still need to fill in:** project name, PI/sponsor, students, emails, expertise. Also adjust any number the
PI disagrees with (targets, RTK).

## 5. Questions for the PI
1. **Where is the garden (address)?** This decides the airspace (Class G vs LAANC vs 0 ft) and the city code.
   Does the homeowner agree in writing? Is there an HOA?
2. **Who files with the UAS Review Board** (an NU employee), and **who is the Part 107 pilot in command** for the
   SV flights?
3. **Budget:** must-haves ≈ $260–350; RTK +$464 (Appendix A).
4. Is **O1 at the SCCMAS field** acceptable (AMA membership, the club's consent, insurance)? Or the NU Oakland
   campus?
5. Will the Review Board accept "camera inward + neighbor notice", or does it want **written neighbor consent**?
   Is an IRB determination needed for incidental images of people?

## 6. First-week actions
- **Read the current state off the drone:**
  - `ver all` on PX4 (firmware version);
  - `cat /etc/nv_tegra_release` on the Jetson (JetPack version);
  - export the PX4 parameter file;
  - check the DepthAI version and settings.
- **Collect the Spring 2026 material:** ULog/rosbags, the `~/drone_test` archive, and wiring photos.
- **Start the paperwork:**
  - PI meeting;
  - UAS Review Board email (UASRB@northeastern.edu);
  - look up the garden's airspace in a LAANC app;
  - order the Remote ID module, BEC/fuse and cables.
- **No flights until** the power fix and the RC kill switch are in place.

---

## Appendix A — Hardware investment
**No GPU purchase is needed.** The RTX 4060 laptop runs PX4 SITL + Gazebo. RL / Isaac Sim are out of scope.

| Priority | Item | Why | Approx. price | Ref |
|---|---|---|---|---|
| Must | RC transmitter + receiver with kill switch (if none) | Safety layer independent of the Jetson | ~$60 + $19 | 02, 04 |
| Must | Power rebuild (fuse, protected 12 V BEC, molded pigtail, insulation) | Fire hazard | ~$40–60 | 04 |
| Must | Remote ID broadcast module (verify on the FAA DOC list) + FAA registration | Legally required outdoors | ~$40 + $5 | 04, 07 |
| Must | GPS mast; TFmini JST-GH adapter; FTDI cable | Compass interference; altitude fix; reliable link | ~$10–20; ~$5–15; ~$24 | 01, 02 |
| Must | Batteries (≥3 total) + LiPo bag; tape measure + ground markers | ~10 min flights; accuracy truth | ~$40–60 each; ~$20 | 04 |
| Must ($0) | Orin Nano Super mode (check BEC ≥25 W); PX4 geofence polygon | Free compute headroom; privacy/§1708.8 control | $0 | 01, 07 |
| Recommended | **RTK GNSS** (H-RTK F9P rover + base) | Centimeter-level waypoints near fences and flower beds | $205 + $259 | 01, 06 |
| Conditional | Anti-collision strobe (twilight flights); handheld anemometer; AMA membership (for SCCMAS) | Late-afternoon flights; wind gate; test field | tens of dollars each (unverified) | 07 |
| Low | Spare Jetson ($399); optical flow ($145); OAK-D Pro W ($529) | Mostly indoor benefits | — | 01, 03, 05 |

## Appendix B — Future work (not in this charter)
- **O3:** ROS 2 offboard patrol from the Jetson.
- **World-frame garden map:** a bridge topic between the groups. The hardware side is calibration, time sync and
  pose quality.
- **Planner integration** (algorithm group).
- **Other:**
  - RTK vs GNSS accuracy study;
  - precision landing on a garden pad;
  - endurance optimization;
  - Jazzy / JetPack 7 migration before Humble's end of life (May 2027).

## Appendix C — Reference map
See `reference/INDEX.md` for the overview.

| Folder | Covers |
|---|---|
| `00_prev_student_reports/` | Weekly reports (history) |
| `01_state_estimation_accuracy/` | TFmini, EKF2, GNSS/RTK, ground truth |
| `02_px4_ros2_control_stack/` | Ports, `px4_msgs`, SITL, failsafe parameters, tooling |
| `03_perception_planning/` | Depth fixes, algorithm-side background |
| `04_power_safety_compliance/` | Power, LiPo, FAA federal rules, NU Policy 615 / UAS Review Board |
| `05_proposal_context_literature/` | Market, comparables, surveys, metrics |
| `06_outdoor_garden/` | PX4 RTK, GPS mounting, Mission/Return modes |
| `07_california_silicon_valley/` | CA statutes, local codes, South Bay airspace, FRIAs/AMA fields, season |

### Caveats
- **Hypothesis:** the port-conflict diagnosis.
- **Estimates:** the TFmini gain, flight time, effort and several prices.
- **Unverified:** the Remote ID module's FAA DOC status, and the garden's airspace (address pending).
- **Not checked:** the Sunnyvale, Cupertino, Fremont and Palo Alto city codes.
- **Not legal advice.**
