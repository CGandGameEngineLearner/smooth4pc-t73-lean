# Relative standard sphere systems and the three-handle consequence

Date: 2026-09-02

## Verdict

The independent large-sphere route is unnecessary.  Subject to a genuine P0
handle presentation with its detector contained in a 3-ball, and to the full
symmetric-monoidal/natural form of C, the three-handle closure S follows from
published general theorems.  Thus the abstract implication

```text
P0 + monoidal C  =>  S
```

is **DISCHARGED**.  Candidate-level S remains **PARTIAL**, rather than
`DISCHARGED`: P0 is now supplied by the Johnson replacement, while the full
symmetric-monoidal C comparison remains open.

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
For the relative statement set `Q=M\Int(B)`.  Their relative uniqueness lemma
performs ambient isotopies fixed on `partial Q`, sphere slides, and boundary
slides over `partial B`.  After `B` is capped back in, a boundary slide over
`partial B` is tubing to an inessential sphere bounding a ball and is removed
by a local isotopy.  Consequently the replacement can be made without moving
the detector supported in `B`.

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

Let `lambda` be the complete detector row supplied by C.  Require C in its
natural form: it is symmetric monoidal for disjoint cobordisms and natural
for boundary cobordisms supported away from the detector ball.  Since each
standard attaching sphere is outside `B`, local action is disjoint from the
point-push, cup and cap in `B`.  Strict monoidality gives, for every source
element `v`,

```text
lambda(v * A_0) = lambda(v) * ev(dotted sphere) = lambda(v),
lambda(v * A_1) = lambda(v) * ev(undotted sphere) = 0.
```

These are equations on the whole source, not a selected-vector check.  They
show that `lambda` annihilates the complete MWW relation submodule for each
of the three standard spheres and therefore descends through the iterated
three-handle coequalizer.

Because all replacements and sphere neighborhoods are outside `B`, there is
no old-factor endpoint permutation to calculate.  The earlier 32-step
Nielsen program and split-tree algebra remain valid optional coordinate
models, but are not load-bearing for this relative proof.

## Remaining obligations

This theorem does not solve P0 or C.  To instantiate it one still needs:

1. a P0 embedded witness whose detector collar lies in an explicitly supplied
   3-ball and whose handle pattern has three 3-handles and one final 4-handle;
2. the actual product coefficient-bimodule comparison from C;
3. proof that this comparison is symmetric monoidal and natural for
   cobordisms disjoint from the detector ball.

Once those exist, no additional candidate-specific sphere movie, pivotal
adapter, foam-sign ledger, or TH1/TH2/THXY file is needed for S.
