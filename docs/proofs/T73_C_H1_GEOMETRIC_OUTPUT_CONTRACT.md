# C-H1 rational relative-isotopy output contract

Date: 2026-09-05

## Required geometric object

The C-H1 representability proof requires one common rational triangulation of
the coefficient exterior in a 3-ball with four parametrized insertion balls.
The source must contain all 630 exterior intervals, all 1260 oriented
boundary endpoints, their complete matching, and explicit framing push-offs.

The movie must be an ambient isotopy relative to the outer boundary and
pointwise relative to all four insertion-ball boundaries.  Its final image
must equal geometry/t73_selected_canopolis_normal_form.json strand by strand,
including the cyclic \(m_2:C_i\to c1:\mathrm{letter}:0\) lane and all 227
added z lanes.

## Accepted movie representation

data/T73_C_H1_RELATIVE_ISOTOPY.schema.json and
scripts/verify_t73_c_h1_relative_isotopy.py implement a restrictive
proof-producing format:

1. every ambient vertex has a rational three-coordinate;
2. every tetrahedron is listed by four vertex IDs and is nondegenerate;
3. the outer boundary and four insertion-ball boundary subcomplexes are
   explicit;
4. every source strand and framing push-off is an edge path in that common
   complex;
5. every time slab moves exactly one non-boundary vertex along a rational
   straight segment;
6. the complete tetrahedral star of that vertex is listed, its link is a
   connected triangulated 2-sphere, and every incident determinant has the
   same nonzero sign before and after the move;
7. because each determinant is affine in the moving vertex, the preceding
   sign check proves nondegeneracy at every time, rather than at finitely
   sampled frames;
8. final source paths and endpoints must equal the rational target paths
   exactly;
9. orientations, source/target insertion balls, product framings and relative
   twists are checked;
10. births, saddles and deaths must all be zero, the closed trace must have
    Euler characteristic zero, and the quantum shift must be zero.

Since strands and push-offs are required to be subcomplex edge paths,
disjointness reduces to the embedded ambient triangulation plus the checked
absence of shared interior vertices.  A source builder must itself produce
the ambient triangulation from a deterministic embedded mesh construction;
an arbitrary self-reported triangulation receipt is not sufficient.

## Fail-closed co-Yoneda consumer

scripts/build_t73_c_h1_coend_certificate.py refuses to construct
audit/t73_c_h1_coend_certificate.json unless the coordinate movie receives
PASS_COORDINATE_MOVIE.  Only then does it record:

\[
p_y=44,\qquad p_z=271,\qquad \ell=227,
\]

the normalized two-representable shift \(-227\), co-Yoneda shift \(-227\),
Kunneth shift \(+227\), reduced normalized shift zero, and conditional final
degree 223.

Thus target geometry, status strings, hashes, word counts, or endpoint counts
alone can never create the categorical certificate.

## Current authoritative result

The newly generated
geometry/t73_selected_source_exterior.json gives the complete combinatorial
four-cycle incidence and 630 pairwise disjoint rational polygonal routes with
pairwise disjoint framing push-offs.  It is explicitly a canonical
representative only, not an AR-relative model, and it has no common
tetrahedral exterior.  Thus it is complete as polygonal source data but does
not yet satisfy the stronger simplicial subcomplex contract.

Schema v2 of geometry/t73_selected_canopolis_normal_form.json corrects the
earlier boundary-type error.  Both source and target now have endpoint counts
\[
(88,88,542,542),
\]
630 exterior arcs and 1260 total boundary endpoints.  On each target side the
88 active Y--Z arcs use one Y and one Z endpoint, while the 227 residual
Z--Z arcs use 454 further Z endpoints.  Exact verification checks all target
arcs and push-offs.

Matching, rather than cardinality, is now decisive.  The source contains the
eight same-side intervals listed below, whereas the abstract target contains
only the two cross-side matching classes.  An ambient isotopy pointwise
relative to the four balls preserves this matching.  Therefore no relative
ambient isotopy exists between the current source and literal split target,
regardless of how many time slices or tetrahedra are added.

The older geometry/t73_product_ribbon_isotopy.json says PASS and
exhibited_product_isotopy=true, but every rectangle frame contains only a
time and an arc hash.  It has no common ambient triangulation, four-box
endpoint incidence, rational cell map, or framing track.  The new verifier
records that file as rejected.

The selected canopolis target is coordinate-defined with the correct complete
boundary type.  Regina or link-complement recognition cannot repair the
remaining matching obstruction: endpoint matching on fixed boundary spheres
is already an isotopy invariant before complement recognition begins.

Therefore no relative-isotopy or co-Yoneda PASS certificate has been
generated.  An actual replacement for the literal split must be a genuinely
nested coend/pivotal construction with explicit natural-transformation cells
and grading; separately, a simplicial realization would still have to place
the polygonal source in one common tetrahedral chart.

## Mixed-orientation matching obstruction

Correcting the target to 630 total arcs is necessary but not sufficient.
The 176 source intervals incident to a y insertion sphere have transitions
\[
\begin{array}{c|r}
\{Y_-,Z_+\}&84\\
\{Y_+,Z_-\}&84\\
\{Y_-,Z_-\}&4\\
\{Y_+,Z_+\}&4.
\end{array}
\]
The final eight rows are recorded explicitly in
audit/t73_c_h1_relative_isotopy_report.json.  They are the intervals adjacent
to the two negatively oriented base y passages
\[
m_2:C_i,\qquad r_{xy}:\mathrm{vertex}:1
\]
on both cable copies and both sides.

A two-representable target with one y box and one oppositely signed z box in
each closure accommodates the first 168 intervals but not these eight.
Preserving their pointwise endpoints forces each proposed closure factor to
use endpoint subsets on both z insertion spheres.  Then two closure balls
cannot be disjoint relative to the four balls, and arbitrary
\(\mathcal C_{271}\) insertion tangles may mix those subsets.

Changing the eight matchings to opposite-side matchings requires four
independent reconnections.  Pivotal mate operations can change how a fixed
tangle is curried, but preserve the total number of active boundary
endpoints, here 176.  They do not produce the 174 endpoints of a
\(P_{86}\to P_{88}\) object.  The weight-one defect instead comes from the
separately chosen external cup \(E_{86}\to E_{88}\).

scripts/audit_t73_defect_aware_currying.py records the four deterministic
candidate reconnections but leaves their left/right mate, Blanchet sign and
Euler degree undetermined.  It therefore refuses the inference from eight
wrong-side intervals to one defect.
