# Geometric premise status, 3 September 2026

P0, C, S, the MWW four-handle layer and the E13 CS handle picture are
discharged for the explicit Johnson replacement. Lean ExternalGeometry
remains uninhabited. The empty-link control `S4ReductionData` is inhabited.
No counterexample is claimed.

## Closed (finite or already-proved algebra)

These are not re-litigated.

- `det A = det(A-I) = 1`
- Euler characteristic `1-2+5-3+1=2`
- degree `-44+227+315-4=494`
- Theorem A: if the external geometry exists, a nonzero class in quantum degree 494 obstructs a diffeomorphism to `S^4`
- Lean proves only that implication. `Smooth4PC.T73External.ExternalGeometry` / `CSExternalGeometry` have no candidate inhabitants. `T73S4Inhabitant.lean` inhabits empty-link `S4ReductionData`
- Frozen public cubic and Lean `computedCubic_eq_2624`: `D_3=2624`. The retired mixed-index value `-59072` is not used
- Public Burau cubic of the frozen Artin word is nonzero
- Nielsen 42-channel route is false; inner conjugation `x^{-1}` is whiskers, not an embedded collar
- Words and framings do not determine `lk(m2, r_yz)`; the railroad PD does
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

## S (Johnson replacement reversed 1-handle picture)

**Status: PASS** for the explicit Johnson replacement reversed 1-handle picture.

**Object that exists.** `scripts/certify_t73_s_standard_spheres.py` places three belt cubes in the far positive octant of the P0 chart.  Each cube interior is recorded as a 4-dimensional 1-handle core, not a 3-ball retained in the chart.  Dual loops meet the owner belt sphere once through `I×{p}` in `S^2×I` and return by a chart L-path that misses every belt cube, the P0 ball, the C1 leftover z-circles and the C2 supports.  Endpoint foams are the `b=0` counit of MWW Example 3.8.  HJ Theorem 5.3 is used only with Lemma Ssystem for kernel invariance, not to fix `B`.  Lemmas 5.5 and 5.7 are not invoked.

This is not an identification with historical `∂W_2`, and it is not a triangulated 4-dimensional W2 lasagna movie.

## P3 (Johnson replacement four-handle picture)

**Status: PASS** for the MWW four-handle layer of the Johnson replacement picture; **PASS** for the homotopy-sphere identification of the constructed CS handle picture.

**Object that exists.** `scripts/certify_t73_p3_four_handle.py` takes the three reversed 1-handles of S, records a 1-3 cancellation along each belt sphere (dual-loop intersection 1, chart return missing every belt cube), and restores an S^3 containing the P0 cube. A PL 4-ball `I^4` of Euler characteristic 1 is attached along that S^3. MWW Proposition 3.4 supplies the empty-link isomorphism onto the closed picture `X_J`. MWW Corollary 3.5 kills the standard `S^4` summand in quantum degree 494. The Lean matrix is replayed: `det A = det(A-I) = 1`.

`scripts/certify_t73_e12_s4.py` computes the empty-link Khovanov complex over Q (rank 1 at quantum degree 0, rank 0 at 494) and glues two copies of the P3 `I^4` along `S^3` to a PL `S^4` of Euler characteristic 2. Lean `T73S4Inhabitant.lean` inhabits `S4ReductionData` on the `EmptyKhQ` control universe, not on the Johnson candidate.

This is not a triangulation of a 4-dimensional `W3`. The P3 certificate itself does not claim `X_J ≅ Σ_A^0`.

**CS handle picture.** `scripts/certify_t73_e13_close.py` constructs a PL automorphism `psi` from 93 3-cell-supported Johnson shears, identity on the protected ball, with `psi_*=A`; the five surviving attaching words as a railroad PL link; a labelled reduced PD with `lk(m2,r_yz)=0`; a bijection of the selected y-channels to the 44 P0 wickets; and a staged Kirby pipeline through C, railroad 1-3, extra S 1-3 pairs, and P3 `I^4`. Lean `CSTopologyData` remains uninhabited.

## Remaining holes

| Premise | Status | Obstruction |
|---|---|---|
| Euclidean/mapping-torus identification | Open remark | Uniqueness of regular neighborhoods is not used; the Euclidean Voronoi surface is not a subcomplex |
| P0d linking | **PASS** | Railroad PD `audit/t73_reduced_link_pd.json`; `lk(m2,r_yz)=0`; Lean `linkingM2Ryz_eq_zero`; paper Lemma P0d-link |
| C3 | Unused | Firewall only; S uses Sendpoint, not C naturality |
| P2/E7 | Unused | Closed HJ 5.3 is not used as “B is fixed” |
| S geometry | **PASS** | Johnson replacement reversed 1-handle picture |
| S endpoint | **PASS** | b=0 foams by MWW Example 3.8 |
| P3/E11--E12 | **PASS** | Four-handle picture `X_J` and MWW 3.5 about `S^4` |
| P3/E13 identification | **PASS** | Constructed CS handle picture identifies `X_J` with `Σ_A^0`; Lean `CSTopologyData` uninhabited |
| Counterexample | Open | Lean implication only; no candidate `ExternalGeometry` instance |

`audit/t73_premise_audit.json` records `overall=OPEN`, P0, C, S, P3/E11, P3/E12 and P3/E13 `proved: true`. `counterexample_claim_proved` remains false.

Current certificate digests:

- P0 `545F5CE8F53F0A9E6D90C516D9C35AB7CA47AA1AD8C2D9820E253E2273769A7C`
- C `0D7D1CAC871D85C4F909C2B31CC7F01809C2558D6FA0655DE9034C4B1C28E7A3`
- C1 `843A80227D8B062F6451013F53D8A5FA0405409548A48854CADE3FF1E5C3BD3A`
- C2 `87BA1649CB27CCDB52E2D7092832C63548C0F3B27ACBFC570F3EF6949EDC1D49`
- S `72A1AFA6BA914A4DA402CFDC9441C8255D903FFA4B3674043991C42B219A2D74`
- S spheres `F3DC5242984F6D56C2D67F16AC8D8996DE40CC74B2BC1BB677963E8298398D2C`
- P3 `B9ED5F7122D69D623F179089EE76B95468EA481863F04C270227E251EE07C7B2`
- E13 CS object `F497862B2E116D2993C721FB92979A0AD45ACA9E69863AF6B6DD3B910C859F0F`
- E13 close `42309427FB78FCFD3208E7F9537C2C7B2B3AFF5484D9E373A69336ABB856B00F`
- E12 S^4 reduction `E7EB5367D63B0D590F850CFAF8878BFBE9094AB98669AD2FD5384E6CD4885069`
- P0a pair `C1877B7696E7A44B5DEBE06BDCAC6CA712A83E49A07973107B7F1C4A728D4435`
- B44 `7C2D2F792C2672221A76CAF08A71F560AF0CB7654B4D537C00FAD00B16EFA187`
