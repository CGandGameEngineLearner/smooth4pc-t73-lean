# Smooth4PC T73 — trace-73 skein-lasagna obstruction

[中文说明](README.zh-CN.md)

This repository presents a paper-level skein-lasagna obstruction for the
trace-73 Cappell--Shaneson homotopy 4-sphere associated with
\[
A=\begin{pmatrix}0&269&1240\\0&41&189\\1&0&32\end{pmatrix}
\]
(Iwaki standard form \(X_{41,189,73}\)).

**The manuscript currently proves P0/E13 at paper level and gives a
conditional skein-lasagna obstruction; C and S remain open at the corrected
coefficient comparison.  No unconditional counterexample is claimed.** The controlling manuscript is
[`paper/spc4-t73-candidate/main.tex`](paper/spc4-t73-candidate/main.tex)
(*A skein-lasagna obstruction for a trace-73 Cappell--Shaneson
sphere*).

## What is proved, and what is open

For an explicit **Johnson-generator** handle presentation the paper now gives
a paper-level construction of **P0** and transports the complete AR upper
handles to obtain **E13/P3**, including \(X_J\cong\Sigma_A^0\).  The
complete source and target constructors now save \(1260\) endpoints and
\(630\) framed arcs each.  Their matchings differ in eight wrong-side
connectors, so the proposed literal two-representable split is refuted.  Its
degree \(223\) is target-only; the actual **C/S** map and its nonzero degree
remain open.

An exact finite calculation gives a nonzero divided cubic \(D_3=2624\). An
Artin--Magnus certificate and the pure-braid Andreadakis theorem establish a
third-order property of the public braid word.

A Lean development formalizes the **abstract quotient argument**: given
interface data assembling the MWW quotients and four-handle transport
(`ExternalGeometry`), a nonzero class in any nonzero quantum degree would obstruct
diffeomorphism with \(S^4\). Those geometric interfaces are **not** constructed
in Lean.

| Layer | Status |
| --- | --- |
| Finite algebra (endpoint scalar \(2624\), historical degree \(494\), \(\det A=\det(A-I)=1\)) | Checked in Lean; no actual MWW class degree is currently constructed |
| Abstract conditional implication | Checked in Lean |
| Johnson P0 / E13 / topological P3 | Proved at paper level after detector retyping |
| C / S coefficient and hemisphere comparison | **Open** at the actual coend/currying and statewise shadow |

The exact topology verifiers use NumPy, SciPy, SymPy, and Shapely. In WSL, create the
persistent environment with
`python3 -m venv /home/lifesize/.cache/t73-topology-venv` followed by
`/home/lifesize/.cache/t73-topology-venv/bin/pip install -r requirements-topology.txt`.
| Lean inhabitant of `ExternalGeometry` | **Open** |

The exact Lean boundary is
[`Smooth4PC/T73External.lean`](Smooth4PC/T73External.lean). Premises audit:

```text
python3 scripts/audit_t73_premises.py --check
```

The legacy script still prints historical PASS labels and is not an
authoritative completion test; use `audit/RUNNING_PAPER_AUDIT.md` and the new
fail-closed gates instead.

The complete selected-C geometry bundle is rebuilt and checked with:

```text
python3 scripts/build_t73_complete_geometry_bundle.py --write
python3 scripts/build_t73_complete_geometry_bundle.py --check
python3 scripts/build_t73_complete_geometry_bundle_v2.py --check
```

This saves all currently reconstructible endpoint/arc geometry.  Its manifest
deliberately remains `OPEN` at the actual coend/currying map.

### Actual AR-to-Kirby construction data

[`geometry/t73_actual_ar_kirby_construction_request.json`](geometry/t73_actual_ar_kirby_construction_request.json)
is generated from the actual AR coordinate atlas by
[`scripts/build_t73_actual_ar_kirby_construction_request.py`](scripts/build_t73_actual_ar_kirby_construction_request.py).
It is a hash-bound `OPEN` request, not a Kirby witness: it records the three
missing chart transitions, the 6 t-bands and 1513 x-bands that require two
boundary edges/splice data, and the seven required final components. Rebuild it
with:

```text
python3 scripts/build_t73_actual_ar_kirby_construction_request.py --check
```

The future witness is validated by
`scripts/verify_t73_ar_to_kirby_presentation.py`; it will only accept explicit
cut-and-surgery geometry and exact AR/t/x source bindings.

The citable source index for digitising the required PL cells is
[`geometry/t73_literature_geometry_ledger.json`](geometry/t73_literature_geometry_ledger.json),
rebuilt with `python3 scripts/build_t73_literature_geometry_ledger.py --check`.
It records source pages/figures and what each source does and does not supply.

