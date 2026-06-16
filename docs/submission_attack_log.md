# Submission Attack Log

## Attack: clean proxy re-binding is assumed

Result: sustained for the old draft. V2 showed why this is dangerous. V3 answers by separating identity re-binding, re-acquisition, ambiguity, and cost in the policy contract and metrics.

Decision impact: final claim is identity-calibrated proxy use, not memory alone.

## Attack: severe ambiguity remains hard

Result: sustained. The full-scale suite includes six ambiguity regimes and reports identity swaps directly. RiskProxy keeps swaps to 0.083 overall; loose proxy acceptance reaches 0.521 swaps overall.

Decision impact: ambiguity is a central stress axis, not a footnote.

## Attack: active search can dominate by gathering more evidence

Result: partly sustained. Active-search proxy has re-acquisition success 0.704 but utility 0.453 because search, delay, and waste costs are high. RiskProxy reaches utility 0.595.

Decision impact: report cost-aware utility and raw re-acquisition metrics together.

## Attack: synthetic benchmark cannot prove physical safety

Result: sustained. The final paper states that real robot logs, object-instance annotations, tactile/geometric confirmation, and learned proxy updates are future work.
