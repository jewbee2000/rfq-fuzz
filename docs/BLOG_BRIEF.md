# Testing the tool that checks the drawing

This is an article brief, not a finished account of an implemented project. Write the final article only after the consumer milestone provides real artifacts, results and failures. Keep it local until the user changes the no-publication instruction.

## Perspective and voice

Use first person, concrete observations and understated curiosity. The available personal-site example about 3D-printed bicycle components is practical and lightly humorous; aim for that directness rather than imitating a particular internet writer. Connect the project to an interest in testing, CAD and how software decisions affect physical parts. Do not invent a job incident, supplier conversation, machine-shop experience, measured result or long-standing personal obsession.

The article should show judgment: researching the original idea, finding existing tools, choosing a more interesting test problem, and discovering where the first implementation failed. Credit existing CAD/drafting projects. Explain the use of coding agents honestly, including how their output was checked. The intellectual substance is the engineering question and evidence, not the number of agents involved.

## A prospective opening

> I'm interested in a slightly awkward question: if a tool tells me an engineering drawing looks good, how would I know whether to trust it?
>
> AI drawing reviewers already exist. The part I want to explore is how to test them. A reviewer ought to notice when a hole is 6 mm in the model and 6.8 mm on the drawing. It should also understand when different numbers are intentional, or when it simply hasn't been given enough information. Those are different problems, and counting warnings doesn't tell me which one the software has solved.

This is suggested language expressing the project's motivation, not a quotation or a claim that implementation is complete. Adjust it with the user's own reactions after the demo.

## Proposed article structure

1. **The original question.** A useful pre-RFQ check seemed like a good idea; research showed that products already do it. Link to representative prior art and explain why duplicating an upload interface was not the interesting part.
2. **A specific physical example.** Show the actual plate drawing and STEP view. Explain one defect, its repair and a valid exception using the recorded manufacturing contract.
3. **Why testing the checker is difficult.** Describe how a generator can create an accidental second error, how hidden context can make a benchmark unfair, and why “thin wall” can be an advisory rather than a manufacturing impossibility.
4. **What was built.** Show the minimal workflow and actual report. Include exact corpus size, excluded cases and one useful result. Separate a deliberately injected reviewer fault from an observed external-review failure.
5. **How agents helped and where they needed constraints.** Give one concrete task/requirement, its acceptance check, and a correction found by the independent validator. Mention Beads only if it was actually used. Agent count and model choice are secondary.
6. **What remains uncertain.** Explain the synthetic scope, common CAD-kernel dependence, template transfer and the distinction between testing reviewer behavior and approving a real part. End with a specific next experiment, not a broad claim about replacing engineers.

Target roughly 800–1,200 words with two or three legible figures. The final length should follow the evidence, not a quota.

## Evidence to collect during implementation

- A clean/defective/corrected drawing crop with an understandable feature association.
- A report screenshot that explains a changed finding.
- Run manifest, reproducible command, commit and exact denominators for any reported metric.
- One failure of the generator, validator or scorer and the corresponding fix.
- An example of a legitimate alternative that should not be flagged.
- A clear record of whether the reviewer comparison is observed, deliberately perturbed or replayed.
- Dependency/source acknowledgements and the eventual repository URL, inserted only once it exists.

The website post should link to the eventual GitHub repository, demo report and reproduction instructions. Do not create fake links, promise results or publish benchmark rankings without enough evidence to support them.
