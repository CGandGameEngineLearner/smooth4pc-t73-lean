# Trace-73 correction and closure research note (2026-09-02)

## Purpose

This note supersedes the unconditional interpretation recorded in commit
`89a4d0e`.  That commit contains useful finite certificates, but its paper
promotes several candidate-level identifications to theorems without
constructing the required geometric and functorial maps.  It is a research
milestone, not a proof of a counterexample to the smooth four-dimensional
Poincare conjecture.

The controlling Lean statement remains

```text
ExternalGeometry -> CSExternalGeometry ->
IsHomotopySphere candidate /\ not Diffeomorphic candidate S4.
```

No inhabitant of either external structure has been constructed in Lean.

## Results that survive the correction

1. The matrix and determinant calculations, including
   `det(A) = det(A-I) = 1`.
2. The frozen 88-dimensional truncated Burau evaluation `-59072` and its
   quantum-degree bookkeeping.
3. Regeneration of the compact word, the 252 six-sweep rows, and the public
   44- and 88-strand braid words.
4. The full-entry order-three check and the exact Artin--Magnus certificate;
   with Darne's pure-braid Andreadakis theorem these establish the relevant
   lower-central-series statement for the public braid and its group-theoretic
   cablings.
5. The integral owner lifts, the unimodular 32-step Nielsen ledger, the
   Frobenius/core-counit algebra, and the conditional Lean nonvanishing chain.
6. The general MWW four-handle theorem, the computation of the `S^4` module,
   and the Cappell--Shaneson determinant criterion, when their
   candidate-identification hypotheses are supplied.

These facts are substantial partial evidence.  None by itself identifies the
finite scalar with a class in the MWW module of the proposed four-manifold.

## Corrected gap verdicts

Only `DISCHARGED`, `PARTIAL`, and `OPEN` are used.

| Item | Verdict | Missing candidate-level object |
|---|---|---|
| P0: compact/frozen diagram is the AR handlebody for `Sigma_A^0` | **OPEN** | An embedded framed Kirby presentation and a labelled ambient-isotopy/Kirby-move ledger from the AR construction.  Word equality, exponent sums, and a named product normal do not determine this object. |
| P1/C: Burau cubic is the MWW evaluation | **OPEN** | The actual product motion `B_act`, a single coordinate transport `P` acting simultaneously on `W,u,ell`, and a natural map from the MWW coefficient trace to the specified completed qHH0/Chern summand, including grading and completion compatibility. |
| P2/E7: owner lifts are actual three-handle spheres | **OPEN** | The actual two-handlebody boundary, its required decomposition/irreducibility and handle count, and three embedded disjoint framed spheres realizing the recorded spherical basis. |
| P2/E10/S: detector descends through the actual three-handle maps | **OPEN** | Candidate-specific MWW hemisphere/foam maps in the same coordinates, including pivotal adapters, signs, normal-level transport, and the six simultaneous identities on `W,u,ell`. |
| P3/E11--E13 | **PARTIAL** | The general theorems are available.  Their use for this candidate still depends on P0 and on identifying the quotients and grading in P1/P2. |

The repository itself independently confirms the two central open joins:
`verify_t73_compact_hattori_binding.py` emits
`required_simultaneous_transport.status = OPEN`, and
`generate_t73_stable_sphere_movies.py` emits
`actual_mww_transport_status = OPEN`.

## Why the earlier closure failed

1. A relator/word ledger was treated as an embedded framed Kirby equivalence.
   The implication is invalid without the missing isotopy or Kirby moves.
2. General trace and tangle functoriality was invoked before constructing the
   candidate-specific functorial arrow.  Functoriality transports a map; it
   does not create the missing map or identify its coordinates.
3. A unimodular homology basis and Nielsen moves were treated as embedded,
   pairwise-disjoint attaching spheres.  Homology data does not provide those
   embeddings or verify the hypotheses of the sphere-replacement theorem.
4. The exact `Gamma_3` certificate proves cubic order, not Hattori/MWW
   naturality or descent.

## Closure programme and falsification gates

The next proof attempt is deliberately map-first.

### Gate G0 (P0)

Construct a machine-readable framed-link object directly from the public AR
product-annulus construction.  Every component must carry an embedding model,
orientation, framing trivialization, and labels through each cancellation.
The compact words are accepted only as projections of that object.  G0 passes
only after a public isotopy/Kirby ledger has independently checkable local
moves and ends at the detector diagram.  If the endpoint requires the absent
historical PD, P0 remains open and the exact absent object/digest stays listed.

### Gate G1 (P1/C)

Define the actual cut coefficient bimodule before choosing endpoint
coordinates.  Extract `B_act` from the same product isotopy as G0, compute one
transport `P`, and verify all three equations

```text
W_actual = P^-1 W_public P
u_actual = P^-1 u_public
ell_actual = ell_public P.
```

Then construct the categorical comparison from the cited coefficient trace
to the qHH0/Chern target and prove that base change `q -> 1+h`, grading shifts,
and division by `h^3` commute.  A local R-matrix match is only one lemma in
this gate.

### Gate G2 (P2/S)

Starting from the G0 two-handlebody, give explicit sphere diagrams or movies,
verify embeddedness, disjointness, framings, the boundary and handle-count
hypotheses, and bind each hemisphere movie to the MWW map.  Compute the
induced endpoint transports and check them simultaneously on `W,u,ell`.
Only then may the core-counit identities be applied.

### Gate G3 (P3 and final join)

Instantiate the precise MWW bidegree and rational base-change statements and
the CS identification from G0.  Finally construct the two Lean external
structures from the discharged lemmas.  Until G0--G3 pass, the paper theorem
is conditional.

## Submission rule

The title, abstract, main theorem, conclusion, README, and generated PDF must
say “conditional” or “candidate pending geometric identification” while any
gate above is open.  No future finite computation may change a gate verdict
unless it constructs the missing candidate-level object and supplies a public
independent check.
