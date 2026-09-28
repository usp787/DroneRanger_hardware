# DroneRanger_hardware

Hardware group repository for **Drone Ranger**, a Northeastern University (Silicon Valley) CS 7980 research
capstone, Fall 2026. The goal is a low-cost autonomous drone that patrols a household garden.

This semester the hardware group will make the Spring 2026 prototype **safe, reliable, measurable and
outdoor-ready**. The work ends with an approved autonomous waypoint patrol over a household garden. Planning,
mapping and obstacle-avoidance algorithms belong to the algorithm group.

> **Status: proposal phase** (charter drafted, 2026-09-27). No flight code has been committed yet.

## Platform
| Component | Part |
|---|---|
| Airframe | Holybro X500 V2 (4S LiPo) |
| Flight controller | Pixhawk 6C running PX4, Holybro M10 GPS |
| Companion computer | NVIDIA Jetson Orin Nano 8 GB (Ubuntu 22.04, ROS 2 Humble) |
| Perception | Luxonis OAK-D Lite stereo depth camera |
| Link | PX4 uXRCE-DDS over TELEM2 ↔ USB-TTL ↔ Jetson; SiK radio ↔ QGroundControl |
| To be installed | TFmini Plus rangefinder, GPS mast, Remote ID module, RC kill switch; RTK GNSS if funded |

## Semester plan (09/28/2026 – 12/25/2026)
| Step | What | Done when |
|---|---|---|
| Fix | Rebuild power wiring (fused, insulated); fix the PX4 ↔ Jetson link; install sensors; configure EKF2, failsafes and geofence | 0 electrical incidents, 0 link drops, 100% of failsafes verified |
| O0 | Rehearse in PX4 SITL (`gz_x500_depth`) + indoor regression flights | Every mission passes in simulation first |
| **O1** | Manual / Position-mode outdoor flight | Compass, GNSS, RC kill, RTL and geofence verified outdoors |
| **O2** | Autonomous PX4 Mission-mode patrol loop over the garden | ≥ 1 loop (≥ 4 waypoints + return) with no pilot takeover |

Accuracy targets:
- hover altitude RMSE ≤ 0.15 m (the Spring baseline had up to 0.5 m error);
- waypoint error measured against surveyed ground markers;
- ≥ 10 min usable flight time.

## Repository layout
| Path | Contents |
|---|---|
| `Project Charter - Drone Ranger Hardware.docx` | Project charter (proposal) |
| `docs/proposal_summary.md` | Planning brief: project status, root causes of the handover issues, compliance checklist, test plan, hardware budget, questions for the PI |
| `reference/` | Research library (papers, datasheets, docs, regulations). **Local only, git-ignored.** Start at `reference/INDEX.md` |

Planned additions as the work proceeds: wiring diagram and bill of materials, versioned PX4 parameter file,
SITL/launch files, pre-flight checklists, and post-flight log-analysis scripts.

## Safety and compliance
- **No flights until** the power system is rebuilt and an RC kill switch is working.
- Every flight needs **Northeastern UAS Review Board approval** (Policy 615), filed ≥ 3 weeks ahead by an NU
  employee.
- **Outdoor flights also need:**
  - FAA registration and Remote ID;
  - a Part 107 pilot in command;
  - LAANC authorization where the airspace requires it;
  - written homeowner permission.
- **Respect privacy** (California Civil Code §1708.8): keep the camera and the geofence inside the host property,
  and never image neighbors.

## Background
This work continues the Spring 2026 prototype. The previous student's technical handover document and the course
charter template are kept locally and are not committed.
