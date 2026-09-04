# Exact exporter for a complete seven-component Kirby diagram

## Scope

`scripts/export_t73_full_handle_diagram.py` is the fail-closed final stage of
the T73 Kirby-data pipeline.  It accepts exactly the stronger coordinate input
described by `audit/t73_full_handle_diagram_input_contract.json`: the five
surviving 2-handle cores, the two dotted 1-handle circles, and one framing
push-off for each 2-handle core.  All twelve curves must be closed rational
polylines in one oriented affine chart.

The executable schema is `data/T73_FULL_HANDLE_DIAGRAM.schema.json`.  In
addition to the original contract it requires the two projection covectors and
the explicit cyclic successor list for each push-off.  These fields remove two
otherwise implicit choices.

This exporter does **not** reconstruct a link from free words or from the old
mixed-crossing railroad ledger.  Its output is valid only after the full
coordinate input exists.

## Exact construction

Let $p_1,p_2\colon\mathbb Q^3\to\mathbb Q$ be the two stored projection
covectors and let $h\colon\mathbb Q^3\to\mathbb Q$ be the height covector.
The exporter checks that the two $p_i$ annihilate the stored projection
direction and that $(p_1,p_2,h)$ is positively oriented relative to the
stored `standard_xyz` orientation.

For projected oriented segments

\[
 a(t)=a_0+t(a_1-a_0),\qquad b(u)=b_0+u(b_1-b_0),
\]

the two-by-two rational linear system $a(t)=b(u)$ is solved with exact
`Fraction` arithmetic.  A regular crossing is retained only when
$0<t,u<1$.  A vertex crossing, overlapping projected segments, a collapsed
projected segment, a triple projected point, or equality of the two heights is
a hard error.  The same check is run on all seven cores and all five
push-offs, so a claimed push-off that meets any stored curve is rejected.

At a crossing the higher branch is `over`.  The sign convention is

\[
 \operatorname{sign}\det\bigl(P(v_{\rm over}),P(v_{\rm under})\bigr),
 \qquad P=(p_1,p_2).
\]

The along-component crossing order is the lexicographic order of exact pairs
`(segment, parameter)`.  If the visits to one component are
$e_0,\ldots,e_{k-1}$, arc label $i$ joins $e_i$ to $e_{i+1}$, cyclically.
At every crossing the PD row uses Spherogram's convention:

* positions 0 and 2 are the incoming and outgoing under-arcs;
* for a positive crossing, positions 3 and 1 are the incoming and outgoing
  over-arcs;
* for a negative crossing, positions 1 and 3 are the incoming and outgoing
  over-arcs.

Consequently every arc label occurs exactly twice, and the structured Gauss
record and the PD record are two serializations of the same computed
half-edge successor graph.

The same construction is also applied to the full twelve-component framed
link (seven cores plus five push-offs).  Its separate PD, successor cycles,
crossing ledger, and twelve-by-twelve pairwise linking matrix make the framing
calculation independently readable instead of retaining only five final
integers.

For distinct oriented components $K_i,K_j$, the exporter computes

\[
 \operatorname{lk}(K_i,K_j)=\frac12
 \sum_{c\in K_i\cap_{\rm proj}K_j}\operatorname{sign}(c).
\]

An odd signed sum is rejected.  The integer coefficient of a 2-handle core
$K$ is computed by the identical formula for $K$ and its stored push-off
$K'$; it is never inferred from blackboard writhe.  The output contains both
the full pairwise linking matrix and the framed five-by-five surgery matrix.

Ordinary PD notation cannot encode a component with no crossings.  The
exporter therefore retains such a component in the authoritative core and
Gauss/cycle records and lists it under `crossingless_components`; the optional
Spherogram exterior check refuses that case rather than silently dropping the
component.

## Independently executable truth example

`scripts/build_t73_full_handle_diagram_example.py` builds seven separated
polygonal Reidemeister-I unknots, all in one rational chart.  The first five
have translated push-offs.  This is a contract example, **not** a proposed T73
diagram.

The committed artifacts are:

* `geometry/examples/seven_component_framed_unlink_input.json`;
* `geometry/examples/seven_component_framed_unlink_export.json`;
* `geometry/examples/seven_component_framed_unlink_open_source_receipt.json`.

