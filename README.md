# Paper 56: Manipulation With Disappearing Goals

Decision: workshop-only.

The thesis is that when a physical goal referent disappears from view, a manipulation planner should optimize over a persistent goal proxy rather than only the currently visible goal state or a drifting last-seen belief.

V1 evidence:

- 1,264-row literature sweep.
- 5,400 deterministic disappearing-goal diagnostic episodes.
- Long-occlusion success: persistent proxy 1.000 versus last-seen belief 0.872.
- Long-occlusion identity swaps: persistent proxy 0.000 versus last-seen belief 0.575.

V2 hardening adds a re-binding ambiguity stress:

- Close distractor: loose proxy success 0.094, swap rate 0.906.
- Close distractor: proxy with re-acquisition success 0.928, swap rate 0.072.
- Severe ambiguity: loose proxy success 0.020, swap rate 0.980.
- Severe ambiguity: proxy with re-acquisition success 0.821, swap rate 0.179.

The supported claim is conditional: persistent proxies help only when identity re-binding and active re-acquisition are explicit and audited.

## Reproduction

```powershell
python scripts/v2_rebinding_ambiguity_stress.py
powershell -ExecutionPolicy Bypass -File scripts/build_pdf.ps1
```

The canonical built PDF is `C:/Users/wangz/Downloads/56.pdf`.

Local generated PDFs are not tracked. The build script copies the generated PDF to the canonical Downloads path and removes `paper/main.pdf`.
