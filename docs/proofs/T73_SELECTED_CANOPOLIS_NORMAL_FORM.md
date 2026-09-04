# Candidate selected four-box canopolis target

Date: 2026-09-05

## Result

An explicit rational target diagram has been constructed and verified. It has
four insertion balls, two disjoint closure balls, 44 active y--z corridors,
227 added z identity arcs, product framings, and a private lane for the cyclic
connector from m_2:C_i to c1:letter:0.

The current data do **not** prove that the actual post-cancellation
coefficient exterior is framed-isotopic to this target relative to all four
insertion balls. Therefore they do not yet prove a literal split union of two
C_271 Hom closures or an ordinary Kunneth tensor product.

## Finite target artifact

The builder build_t73_selected_canopolis_normal_form.py starts from the
source-bound all-owner primitives and selects the m2 and r_xy state. It
creates four rational insertion cuboids, two disjoint closure balls, 44 active
and 227 added primitive records, one 271-strand target realization in each
closure ball, a product normal, and cyclic private lane 43.

The verifier checks source IDs, counts, unique private levels, target-ball
separation, box containment, product framings, push-offs and absence of braid
data. Six mutations fail. Its verdict is deliberately PASS_TARGET_ONLY. It
reports SOURCE_RELATIVE_ISOTOPY=OPEN and BOUNDARY_ENDPOINT_INCIDENCE=OPEN.

## Why source IDs and private levels are insufficient

A tangle exterior relative to four holes is determined not only by the names
of its arcs, but by every oriented boundary endpoint and the matching between
the four parametrized boundary spheres. The all-owner primitive artifact
records source events and local connectors. It does not give:

1. the complete oriented endpoint set on each insertion sphere;
2. the source matching permutation;
3. the target matching permutation induced by J;
4. a bijection proving the matchings agree;
5. an ambient movie relative to all four spheres.

The target assigns a private straight lane to each primitive. This proves the
target itself is embedded and split, not that the source has the same relative
tangle type.

The cyclic m2 connector is the first visible unresolved case. Its source
record passes through the bottom coordinate arc and the t/h_CS cancellation
collar. A private target lane records where it should go, but no source
endpoint matching or relative disk movie moves it there with every insertion
sphere fixed. The 227 residual tracks have the same simultaneous problem.

No topological obstruction has been established. Freedom in the original
Johnson connectors and cancellation bands may permit this presentation, but
that freedom must be used in a construction recording the full four-boundary
matching from the start. It cannot be inferred from free words or source
hashes.

## Grading dichotomy

If a framed ambient isotopy relative to all four insertion balls exists, its
trace has Euler characteristic zero and adds no quantum shift. The two
closure balls then give a literal split union; enriched co-Yoneda may evaluate
the z coend, and ordinary Kunneth may be applied afterwards.

If source and target endpoint matchings differ, changing one into the other
requires a gluing cobordism with saddles or inverse saddles. That is not an
ambient isotopy. Its Euler characteristic and framing contribution must be
included in the Khovanov--Rozansky degree. The displayed minus-44 is the C_44
Hom-normalization correction and does not automatically account for such a
cobordism.

Thus neither the literal tensor decomposition nor the absolute grading is
certified until the endpoint incidence decides which side applies.

## Exact completion datum

A sufficient artifact must give four parametrized triangulated insertion
spheres, every oriented source and target endpoint, the complete source and
target matching graphs, an equality of those graphs under the boundary
parametrizations, and a simultaneous framed ambient isotopy relative to all
four spheres including the cyclic connector and all 227 residual tracks.
Upper-handle maps must be transported if standardization occurs after P0.
