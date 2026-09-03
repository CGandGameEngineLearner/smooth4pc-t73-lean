# QSTAR R8 — Lean compile and axiom receipt

Verdict: `PASS_WITH_DIRTY_DEPENDENCY_DISCLOSURE`
Scientific scope: compilation and kernel-dependency evidence only.  This
receipt does not certify any candidate-specific geometric premise.

## Audited working identity

- base HEAD: `8160d15d4943290f9e672647173bc5f023e86fa9`
- base HEAD tree: `9b619f5c6257a82443df02e334669e72ab3c6a1f`
- state: intentional uncommitted erratum changes
- platform: Windows, x86-64

The compilation was performed before the erratum commit so that the commit can
contain the resulting raw audit and this receipt.

## Toolchain and dependency identity

- Lean: `4.32.1`, commit `f054605aea4b840552cca2e725580bffd1e1b704`
- Lake: `5.0.0-src+f054605`
- Python: `3.13.3`
- `lean.exe` SHA-256:
  `C3F02A2B739078D1237AF9FEEFD27EC85B943B56870234B42BC0111D6699D54D`
- `lake.exe` SHA-256:
  `9274B0E4370EF69517F5AD70E2997F6190996D3A1174B295BEEC8E77B82BBB3C`
- `lean-toolchain` SHA-256:
  `8E3538E0AB5F81A3EE04927D8838C8C674E0E112838B4B3CE87EC218143276AF`
- `lakefile.toml` SHA-256:
  `C5EC1B13BA3C1FFE623E5854526F3031F7E78F850FF63C859C2D0BED7C1168A5`
- `lake-manifest.json` SHA-256:
  `B69454066162F1084E6D2C97D28697034506AEC76B2C986E91F33F28A4F308BF`

Resolved mathlib:

- HEAD: `520045ab14e26149ee970e2e617ca04b09bde5d6`
- tree: `b701c3b42faf7960b44e01a1359800f5ec35cbf8`
- current `git status --short` entry count: `0`

The earlier R7 receipt disclosed a different dependency workspace with a
dirty count of `126`.  That historical disclosure remains part of the record;
it is not silently rewritten as a clean run.  The checkout actually used for
this R8 compile reports zero status entries.

## Fresh-output unittest

Command:

    $env:T73_LAKE = 'C:/Users/LENOVO/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe'
    $env:T73_TMP = 'C:/Users/LENOVO/AppData/Local/Temp'
    python -B tests/test_t73_minimal_formalization.py -v

Result:

- process exit: `0`
- tests: `2/2 OK`
- the test compiled the tracked T73 source set into a new temporary olean root
- the source and output scans found no `sorry`, `admit`, project `axiom`,
  `unsafe`, or `extern` shortcut

## Direct module and axiom audit

The tracked Lean library targets required by `T73Audit.lean` were rebuilt.
The direct command was:

    lake env lean T73Audit.lean

Result:

- process exit: `0`
- raw output bytes: `14182`
- raw output SHA-256:
  `011856649EA7EF0C43558889EAE6F44933D253B5343BDB3FC8F06517BBA2FE3A`
- `#print axioms` reports: `38`
- 2 declarations: `[propext]`
- 5 declarations: `[propext, Quot.sound]`
- 31 declarations: `[propext, Classical.choice, Quot.sound]`
- `sorryAx`: absent
- any axiom outside that allowlist: absent

The complete raw output is
`docs/proofs/QSTAR_R8_T73AUDIT_RAW_20260903.txt`.

Key source hashes:

- `T73Audit.lean`:
  `9279C11348F45A4AC5EE8424AF049555D2DC7B5C3625B7DB594FA39BE47D4233`
- `tests/test_t73_minimal_formalization.py`:
  `02B05D2CE0E2317B302B387C548F99B2D046830833F472852B9C9B247DAF1609`

## Conclusion

The erratum Lean layer compiles from a fresh temporary output root, the direct
audit exits zero, and every reported dependency lies in the stated
foundational allowlist.  The compiled arithmetic now includes
`computedCubic_eq_2624`.  These facts verify the finite arithmetic and the
conditional implication only; they do not instantiate the external geometry.
