# Reproducible P0 reconstruction pipeline

This document records the strict P0 reconstruction protocol.  Geometric P0
remains Open after P0a:

```text
python3 scripts/certify_t73_p0_johnson.py --check --skip-geometric-braid
P0_STATUS=OPEN
```

The older symbolic witness remains a rejected control; no identity with the
unavailable historical PD is claimed.

## Retired route diagnostics

The upstream AR geometry stages are replayed with:

```text
python3 scripts/build_t73_ar_torus.py --check
python3 scripts/factor_t73_matrix_nielsen.py --check
python3 scripts/build_t73_psi_candidate.py --check
python3 scripts/generate_t73_heegaard_nielsen_movie.py --check
python3 scripts/compare_t73_nielsen_passages.py --check
python3 scripts/check_t73_p0_pipeline.py --check
```

The torus stage constructs the scaled period-four Freudenthal model, and the
matrix stage factors the trace-73 matrix into 19 exact elementary moves.  The
paired Heegaard movie preserves the primal/dual intersection pairing at every
step.  Exact local templates cover 52 unit slides, 62 sequential supports are
placed away from the section arc, and the handle-foot routes admit disjoint
radius-1/32 thickenings.  That branch did not compose these cells into one
simplex-by-simplex homeomorphism and correctly returned `OVERALL=OPEN`; it is
not the current Johnson proof.

The explicit Nielsen representative is no longer merely incomplete: after
the registered cancellations its $m_2$ word has length 309 and 40 $y/Y$
passages, so together with $r_{xy}$ it has 42 channels.  The compact
representative has length 311 and 44 channels.  Thus this particular Nielsen
route is falsified for the public collar.  The Johnson side-choice route below
supplies the required different representative.

The word-level part of that movie has now been generated: both representatives
collect to `y^40 z^269`, and the combined movie contains 11257 `r_yz`
commutations plus one free bigon.  Every step has an owner-preserving local PL
band template.  The remaining gate is the embedding of those bands in the
actual reduced `m2 union r_yz` link and the global product-framing transport.

The signed schedule has net `r_yz` coefficient one.  Since the AR fiber
handle has product framing zero, the framing change is
`2*linking(m2,r_yz)`.  The movie is framing-preserving exactly when the actual
reduced Kirby-diagram linking is zero; this integer cannot be recovered from
the free-word ledger.

`scripts/extract_t73_ryz_linking.py` computes this integer from a labelled
reduced-link PD ledger satisfying `audit/t73_reduced_link_pd_schema.json`.
The extractor validates crossing signs, mixed-component ownership, evenness
of the signed crossing sum and the normal-field receipt.  No actual reduced
PD ledger is currently available, so this gate remains open.

The necessity of that input is machine-checked.  Two local-clasp controls
share the same component word hashes and framing ledger but have linking zero
and one.  `scripts/falsify_t73_linking_from_words.py` therefore falsifies the
claim that the committed word data determine the framing gate.

The compact straight-word lift also fails a stronger necessary condition:
GAP 4.12.1 finds its `F_3` endomorphism injective but not surjective.  The same
test accepts the explicit Nielsen positive control.  Therefore the compact
three-word list cannot itself be the image of a handlebody homeomorphism.

The search code finds a replacement automorphism by simultaneous inner
conjugation with `x^-1`.  It has length-311 `m2` and 44 channels, but not the
exact compact word.  Its exact comparison movie has 11754 commutations, two
bigons and net `r_yz` coefficient `-40`.  The bounded depth-three IA search
found no zero-coefficient channel-compatible representative.

The simultaneous inner correction is only a based lift.  Its three cyclic
spine classes agree with the original Nielsen classes, so the count change
from 42 to 44 is caused by common whiskers, not by a proved change of the
unbased embedded collar.  `audit_t73_inner_conjugation_geometry.py` therefore
rejects it as a P0 witness.

Johnson's eight-generator theorem supplies the correct search space.  The
matrix is factored into 93 unit `alpha_ij` moves, and each square diagonal has
two splitting-preserving side choices.  The saved 93-bit choice is a GAP
free-basis automorphism, has exact compact `m2` length 311, has 44 total
channels, and has zero class-two `r_yz` difference.  Its 93 square movies are
made relative to a uniform protected ball of radius `1/196104`.  The Johnson
collar generator supplies 44 rational product lanes, and the AR-side six-leg
generator is re-extracted as the public 11340-letter braid.

