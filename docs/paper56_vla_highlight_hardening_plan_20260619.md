# Paper 56 VLA Highlight Hardening Plan

Objective: make Paper 56's boxed PDF highlights match the VLA-v4 role-model PDF while preserving the final full-scale disappearing-goal manipulation benchmark and bounded identity-calibrated proxy claim.

## Role-Model Target

- Citation links use green rectangular borders with no fill.
- Internal references use red rectangular borders with no fill.
- URL links use the same green border family as citations.
- Border width is `pdfborder={0 0 1}`, matching the VLA-v4 annotation metadata.
- Boxes stay tight to linked text and must not affect typography, spacing, figure captions, tables, or scientific content.

## Current Paper 56 Mismatch

- `Downloads/56.pdf` is a 25-page final v3 full-scale submission candidate.
- Link annotations appear on pages 3, 4, and 5.
- The current PDF has 12 red internal-reference links and no visible citation/URL link annotations in the metadata.
- All 12 links have invisible border width `0`, so the page appearance does not match the VLA-v4 role model.
- `paper/main.tex` uses `\hypersetup{hidelinks}`, which suppresses the visible link boxes.

## Execution Plan

1. Keep RAM use low by rendering only affected pages before and after the edit: pages 3, 4, and 5.
2. Replace `\hypersetup{hidelinks}` in `paper/main.tex` with explicit VLA-style link annotation settings:
   - `colorlinks=false`
   - `pdfborder={0 0 1}`
   - `citebordercolor={0 1 0}`
   - `linkbordercolor={1 0 0}`
   - `urlbordercolor={0 1 0}`
3. Rebuild with `scripts\build_pdf.ps1`, which exports the canonical final PDF to `C:\Users\wangz\Downloads\56.pdf`, writes build metadata, and removes local `paper/main.pdf`.
4. Validate the rebuilt PDF annotation metadata with `pypdf`; expected result is 12 red internal-reference boxes, all with border `0 0 1`.
5. Render pages 3, 4, and 5 again and visually compare with the VLA-v4 role model.
6. Update README/status/build metadata and SHA text if the rebuild changes the canonical PDF.
7. Remove Paper 56 temporary render folders, then commit and push the clean repo.

## Non-Goals

- Do not rerun the full-scale benchmark.
- Do not change tables, figures, result claims, page count target, or bounded identity-safety language.
- Do not pad the paper or alter manuscript content beyond link-box styling and stale metadata.
