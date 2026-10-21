#!/usr/bin/env python
"""Scripted flight for the wind smoke test (MAVSDK-Python, the Spring 2026 scripted-flight stack).

Arms PX4 SITL, takes off to --alt, holds position (PX4 Hold mode) until smoke_wind.py marks the wind profile as
finished (it writes <sim log>.done), then lands and disarms. PX4's own telemetry is logged as a second view.

    python fly_hover.py --done-file $RUN_DIR/sim_log.csv.done --log $RUN_DIR/px4_telemetry.csv

Needs `pip install "mavsdk<4"` (any Python 3.9+). PX4 SITL instance i sends its offboard/API MAVLink stream to UDP
14540+i, but PX4 v1.14 sends every instance above 9 to UDP 14549 instead.
"""
import argparse
import asyncio
import csv
import pathlib
import time

from mavsdk import System

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--url", default="udpin://0.0.0.0:14540", help="MAVSDK connection URL")
ap.add_argument("--alt", type=float, default=3.0, help="take-off altitude, m")
ap.add_argument("--done-file", type=pathlib.Path, required=True, help="file smoke_wind.py writes when finished")
ap.add_argument("--log", type=pathlib.Path, required=True)
ap.add_argument("--timeout", type=float, default=900.0, help="wall-clock limit for the hover phase, s")
ap.add_argument("--connect-timeout", type=float, default=1500.0,
                help="wait this long for PX4 (Isaac Sim's first start compiles shaders), s")
ap.add_argument("--relax-link-failsafes", action="store_true",
                help="set NAV_RCL_ACT=0 and NAV_DLL_ACT=0 (no RC or GCS in SITL) before arming")
args = ap.parse_args()


async def wait_for(predicate_stream, label, timeout=120.0):
    t0 = time.time()
    async for value in predicate_stream:
        if value:
            print(f"[fly_hover] {label}: ok")
            return
        if time.time() - t0 > timeout:
            raise TimeoutError(label)


async def log_telemetry(drone, stop):
    args.log.parent.mkdir(parents=True, exist_ok=True)
    att = {"roll": float("nan"), "pitch": float("nan"), "yaw": float("nan")}

    async def attitude():
        async for a in drone.telemetry.attitude_euler():
            att.update(roll=a.roll_deg, pitch=a.pitch_deg, yaw=a.yaw_deg)

    task = asyncio.ensure_future(attitude())
    with open(args.log, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["wall_s", "n", "e", "d", "vn", "ve", "vd", "roll_deg", "pitch_deg", "yaw_deg"])
        t0 = time.time()
        async for pv in drone.telemetry.position_velocity_ned():
            p, v = pv.position, pv.velocity
            w.writerow([f"{time.time() - t0:.2f}", p.north_m, p.east_m, p.down_m, v.north_m_s, v.east_m_s,
                        v.down_m_s, att["roll"], att["pitch"], att["yaw"]])
            if stop.is_set():
                break
    task.cancel()


async def statustext(drone):
    async for s in drone.telemetry.status_text():
        print(f"[px4] {s.type}: {s.text}")


async def fly(drone):
    # connect() starts the local mavsdk_server and opens a gRPC channel to it. mavsdk_server opens its gRPC port only
    # after it has seen PX4 on args.url, so this wait also covers Isaac's start (shader compile) and PX4's boot.
    try:
        await asyncio.wait_for(drone.connect(system_address=args.url), timeout=args.connect_timeout)
    except asyncio.TimeoutError:
        raise SystemExit(f"[fly_hover] mavsdk_server saw no PX4 on {args.url} within {args.connect_timeout:.0f} s: "
                         "check that the 'Onboard' line in px4.log sends to this port and that Isaac connected to "
                         "PX4. If this log shows 'HTTP proxy handshake ... 403', localhost is not in no_proxy "
                         "(see explorer/env.sh)")
    print(f"[fly_hover] mavsdk_server found PX4 on {args.url}", flush=True)
    asyncio.ensure_future(statustext(drone))
    await wait_for((s.is_connected async for s in drone.core.connection_state()), "connected", args.connect_timeout)
    await wait_for((h.is_global_position_ok and h.is_home_position_ok async for h in drone.telemetry.health()),
                   "global position + home", 300)
    if args.relax_link_failsafes:
        for name in ("NAV_RCL_ACT", "NAV_DLL_ACT"):
            await drone.param.set_param_int(name, 0)
            print(f"[fly_hover] {name} = 0")

    # PX4 ends Takeoff once within NAV_MC_ALT_RAD (default 0.8 m) of the target and then holds wherever it is: with
    # the default it held 2.2 m, below smoke_wind.py's 2.5 m wind trigger (smoke job 11291459)
    await drone.param.set_param_float("NAV_MC_ALT_RAD", 0.1)
    print("[fly_hover] NAV_MC_ALT_RAD = 0.1")

    stop = asyncio.Event()
    logger = asyncio.ensure_future(log_telemetry(drone, stop))
    await drone.action.set_takeoff_altitude(args.alt)
    await drone.action.arm()
    await drone.action.takeoff()
    print(f"[fly_hover] take-off to {args.alt} m; holding until {args.done_file} appears")

    t0 = time.time()
    while not args.done_file.exists():
        if time.time() - t0 > args.timeout:
            print("[fly_hover] timeout waiting for the sim; landing")
            break
        await asyncio.sleep(1.0)

    await drone.action.land()
    await wait_for((not a async for a in drone.telemetry.in_air()), "landed", 120)
    stop.set()
    await asyncio.sleep(1.0)
    logger.cancel()
    print("[fly_hover] done")


async def main():
    drone = System()
    try:
        await fly(drone)
    finally:
        # MAVSDK reads mavsdk_server's output in a non-daemon thread and kills the server from atexit, which Python
        # runs only after joining that thread: without this the script never exits (smoke job 11290435).
        drone._stop_mavsdk_server()


if __name__ == "__main__":
    asyncio.run(main())
