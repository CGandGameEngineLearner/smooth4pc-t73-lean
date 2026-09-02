# Compact Aitchison--Rubinstein presentation

**Status:** `PARTIAL -- WORD/FRAMING-NAME LEDGER; EMBEDDED KIRBY EQUIVALENCE OPEN`

> The compact generator proves word-level and product-normal bookkeeping.  It
> does not output an embedded framed link or a labelled Kirby/isotopy ledger,
> so it does not discharge P0.

This note constructs a public replacement for the unavailable historical
2,126,291-crossing planar diagram.  It defines the candidate directly from
the Aitchison--Rubinstein linear product-ribbon construction and retains
product framings throughout.  It does not claim byte equality with the
historical PD file.

## Public replay

Run:

```text
python -B scripts/generate_t73_compact_kirby_ledger.py --check
python -I -B tests/test_t73_compact_kirby_ledger.py -v
```

The current ledger identity is

```text
BA45C92B6A5605CB259F29E3550BC367C0783BBA9206E2633582B2ABE81DE1BC
```

## Construction

Let

\[
A=\begin{pmatrix}0&269&1240\\0&41&189\\1&0&32\end{pmatrix}.
\]

For the coordinate circle `x_j`, the straight segment from the origin to
`A e_j` crosses the integer coordinate faces at rational times

\[
t=\frac{k}{(Ae_j)_i}.
\]

Ordering these events gives the linear Christoffel word for the top edge of
the Aitchison--Rubinstein product annulus.  A fixed product perturbation
orders coincident events with the terminal axis first and the remaining axes
in descending cyclic order.  The complete mapping-torus attaching word is

\[
m_j=t\,\phi_A(x_j)\,t^{-1}x_j^{-1}.
\]

The normal is the product-annulus normal from the construction, not a
blackboard integer.

Cancel `(t,h_CS)` using the product pair.  Because `Ae_1=e_3`, the remaining
word `m_1=z x^{-1}` is a second product cancelling pair.  Its cancellation
replaces `x` by `z` on every surviving ribbon.  The two nested product bigons
in `r_zx=[z,z]` give a split unknot with zero relative framing.

The generator independently obtains

```text
m_2: length 311, exponent sums (y,z)=(40,269)
m_3: length 1460, exponent sums (y,z)=(189,1271)
r_zx: empty reduced word plus its transported zero-framed product disk
```

These are precisely the registered reduced word data.  Since every step is
performed on the Aitchison--Rubinstein product ribbons, the resulting
genus-two handle presentation is, by construction, a framed presentation of
the Cappell--Shaneson manifold `Sigma_A^0`.

## Local detector collar

`T73_COMPACT_POINT_PUSH_BRIDGE.md` independently defines the 44-strand
collar braid as six explicit sweeps.  A braid word is an actual framed tangle
morphism in the cabled one-handle category, so the compact presentation no
longer needs to extract that morphism from a planar PD projection.

What is still required is a coefficient-level binding: the selected balanced
copies of `r_xy` and `m_2`, their cut objects, the Hattori rectangle and both
left/right action squares must identify the actual MWW coefficient bimodule
with this compact collar model.  The compact word identities alone do not
prove those naturality squares.

## Consequences

The following facts no longer depend on the historical PD bytes:

1. the candidate manifold is the standard Cappell--Shaneson construction for
   the displayed matrix;
2. the framings used by the replacement presentation are actual product
   framings;
3. the two cancellations and reduced gate words are public and replayable;
4. the local point-push braid is a public actual tangle morphism.

The remaining P0/P1 join is the actual coefficient/Hattori binding, not the
existence of a candidate manifold or a local braid.