The complementary-handlebody filter applies each IA correction to the dual
meridians `[x,y]`, `[y,z]`, `[z,x]` and accepts a signed permutation of their
conjugacy classes.  This is a strict sufficient disk-system extension test.
At depth three, 751 channel-compatible candidates genuinely change the
detector cyclic class and none pass.  The condition is not necessary, so this
is a bounded route elimination rather than a global P0 falsification.

## Current Johnson witness

The current proof chain is:

```text
factor_t73_matrix_johnson.py
  -> search_t73_johnson_alpha_sides.py
  -> generate_t73_johnson_alpha_movie.py
  -> straighten_t73_johnson_relative_ball.py
  -> certify_t73_johnson_cancellations.py
  -> generate_t73_johnson_ribbon_collar.py
  -> derive_t73_johnson_six_sweeps.py
  -> generate_t73_johnson_geometric_braid.py
  -> certify_t73_p0_johnson.py
```

The committed summary is `audit/t73_p0_johnson_certificate.json`.  All source
geometry is generated before the public target is read; the final comparison
is letter-for-letter in the relative-endpoint braid group.

## Witness contract

The input must contain exact rational PL data for:

1. a triangulated 3-ball and its boundary triangles;
2. 44 labelled monotone polylines in a collar, with one nonzero normal vector
   at every vertex;
3. a certificate binding every strand to a segment of the actual AR attaching
   link, including endpoints and transported normals;
4. the two local cancellation movies, including owner and normal-field
   transport;
5. an ordered elementary crossing movie whose Artin letters are computed from
   the AR geometry, not copied from the public input.

The crossing movie contains a derivation receipt with the canonical digest of
the ball, the 44 strand polylines and the AR passage-binding map.  The
verifier recomputes this digest before reading the events, so public rows
cannot be attached to unrelated geometry.

The program independently reconstructs the public target word from the
primitive six-sweep rows in `data/T73_DELTA3_PUBLIC_INPUT.json`.  It never uses
that word to construct the source geometry.  The source movie has 11340
elementary crossings; the 252 public rows are used only to regenerate the
target word.  The AR-derived movie itself must agree letter-for-letter with
the target.

For a candidate containing explicit strand coordinates, the elementary movie
can be generated independently with:

```text
python3 scripts/reconstruct_t73_p0.py P0_INPUT.json --derive-events
```

This mode enumerates pairwise segment intersections in exact rational
arithmetic and emits the event list.  It does not read the public crossing
rows.  The resulting events must still be attached to the AR source segments
and pass the full P0 verifier.

The calibration program
`scripts/generate_t73_target_braid_control.py` constructs a rational 44-strand
realization of the target word and is covered by the P0 tests.  It is a
negative control for the AR gate: its word comparison passes, but it has no AR
passage binding and is not a P0 witness.

## Mathematical content of a passing certificate

Let (K) be the explicit framed AR attaching link in the reduced boundary
handlebody, and let (c_i:[0,1]	o B), (1leq ileq44), be the certified
collar strands.  The certificate supplies a PL ball (B), a collar height
function (z), and a framing vector field (n_i).  The verifier checks the
finite conditions needed for the intended geometric argument:

* every (c_i) is height-monotone, so it is a braid strand;
* the supplied embeddedness and disjointness receipt applies to the complete
  PL complex, not just to its word projection;
* the AR passage map preserves component ownership, endpoint order and
  normal fields through both cancellations;
* each movie event records its height, two strands, over-strand, sign and
  Artin letter; and
* the derivation receipt binds the movie to the supplied ball, strands and AR
  passage map by digest;
* the ordered Artin word from these events equals the public 11340-letter
  word.

The last equality is equality in the braid group representation determined by
the relative endpoint movie, not equality of exponent sums.  The first four
conditions identify the movie with the actual AR collar.  Therefore a passing
certificate proves that the geometric braid of the embedded framed ball is
the public braid.  Conversely, a hash, writhe, permutation, free-group word,
or mapping-class realization without the AR passage map does not satisfy the
input contract.

## Current replay

The current committed object is intentionally rejected:

```text
python3 scripts/reconstruct_t73_p0.py audit/t73_ar_product_witness.json
```

Expected result at the current revision:

```text
P0_RECONSTRUCTION=OPEN
REASON=wrong P0 reconstruction schema
```

This is the correct result because the existing object contains descriptive
strings and public-input-derived rows, rather than the required PL geometry.
Once an actual AR parameterization and its independent receipts are supplied,
the same command is the final P0 gate.