[`geometry/t73_unified_kirby_foot_chart.json`](geometry/t73_unified_kirby_foot_chart.json)
combines all four AR Figure 2a foot pairs with verified T73 passage data. The
t/x histories bind to their belt spheres and verified cancellations; the final
y/z state has 235 and 1550 reflection-paired passages. Rebuild it with
`python3 scripts/build_t73_unified_kirby_foot_chart.py --check` and verify it
with `python3 scripts/verify_t73_unified_kirby_foot_chart.py`. The final passage
data are in
[`geometry/t73_final_yz_foot_state.json`](geometry/t73_final_yz_foot_state.json),
with foundational Johnson-only bindings in
[`geometry/t73_yz_foot_lane_binding.json`](geometry/t73_yz_foot_lane_binding.json).
The five cyclic orders are in
[`geometry/t73_final_component_passage_cycles.json`](geometry/t73_final_component_passage_cycles.json):
`311,1462,4,4,4`, retaining the two bottom coordinate passages before any
explicit free-reduction isotopy.
The first common-R3 routing is saved, fail-closed, in
[`geometry/t73_actual_kirby_core_embedding.json`](geometry/t73_actual_kirby_core_embedding.json)
with status `SOURCE_BOUND_KIRBY_CORE_CANDIDATE_STRUCTURAL_CHECK_ONLY`.
Its compact push/projection manifest is
[`geometry/t73_actual_kirby_framed_input.json`](geometry/t73_actual_kirby_framed_input.json).
Use `build_t73_actual_kirby_framed_input.py --materialize PATH` to expand it
outside the repository. `export_t73_full_handle_diagram.py` now uses a Shapely
STRtree streaming broad phase, but no actual PD/framing export has passed yet.
The actual passage words are compared with the historical railroad ledger in
[`geometry/t73_final_railroad_word_binding.json`](geometry/t73_final_railroad_word_binding.json).
The old m3 compact word is rejected as nonconjugate to the Johnson passage
order. Regenerating railroad crossings from the actual words gives 1878 mixed
crossings and connector counts `84,378,4,4,0`. Verify with
`python3 scripts/verify_t73_final_railroad_word_binding.py`.
The corrected target continues with
[`geometry/t73_actual_railroad_core_coordinates.json`](geometry/t73_actual_railroad_core_coordinates.json)
(1178 exact generic raw-passage core crossings),
[`geometry/t73_railroad_product_framings.json`](geometry/t73_railroad_product_framings.json)
(five zero-linking target push-offs), and
[`geometry/t73_source_bound_standard_pd_candidate.json`](geometry/t73_source_bound_standard_pd_candidate.json).
The latter has 4748 standard PD rows, 9496 arc labels, and 1785 passage-bound
dotted Hopf clasps. Its verdict is
`PASS_SOURCE_BOUND_STANDARD_PD_COMBINATORICS_ONLY`: target framings pass, but
the framed hybrid-to-railroad isotopy remains open. The rejected diagonal-only
closure is retained in
[`audit/t73_actual_railroad_standard_pd_gap.json`](audit/t73_actual_railroad_standard_pd_gap.json).
Three optional free-reduction endpoint-tube candidates are saved in
[`geometry/t73_final_free_reduction_bigons.json`](geometry/t73_final_free_reduction_bigons.json).
They identify one inverse pair on m3 and two nested pairs on r_zx using
disjoint z-foot endpoint tubes, but do not contain the central-connector
spanning surfaces. Rebuild/check with
`build_t73_final_free_reduction_bigons.py --check` and
`verify_t73_final_free_reduction_bigons.py`; verdict:
`PASS_FREE_REDUCTION_ENDPOINT_TUBES_ONLY`. They are not used by the raw-passage
kappa path.
The surviving framed 1-skeleton map is
[`geometry/t73_hybrid_to_railroad_graph_map.json`](geometry/t73_hybrid_to_railroad_graph_map.json).
It maps 1785 source vertices and 1785 connector edges bijectively onto all
raw-passage railroad event/segment cells, including all 1513 hybrid
replacements. Verify with
`verify_t73_hybrid_to_railroad_graph_map.py`. Verdict:
`PASS_HYBRID_TO_RAILROAD_FRAMED_GRAPH_ISOMORPHISM_ONLY`; ambient tracks remain
open.
The graph map extends over all five framed regular neighborhoods in
[`geometry/t73_hybrid_to_railroad_tubular_map.json`](geometry/t73_hybrid_to_railroad_tubular_map.json).
Its five solid-torus templates contain 5385 tetrahedra and 10770 boundary
triangles, with identity closing fiber maps and zero relative twists. Verify
with `verify_t73_hybrid_to_railroad_tubular_map.py`; only the handlebody
complement extension remains open.
The complement boundary data now include
[`geometry/t73_foot_to_dotted_slot_map.json`](geometry/t73_foot_to_dotted_slot_map.json)
and 1785 explicit reflection-paired paths in
[`geometry/t73_foot_to_dotted_disk_tracks.json`](geometry/t73_foot_to_dotted_disk_tracks.json).
Their verifier performs 2,455,940 exact fixed-point collision checks. These
tracks are thickened to explicit supported PL ambient isotopies in
[`geometry/t73_dotted_disk_ambient_extensions.json`](geometry/t73_dotted_disk_ambient_extensions.json).
The reusable corridor template has 36 spacetime tetrahedra per segment; its
3570 segment instances give 257040 reflection-paired physical tetrahedron
instances. Rebuild and independently verify with
`python3 scripts/build_t73_dotted_disk_ambient_extensions.py --write` and
`python3 scripts/verify_t73_dotted_disk_ambient_extensions.py`; verdict:
`PASS_REFLECTION_PAIRED_AMBIENT_DOTTED_DISK_EXTENSIONS`. This closes the local
foot-disk extension, not the source-to-railroad complement isotopy. Every
reduced source edge is also bound to its raw geometry in
[`geometry/t73_reduced_source_connector_provenance.json`](geometry/t73_reduced_source_connector_provenance.json):
1773 Johnson central connectors and 12 dual-boundary connectors partition all
1785 raw target edges one-to-one.
The exact native source-connector projection is too large for Git and is kept
at `C:\Users\Administrator\.cache\t73_actual_source_connector_projection.full.json`
(about 1.68 GB). Its compact receipt is
[`audit/t73_actual_source_connector_projection_receipt.json`](audit/t73_actual_source_connector_projection_receipt.json):
7116 segments, 4,791,364 broad candidates, and 1,758,060 exact crossings.
Regenerate with `build_t73_actual_source_connector_projection.py --write` and
stream/check with `build_t73_actual_source_connector_projection_receipt.py`.
The current source-native seven-component connector/local-Hopf PD skeleton is stored as SQLite at
`C:\Users\Administrator\.cache\t73_actual_source_standard_pd.sqlite`
(about 817 MB), with compact receipt
[`audit/t73_actual_source_standard_pd_sqlite_receipt.json`](audit/t73_actual_source_standard_pd_sqlite_receipt.json).
It has 1,761,630 crossings and 3,523,260 arc labels; those rows pass full integrity/incidence
check is `python3 scripts/verify_t73_actual_source_standard_pd_sqlite.py --full
--check-database-sha`. The actual core linking matrix has
`lk(m_2,m_3)=-318`, while dotted linking is `(40,269)` and `(189,1271)`.
Therefore the small zero-linking railroad target is not directly ambient
isotopic as a fixed seven-component S3 link. It may still be related by the
required dotted-handle/handlebody map, so this does not by itself refute
kappa_AR. It is no longer called a complete source-native PD: the explicit
post-x cache proves that 60,520 replacement core segments and their 60,520
push segments were omitted. The machine-readable gap is
[`audit/t73_source_pd_post_x_coverage_gap.json`](audit/t73_source_pd_post_x_coverage_gap.json),
verified by `python3 scripts/verify_t73_source_pd_post_x_coverage.py`. The
SQLite remains a valid connector/local-Hopf skeleton; full replacement-path
projection and source product framings remain open.
The corrected pieces are now assembled into five closed framed cycles in the
graph of verified charts at
[`geometry/t73_post_x_framed_cycle_assembly.json`](geometry/t73_post_x_framed_cycle_assembly.json).
It exhausts 3558 blocks and gives matching 68176-edge core and push cycles;
every abstract vertex has one incoming and one outgoing block. Rebuild/check
with `python3 scripts/build_t73_post_x_framed_cycle_assembly.py --check` and
`python3 scripts/verify_t73_post_x_framed_cycle_assembly.py`. This closes
combinatorial cycle incidence, not the cancellation-complement embedding into
one S3 chart.
The x/m1 collar now has an explicit x-product extension in
[`geometry/t73_x_m1_collar_product_extension.json`](geometry/t73_x_m1_collar_product_extension.json):
36 transverse tetrahedra become 144 orientation-preserving 4-simplices. It
covers all 12104 remaining local core segments and 6052 band-lane segments.
The verifier also finds 4768 original local push-lane segments entering the
deleted inner cube; the previously verified uniform outward framing repairs
all of them and puts 12104+6052 pushed segments in the collar domain. Run
`python3 scripts/build_t73_x_m1_collar_product_extension.py --check` and
`python3 scripts/verify_t73_x_m1_collar_product_extension.py`. Piecewise-affine
images of the full hybrid paths remain to be emitted.
Those nontrivial images are now stored at
`C:\Users\Administrator\.cache\t73_x_m1_ejected_band_lanes.jsonl.gz`
(about 58.2 MB), with receipt
[`audit/t73_x_m1_ejected_band_lanes_receipt.json`](audit/t73_x_m1_ejected_band_lanes_receipt.json).
The exact product-simplex intersections subdivide 12104 core/outward-push lane
segments into 30144 affine image segments. Full verification recomputes every
barycentric containment, source interpolation, target image and adjacency:
`python scripts/verify_t73_x_m1_ejected_band_lanes.py --full --input-cache
C:\Users\Administrator\.cache\t73_post_x_framed_replacement_cells.jsonl.gz
--check-cache-sha`. The four splice-end segments per replacement are also
mapped in `C:\Users\Administrator\.cache\t73_x_m1_ejected_splice_stubs.jsonl.gz`
(about 6.3 MB), with receipt
[`audit/t73_x_m1_ejected_splice_stubs_receipt.json`](audit/t73_x_m1_ejected_splice_stubs_receipt.json).
Its 12104 core+push source stubs give 25712 affine image segments. Full check:
`python scripts/verify_t73_x_m1_ejected_splice_stubs.py --full --input-cache
C:\Users\Administrator\.cache\t73_post_x_framed_replacement_cells.jsonl.gz
--check-cache-sha`. The middle 48416 core and 48416 push m1-complement
segments are outside these local germs; F-592/F-593 below construct the full
tubular map needed to transport them.
The first full-curve tubular layer is
[`geometry/t73_m1_parallel_annulus_tubular_frame.json`](geometry/t73_m1_parallel_annulus_tubular_frame.json).
A common rational outward vector is transverse to the tangent/parallel frame
on all 34 m1 segments; 68 annulus triangles give 204 nondegenerate tubular
tetrahedra, and 274 exact quotient checks separate the source and pushed
annuli. Verify with `python3
scripts/verify_t73_m1_parallel_annulus_tubular_frame.py`. Exact nonincident
tetrahedron clearance now passes and is recorded in
[`audit/t73_m1_parallel_annulus_tubular_clearance_receipt.json`](audit/t73_m1_parallel_annulus_tubular_clearance_receipt.json):
573 exact rational convex-hull feasibility checks find no nonincident
tetrahedron intersection in the quotient. Verdict:
`PASS_M1_PARALLEL_ANNULUS_NONINCIDENT_TETRAHEDRON_CLEARANCE`. The tube can now
be used to transport the 48416 middle complement segments.
The compactly supported ambient ejection itself is
[`geometry/t73_m1_parallel_annulus_ambient_ejection.json`](geometry/t73_m1_parallel_annulus_ambient_ejection.json).
Its PL interval map sends levels `(-1,0,2)` to `(-1,1,2)`, fixes both support
boundaries, and has 408 orientation-preserving tetrahedra. The full receipt
[`audit/t73_m1_parallel_annulus_ambient_ejection_receipt.json`](audit/t73_m1_parallel_annulus_ambient_ejection_receipt.json)
records 2100 exact nonincident convex-hull checks and verdict
`PASS_M1_PARALLEL_ANNULUS_AMBIENT_EJECTION_SUPPORT_CLEARANCE`. Its application
is stored at
`C:\Users\Administrator\.cache\t73_x_m1_ejected_middle_complements.jsonl.gz`
(about 53.2 MB), with receipt
[`audit/t73_x_m1_ejected_middle_complements_receipt.json`](audit/t73_x_m1_ejected_middle_complements_receipt.json).
All 48416 middle core and 48416 product-push segments pass 99858 vertex-image
checks and cache SHA verification. Full command: `python
scripts/verify_t73_x_m1_ejected_middle_complements.py --full --input-cache
C:\Users\Administrator\.cache\t73_post_x_framed_replacement_cells.jsonl.gz
--check-cache-sha`. Together with F-590/F-591, all 60520 replacement core
segment images now exist blockwise. Their 3026 local/global endpoint pairs use
different target charts and still lack an extended transition for both core
and push. This fail-closed gap is
[`audit/t73_x_m1_ejection_overlap_transition_gap.json`](audit/t73_x_m1_ejection_overlap_transition_gap.json).
It is now resolved in the graph of charts by
`C:\Users\Administrator\.cache\t73_x_m1_ejection_overlap_transitions.jsonl.gz`
(about 1.86 MB), with receipt
[`audit/t73_x_m1_ejection_overlap_transitions_receipt.json`](audit/t73_x_m1_ejection_overlap_transitions_receipt.json).
The 3026 disjoint framed mapping-cylinder germs contain 18156 tetrahedra and
match all 3026 core and push boundary pairs. Full check: `python
scripts/verify_t73_x_m1_ejection_overlap_transitions.py --full --stub-cache
C:\Users\Administrator\.cache\t73_x_m1_ejected_splice_stubs.jsonl.gz
--middle-cache C:\Users\Administrator\.cache\t73_x_m1_ejected_middle_complements.jsonl.gz
--check-cache-sha`. Charted-cycle continuity now passes; conversion to one
affine dotted-S3 chart remains open.
The complete merged x/m1 result is
[`geometry/t73_x_m1_complete_framed_cancellation_image.json`](geometry/t73_x_m1_complete_framed_cancellation_image.json).
It binds the persisted full overlap verification and assembles five closed
atlas cycles: 68176 source core edges become 81812 target core and 86188 target
push edges after exact subdivision. Verify with `python3
scripts/verify_t73_x_m1_complete_framed_cancellation_image.py`; verdict:
`PASS_COMPLETE_X_M1_FRAMED_CANCELLATION_IMAGE_IN_ATLAS`. The next operation is
the y/z dotted-handle conversion followed by a single affine-S3 realization.
The exhaustive y/z substitution table is
[`geometry/t73_yz_dotted_passage_replacement_map.json`](geometry/t73_yz_dotted_passage_replacement_map.json).
It locates the two-segment base-18--20 z subpath inside every one of the 1513
x-replacement middles and binds all 272 other Johnson/bottom/dual passages.
Thus 3590 source core/push segments are replaced by 1785 framed Hopf segments,
giving projected post-conversion counts core=80007 and push=84383. Verify with
`python3 scripts/verify_t73_yz_dotted_passage_replacement_map.py`. The 1785
framed passage mapping cylinders are the next gate.
They are stored at
`C:\Users\Administrator\.cache\t73_yz_framed_passage_mapping_cylinders.jsonl.gz`
(about 1.87 MB), with construction and full-verification receipts in
[`audit/t73_yz_framed_passage_mapping_cylinders_receipt.json`](audit/t73_yz_framed_passage_mapping_cylinders_receipt.json)
and
[`audit/t73_yz_framed_passage_mapping_cylinders_verification.json`](audit/t73_yz_framed_passage_mapping_cylinders_verification.json).
All 21540 tetrahedra and 1785 disjoint supports pass. The resulting seven-
component atlas is
[`geometry/t73_complete_framed_dotted_atlas.json`](geometry/t73_complete_framed_dotted_atlas.json):
80007 framed-core edges, 84383 push edges and two four-edge dotted polygons.
Verdict: `PASS_COMPLETE_SEVEN_COMPONENT_FRAMED_DOTTED_ATLAS`. A single affine
S3 chart and its complete PD remain open.
The core part of that realization is now one affine chart in
[`geometry/t73_affine_s3_core_realization.json`](geometry/t73_affine_s3_core_realization.json).
It retains all 7092 actual Johnson connector segments, inserts all 1785 local
Hopf arcs, and uses 3558 four-segment exterior corridors, for 23109 core
segments. The full receipt
[`audit/t73_affine_s3_core_realization_verification.json`](audit/t73_affine_s3_core_realization_verification.json)
records 25,318,728 exact waypoint/endpoint-fiber incidence checks and verdict
`PASS_CANONICAL_AFFINE_S3_CORE_EMBEDDING`. Affine push corridors, hence
integer framings and the complete framed PD, remain open.
The five affine push cycles are now included in
[`geometry/t73_affine_s3_framed_realization.json`](geometry/t73_affine_s3_framed_realization.json).
It has 23109 core and 23109 push segments plus the two dotted components. Its
full receipt
[`audit/t73_affine_s3_framed_realization_verification.json`](audit/t73_affine_s3_framed_realization_verification.json)
records 50,637,456 push-waypoint/fiber checks and 4,567,172 exact nonincident
endpoint-fiber/base-segment checks. Verdict:
`PASS_CANONICAL_AFFINE_S3_FRAMED_LINK_EMBEDDING`. This proves five disjoint
companion cycles, but not yet the product framing: the 3558 independently
routed push corridors have no ruled ribbons to the core corridors. The
fail-closed correction is
[`audit/t73_affine_push_corridor_framing_gap.json`](audit/t73_affine_push_corridor_framing_gap.json).
Corridor product ribbons must be built before projection or integer framing.
A local repair is now cached at
`C:\Users\Administrator\.cache\t73_affine_s3_product_framed_realization.json`
(112,997,433 bytes), with receipt
[`audit/t73_affine_s3_product_framed_realization_receipt.json`](audit/t73_affine_s3_product_framed_realization_receipt.json).
It linearly interpolates the verified endpoint product normals along every
core corridor, giving 28464 ruled triangles; all 7116 endpoint matches and
28464 local transversality checks pass. Run
`python3 scripts/verify_t73_affine_s3_product_framed_realization.py`. Exact
nonlocal clearance now passes in
[`audit/t73_affine_s3_product_ribbon_global_clearance.json`](audit/t73_affine_s3_product_ribbon_global_clearance.json).
After shrinking only the three interior corridor normals by `1/1000` while
fixing all endpoint product normals, 1779 exact triangle/triangle and 3560
exact segment/triangle survivors are disjoint. Verdict:
`PASS_AFFINE_S3_PRODUCT_CORRIDOR_RIBBON_GLOBAL_CLEARANCE`. The five affine
companions are now certified product push-offs.
Their exact affine-model self-linkings are saved in
[`geometry/t73_verified_integer_surgery_framings.json`](geometry/t73_verified_integer_surgery_framings.json):
`m_2=-156621`, `m_3=-3338112`, `r_xy=-1`, `r_yz=-1`, `r_zx=-3`.
The five component databases are under `C:\Users\Administrator\.cache\` as
`t73_product_self_linking_*.sqlite`; m3 is about 4.30 GB. All 25,776,472
crossings and database SHAs were independently replayed in
[`audit/t73_product_self_linking_full_verification.json`](audit/t73_product_self_linking_full_verification.json).
Run `python3 scripts/verify_t73_verified_integer_surgery_framings.py`; verdict:
`PASS_FIVE_AFFINE_MODEL_PRODUCT_SELF_LINKINGS_ONLY`. The ten model pairwise
core linkings are also fully replayed in
[`audit/t73_pairwise_core_linking_full_verification.json`](audit/t73_pairwise_core_linking_full_verification.json).
Together they form a seven-component dotted-surgery matrix with determinant
`-3` and Smith diagonal `(1,1,1,1,1,1,3)`, predicting boundary H1=`Z/3`.
This contradicts the required post-2-handle boundary that three 3-handles can
turn into S3. Therefore these exact values describe the constructed affine
model but are not valid T73 surgery framings; see
[`audit/t73_affine_kirby_matrix_homology_obstruction.json`](audit/t73_affine_kirby_matrix_homology_obstruction.json).
The exact repair target and its realized local PL correction are recorded in
[`geometry/t73_kirby_homology_admissible_correction.json`](geometry/t73_kirby_homology_admissible_correction.json)
and
[`geometry/t73_dual_zero_framing_twist_ribbons.json`](geometry/t73_dual_zero_framing_twist_ribbons.json).
Because the dotted-incidence block has determinant `-1`, retaining every core
and off-diagonal linking uniquely forces the three dual framings to zero. The
scripts insert rational square-normal twists `+1,+1,+3`; all 144 exact
self-linking crossings replay to zero, and 40 new ribbon triangles pass an
incremental global check against 32,028 retained ribbon triangles and 46,260
framed segments. The aggregate
[`geometry/t73_homology_admissible_affine_framed_model.json`](geometry/t73_homology_admissible_affine_framed_model.json)
has rank `4`, nullity `3`, signature `0`, and Smith diagonal
`(1,1,1,1,0,0,0)`. Verdict:
`PASS_HOMOLOGY_ADMISSIBLE_AFFINE_FRAMED_MODEL_ONLY`; the relative T73
meridian/longitude equivalence remains open. In addition, the coverage gate
[`audit/t73_affine_core_atlas_coverage_gap.json`](audit/t73_affine_core_atlas_coverage_gap.json)
shows that this is a skeleton model: it contains 7,092 retained connector,
1,785 dotted-passage and 14,232 substitute corridor segments, but none of the
60,520 explicit post-x replacement core segments (and 60,520 pushes) required
by the 80,007/84,383-segment complete atlas. Therefore its homology PASS is not
a complete-T73 PD PASS. Rebuild and verify with:

```bash
python3 scripts/build_t73_kirby_homology_admissible_correction.py --write
python3 scripts/build_t73_dual_zero_framing_twist_ribbons.py --write
python3 scripts/build_t73_dual_zero_framing_twist_global_clearance_receipt.py
python3 scripts/build_t73_homology_admissible_affine_framed_model.py --write
python3 scripts/verify_t73_homology_admissible_affine_framed_model.py
python3 scripts/audit_t73_affine_core_atlas_coverage.py --check
python3 scripts/verify_t73_affine_core_atlas_coverage_gap.py
```

The first coverage-repair stage is now materialized outside Git at
`C:\Users\Administrator\.cache\t73_x_m1_complete_explicit_replacement_images.jsonl.gz`
(68,417,260 bytes), with construction and full independent replay receipts in
[`audit/t73_x_m1_complete_explicit_replacement_images_receipt.json`](audit/t73_x_m1_complete_explicit_replacement_images_receipt.json)
and
[`audit/t73_x_m1_complete_explicit_replacement_images_verification.json`](audit/t73_x_m1_complete_explicit_replacement_images_verification.json).
All 1,513 replacement blocks are reconstructed from the lane, splice-stub,
middle-complement and overlap-transition streams. The result has 77,182 core
and 81,558 push segments, including 6,052 explicit transition center tracks;
24,208 piece-boundary matches and the full cache SHA were independently
replayed. This closes fragmented 4D-atlas assembly, not the common 3-manifold
chart. Rebuild in WSL with:

```bash
python3 scripts/build_t73_x_m1_complete_explicit_replacement_images.py \
  --output /mnt/c/Users/Administrator/.cache/t73_x_m1_complete_explicit_replacement_images.jsonl.gz
