#!/usr/bin/env python
"""Smoke test: Isaac Sim 5.1 + Pegasus 5.1 + PX4 SITL v1.14.3 with the wind publisher (dummy wind).

Run with Isaac Sim's Python (inside the container on Explorer, see ../explorer/run_smoke.sbatch):

    ./python.sh smoke_wind.py --px4-dir $PX4_DIR --wind smoke --log $RUN_DIR/sim_log.csv

What it does
  1. Starts Isaac Sim headless, builds a World with Pegasus' PX4 settings (physics 250 Hz, lockstep) and a
     local ground plane. The plane needs no NVIDIA asset server, which Explorer compute nodes may not reach.
  2. Puts the PX4 GPS origin at the NU Silicon Valley campus, ready for the San Jose wind data in a later week.
  3. Spawns Pegasus' Iris with the PX4 MAVLink backend and WindDrag(WindPublisher(profile)) as its drag model.
  4. Steps physics until the wind profile has finished (the profile clock starts when the vehicle first
     climbs above --trigger-alt, i.e. after fly_hover.py has taken off), then writes <log>.done and exits.

PX4 is either autolaunched by Pegasus (--px4-autolaunch, the legacy setup) or started separately and connects
to TCP 4560 + instance (default here, so PX4 can run from its own build container).

Pegasus is imported from PYTHONPATH (not `pip install -e`, whose setup.py edits a .kit file inside the read-only
Isaac image). The two deprecated extensions Pegasus' vehicle code imports are enabled explicitly below; the
`isaacsim.replicator.agent.core` dependency is needed only by Pegasus' People module, which is not used here.
Arguments this script does not know (e.g. --portable-root DIR) are passed on to Kit.
"""
import argparse
import pathlib
import sys
import time

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--px4-dir", required=True, help="PX4-Autopilot checkout built with 'make px4_sitl_default'")
ap.add_argument("--instance", type=int, default=0,
                help="PX4 instance / Pegasus vehicle_id: TCP 4560+i, MAVLink UDP 14540+i (unique per shared node; "
                     "keep i <= 8, PX4 v1.14 sends instances above 9 to UDP 14549)")
ap.add_argument("--px4-autolaunch", action="store_true", help="let Pegasus start PX4 (needs PX4 runnable here)")
ap.add_argument("--px4-model", default="gazebo-classic_iris", help="PX4_SIM_MODEL / airframe for PX4 v1.14")
ap.add_argument("--wind", default="smoke", help="none | smoke | constant:E,N[,U] | csv:<path>")
ap.add_argument("--trigger-alt", type=float, default=2.5, help="start the wind clock above this height, m")
ap.add_argument("--drag", type=float, nargs=3, default=[0.50, 0.30, 0.0], help="linear drag, N/(m/s), FLU")
ap.add_argument("--log", type=pathlib.Path, required=True, help="CSV log of state, wind and drag force")
ap.add_argument("--max-sim-time", type=float, default=600.0, help="give up after this much simulated time, s")
ap.add_argument("--origin", type=float, nargs=3, default=[37.3377, -121.8898, 30.0], help="lat lon alt")
ap.add_argument("--gui", action="store_true", help="open the Isaac Sim window (default: headless)")
args, kit_args = ap.parse_known_args()
sys.argv = [sys.argv[0]] + kit_args

from isaacsim import SimulationApp  # noqa: E402  (must come before any omni import)

simulation_app = SimulationApp({"headless": not args.gui})

import os  # noqa: E402

if os.environ.get("PEGASUS_EXT_DIR"):   # python.sh may rewrite PYTHONPATH; this always works
    sys.path.insert(0, os.environ["PEGASUS_EXT_DIR"])

from isaacsim.core.utils.extensions import enable_extension  # noqa: E402

for ext in ("omni.isaac.core", "omni.isaac.dynamic_control"):   # deprecated in 5.x, still used by Pegasus 5.1.0
    enable_extension(ext)
simulation_app.update()

