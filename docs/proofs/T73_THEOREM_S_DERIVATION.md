# Theorem S: decomposition-independent sphere closure

**Status:** `OPEN -- PROPOSED CONSEQUENCE OF C PLUS CANDIDATE SPHERE MAPS`

> Correction.  A unimodular owner lattice and a formal Nielsen program do not
> construct embedded disjoint framed spheres in the actual two-handlebody
> boundary.  The whole-surface argument below also presupposes the actual MWW
> hemisphere maps, pivotal adapters, foam signs and simultaneous endpoint
> transports.  General strict functoriality does not create these maps.

## Statement

Assume the statewise comparison maps and rows from Theorem C commute with
MWW beta/psi maps.  For each of the three compact sphere classes, the MWW
undotted sphere map is killed by the target row and the once-dotted sphere map
pulls the target row back to the source row.  The conclusion is independent
of a decomposition into sphere slides, bands and pivotal adapters.

## Embedded sphere system

The compact Kirby boundary map has kernel basis
`(rxy,ryz,rzx)`.  The unique owner lifts are

\[
(0,0,-1311,8608,-1),\quad
(0,0,-189,1241,0),\quad
(0,0,41,-269,1).
\]

The 32-step Nielsen ledger realizes their unimodular coordinate matrix by
permutations, orientation reversals and sphere slides of the standard
complete sphere system in `#^3(S^1 x S^2)`.  Every move preserves embeddedness,
normal framing and pairwise disjointness.  Horvat--Jab\l{}onowski's theorem
identifies the resulting system with the actual three-handle attaching
system up to the same moves.

## Whole-surface argument

Fix one oriented chosen sphere `S_j`.  In MWW's notation write it as the union
of a planar surface `Sigma_j` in the one-handle boundary and the signed
parallel two-handle core disks prescribed by its owner lift.  Let `J_j` be a
small oriented equator and let the two hemispheres be `Delta_+` and `Delta_-`.

The target row from Theorem C closes every new cable component using the same
parallel two-handle core counit disk that appears in MWW's comparison square.
Therefore the composite of the raw sphere movie with the target row is, as an
oriented foam, the disjoint product of:

1. the old detector surface; and
2. the complete sphere `S_j`, carrying zero or one dot.

This description uses the complete surface, not a chosen sequence of Morse
events.  Any permutations, negative slides, orientation reversals and
pivotal adapters introduced by a decomposition occur in inverse pairs when
the surface is closed with its own core disks.  BHPW strict functoriality and
bicolored isotopy identify every such decomposition with the same closed
foam map.

For the rank-two Frobenius theory,

\[
\operatorname{ev}(S^2)=0,
\qquad
\operatorname{ev}(S^2\text{ with one dot})=1.
\]

Consequently, on the complete MWW source,

\[
\lambda_{t_j}\Psi_{j,0}=0,
\qquad
\lambda_{t_j}\Psi_{j,1}=\lambda_s.
\]

These are exactly the two relations in the `N=2` specialization of MWW
Theorem 3.10.  Applying them to all three spheres and taking the quotient
gives the required `q12` descent.

## Why no separate sign certificate remains

The 49 signed slide bands and two orientation reversals are one method of
presenting the embedded spheres.  They are not additional inputs to the foam
map: strict functoriality assigns the map to the complete oriented cobordism.
Since the final closed component is the same dotted or undotted sphere, its
evaluation fixes the sign.  Thus Theorem S requires no TH-sized row replay.

## Dependency

The only retained hypothesis is Theorem C's statewise cable coherence.  It is
needed because the target row must be defined on the complete beta/psi
quotient before the core-counit closure can be applied.  Once C is complete,
S follows without a further candidate-specific scalar or matrix computation.