python3 scripts/build_t73_x_m1_complete_explicit_replacement_images_verification.py
```

The 48,416-segment middle-complement portion is now mapped source-relatively
into an explicit rational R3 solid torus. The chart
[`geometry/t73_x_m1_canonical_r3_annulus_chart.json`](geometry/t73_x_m1_canonical_r3_annulus_chart.json)
has 204 quotient vertices, 408 nondegenerate tetrahedra, and a connected
408-triangle torus boundary. The mapped stream is cached at
`C:\Users\Administrator\.cache\t73_x_m1_middle_paths_r3.jsonl.gz`; its
construction/full-replay receipts are
[`audit/t73_x_m1_middle_paths_r3_receipt.json`](audit/t73_x_m1_middle_paths_r3_receipt.json)
and
[`audit/t73_x_m1_middle_paths_r3_verification.json`](audit/t73_x_m1_middle_paths_r3_verification.json).
All 99,858 source Q4 core/push points recover unique quotient angular indices;
1,511 paths run forward and two backward. The 96,832 rational framing-ribbon
triangles lie in 1,513 pairwise-disjoint radial strips. The remaining R3 work
is exactly the splice stubs, band lanes, and overlap tracks. Rebuild with:

```bash
python3 scripts/build_t73_x_m1_canonical_r3_annulus_chart.py --write
python3 scripts/build_t73_x_m1_middle_paths_r3.py \
  --output /mnt/c/Users/Administrator/.cache/t73_x_m1_middle_paths_r3.jsonl.gz
