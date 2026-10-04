# Requirements

Generated from [requirements.json](../requirements.json), the source of truth. Status and acceptance evidence describe the bounded synthetic release; acceptance criteria remain the original contract. See [evidence matrix](REQUIREMENTS_EVIDENCE.md) and [Should deferrals](SHOULD_DEFERRALS.md).

## Must

### R01 — Local review-regression workflow

Provide a local CLI and Python API for generate, validate, export, import, compare and report; separate package-consistency from CNC advisory results.

**Rationale:** The useful product is a repeatable reviewer test, not another manufacturing-approval app.

**Acceptance:** A clean consumer runs the supplied complete workflow offline with imported results and sees both tracks independently.

**Delivery/status:** M5; T13; in_progress.

### R02 — Sufficient public context and private answers

Version PacketSpec, CapabilityProfile, MutationSpec, OracleRecord, ReviewResult and RunManifest. Every premise needed by a reviewer is public; answer keys and defect labels are private.

**Rationale:** Hidden intent makes an unfair benchmark; metadata leakage makes an easy but meaningless one.

**Acceptance:** Schema tests reject missing authority/units where required; an export audit finds no oracle fields or revealing labels; missing critical-callout and revision cases expose their governing contract.

**Delivery/status:** M1; T04; verified.

### R03 — Bounded realistic part families

Support one-solid plate/hole-pattern, blind-bore/counterbore block and open-pocket block families with explicit feature groups and setups.

**Rationale:** Simple analytic geometry supports independent measurement while still exercising hardware-review problems.

**Acceptance:** Each family exports/reimports correctly over documented parameter bounds; unsupported topology fails explicitly; representative drawings receive visual inspection.

**Delivery/status:** M2; T06; verified.

### R04 — Actual STEP, PDF and PNG artifacts

Produce ordinary STEP and visible vector PDF, with PNG rendered from that PDF. Record units, hash, view/feature associations and rendering provenance.

**Rationale:** Reviewers must consume real engineering artifacts, not privileged generator objects.

**Acceptance:** Independent STEP reader confirms relevant geometry; PDF text and raster checks agree on required visible labels; PNG remains readable; hidden/clipped text fails validation.

**Delivery/status:** M2; T06, T08; verified.

### R05 — Six objective fault operators

Implement O01 diameter/model mismatch, O02 scoped count mismatch, O03 units mismatch, O04 incompatible global material declarations, O05 removal of a declared requirement and O06 release-association mismatch.

**Rationale:** These are useful and checkable package errors without pretending to solve full drawing intent or CNC process planning.

**Acceptance:** Each operator has prerequisites, allowed deltas and invariant checks; unsupported/ambiguous applications are rejected; the final visible/exported defect is verified.

**Delivery/status:** M2; T07, T08; verified.

### R06 — Conditional manufacturing track

Implement A01 wall advisory, A02 hole depth/diameter advisory, A03 named setup envelope exclusion and A04 finish/tolerance-stage context; include material-dependent applicability.

**Rationale:** Supplier recommendations and process defaults are conditional. Conflating them with impossibility would create bad engineering advice.

**Acceptance:** Boundary and alternate-profile cases produce the specified conclusion class; unknown finish stage stays unknown unless a public default resolves it; stock/fixture allowances are explicit.

**Delivery/status:** M2; T05, T07, T08; verified.

### R07 — Repairs, valid lookalikes and uncertainty controls

Pair objective defects with repaired twins and legitimate alternatives; include underdetermined cases and sparse CAD-authoritative drawings.

**Rationale:** A useful reviewer catches errors without flagging every omission or pretending incomplete evidence is enough.

**Acceptance:** Always-flag, always-clear and always-abstain baselines each fail the relevant metrics; controls cover correct units, REF values, aliases, precedence and independent document revisions.

**Delivery/status:** M4; T07, T11; verified.

### R08 — Independent oracle and fixture quarantine

Validate re-imported STEP measurements, actual visible drawing content and mutation isolation using code separated from generation; quarantine uncertainty and collateral defects.

**Rationale:** Generator metadata alone proves only that the generator agrees with itself.

**Acceptance:** Analytic checks and final-artifact measurements agree within recorded tolerance; deliberate export corruption is caught; invalid fixtures and their reasons are retained and excluded transparently.

**Delivery/status:** M2; T08; verified.

### R09 — Versioned rule provenance

Store source/date, short paraphrase, applicability, units, threshold, comparison, severity, precedence and limits for each rule. Label synthetic profiles and project-selected values.

**Rationale:** Published guidance varies by supplier; reproducibility requires knowing which policy produced the expected answer.

**Acceptance:** Every scored advisory points to a profile/rule version; unknown material/profile combinations abstain; no unsupported universal manufacturing threshold appears in reports.

**Delivery/status:** M1; T05; verified.

