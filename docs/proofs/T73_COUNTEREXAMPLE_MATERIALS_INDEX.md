# T73 counterexample candidate materials index

**Status:** CANDIDATE_PROOF_PENDING_INDEPENDENT_REVIEW

This file is the entry point. The mathematical derivations and the formerly
machine-local load-bearing certificates are now colocated in the repository.
Their byte identities are pinned below and in
[`evidence/public_geometry/SHA256SUMS`](../../evidence/public_geometry/SHA256SUMS).

## Core proof

1. [T73_SPC4_COUNTEREXAMPLE_CANDIDATE_PROOF.md](T73_SPC4_COUNTEREXAMPLE_CANDIDATE_PROOF.md)
   End-to-end proof and dependency table.
2. [T73_GA1_DESCENDING_BRIDGE.md](T73_GA1_DESCENDING_BRIDGE.md)
   Actual Aitchison--Rubinstein product-ribbon, suspension, whole-boundary
   Laudenbach--Poenaru and DIAGRAM bridge.
3. [T73_PROOF_STATE_LEDGER.md](T73_PROOF_STATE_LEDGER.md)
   Recovery ledger, supersession chronology and forbidden stale routes.

## Colocated supporting derivations

| local file | source object SHA-256 | role |
|---|---|---|
| [T73_EVIDENCE_QTRACE_SOURCE_LEDGER.md](T73_EVIDENCE_QTRACE_SOURCE_LEDGER.md) | 99913F0AF70CF5FF650492C2740F98B7053FEBBB58212DA32B506D863836EA84 | coefficient q-trace and divided functional |
| [T73_EVIDENCE_RAW_STATE_BINDING.md](T73_EVIDENCE_RAW_STATE_BINDING.md) | BCBFBC9F8A5350D323EC2876352EC25C6690E5BB6AD4F2C264441BA4D73CDEF6 | actual selected raw state and degree |
| [T73_EVIDENCE_ETA_T1_DELTA3.md](T73_EVIDENCE_ETA_T1_DELTA3.md) | 96E20A5D75B3A6B3587267BF2052A79845E378F96901351B5DC52BB5D16EF183 | v_T versus xi and the exact cubic |
| [T73_EVIDENCE_ONE_CUP_E5_E6.md](T73_EVIDENCE_ONE_CUP_E5_E6.md) | 6A63978D734EFF30B8F6C2E6F9800F9338B3499BA1CA4D6AF4880716468FE865 | complete one-/two-handle divided quotient |
| [T73_EVIDENCE_W2_CORE_FACTOR.md](T73_EVIDENCE_W2_CORE_FACTOR.md) | 73F5D57A2074B133687018D1D8641FF2DA76ED5B01F055B6D89E7F086F10E129 | local core/counit factorization |
| [T73_EVIDENCE_E8_CHOSEN_SPHERES.md](T73_EVIDENCE_E8_CHOSEN_SPHERES.md) | C33AF1FCAE8F0056A75D1841E1151786C2EBB756AD8A768C4E3E6704274E2B43 | chosen-sphere geometry and whole-source rows |
| [T73_EVIDENCE_GLOBAL_DESCENDING.json](T73_EVIDENCE_GLOBAL_DESCENDING.json) | B180465D4D586A555249F6D545C78F749BCAF68908579F3AED55FF4096CF667E | exact 2,126,291-crossing replay with gate-aligned basepoints; input PD SHA is recorded inside |
| [../../scripts/verify_t73_global_descending.py](../../scripts/verify_t73_global_descending.py) | 92017C224F9D54715EE6125374ACBF361B3A04BF61FB161D4DEF3E9F23F9C05E | linear-time independent replay of the frozen PD |
| [../../scripts/t73_g1_kirby_slide_backup.py](../../scripts/t73_g1_kirby_slide_backup.py) | 94CA0240D0424F90DDF36D2B0483EE52BD3D4369DAE17DB8BBD4DBE002B1E519 | non-load-bearing collected/billiard backup |

The local Markdown copies preserve the mathematical text of the named source
objects. Their repository byte hashes differ because Git normalizes line
endings and the filenames are new; the table records the original source
identities.

## Colocated finite inputs

| repository object | SHA-256 | role |
|---|---|---|
| [ACTUAL_PD_CABLE_UNIT_CERT.json](../../evidence/public_geometry/ACTUAL_PD_CABLE_UNIT_CERT.json) | 7F3D3618D6A790A9B60EE8085B647AC2AB742E1BC9C15841F1BEF015034217B5 | exact paired-annulus/cable certificate |
| [TH1_EXHAUSTIVE_ALL_ROW_GEOMETRY.json](../../evidence/public_geometry/TH1_EXHAUSTIVE_ALL_ROW_GEOMETRY.json) | EE620E6B085A5F9E1C73CFDD1AD04FC0682CEC74DA3DBF8AFE70DD19C038E3A0 | exhaustive TH1 receipt |
| [TH2_EXHAUSTIVE_ALL_ROW_GEOMETRY.json](../../evidence/public_geometry/TH2_EXHAUSTIVE_ALL_ROW_GEOMETRY.json) | 4D1B627C0343A1C464319704EAFADCA127902A2E4E90CF1C283004359B7ADC24 | exhaustive TH2 receipt |
| [THXY_FULL_MACRO_P3FREE_HJ_CERT.json](../../evidence/public_geometry/THXY_FULL_MACRO_P3FREE_HJ_CERT.json) | EABF67C0D1AE309F0281297710A283B8ED5A11D88C8E810837932313F4C53227 | THXY full-coordinate certificate |
| [t73_reduced_billiard.pd.json](../../evidence/public_geometry/t73_reduced_billiard.pd.json) | E6912A64457557469E5C691B4D57ABDBBF4C45ADB05492777C574223D0C06F8A | 2,126,291-crossing input to the global-descending replay |

Run `python -I -B scripts/verify_public_geometry_evidence.py` from a clone to
verify every bundled SHA and recompute the global-descending result from the
full PD.  The three chosen-sphere receipts can now be inspected directly;
their much larger upstream construction trees are not silently represented as
part of this repository.

Primary public source for the Aitchison--Rubinstein construction:
https://math.berkeley.edu/~kirby/papers/Gordon%20and%20Kirby%20%28editors%29%20-%20Four-manifold%20theory%20%28Durham%29%20-%20MR0780574.pdf

## Scope firewall

- Carrying class: v_T=eta_R[T_1], not xi and not mixed Z.
- Exact value: D_3(v_T)=-59072.
- Final quantum degree: 494.
- The proof is at the divided h^3 coefficient; it does not claim full-q
  sphere matrices.
- The G1 bridge transports the actual product framing. It does not certify the
  emitter's numeric blackboard framing or the writhes 267/1270.
- A PASS in the local hostile audits is not Lean formal verification or
  external mathematical acceptance.