python3 scripts/build_t73_x_m1_middle_paths_r3_verification.py
```

A literal endpoint audit then found and repaired a separate framing interface.
All 3,026 replacement core ports equal their adjacent Johnson-connector or
dual-passage endpoint modulo the mapping-torus deck, but none of their push
ports initially matched: the four mismatch classes have counts
`2480,538,4,4`. See
[`audit/t73_post_x_connector_stub_framing_gap.json`](audit/t73_post_x_connector_stub_framing_gap.json).
The cache
`C:\Users\Administrator\.cache\t73_post_x_connector_stub_framing_transitions.jsonl.gz`
now contains 3,026 explicit (1/10^6)-collar normal homotopies and 12,104
ruled ribbon triangles. All 6,052 endpoint-normal matches, 12,104 transverse
normal tests, zero total relative twist and the full cache SHA replay in
[`audit/t73_post_x_connector_stub_framing_transitions_verification.json`](audit/t73_post_x_connector_stub_framing_transitions_verification.json).
Verdict: `PASS_POST_X_CONNECTOR_STUB_FRAMING_TRANSITIONS_FULL_LOCAL`; global
transition-ribbon clearance is recorded in
[`audit/t73_post_x_connector_stub_framing_transition_global_clearance.json`](audit/t73_post_x_connector_stub_framing_transition_global_clearance.json).
After replacing exactly 3,026 old product segments, the verifier checks 12,104
new triangles against 8,164 retained product-ribbon triangles and 20,268
corrected framed segments. It reduces about 17 million broad candidates in
each phase to 4,527 exact rational intersection tests; all are disjoint.
Verdict: `PASS_POST_X_CONNECTOR_STUB_FRAMING_TRANSITION_GLOBAL_CLEARANCE`.

Global linear projection probes are recorded in
[`audit/t73_affine_s3_projection_probe.json`](audit/t73_affine_s3_projection_probe.json).
xz/yz collapse dotted edges; three regular tilts produce at least 258,453,247
broad candidates. The selected next route is piecewise diagram assembly from
the already verified central, Hopf and corridor chart projections.
The three missing pre-cancellation dual-cell product ribbons are now explicit
in [`geometry/t73_actual_dual_product_ribbons.json`](geometry/t73_actual_dual_product_ribbons.json).
Each planar dual boundary has an eight-quadrilateral/16-triangle annulus to a
rational normal push-off; the translated spanning disk proves source
self-linking zero. Rebuild with
`python3 scripts/build_t73_actual_dual_product_ribbons.py --write` and verify
with `python3 scripts/verify_t73_actual_dual_product_ribbons.py`. The x-slide
transport into the post-cancellation source-native PD is still open.
All 1513 post-x framed replacement cells are expanded, rather than retained
only as hashes, in the WSL cache
`/home/lifesize/.cache/t73_post_x_framed_replacement_cells.jsonl.gz` (about
36.3 MB). The committed receipt is
[`audit/t73_post_x_framed_replacement_cells_receipt.json`](audit/t73_post_x_framed_replacement_cells_receipt.json).
It covers 6052 band triangles and 77163 exact normal/push vertices, including
the two retained source stubs of every replacement. Rebuild
with `python3 scripts/build_t73_post_x_framed_replacement_cells.py`; use
`python3 scripts/verify_t73_post_x_framed_replacement_cells.py --full
--check-cache-sha` for the full streamed verification. These cells remain in
their rigorously glued global/local charts; the unified S3 push-off projection
and five integer diagonal framings are the next gate.
The local dotted-handle replacement itself is now geometric in
[`geometry/t73_actual_dotted_s3_passage_cells.json`](geometry/t73_actual_dotted_s3_passage_cells.json).
Two disjoint oriented dotted rectangles contain all 1785 ordered framed Hopf
passages and 3570 ribbon triangles. Its 3570 exact local crossings reproduce
the source-native SQLite linking values `(40,269)` for m2 and `(189,1271)` for
m3, with zero dual-component dotted linking. Rebuild/check with
`python3 scripts/build_t73_actual_dotted_s3_passage_cells.py --check` and
`python3 scripts/verify_t73_actual_dotted_s3_passage_cells.py`. Exterior
The four framed marked-strip mapping cylinders that glue the physical feet to
these local charts are stored in
[`geometry/t73_dotted_s3_foot_collars.json`](geometry/t73_dotted_s3_foot_collars.json).
They contain 24 tetrahedra and match all 3570 core endpoints and all 3570 push
endpoints, including the Figure-2a reflections. Rebuild/verify with
`python3 scripts/build_t73_dotted_s3_foot_collars.py --check` and
`python3 scripts/verify_t73_dotted_s3_foot_collars.py`. The remaining gluing
problem is the central connector complement, not the marked foot strips.
The exact actual connector/product-push crossing ledger for m2 and m3 is the
SQLite cache
`C:\Users\Administrator\.cache\t73_actual_source_connector_push_projection.sqlite`
(about 579 MB), bound by
[`audit/t73_actual_source_connector_push_projection_receipt.json`](audit/t73_actual_source_connector_push_projection_receipt.json).
It contains 2,528,401 crossings reconstructed from 6,936,192 broad candidates.
The connector-only signed sums are `-345` for m2 and `-1206` for m3. The odd
m2 sum is a fail-closed proof that these open connector cells cannot yet define
an integer framing; band-splice/collar contributions must be added. Rebuild
with `python scripts/build_t73_actual_source_connector_push_projection.py
--output C:\Users\Administrator\.cache\t73_actual_source_connector_push_projection.sqlite`;
full verification is `python
scripts/verify_t73_actual_source_connector_push_projection.py --full
--check-database-sha`.

Separately, the C-cut 44-lane candidate realization is
[`geometry/t73_y_foot_lane_candidate.json`](geometry/t73_y_foot_lane_candidate.json):
44 actual y-cut passages are bound to distinct rational y-foot targets and
product-normal framing rectangles. Rebuild/check it with:

```text
python3 scripts/build_t73_y_foot_lane_candidate.py --check
python3 scripts/verify_t73_y_foot_lane_candidate.py
```

Its verifier reports `PASS_CANDIDATE_PL_DISJOINTNESS_ONLY`; this is not an actual
AR relative Kirby movie.

The six-step t-cancellation candidate movie is
[`geometry/t73_candidate_t_band_movie.json`](geometry/t73_candidate_t_band_movie.json),
rebuilt with `python3 scripts/build_t73_candidate_t_band_movie.py --check`.
It records rectangle segments, attachments, splice descriptors and ordered
candidate link states without claiming an actual Kirby cancellation.
The six source/target attachment endpoints that are genuinely recoverable
from the AR records are saved separately in
[`geometry/t73_t_band_attachment_locators.json`](geometry/t73_t_band_attachment_locators.json),
rebuilt with `python3 scripts/build_t73_t_band_attachment_locators.py --check`.
Its scope is `VERIFIED_ENDPOINTS_ONLY`.
Canonical rational intervals around these locators are saved in
[`geometry/t73_t_band_attachment_intervals.json`](geometry/t73_t_band_attachment_intervals.json),
rebuilt with `python3 scripts/build_t73_t_band_attachment_intervals.py --check`.
The locator is verified; the width-based interval choice remains candidate.
`python3 scripts/verify_t73_t_band_attachment_intervals.py` independently
proves that all six source intervals lie on actual lambda/mu core edges and
all target intervals lie on their parallel h_CS lines, reporting
`PASS_T_INTERVAL_ACTUAL_EDGE_BINDING_CANDIDATE_WIDTH`.
`verify_t73_t_band_parallel_hcs_targets.py` proves the six target lines are
actual framed h_CS parallels with ordered coefficients
`[-25,-15,-5,5,15,25]`, reporting `PASS_ACTUAL_HCS_PARALLEL_TARGET_BINDING`.
Boundary-compatible normal homotopies for all six t-bands are saved in
[`geometry/t73_t_band_framing_extensions.json`](geometry/t73_t_band_framing_extensions.json).
Rebuild and independently check them with
`build_t73_t_band_framing_extensions.py --check` and
`verify_t73_t_band_framing_extensions.py`. The interior interpolation remains
candidate; the source and h_CS boundary framings are actual-record bindings.
The corresponding six rational PL disks in the actual octahedral t-belt
collar are saved in
[`geometry/t73_t_band_collar_surfaces.json`](geometry/t73_t_band_collar_surfaces.json).
Rebuild and check them with
`python3 scripts/build_t73_t_band_collar_surfaces.py --check` and
`python3 scripts/verify_t73_t_band_collar_surfaces.py`. Each disk is locally
embedded and has the exact source/target intervals, but the six slides are
sequential, not simultaneous: after the current-link-safe rational reroutes,
the verifier records residual surface intersections for band pairs `(0,2)`,
`(0,4)`, `(1,4)`, and `(2,4)` at distinct movie times. The verdict
`PASS_T_BAND_COLLAR_DISKS_SEQUENTIAL_CANDIDATE_FRAMING_ONLY` does not yet
certify current-link replay or an actual Kirby equivalence.
The first genuine sequential state transition built from that collar data is
[`geometry/t73_t_band_sequential_state_01.json`](geometry/t73_t_band_sequential_state_01.json).
Reproduce it with `python3 scripts/build_t73_t_band0_sequential_state.py --check`
and verify it with `python3 scripts/verify_t73_t_band0_sequential_state.py`.
The latter independently rebuilds every splice piece, checks quotient
embeddedness, the framed push-off, both attachment-only contacts, clearance
from every stationary component, and exact recovery of the refined source
lift by the inverse move. Its verdict is
`PASS_T_BAND0_SEQUENTIAL_FRAMED_KIRBY_SLIDE`; only state `0 -> 1` is covered.
The compact, replayable delta movie for all six slides is
[`geometry/t73_t_band_sequential_movie.json`](geometry/t73_t_band_sequential_movie.json).
Use `python3 scripts/build_t73_t_band_sequential_movie.py --check` and
`python3 scripts/verify_t73_t_band_sequential_movie.py`. It uniquely rebinds
each source interval in its immediately preceding state, handles wrapped
interval deck lifts and both seam orientations, propagates inherited seams,
checks each disk/new framed curve against the current link and actual dual-core
spatial projections, and verifies every inverse. The result is
`PASS_SIX_T_BAND_SEQUENTIAL_FRAMED_KIRBY_SLIDES`. The JSON stores replay deltas
and content hashes instead of duplicating tens of megabytes of normal vectors.
The next cancellation gate is saved in
[`audit/t73_t_hcs_cancellation_readiness.json`](audit/t73_t_hcs_cancellation_readiness.json).
The original state-6 push-offs had four segments entering the open t-ball.
[`geometry/t73_t_hcs_framing_exteriorization.json`](geometry/t73_t_hcs_framing_exteriorization.json)
records 63 canonical outward normal replacements. Rebuild/check with
`build_t73_t_hcs_framing_exteriorization.py --check`,
`verify_t73_t_hcs_framing_exteriorization.py`, and
`build_t73_t_hcs_cancellation_readiness.py --check`. The exact verdicts are
`PASS_STATE6_FRAMING_EXTERIORIZATION` and
`READY_FOR_EXPLICIT_T_HCS_CANCELLATION_MAP`; the cellwise cancellation map is
still required.
The finite pre-cancellation collar map is
[`geometry/t73_t_hcs_collar_ejection_map.json`](geometry/t73_t_hcs_collar_ejection_map.json).
Rebuild/check it with `build_t73_t_hcs_collar_ejection_map.py --check` and
`verify_t73_t_hcs_collar_ejection_map.py`. Its 24 orientation-preserving
tetrahedra push the inner octahedron from `r` to `3r/2` while fixing `2r`, and
the verifier returns `PASS_T_HCS_COLLAR_EJECTION_CELL_MAP`. This is the collar
ejection layer.
The completed standard-pair deletion and carried post-link manifest are in
[`geometry/t73_t_hcs_handle_pair_deletion.json`](geometry/t73_t_hcs_handle_pair_deletion.json).
Run `build_t73_t_hcs_handle_pair_deletion.py --check`, then run
`verify_t73_t_hcs_handle_pair_deletion.py` with the topology venv. It verifies
the staircase triangulations of `Delta1 x Delta3` and `Delta2 x Delta2`, their
three-tetrahedron attaching 3-ball, the resulting PL 4-ball/S3 boundary, the
actual barycentric belt crossing and AR framing, and the six-component
post-cancel manifest. Verdict:
`PASS_T_HCS_HANDLE_PAIR_DELETION_AND_POST_LINK_STATE`.
The first x-slide attachment layer is
[`geometry/t73_x_band0_attachment_surface.json`](geometry/t73_x_band0_attachment_surface.json).
Rebuild and check it with `build_t73_x_band0_attachment_surface.py --check`
and `verify_t73_x_band0_attachment_surface.py`. It binds `c1:letter:0` to the
post-cancel m2 vertex range `[20,22]` in deck `[269,40,0]`, binds the target to
the twentieth framed m1 parallel, and verifies a six-vertex PL disk. Its
derived boundary-framing verdict is
`PASS_X_BAND0_ACTUAL_ATTACHMENTS_AND_BOUNDARY_FRAMING`.
The complete local obstacle state is
[`geometry/t73_x_positive_belt_state0.json`](geometry/t73_x_positive_belt_state0.json):
one cancelling m1 arc, 1509 Johnson arcs, and four dual passages. Run
`build_t73_x_positive_belt_state0.py --check` and
`verify_t73_x_band0_current_link_clearance.py`; 24,232 exact tests give
`PASS_X_BAND0_CURRENT_LINK_AND_PUSH_CLEARANCE`.
The two actual affine chart germs and framing transport are saved in
[`geometry/t73_x_band0_chart_transitions.json`](geometry/t73_x_band0_chart_transitions.json)
and verified by `verify_t73_x_band0_chart_transitions.py`.
The complete twentieth m1 parallel is
[`geometry/t73_x_band0_m1_parallel.json`](geometry/t73_x_band0_m1_parallel.json),
verified by `verify_t73_x_band0_m1_parallel.py`. The oriented band uses the
noncollapsing half-vector rotation `+e_x -> -e_nu -> -e_x`, so its inserted m1
passage has sign `-1` and cancels the source sign `+1`.
The resulting global/local state transition is
[`geometry/t73_x_band_hybrid_state_0000_0001.json`](geometry/t73_x_band_hybrid_state_0000_0001.json).
Rebuild/check it with `build_t73_x_band0_hybrid_state.py --check` and
`verify_t73_x_band0_hybrid_state.py`; the verdict is
`PASS_X_BAND0_HYBRID_FRAMED_STATE_0_TO_1`.
All 1513 positive-belt local state deltas are saved compactly in
[`geometry/t73_x_band_local_movie.json`](geometry/t73_x_band_local_movie.json).
Rebuild them with `python3 scripts/build_t73_x_band_local_movie.py --check`.
The full current-segment replay is
`python3 scripts/verify_t73_x_band_local_movie.py`; set `T73_PROGRESS=1` for
progress output. It verifies 1514 states, including every retained source
stub, band lane, and m1-parallel stub, and returns
`PASS_ALL_1513_X_LOCAL_FRAMED_BAND_STATES`. The first full run is hash-bound in
[`audit/t73_x_band_local_movie_verification.json`](audit/t73_x_band_local_movie_verification.json).
Daily tests use `python3 scripts/build_t73_x_band_local_movie_receipt.py --check`;
receipt regeneration requires explicit `--write --full`. This receipt covers
the local state layer; the component-level hybrid movie below covers all
global splices.
Every orientation-rotation midpoint uses the outward movie height
`nu=1+(band_index+1)*width`; its two cross-section vertices therefore remain at
or outside the transverse D3 boundary. The receipt was regenerated by a full
1513-state replay after this correction.
All target parallels are nevertheless now global: the single quotient annulus
[`geometry/t73_x_m1_parallel_foliation.json`](geometry/t73_x_m1_parallel_foliation.json)
contains levels `20,40,...,30260`. Rebuild/check it with
`build_t73_x_m1_parallel_foliation.py --check` and
`verify_t73_x_m1_parallel_foliation.py`. The latter returns
`PASS_ALL_1513_M1_PARALLELS_IN_EMBEDDED_QUOTIENT_ANNULUS`; four mapping-torus
seam triangles are treated as gluing cells, not affine triangles.
All source-side global chart germs are saved in
[`geometry/t73_x_source_chart_germs.json`](geometry/t73_x_source_chart_germs.json).
Rebuild/check with `build_t73_x_source_chart_germs.py --check` and
`verify_t73_x_source_chart_germs.py`. It locates 1509 Johnson top arcs and four
oriented dual-disk boundary arcs uniquely in their actual components, returning
`PASS_ALL_1513_X_SOURCE_CHART_GERMS` without assuming `nu=u`.
The complete component-level atlas movie is
[`geometry/t73_x_band_hybrid_movie.json`](geometry/t73_x_band_hybrid_movie.json).
Rebuild/check it with `build_t73_x_band_hybrid_movie.py --check` and
`verify_t73_x_band_hybrid_movie.py`. It verifies 1513 replacement cells, 6052
chart gluings, 1513 inverses, and all component Merkle states, returning
`PASS_ALL_1513_X_HYBRID_PIECE_WORD_STATES`. Chart-typed cell replacements are
used deliberately; no false global coordinate identification is introduced.
The second cancelling pair is now explicit. The core collar map
[`geometry/t73_x_m1_collar_ejection_map.json`](geometry/t73_x_m1_collar_ejection_map.json)
and framing exteriorization
[`geometry/t73_x_m1_framing_exteriorization.json`](geometry/t73_x_m1_framing_exteriorization.json)
return `PASS_X_M1_CORE_COLLAR_EJECTION_MAP` and
`PASS_X_FINAL_LINK_UNIFORM_OUTWARD_FRAMING`. The standard 4-ball deletion and
five-component output are
[`geometry/t73_x_m1_handle_pair_deletion.json`](geometry/t73_x_m1_handle_pair_deletion.json).
Run its builder, then run `verify_t73_x_m1_handle_pair_deletion.py` with the
topology environment; verdict:
`PASS_X_M1_HANDLE_PAIR_DELETION_AND_FIVE_COMPONENT_STATE`.
The first end-to-end candidate slide, including an explicit closed post-slide
4D core, is
[`geometry/t73_candidate_t_band0_splice.json`](geometry/t73_candidate_t_band0_splice.json),
rebuilt with `python3 scripts/build_t73_candidate_t_band0_splice.py --check`.
Its scope is `CANDIDATE_CLOSED_SPLICE_ONLY` pending intersection and Kirby-move checks.
The complete candidate band disk between the two attachment intervals is
[`geometry/t73_candidate_t_band0_surface.json`](geometry/t73_candidate_t_band0_surface.json),
rebuilt with `build_t73_candidate_t_band0_surface.py --check` and independently
checked by `verify_t73_candidate_t_band0_surface.py`. It is an 8-vertex,
6-triangle framed disk with the four declared boundary parts. Exact
barycentric and edge-triangle checks give
`PASS_CANDIDATE_FRAMED_BAND_DISK_AND_PUSH_LOCAL_EMBEDDEDNESS_ONLY`, including
the push-off surface and all disk-versus-push triangle pairs.
`verify_t73_candidate_t_band0_surface_clearance.py` checks the disk and push
disk against all five other cores; all 128184 quotient AABB pairs are exactly
disjoint, giving `PASS_CANDIDATE_BAND_SURFACE_OTHER_CORE_CLEARANCE_ONLY`.
`verify_t73_candidate_t_band0_relative_boundary.py` then checks the actual
source interval, parallel h_CS target interval, both movie lanes and their
boundary normals, reporting `PASS_CANDIDATE_BAND0_RELATIVE_BOUNDARY_ONLY`.
`verify_t73_candidate_t_band0_relative_contacts.py` solves exact
segment-triangle intersection intervals and proves every m1/h_CS contact lies
on those two attachment edges, reporting
`PASS_CANDIDATE_BAND0_RELATIVE_CONTACTS_ONLY`.
`python3 scripts/verify_t73_candidate_t_band0_splice.py` currently returns
`OPEN_PERIODIC_T3_LIFT_REQUIRED`: the saved source core uses wrapped torus
coordinates and must be lifted before affine PL intersection tests are valid.
The verified continuous lifts are saved in
[`geometry/t73_ar_core_universal_lifts.json`](geometry/t73_ar_core_universal_lifts.json),
rebuilt with `python3 scripts/build_t73_ar_core_universal_lifts.py --check`.
Their closing deck translations are exactly the columns of `A-I`.
The quotient-aware reconstruction of the first t-band splice is
[`geometry/t73_candidate_t_band0_quotient_splice.json`](geometry/t73_candidate_t_band0_quotient_splice.json),
rebuilt with `python3 scripts/build_t73_candidate_t_band0_quotient_splice.py --check`.
Its universal-cover endpoints differ by the verified m1 deck translation.
The independent quotient verifier is
`python3 scripts/verify_t73_candidate_t_band0_quotient_splice.py`; it treats
the unique `u=0~1` mapping-torus seam as a gluing cell and reports
`PASS_CANDIDATE_QUOTIENT_FRAMED_EMBEDDEDNESS_ONLY` after checking both the
remaining PL segments and their boundary-compatible push-off.
`python3 scripts/verify_t73_candidate_t_band0_core_clearance.py` additionally
checks all relevant deck translates against the actual m2/m3 lifts and the
candidate dual-cell lifts described below.
The three candidate dual-core lifts are saved in
[`geometry/t73_candidate_dual_core_lifts.json`](geometry/t73_candidate_dual_core_lifts.json),
rebuilt with `python3 scripts/build_t73_candidate_dual_core_lifts.py --check`.
With these candidate `u=1/2` lifts included, the clearance verifier checks both
the post-slide core and its push-off and reports
`PASS_CANDIDATE_FRAMED_ALL_CORE_CLEARANCE_ONLY`.

The 1513-step x-cancellation candidate movie is
[`geometry/t73_candidate_x_band_movie.json`](geometry/t73_candidate_x_band_movie.json),
rebuilt with `python3 scripts/build_t73_candidate_x_band_movie.py --check`.
It uses the same candidate-only status and has not replayed actual link states.
Both t/x candidate movies are independently checked with
`python3 scripts/verify_t73_candidate_band_movies.py`. The current verdict
`PASS_CANDIDATE_MOVIE_RECORDS_ONLY` verifies all 1519 bands and 3035 rectangle
segments, not an actual Kirby slide movie.

[`geometry/t73_actual_cancellation_splice_request.json`](geometry/t73_actual_cancellation_splice_request.json)
is the next generated input layer. It enumerates all 6 t-bands and 1513
x-bands with their source center-path hash and required boundary/splice fields:

```text
python3 scripts/build_t73_actual_cancellation_splice_request.py --check
```

For software exploration only, the explicitly non-actual candidate input is
[`geometry/t73_candidate_kirby_presentation.json`](geometry/t73_candidate_kirby_presentation.json),
with its PD/framing export at
[`geometry/t73_candidate_kirby_export.json`](geometry/t73_candidate_kirby_export.json).
Its SnapPy/Spherogram/Regina receipt is
[`geometry/t73_candidate_kirby_open_source_receipt.json`](geometry/t73_candidate_kirby_open_source_receipt.json)
(7 components, 7 crossings, 7 cusps and 36 tetrahedra).
Regenerate with `python3 scripts/build_t73_candidate_kirby_presentation.py --write`
followed by `scripts/export_t73_full_handle_diagram.py`. Its status is
`CANDIDATE_UNVERIFIED`; it must never be used to close P0, C, S or P3/E13.
The candidate coordinate lifts for all 6 t-bands and 1513 x-bands are saved in
[`geometry/t73_candidate_band_chart_normalization.json`](geometry/t73_candidate_band_chart_normalization.json)
and rebuilt with `python3 scripts/build_t73_candidate_band_chart_normalization.py --check`.
Their 3035 rational PL rectangle segments, boundaries and push-offs are saved in
[`geometry/t73_candidate_band_rectangles.json`](geometry/t73_candidate_band_rectangles.json)
and rebuilt with `python3 scripts/build_t73_candidate_band_rectangles.py --check`.
The ordered 1519-band strip and endpoint-splice descriptors are saved in
[`geometry/t73_candidate_band_splice_descriptors.json`](geometry/t73_candidate_band_splice_descriptors.json)
and rebuilt with `python3 scripts/build_t73_candidate_band_splice_descriptors.py --check`.

### Gmsh frames and partitioned-frame inputs

The independently verified Gmsh prefix-20 frame is
[`geometry/examples/t73_selected_source_gmsh_prefix20_frame.json`](geometry/examples/t73_selected_source_gmsh_prefix20_frame.json).
Its verification receipt is
[`audit/t73_selected_source_gmsh_prefix20_frame_verification.json`](audit/t73_selected_source_gmsh_prefix20_frame_verification.json).
It contains 4134 vertices, 23725 tetrahedra, 20 arcs/ribbons, five boundary
components and exact exterior volume 63968; its only valid status is
`PASS_PREFIX_ONLY`, not complete T73 geometry.

The partitioned route retains three exact, committed inputs:

- [`geometry/t73_selected_source_partition_z0.json`](geometry/t73_selected_source_partition_z0.json): all ruled-ribbon, core, push-off and connector fragments cut at `z=0`;
- [`geometry/t73_z0_interface_triangulation.json`](geometry/t73_z0_interface_triangulation.json): the common 36-vertex/42-triangle interface with four insertion-hole loops;
- [`scripts/probe_t73_z0_block_volumes_gmsh.py`](scripts/probe_t73_z0_block_volumes_gmsh.py): a fail-closed Gmsh OCC probe. Its `PASS_FRAGMENT_BATCH_ONLY` result covers only the requested lower-side fragment batch, never the complete frame.

For WSL topology runs, use an isolated environment (the Gmsh wheel also needs
the listed system runtime libraries):

```text
python3 -m venv ~/.venvs/t73-topology
~/.venvs/t73-topology/bin/python -m pip install 'regina>=7.4' 'gmsh==4.15.2'
sudo apt-get install libglu1-mesa libxft2
~/.venvs/t73-topology/bin/python scripts/probe_t73_z0_block_volumes_gmsh.py --fragments 10
```

Routine exact checks, which do not rerun a full mesh, are:

```text
python3 scripts/build_t73_selected_source_partition_z0.py --check
python3 scripts/build_t73_z0_interface_triangulation.py --check
python3 scripts/build_t73_gmsh_frame_verification_receipt.py --check-files
python3 scripts/build_t73_gmsh_frame_verification_receipt.py --check-files --frame geometry/examples/t73_selected_source_gmsh_prefix20_frame.json --output audit/t73_selected_source_gmsh_prefix20_frame_verification.json --expected-prefix 20 --expected-vertices 4134 --expected-tetrahedra 23725 --expected-arcs 20 --expected-ribbons 20 --expected-boundary-components 5 --expected-exact-volume 63968
```

The monolithic 630-ribbon HXT attempt was OOM-killed without writing a mesh.
The partition inputs and probes are therefore preserved as construction data;
the common 630-ribbon tetrahedral frame gate remains `OPEN`.

**Erratum (2 September 2026).** An earlier draft mixed two endpoint index
tables and reported \(-59072\). With both objects in the collar table used by
the braid word, the exact value is \(+2624\) (still nonzero).

## PDFs for review

- English: [`output/pdf/spc4-t73-candidate.pdf`](output/pdf/spc4-t73-candidate.pdf)
- Chinese: [`output/pdf/spc4-t73-candidate-zh.pdf`](output/pdf/spc4-t73-candidate-zh.pdf)

Paper sources and build notes:
[`paper/spc4-t73-candidate/README.md`](paper/spc4-t73-candidate/README.md).

The default paper build writes the reviewed English PDF directly to the
repository output directory (Windows path
`C:\Users\Administrator\Documents\ChatGPT\smooth4pc-t73-lean\output\pdf`):

```text
bash scripts/build_papers.sh          # English, default
bash scripts/build_papers.sh --zh     # Chinese only
bash scripts/build_papers.sh --all    # both
```

## Start here

1. Read the paper abstract and §3 (precise statements) in
   [`paper/spc4-t73-candidate/main.tex`](paper/spc4-t73-candidate/main.tex)
   or the English PDF above.
2. Follow [`REPRODUCING.md`](REPRODUCING.md) to build from a fresh clone, audit
   reported axioms, and recompute the detector.
3. Replay the current actual-geometry chain with the single command below
   (or use the individual commands for a failing stage).
4. For the independent-review boundary map, see
   [`docs/INDEPENDENT_REVIEW.md`](docs/INDEPENDENT_REVIEW.md).

## Fast replay

Requires Python 3.10+. From the repository root:

```text
# Current actual AR → C → S → four-handle chain
python3 -B scripts/verify_t73_actual_chain.py

