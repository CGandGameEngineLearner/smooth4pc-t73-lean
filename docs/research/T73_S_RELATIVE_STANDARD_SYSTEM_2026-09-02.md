# Relative standard sphere systems and the three-handle consequence

Date: 2026-09-02

## Verdict

The independent large-sphere route is unnecessary for the intended argument,
but that argument is **not** discharged.  The current paper keeps S Open:
closed-manifold HJ Theorem 5.3 is not used to fix `B`, and there is no
B-fixing move list from the actual attaching system in
`Q = partial W2 \\ Int B0`.

```text
P0 + monoidal C  =/=>  S
```

S remains **OPEN**.

## Sources checked

- Horvat--Jablonowski, *On 4-dimensional 3-handle attachments*,
  [arXiv:2510.20282](https://arxiv.org/abs/2510.20282), Theorem 5.3 and the
  relative uniqueness lemma for complete sphere systems.
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

Fix a 3-ball `B` in `M`.  The actual system has connected complement, so it
contains a small 3-ball.  Any two orientation-preserving embedded 3-balls in
a connected oriented 3-manifold are ambient isotopic; applying the inverse
isotopy to the attaching system moves it off the fixed `B`.  Choose a standard
complete system of three nonseparating spheres in `M\Int(B)`; its
complement is connected and its classes form the standard basis of
`H_2^sph(M)`.

Horvat--Jablonowski Theorem 5.3 identifies this standard system with the
actual attaching system up to permutation, 3--3 handle slides, and isotopy.
The final proof instead applies HJ Theorem 5.3 in the closed manifold and
uses Lemma Ssystem: slide-equivalent complete systems give total
three-handle maps with the same kernel.  Thus the standard system outside
`B` may be used without transporting the detector, and no relative boundary
slide is needed.

This proves the geometric E7 replacement from the handle pattern and the
detector-ball field of P0; no owner-coordinate columns or TH-sized sphere
certificate is required.

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

The intended lemmas would supply a fixed-detector kernel replacement and
an actual endpoint square.  They are not presently proved: S remains Open.
Closed-manifold HJ Theorem 5.3 is not used to conclude that `B` is fixed.
