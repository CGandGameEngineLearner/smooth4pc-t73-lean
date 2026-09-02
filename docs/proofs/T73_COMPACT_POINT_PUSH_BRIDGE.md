# Compact public point-push bridge

**Status:** `DISCHARGED for the local collar braid; global P0 remains OPEN`

This note replaces the 252 primitive `r_xy/m_2` crossing rows by a compact,
independently executable six-sweep schema.  It does not use the missing full
PD file, its builder, or any historical `D:/tmp` object.

Run:

```text
python -B scripts/verify_t73_compact_point_push.py
python -I -B tests/test_t73_compact_point_push.py -v
```

## Compact schema

There are 41 ordinary wickets, numbered 3 through 43, and one return wicket,
numbered 44.  The collar contains six oriented sweeps, each meeting all 42
wickets exactly once.  Thus the factor count is

\[
6\cdot 42=252.
\]

Between consecutive ordinary wickets, the `m_2` segment coordinate follows
the 40-step Christoffel schedule

```text
32 28 32 28 32 28 32 32 28 32
28 32 28 32 28 32 32 28 32 28
32 28 32 32 28 32 28 32 28 32
28 32 32 28 32 28 32 28 32 28
```

The four segment origins are `21, 23, 25, 27`.  The two long horizontal legs
use the corresponding x-increments `112` and `96`; the two short return legs
have constant x-increment `16`.  Four explicitly recorded return-wicket rows
close the cyclic passages.  All remaining fields -- owner, oriented sign,
left/right pure-braid convention, wicket roles and passage exponent -- are
determined by the sweep.

The verifier generates all rows from these data, sorts them by frozen source
index, and compares every field with
`data/T73_DELTA3_PUBLIC_INPUT.json`.  It separately regenerates the oriented
chronology

```text
180,...,263; 174,...,91; 86,...,3
```

and expands each row into the appropriate Artin pure-braid generator.

## Verified identities

The clean replay proves:

```text
crossing factors: 252
crossing-row SHA-256:
  81765489EE2B1594271ED378D1D458C1A00C3C69975742815AD24AEDC89D2B1D
B44 length: 11340
B44 SHA-256:
  7C2D2F792C2672221A76CAF08A71F560AF0CB7654B4D537C00FAD00B16EFA187
```

The mutation test changes one generated coordinate and verifies that the
identity check fails.

## Mathematical consequence and retained boundary

The public 44-strand word is therefore not merely a hash-pinned projection of
an unavailable large diagram.  It is a reproducible marked collar braid
specified by six affine sweeps and one 40-step schedule.  Its cabling and
Burau evaluation may be based on this compact object.

More intrinsically, the six sweeps prescribe a loop of the `r_xy` product
connector through the complement of the `m_2` product passages.  At every
crossing row the moving wicket follows the declared left/right pure-generator
chart, and between consecutive rows it follows the affine horizontal leg.
The return wicket closes the loop with identity owner permutation and zero
relative product-framing change.  Isotopy extension gives a framed ambient
isotopy `Phi_t` of a tubular neighborhood of the two owner annuli.

For an arbitrary MWW cable state, apply `Phi_t` simultaneously to every
parallel physical copy.  This defines the statewise companion motion `W_s`.
It is the full cabling of one base motion, not `W disjoint Id` on a preferred
old subset.  Consequently physical-copy braids and undotted/dotted pair
addition commute with the family `W_s` by ordinary cabling functoriality.  On
the base balanced state the induced 88-endpoint braid is exactly the public
cabled word.

This result by itself does **not** identify the ambient four-manifold.  The
remaining global theorem must
construct a component- and framing-preserving map from the
Aitchison--Rubinstein product-ribbon handle presentation to a reduced Kirby
presentation containing this collar, and must show that the induced endpoint
transport carries the selected source vector, cap covector and point-push
operator simultaneously.  `T73_COMPACT_AR_PRESENTATION.md` supplies the
replacement global presentation used for that join.  No claim about the
missing full PD bytes is made.
