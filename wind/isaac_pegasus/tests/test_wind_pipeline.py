"""Offline tests for the wind publisher, WindDrag and the smoke-test checker (no Isaac Sim needed).

    python wind/isaac_pegasus/tests/test_wind_pipeline.py        # or: python -m pytest wind/isaac_pegasus/tests

The closed-loop test replaces Isaac Sim + PX4 by a point-mass quadrotor with a PID position controller and a
thrust-aligned attitude, drives it through the same WindPublisher -> WindDrag -> log path the Isaac app uses,
and runs check_smoke.py on the log. It checks sign conventions and the checker logic, not Pegasus itself.
"""
import pathlib
import sys
import tempfile

import numpy as np
from scipy.spatial.transform import Rotation

SIM = pathlib.Path(__file__).resolve().parents[1] / "sim"
sys.path.insert(0, str(SIM))
from check_smoke import run_checks  # noqa: E402
from wind_drag import WindDrag  # noqa: E402
from wind_publisher import SMOKE_SCHEDULE, Schedule, WindPublisher, from_spec  # noqa: E402


class FakeState:
    """The fields of pegasus.simulator.logic.state.State that WindDrag reads."""

    def __init__(self, position=(0, 0, 0), velocity=(0, 0, 0), quat=(0, 0, 0, 1)):
        self.position = np.array(position, dtype=float)
        self.linear_velocity = np.array(velocity, dtype=float)
        self.attitude = np.array(quat, dtype=float)
        self.linear_body_velocity = Rotation.from_quat(self.attitude).inv().apply(self.linear_velocity)


def test_zero_wind_matches_linear_drag():
    s = FakeState(velocity=(1.0, -2.0, 0.5), quat=Rotation.from_euler("z", 30, degrees=True).as_quat())
    f = WindDrag(WindPublisher(from_spec("none"))).update(s, 0.004)
    assert np.allclose(f, -np.diag([0.5, 0.3, 0.0]) @ s.linear_body_velocity)


def test_hovering_vehicle_is_pushed_downwind():
    s = FakeState(position=(0, 0, 3), quat=Rotation.from_euler("z", 90, degrees=True).as_quat())  # nose north
    d = WindDrag(WindPublisher(from_spec("constant:3,0,0")))
    f_world = Rotation.from_quat(s.attitude).apply(d.update(s, 0.004))
    assert f_world[0] > 0 and abs(f_world[1]) < 1e-9   # east wind, nose north: body y carries it (0.3 * 3)
    assert np.isclose(f_world[0], 0.9)


def test_moving_with_the_wind_feels_no_drag():
    s = FakeState(velocity=(3.0, 0.0, 0.0))
    assert np.allclose(WindDrag(WindPublisher(from_spec("constant:3,0,0"))).update(s, 0.004), 0.0)


def test_trigger_and_schedule():
    p = WindPublisher(Schedule(SMOKE_SCHEDULE), trigger_alt=2.5)
    assert np.allclose(p.update(10.0, 1.0), 0) and not p.started
    p.update(12.0, 2.6)
    assert p.started and np.allclose(p.update(12.0 + 20.0, 3.0), [3, 0, 0])
    assert not p.done and (p.update(12.0 + 95.0, 3.0) is not None) and p.done


def test_csv_profile_roundtrip(tmp_path=None):
    tmp = pathlib.Path(tmp_path or tempfile.mkdtemp())
    path = tmp / "w.csv"
    path.write_text("t_s,wind_e,wind_n,wind_u,speed,from_deg\n0,1,0,0,1,270\n10,3,2,0,3.6,236\n")
    w = from_spec(f"csv:{path}")
    assert np.allclose(w.wind_enu(5.0), [2, 1, 0]) and w.duration == 10.0 and np.allclose(w.wind_enu(11), 0)


def fly_point_mass(log_path, mass=1.5, dt=1 / 250, t_end=115.0):
    """PID position hold at 3 m with the thrust axis as attitude (yaw 0), through WindDrag."""
    g = np.array([0, 0, 9.81])
    drag = WindDrag(WindPublisher(from_spec("smoke"), trigger_alt=2.5), log_path=str(log_path))
    p, v, integ = np.array([0, 0, 0.07]), np.zeros(3), np.zeros(3)
    ref = np.array([0, 0, 3.0])
    quat = np.array([0, 0, 0, 1.0])
    kp, kd, ki = np.array([2.0, 2.0, 4.0]), np.array([2.5, 2.5, 4.0]), np.array([0.6, 0.6, 1.0])
    for _ in range(int(t_end / dt)):
        s = FakeState(p, v, quat)
        f_world = Rotation.from_quat(quat).apply(drag.update(s, dt))
        e = ref - p
        integ += e * dt
        thrust = mass * (g + kp * e - kd * v + ki * integ)
        z_b = thrust / np.linalg.norm(thrust)
        y_b = np.cross(z_b, [1.0, 0.0, 0.0])
        y_b /= np.linalg.norm(y_b)
        quat = Rotation.from_matrix(np.column_stack([np.cross(y_b, z_b), y_b, z_b])).as_quat()
        a = (thrust + f_world) / mass - g
        v = v + a * dt
        p = p + v * dt
    drag.close()


def test_closed_loop_smoke_passes(tmp_path=None):
    log = pathlib.Path(tmp_path or tempfile.mkdtemp()) / "sim_log.csv"
    fly_point_mass(log)
    checks = run_checks(log)
    failed = [c for c in checks if not c["pass"]]
    assert not failed, failed


def test_checker_fails_without_wind(tmp_path=None):
    """A run where the wind never reaches the vehicle (e.g. stock LinearDrag) must fail the checker."""
    log = pathlib.Path(tmp_path or tempfile.mkdtemp()) / "sim_log.csv"
    fly_point_mass(log)
    import pandas as pd
    df = pd.read_csv(log)
    df[["f_e", "f_n", "f_u"]] = 0.0                     # pretend no force was applied
    df.to_csv(log, index=False)
    assert not all(c["pass"] for c in run_checks(log))


def test_checker_reports_empty_log(tmp_path=None):
    """Smoke run 11288256: the sim log was empty (no take-off); the checker must FAIL, not raise."""
    log = pathlib.Path(tmp_path or tempfile.mkdtemp()) / "sim_log.csv"
    log.write_text("")
    checks = run_checks(log)
    assert len(checks) == 1 and not checks[0]["pass"]


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok ", name)
