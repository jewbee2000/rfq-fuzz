# Standalone RFQ review observations

This record is the raw narrative of the independent Codex review of the supplied public packages. The only decision obligation is `bore_group_consistency` on H1. No manufacturing certification, physical-part assertion, or process feasibility determination is made.

## Provenance and method

The reviewer was a Codex agent described generically as based on GPT-6. The exact served model version was unavailable and was not guessed. The reviewer read this standalone folder's `PROMPT.txt`, `review-result.schema.json`, the three `public/*/packet.json` files, and their actual `drawing.pdf`, `drawing.png`, and `part.step` files. The reviewer did not read repository implementation, a validator, reference checker, expected answers, answer records, other chats, or outside sources. No packet text was executed. No public inputs were edited, no files were transmitted, no dependencies installed, no paid API called, and no commit made by the reviewer. Runtime was not measured and is null in the result.

The permitted interpreter was `C:/Users/Walt/Documents/Codex/2026-10-03/g/outputs/projects/rfq-fuzz/.venv/Scripts/python.exe`. The script records Python 3.12.2, cadquery-ocp 7.8.1.1.post1, build123d 0.10.0, pypdf 6.9.1, pypdfium2 5.14.0 and Pillow 12.3.0. The script imports and uses OCP, pypdf, pypdfium2 and Pillow; the installed build123d distribution version is recorded without using its model construction API.

I wrote `measure.py` independently within review-output. It reloads each actual STEP separately with `STEPControl_Reader`, checks kernel shape validity and topology, reads analytical cylinder radii/axes and circular face boundaries, and classifies interior points. It computes actual SHA-256 hashes of each packet and artifact and compares artifact hashes with the public packet declarations. It extracts text from actual PDFs with pypdf and renders every PDF page with PDFium at scale 2. I visually inspected all three supplied PNGs at their original 2339×1654 resolution and all three independently rendered PDF pages at 1684×1191. Grouped callouts, note rows, views and title blocks were readable; required bore/stage evidence matched between PDF renders and supplied PNGs. I did not infer any engineering dimensions from image scale.

The first point-classification probe assumed a Z=0..8 plate and consequently sampled the top boundary and exterior. Its raw stdout is retained in `measurement-run.txt`. The STEP bounds actually showed Z=-4..4, so I corrected the script to derive interior probe heights from the measured bounds and reran it. The final `measurements.json` and `measurement-run-corrected.txt` supersede that initial probe. Analytical cylinder/radius measurements were unchanged. The corrected probes are Z=-3.9, 0 and 3.9; bore axes are outside the material, and plate point (0,0,0) is inside.

## Shared measured geometry and association

Each actual STEP reload succeeded, transferred one root, and produced one kernel-valid solid with ten faces (six planes, four cylindrical walls). Its nominal plate limits are X=-40..40, Y=-25..25, Z=-4..4 mm, with the reported bounding box expanded by approximately 1e-7 mm kernel tolerance. Its volume is 31095.22131576612 mm³.

All four analytical cylindrical walls have radius 3.0 mm and diameter 6.0 mm. Their axes are parallel to +Z at XY centers (-25,-15), (-25,15), (25,-15), (25,15), matching the public H1 association. Each wall spans the full 2π angular interval and has radius-3 circular boundaries at Z=-4 and Z=4, which are also boundaries of the plate's lower and upper planar faces. These topological and analytical measurements establish four through bores over the plate's 8 mm thickness. Corrected bore-axis probes classify OUT at three heights inside the plate thickness while a plate-center probe classifies IN. I relied on these actual reload measurements, not the declared feature centers alone or an in-memory generator model.

The three supplied STEP files have the same actual SHA-256, `b439aa4be158cbb10535ec81482a99872678d912d9f3b93c76eba389a99d965c`, but I read and measured each file individually. All declared public artifact hashes matched the actual bytes. The public context permits the MP-001 model A / drawing A association, mm units, and H1 group of four through Z bores. Actual rendered title blocks say MP-001, A, mm, 6061-T6, and SEE CALLOUT. The plate's visible 80, 50 and 8 dimensions agree with the STEP extents, but the review decision concerns H1 only. No location tolerance or extra drawing dimension was invented.

## pk-4d90

Actual packet SHA-256: `e92576eab2c7012132c85507a8f373de395a7ec6544d7b863bb795d1f1317812`.