# Also rebuild the expensive 93-factor PL map and aggregate P0 certificate
python3 -B scripts/verify_t73_actual_chain.py --full
```

Expected final lines:

```text
T73_ACTUAL_CHAIN=PASS
T73_FORMAL_STATUS=CONDITIONAL_EXTERNAL_GEOMETRY
```

The first line covers the mathematical certificate chain. The second records
the remaining formalization boundary: no Lean inhabitant of
`ExternalGeometry` or `CSTopologyData` is manufactured from JSON booleans.

## Individual replay commands

Requires **Python 3.10+** from the repository root. On Windows, `python` is
fine wherever `python3` appears. Each `--check` regenerates the certificate
in memory and compares it to the committed JSON under `audit/`.

### Finite detector (\(D_3=2624\))

```text
python -I -B scripts/recompute_t73_delta3.py --check
```

Expect `DELTA3_ETA_T1=2624`, `DELTA3_XI=0`, and `VERIFY=PASS`.

### Johnson P0 → C → S → P3/E13

```text
# P0 (~1–2 min): AR bridge, cancellations, geometric braid
python -B scripts/certify_t73_p0_johnson.py --check

# Actual AR link and both Kirby cancellations
python -B scripts/verify_t73_actual_ar_link.py --check
python -B scripts/verify_t73_handle_cancellation.py --check
python -B scripts/verify_t73_actual_cut_tangle.py --check

