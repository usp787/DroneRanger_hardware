#!/usr/bin/env python
"""Stage-B check: Isaac Sim 5.1 headless + Pegasus imports + WindDrag, without PX4.

    ./python.sh check_isaac.py --log $RUN_DIR/check_isaac.csv

Spawns Pegasus' Iris on a local ground plane with no flight-control backend (rotors stay off), applies a constant
dummy wind and steps 2 s of physics. It prints ISAAC_PEGASUS_OK when the app starts, Pegasus imports, the vehicle
spawns, physics steps and WindDrag applies a non-zero force. Run it before the full smoke test so problems in
Isaac/Pegasus are separated from problems in PX4 or MAVLink. Unknown arguments are passed on to Kit.
"""
import argparse
import pathlib
import sys
import time

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--log", type=pathlib.Path, required=True)
ap.add_argument("--wind", default="constant:5,0,0")
ap.add_argument("--seconds", type=float, default=2.0)
args, kit_args = ap.parse_known_args()
sys.argv = [sys.argv[0]] + kit_args

t_start = time.time()
from isaacsim import SimulationApp  # noqa: E402

simulation_app = SimulationApp({"headless": True})
print(f"[check_isaac] SimulationApp started in {time.time() - t_start:.0f} s", flush=True)

import os  # noqa: E402

if os.environ.get("PEGASUS_EXT_DIR"):   # python.sh may rewrite PYTHONPATH; this always works
    sys.path.insert(0, os.environ["PEGASUS_EXT_DIR"])

from isaacsim.core.utils.extensions import enable_extension  # noqa: E402

for ext in ("omni.isaac.core", "omni.isaac.dynamic_control"):
    enable_extension(ext)
simulation_app.update()

import omni.timeline  # noqa: E402
from isaacsim.core.api.objects import GroundPlane  # noqa: E402
from isaacsim.core.api.world import World  # noqa: E402
from pegasus.simulator.logic.interface.pegasus_interface import PegasusInterface  # noqa: E402
from pegasus.simulator.logic.vehicles.multirotor import Multirotor, MultirotorConfig  # noqa: E402
from pegasus.simulator.params import ROBOTS  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from wind_drag import WindDrag  # noqa: E402
from wind_publisher import WindPublisher, from_spec  # noqa: E402

print("[check_isaac] Pegasus imported", flush=True)
pg = PegasusInterface()
pg._world = World(**pg._world_settings)
world = pg.world
world.scene.add(GroundPlane(prim_path="/World/GroundPlane", size=50.0, z_position=0.0))
args.log.parent.mkdir(parents=True, exist_ok=True)
drag = WindDrag(WindPublisher(from_spec(args.wind)), log_path=str(args.log), log_every=25)
config = MultirotorConfig()
config.drag = drag
config.backends = []
Multirotor("/World/quadrotor", ROBOTS["Iris"], 0, [0.0, 0.0, 0.5], [0.0, 0.0, 0.0, 1.0], config=config)
world.reset()
omni.timeline.get_timeline_interface().play()
steps = 0
while drag.t < args.seconds and steps < 100000:
    world.step(render=False)
    steps += 1
drag.close()
force = abs(drag.drag[0]) + abs(drag.drag[1])
ok = drag.t >= args.seconds and force > 0.0
print(f"[check_isaac] {steps} steps, sim t={drag.t:.2f} s, last wind {drag.wind}, last drag force {drag.drag} N",
      flush=True)
print("ISAAC_PEGASUS_OK" if ok else "ISAAC_PEGASUS_FAILED", flush=True)
simulation_app.close()
sys.exit(0 if ok else 1)