### R10 — Explicit conclusion semantics

Distinguish contradiction, profile_exclusion, advisory, missing_information, supported_clear and unsupported; separate fixture invalidity and execution errors.

**Rationale:** A binary pass/fail label loses the important engineering distinction between contradiction, risk and absent evidence.

**Acceptance:** Contract and scorer tests cover every class; replacing unknown with clear or advisory with impossible causes acceptance failures.

**Delivery/status:** M1; T04, T10; verified.

### R11 — Vendor-neutral review interface

Support ordinary public bundle export, structured-result import and a bounded local-process adapter. Demonstrate one genuine external reviewer as well as the reference path.

**Rationale:** A harness usable only by its own checker is not enough. Offline use should not depend on a paid API.

**Acceptance:** The same bundle reaches two independent review paths. At M0 the external reviewer examines the O01 PDF/PNG drawing, STEP geometry and public manufacturing-stage context; its raw response/provenance is retained. STEP-only integrations are later advisory-track evidence and cannot substitute for this gate.

**Delivery/status:** M3; T03, T09; verified.

### R12 — Coverage and failed-run accounting

Record explicit completion, partial, unsupported, timeout and error states plus reviewed modalities/obligations; preserve raw outputs.

**Rationale:** Silence or a crash must not masquerade as a clean part or inflate accuracy.

**Acceptance:** Missing/malformed results, partial runs, empty findings and explicit clear responses produce distinct reports and denominators; interrupted runs can resume without overwriting history.

**Delivery/status:** M3; T09, T10, T12; verified.

### R13 — Evidence-aware matching and adjudication

Match category/conclusion/location or feature evidence one-to-one; deduplicate root-cause findings; keep unmatched findings unadjudicated until reviewed.

**Rationale:** Vague warnings are not detections, and an unexpected finding may reveal a real fixture defect.

**Acceptance:** A wrong-region warning does not match; duplicates cannot increase recall; unit-root-cause grouping works; answer-key corrections create a new version and invalidate stale comparisons.

**Delivery/status:** M3; T10; verified.

### R14 — Honest per-track metrics

Report operator recall, named-clean-obligation false-alert rate, explicit false-clear rate, abstention, coverage, invalid/error rates and counts; no composite intelligence score.

**Rationale:** The corpus proves only its finite obligations. A high detection rate alone can reward indiscriminate warnings.

**Acceptance:** Known synthetic result sets yield hand-calculated numerators/denominators; unadjudicated findings prevent finalized precision claims; misses and explicit false clears stay distinct.

**Delivery/status:** M3; T10; verified.

### R15 — Actionable version regression

Compare runs on identical suite/oracle/profile versions and show changed findings with artifact evidence; reject incompatible comparisons by default.

**Rationale:** The practical outcome is diagnosing a change in a review tool.

**Acceptance:** A consumer identifies a detected-to-missed case and a new false alert from the report; mismatched oracle/profile hashes are flagged. Deliberately injected reviewer regressions are labeled and kept separate from genuine external observations.

**Delivery/status:** M5; T03, T10, T13; in_progress.

### R16 — Replay and leakage-resistant partitions

Record versions, hashes, seeds, environment and raw results; split by source family/layout/ancestry; keep all twins in one partition.

**Rationale:** Random seeds do not guarantee reproducibility or prevent near-duplicate leakage.

**Acceptance:** Same configuration reproduces semantics within documented tolerances; split audit finds no ancestry overlap; exported packets omit mutation-revealing names/metadata.

**Delivery/status:** M4; T11; verified.

### R17 — Challenge the validator and scorer

Use independent review, analytic examples and deliberate evaluator faults in unit conversion, comparison, severity, deduplication, leakage and unknown handling.

**Rationale:** A passing self-generated corpus can conceal a broken evaluation system.

**Acceptance:** At least one relevant broken implementation in each category is detected by the acceptance suite; surviving mutants have an explicit limitation or block release.

**Delivery/status:** M4; T11; verified.

### R18 — Inspectible offline report

Create escaped local HTML containing source crop/page, geometric evidence where relevant, expected/actual conclusion, rule provenance and regression context.

**Rationale:** Engineers need to debug a concrete issue, not merely read a score.

**Acceptance:** An independent reader can trace an example from report to exact source artifact and expected contract; reports work without a server/network; embedded arbitrary text cannot execute scripts.

**Delivery/status:** M4; T12; verified.

### R19 — Bounded and explicit data handling

Validate schemas, file signatures, paths, size/pages/solids and process timeouts; do not execute packet text or send data to hosted services by default.

**Rationale:** Drawings are untrusted inputs and often private. Resource failures must be observable.

**Acceptance:** Malformed/path-traversal/oversized cases fail with retained reasons; adapter timeout terminates its work; no network access is needed for the offline consumer workflow.

