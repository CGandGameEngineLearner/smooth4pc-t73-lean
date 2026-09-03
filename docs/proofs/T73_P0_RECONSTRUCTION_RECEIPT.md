# P0 reconstruction gate receipt

This receipt records the reproducible strict P0 proof.  The current Johnson
replacement is `PASS`; the OPEN outputs below are retained as rejected-route
controls.

```text
python3 scripts/certify_t73_p0_johnson.py --check
T73_P0_JOHNSON_CERTIFICATE=PASS
P0_STATUS=PROVED_FOR_EXPLICIT_JOHNSON_REPLACEMENT_PRESENTATION
CERTIFICATE_SHA256=02CEDCE915EBFC2B3C0A88D10BEEB050F0D7DD828F6F11DC849DA83ED2BC05D2
```

The retired Nielsen stages report:

```text
T73_AR_TORUS_MODEL=PASS
T73_MATRIX_NIELSEN_FACTORIZATION=PASS
OPERATIONS=19
T73_HEEGAARD_NIELSEN_MOVIE=PASS
T73_P0_PIPELINE=PASS
OVERALL=OPEN
```

The exact passage comparison additionally reports:

```text
NIELSEN_CHANNELS=42
COMPACT_CHANNELS=44
NIELSEN_ROUTE_STATUS=FALSIFIED_FOR_PUBLIC_44_CHANNEL_COLLAR
P0_GLOBAL_STATUS=OPEN
```

The candidate comparison movie reports:

```text
T73_WORD_KIRBY_MOVIE=PASS
RYZ_COMMUTATIONS=11257
FREE_BIGONS=1
T73_RYZ_BAND_SCHEDULE=PASS
SCHEDULE_LENGTH=11258
GLOBAL_BAND_EMBEDDING_STATUS=OPEN
```

The framing audit reports:

```text
NET_RYZ_SLIDE_COEFFICIENT=1
FRAMING_RYZ=0
FRAMING_CHANGE=2*linking(m2,r_yz)
FRAMING_STATUS=OPEN
```

The linking extractor is replayed with:

```text
python3 scripts/extract_t73_ryz_linking.py
```

At this revision it returns `T73_RYZ_LINKING=OPEN` because
`audit/t73_reduced_link_pd.json` is absent.  The historical manifest path
`D:/tmp/s4pc_ruler/DIAGRAM/out/t73_reduced_billiard.pd.json`, corresponding to
`/mnt/d/tmp/...` under WSL, was checked directly and is also absent.

The non-identifiability control reports:

```text
T73_LINKING_FROM_WORDS_FALSIFICATION=PASS
ZERO_CONTROL=0
UNIT_CONTROL=1
WORD_LEDGER_DETERMINES_LINKING=False
```

The preferred Johnson side-choice route supersedes the linking-dependent IA
candidate.  It reports an exact compact `m2` match, 44 channels and net
`r_yz` coefficient zero.  See
`docs/proofs/T73_JOHNSON_ALPHA_SIDE_RECEIPT.md` for the 93-bit choice and
deterministic search replay.

These retired-route `PASS` values apply only to their finite stage checks.  Exact local
templates, section-arc-relative support placements, handle-foot routes and
disjoint radius-1/32 thickenings are available.  That route remained open and
is not used by the Johnson certificate.

## Commands

From the repository root:

```text
python3 -m py_compile scripts/reconstruct_t73_p0.py
python3 tests/test_t73_p0_reconstruction.py -v
python3 scripts/reconstruct_t73_p0.py audit/t73_ar_product_witness.json
python3 scripts/check_t73_claim_boundary.py
```

The P0 reconstruction test command reports six passing tests, and the AR
geometry pipeline reports fourteen passing tests.  The reconstruction command
returns exit code 2 and:

```text
P0_RECONSTRUCTION=OPEN
REASON=wrong P0 reconstruction schema
```

This is expected because `audit/t73_ar_product_witness.json` is the older
symbolic witness and does not satisfy
`audit/t73_p0_reconstruction_schema.json`.

## Strict witness contract

Any replacement input must include exact rational PL vertices for the ball and
44 strands, normal vectors, an AR passage-binding map, two cancellation
movies, and a geometry-bound 11340-event elementary crossing movie.  The
program compares those Artin letters with the target regenerated from the 252
public factor rows.  The public target is never used to construct the AR
geometry.

The program also provides `--derive-events`, which enumerates elementary
crossings directly from the rational strand polylines.  A derived list still
needs the AR segment labels, independent embeddedness receipt and full
passage-binding data before it can pass P0.

The calibration control `scripts/generate_t73_target_braid_control.py` passes
the independent geometric extraction test: its explicit rational strands
recover all 11340 target letters.  It is intentionally not accepted as P0,
because it is synthetic and carries no AR passage-binding data.

## Paper build

The paper was rebuilt with three `pdflatex` invocations and one `bibtex`
invocation from `paper/spc4-t73-candidate`.  The resulting files were:

```text
paper/spc4-t73-candidate/main.pdf
output/pdf/spc4-t73-candidate.pdf
```

Both copies had SHA-256:

```text
c4a6ca9adc845e6514678eebcdb075ac71c6c033659895b6ded4f74de8111f2d
```

The claim-boundary check passed.  The paper states P0 as discharged for the
Johnson replacement while retaining C and S as open.  Appendix B contains the
soundness lemma and the committed passing certificate.
