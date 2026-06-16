# Claims

## Supported

- Disappearing-goal manipulation should be evaluated as goal-identity preservation, not only visible-state tracking.
- A persistent goal proxy is useful only when identity re-binding, re-acquisition, ambiguity, and cost are explicit and measured.
- RiskProxy is the best non-oracle policy in the full-scale deterministic benchmark: utility 0.595, success 0.706, identity swap rate 0.083.
- Loose proxy acceptance is a strong negative control: utility -0.261 and identity swap rate 0.521.
- Last-seen belief is also unsafe under drift: utility -0.259 and identity swap rate 0.392.
- Identity swaps, re-binding precision, re-acquisition success, search cost, delay, waste, and safety exposure should be reported separately.

## Not Supported

- Deployment-ready robot safety.
- Universal partial-observability solving.
- A claim that memory alone solves disappearing goals.
- Silent nearest-neighbor proxy acceptance under distractors.
- Replacement of real robot validation, tactile confirmation, or human-labeled ambiguity audits.

## Boundary

The paper supports a benchmark and planning-interface discipline for identity-calibrated goal proxies. V2 remains a negative control showing that uncalibrated proxy re-binding can bind to distractors with high confidence.
