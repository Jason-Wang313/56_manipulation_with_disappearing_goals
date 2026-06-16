# Paper56 Full-Scale Execution Plan

## Starting Point

At the start of this full-scale pass, Paper56 is a v2 workshop-level mechanism note. The claim is that manipulation planners should preserve a persistent goal proxy when the physical goal referent disappears from view. V1 showed that persistent proxies beat visible-only and last-seen belief baselines in a 5,400-episode deterministic diagnostic. V2 added the crucial hostile stress: loose proxy acceptance collapses under close distractors and severe ambiguity, while explicit re-acquisition recovers most but not all cases.

The final version must not claim that a persistent proxy alone solves occlusion. The stronger submission-grade claim should be:

> Manipulation with disappearing goals requires identity-preserving goal proxies whose re-binding, re-acquisition, ambiguity, and action-cost tradeoffs are explicit and measured.

This paper should become a full-scale deterministic benchmark and reporting discipline for goal identity under disappearance, not a universal partial-observability theorem or real-robot deployment claim.

## Final Title Direction

Use a title close to:

**Identity-Calibrated Goal Proxies for Manipulation with Disappearing Goals**

The title should signal that the contribution is not merely memory under occlusion. It is calibrated goal identity, re-binding, and active re-acquisition.

## Core Scientific Question

When a manipulation target disappears, which policy best preserves task identity without silently binding to distractors or wasting excessive re-acquisition effort?

The benchmark must separate four failure modes:

- **Visibility failure:** the goal disappears and a visible-only policy stops or drifts.
- **Belief drift:** a last-seen belief keeps acting but accumulates state error.
- **Identity swap:** a proxy binds to a distractor or false observation.
- **Over-search:** a cautious policy spends too much active re-acquisition cost and loses task utility.

## Full-Scale Factor Grid

Use a deterministic RAM-light grid with short factor codes and a streamed row-level CSV.

### Task Families: 12

- Tabletop pick-and-place into an occluded cup.
- Shelf insertion where the slot disappears behind the wrist.
- Drawer or container placement where the interior becomes hidden.
- Human handover with an occluded receiving pose.
- Bimanual assembly where one hand covers the goal feature.
- Tool-use alignment with a hidden fastener or contact point.
- Cable or cloth routing through a briefly hidden aperture.
- Bin picking with target/distractor identity ambiguity.
- Mobile manipulation with navigation-induced view loss.
- Table clearing with language-specified referents.
- Regrasping where the target frame is covered by the object.
- Recovery after a failed grasp with the original target hidden.

### Horizon Regimes: 6

- Short disappearance with immediate reappearance.
- Medium disappearance during approach.
- Long disappearance through the decisive action.
- Delayed execution after observation.
- Receding-horizon replanning under intermittent visibility.
- Mixed long-horizon task with several disappearance intervals.

### Occlusion Regimes: 6

- Self-occlusion by the robot arm.
- Object-carried occlusion by the grasped item.
- Environmental occlusion by shelf, drawer, or bin geometry.
- Human occlusion in handover or shared workspace.
- Container-interior disappearance after approach.
- Full disappearance followed by late reappearance.

### Ambiguity Regimes: 6

- Clear reappearance.
- Close spatial distractor.
- Appearance-similar distractor.
- Crossing trajectories during disappearance.
- Goal moves while hidden.
- Adversarial false observation at reappearance.

### Re-Acquisition And Observability Regimes: 5

- Vision-only passive reappearance.
- Active camera or wrist motion.
- Tactile/geometric confirmation.
- Language or semantic anchor disambiguation.
- Multi-modal re-acquisition with delayed confirmation.

### Dynamics And Cost Regimes: 5

- Static scene with cheap re-acquisition.
- Moving target with moderate re-acquisition cost.
- Moving distractor with high identity ambiguity.
- High action cost where search delays hurt success.
- Human-proximity safety-critical regime.

### Policies: 8

- Visible-only goal controller.
- Last-seen drifting belief.
- Loose proxy acceptance.
- Identity-gated proxy.
- Proxy with explicit re-acquisition.
- Active-search proxy.
- Risk-calibrated identity proxy (proposed method).
- Oracle proxy with true identity and ambiguity labels.

### Expected Compact Rows

The target grid is:

`12 tasks x 6 horizons x 6 occlusions x 6 ambiguities x 5 observability regimes x 5 cost regimes x 8 policies = 518,400 compact rows.`

Each compact row should represent:

- 19 seeds.
- 7 robot/object instances.
- 5 environment layouts.
- 4 disappearance schedules.
- 4 perception/noise calibrations.
- 32 episodes.

That is 340,480 represented evaluations per row. With 80 manipulation-planning ticks per episode, each row represents 27,238,400 tick decisions.

Expected totals:

- Represented evaluations total: 176,504,832,000.
- Represented manipulation-planning tick decisions total: 14,120,386,560,000.

These numbers are represented counts, not a claim that every tick is physically simulated.

