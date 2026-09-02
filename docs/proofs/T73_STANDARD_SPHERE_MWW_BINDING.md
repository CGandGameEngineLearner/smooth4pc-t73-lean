# Standard-sphere MWW binding for the compact presentation

**Status:** `SUPERSEDED BY THE DECOMPOSITION-INDEPENDENT THEOREM S`

This note replaces the missing TH1/TH2/THXY geometry by a standard complete
sphere system in the boundary of the compact AR two-handlebody.

## Relative complete sphere system

The compact Cappell--Shaneson handle decomposition has three 3-handles and
one final 4-handle.  Immediately before the 4-handle the boundary is `S^3`.
Reversing the three 3-handles attaches three 1-handles to `S^3`, so

\[
\partial W_2\cong\#^3(S^1\times S^2).
\]

Let `B` be a closed 3-ball containing the marked point-push detector collar.
Choose the standard three nonseparating spheres in the complement of the
corresponding standard ball in `#^3(S^1 x S^2)`.  A boundary diffeomorphism
may be adjusted on a ball by isotopy, so their pullbacks give a complete
pairwise-disjoint framed sphere system disjoint from `B`.

The complement is connected and the three classes are the standard basis of
the spherical second homology.  Horvat--Jab\l{}onowski's Theorem 5.3 therefore
identifies this system with the original three-handle attaching system up to
isotopy, permutation and sphere slides.  The corresponding upper cobordisms
are diffeomorphic relative to the incoming `W_2`.

The optional coordinate basis recorded in `T73Finite.lean` is obtained from
this standard system by the public 32-step Nielsen program

```text
python -B scripts/generate_t73_sphere_slide_ledger.py
```

but the coordinate change is not needed to define the standard system.

## MWW maps away from the detector collar

Choose disjoint product neighborhoods of the three standard spheres outside
`B`.  For each sphere, its equator and the two hemisphere movies are supported
away from the old 88-endpoint detector block.  Cutting parallel copies of the
two-handle attaching circles uses separate normal levels, so the old selected
copies pass through by identity cylinders.

In BPW/BHPW endpoint coordinates, one standard sphere therefore has one new
Frobenius factor and the two constant maps are

\[
F_0^{(0)}=Id_{old}\otimes 1,
\qquad
F_1^{(0)}=Id_{old}\otimes X.
\]

The W2 core counit is `Id_old tensor epsilon`.  Hence

\[
(Id\otimes\epsilon)F_0^{(0)}=0,
\qquad
(Id\otimes\epsilon)F_1^{(0)}=Id.
\]

These are the `b=1` instances of the arbitrary split-tree equations already
proved in `Smooth4PC/T73SplitMovie.lean` and
`Smooth4PC/T73SphereQuotient.lean`.

Any positive/pure transport caused by changing normal levels has constant
term identity on the old factor.  `Smooth4PC/CubicJet.lean` proves that such
`Id+O(h)` source and target transports cannot change an incoming cubic
leading row.  Thus the divided detector satisfies the undotted-zero and
dotted-identity equations for each of the three standard spheres.

The preceding conclusion requires the old-factor transport really to have
identity constant term in the same coordinates as the public `W,u,ell`.
Choosing a boundary identification does not prove this: any nontrivial
constant permutation must be transported simultaneously through all three
objects.  The 32-step homology ledger alone does not determine that endpoint
transport.

## Remaining review boundary

The argument uses only a relative-ball choice, product tubular neighborhoods,
published MWW gluing locality, strict tangle functoriality, and the HJ
replacement theorem.  It avoids all unavailable large sphere certificates.

Before changing the paper to an unconditional result, one must construct the
actual endpoint transport induced by the relative standard-sphere movie and
check it simultaneously on `W,u,ell`, in addition to confirming that selected
cable normal levels are fixed.  Until that join is proved, the status remains
partial rather than discharged.
