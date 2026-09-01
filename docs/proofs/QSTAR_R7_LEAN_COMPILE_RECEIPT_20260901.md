# QSTAR R7 — Lean compile and axiom receipt

Verdict: `PASS_WITH_DIRTY_DEPENDENCY_DISCLOSURE`  
Scientific scope: compilation and kernel-dependency evidence only; no geometric
premise is certified by this receipt.

## Audited identity

- branch: `formalize/t73-falsification`
- HEAD: `cf4a990cca9a693e0c32b6cd8a978942cd03168a`
- HEAD tree: `1bc704774bc8a7eef732801d34f368d622eff5d4`
- 2026-09-01 JST first-parent commits: 26
- tracked worktree changes before and after both runs: 0
- cached changes: 0
- top-level untracked entries: 20
- main-status LF-SHA256:
  `E4202EF0E488AD2C94538D57C9A4359B367DDD3AF273659B1F8486E0B8958D93`

The main worktree is therefore tracked-clean at the audited HEAD, but the
whole directory is not clean because of pre-existing untracked Task-5,
dependency, evidence, script and test paths.

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
  `C1999195B676FED260F87EC541423C1A65E4CF06BC250D7ADB769C67A045DCFF`
- `lake-manifest.json` SHA-256:
  `07C8A31C34DDA3AF0F8FD493B03FFC069AE2E7CFD685396A4EA74756B93A3FBC`

Resolved mathlib:

- path: `D:/tmp/lean_joint_audit/mathlib4`
- HEAD: `520045ab14e26149ee970e2e617ca04b09bde5d6`
- tree: `b701c3b42faf7960b44e01a1359800f5ec35cbf8`
- tracked changes: 0
- cached changes: 0
- untracked root probes: 45
- status LF-SHA256:
  `708032AE9B1650B1E0C70782FA857E380040D4F08565C6291E98159E2570D673`
- eight package dependencies: manifest revisions matched; dirty count `0`
- `Mathlib.olean` SHA-256:
  `1F0BCB563F3802B5CDAE7068BE69B739209A466F8535B4EF71CFD14BF9C29E06`

The 45 untracked files are unrelated root-level scaling-law probe/audit
`.lean/.olean` files.  No tracked mathlib source was modified.  This is still
not a hermetic clean clone, and the receipt does not claim otherwise.  The
earlier reported count `126` is not the state observed during this run.

## Full unittest

Command:

    $env:T73_LAKE = 'C:/Users/LENOVO/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe'
    $env:T73_TMP = 'C:/Users/LENOVO/AppData/Local/Temp'
    python -B tests/test_t73_minimal_formalization.py -v

Result:

- start: `2026-09-01T21:08:24.9627019+09:00`
- end: `2026-09-01T21:15:22.9117898+09:00`
- elapsed wall time: `417.949 s`
- process exit: `0`
- tests: `2/2 OK`
- stdout: `<empty>`

Complete stderr:

    test_axiom_report_gate_rejects_a_synthetically_removed_line (__main__.T73FiniteFormalizationTests.test_axiom_report_gate_rejects_a_synthetically_removed_line) ... ok
    test_finite_module_exists_and_builds (__main__.T73FiniteFormalizationTests.test_finite_module_exists_and_builds) ... ok

    ----------------------------------------------------------------------
    Ran 2 tests in 417.351s

    OK

The test compiles all tracked T73 modules into a fresh temporary olean root,
checks the sphere-coordinate consumer, scans the source set for forbidden
`sorry`, `admit`, project `axiom`, `unsafe`, `extern`, and validates every
required axiom report.

## Independent module build and direct axiom audit

A second run compiled 14 project sources, in dependency order, into:

    C:/Users/LENOVO/AppData/Local/Temp/
      t73-audit-receipt-48398aacca344c40817e9d6ba5fe6800/olean

- module builds: `14/14`, every exit `0`
- build elapsed: `224.824 s`
- direct `T73Audit.lean` run: exit `0`
- direct audit elapsed: `17.569 s`
- stdout bytes: `14194`
- stderr bytes: `0`
- raw output SHA-256:
  `DAD82BEEF534DF5E3FE012958EF3869BC10C782467DD5762A138801FF0706845`
- `#print axioms` reports: `38`

The complete raw output is
`docs/proofs/QSTAR_R7_T73AUDIT_RAW_20260901.txt`.

Axiom report partition:

- 2 declarations: `[propext]`
- 5 declarations: `[propext, Quot.sound]`
- 31 declarations:
  `[propext, Classical.choice, Quot.sound]`
- `sorryAx`: absent
- any axiom outside that allowlist: absent

Key source hashes:

- `T73Audit.lean`:
  `98484633F2B8D04E3524C41F207C535D6EC66743FBEC65FDF54CAE3A900CBC66`
- `tests/test_t73_minimal_formalization.py`:
  `73FCF87370903BD3EE88BADF48E5CCBDECCACC6C96B2827DF094E528A49CBCC8`

## Conclusion

The 9/1 tracked Lean layer at the named HEAD compiles twice and its audited
declarations use only the three stated foundational axioms.  This closes the
missing on-disk compile/axiom receipt.  It does not instantiate or prove the
external geometric interfaces.