## Proposed Method

Name the proposed policy something like `RiskProxy` or `IdentityProxy`. The method should maintain a goal proxy with:

- Goal identity binding.
- Geometry anchor.
- Affordance or task role.
- Uncertainty and staleness.
- Re-binding gate.
- Re-acquisition trigger.
- Action-cost estimate.
- Human-proximity or safety-critical flag.

The policy should compute a risk score:

`identity_risk = ambiguity + false_observation_risk + drift + human_risk + action_irreversibility - diagnosis_quality - semantic_anchor_strength`

and use it to choose whether to continue acting, tighten the gate, search actively, pause for re-acquisition, or escalate/abort.

## Metrics

Report component metrics, not only utility:

- Mission success.
- Final goal error.
- Identity swap rate.
- Proxy loss rate.
- Re-binding precision.
- Re-acquisition success.
- Search effort.
- Action delay.
- Wasted search.
- Safety or collision exposure.
- Goal-progress retention during disappearance.
- Utility.

Utility should reward success, low final error, goal-progress retention, re-binding precision, and bounded identity risk. It should penalize swaps, proxy loss, false re-binding, wasted search, action delay, collision exposure, and over-conservative re-acquisition.

## Baseline And Ablation Requirements

- Visible-only tests dependence on current observation.
- Last-seen belief tests drifting memory without identity gating.
- Loose proxy acceptance preserves the v2 catastrophic negative control.
- Identity-gated proxy tests static identity rejection without active search.
- Proxy with re-acquisition tests the v2 recovery mechanism.
- Active-search proxy tests aggressive information gathering.
- Risk-calibrated identity proxy is the proposed policy.
- Oracle proxy is the upper bound and must remain best overall.

## Expected Result Shape

- Oracle should be best overall.
- Risk-calibrated identity proxy should be best non-oracle by utility.
- Proxy with re-acquisition should be a strong baseline.
- Loose proxy acceptance should look good in easy regimes but collapse under close distractor, appearance-similar distractor, and adversarial false observation.
- Last-seen belief should degrade under long disappearance and moving-target regimes.
- Active search should reduce swaps but pay high search/delay cost in cheap or clear regimes.
- Visible-only should fail under long disappearance even when it avoids swaps.

## Figures And Tables

Generate from summary artifacts:

- Scale table.
- Aggregate policy table.
- Ambiguity stress table.
- Occlusion stress table.
- Horizon stress table.
- Re-acquisition/observability stress table.
- Dynamics/cost stress table.
- Task-family summary table.
- Figure: utility and identity swaps by policy.
- Figure: success versus swap frontier.
- Figure: active re-acquisition cost versus utility.
- Figure: ambiguity-regime collapse of loose proxy.
- Figure: horizon-length degradation of last-seen belief.

## Writing Expansion Plan

The final manuscript must reach at least 25 pages with real content:

- Preserve v2 re-binding ambiguity stress as the negative control.
- Reframe the contribution as identity-calibrated goal proxies, not just persistent memory.
- Add full benchmark design and factor rationale.
- Add policy definitions and risk-score equations.
- Add aggregate, ambiguity, occlusion, horizon, observability, cost, and task result sections.
- Add case studies: shelf insertion, handover, bin target swap, hidden drawer interior, language referent disappearance, and active search over-cost.
- Add appendices: metric semantics, deterministic generator, artifact map, RAM-light execution, reviewer attacks, claim guardrails, real-robot validation protocol, falsification criteria, and final artifact contract.

## RAM-Light Execution Strategy

- Stream compact rows directly to `results/full_scale/condition_metrics.csv`.
- Store short factor codes and labels in `results/full_scale/factor_maps.json`.
- Keep only summary accumulators in memory.
- Generate summary CSVs for policy, task, horizon, occlusion, ambiguity, observability, cost, and policy-by-axis panels.
- Generate LaTeX tables and PDF/PNG figures from summaries.
- Keep the condition CSV under GitHub's 100 MB hard limit by using short codes and bounded decimal precision.

## Final Acceptance Checklist

- Detailed plan exists before experiment/manuscript edits.
- Full-scale runner completes and writes validation JSON.
- Compact row count is exactly 518,400.
- Represented evaluation and tick-decision counts match the design.
- Risk-calibrated identity proxy is best non-oracle by utility.
- Oracle remains best overall.
- Proxy with re-acquisition remains a strong baseline.
- Loose proxy visibly raises identity swaps under ambiguity.
- Last-seen belief visibly degrades under long disappearance.
- Active-search proxy shows the search-cost tradeoff.
- Manuscript is at least 25 pages.
- Final PDF is exported to `C:/Users/wangz/Downloads/56.pdf` only after finalization.
- Local `paper/main.pdf` is removed after build.
- Representative PDF pages are rendered and visually inspected.
- README, status, audit, reproducibility, and readiness docs are updated.
- Git checks pass.
- Commit and push before moving to Paper57.
