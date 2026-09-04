# Complete selected four-box target template

Date: 2026-09-05

## Constructed target

`scripts/build_t73_selected_canopolis_normal_form.py` now writes a complete
finite target diagram, rather than one record per informal primitive.  It has
four parametrized insertion balls in two disjoint closure balls.  The exact
endpoint counts are

| insertion ball | endpoints |
|---|---:|
| `Y_source` | 88 |
| `Z_target` | 542 |
| `Z_source` | 542 |
| `Y_target` | 88 |

Thus the target contains 1260 boundary endpoints and 630 framed PL arcs.  In
each closure ball there are precisely:

- 88 straight active Y--Z arcs, the two oriented boundary sides of the 44
  product ribbons; and
- 227 boundary-parallel Z--Z arcs, each with two distinct Z endpoints and an
  explicit four-vertex U-shaped rational polyline.

Every endpoint, centerline vertex and positive push-off vertex is stored, and
each arc records its initial/terminal endpoint and listed-vertex orientation.
The two sides of the cyclic `m_2:C_i` to `c1:letter:0` ribbon are primitive
indices 86 and 87.  The common product normal is a small rational vector and
every relative twist is zero.

The exact verifier checks all source IDs, endpoint tables, one-use endpoint
incidence, the 88/227 split on both sides, closure-ball separation, insertion
ball avoidance, all centerline/push-off intersections, the cyclic connector,
and nine hostile mutations.  Its positive verdict is
`PASS_COMPLETE_TARGET_TEMPLATE`.

## What this does not prove

The target is an abstract canopolis template.  It is not the endpoint
matching of the selected source coefficient exterior.  The independently
constructed source has the same per-sphere endpoint cardinalities but has
the active transition table

| source sphere pair | intervals |
|---|---:|
| `Y_minus--Z_plus` | 84 |
| `Y_plus--Z_minus` | 84 |
| `Y_minus--Z_minus` | 4 |
| `Y_plus--Z_plus` | 4 |

The last eight intervals are wrong-side connectors for a literal split into
the proposed two representable closure balls.  A relative ambient isotopy
fixing the four insertion spheres preserves the endpoint matching, not only
the four endpoint counts.  Consequently the literal source-to-target split
is refuted for the saved incidence; it is no longer merely an unconstructed
isotopy.

Pivotal duality can change which boundary is read as input or output, but it
does not reconnect fixed endpoints.  Cross-pairing the eight intervals would
require four explicit reconnection cobordisms.  No saddle movie, Blanchet
sign, or Euler/quantum degree for those reconnections has been constructed.
Moreover pivotal mates preserve the 176 active endpoints, whereas the
external one-cup target `P86 -> P88` has 174.  The one defect comes from the
separately selected external cup, not from the eight wrong-side intervals.

## Grading consequence

The arithmetic `227 - 4 = 223` remains the intrinsic ledger of the
counterfactual literal two-representable split.  Since the saved source does
not have that relative split, this arithmetic does not establish the degree
of the actual coefficient comparison.  Degree-zero pivotal retyping cannot
restore the historical value 494.  An actual proof of C must instead supply
the full z-coend natural transformation and any required reconnection cells,
then derive the grading from those cells.