# C: every actual rectangle/circle, comparison supports, assembled witness
python -B scripts/verify_t73_actual_product_rectangles.py --check
python -B scripts/verify_t73_actual_leftover_z_circles.py --check
python -B scripts/verify_t73_actual_geometric_braid.py --check
python -B scripts/verify_t73_endpoint_transport.py --check
python -B scripts/certify_t73_c1_cut_link.py --check
python -B scripts/certify_t73_c2_comparison.py --check
python -B scripts/verify_t73_product_ribbon_isotopy.py --check
python -B scripts/generate_t73_c_comparison_witness.py --check

# S: actual H1 disk tracks, Kirby surface transport, sphere/hemisphere maps
python -B scripts/verify_t73_johnson_dual_disk_movie.py --check
python -B scripts/verify_t73_three_handle_surface_transport.py --check
python -B scripts/verify_t73_actual_sphere_system.py --check
python -B scripts/verify_t73_hemisphere_movies.py --check
python -B scripts/certify_t73_s_relative_moves.py --check

# P3: four-handle picture, standard-S^4 support, CS identification
python -B scripts/certify_t73_p3_four_handle.py --check
python -B scripts/certify_t73_e12_s4.py --check
python -B scripts/certify_t73_e13_close.py --check
python -B scripts/certify_t73_e13_identification.py --check

