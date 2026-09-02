# C comparison attempt: representable coefficients and the endpoint type

Date: 2026-09-02

## Verdict

The abstract representable-coefficient part of C is **DISCHARGED** over the
ordinary rational coefficient trace.  The candidate-specific comparison C
remains **OPEN** because the actual product-annulus coefficient bimodule has
not been identified, with both actions, with that representable model; its
quantum/completed lift and the simultaneous endpoint transport are likewise
not constructed.

## Primary sources checked

- Manolescu--Walker--Wedrich,
  [arXiv:2206.04616](https://arxiv.org/abs/2206.04616), especially the
  one-handle quotient and its reformulation as zeroth Hochschild homology of
  the tangle category with the coefficient bimodule determined by the actual
  cut tangle.
- Beliakova--Putyra--Wehrli,
  [arXiv:1605.03523](https://arxiv.org/abs/1605.03523), especially the
  universal quantum trace, the canonical full and faithful functor from the
  vertical trace to the horizontal trace, quantum-horizontal-trace
  functoriality, and the action on oriented cablings.
- Beliakova--Hogancamp--Putyra--Wehrli,
  [arXiv:1903.12194](https://arxiv.org/abs/1903.12194), for strict integral
  tangle/foam functoriality and the flat-base qHH/Chern statement for the
  specified quantum web algebras.

These sources give the relevant general functors.  They do not identify the
trace-73 cut coefficient bimodule or its selected class.

## Correct endpoint type

The earlier proposed statement wrote a target resembling

```text
Hom_{U_q}(V^tensor86, V^tensor88)_{weight 86}.
```

This is not the correct 88-dimensional endpoint object: a weight space is a
submodule of a representation, not of the set of intertwiners.  Put

```text
E86 = (V^tensor86)_{weight 86},
E88 = (V^tensor88)_{weight 86}.
```

Then `E86` is one-dimensional and `E88` is 88-dimensional.  The endpoint of
the cup is a map in

```text
Hom_{Q[[h]]}(E86,E88) ~= E88.
```

The tangle maps that produce it are `U_q(sl2)` intertwiners before restriction
to weight spaces.  The public Burau operator is an endomorphism of `E88`, and
the cap is a map `E88 -> E86`.  This corrected typing is used in the closure
programme.

## Abstract Hattori reduction now proved

Let `C` be a small rational-linear category and let `B` be a linear
autofunctor whose maps on all hom spaces are linear equivalences.  Define the
transported representable coefficient bimodule by

```text
M_B(x,y) = Hom_C(Bx,By),
```

with the left and right actions obtained by applying `B` to the acting
morphism and composing.  Applying `B^{-1}` on each hom space gives a
two-sided coefficient-bimodule equivalence

```text
M_B ~= Hom_C(-,-).
```

It follows functorially that

```text
HH0(C;M_B) ~= HH0(C;Hom_C(-,-)).
```

This is encoded and kernel checked in
`Smooth4PC/RepresentableCoefficient.lean`.  The proof verifies both action
squares, sends the cyclic-relation span to the cyclic-relation span in both
directions, and constructs the quotient linear equivalence.  It introduces
no geometric axiom.  `T73RepresentableAudit.lean` prints the axioms of the
load-bearing statements.

## What this removes from C

Once a genuine product Hattori equivalence

```text
H_{T,T'} : M_R(T,T')
  ~= Hom(B_act T, B_act T') tensor A^tensor227
```

is supplied as a coefficient-bimodule equivalence, the passage from the
representable hom factor to the regular vertical trace is no longer an
assumption.  Evaluation of the separate Frobenius factors by
`epsilon(X)=1`, followed by BPW's canonical vertical-to-horizontal trace
functor, is the intended general route to the endpoint tangle map.

## Remaining candidate-specific fields

The following are still not constructed.

1. The P0 detector-collar embedding that determines `B_act` and the public
   wicket order.
2. The actual family `H_{T,T'}` for every source/target tangle, not only the
   count `44,271,227`.
3. Both action-naturality squares for `H`.
4. The q-deformed/completed version over `Q[[h]]`, including the grading
   shifts and specialization to ordinary coefficient `HH0`.
5. The single coordinate transport acting simultaneously on the public
   operator, cup vector, and cap row.

Thus the C gap is smaller and better typed, but it is not discharged at the
candidate level.
