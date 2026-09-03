# Geometric premise status, 3 September 2026

Work stopped at **P0a**. Later premises are Open and are not treated as theorems.

## Closed (finite or already-proved algebra)

These are not re-litigated.

- `det A = det(A-I) = 1`
- Euler characteristic `1-2+5-3+1=2`
- degree `-44+227+315-4=494`
- Theorem A: if the external geometry exists, a nonzero class in quantum degree 494 obstructs a diffeomorphism to `S^4`
- Lean proves only that implication. `Smooth4PC.T73External.ExternalGeometry` / `CSExternalGeometry` have no inhabitants
- Frozen public cubic and Lean `computedCubic_eq_2624`: `D_3=2624`. The retired mixed-index value `-59072` is not used
- Public Burau cubic of the frozen Artin word is nonzero
- Nielsen 42-channel route is false; inner conjugation `x^{-1}` is whiskers, not an embedded collar
- Words and framings do not determine `lk(m2, r_yz)`
- **P0d (finite fact only):** 93-bit Johnson `alpha_ij` search, GAP free basis, 44 y-channels, public 11340-letter word match

## P0a (first failure)

**Status: Open.**

**Object that exists.** `scripts/certify_t73_johnson_ar_bridge.py` builds a 48-tetrahedron Freudenthal triangulation of Johnson's period-one torus (scaled period 2) and the affine map `S(u)=2u-(1/2,1/2,1/2)` as a simplex-by-simplex map onto the period-two AR torus. Every 1-simplex of the Johnson spines `K1` and `K2` is carried onto the AR coordinate spines through `Q` and `Qbar`. The linear part is `2I`, so Johnson's Euclidean Voronoi handlebodies map onto Voronoi cells of those image spines. The recorded protected metric ball of radius `1/196104` about `0` maps to the ball of radius `2/196104` about `Q`. A PL core cube of half-side `1/400000` is mapped vertexwise.

**Obstruction.** Aitchison--Rubinstein's mapping-torus handlebodies are not present as a certified PL neighborhood of those spines. Uniqueness of regular neighborhoods is not used. The Euclidean Voronoi surface is piecewise-quadric and is not a subcomplex of the triangulation. Therefore there is no homeomorphism of the complete Heegaard pairs as certified complexes.

`scripts/reconstruct_t73_p0.py` still has no parseable geometric input.

## Remaining holes (not attempted; P0a failed first)

| Premise | Status | Obstruction |
|---|---|---|
| P0b | Open | Word identities `psi(x)=z` and `m1=z x^{-1}` only; no framed Kirby movies |
| P0c | Open | 44 points in `D^2` are not polylines in an embedded ball `B subset ∂W2` |
| P0d linking | Open | No reduced PD or normal-field movie after an actual collar |
| C1 | Open | No isotopy of the actual cut link; 44/227 are word counts |
| C2 | Open | Not quoted: C1 does not exist |
| S geometry | Open | No B-fixing move list in `Q=∂W2 \ Int B0`; closed HJ Thm 5.3 is not used as “B is fixed”; `detector_fixed` is false |
| S endpoint | Open | `actual_standard_sphere_endpoint_foam_computed=false`; no movies |
| Counterexample | Open | Lean implication only; no `ExternalGeometry` instance |

`audit/t73_premise_audit.json` records `overall=OPEN` and `proved: false` on every candidate-specific geometric item.

Current certificate digests:

- P0 `FF653CE41D102D1770E967417FDF8D4C5857E253C275BBB9381887E29D9BAC96`
- C `94F4D5DE9ED2342B32EDE3FEEA69F3EBE9BFDC5D5FD4432A9BD166FCBD46BC4C`
- S `A5DECACF9C443D353A2E10E547069CE86CA3F1A33E04D408170634CCB526AC2D`

Acceptance tests 1--6 all fail. Test 7 regenerated the premise audit only as Open. Lean still has no `sorry` and no `ExternalGeometry` instance.
