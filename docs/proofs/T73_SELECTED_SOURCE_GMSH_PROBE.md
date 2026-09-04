# Gmsh conformal-mesh probe for the selected source

Date: 2026-09-05

## Purpose and scope

`scripts/probe_t73_selected_source_gmsh.py` tests Gmsh as an alternative to
the monolithic TetGen PLC route.  The outer volume is the cube
`[-20,20]^3` with the four insertion cubes removed.  For each selected route,
its four saved ruled-ribbon triangles are added as internal OCC plane
surfaces, and all ribbon edges are embedded in the volume.

The prefix-20 receipt is a resource/CAD-incidence probe and contains counts
only. Separately, prefix 10 is exported as a complete tetrahedral frame with
all nodes, tetrahedra and physical subcomplex data. The complete 630-ribbon
frame remains `OPEN`.

## Boundary-incidence correction

The first one-ribbon run failed with a precise HXT error: a ribbon endpoint
vertex intersected an unrefined insertion-ball facet.  Merely embedding the
internal ribbon surface in the volume was insufficient because its transverse
endpoint edge lies in the hole boundary.

The corrected construction first identifies the unique OCC boundary surface
containing each initial and terminal core--push connector and embeds that
curve in the boundary surface.  It then embeds all ribbon surfaces and curves
in the volume.  This mirrors Gmsh's documented bottom-up conformity rule:
internal curves and surfaces must be explicitly embedded in higher-dimensional
entities ([Gmsh tutorial 15 and mesh documentation](https://gmsh.info/doc/texinfo/gmsh.html)).

## Observed prefixes

Using Gmsh 4.15.2 with the HXT three-dimensional algorithm:

| route prefix | ribbon surfaces | boundary connectors | nodes | tetrahedra | result |
|---:|---:|---:|---:|---:|---|
| 1 | 4 | 2 | 1746 | 9009 | pass |
| 10 | 40 | 20 | 2664 | 14599 | pass |
| 20 | 80 | 40 | 4134 | 23725 | pass |

The prefix-20 receipt is saved as
`audit/t73_selected_source_gmsh_prefix20.json` and is bound to source SHA
`0B5D34B8581E6208D573C1934CE8BE225BAA874AE1120ED6A64027DD007BF741`.
`scripts/verify_t73_selected_source_gmsh_probe.py` checks its hash, source
binding, counts and non-completion scope, and rejects count/status mutations.

The stronger artifact
`geometry/examples/t73_selected_source_gmsh_prefix10_frame.json` contains 2664
restored rational vertices and 14599 tetrahedra. Gmsh curve nodes are restored
with one exact parameter on each saved rational segment; ribbon-surface nodes
are restored with exact barycentric coordinates on their saved carrier
triangle; boundary nodes are restored to the exact axis-aligned face. The
independent, Gmsh-free frame verifier checks five spherical boundaries, the
ten subdivided core and push paths, ten ribbon disks, consistent nonzero
tetrahedron orientation and exact volume 63968. Its verdict is
`PASS_PREFIX_ONLY`.

The full verification run is persisted in
`audit/t73_selected_source_gmsh_prefix10_frame_verification.json`.  This
receipt binds the frame byte hash, embedded payload hash, source hash,
verifier path and all verified counts.  Routine bundle checks validate those
bindings without rerunning the 24-second vertex-link computation; regenerating
the receipt with `--write` always reruns the complete independent verifier.

A prefix-50 attempt was interrupted by the surrounding execution boundary
before it returned a result.  It is not recorded as either success or failure.
The complete export of prefix 20 was likewise interrupted before a file was
written; only its counts-only resource receipt is retained.

## Remaining work

The export and restoration path is therefore implemented. To turn it into
the complete frame constructor, it must scale to all 630 ribbons while the
independent verifier reconstructs:

1. exactly five spherical boundary components;
2. every subdivided core and push-off edge path;
3. every subdivided ribbon disk and its exact saved carrier triangles;
4. rational nonzero tetrahedral orientations and total volume 63968.

Only that exported and independently accepted object can close the full
tetrahedral-frame gate.
