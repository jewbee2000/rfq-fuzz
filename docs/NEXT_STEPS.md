# Next steps and owner checklist

2026-10-04. M0–M5 are complete for the bounded synthetic regression scope:
22 Must requirements, 15 completed tasks and 270 passing integrated tests.
The [requirements evidence matrix](REQUIREMENTS_EVIDENCE.md) and
[Should deferrals](SHOULD_DEFERRALS.md) remain the acceptance record.
The public source repository is [jewbee2000/rfq-fuzz](https://github.com/jewbee2000/rfq-fuzz).
The labeled [article draft](BLOG_DRAFT.md) is readable in that repository; it has
not been posted to the blog. No additional milestone is accepted by this roadmap.

## What Walt should do now

1. **Inspect the consumer result.** In this existing Windows checkout, run:

   ```powershell
   .venv/Scripts/python.exe -m rfqfuzz.v1 demo examples/v1-demo work/owner-demo
   ```

   Use a new output directory if `work/owner-demo` already exists. Open
   `work/owner-demo/report/index.html`. Confirm that the report makes the two
   deliberately injected changes understandable: a material contradiction goes
   from detected to silently missed, and a valid diameter goes from correctly
   clear to falsely flagged. These are replay controls. For a fresh installation,
   follow [DEMO.md](DEMO.md), including Python 3.12 and platform setup.

2. **Provide one packet you have permission to use.** Start with a simple
   CNC plate or prismatic block: STEP, its drawing PDF and the governing RFQ
   context. Remove confidential information and record whether the files may be
   publicly redistributed or must stay local. Supply units, material/finish,
   process stage, CAD/drawing authority, feature correspondence and any named shop
   setup limits. A synthetic packet separately authored by an engineer is a
   useful fallback if no real packet can be shared. A new layout may require an
   explicit import extension; current support is finite, not arbitrary CAD/PDF.

3. **Arrange a qualified CNC engineer's review.** Ask the engineer to record the
   evidence for a defect, its repaired twin, a valid lookalike and a genuinely
   unresolved case under the same declared premises. Record disagreements and
   quarantine ambiguous or accidentally multi-defect cases. Expected answers
   stay separate from the packet presented to a reviewer. Do not ask the engineer
   to certify a manufactured part on the strength of this toolkit.

4. **Name the first reviewer to test.** Supply the actual product or local
   reviewer, version, access method and two configurations to compare. The first
   run can use the existing manual result-import path. A hosted run requires
   explicit authorization for that adapter and those packet files; public source
   publication does not authorize uploading private packets. Never include the
   private expected answers or mutation labels in the reviewer input.

5. **Review the article before deciding to publish it.** Check the
   [blog evidence map](BLOG_EVIDENCE.md). Keep synthetic replay controls,
   independently observed external findings and future engineer-reviewed cases
   distinct. The current article can describe the completed bounded work; broader
   reliability claims require new evidence. Posting to the blog remains a
   separate decision and is not authorized here.

## Next engineering work, in dependency order

| Proposed step | Depends on | Concrete acceptance |
|---|---|---|
| Native Windows/Linux continuous checks | Public repository; documented platform dependencies | A clean runner installs the pins, preserves M0, passes the suite and reproduces the 15-case offline demo. Keep failure logs and resource bounds. Existing local consumer evidence is not a CI run. |
| Engineer-reviewed transfer pilot | Owner checklist items 2–3 | Rights, premises, engineer adjudication and reopened STEP/PDF/PNG evidence are retained. Unsupported or disputed packets remain unresolved. |
| Real reviewer comparison | Validated pilot; item 4 | Fresh public-only inputs, raw outputs, reviewer version/configuration, separate-track results and source-linked changes are retained. Investigate scorer disagreements rather than force matches. |
| Frozen external holdout | Pilot works; separately authored packets are available | Reserve case lineages and layouts before tuning. Start with a small set, for example 3–5 packets; it is diagnostic transfer evidence, not an accuracy estimate. Report all invalid, unsupported, timeout and uncovered results. |
| Small consumer usability trial | Repeatable real comparison | An independent user completes the workflow and identifies the source of a changed result without coordinator intervention. Record failures and useful feedback. |

Preserve the accepted M0 example and the completed M1–M5 evidence throughout.
Create a new requirements/task graph for any accepted follow-on scope; do not
reopen completed tasks or quietly relabel Should deferrals as implemented.
Prioritize whether the oracle transfers and the report changes a user's decision
before expanding the synthetic corpus, adding a CAD viewer or building hosting.

If independent adjudication repeatedly cannot establish an answer, narrow the
supported decision contract or stop that extension. A public repository alone is
neither evidence of user demand nor proof of general manufacturing competence.
