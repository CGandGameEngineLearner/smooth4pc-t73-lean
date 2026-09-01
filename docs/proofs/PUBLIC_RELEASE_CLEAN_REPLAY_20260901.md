# Public-release clean replay receipt

Verdict: `PASS`

This receipt concerns the source commit below.  The commit that adds this
receipt is documentation-only; no Lean, Python, input, manifest or build
configuration file changes after the tested commit.

## Identity and fresh-clone boundary

- tested commit: `efe5d62beffc2944e0208d6d70249ff3573c70ab`
- tested tree: `3be474ea9bd7030445bab44339e33fcd927eeed9`
- clone created: `2026-09-01T22:43:15.7473178+09:00`
- clone command:

  ```text
  git clone --no-local --branch formalize/t73-falsification \
    D:/toffee_code_in_Cursor/smooth4pc-t73-lean \
    D:/tmp/smooth4pc_public_release_clean_clone_20260901_efe5d62
  ```

- source status immediately after clone: empty
- no `.lake/` or `deps/` directory was present in the clone before dependency
  materialization
- source status after every replay command: empty

The local source URL above predates creation of the public GitHub remote.  The
`--no-local` clone copied Git objects instead of borrowing a working tree; the
tested tree is identified by its commit and tree hashes.

## Dependency replay

Environment:

- Lean `4.32.1`, toolchain `leanprover/lean4:v4.32.1`
- mathlib `520045ab14e26149ee970e2e617ca04b09bde5d6`
- committed `lake-manifest.json` SHA-256:
  `B69454066162F1084E6D2C97D28697034506AEC76B2C986E91F33F28A4F308BF`

Command:

```text
lake update
git diff --exit-code -- lake-manifest.json
```

The first network attempt ended during the mathlib Git transfer with
`curl 56 ... unexpected eof`; Lake removed the incomplete clone.  Repeating
the same command with the same lockfile completed successfully.  The second
run fetched every locked repository and decompressed 8,638 cached files.

Results:

- successful `lake update` exit: `0`
- committed-manifest diff exit: `0`
- mathlib tracked/untracked status count: `0`
- all eight inherited package repositories: locked HEAD matched, status count
  `0`

## Independent detector replay

Command:

```text
python -I -B scripts/recompute_t73_delta3.py --check
```

Exit: `0`

Output:

```text
INPUT_SHA256=04507506DC577384BC4C04765CCB212C1481DC71810C6AB3232F1AB690F16909
B44_LENGTH=11340
B44_SHA256=7C2D2F792C2672221A76CAF08A71F560AF0CB7654B4D537C00FAD00B16EFA187
B88_LENGTH=45360
B88_SHA256=C13D0A3BA9B05F41A6D2C5B4AB12DDECDABEFC1883835891AD3BD2B8955B5FFB
ELL_RHOW_MINUS_I_U_EPS=[0,0,0,7384,-660412,34814626,-1365512573]
ELL_RHOW_MINUS_I_SQUARED_U_EPS=[0,0,0,0,0,0,-456576]
DELTA3_ETA_T1=-59072
DELTA3_XI=0
PLAIN_SHADOW_CUBIC_XI=-59072
VERIFY=PASS
```

The public input contains no literal or JSON integer equal to `7384` or
`-59072` and contains neither expanded Artin word.

## Full temporary-root module replay

Command:

```text
python -B tests/test_t73_minimal_formalization.py -v
```

Result:

```text
test_axiom_report_gate_rejects_a_synthetically_removed_line ... ok
test_finite_module_exists_and_builds ... ok

Ran 2 tests in 249.682s

OK
```

Process exit: `0`.  This test compiled all 14 audited project modules into a
fresh temporary olean root, compiled the sphere consumer, ran `T73Audit.lean`,
required exactly 38 axiom reports, rejected any axiom outside the stated
allowlist and rejected `sorryAx`.

## Direct Lake audit

Command:

```text
lake lean T73Audit.lean
```

- start: `2026-09-01T22:53:31.2660177+09:00`
- end: `2026-09-01T22:55:03.8547994+09:00`
- elapsed: `92.5887817 s`
- exit: `0`
- UTF-8 output bytes: `16,460`
- output SHA-256:
  `DC2E4A1A1ECE6B737A84A5C7B201C06AFFAFACC551E8C19DB4CF55672B3D0944`
- `#print axioms` reports: `38`
- lines containing `sorryAx`: `0`

Exact axiom-output partition:

- 2 reports: `[propext]`
- 5 reports: `[propext, Quot.sound]`
- 31 reports: `[propext, Classical.choice, Quot.sound]`
- any other axiom: absent

The declaration names and the earlier byte-for-byte raw audit output are in
`T73Audit.lean` and `QSTAR_R7_T73AUDIT_RAW_20260901.txt`; the fresh-clone
unittest independently checked the complete 38-name set rather than only the
partition counts.

## Conclusion

The tested public source tree can be materialized without local dependency
paths, reproduces the detector from compact result-free input, compiles the
complete audited Lean chain through both supported entry paths, and reports no
project proof escape.  This is build and kernel evidence; the external
geometry boundary remains exactly the one disclosed in
`docs/INDEPENDENT_REVIEW.md`.
