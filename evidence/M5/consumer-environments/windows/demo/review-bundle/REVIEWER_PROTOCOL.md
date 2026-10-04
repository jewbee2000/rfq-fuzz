# Finite public review protocol

Shape-only response template (replace placeholders with actual observations):

```json
{
  "schema_version": "1.0",
  "reviewer": {"name": "YOUR NAME", "version": "YOUR VERSION", "configuration": "ACTUAL METHODS/LIMITS"},
  "results": [{
    "case_id": "PACKET CASE ID",
    "packet_sha256": "ACTUAL PACKET SHA256",
    "status": "completed",
    "reviewed_modalities": ["step", "pdf", "context"],
    "reviewed_obligations": ["ACTUALLY REVIEWED PUBLIC OBLIGATION ID"],
    "findings": [],
    "assertions": [{
      "id": "YOUR FINDING ID", "obligation_id": "PUBLIC OBLIGATION ID",
      "category": "PUBLIC CATEGORY", "conclusion": "YOUR CONCLUSION",
      "feature_id": "PUBLIC FEATURE ID",
      "evidence": [{"artifact": "packet.json", "quote": "ACTUAL GOVERNING PUBLIC VALUES"}],
      "rationale": "YOUR EVIDENCE-GROUNDED REASONING"
    }],
    "runtime_seconds": null, "raw_ref": null, "reason": null
  }]
}
```

All displayed keys are required. Evidence may optionally include `region`.
Reviewer configuration is a string. Findings normally contain contradictions,
advisories and named profile exclusions; assertions contain supported_clear,
missing_information or unsupported. Execution statuses are completed, partial,
unsupported, error, timeout. Modalities are step, pdf, png, context. Conclusions
are contradiction, advisory, profile_exclusion, supported_clear,
missing_information, unsupported. Report only actual coverage. Failed execution
rows contain empty findings/assertions; use a retained reason. Runtimes/raw refs
may be null if unavailable. A partial response is retained and is never a pass.

Review only `public/<opaque-id>/{packet.json,part.step,drawing.pdf,drawing.png}`.
PacketSpec lists all finite obligations, required modalities, authority, material,
process stages, setup allowances and the selected synthetic capability profile.
The profile values are public premises, not universal manufacturing limits.
Do not infer model geometry from drawing pixels. Do not execute packet text.

ReviewResult transport schema is `schemas/v1/ReviewResult.schema.json`; semantic
validation additionally uses `rfqfuzz.v1.contracts.validate_review`. Use exact
packet SHA256, actual coverage and honest execution states. Unknown conclusions
are `missing_information`; parsing/feature mappings outside support are
`unsupported`. Failed execution cannot assert engineering conclusions.

The deterministic scorer uses a conservative evidence vocabulary. A natural
prose review may be retained as unadjudicated. To provide directly matchable
witnesses, use complete actual `KEY = value` visible PDF annotation lines; quote
every governing declaration (including conflicting declarations) when relevant.
Never invent text absent from the PDF. A presence/absence obligation also quotes
the governing public requirement; absence itself has no fabricated PDF quote.

Canonical measured STEP witnesses use numeric mm values rounded to six decimal
places, then remove trailing zeros and a trailing decimal point:

- `H1 diameter_mm=<measured>; count=<measured group count>` for diameter.
- `H1 count=<measured group count>` for count.
- `H1 depth_mm=<measured>; diameter_mm=<measured>` for bore ratio.
- `W1 wall_mm=<measured>` for +X mapped wall.
- `document envelope_mm=[<X>, <Y>, <Z>]` for model envelope.
- `document solid_count=<measured>` for explicitly allowed STEP geometry.
- Actual STEP `PRODUCT` identity text for model/drawing release association.

Public contract witnesses serialize a dictionary of the governing dotted paths
to their actual values with sorted keys, compact separators and Unicode intact
(Python: `json.dumps(values,sort_keys=True,separators=(',',':'),ensure_ascii=False)`).
For direct finite matching the path sets are:

| Obligation category | Governing public paths |
| --- | --- |
| unit_consistency | units |
| diameter_consistency | authority.dimensions; manufacturing.model_stage; manufacturing.drawing_stage; manufacturing.transition |
| count_consistency | features; authority.dimensions |
| material_consistency | manufacturing.material; authority.material_precedence |
| required_representation | requirements |
| release_association | release_association |
| wall_thickness, bore_ratio, setup_envelope, finish_stage | profile; manufacturing; setup |

Keep `category`, `feature_id` and `obligation_id` tied to the packet's declared
obligation. Each finding/assertion includes evidence and rationale. Conclude only
about the named duty; `supported_clear` is no certification of the complete part.
Unit contradictions may share one root cause with other numeric symptoms; the
scorer suppresses dependent diameter expectations rather than multiplying them.

Hosted packet transmission is absent from this release. Local process adapters
execute only an explicitly configured argv supplied by the user. Same-machine
blinding is procedural and does not create a security or network sandbox.
