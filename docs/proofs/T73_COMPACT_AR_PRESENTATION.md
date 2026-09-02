# Compact Aitchison--Rubinstein presentation

**Status:** `DISCHARGED FOR THE REPLACEMENT PRESENTATION`

The historical 2,126,291-crossing PD is retired.  The paper instead defines
the handle presentation directly from the public Aitchison--Rubinstein
product construction and embeds the detector collar in that presentation.

## Public objects

- primary scan: the Berkeley copy of *Four-Manifold Theory*, SHA-256
  `6F7E95B8266876774667AD40EA3DE964B165680D6789A34E49BF598C3AE04DF0`;
- witness: `audit/t73_ar_product_witness.json`;
- generator/verifier: `scripts/generate_t73_ar_product_witness.py`;
- detailed proof: `docs/research/T73_P0_AR_PRODUCT_DISCHARGE_2026-09-02.md`.

Run:

```text
python -B scripts/generate_t73_ar_product_witness.py --check \
  --source-pdf PATH_TO_PUBLIC_AR_SCAN
python -B scripts/check_t73_p0_embedded_witness.py \
  audit/t73_ar_product_witness.json
python -I -B tests/test_t73_ar_product_witness.py -v
```

## Construction boundary

AR pp. 5--7 give the simultaneous embedded mapping-torus attaching circles
and their framing annuli.  Pages 8--12 give the coordinate-spine torus model
and handlebody-preserving representative.  Pages 16--17 give the parallel
strip normal field.  A mapping-torus diffeomorphism pulls the whole
construction back to the linear map induced by the displayed matrix.

The two geometric cancellations are `(t,h_CS)` and `(x,m_1)`.  The first is
the complementary pair identified by AR; the second uses `A e_1=e_3` and the
single geometric `x` passage of `m_1=z x^-1`.  All other components and normal
fields are transported by product bands.

The public word ledger is now used only as the exact projection of this actual
embedded construction.  In particular, the empty post-cancellation word of
`r_zx` is not promoted to a split-unknot claim.

## Detector collar

After cutting the remaining `y,z` handles, a regular neighborhood of the 42
`m_2` and two `r_xy` y-passages is a standard 3-ball with 44 labelled
wickets.  The public pure braid is realized there by the mapping-class
interpretation of the braid group and isotopy extension.  This constructs the
actual collar used by the replacement proof; it does not identify the
historical PD collar.

## Retained gap

P0 is discharged.  C still must identify the actual cut coefficient bimodule
of this product presentation with the completed representable endpoint model,
including both actions, grading/completion and simultaneous transport.
