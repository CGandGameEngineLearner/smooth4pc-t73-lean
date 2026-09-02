# Reproducing the T73 audit

These commands are intended for a fresh clone with no pre-existing `.lake/`
directory or local `deps/` tree.

## 1. Prerequisites

- Git
- [elan](https://github.com/leanprover/elan), which installs the Lean version
  named by `lean-toolchain`
- Python 3.10 or later

On Windows, if Git fails with `SEC_E_NO_CREDENTIALS`, set the OpenSSL backend
for the current shell before fetching dependencies:

```powershell
$env:GIT_CONFIG_COUNT = '1'
$env:GIT_CONFIG_KEY_0 = 'http.sslBackend'
$env:GIT_CONFIG_VALUE_0 = 'openssl'
```

## 2. Clone and materialize the pinned dependencies

```text
git clone <repository-url> smooth4pc-t73-lean
cd smooth4pc-t73-lean
lake update
git diff --exit-code -- lake-manifest.json
lake exe cache get
```

`git diff --exit-code` must return exit code `0`; otherwise the dependency
lockfile does not match the published source.

## 3. Compile the complete audited chain

```text
python -B tests/test_t73_minimal_formalization.py -v
lake lean T73Audit.lean
```

Expected results:

- the Python suite reports `Ran 2 tests` and `OK`;
- `T73Audit.lean` exits `0`;
- exactly 38 `#print axioms` reports appear;
- every report is a subset of
  `propext`, `Classical.choice`, `Quot.sound`;
- the output contains no `sorryAx`.

The Python test enforces those conditions, scans the audited Lean sources for
forbidden proof escapes and builds every project module into a fresh temporary
olean root.

## 4. Recompute the detector independently

```text
python -I -B scripts/recompute_t73_delta3.py --check
```

The script reconstructs the registered point-push word from primitive crossing
rows, rebuilds its two-cable action and performs exact truncated-polynomial
arithmetic. Its input does not contain `7384` or `-59072` as expected values.
The bearing output is:

```text
ELL_RHOW_MINUS_I_U_EPS=[0,0,0,7384,-660412,34814626,-1365512573]
DELTA3_ETA_T1=-59072
VERIFY=PASS
```

## 5. Verify the public geometry evidence

Before that, verify the public geometry evidence and recompute the
2,126,291-crossing global-descending certificate:

```text
python -I -B scripts/verify_public_geometry_evidence.py
```

The command must end with `GLOBAL_DESCENDING=PASS` and `VERIFY=PASS`.

## 6. Check the convention freeze

The legality criteria were committed before the detailed convention search:

```text
git merge-base --is-ancestor cf4a990 9d75dcd
```

The command must exit `0`. The two records are:

- `docs/proofs/QSTAR_R7_LEGALITY_CRITERIA_PRESEARCH_20260901.md`
- `docs/proofs/QSTAR_R7_LEGALITY_ADJUDICATION_20260901.md`

## 7. Interpret the result correctly

Compilation verifies the finite algebra and the implication from the
`ExternalGeometry` and Cappell--Shaneson interfaces to the final conclusion.
It does not turn those interfaces into kernel-checked differential topology.
Their published sources, exact scope and candidate-specific evidence are
listed in `docs/INDEPENDENT_REVIEW.md`.

For a clean replay certificate with exact commands, exit codes, hashes and raw
axiom output, see `docs/proofs/PUBLIC_RELEASE_CLEAN_REPLAY_20260901.md`.
