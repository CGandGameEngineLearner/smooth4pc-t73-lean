# Complete selected source coefficient exterior

Date: 2026-09-05

## Constructed data

The artifact geometry/t73_selected_source_exterior.json is generated from the
actual reduced event lists for m2 and r_xy, not from word hashes. It contains
four oriented cable-component cycles:

- m2 negative and positive copies, with 311 events each;
- r_xy negative and positive copies, with 4 events each.

The positive copy uses the reduced cyclic order and the negative copy uses
the reversed order with every event orientation reversed. For every event the
artifact records owner, cable sign, traversal index, original event index,
source ID, handle, base and effective orientations, entry sphere, exit sphere,
and endpoint IDs.

The four parametrized insertion spheres carry:

| sphere | endpoints |
|---|---:|
| Y_minus | 88 |
| Y_plus | 88 |
| Z_minus | 542 |
| Z_plus | 542 |

Each cabled passage has one endpoint on each side of its cut handle. Thus the
headline passage counts are 88 y and 542 z, while the complete boundary point
set has 1260 points.

For every cable component, the exit endpoint of each event is matched to the
entry endpoint of the next event in its oriented cyclic order. This gives 630
exterior intervals and exactly four cyclic seams. The positive m2 seam is

    m_2:C_i -> c1:letter:0,

and the negative m2 seam is its orientation reverse.

For either cable sign, the 315 intervals split combinatorially as 88
cross-handle y--z intervals and 227 z--z residual intervals. This corrects the
earlier target count 44+227: each of the 44 product ribbons has two oriented
boundary sides, so a closure sees 88 active intervals.

## Rational representative

The insertion spheres are boundaries of four disjoint rational cubes inside a
larger cube. Distinct rational grids place all 1260 endpoints on designated
faces. Every matched interval is represented by a two-segment rational
polyline with a private bend. The generator chooses bends successively and
rejects any segment meeting an insertion-ball interior or any previously
chosen segment.

The endpoint framing is the same small rational product normal on all four
spheres. A constant translation of a bent V-shaped route can intersect the
original route, so the implementation does not make that false assumption.
Instead it searches for a rational interior normal at each bend while keeping
the endpoint normals fixed. The resulting pushed-off polyline is checked
against every centre route and every earlier push-off. Each interval also
saves the four rational triangles of the ruled strip between core and
push-off, together with its complete boundary. The common endpoint normal is
the dyadic value \(2^{-20}\) in the product direction and the maximum
vertexwise \(L^1\) width is \(23/2^{18}\). Candidate centre routes are now
accepted only when every new segment stays at exact distance greater than
\(10^{-3}\) from all earlier routes. This avoids numerically acute PLC data
while retaining a rigorous tubular margin.

An exact global clearance certificate computes the minimum squared distance
between centre segments belonging to different intervals and the maximum
vertexwise \(L^1\) ribbon width. It verifies
\[
d_{\min}^2>(2w_{\max})^2,
\]
which proves that ruled ribbons belonging to distinct intervals are
disjoint. Thus all 2520 rational ribbon triangles are saved; incorporating
them as triangle subcomplexes of a common ambient tetrahedralization remains
the next simplicial step.

The verifier recomputes every event orientation and side, proves that each
entry and exit endpoint is used exactly once, checks all cyclic seams, insertion
faces, rational routes, framing push-offs, ruled triangles and the exact
clearance bound. Nine mutations fail.

## Exact scope

This is a complete canonical representative of the source endpoint incidence
and exterior matching determined by the reduced event cycles. It is not yet a
proof that the actual AR coefficient exterior is relatively framed-isotopic
to this representative. The artifact records this by
actual_ar_relative_isotopy_proved=false.

It also does not produce a single P86-to-P88 Hom target. Passing from four
insertion spheres with 1260 points to a morphism with 86+88 external points is
not an ambient isotopy:

1. the 1084 z-sphere endpoints must be glued to the arbitrary z insertion
   objects and evaluated through the z coend;
2. two of the 176 y-sphere endpoints are organized by the selected cup, leaving
   the 86-to-88 defect;
3. every pivotal turn and its grading must be recorded.

An ambient isotopy preserves boundary components and endpoint cardinalities,
so it cannot itself perform these operations. The required next artifact is a
boundary-parametrized canopolis gluing/currying operation, with separate
topological cells for the z coend and the one-cup pivotal turn. Its Euler and
framing degree must be computed rather than folded into the Hom normalization.
