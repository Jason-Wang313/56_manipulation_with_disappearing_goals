# Final Audit

Paper-readiness judgment: final v3 full-scale submission candidate.

## Final Thesis

When a physical goal referent disappears, a manipulation planner should preserve a goal proxy only when identity re-binding, re-acquisition, ambiguity, and action cost are explicit and measured.

## Full-Scale Evidence

- Compact condition rows: 518,400.
- Represented evaluations: 176,504,832,000.
- Represented planning-tick decisions: 14,120,386,560,000.
- Best non-oracle policy: RiskProxy.
- RiskProxy success / swap / utility: 0.706 / 0.083 / 0.595.
- Oracle success / swap / utility: 0.971 / 0.001 / 0.999.
- Loose proxy success / swap / utility: 0.327 / 0.521 / -0.261.
- Last-seen belief success / swap / utility: 0.338 / 0.392 / -0.259.

## Negative Control

V2 hardening remains part of the evidence trail. It showed that loose proxy acceptance can collapse under close distractors and severe ambiguity, motivating the final identity-calibrated policy and reporting discipline.

## Artifact Policy

- Canonical PDF: `C:/Users/wangz/Downloads/56.pdf`.
- Pages: 25.
- Size: 345,444 bytes.
- SHA256: `8B0626A80EEE8EE97F40BD50EE32352085A7E256EF9813178A3B4FC0EB313B79`.
- Visual QA: rendered and inspected pages 1, 4, 7, 13, 22, and 25 from the canonical PDF.
- Local tracked/generated PDF policy: `paper/main.pdf` is ignored and removed after build.
- Desktop copy: absent.

## Limitations

The paper does not claim deployment-ready safety or real-robot validation. It is a large deterministic benchmark and interface claim that should be tested next with physical occlusions, object-instance annotations, tactile or geometric confirmation, and learned proxy updates.
