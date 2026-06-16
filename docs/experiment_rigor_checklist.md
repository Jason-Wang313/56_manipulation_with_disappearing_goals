# Experiment Rigor Checklist

- Original diagnostic episodes: 5,400.
- V2 ambiguity stress: 9,000 episodes, retained as a negative control.
- Full-scale compact condition rows: 518,400.
- Represented evaluations: 176,504,832,000.
- Represented planning-tick decisions: 14,120,386,560,000.
- Axes: 12 task families, 6 horizons, 6 occlusions, 6 ambiguity regimes, 5 observability regimes, 5 cost regimes, 8 policies.
- Metrics: success, final error, identity swap, proxy loss, re-binding precision, re-acquisition success, search, delay, waste, safety exposure, progress, utility.
- Generated tables and figures: yes, from `results/full_scale/`.
- RAM-light execution: streamed condition CSV and aggregate summaries.
- Real robot data: no.
- Final decision: final v3 full-scale submission candidate with explicit real-robot limitation.
