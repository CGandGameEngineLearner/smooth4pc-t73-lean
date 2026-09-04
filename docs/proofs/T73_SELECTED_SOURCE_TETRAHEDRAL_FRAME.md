# Selected-source tetrahedral frame

## Scope

`scripts/build_t73_selected_source_tetrahedral_frame.py` attempts to convert
the saved canonical source exterior into a single constrained tetrahedral
complex. Its
ambient region is the cube `[-20,20]^3` with the interiors of the four saved
insertion cubes removed.  Consequently its required boundary is exactly five
triangulated 2-spheres: the outer sphere and `y_left`, `y_right`, `z_left`,
`z_right`.

The complete 630-ribbon frame is not yet constructed. A saved ten-ribbon
prefix proves the complete PLC/verification format on a nontrivial subfamily.
This construction does **not** assert the outstanding AR-relative isotopy to
the defect-aware coend target.  The saved flag
`actual_ar_relative_isotopy_proved` remains false.  The artifact is an initial
source frame on which such a movie could later be recorded.

## PLC supplied to TetGen

The constructor uses the open-source TetGen 0.8.4 Python wrapper and Triangle
for the planar insertion faces.  The input piecewise-linear complex contains:

1. the triangulated outer cube and all four triangulated insertion cubes;
2. every one of the 630 saved source centrelines as two required segments;
3. every positive framing push-off as two required segments;
4. the four `ruled_ribbon_triangles` saved for each interval, hence 2,520
   required internal facets; and
5. all core--push endpoint edges as constrained edges of the appropriate
   insertion face.

TetGen is run with exact predicates enabled and vertex/facet merging disabled.
Facet bisection is permitted. Unique input markers recover every subdivided
boundary or ribbon face; the output edge graph recovers each subdivided core
and push-off segment by exact ordered parameters. Adjacent marked facets must
induce identical subdivisions on their common edge. The verifier then proves
that the subfaces cover the original rational face and that every recovered
path reduces to the saved rational polyline.

## Binary64 conditioning and rational restoration

Independent conversion of rational points `p` and `p+n` to binary64 can break
an exact repeated-translation identity.  TetGen may then regard four exactly
coplanar rational points as a non-coplanar quadruple and output a tetrahedron
that becomes flat when the rationals are restored.  This failure was observed
and is rejected.

The constructor therefore creates a common dyadic *meshing embedding*:

- core coordinates are rounded to the grid `2^-40 Z^3`;
- every saved framing displacement is an integral multiple of the common
  dyadic normal unit `2^-20`; and
- each push vertex is formed from its already-rounded core vertex plus that
  exact dyadic displacement.

The final artifact does not silently replace the source geometry by this
conditioning embedding.  Once TetGen returns its incidence data, all PLC
vertices are restored to the authoritative rationals in
`geometry/t73_selected_source_exterior.json`.  Any free Steiner vertex is
stored as its exact dyadic binary64 value.

## Independent acceptance gate

`scripts/verify_t73_selected_source_tetrahedral_frame.py` uses no TetGen code.
It checks:

- the embedded payload hash and exact source-exterior hash;
- a connected combinatorial 3-manifold whose vertex links are spheres or
  disks;
- exactly five named boundary components, each a connected triangulated
  2-sphere;
- 630 pairwise vertex-disjoint embedded edge paths and 630 pairwise
  vertex-disjoint triangle-subcomplex disks;
- exact `88,88,542,542` endpoint incidence and complete owner/copy/source
  provenance;
- equality of every reduced core path, push-off path, and four ribbon
  triangles with the saved rational source data;
- nonzero, consistent exact rational orientation of every tetrahedron; and
- exact total tetrahedral volume
  `40^3 - 4*2^3 = 63968`.

Thus a floating-point mesher cannot earn `PASS` merely by returning an index
array.  A lost constraint, a stale source, a zero-volume simplex, an orientation
flip after rational restoration, a missing insertion ball, or a volume gap all
fail closed.

## Reproduction

The optional topology environment used during construction contains TetGen,
NumPy, and Triangle.  A one-ribbon smoke test is:

```text
/tmp/t73-topology-tools/bin/python \
  scripts/build_t73_selected_source_tetrahedral_frame.py --limit 1
```

The committed prefix is produced and independently checked with:

```text
/tmp/t73-topology-tools/bin/python \
  scripts/build_t73_selected_source_tetrahedral_frame.py --limit 10 --write \
  --output geometry/examples/t73_selected_source_tetrahedral_prefix10.json
python3 scripts/verify_t73_selected_source_tetrahedral_frame.py \
  geometry/examples/t73_selected_source_tetrahedral_prefix10.json
```

It has five spherical boundary components, ten core paths, ten ribbon disks,
101 vertices, 858 tetrahedra, and exact exterior volume 63968.

## Monolithic resource obstruction

The one- and ten-ribbon prefixes pass. A 50-ribbon run remained CPU-bound for
over six minutes, and a 20-ribbon run reached 14.6 GB resident memory in about
40 seconds, both before producing a mesh. Allowing TetGen facet subdivision
did not remove the 20-ribbon memory explosion. Those probes were terminated
and no partial output was accepted.

The public constructor therefore rejects any monolithic request above ten
ribbons unless `--unsafe-monolithic` is explicitly supplied. That switch is
only for a resource-audited experiment; it does not change the verifier or
permit prefix data at the complete artifact path. The full solution now
requires a partitioned construction with certified matching boundary
triangulations and an independently checked simplicial gluing map.