# Premise summary (mathematical PASS; analytic Lean packaging remains open)
python -B scripts/audit_t73_premises.py --check
python -B scripts/check_t73_claim_boundary.py
```

| Script | Role | Expect |
| --- | --- | --- |
| `certify_t73_p0_johnson.py` | P0 Johnson replacement | `T73_P0_JOHNSON_CERTIFICATE=PASS` |
| `verify_t73_actual_ar_link.py` | Seven-component framed AR link | `ACTUAL_AR_LINK=PASS` |
| `verify_t73_handle_cancellation.py` | Actual t/h_CS and x/m_1 movies | `T_HCS=PASS`, `X_M1=PASS` |
| `verify_t73_actual_cut_tangle.py` | Post-cancellation detector | `PASSAGES=44`, `LEFTOVER_Z_CIRCLES=227` |
| `verify_t73_actual_product_rectangles.py` | Every actual y/z rectangle | `RECTANGLES=44` |
| `verify_t73_actual_leftover_z_circles.py` | Every source-bound leftover circle | `CIRCLES=227` |
| `certify_t73_c1_cut_link.py` | 44 ribbons + 227 leftover \(z\) | `RECTANGLES=44`, `LEFTOVER_Z_CIRCLES=227` |
| `certify_t73_c2_comparison.py` | Disjoint C2 supports / \(H\) movies | `T73_C2_COMPARISON=PASS` |
| `generate_t73_c_comparison_witness.py` | C ledger bound to P0/C1/C2 | `C_STATUS=PASS` |
| `verify_t73_johnson_dual_disk_movie.py` | 93-factor H1 disk transport | `GEOMETRIC_CORE_COUNTS=[12578,1824,409]` |
| `verify_t73_three_handle_surface_transport.py` | Disk tracks through every Kirby band | `ACTUAL_THREE_HANDLE_SURFACE_TRANSPORT=PASS` |
| `verify_t73_actual_sphere_system.py` | Actual partial-W2 sphere system | `ACTUAL_SPHERE_SYSTEM=PASS` |
| `verify_t73_hemisphere_movies.py` | Actual MWW three-handle maps | `ACTUAL_W2_LASAGNA_MAP=True` |
| `certify_t73_p3_four_handle.py` | \(X_J\) four-handle layer | `E11`/`E12` PASS; `E13=PARTIAL` by design |
| `certify_t73_e12_s4.py` | Historical empty-link degree \(494\) check; MWW vanishing holds in every nonzero degree, but the actual candidate degree is open | `S4_DEGREE_494_ZERO=True` |
| `certify_t73_e13_*.py` | \(X_J\cong\Sigma_A^0\) pipeline | `IDENTIFIED_WITH_SIGMA=True` |
| `audit_t73_premises.py` | Aggregate status | `PASS_MATHEMATICAL_LEAN_PARTIAL`, `COUNTEREXAMPLE=True` |
| `check_t73_claim_boundary.py` | Paper/Lean claim boundary | `T73_CLAIM_BOUNDARY=UNCONDITIONAL_PAPER_LEAN_PARTIAL` |

**Notes.**

- Certificates are SHA-chained: C binds to P0, S to P0+C, P3 to P0+C+S. Changing an upstream certificate without regenerating dependents will fail `--check`.
- `certify_t73_p3_four_handle.py` reporting `E13=PARTIAL` is expected; full \(\Sigma_A^0\) identification is in the `e13_*` scripts.
- The old word-only `band_slides` and `derived_crossings` route was removed;
  current checks start from the actual framed AR link and source-bound arcs.
- Lean compile (`tests/test_t73_minimal_formalization.py`) is separate and slower (~5–10 min); see [`REPRODUCING.md`](REPRODUCING.md).

### Focused tests and Lean compilation

```text
python3 -m unittest \
  tests.test_t73_actual_cut_tangle \
  tests.test_t73_actual_product_rectangles \
  tests.test_t73_actual_leftover_z_circles \
  tests.test_t73_actual_geometric_braid \
  tests.test_t73_endpoint_transport \
  tests.test_t73_johnson_dual_disk_movie \
  tests.test_t73_three_handle_surface_transport \
  tests.test_t73_actual_three_handle \
  tests.test_t73_e13_close tests.test_t73_e13_identification

