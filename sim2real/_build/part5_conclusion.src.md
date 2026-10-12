## 5. Conclusion

The sim-to-real literature has moved from treating simulation as a substitute for reality to treating it as an instrument. A simulator is useful when three things are true [@choi2021; @aljalbout2026]:
- it has been calibrated against the real system;
- its remaining uncertainty is randomized;
- its predictions are checked against measurements.

DroneRanger's architecture already has the hardest piece: one interface that runs unchanged in simulation and in flight [@ling2026]. What it lacks is the instrumentation that would let it *show* transfer:
- a calibrated X500 model;
- sensor models with realistic failure modes;
- a timing model of the Jetson–Pixhawk link;
- paired sim and real measurements against independent truth.

These are hardware-group deliverables this semester. They are also the foundation that the RL group's policy and, later, learned wildlife deterrence will need [@zha2026lit]. The practical rule for the semester: no mission flies without passing SITL first, and no SITL result is reported without its real-world counterpart.

### Limitations of this review

- **Not systematic.** This is a narrative review: the search was wide but not exhaustive.
- **Preprints.** Several of the most relevant 2025–2026 works are preprints; they are labelled as such.
- **Vendor claims.** Claims about simulators such as Genesis and Newton come from their developers and have not been independently validated.
- **Estimated project figures.** DroneRanger numbers taken from project notes (all-up weight, hover throttle, wind statistics) are estimates until measured on the vehicle.
