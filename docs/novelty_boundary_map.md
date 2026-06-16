# Novelty Boundary Map

## Not Novel

- Partial observability.
- Active perception.
- Occlusion-robust perception.
- Object memory.
- Tracking hidden state.
- Task-and-motion planning.

## Plausible Contribution

The contribution is the action-facing planning interface: a disappearing goal is represented as a proxy with identity, geometry, affordance, uncertainty, re-binding rules, and re-acquisition policy. The planner consumes that proxy rather than a raw visible state or an unchecked last-seen location.

## Final Boundary

The full-scale result supports identity-calibrated proxy evaluation across task family, horizon, occlusion, ambiguity, observability, cost, and policy axes. V2 remains a negative control proving that uncalibrated proxy persistence is not enough.
