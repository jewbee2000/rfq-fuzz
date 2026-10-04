# Dependency and license decisions

Date: 2026-10-04. The RFQFuzz prototype uses **AGPL-3.0-only** for original program source, compatible with the selected Draftwright dependency. The root LICENSE retains the complete AGPL text. Generated synthetic fixture content is authored in this repository; no proprietary customer drawings or standards tables are included. No release/distribution has been performed.

| Component | Pinned version | Upstream license / notice source |
|---|---|---|
| [Draftwright](https://github.com/pzfreo/draftwright/tree/8fb66e0ae75783587380a30628d9ac6b0134da33) | 0.4.35 | AGPL-3.0; release SHA `8fb66e0ae75783587380a30628d9ac6b0134da33`; installed LICENSE |
| build123d | 0.10.0 | Apache-2.0; installed dist-info license |
| build123d-drafting-helpers | 0.15.5 | Apache-2.0; installed dist-info license |
| Quiddity | 0.3.3 | Apache-2.0; installed dist-info license |
| cadquery-ocp | 7.8.1.1.post1 | Binding Apache-2.0; OCCT kernel LGPL-2.1 with additional exception, see [OCCT license](https://dev.opencascade.org/resources/licensing) and installed binding notices |
| ReportLab | 5.0.1 | BSD; installed license |
| svglib | 2.2.0 | LGPL-3.0; installed metadata/notices |
| pypdf | 6.9.1 | BSD-3-Clause; installed license |
| pypdfium2 / bundled PDFium | 5.14.0 | Apache-2.0/BSD-3-Clause wrapper; PDFium third-party license inventory is bundled in the distribution |
| Pillow | 12.3.0 | MIT-CMU with bundled third-party notices |
| pytest | 9.0.2 | MIT |
| Poppler (external executable) | See environment.json | GPL-2.0-or-later; supplied by host runtime, not vendored in this repository |

The complete installed dependency inventory, including transitive packages, metadata and notice locations, is `evidence/M0/environment.json`. The source-download hashes are `evidence/M0/install-report.json`. Notices from the principal stack are retained under `docs/licenses/`; future packaging must preserve bundled third-party notices (including fonts, PDFium and OCCT), not rely on this short table as a redistribution checklist. Missing/ambiguous metadata is retained, not assigned an invented license. No proprietary fit/tolerance tables are reproduced or used by the M0 finite consistency check.

## V1 local consumer

V1 original source remains AGPL-3.0-only. It reuses build123d/OCCT for controlled
geometry, ReportLab for bounded vector drawings, Poppler for exported PNGs and
pypdf/PDFium for separately checked drawing content. Draftwright remains pinned
for the unchanged M0 regression and smoke; v1 does not claim a general drafting
engine. The installable package includes the public reviewer protocol.

requirements-v1.lock preserves the67M0pins and adds observed Linux-only
pexpect4.9.0/ptyprocess0.7.0. requirements-build.lock pins setuptools80.9.0 and
wheel0.45.1. Actual platform package/license metadata, download provenance and
runtime records are retained with M5 consumer evidence; coordinator inventory is
`evidence/M5/environment-windows-coordinator.json`. Runtime installations retain
their wheel-provided notices. No proprietary standards tables are reproduced.

The independent full inventories/notices are under
`evidence/M5/consumer-environments/windows` (71distributions/212notices) and
`linux` (73distributions/214notices plus system notices). Installation/download
reports and the retained handoff README identify actual paths and environments.

Separately authored synthetic transfer assets retain author provenance and
AGPL-compatible license at `evidence/M5/transfer-v2/author`. Their independent
source/measurement check is evidence about finite interoperability, not manufacture.

Portable QEMU/Ubuntu were verification infrastructure under ignored work folders;
neither guest image nor executable is distributed with RFQFuzz. Their actual
source URLs, published checksums, licenses and setup failures are retained in M5
environment evidence. No installer was executed globally. Guest SSH credentials
and disk images remain excluded from retained release evidence.

