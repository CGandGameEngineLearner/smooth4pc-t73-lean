# P0 audit: the public braid is not identified with an AR collar braid

Date: 2026-09-02

## Verdict

**OPEN.** The public 11340-letter pure braid has not been derived as the
relative-endpoint isotopy class of the 44 passages in the reduced
Aitchison--Rubinstein handlebody. Under the project stopping rule, C and S
must not be attempted as candidate-level closures until this identification
is supplied.

## Public-source check

The Berkeley scan of Aitchison--Rubinstein was downloaded from the URL used
by the repository. Its SHA-256 is

    6F7E95B8266876774667AD40EA3DE964B165680D6789A34E49BF598C3AE04DF0

which agrees with the pinned source digest. The paper supplies the general
mapping-torus handle construction, product annuli, and handlebody-preserving
representatives. It does not specify the later 44-wicket labeling or the
six-sweep point-push movie.

## Provenance mismatch

The authoritative provenance in data/T73_DELTA3_PUBLIC_INPUT.json says that
the 252 crossing rows were extracted from T73_COLLAR_BRAID.json and from a
frozen 2,126,291-crossing planar diagram. The latter is not public. The
replacement script verify_t73_compact_point_push.py proves only that a compact
six-sweep formula regenerates those rows and the same Artin word. Its own
scope statement says:

    local marked collar braid only; no full Kirby identification

No function in generate_t73_ar_product_witness.py computes the 252 rows from
the AR component parametrizations, the cancellation bands, or an ambient
embedding. Instead, it imports the already frozen public input and records
its length and digest under detector_collar.

## The isotopy-extension error

The proposed discharge makes the following invalid inference:

1. choose the public pure braid as a mapping class of a punctured disk;
2. realize that mapping class by point-pushing and isotopy extension;
3. conclude that it is the braid already induced by the selected AR
   passages.

Steps 1--2 construct a braid with the requested word. They do not establish
step 3. A relative-endpoint isotopy class of a monotone tangle in
D^2 times I is precisely braid-group data. Isotopy extension realizes a
chosen class; it does not identify that class with a pre-existing tangle.
Otherwise every pure braid could be declared isotopic relative endpoints to
the same product tangle.

The nonzero third-order Burau calculation is also incompatible with treating
the public word as the identity braid. Thus the missing comparison cannot be
removed by saying that the inserted point-push is merely an ambient isotopy
of a trivial product collar.

## Minimum missing object

P0 requires one of the following equivalent public objects:

1. an explicit framed PL/smooth embedding of the reduced AR attaching link
   and ball B, together with a projection movie whose ordered crossing trace
   is the public 252-row ledger; or
2. a labeled Kirby/isotopy movie from that embedded AR pair to a public
   embedded collar representative of the 11340-letter braid.

The movie must preserve component ownership, endpoint order, product normals,
and the two cancellation bands. A JSON assertion, digest, word equality,
permutation, or writhe is not such an object.

## Consequence

P0 remains OPEN rather than DISCHARGED. Since the actual MWW coefficient
object in C and the fixed detector in S both depend on this same embedded
pair, their candidate-level closure is not meaningful before the missing P0
comparison is constructed.