The exact export has seven negative self-crossings, seven PD rows, no
crossingless component, zero pairwise linking, and push-off linking $+1$ on
each of the five 2-handles.  Spherogram 2.4.1 independently reads the PD as
seven components and the framed-link PD as twelve components with 42
crossings.  SnapPy 3.3.2 produces a seven-cusped, 36-tetrahedron link
exterior, and Regina 7.4 reconstructs 36 tetrahedra from the undecorated
SnapPy isomorphism signature.  Regina additionally reports a valid,
orientable, connected ideal triangulation with seven boundary components.
The receipt is hash-bound to the exact export.

Rebuild and verify with:

```text
python3 scripts/build_t73_full_handle_diagram_example.py --check
python3 scripts/export_t73_full_handle_diagram.py \
  geometry/examples/seven_component_framed_unlink_input.json \
  --check geometry/examples/seven_component_framed_unlink_export.json
/tmp/t73-topology-tools/bin/python \
  scripts/export_t73_full_handle_diagram.py \
  geometry/examples/seven_component_framed_unlink_input.json \
  --check geometry/examples/seven_component_framed_unlink_export.json \
  --engines-output geometry/examples/seven_component_framed_unlink_open_source_receipt.json
python3 -m unittest tests.test_t73_full_handle_diagram_export -v
```

## First missing T73 coordinate map

`scripts/check_t73_full_handle_diagram_input_gap.py --expect-open` locates the
first gap without trusting status strings.

When `geometry/t73_full_handle_diagram_input.json` is eventually written, the
gap checker will change to `PASS` only if the generic exporter accepts it and
its `provenance` object equals the live SHA values of the AR link and both
cancellation artifacts.  Thus the present negative gate does not permanently
institutionalize an `OPEN` answer.

The first absent datum is a Kirby **presentation** map, schematically

\[
 \kappa_{\rm AR}^{\rm pres}\colon
 \{\text{seam-identified }T^3\!\times I\text{ charts, }t/x\text{ belt charts,
 dual-cell chart}\}
 \dashrightarrow
 \{\text{dotted-circle link data in }S^3\setminus\{\infty\}\cong\mathbb Q^3\}.
\]

The dashed arrow is essential: this is a cut-and-surgery quotient
presentation, not an ambient embedding.  Indeed the pre-cancellation
attaching boundary is \(\#^4(S^1\times S^2)\), and the final boundary is
\(\#^2(S^1\times S^2)\).  By invariance of domain, an embedding of either
closed connected 3-manifold in \(S^3\) would have open-and-closed image and
hence be onto, contradicting their nonzero first homology.  The alternative
to a dotted-circle presentation is therefore an explicit triangulation of
the relevant \(\#^g(S^1\times S^2)\), not an embedding of it into \(S^3\).

The presentation map needs compatible transition maps on overlaps.  It must
carry the cut-open AR cores,
framing ribbons, belt spheres, both boundary edges of every slide band, and
all surgery quotient pairings into one oriented rational Kirby chart.

A complete pre-cancellation snapshot has seven 2-handle cores and **four**
dotted meridians $x,y,z,t$.  The snapshot with two dotted meridians $y,z$ is
necessarily post-cancellation and has five surviving 2-handle cores.  Mixing
seven pre-cancellation cores with only two dotted meridians would not describe
either stage of the handle movie.

This really is the first missing coordinate map:

* `geometry/t73_actual_ar_link.json` stores the $m_i$ cores in
  four-coordinate $T^3\times I$ seam charts;
* the three dual-cell boundaries and band centers live in several
  three-coordinate local charts;
* no transition plus cut/surgery presentation into a common $S^3$ diagram is
  stored.

After that first map, two further explicit surgery traces are required.
`geometry/t73_cancel_t_hcs.json` stores each belt-sphere band **center** and a
target point, but not both band edges, attachment parameters, or the spliced
post-cancellation cyclic polyline.  `geometry/t73_cancel_x_m1.json` likewise
stores 1513 center paths and a reference to the $m_1$ replacement curve, but
not 1513 embedded parallel replacement arcs or the final five closed cores.
Finally the dotted $y,z$ cores and the five transported final push-offs must
be emitted in the same chart.

Until these data are constructed, the old 1958-crossing railroad file cannot
be promoted to an actual T73 PD code: it is missing precisely the geometry
that this exporter recomputes.
