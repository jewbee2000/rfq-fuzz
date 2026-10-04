# T02: one exported plate challenge

Requirements: R03/R04/R08, bounded M0 subset. Full part-family and operator coverage remain later work. This is one synthetic ancestry, three presentations; no physical part has been manufactured.

Final artifacts are `bundle/public/{pk-7a1c,pk-b8e2,pk-4d90}/{part.step,drawing.pdf,drawing.png,packet.json}`. Private generator intent is `bundle/private/mutations.json`; it is not validator ground truth. The public cases contain every governing stage/authority premise and no expected answer. Model bytes are copied from one export, removing role-correlated export timestamps. Export audits cover allowlisted files, packets, PDF search text/metadata, STEP text and PNG metadata. Same-machine blinding is procedural.

The independent validator is authored in a separate checkout and imports direct OCCT readers, never generator code. Its analytic dimensions come from the frozen finite contract rather than generator metadata. Initial direct measurements: one valid solid, bbox **[-40,-25,-4,40,25,4] mm**, four full cylindrical Z walls at XY (+/-25,+/-15), radius **3 mm**, depth **8 mm**. Volume **31095.22131576612 mm3** versus **80*50*8 - 4*pi*3^2*8**, error **-1.82e-11 mm3**. OCCT remains a disclosed common kernel.

Coordinator visually inspected all final actual Poppler PNGs (200 DPI, 2339 x 1654) and retained hash-bound observations in `visual-attestation.json`. Callouts visibly read `4x diameter 6.8 +/-0.05 THRU`, `4x diameter 6 +/-0.05 THRU`, and `4x diameter 6.8 +/-0.05 THRU`. All four bores, envelope labels 80/50/8, units, material, identity, stage notes and group association are readable and unclipped. The stage alternative explicitly reams H1 after the supplied intermediate model stage. All views explicitly represent the supplied model stage; this matters because the numeric callout can govern a later stage.

Draftwright search text includes correctly decoded Unicode multiplication/diameter/plus-minus symbols; initial shell replacement glyphs were console encoding. Search text is invisible and insufficient to establish visibility. The validator supplements it with independent PDFium rendering, raster-region ink and shipped-PNG agreement, retained crops, and visual attestation. This is curated proof for this layout, not general OCR or arbitrary engineering drawing interpretation.

Retained first attempt: `attempt-01/`, excluded because its view-stage premise was not explicit enough for the legitimate alternative. Three initial presentations were quarantined as an authoring group. Adding the view-stage note caused Draftwright's completeness policy to select scale 1:2; final visible labels remained readable. Its missing-location lint is outside this finite CAD-authoritative drawing obligation: nominal positions are in the supplied model and the public group mapping. Diameter-declaration lint on the 6.8 cases is expected from the intentionally different annotation (or staged target) and is not used as an oracle. No incidental dimension/identity/material change is accepted.

Actual acceptance commands/results and integration commit are appended after the independent validator runs on the combined checkout. The source/fixture content is retained under Git with `.gitattributes` prohibiting evidence newline transformations.

## Combined-checkout acceptance (performed)

```powershell
./.venv/Scripts/python.exe tools/m0.py validate
./.venv/Scripts/python.exe -m pytest tests/m0/test_validation.py tests/m0/test_public.py --basetemp evidence/M0/negative-tests -q
```

Actual results: **15 passed in 10.63s**, no warnings. Validator: all **3/3 valid**, **6/6 suite invariants true**, **0 fixture failures**. Diameter/stage observations yield exactly one contradiction and two supported-clear H1 obligations. All three PDFium-versus-Poppler comparisons have unmatched-ink ratio **0.0**, within the declared heuristic limit **0.015**. Coordinator additionally inspected all three independent PDFium callout crops, confirming count/diameter/plus-minus/tolerance/THRU text is readable.

Retained evidence: `T02-tests.txt`, `T02-validation.txt`, `validation/oracle.json`, each `validation/*/inspection.json`, rendered page/crops, and `negative-tests/` containing 15 inspection records plus mutated inputs and test witnesses. Eleven independent-validator tests include hidden-callout/stage-note whiteouts, actual STEP metre units, missing third/fourth bore, truncated STEP, stale/no attestation, unsupported schema, hashes and white PNG; four public-interface tests challenge missing premises, sidecars and traversal. These are deliberate fixture corruption controls, excluded from the frozen scored suite. The three first-attempt presentations remain separately quarantined; the final suite's 0/3 invalid rate must not hide that authoring history.

Generator and validator are separate modules/owners. Independent worker source commit `289a9a19bc03bedc313387b81d952a88461ff55e` integrated sequentially as `9857b23`. Task closure commit is in tasks.json. Assessment: finite exported-artifact oracle works for this challenge; proceed to T03 to test whether an independent reviewer can use it. No second part family or corpus expansion.