**Delivery/status:** M4; T09, T12; verified.

### R20 — Consumer evidence and truthful release claims

Provide clean-install examples, an actual external-review walkthrough, known limits, source/dependency/license inventory and a factual unpublished blog draft.

**Rationale:** Portfolio evidence requires a working consumer experience and verifiable engineering decisions.

**Acceptance:** Independent consumer repeats the workflow; report and raw results are retained. Broad industry-usefulness claims require separately authored and engineer-reviewed evidence; otherwise label synthetic limitations.

**Delivery/status:** M5; T13, T14; in_progress.

### R21 — Traceable agent implementation

Tie tasks to requirements, prerequisites, acceptance commands, retained evidence and local commits. Separate generator, validator and evaluator ownership where useful.

**Rationale:** Modern agent work is credible when its outcomes can be checked and resumed.

**Acceptance:** Every Must ID has completion evidence; task graph has no cycles; milestone decisions and unresolved assumptions are recorded; no publication/push occurs.

**Delivery/status:** M5; T00, T14; in_progress.

### R22 — Reproducible supported environments

Pin a compatible CAD/drawing stack; test the documented installation and core workflow on Windows and Linux; isolate project dependencies.

**Rationale:** An open-source tool is less useful if only its author environment can run it.

**Acceptance:** Fresh environments pass the core demo with semantic artifact checks; platform-specific limits are documented; no SolidWorks, GPU or paid model is a core requirement.

**Delivery/status:** M5; T01, T13; in_progress.

## Should

### S01 — Engineer-authored external cases

Allow a user to register owned STEP/PDF packets with explicit feature mappings, finite obligations and manually reviewed expected answers.

**Rationale:** This is the most direct route from a synthetic toolkit to a team's actual regression suite.

**Acceptance:** At least one separately authored packet works without generator-private fields; unsupported mappings are rejected; provenance/license and review notes are retained.

**Delivery/status:** M5; T13; partial_with_deferred_scope.

### S02 — Elementary tolerance and thread-depth operators

Add contradictory numeric intervals/dimension chains and simple blind-bore engagement conflicts only with explicit modeling assumptions.

**Rationale:** These are useful next cases, but functional tolerance/GD&T interpretation and tap geometry can introduce ambiguity.

**Acceptance:** Independent arithmetic/geometry checks and valid REF/alternate-process controls establish each case; uncertain process assumptions prevent scoring.

**Delivery/status:** post-v1; no initial task; deferred.

### S03 — External interoperability fixtures

Use a small licensed NIST or separately authored STEP/PMI set for importer robustness, not as unquestioned good-drawing ground truth.

**Rationale:** External files exercise failure modes missed by generated examples.

**Acceptance:** Every case records provenance and intended check; NIST limitations are stated; unsupported PMI produces explicit unavailable data.

**Delivery/status:** M5; T13; partial_with_deferred_scope.

### S04 — Interactive evidence navigation

Add a local 3D highlight and linked page/feature navigation to the static report.

**Rationale:** This could reduce diagnostic effort once the report has demonstrated value.

**Acceptance:** A consumer locates the affected face and annotation without interpreting internal IDs; static report remains usable without the viewer.

**Delivery/status:** post-v1; no initial task; deferred.

### S05 — Broader presentation metamorphisms

Vary font/layout/view order and PNG resolution within known legibility bounds; preserve meaning.

**Rationale:** Review quality should not depend entirely on one drawing template.

**Acceptance:** Meaning-preserving variants retain expected conclusions; illegible or ambiguously associated cases are quarantined; transfer errors are separately reported.

**Delivery/status:** M4; T11; deferred.

### S06 — Optional hosted reviewer integration

Add a live model API adapter only after offline/manual integration works, with explicit opt-in data transfer and budget.

**Rationale:** This makes repeated model evaluation easier without burdening the basic tool.

**Acceptance:** Record model/prompt/cost where available; replay needs no API key; missing credentials and exceeded budget fail clearly.

**Delivery/status:** post-v1; no initial task; deferred.

### S07 — Additional independent oracle signal

Cross-check a representative subset with another CAD reader or separately authored geometry and human review.

**Rationale:** A shared OCCT kernel leaves common-mode risk even with independent modules.

**Acceptance:** Publish disagreement analysis; never select the preferred answer merely because it agrees with the generator.

**Delivery/status:** M5; T13; partial_with_deferred_scope.

## Could

### C01 — Failure minimization

Shrink a failing packet/parameter set while preserving the independently validated failure.

**Rationale:** Smaller reproductions could help reviewer maintainers debug.

**Acceptance:** Every shrink is revalidated and retains the same expected obligation; minimization never changes the conclusion without recording it.

**Delivery/status:** later; no initial task; deferred.

### C02 — Semantic AP242 PMI