The supplied PNG and actual PDF render show `4× Ø6.8 ±0.05 THRU` pointing to a member of the four-bore plan view. Note 2 says `H1 = ALL FOUR Z THROUGH BORES`; note 3 says `MODEL STAGE: INTERMEDIATE`; note 4 says `DRAWING STAGE: FINISHED`; note 6 says `VIEWS SHOW SUPPLIED MODEL AT MODEL STAGE`; note 7 says `H1: REAM AFTER MODEL STAGE TO DRAWING SIZE`. PDF extracted text contains the same wording and a lower-case ø glyph corresponding to the visible diameter symbol.

The packet independently states model stage intermediate, drawing stage finished, transition operation ream for H1 from intermediate to finished targeting the drawing bore callout, and finish none. Its rule says `same-stage drawing intervals must contain STEP nominal; explicit later-stage operation governs its target stage`. This later-stage H1 operation applies to the grouped target interval [6.75,6.85] mm, while the actual STEP measures all four intermediate bores as Ø6 mm.

Decision: completed; `supported_clear` for H1 `bore_group_consistency`. A smaller intermediate bore and an explicitly later enlarged target are consistent with this stage contract. Required engineering context is visible and agrees with the packet. I do not assess whether this particular reaming allowance, equipment, tooling or tolerance is practically feasible. CNC advisory remains unsupported. Render evidence is `pk-4d90-pdf-page-1.png`; extracted text is `pk-4d90-pdf-text.txt`; measurement details are the pk-4d90 entry in `measurements.json`.

## pk-7a1c

Actual packet SHA-256: `17fa0bb2e63e161bba519f80953fe87bca4cf5f3e623cf5273f738ad7d77ffc6`.

The supplied PNG and actual PDF render show `4× Ø6.8 ±0.05 THRU`. Note 2 identifies all four H1 Z through bores. Notes 3 and 4 state both model and drawing stages are FINISHED; note 7 says `H1: DRAWING AND MODEL APPLY AT SAME STAGE`. The packet also sets both stages to finished and transition null.

The drawing interval is [6.75,6.85] mm, whereas the independently reloaded actual STEP nominal for every group member is 6.00 mm. Every member is 0.75 mm below the lower bound. The stage notes prevent explaining the mismatch as an intermediate machining stage; finish is none, so no finishing allowance is provided. The model/drawing A/A association is allowed and the units agree, leaving an explicit H1 diameter contradiction under the finite consistency rule.

Decision: completed; one `contradiction` finding for grouped H1 `bore_group_consistency`, covering all four members. This is a package inconsistency; manufacturing feasibility and CNC advisories remain unsupported. Render evidence is `pk-7a1c-pdf-page-1.png`; extracted text is `pk-7a1c-pdf-text.txt`; measurement details are the pk-7a1c entry in `measurements.json`.

## pk-b8e2

Actual packet SHA-256: `74f329f490ae060c8e42a8613242e38b2cc54e5b8618b54c5ae373cc5651aef2`.

The supplied PNG and actual PDF render show `4× Ø6 ±0.05 THRU`. Note 2 identifies all four H1 Z through bores. Notes 3 and 4 state both stages are FINISHED; note 7 says `H1: DRAWING AND MODEL APPLY AT SAME STAGE`. The packet agrees and sets transition null.

The grouped drawing interval [5.95,6.05] mm contains each independently measured actual STEP nominal diameter of 6.00 mm. The four-member quantity, through condition and Z orientation agree. The packet's H1 association matches the four measured bore axes; units, allowed revision pair and stage notes agree.

Decision: completed; `supported_clear` for H1 `bore_group_consistency`. CNC advisory remains unsupported. No actual manufactured part or broad manufacturing competence is established. Render evidence is `pk-b8e2-pdf-page-1.png`; extracted text is `pk-b8e2-pdf-text.txt`; measurement details are the pk-b8e2 entry in `measurements.json`.

## Limits and evidence retained

All required evidence for the named finite obligation was established. No case needed a missing_information conclusion and none timed out or errored. completed means this scoped review was completed, including the contradiction case; it is not a pass or approval status. Through-bore geometry is supported by reopened STEP topology; no physical part was inspected or manufactured. No tests of process feasibility, tool access, workholding, inspection planning or general standards compliance were performed. Clear assertions are restricted to the supplied finite release contract. The isolation is procedural on the same machine, not a security boundary.

Retained artifacts are review.json, this observations.md, independently written measure.py, complete measurements.json, initial and corrected measurement stdout, all three extracted PDF text files, and all three actual PDF page renders. The response-only schema/hash verification script check_response.py ran successfully and saved response-check.json. A separate internal response-quality audit reported no material problems and is retained in response-audit.md; that audit did not redo geometry or image inspection. These response checks do not establish engineering truth.