import carb  # noqa: E402
import omni.timeline  # noqa: E402
from isaacsim.core.api.objects import GroundPlane  # noqa: E402
from isaacsim.core.api.world import World  # noqa: E402  (the class PegasusInterface itself uses)
from pegasus.simulator.logic.backends.px4_mavlink_backend import (  # noqa: E402
    PX4MavlinkBackend, PX4MavlinkBackendConfig)
from pegasus.simulator.logic.interface.pegasus_interface import PegasusInterface  # noqa: E402
from pegasus.simulator.logic.vehicles.multirotor import Multirotor, MultirotorConfig  # noqa: E402
from pegasus.simulator.params import ROBOTS  # noqa: E402
from scipy.spatial.transform import Rotation  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from wind_drag import WindDrag  # noqa: E402
from wind_publisher import WindPublisher, from_spec  # noqa: E402


def main():
    timeline = omni.timeline.get_timeline_interface()
    pg = PegasusInterface()
    pg.set_global_coordinates(*args.origin)          # before the vehicle: sensors read it at creation
    pg._world = World(**pg._world_settings)         # Pegasus' PX4 world settings (physics_dt 1/250)
    world = pg.world
    world.scene.add(GroundPlane(prim_path="/World/GroundPlane", size=200.0, z_position=0.0))

    args.log.parent.mkdir(parents=True, exist_ok=True)
    publisher = WindPublisher(from_spec(args.wind), trigger_alt=args.trigger_alt)
    wind_drag = WindDrag(publisher, drag_coefficients=args.drag, log_path=str(args.log))

    config = MultirotorConfig()
    config.drag = wind_drag
    config.backends = [PX4MavlinkBackend(PX4MavlinkBackendConfig({
        "vehicle_id": args.instance,
        "px4_autolaunch": args.px4_autolaunch,
        "px4_dir": args.px4_dir,
        "px4_vehicle_model": args.px4_model,
    }))]
    Multirotor("/World/quadrotor", ROBOTS["Iris"], args.instance, [0.0, 0.0, 0.07],
               Rotation.from_euler("XYZ", [0.0, 0.0, 0.0], degrees=True).as_quat(), config=config)
    world.reset()

    carb.log_warn(f"[smoke_wind] wind={args.wind} trigger_alt={args.trigger_alt} log={args.log}")
    # PX4 runs in lockstep, so its clock only advances while we step: keep stepping after the profile ends until
    # fly_hover.py (which watches the .done file) has landed the vehicle, then exit.
    done_file = pathlib.Path(str(args.log) + ".done")
    timeline.play()
    wall0, done_at, landed_since, reported = time.time(), None, None, False
    while simulation_app.is_running():
        world.step(render=args.gui)
        t = wind_drag.t
        if publisher.started and not reported:
            carb.log_warn(f"[smoke_wind] wind clock started at sim t={t:.1f} s")
            reported = True
        if publisher.done and done_at is None:
            done_at = t
            done_file.write_text(f"profile_done_sim_time {t:.2f}\n")
            carb.log_warn(f"[smoke_wind] profile finished at sim t={t:.1f} s; waiting for landing")
        if done_at is not None:
            if wind_drag.last_altitude < 0.2:
                landed_since = t if landed_since is None else landed_since
                if t - landed_since > 3.0:
                    break
            else:
                landed_since = None
            if t > done_at + 120.0:
                carb.log_error("[smoke_wind] no landing within 120 s of sim time after the profile; exiting")
                break
        if t > args.max_sim_time:
            carb.log_error("[smoke_wind] max sim time reached before the profile finished (did the drone take off?)")
            done_file.write_text("profile_done_sim_time none\n")
            break

    wind_drag.close()
    with open(done_file, "a") as f:
        f.write(f"exit_sim_time {wind_drag.t:.2f}\nwall_time {time.time() - wall0:.1f}\n"
                f"profile_done {publisher.done}\n")
    carb.log_warn(f"[smoke_wind] sim {wind_drag.t:.1f} s in {time.time() - wall0:.1f} s wall time")
    timeline.stop()
    simulation_app.close()


if __name__ == "__main__":
    main()