python3 scripts/generate_t73_lean_geometry.py --check
python3 scripts/check_t73_external_geometry_boundary.py
lake env lean Smooth4PC/T73CertificateIndex.lean
lake env lean Smooth4PC/T73JohnsonTransvections.lean
lake env lean Smooth4PC/T73GeometryPack.lean
lake env lean Smooth4PC/T73Conditional.lean
```

`lake build` has no default target in this repository; use the explicit module
commands above. The generated Lean index records the actual artifact hashes and
the exact counts `44`, `227`, `93`, `[12578,1824,409]`, `6`, and `1513`.
The boundary checker must report
`OPEN_MISSING_ANALYTIC_MWW_FOUNDATIONS`; changing this to PASS requires actual
Lean definitions of the MWW modules and maps, not a certificate flag.

## Reproducibility contract

- Lean toolchain: `leanprover/lean4:v4.32.1`
- mathlib revision: `520045ab14e26149ee970e2e617ca04b09bde5d6`
- Python: 3.10 or later
- Lean axiom reports are checked by the focused formalization tests rather
  than a hand-maintained count in this README.
- allowed reported axioms: `propext`, `Classical.choice`, `Quot.sound`
- `sorryAx`: absent
- expected detector value: `2624`

The committed `lake-manifest.json` pins Lean dependencies. Build products and
local dependency copies are not part of the source contract.

## Scope

This is a public verification package for a **conditional obstruction**, not
an unconditional counterexample or a claim of complete Lean formalization.
The remaining load-bearing problem is the relative two-representable MWW
coefficient split and its statewise beta/psi/hemisphere naturality.

## Why this is being released on GitHub first

GitHub is the first public release channel for access, speed and
reproducibility—not a substitute for scholarly review. Existing arXiv history
is in computer science; mathematics-category endorsement may be unavailable.
The full argument, Lean sources, certificates and replay instructions are
inspectable here. After substantive scrutiny, a conventional preprint
submission is intended.

## License

The repository is released under the [MIT License](LICENSE).