Consume supported semantic PMI where present; never assume STEP includes material/tolerance intent.

**Rationale:** PMI could broaden valid alternate representations.

**Acceptance:** Explicitly supported entities round-trip with evidence; absent or unsupported PMI is unknown, not a parser success claim.

**Delivery/status:** later; no initial task; deferred.

### C03 — Fixed-tool accessibility challenges

Add simple reach/radius cases under a fully declared tool catalog, setup and alternate-process boundary.

**Rationale:** This adds geometric DFM depth but requires more careful process assumptions.

**Acceptance:** Independent geometric witness supports a named-profile exclusion; other machines/tools are not ruled out globally.

**Delivery/status:** later; no initial task; deferred.

### C04 — Reviewer-output normalization assistance

Use an optional model to propose mappings from free prose to Finding records, subject to review or calibrated validation.

**Rationale:** It can lower adapter effort, but an opaque judge must not control ground truth.

**Acceptance:** Raw text and proposed mapping are retained; disputed mappings remain unadjudicated; deterministic structured path stays available.

**Delivery/status:** later; no initial task; deferred.

## Won't

### W01 — A new general DFM approval application

Do not offer arbitrary upload-and-certify behavior or imply that a passing benchmark approves a part for manufacture.

**Rationale:** The original idea already exists and general feasibility requires more manufacturing context.

**Acceptance:** Docs/UI explicitly describe testing reviewers; no global machinable badge or certification claim.

**Delivery/status:** v1; no initial task; respected.

### W02 — Arbitrary 2D-to-3D reconstruction

Do not infer complete geometry from arbitrary PDF/PNG or measure manufacturing dimensions from drawing pixels.

**Rationale:** Projection ambiguity and image scaling make strong geometric claims unsafe.

**Acceptance:** Document-only review has explicit modality limits; model-dependent obligations require STEP and correspondence.

**Delivery/status:** v1; no initial task; respected.

### W03 — Native proprietary CAD drawing support

Do not parse .slddrw or require SolidWorks/Document Manager in the open-source core.

**Rationale:** Licensing, platform and format complexity add little to the central testing contribution.

**Acceptance:** Unsupported native files explain the PDF/STEP export route; no bundled proprietary keys or libraries.

**Delivery/status:** v1; no initial task; respected.

### W04 — Complete GD&T or functional approval

Do not certify ASME/ISO compliance, complete dimensioning, tolerance stack-ups or inferred design intent.

**Rationale:** This needs broader semantics, standards access and domain judgment; sparse drawings can be correct.

**Acceptance:** Only named finite obligations are scored; no proprietary standard tables copied into the project.

**Delivery/status:** v1; no initial task; respected.

### W05 — General CAM and manufacturing simulation

Exclude five-axis/turning process planning, fixture synthesis, cutting-force/tool-life simulation, cycle time and price.

**Rationale:** These are separate substantial products and defeat a small feasible scope.

**Acceptance:** No report suggests process simulation or physical manufacture was performed.

**Delivery/status:** v1; no initial task; respected.

### W06 — Other manufacturing processes

Exclude injection molding, die casting, stamping and sheet-metal bending.

**Rationale:** Each needs distinct geometry/rules/oracles, and adjacent benchmark work already exists.

**Acceptance:** CNC track boundaries remain explicit; architecture extensibility is not advertised as implemented support.

**Delivery/status:** v1; no initial task; respected.

### W07 — Arbitrary imported artifact mutation

Do not automatically edit unrestricted customer PDFs or arbitrary STEP topology.

**Rationale:** Proving semantic correspondence and mutation isolation is much harder outside controlled families.

**Acceptance:** External cases are manually registered and independently reviewed; unsupported mutations refuse clearly.

**Delivery/status:** v1; no initial task; respected.

### W08 — Universal material/finish predictions

Do not generate a general compatibility database, coating compensation or machining parameter recommendations.

**Rationale:** Published supplier guidance is conditional and insufficient for universal rules.

**Acceptance:** Use only explicit sourced/profile assumptions; missing applicability yields unknown.

**Delivery/status:** v1; no initial task; respected.

### W09 — Hosted service or full Gas Town deployment

Exclude accounts, billing, multi-tenant uploads, orchestration services and a large autonomous agent fleet.

**Rationale:** They add operational work before the engineering tool is useful.

**Acceptance:** The core runs locally; Beads stays optional development tooling.

**Delivery/status:** v1; no initial task; respected.

### W10 — Unapproved publication or invented experience

Do not push, deploy, send supplier orders, publish blog content or claim personal shop-floor experience/results not evidenced.

**Rationale:** The user's standing constraint is local commits only, and a credible portfolio must remain factual.

**Acceptance:** All artifacts and article drafts stay local; reported results cite actual retained evidence.

**Delivery/status:** current; no initial task; respected.
