"""Wind publisher for the Isaac Sim + Pegasus + PX4 SITL pipeline.

The publisher owns a wind profile and a clock. Every physics step the drag model asks it for the wind at the
current simulation time and gets back the velocity of the air in the ENU world frame (the Isaac Sim / Pegasus
world frame), in m/s. Keying the wind to simulation time, not wall time, keeps a replay deterministic: PX4 runs
in lockstep with the physics, so the same profile always meets the vehicle at the same point of its flight.

Profiles (choose one with `from_spec`):
  none                     calm air
  constant:E,N[,U]         constant wind, m/s
  smoke                    the dummy schedule used by the smoke test (SMOKE_SCHEDULE below)
  csv:<path>               a series written by wind/tools/make_wind_profile.py (columns t_s, wind_e, wind_n, wind_u)

With `trigger_alt` set, the profile clock starts only when the vehicle first climbs above that height, so the
schedule lines up with the hover regardless of how long arming and take-off took.
"""
import csv
import math

import numpy as np

# (start s, end s, kind, params). Times are relative to the trigger. "sine" = mean + amplitude * sin(2 pi f t).
SMOKE_SCHEDULE = [
    (0.0, 15.0, "calm", {}),                                            # settle in hover
    (15.0, 35.0, "constant", {"enu": (3.0, 0.0, 0.0)}),                 # 3 m/s step, blowing toward +East
    (35.0, 50.0, "calm", {}),                                           # recover
    (50.0, 80.0, "sine", {"mean": (0.0, 2.0, 0.0), "amp": (0.0, 1.5, 0.0), "freq_hz": 0.2}),  # gusty northward
    (80.0, 90.0, "calm", {}),
]


class Profile:
    """Base class: wind_enu(t) for t >= 0 seconds since the profile started."""
    duration = math.inf

    def wind_enu(self, t):
        return np.zeros(3)


class Constant(Profile):
    def __init__(self, enu):
        self.enu = np.asarray(enu, dtype=float)

    def wind_enu(self, t):
        return self.enu.copy()


class Schedule(Profile):
    """Piecewise segments of calm, constant or sinusoidal wind."""

    def __init__(self, segments):
        self.segments = segments
        self.duration = max(end for _, end, _, _ in segments)

    def wind_enu(self, t):
        for start, end, kind, p in self.segments:
            if start <= t < end:
                if kind == "calm":
                    return np.zeros(3)
                if kind == "constant":
                    return np.asarray(p["enu"], dtype=float)
                if kind == "sine":
                    phase = math.sin(2 * math.pi * p["freq_hz"] * (t - start))
                    return np.asarray(p["mean"], dtype=float) + np.asarray(p["amp"], dtype=float) * phase
                raise ValueError(f"unknown segment kind {kind!r}")
        return np.zeros(3)


class CsvProfile(Profile):
    """Linear interpolation of a make_wind_profile.py CSV; calm after its last sample."""

    def __init__(self, path):
        with open(path, newline="") as f:
            rows = list(csv.DictReader(f))
        self.t = np.array([float(r["t_s"]) for r in rows])
        self.w = np.array([[float(r["wind_e"]), float(r["wind_n"]), float(r["wind_u"])] for r in rows])
        self.duration = float(self.t[-1])

    def wind_enu(self, t):
        if t > self.duration:
            return np.zeros(3)
        return np.array([np.interp(t, self.t, self.w[:, i]) for i in range(3)])


def from_spec(spec):
    if spec == "none":
        return Profile()
    if spec == "smoke":
        return Schedule(SMOKE_SCHEDULE)
    if spec.startswith("constant:"):
        vals = [float(x) for x in spec.split(":", 1)[1].split(",")]
        return Constant(vals + [0.0] * (3 - len(vals)))
    if spec.startswith("csv:"):
        return CsvProfile(spec.split(":", 1)[1])
    raise ValueError(f"unknown wind spec {spec!r} (none | smoke | constant:E,N[,U] | csv:<path>)")


class WindPublisher:
    """Publishes the profile's wind at simulation time t (seconds since physics start)."""

    def __init__(self, profile, trigger_alt=None):
        self.profile = profile
        self.trigger_alt = trigger_alt
        self.t0 = 0.0 if trigger_alt is None else None
        self.t_rel = None

    def update(self, t_sim, altitude_m):
        if self.t0 is None and altitude_m >= self.trigger_alt:
            self.t0 = t_sim
        if self.t0 is None:
            self.t_rel = None
            return np.zeros(3)
        self.t_rel = t_sim - self.t0
        return self.profile.wind_enu(self.t_rel)

    @property
    def started(self):
        return self.t0 is not None

    @property
    def done(self):
        return self.t_rel is not None and self.t_rel >= self.profile.duration
