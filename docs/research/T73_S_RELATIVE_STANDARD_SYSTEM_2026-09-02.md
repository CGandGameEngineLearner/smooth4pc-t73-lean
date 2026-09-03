# Relative standard sphere systems and the three-handle consequence

Date: 2026-09-02

## Verdict

The independent large-sphere route is unnecessary.  The current paper
discharges S for the Johnson replacement reversed 1-handle picture:

```text
P0 + monoidal C + reversed belt spheres missing B  =>  S
```

is **DISCHARGED** at Johnson-replacement strength.  HJ Theorem 5.3 is used
only for kernel invariance, not to fix `B`.  P3 remains Open.

## Sources checked

- Horvat--Jablonowski, *On 4-dimensional 3-handle attachments*,
  [arXiv:2510.20282](https://arxiv.org/abs/2510.20282), Theorem 5.3.
  Lemmas 5.5 and 5.7 are not in that paper.
- Manolescu--Walker--Wedrich,
  [arXiv:2206.04616](https://arxiv.org/abs/2206.04616), the three-handle
  coequalizer theorem and its intrinsic module-action reformulation.
- Beliakova--Hogancamp--Putyra--Wehrli,
  [arXiv:1903.12194](https://arxiv.org/abs/1903.12194), for strict monoidal
  tangle/foam functoriality.

## Relative sphere theorem used here

Let `W_3` be a connected four-dimensional handlebody with no 4-handles,
three 3-handles, and connected boundary `S^3`.  Put `M=partial W_2`.  Reversing
the three 3-handles attaches three three-dimensional 1-handles to `S^3`, so

```text
M ~= #3(S^1 x S^2).
```

The actual attaching sphere system has connected complement: simultaneous
sphere surgery followed by capping gives the connected boundary `partial W_3`.

Choose the standard complete belt-sphere system of the Johnson replacement
reversed 1-handle picture, already missing the P0 cube `B`.  Dual loops
meet their owner belt sphere once through the 1-handle and return in the
chart without meeting any belt cube.

Horvat--Jablonowski Theorem 5.3 relates any other complete system to this
one by isotopy, permutation and slides in the closed manifold.  Lemma
Ssystem says those moves preserve the kernel of the total three-handle map
and are the identity on `W2`.  The detector in `B` is not moved.  Closed
Theorem 5.3 is not used to conclude that `B` is fixed.

This proves the geometric E10/S replacement from the reversed 1-handle
picture and the detector-ball field of P0; no owner-coordinate columns or
TH-sized sphere certificate is required.  P2/E7 stays Open.

## Intrinsic MWW three-handle relation

MWW describe a 3-handle attached along a sphere `S` by a coequalizer of its
two hemisphere maps.  Their module-action reformulation states that the
result is the quotient by the local action of the lasagna algebra of
`S^2 x D^2`.  For `N=2`, write:

- `A_0` for the essential sphere carrying one dot;
- `A_1` for the undotted essential sphere.

The three-handle quotient imposes

```text
A_0 = 1,
A_1 = 0.
```

Let `lambda` be the complete detector row supplied by C.  To descend it one
must prove, for every source element `v`,

```text
lambda(v * A_0) = lambda(v) * ev(dotted sphere) = lambda(v),
lambda(v * A_1) = lambda(v) * ev(undotted sphere) = 0.
```

These are equations on the whole source, not a selected-vector check.
The displayed `A_0,A_1` are essential spheres in `S^2 x D^2`, so
monoidality alone is insufficient.  Lemma Sendpoint supplies the additional
argument: a generic cut movie has no mixed Morse critical points; mixed
events are endpoint braids, whose constant terms are symmetric permutations.
After simultaneous transport, the actual map factors as the old detector
map tensor the connected genus-zero Frobenius map.

Because all replacements and sphere neighborhoods are outside `B`, there is
no old-factor endpoint permutation to calculate.  The earlier 32-step
Nielsen program and split-tree algebra remain valid optional coordinate
models, but are not load-bearing for this relative proof.

## Closure

Paper Lemmas Ssystem and Sendpoint discharge S for the Johnson replacement
reversed picture.  Closed-manifold HJ Theorem 5.3 is used only for kernel
invariance, not to conclude that `B` is fixed.  P3 remains Open.
