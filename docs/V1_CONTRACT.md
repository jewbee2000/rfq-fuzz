# V1 interface freeze (T04)

The `rfqfuzz.v1` namespace owns schema version 1.0. M0's m0.1 code, schemas,
hash-bound visual attestation and ordinary artifacts remain immutable regression
inputs. Migration is explicitly refused: its one-obligation meanings must not be
silently expanded. `tools/m0.py` remains the historical entry point.

Public PacketSpec contains authority, allowed revision pairs, units, stages,
material precedence, finite required representations, feature/view correspondence,
selected full synthetic CapabilityProfile and explicit setup allowances. It
contains no variant, operator, answer, partition or ancestry. An opaque case ID
does not reveal a mutation. All actual file bytes are hashed; only the three fixed
ordinary filenames are accepted. Supported model units are mm; drawing units may
be mm or in. Unit conversion is dimensional normalization, not pixel measurement.

MutationSpec is private intent and isolation policy. OracleRecord is a separate
reader's measurements and visible evidence, with independently derived expected
conclusions. Invalid, unsupported, timed-out and unverified fixtures have reasons
and no expectations. A visual attestation must bind to the exact artifacts before
curated fixtures become scorable. Private intent is never the numeric oracle.

ReviewResult explicitly records coverage per case/obligation/modality, execution
state, findings, clear/unknown assertions, runtime if measured, and raw reference.
Findings carry category, conclusion, public location and artifact witnesses.
Multiple obligations may share one root cause. One-to-one matches cannot earn
credit twice. Empty results are unasserted, not clear. A missing-information
decision is an engineering conclusion; a timeout is an execution failure.

RunManifest binds actual suite, oracle, selected profiles and raw responses plus
adapter version, environment, seed, limits and failures. Comparisons require all
three input hashes to agree. Answer-key correction changes the oracle hash.

Transport schemas under `schemas/v1` and semantic checks in
`src/rfqfuzz/v1/contracts.py` define the worker boundary. The v1 generator,
validator and evaluator live in separate modules and exchange these records.
Native STEP/PDF parser processes must be bounded; same-user local adapters are
procedural isolation, not an adversarial sandbox. No hosted calls are implicit.
