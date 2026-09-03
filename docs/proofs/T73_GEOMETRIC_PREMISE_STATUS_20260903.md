# Geometric premise status, 3 September 2026

P0 and C are discharged for the explicit Johnson replacement. S remains Open
and is not treated as a theorem. No counterexample is claimed.

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
- **P0d (finite fact):** 93-bit Johnson `alpha_ij` search, GAP free basis, 44 y-channels, public 11340-letter word match

## P0 (Johnson replacement)

**Status: PASS** for the explicit Johnson replacement presentation.

**Object that exists.** `scripts/certify_t73_johnson_ar_bridge.py` builds a 48-tetrahedron Freudenthal triangulation of Johnson's period-one torus (scaled period 2) and the affine map `S(u)=2u-(1/2,1/2,1/2)` as a simplex-by-simplex map onto a triangulation of the period-two torus. Every 1-simplex of the Johnson spines `K1` and `K2` is carried onto the AR coordinate spines through `Q` and `Qbar`.

`scripts/certify_t73_spine_star_handlebodies.py` reuses the committed 384-tetrahedron Freudenthal torus from `scripts/build_t73_ar_torus.py`. Closed vertex-stars of `L_B` and `L_D` have 156 tetrahedra each. Discrete Voronoi assignment of each tetrahedron by squared torus distance of its barycenter to the two spines yields a Heegaard pair: **192+192** tetrahedra, Euler characteristic `-2`, a 96-triangle genus-three interface, `Q` interior, and the protected PL cube inside the `L_B` cell. The same assignment on the period-4 Johnson mesh is carried onto that pair by `T(v)=v-(1,1,1)`.

`scripts/build_t73_p0_reconstruction_input.py` places the 44 Johnson six-sweep strands as height-monotone polylines in a triangulated cube (certified 3-ball), binds each strand to a Johnson y-wicket, and supplies two local product 1/2-handle cancellation movies of geometric intersection 1. `scripts/reconstruct_t73_p0.py` accepts that input and recovers the public 11340-letter word. Uniqueness of regular neighborhoods is not used.

The cube is a certified 3-ball containing the six-sweep strands, not a separately certified subset `B ⊂ ∂W_2` of the 4-manifold. The cancellation movies are local intersection-1 models in `R^3`, plus the word identities `psi(x)=z` and `m1=z x^{-1}`.

## C (Johnson replacement collar)

**Status: PASS** for the explicit Johnson replacement collar.

**Object that exists.** `scripts/certify_t73_c1_cut_link.py` rebuilds the P0 reconstruction strands, runs `reconstruct_t73_p0.py`'s `verify_ball`, `verify_strands` and `strand_points_in_ball`, and takes each strand as a y-side. The z-side is the certified product-normal translate. The pairing recovered from those PL sides is the Johnson y-then-z pairing, with 227 leftover z-circles off the P0 cube.

`scripts/certify_t73_c2_comparison.py` records the 44 product movies as H, two explicit support cubes disjoint from the P0 ball, cores and leftover circles, the selected cable counts `(44,227)`, and the Lean `coefficientHH0Equiv` reduction.

This is not an isotopy of a cut link in `∂W_2`, and it is not a chain-level Blanchet--Khovanov complex of the actual W2 cut.

## Remaining holes (S)

| Premise | Status | Obstruction |
|---|---|---|
| Euclidean/mapping-torus identification | Open remark | Uniqueness of regular neighborhoods is not used; the Euclidean Voronoi surface is not a subcomplex |
| P0d linking | Open | No reduced PD or normal-field movie after the collar |
| S geometry | Open | PL model of `#^3(S^1 x S^2)` as S^3 with three 1-handles contains the P0 cube; kernel unknots `r_xy`, `r_yz`, `r_zx` and 32 Nielsen generator movies miss that cube, but they are not a B-fixing move list in `Q=∂W2 \ Int B0`; closed HJ Thm 5.3 is not used as “B is fixed”; `detector_fixed` is false |
| S endpoint | Open | Replacement belt-sphere foams exist; `actual_standard_sphere_endpoint_foam_computed=false` |
| Counterexample | Open | Lean implication only; no `ExternalGeometry` instance |

`audit/t73_premise_audit.json` records `overall=OPEN`, P0 and C `proved: true`, and `proved: false` on S. `counterexample_claim_proved` remains false.

Current certificate digests:

- P0 `545F5CE8F53F0A9E6D90C516D9C35AB7CA47AA1AD8C2D9820E253E2273769A7C`
- C `0D7D1CAC871D85C4F909C2B31CC7F01809C2558D6FA0655DE9034C4B1C28E7A3`
- C1 `843A80227D8B062F6451013F53D8A5FA0405409548A48854CADE3FF1E5C3BD3A`
- C2 `87BA1649CB27CCDB52E2D7092832C63548C0F3B27ACBFC570F3EF6949EDC1D49`
- S `94DDC2E72EA0068D83EAC9C8128BE17363E3A658B30763C9D7804AE079F78996`
- S spheres `79946FE07B1EBF0E9C54C818D900153FA32C3DE7FAEDAB5EAD6D4CF47B926E94`
- P0a pair `C1877B7696E7A44B5DEBE06BDCAC6CA712A83E49A07973107B7F1C4A728D4435`
- B44 `7C2D2F792C2672221A76CAF08A71F560AF0CB7654B4D537C00FAD00B16EFA187`
