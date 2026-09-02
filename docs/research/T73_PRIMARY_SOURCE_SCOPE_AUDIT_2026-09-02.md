# Primary-source scope audit for the remaining trace-73 joins

Date: 2026-09-02

This is a proof-attempt record, not a literature summary.  The question is
whether the cited general theorems themselves construct the candidate-level
maps needed for P1/C and P2/S.

## Sources checked

- Manolescu--Walker--Wedrich, *Skein lasagna modules and handle
  decompositions*, [arXiv:2206.04616](https://arxiv.org/abs/2206.04616), in
  particular the one-handle cutting/gluing theorem, the two-/three-handle
  formula, Proposition 3.4, Corollary 3.5, and the Chern-character discussion.
- Beliakova--Hogancamp--Putyra--Wehrli, *On the functoriality of sl(2) tangle
  homology*, [arXiv:1903.12194](https://arxiv.org/abs/1903.12194), in
  particular the flat-base quantum Hochschild/Chern statement and strict
  tangle functoriality.
- The BPW quantum annular/horizontal-trace results cited in the paper, used
  only for their stated functorial constructions.

The arXiv source trees were inspected directly.  No unavailable local
certificate was treated as evidence.

## Attempt C1: obtain the endpoint functional directly from MWW's
one-handle theorem

MWW's one-handle theorem expresses the lasagna module as a quotient of a
direct sum over all inserted tangles.  Equivalently, it is a zeroth Hochschild
trace with a coefficient bimodule determined by the actual cut tangle `R`.
The theorem provides the gluing isomorphism after `R`, its boundary points,
and both category actions are geometrically fixed.

It does **not** identify the trace for an arbitrary coefficient bimodule with
the 88-dimensional one-particle endpoint representation used by the public
Burau script.  Therefore the theorem cannot be applied before constructing:

1. the actual cut tangle and coefficient bimodule;
2. a bimodule morphism/equivalence compatible with both actions; and
3. the induced map to the stated qHH0 endpoint summand.

Verdict: **OPEN**.  The attempted direct implication is invalid.

## Attempt C2: use the Chern character to force the missing comparison

MWW's Chern-character proposition gives injectivity under Krull--Schmidt and
finite-endomorphism hypotheses in the setting in which it is invoked.  The
BHPW flat-base result gives a Chern isomorphism for their specified quantum
web algebras.  Neither statement says that the candidate coefficient
bimodule `M_R` is that algebra, or that the selected Hattori class maps to the
public cup vector and covector.

Even an isomorphism on the target algebra's qHH0 cannot identify an element
of the source coefficient trace without a functor/bimodule map.  Thus the
word “Chern” does not fill the missing arrow.

Verdict: **OPEN**.  The required source-to-target natural map is additional
candidate-level data.

## Attempt C3: choose coordinates so that `B_act` equals the public braid

Changing endpoint coordinates by `P` necessarily changes all three objects:

```text
W_actual = P^-1 W_public P,
u_actual = P^-1 u_public,
ell_actual = ell_public P.
```

The compact Hattori ledger fixes counts and formal normal forms but does not
determine the actual west-to-east product motion or `P`.  Setting only
`B_act = B_public` is not a harmless convention; it holds `W,u,ell` fixed and
is circular.  General tangle functoriality proves invariance after the same
geometric isotopy has been constructed, not existence of that isotopy.

Verdict: **OPEN**.  A single simultaneous transport certificate is minimal.

## Attempt S1: derive embedded attaching spheres from the unimodular owner
basis

The owner lifts and 32 Nielsen operations prove an integral coordinate
statement.  They do not produce maps `S^2 -> partial W_2`, prove that the maps
are embeddings with disjoint images, or identify their normal framings.
They also do not derive the candidate boundary and irreducibility hypotheses
needed by the cited sphere-replacement theorem.

Verdict: **OPEN**.  Homology and Nielsen data are necessary but not sufficient.

## Attempt S2: close the MWW maps by a whole-sphere evaluation

For an already identified hemisphere map, closing it with its own core disks
does reduce the rank-two Frobenius calculation to
`ev(S^2)=0` and `ev(dot S^2)=1`.  The missing step is precisely that the
candidate's raw MWW map, after pivotal adapters, signs, normal-level choices
and endpoint coordinate transport, is the foam being closed.  Strict
functoriality makes two presentations of a fixed cobordism agree; it does not
identify the proposed combinatorial movie with the fixed cobordism.

Verdict: **OPEN**.  The whole-sphere calculation is a conditional algebraic
lemma, not a candidate-level proof.

## Result of this proof attempt

The primary sources validate the general P3 machinery and several local
lemmas, but they do not close C or S.  More computation inside the existing
88-dimensional model cannot repair this, because the missing objects are the
source coefficient bimodule map and embedded sphere/hemisphere maps.

The shortest viable path remains:

1. solve P0 by emitting an actual embedded framed presentation;
2. derive `B_act` and `P` from that same embedding;
3. implement the induced coefficient-bimodule morphism on generators and
   verify both action squares;
4. construct actual embedded sphere movies in that presentation and evaluate
   the induced MWW maps in the same coordinates.

Until those objects exist, all four candidate joins remain assumptions and
the paper is conditional.
