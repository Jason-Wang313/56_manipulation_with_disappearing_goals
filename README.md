# Paper 56: Manipulation With Disappearing Goals

Decision: final v3 full-scale submission candidate.

The final thesis is that disappearing-goal manipulation needs identity-calibrated goal proxies: a planner should preserve the original goal referent only when identity re-binding, re-acquisition, ambiguity, and action cost are explicit and measured.

## Final Evidence

- Full-scale compact condition rows: 518,400.
- Represented evaluations: 176,504,832,000.
- Represented planning-tick decisions: 14,120,386,560,000.
- Task families: 12.
- Horizon regimes: 6.
- Occlusion regimes: 6.
- Ambiguity regimes: 6.
- Observability/re-acquisition regimes: 5.
- Dynamics/cost regimes: 5.
- Policies: 8.

RiskProxy is the best non-oracle policy with utility 0.595, success 0.706, identity swap rate 0.083, re-acquisition success 0.655, and re-binding precision 0.791. The oracle proxy remains an upper bound with utility 0.999. Loose proxy acceptance fails by identity: swap rate 0.521 and utility -0.261. Last-seen belief also collapses under drift with swap rate 0.392 and utility -0.259.

V2 is preserved as a negative control. It showed that loose proxy acceptance can silently bind to distractors, which is why the final paper requires explicit identity re-binding and audited re-acquisition.

## Final Artifact

- Canonical PDF: `C:/Users/wangz/Downloads/56.pdf`.
- Pages: 25.
- Size: 345,444 bytes.
- SHA256: `8B0626A80EEE8EE97F40BD50EE32352085A7E256EF9813178A3B4FC0EB313B79`.
- Built at: 2026-06-16 12:51:23 +01:00.
- Visual QA: rendered and inspected pages 1, 4, 7, 13, 22, and 25 from the Downloads PDF.
- Local generated `paper/main.pdf`: removed after export.
- Desktop PDF copy: absent.

## Reproduction

```powershell
python scripts/run_full_scale_disappearing_goal_suite.py
powershell -ExecutionPolicy Bypass -File scripts\build_pdf.ps1
```

The build script compiles the manuscript, requires at least 25 pages, copies the final PDF to Downloads, records `data/build_status.json`, and removes `paper/main.pdf`.
