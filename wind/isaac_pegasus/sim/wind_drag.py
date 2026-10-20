"""Air-relative drag for Pegasus Simulator v5.1.0: the hook that lets wind act on the vehicle.

Pegasus' stock LinearDrag computes F_body = -D * v_body from the ground-relative velocity, so wind has no effect.
WindDrag uses the velocity relative to the air instead:

    v_air_body = v_body - R^T w_world        F_body = -D * v_air_body

where R rotates the FLU body frame into the ENU world frame (Pegasus State.attitude, [qx, qy, qz, qw]) and w_world
comes from a WindPublisher. With zero wind it is exactly LinearDrag, with the same default coefficients
(MultirotorConfig: [0.50, 0.30, 0.0] N per m/s). Use it by setting `MultirotorConfig.drag = WindDrag(...)`.

It also logs the state, the wind and the applied force (the ground truth the smoke-test checker reads).
"""
import csv

import numpy as np
from scipy.spatial.transform import Rotation

try:  # inside Isaac Sim with Pegasus installed
    from pegasus.simulator.logic.dynamics.drag import Drag
except ImportError:  # unit tests on a plain Python install
    class Drag:
        def __init__(self):
            pass

LOG_FIELDS = ["t", "t_rel", "pos_e", "pos_n", "pos_u", "vel_e", "vel_n", "vel_u", "qx", "qy", "qz", "qw",
              "wind_e", "wind_n", "wind_u", "f_body_x", "f_body_y", "f_body_z", "f_e", "f_n", "f_u"]


class WindDrag(Drag):
    def __init__(self, publisher, drag_coefficients=(0.50, 0.30, 0.0), log_path=None, log_every=5):
        super().__init__()
        self._publisher = publisher
        self._D = np.diag(drag_coefficients)
        self._drag_force = np.zeros(3)
        self.wind = np.zeros(3)
        self.t = 0.0
        self.last_altitude = 0.0
        self._step = 0
        self._log_every = log_every
        self._log_file = open(log_path, "w", newline="") if log_path else None
        self._log = csv.writer(self._log_file) if self._log_file else None
        if self._log:
            self._log.writerow(LOG_FIELDS)

    @property
    def drag(self):
        return self._drag_force

    @property
    def publisher(self):
        return self._publisher

    def update(self, state, dt):
        self.t += dt                                    # Pegasus calls this once per physics step
        self.last_altitude = float(state.position[2])
        self.wind = self._publisher.update(self.t, self.last_altitude)
        R = Rotation.from_quat(state.attitude)          # FLU body -> ENU world; scipy also uses [x, y, z, w]
        v_air_body = np.asarray(state.linear_body_velocity, dtype=float) - R.inv().apply(self.wind)
        self._drag_force = -self._D @ v_air_body
        if self._log and self._step % self._log_every == 0:
            t_rel = self._publisher.t_rel
            self._log.writerow([f"{self.t:.4f}", "" if t_rel is None else f"{t_rel:.4f}",
                                *np.round(state.position, 4), *np.round(state.linear_velocity, 4),
                                *np.round(state.attitude, 6), *np.round(self.wind, 4),
                                *np.round(self._drag_force, 4), *np.round(R.apply(self._drag_force), 4)])
        self._step += 1
        return self._drag_force

    def close(self):
        if self._log_file:
            self._log_file.close()
            self._log_file = None
